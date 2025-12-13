import time
from typing import Any

from .consts import (
    ATHENA_CATALOG,
    ATHENA_DATABASE,
    ATHENA_OUTPUT_LOCATION,
    ATHENA_WORKGROUP,
)


def run_athena_query(
    sql: str,
    athena_client,
    max_wait_seconds: int = 60,
    poll_interval_seconds: float = 0.5,
) -> list[dict[str, Any]]:
    start_resp = athena_client.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={
            "Catalog": ATHENA_CATALOG,
            "Database": ATHENA_DATABASE,
        },
        ResultConfiguration={
            "OutputLocation": ATHENA_OUTPUT_LOCATION,
        },
        WorkGroup=ATHENA_WORKGROUP,
    )
    qid = start_resp["QueryExecutionId"]

    deadline = time.time() + max_wait_seconds
    while True:
        exec_resp = athena_client.get_query_execution(QueryExecutionId=qid)
        state = (
            exec_resp.get("QueryExecution", {})
            .get("Status", {})
            .get("State", "UNKNOWN")
        )
        if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        if time.time() >= deadline:
            raise TimeoutError(f"Athena クエリがタイムアウトしました: {qid}")
        time.sleep(poll_interval_seconds)

    if state != "SUCCEEDED":
        reason = (
            exec_resp.get("QueryExecution", {})
            .get("Status", {})
            .get("StateChangeReason", "")
        )
        raise RuntimeError(f"Athena クエリ失敗: state={state} reason={reason}")

    rows: list[dict[str, Any]] = []
    next_token: str | None = None
    header: list[str] | None = None

    while True:
        kwargs: dict[str, Any] = {"QueryExecutionId": qid}
        if next_token:
            kwargs["NextToken"] = next_token
        result_resp = athena_client.get_query_results(**kwargs)

        result_set = result_resp.get("ResultSet", {}) or {}
        meta = result_set.get("ResultSetMetadata", {}) or {}
        cols = meta.get("ColumnInfo", []) or []
        col_names = [c.get("Name", "") for c in cols]

        rs_rows = result_set.get("Rows", []) or []
        if header is None:
            header = col_names
            rs_rows = rs_rows[1:] if rs_rows else []

        for r in rs_rows:
            data = r.get("Data", []) or []
            values = [d.get("VarCharValue") for d in data]
            row = {
                header[i]: (values[i] if i < len(values) else None)
                for i in range(len(header))
            }
            rows.append(row)

        next_token = result_resp.get("NextToken")
        if not next_token:
            break

    return rows
