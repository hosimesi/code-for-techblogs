import asyncio
import logging
import os

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP

load_dotenv(verbose=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


mcp_http_server = MCPServerHTTP(
    url="http://127.0.0.1:8000/sse",
)

client_agent = Agent(
    "openai:gpt-4o-mini",
    mcp_servers=[mcp_http_server],
    system_prompt="ユーザーのリクエストを解釈し、必要に応じて利用可能なツールを使ってください。出力はツールの出力をそのまま出力してください。",
)


async def main_client():
    async with client_agent.run_mcp_servers():
        prompt = "日本の有名な観光地について教えて"
        result = await client_agent.run(prompt)
        logger.info(f"最終的な回答: {result.output}")


if __name__ == "__main__":
    asyncio.run(main_client())
