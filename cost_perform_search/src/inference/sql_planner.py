import json
import re
from typing import Literal

from pydantic import BaseModel, Field
from shared.consts import ATHENA_DATABASE, ATHENA_TABLE


class QueryPlan(BaseModel):
    source: Literal["s3table", "s3vectors"]
    sql: str
    reason: str = Field(default="")


_PROHIBITED = re.compile(
    r"(?is)\b(insert|update|delete|drop|create|alter|truncate|grant|revoke|msck|repair|call|merge)\b"
)
_COMMENT = re.compile(r"(?s)--|/\*|\*/")


def _extract_first_json_object(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    s = re.sub(r"(?is)```(?:json)?\s*", "", s)
    s = re.sub(r"(?is)\s*```", "", s)

    start = s.find("{")
    end = s.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return ""
    return s[start : end + 1].strip()


def _looks_like_table_query(query: str) -> bool:
    q = (query or "").strip()
    if not q:
        return False
    keywords = [
        "売上",
        "売り上げ",
        "売り上",
        "利益",
        "営業利益",
        "経常利益",
        "純利益",
        "税引前",
        "推移",
        "前年差",
        "増減",
        "合計",
        "平均",
        "最大",
        "最小",
        "FY",
        "年",
        "月",
        "四半期",
    ]
    return any(k in q for k in keywords)


def _period_candidates(query: str) -> list[str]:
    q = (query or "").strip()
    if not q:
        return []

    m = re.search(r"(?i)\bFY\s*([12][0-9]{3})\b", q)
    if m:
        return [f"FY{m.group(1)}"]

    m = re.search(r"\b([12][0-9]{3})\s*(年|年度)?\b", q)
    if m:
        return [f"FY{m.group(1)}"]

    return []


def _fallback_sql(query: str) -> str:
    periods = _period_candidates(query)
    base = (
        "SELECT period, net_sales, operating_income, ordinary_income, net_income "
        f"FROM {ATHENA_TABLE} "
    )
    if periods:
        p = periods[0]
        base += f"WHERE period = '{p}' "
    base += "ORDER BY period DESC LIMIT 200"
    return base


def _is_safe_sql(sql: str) -> bool:
    s = (sql or "").strip()
    if not s:
        return False
    if ";" in s:
        return False
    if _COMMENT.search(s):
        return False
    if _PROHIBITED.search(s):
        return False
    if not re.match(r"(?is)^(select|with)\b", s):
        return False
    if ATHENA_TABLE.lower() not in s.lower():
        return False
    return True


def plan_query_with_sql(
    query: str,
    bedrock_runtime_client,
    model_id: str,
) -> QueryPlan:
    """
    ユーザーの自然言語から:
    - S3テーブル(Athena)向きなら SQL を生成 (source=s3table)
    - それ以外はベクター検索 (source=s3vectors)
    を JSON で返す。
    """
    schema = f"""
データベース: {ATHENA_DATABASE}
テーブル: {ATHENA_TABLE}
カラム:
- period (string, required) 例: "FY2025" のような会計年度
- net_sales (int)
- operating_income (int)
- non_operating_income (int)
- non_operating_expenses (int)
- ordinary_income (int)
- extraordinary_gains (int)
- extraordinary_losses (int)
- income_before_taxes (int)
- net_income (int)
- net_income_non_controlling_interests (int)
- net_income_attributable_to_owners (int)
説明: サイバーエージェントの年毎の売上や利益などのデータ。単位は百万円。
"""

    system_text = f"""
あなたは「日本語の質問 → どのデータソースを使うべきか判定し、必要なら Athena 用SQLを生成する」アシスタントです。
必ず次の JSON だけを返してください（前後に説明文や Markdown を付けない）:
{{"source":"s3table"|"s3vectors","sql":"...","reason":"..."}}

利用可能なデータ:
1) S3ベクター検索: 一般的なナレッジ検索向き
2) S3テーブル(Athena): 数値集計・期間(period)での絞り込み・指標(売上/利益など)の問い合わせ向き

S3テーブルのスキーマ:
{schema}

SQL生成ルール（重要）:
- Athena(Presto/Trino) 方言を想定
- SELECT のみ（DDL/DMLは禁止）。セミコロン禁止。コメント記法禁止。
- 参照できるテーブルは {ATHENA_TABLE} のみ
- 必ず LIMIT を付ける（最大 200）
- ユーザーが期間/年度を指定していれば period で絞り込む
  - "FY2025" → period='FY2025'
  - "2025年" / "2025年度" / "2025" → period='FY2025'
- 指標の対応:
  - 売上 → net_sales
  - 営業利益 → operating_income
  - 経常利益 → ordinary_income
  - 税引前利益 → income_before_taxes
  - 純利益 → net_income
"""

    user_text = f"ユーザーの質問: {query}"

    resp = bedrock_runtime_client.converse(
        modelId=model_id,
        system=[{"text": system_text}],
        messages=[{"role": "user", "content": [{"text": user_text}]}],
    )
    content = resp.get("output", {}).get("message", {}).get("content", []) or []
    raw = ""
    if content and isinstance(content, list) and "text" in content[0]:
        raw = str(content[0]["text"])

    json_text = _extract_first_json_object(raw)
    try:
        data = json.loads(json_text) if json_text else None
    except Exception:
        data = None

    if not isinstance(data, dict):
        if _looks_like_table_query(query):
            fallback_sql = _fallback_sql(query=query)
            return QueryPlan(
                source="s3table",
                sql=fallback_sql,
                reason="planner_json_parse_failed_fallback_sql",
            )
        return QueryPlan(source="s3vectors", sql="", reason="planner_json_parse_failed")

    source = str(data.get("source", "s3vectors"))
    sql = str(data.get("sql", "") or "")
    reason = str(data.get("reason", "") or "")

    if source == "s3table":
        if _is_safe_sql(sql):
            periods = _period_candidates(query)
            if periods:
                p = periods[0]
                sql = re.sub(
                    r"(?is)\bperiod\s*=\s*'([12][0-9]{3})'\b",
                    f"period = '{p}'",
                    sql,
                )
            return QueryPlan(source="s3table", sql=sql, reason=reason)
        if _looks_like_table_query(query):
            fallback_sql = _fallback_sql(query=query)
            return QueryPlan(
                source="s3table", sql=fallback_sql, reason="unsafe_sql_fallback_sql"
            )
        return QueryPlan(source="s3vectors", sql="", reason="unsafe_sql")

    return QueryPlan(source="s3vectors", sql="", reason=reason)
