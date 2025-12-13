import logging
import os
from typing import Any

from pypdf import PdfReader
from shared.consts import PDF_PATH, S3_VECTORS_BUCKET_NAME, S3_VECTORS_INDEX_NAME
from shared.embeddings import embed_text

logger = logging.getLogger(__name__)

MAX_METADATA_BYTES = 1800
PAGES_PER_CHUNK = 2
INDEX_START_PAGE = 32
INDEX_END_PAGE = 133


def _trim_to_max_bytes(s: str, max_bytes: int) -> str:
    b = s.encode("utf-8")
    if len(b) <= max_bytes:
        return s
    cut = b[:max_bytes]
    while cut:
        try:
            return cut.decode("utf-8")
        except UnicodeDecodeError:
            cut = cut[:-1]
    return ""


def run_indexing(bedrock_runtime_client, s3vectors_client) -> None:
    try:
        reader = PdfReader(PDF_PATH)
    except Exception:
        raise Exception("読み込み失敗")

    pages = reader.pages
    vectors: list[dict[str, Any]] = []

    total_pages = len(pages)
    start = max(1, INDEX_START_PAGE)
    end = min(total_pages, INDEX_END_PAGE)

    if start > end:
        logger.warning(
            f"indexing 対象ページが不正です: start={start} end={end} total={total_pages}"
        )
        return

    for page_start in range(start, end + 1, PAGES_PER_CHUNK):
        page_end = min(end, page_start + (PAGES_PER_CHUNK - 1))

        texts: list[str] = []
        for p in range(page_start, page_end + 1):
            t = pages[p - 1].extract_text() or ""
            if t.strip():
                texts.append(t.strip())

        combined_text = "\n\n".join(texts).strip()
        logger.info(
            f"処理中: ページ {page_start}-{page_end}, テキスト: {combined_text[:100]}..."
        )

        if not combined_text:
            continue

        embedding = embed_text(
            text=combined_text, bedrock_runtime_client=bedrock_runtime_client
        )

        metadata: dict[str, str | int] = {
            "source_file": os.path.basename(PDF_PATH),
            "page_number": page_start,
            "page_end": page_end,
            "source_text": _trim_to_max_bytes(combined_text, MAX_METADATA_BYTES),
        }

        vectors.append(
            {
                "key": f"{os.path.basename(PDF_PATH)}_{page_start}-{page_end}",
                "data": {"float32": embedding},
                "metadata": metadata,
            }
        )

        if len(vectors) >= 50:
            s3vectors_client.put_vectors(
                vectorBucketName=S3_VECTORS_BUCKET_NAME,
                indexName=S3_VECTORS_INDEX_NAME,
                vectors=vectors,
            )
            vectors = []

    if vectors:
        s3vectors_client.put_vectors(
            vectorBucketName=S3_VECTORS_BUCKET_NAME,
            indexName=S3_VECTORS_INDEX_NAME,
            vectors=vectors,
        )
