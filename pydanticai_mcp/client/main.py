import asyncio
import logging
import os

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

load_dotenv(verbose=True)

notion_api_key = os.getenv("NOTION_API_KEY")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

notion_mcp_env = {
    "OPENAPI_MCP_HEADERS": f'{{"Authorization": "Bearer {notion_api_key}", "Notion-Version": "2022-06-28"}}'
}


notion_server = MCPServerStdio(
    command="npx",
    args=["-y", "@notionhq/notion-mcp-server"],
    env=notion_mcp_env,
)

agent = Agent(
    # "google-gla:gemini-2.0-flash-lite",
    "openai:gpt-4o-mini",
    mcp_servers=[notion_server],
)


async def main():
    logger.info("MCPサーバを起動してエージェントを実行します...")
    async with agent.run_mcp_servers():
        prompt = "MCPテストというページに議事録のフォーマットを作成して"
        logger.info(f"実行するプロンプト: {prompt}")
        result = await agent.run(prompt)
        logger.info(f"エージェントからの出力: {result.output}")


if __name__ == "__main__":
    asyncio.run(main())
