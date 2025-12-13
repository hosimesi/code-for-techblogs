# Cost Perform Search（S3 Vectors + S3 Tables）

## セットアップ（ローカル）

```bash
uv sync
```

## 環境変数（.env）

```dotenv
# AWS
AWS_REGION=ap-northeast-1
AWS_PROFILE=default

# Bedrock
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0
BEDROCK_CHAT_MODEL_ID=anthropic.claude-haiku-4-5-20251001-v1:0

# S3 Vectors
S3_VECTORS_BUCKET_NAME=<your-s3vectors-bucket-name>
S3_VECTORS_INDEX_NAME=<your-s3vectors-index-name>

# Athena (S3 Tables)
ATHENA_CATALOG=s3tablescatalog/<your-s3tables-table-bucket-name>
ATHENA_DATABASE=<your-s3tables-namespace>
ATHENA_TABLE=<your-s3tables-table-name>
ATHENA_WORKGROUP=<your-athena-workgroup>
ATHENA_OUTPUT_LOCATION=s3://<your-athena-output-bucket>/athena-query-results/
ATHENA_AMOUNT_UNIT=百万円
```

## AWSリソース準備（CLI）

### 汎用S3（PDF置き場）

```bash
aws s3 mb s3://<your-standard-bucket-name> --region ap-northeast-1
aws s3 cp data/AIDataTechnologyMap.pdf s3://<your-standard-bucket-name>/
```

### S3 Vectors（ベクトルバケット / インデックス）

```bash
aws s3vectors create-vector-bucket \
  --vector-bucket-name <your-s3vectors-bucket-name>

aws s3vectors create-index \
  --vector-bucket-name <your-s3vectors-bucket-name> \
  --index-name <your-s3vectors-index-name> \
  --data-type float32 \
  --dimension 1024 \
  --distance-metric cosine
```

### S3 Tables（テーブルバケット / namespace / table）

```bash
aws s3tables create-table-bucket --name <your-s3tables-table-bucket-name>

aws s3tables create-namespace \
  --table-bucket-arn "<your-s3tables-table-bucket-arn>" \
  --namespace <your-s3tables-namespace>

aws s3tables create-table \
  --table-bucket-arn "<your-s3tables-table-bucket-arn>" \
  --namespace <your-s3tables-namespace> \
  --name <your-s3tables-table-name> \
  --format 'ICEBERG' \
  --metadata '{"iceberg": {"schema": {"fields": [{"name": "period", "type": "string", "required": true},{"name": "net_sales", "type": "int", "required": false},{"name": "operating_income", "type": "int", "required": false},{"name": "non_operating_income", "type": "int", "required": false},{"name": "non_operating_expenses", "type": "int", "required": false},{"name": "ordinary_income", "type": "int", "required": false},{"name": "extraordinary_gains", "type": "int", "required": false},{"name": "extraordinary_losses", "type": "int", "required": false},{"name": "income_before_taxes", "type": "int", "required": false},{"name": "net_income", "type": "int", "required": false},{"name": "net_income_non_controlling_interests", "type": "int", "required": false},{"name": "net_income_attributable_to_owners", "type": "int", "required": false}]}}}'
```

### Athena（出力先S3 / workgroup）

```bash
aws s3 mb s3://<your-athena-output-bucket> --region ap-northeast-1

aws athena update-work-group \
  --work-group <your-athena-workgroup> \
  --configuration-updates '{"ResultConfigurationUpdates": {"OutputLocation": "s3://<your-athena-output-bucket>/athena-query-results/","RemoveAclConfiguration": false,"RemoveEncryptionConfiguration": false}}'
```

### Athena（データ投入例）

```sql
INSERT INTO <your-s3tables-table-name>
VALUES
('FY2021', 666149, 104070, 861, 548, 104382, 2201, 6173, 100410, 66359, 25117, 41242),
('FY2022', 709923, 67552, 999, 648, 67902, 1633, 8299, 61236, 38096, 15194, 22901),
('FY2023', 719451, 22351, 1263, 904, 22710, 1470, 3854, 20326, 9151, 5611, 3540),
('FY2024', 801236, 40083, 1753, 2121, 39715, 313, 8815, 31213, 20376, 4398, 15977),
('FY2025', 874030, 71702, 1622, 1581, 71743, 2319, 7835, 66227, 41964, 10296, 31667);
```

## 実行

```bash
uv run src/main.py indexing
```

```bash
uv run src/main.py inference
```
