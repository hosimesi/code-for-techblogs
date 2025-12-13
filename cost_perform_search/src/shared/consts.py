import os

AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")
AWS_PROFILE = os.getenv("AWS_PROFILE", "default").strip()

BEDROCK_EMBEDDING_MODEL_ID = os.getenv(
    "BEDROCK_EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0"
)

S3_VECTORS_BUCKET_NAME = os.getenv(
    "S3_VECTORS_BUCKET_NAME", "ais-advent-calendar-2025-vector"
)
S3_VECTORS_INDEX_NAME = os.getenv(
    "S3_VECTORS_INDEX_NAME", "ais-advent-calendar-2025-vector-index"
)

BEDROCK_CHAT_MODEL_ID = os.getenv(
    "BEDROCK_CHAT_MODEL_ID",
"anthropic.claude-haiku-4-5-20251001-v1:0",
)

EMBEDDING_DIMENSIONS = 1024
EMBEDDING_NORMALIZE = True

PDF_PATH = os.path.join("data", "AIDataTechnologyMap.pdf")
TOP_K = 5

# Athena (S3 Tables) 設定
ATHENA_CATALOG = os.getenv(
    "ATHENA_CATALOG", "s3tablescatalog/ais-advent-calendar-2025-table"
)
ATHENA_DATABASE = os.getenv(
    "ATHENA_DATABASE", "ais_advent_calendar_2025_table_namespace"
)
ATHENA_WORKGROUP = os.getenv("ATHENA_WORKGROUP", "primary")
ATHENA_OUTPUT_LOCATION = os.getenv(
    "ATHENA_OUTPUT_LOCATION",
    "s3://ais-advent-calendar-2025-athena-ouput/athena-query-results/",
).strip()

ATHENA_TABLE = os.getenv("ATHENA_TABLE", "ca_sales_table")
ATHENA_AMOUNT_UNIT = os.getenv("ATHENA_AMOUNT_UNIT", "百万円")
