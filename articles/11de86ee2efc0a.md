---
title: "PydanticAIとMCP"
emoji: "🌊"
type: "tech"
topics: ["agent", "pydanticai", "mcp", "llm"]
published: true
published_at: 2025-05-12 08:30
---
## 概要
PydanticAIを使ってMCPを触ってみたいと思います。
今回のスコープではMCPクライアントとしてPydanticAIを使う方法とMCPサーバ内でPydanticAIを使う方法を紹介します。

本文中のコード: https://github.com/hosimesi/code-for-techblogs/tree/main/pydanticai_mcp

## PydanticAIとは
[PydanticAI](https://ai.pydantic.dev/)は、生成AIのアプリケーションを作るためのPythonフレームワークです。前回の記事でも取り扱ったので、詳しくは[公式ドキュメント](https://ai.pydantic.dev/)と[こちら](https://zenn.dev/hosimesi/articles/4085071b920734)を参照してください。

## Model Context Protocolとは
Model Context Protocol(MCP)は、[Anthropic](https://www.google.com/search?q=anthropic+mcp&sourceid=chrome&ie=UTF-8)が提唱したAIアプリケーションが共通のインターフェースを使用して外部のツールやサービスに接続できるように標準化されたプロトコルです。

## 環境構築
[uv](https://docs.astral.sh/uv/guides/install-python/)を使用して環境を構築します。まずは、必要になるpydantic-aiをインストールします。
```bash
$ uv init
```
```bash
$ uv add pydantic-ai
```
環境変数読み込みのための[dotenv](https://pypi.org/project/python-dotenv/)もインストールします。
```bash
$ uv add python-dotenv
```
非同期実行のためのasyncioもインストールします。
```bash
$ uv add asyncio
```
MCPサーバ作成のためのfastmcpもインストールします。
```bash
$ uv add fastmcp
```
後ほど設定しますが、.envを作成しておきます。
```bash
$ cp .env.example .env
```

## MCPクライアントとしてPydanticAIを使用する
公式ドキュメントにある通り、PydanticAIでMCPサーバに接続する方法は2つあります。
- MCPServerHTTP
  - HTTP SSEトランスポートを使用してMCPサーバに接続する
- MCPServerStdio
  - サーバをサブプロセスとして実行し、stdioトランスポートを使用してサーバに接続する

`MCPServerHTTP`は、設定されたSSEに対応したエンドポイントに対してHTTPリクエストを送信して通信を行います。
公開済みのリモートMCPサーバなどすでにインターフェイスが整っているMCPサーバに有効です。
`MCPServerStdio`はMCPサーバをPydanticAIのサブプロセスとして起動し、標準入力（stdin）と標準出力（stdout）を通じて通信します。つまり、コード内でMCPサーバの起動コマンドを直接入力してプロセス間で通信するため、ローカル開発などサクッと試したいときに便利です。

今回はNotionの公式MCPサーバをPydanticAIのMCPクライアントからMCPServerStdio形式で呼び出して使ってみたいと思います。

Notionの公式ページの[Integration設定](https://www.notion.so/profile/integrations)からMCP用のIntegrationを作成します。
![NotionのIntegration設定](https://storage.googleapis.com/zenn-user-upload/691149fe5186-20250511.png)
Integrationのシークレットキーが生成されるので、こちらを保存しておきます。
:::message alert
機密情報なので取り扱いには注意してください
:::

上記の情報含めて、.envにシークレットを書いておきます。
```bash
$ vim .env
```
```sh:.env
GEMINI_API_KEY=xxxxx
NOTION_API_KEY=xxxxx
OPENAI_API_KEY=xxxxx
```

次にNotionのページの設定をしていきます。Integration TypeがInternalの場合、Integrationが接続できるページは手動で許可する必要があります。
以下のように「MCPテスト」というテストページを作って、許可しておきます。
![Notion Integration許可](https://storage.googleapis.com/zenn-user-upload/80986ffbbe13-20250511.png)
こちらで準備は完了です。

次に、MCPクライアントの実装をしていきます。PydanticAIでMCPサーバを使う上で重要な部分は以下の部分になります。
以下のようにサブプロセスで起動するMCPサーバを指定します。
```python
notion_server = MCPServerStdio(
    command="npx",
    args=["-y", "@notionhq/notion-mcp-server"],
    env=notion_mcp_env,
    name="notion_mcp",
)
```
その後、Agentの引数に作成したMCPサーバのインスタンスを設定するだけで使うことができます。もちろん、MCPサーバは複数設定できるため、使いたいツール群をまとめて登録しておくと便利です
```python
agent = Agent(
    "google-gla:gemini-2.0-flash-lite",
    mcp_servers=[notion_server],
    instrument=True,
)
```

最終的なPythonファイルは以下のようになります。
```python:main.py
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
```

実行してみます。
```bash
$ uv run python client/main.py
```

今回、議事録のフォーマットを作成してもらいましたが以下のように正常に作られていそうです。PydanticAIではTool Callingのように数行追加するだけでMCPクライアントとして動作するのはとても便利そうです。
![議事録フォーマット](https://storage.googleapis.com/zenn-user-upload/ef08a6910ee7-20250511.png)

:::message
OpenAI Agent SDK互換になっており、他のLLMだとパッチを当てないと動かないのかなと思います。自分の手元だとGemini 2.0だと動きませんでした。
:::

## MCPサーバ内でPydanticAIを使用する
次に先ほどのようなNotionのMCPサーバのようなものの内部で、PydanticAIを使って実装してみたいと思います。今回は簡単にMCPが作成可能な[fastmcp](https://github.com/jlowin/fastmcp)を使いたいと思います。そして、先ほどはMCPServerStdioクライアントからMCPサーバに繋いでいましたが、今回はMCPServerHTTPでアクセスできるようにMCPサーバを構築します。
全ての質問に対して関西弁で答えるMCPサーバを[公式ドキュメント](https://ai.pydantic.dev/mcp/server/)を参考に構築したいと思います。
fastmcpにはserverの起動オプションでsseかstdioを選択できるので、sseを選択して以下のように実装します。
```python:server.py
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
```

そして、あるプロセスで実行しておきます。
```bash
$ uv run python server/main.py
```

次にクライアント側の実装をします。先ほど作成したMCPServerHTTPのサーバをMCPサーバとして登録して呼び出します。ここでプロンプトにはツールの出力をそのまま出力させるように設定します。
```python:client.py
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
```

そして実行します。
```bash
$ uv run python server/client.py
```

すると以下のように返ってきます。
```text:output.txt
INFO:__main__:最終的な回答: ほんなら、日本の有名な観光地について話すで！

まずは何と言うても京都やな。古い寺院や神社がたくさんあって、金閣寺や清水寺はほんまに美しいで。秋の紅葉や春の桜が特に人気やし、外国からの観光客も多いわ。

次に大阪。大阪城や道頓堀、大阪の食いもん、たこ焼きやお好み焼きが有名やし、ほんまに食べ物天国やね。ユニバーサル・スタジオ・ジャパンもあって、遊びも楽しめるで！

あとは東京。スカイツリーや浅草寺、原宿の竹下通りなんかがあって、結構賑やかやで。今時の若者の流行もここに集まってるし、見どころ満載やな。

最後に沖縄も忘れたらあかんで！美しい海とかビーチがあって、リゾート気分を味わいたい人には最高やんな。

ほんまに日本には素敵な観光地がいっぱいあるから、行ってみたらええで！
```

MCPサーバ内でもPydanticAIを使用することができました。

## まとめ
本記事では、MCPクライアント、MCPサーバでPydanticAIを使用してみました。
PydanticAIを使用することでインターフェイスを大きく変えなくてすみ、MCPの実装が比較的簡単に行えるようになるので便利です。

## 参考
https://ai.pydantic.dev/
https://github.com/jlowin/fastmcp

