from typing import Any

from pydantic import BaseModel
from shared.consts import S3_VECTORS_BUCKET_NAME, S3_VECTORS_INDEX_NAME, TOP_K
from shared.embeddings import embed_text


class SearchHit(BaseModel):
    key: str
    metadata: dict[str, Any]
    distance: float | None = None


def search_vector_index(
    query: str,
    bedrock_runtime_client,
    s3vectors_client,
) -> list[SearchHit]:
    query_vec = embed_text(text=query, bedrock_runtime_client=bedrock_runtime_client)

    response = s3vectors_client.query_vectors(
        vectorBucketName=S3_VECTORS_BUCKET_NAME,
        indexName=S3_VECTORS_INDEX_NAME,
        queryVector={"float32": query_vec},
        topK=TOP_K,
        returnDistance=True,
        returnMetadata=True,
    )

    hits: list[SearchHit] = []
    for v in response.get("vectors", []) or []:
        key = str(v.get("key", ""))
        metadata = v.get("metadata")
        metadata_dict = dict(metadata) if isinstance(metadata, dict) else {}
        distance = v.get("distance")
        dist = float(distance) if distance is not None else None
        hits.append(SearchHit(key=key, metadata=metadata_dict, distance=dist))

    return hits


def _format_context(hits: list[SearchHit], *, max_chars_per_hit: int = 800) -> str:
    lines: list[str] = []
    for i, h in enumerate(hits, start=1):
        src_file = h.metadata.get("source_file")
        page = h.metadata.get("page_number")
        text = h.metadata.get("source_text") or ""
        if not isinstance(text, str):
            text = ""
        text = text.replace("\n", " ").strip()
        if len(text) > max_chars_per_hit:
            text = text[:max_chars_per_hit] + "…"
        lines.append(f"[{i}] source_file={src_file} page={page} key={h.key}\n{text}")
    return "\n\n".join(lines)


def generate_answer(
    *,
    query: str,
    hits: list[SearchHit],
    bedrock_runtime_client,
    model_id: str,
) -> str:
    context = _format_context(hits)
    return generate_answer_from_context(
        query=query,
        context=context,
        bedrock_runtime_client=bedrock_runtime_client,
        model_id=model_id,
        citation_hint="(source_file, page)",
    )


def generate_answer_from_context(
    query: str,
    context: str,
    bedrock_runtime_client,
    model_id: str,
    citation_hint: str,
) -> str:
    system_text = (
        "あなたは日本語で回答するアシスタントです。与えられたコンテキストのみを根拠に、"
        "ユーザーの質問に簡潔に答えてください。根拠として参照した箇所は "
        f"{citation_hint} を添えて示してください。"
        "数値を回答する場合、コンテキストに単位（例: amount_unit）があれば必ず単位を付けてください。"
        "コンテキストに情報がない場合は、推測せず『不明』と述べ、追加で必要な情報を提示してください。"
    )
    user_text = (
        f"## 質問\n{query}\n\n## コンテキスト\n{context or '（該当コンテキストなし）'}"
    )

    resp = bedrock_runtime_client.converse(
        modelId=model_id,
        system=[{"text": system_text}],
        messages=[{"role": "user", "content": [{"text": user_text}]}],
    )
    content = resp.get("output", {}).get("message", {}).get("content", []) or []
    if content and isinstance(content, list) and "text" in content[0]:
        return str(content[0]["text"])
    return ""
