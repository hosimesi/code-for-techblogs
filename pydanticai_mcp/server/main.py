import logging
from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic_ai import Agent

load_dotenv(verbose=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = FastMCP("PydanticAI MCP Server")

server_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="あなたは関西人です。すべての回答は関西弁で回答してください。",
)


@server.tool()
async def kansai_answer(theme: str) -> str:
    """関西弁で回答を作成します。"""
    logger.info(f"ツールの呼び出し: kansai_answer, theme='{theme}'")
    r = await server_agent.run(f"関西弁で「{theme}」についての回答を作成してください。")
    logger.info(f"エージェントからの出力: {r.output}")
    return r.output


if __name__ == "__main__":
    logger.info("MCPサーバを起動します...")
    try:
        server.run(transport="sse", host="127.0.0.1", port=8000)
    except KeyboardInterrupt:
        logger.info("MCPサーバを停止します...")
        server.stop()
