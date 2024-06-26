import asyncio

from src.services.inference_server import serve
from src.utils.logging import get_logger

logger = get_logger(__name__)


def main() -> None:
    logger.info("Starting server.")
    bind_address = "[::]:8080"

    asyncio.run(serve(bind_address))


if __name__ == "__main__":
    main()
