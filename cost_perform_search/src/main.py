import argparse
import logging

from dotenv import load_dotenv
from indexing.pdf_indexer import run_indexing
from inference.search import (
    generate_answer,
    generate_answer_from_context,
    search_vector_index,
)
from inference.sql_planner import plan_query_with_sql
from shared.athena import run_athena_query
from shared.clients import create_client
from shared.consts import (
    ATHENA_AMOUNT_UNIT,
    ATHENA_CATALOG,
    ATHENA_DATABASE,
    ATHENA_TABLE,
    BEDROCK_CHAT_MODEL_ID,
)
from shared.logging_utils import setup_logging

load_dotenv()

logger = logging.getLogger(__name__)


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cost_perform_search")
    parser.add_argument("mode", choices=["indexing", "inference"])
    return parser


def main() -> None:
    setup_logging()
    args = parser().parse_args()

    bedrock_runtime_client = create_client("bedrock-runtime")
    s3vectors_client = create_client("s3vectors")
    athena_client = create_client("athena")

    if args.mode == "indexing":
        run_indexing(
            bedrock_runtime_client=bedrock_runtime_client,
            s3vectors_client=s3vectors_client,
        )
        return

    try:
        while True:
            try:
                query = input("query> ").strip()
            except EOFError:
                logger.info("終了")
                return

            if not query:
                continue

            plan = plan_query_with_sql(
                query=query,
                bedrock_runtime_client=bedrock_runtime_client,
                model_id=BEDROCK_CHAT_MODEL_ID,
            )

            if plan.source == "s3table" and plan.sql:
                logger.info(
                    "route=s3table "
                    f"catalog={ATHENA_CATALOG} db={ATHENA_DATABASE} table={ATHENA_TABLE}"
                )
                logger.info("sql: " + plan.sql)

                use_table = True
                athena_error = ""
                try:
                    rows = run_athena_query(sql=plan.sql, athena_client=athena_client)
                except Exception as e:
                    use_table = False
                    athena_error = str(e)
                    logger.exception(f"athena query failed: {e}")
                    logger.info("fallback to s3vectors (athena failed)")
                    rows = []

                if use_table:
                    logger.info(f"athena rows: {len(rows)}")

                if plan.source == "s3table":
                    max_rows = 30
                    shown = rows[:max_rows]
                    if shown:
                        cols = list(shown[0].keys())
                        lines = [
                            f"source_table={ATHENA_TABLE} catalog={ATHENA_CATALOG} database={ATHENA_DATABASE}",
                            f"amount_unit={ATHENA_AMOUNT_UNIT} (金額系カラム: net_sales/operating_income/ordinary_income/net_income など)",
                            "columns: " + ", ".join(cols),
                            "rows:",
                        ]
                        for r in shown:
                            kv = ", ".join(f"{k}={r.get(k)}" for k in cols)
                            lines.append(kv)
                        context = "\n".join(lines)
                    else:
                        context = (
                            f"source_table={ATHENA_TABLE} catalog={ATHENA_CATALOG} database={ATHENA_DATABASE}\n"
                            "rows: 0"
                        )

                    answer = generate_answer_from_context(
                        query=query,
                        context=context,
                        bedrock_runtime_client=bedrock_runtime_client,
                        model_id=BEDROCK_CHAT_MODEL_ID,
                        citation_hint="(table, period) もしくは (table, columns)",
                    )
                    print("\nanswer>\n" + answer + "\n")
                    continue

            if plan.source == "s3table" and not plan.sql:
                logger.info("route=s3vectors reason=table_planned_but_sql_empty")
            elif plan.source == "s3table":
                logger.info(
                    f"route=s3vectors reason=athena_failed error={athena_error}"
                )
            else:
                logger.info(f"route=s3vectors reason={plan.reason}")
            hits = search_vector_index(
                query=query,
                bedrock_runtime_client=bedrock_runtime_client,
                s3vectors_client=s3vectors_client,
            )
            hit_lines: list[str] = []
            for h in hits:
                meta = (
                    f"source_file={h.metadata.get('source_file')} "
                    f"page={h.metadata.get('page_number')}"
                )
                dist = f"distance={h.distance:.6f}" if h.distance is not None else ""
                head = f"{dist}\t" if dist else ""
                hit_lines.append(f"{head}{h.key}\t{meta}")

            if hit_lines:
                logger.info("hits:\n" + "\n".join(hit_lines))
            else:
                logger.info("hits: 0")

            answer = generate_answer(
                query=query,
                hits=hits,
                bedrock_runtime_client=bedrock_runtime_client,
                model_id=BEDROCK_CHAT_MODEL_ID,
            )
            print("\nanswer>\n" + answer + "\n")
    except KeyboardInterrupt:
        logger.info("終了")
        return


if __name__ == "__main__":
    main()
