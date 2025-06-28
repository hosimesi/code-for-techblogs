---
title: "pydantic-graphの中を見る"
emoji: "👻"
type: "tech"
topics: [Python, Pydantic, PydanticAI, Graphs]
published: true
published_at: 2025-06-30 08:00
---

pydantic-graphの中のコードを読みながら、どのように実装されているかを見てみました。

## 概要
AIエージェントライブラリであるPydanticAIの機能の一部にpydantic-graphがあります。
これは、Python用の非同期グラフおよびステートマシンを作るためのライブラリですが、なかなかこの機能単体で使用する場面は少ないと思います。
今回はこのライブラリがどのように実装されているかを[コード](https://github.com/pydantic/pydantic-ai/tree/main/pydantic_graph)を追いながら見ていきます。

本文中のコード: https://github.com/hosimesi/code-for-techblogs/tree/main/pydanticai_graph

## PydanticAIとは
[PydanticAI](https://ai.pydantic.dev/)は、生成AIのアプリケーションを作るためのPythonフレームワークです。前回の記事でも取り扱ったので、詳しくは[公式ドキュメント](https://ai.pydantic.dev/)と[こちら](https://zenn.dev/hosimesi/articles/4085071b920734)を参照してください。

## pydantic-graphとは
PydanticAIの機能の一部ではありますが、PydanticAIに依存しておらず、このライブラリ単体で動作します。このライブラリのコアな考え方としては、ノード間の繋がりであるエッジを、ノードが返すオブジェクトの型ヒントとして定義しようという点です。Pydanticが得意とする型ヒントをベースにすることで、Pythonでありながらある程度型安全に複雑なワークフローやステートマシンを構築できます。公式でもある通り、高度なユースケース以外ではpydantic-graphを直接使うのではなく、PydanticAIのエージェントやマルチエージェントワークフローを使うことが推奨されています。
:::message alert
Don't use a nail gun unless you need a nail gun

If PydanticAI agents are a hammer, and multi-agent workflows are a sledgehammer, then graphs are a nail gun:
:::

## 環境構築
[uv](https://docs.astral.sh/uv/guides/install-python/)を使用して環境を構築します。まずは、必要になるpydantic-aiをインストールします。
```bash
$ uv init
```
```bash
$ uv add pydantic-graph
```
非同期実行のためのasyncioもインストールします。
```bash
$ uv add asyncio
```

## pydantic-graphを動かしてみる
まずは、簡単にpydantic-graphを動かしてみます。信号の移り変わりを表すコードを実行してみます。AIエージェントの要素は全くないコードになっていますが、LLMを叩くAgentを使った場合も基本的には同じです。
```Python:sample.py
import asyncio
from dataclasses import dataclass

from pydantic_graph import BaseNode, End, Graph, GraphRunContext


@dataclass
class TrafficState:
    current_color: str


@dataclass
class RedLight(BaseNode[TrafficState, None, str]):
    async def run(self, ctx: GraphRunContext) -> End[str]:
        print("赤信号")
        await asyncio.sleep(1)
        return End("サイクル終了")


@dataclass
class YellowLight(BaseNode[TrafficState, None, str]):
    async def run(self, ctx: GraphRunContext) -> RedLight:
        print("黄信号")
        await asyncio.sleep(1)
        return RedLight()


@dataclass
class GreenLight(BaseNode[TrafficState, None, str]):
    async def run(self, ctx: GraphRunContext) -> YellowLight:
        print("青信号")
        await asyncio.sleep(1)
        return YellowLight()


traffic_graph = Graph(
    nodes=[GreenLight, YellowLight, RedLight],
    state_type=TrafficState,
    run_end_type=str,
)


async def main():
    initial_state = TrafficState(current_color="green")

    result = await traffic_graph.run(GreenLight(), state=initial_state)

    print(f"\n最終結果: {result}")


if __name__ == "__main__":
    asyncio.run(main())
```

```text
青信号
黄信号
赤信号

最終結果: GraphRunResult(output='サイクル終了', state=TrafficState(current_color='green'))
```
このように面白い点としては、Graphを定義してrunするだけでNodeが順番に実行され、信号が変わっていくのが分かるかと思います。
このGraphにあるNodeが順番に実行されるようにするためにどういう実装がされているのでしょうか。


## pydantic-graphのコンポーネント
pydantic-graphでは上記のようにノードを繋げて、runするだけで各ノードが実行されるための主要コンポーネントがあります。以下がそのコンポーネントになります。
- `GraphRunContext`
  - 実行時に渡されるグラフレベルのコンテキストで、グラフの状態や依存関係を持ちます。
- `End`
  - グラフの実行の終了を表すためのコンポーネントです。
- `BaseNode`
  - Nodeのコアであり、通常Dataclassで定義されます。
  - runメソッドを必ず持ち、その中に処理を書き、次のノードの型ヒントを返します。
- `Graph`
  - 実行グラフであり、ワークフローのようなものです。
  - 複数のNodeから構成されます。
- `State`
  - 基本的にDataclassで構築され、GraphのStateを管理します。
- `BaseStatePersistence`
  - データの永続化のためのコンポーネントであり、オブジェクトの保存と取得を担います。

## pydantic-graphのコア
Graphを作ってrunをするだけで全てのNodeが実行される原理を実装ベースで確認します。先ほど挙げた主要コンポーネントがどのように実装され、連携しているのかをコードを追いながら確認します。

### End
Endは単なるDataclassになっています。内部ではsnapshotを取ったするメソッドが生えていますが基本的にはEnd型を返しています。
```Python:pydantic_graph/node.py
@dataclass
class End(Generic[RunEndT]):
    """Type to return from a node to signal the end of the graph."""

    data: RunEndT
    """Data to return from the graph."""

    def deep_copy_data(self) -> End[RunEndT]:
        """Returns a deep copy of the end of the run."""
        if self.data is None:
            return self
        else:
            end = End(copy.deepcopy(self.data))
            end.set_snapshot_id(self.get_snapshot_id())
            return end

    def get_snapshot_id(self) -> str:
        if snapshot_id := getattr(self, '__snapshot_id', None):
            return snapshot_id
        else:
            self.__dict__['__snapshot_id'] = snapshot_id = generate_snapshot_id('end')
            return snapshot_id

    def set_snapshot_id(self, set_id: str) -> None:
        self.__dict__['__snapshot_id'] = set_id
```
そしてGraphのコアであるGraphRun側でNodeの判定をし、Endの場合はStopAsyncIterationを呼び出しています。これによってGraph側でイテレーションを止めます。
```Python:pydantic_graph/graph.py
class GraphRun:
    def __init__(self, graph, start_node, state, ...):
        ...
    async def __anext__(self) -> BaseNode[StateT, DepsT, RunEndT] | End[RunEndT]:
        """Use the last returned node as the input to `Graph.next`."""
        if not self._is_started:
            self._is_started = True
            return self._next_node

        if isinstance(self._next_node, End):
            raise StopAsyncIteration

        return await self.next(self._next_node)
```
### BaseNode
BaseNodeはNodeのコアのクラスであり、主要な部分はrunメソッドとその戻り値の型ヒントです。型ヒントによって明示的に次のNodeを指定し、インスタンスを渡すことで、次のNodeでもrunメソッドが呼ばれます。runメソッドはとてもシンプルで、いわゆる処理のコアになるビジネスロジックを書く場所になります。つまりLLMを使って何かするエージェントの実装も基本的にはこの中で書くことができます。先ほどのGraphでrunをするとNodeが順序に従って実行される部分になります。
```Python:pydantic_graph/node.py
class BaseNode(Generic[StateT, DepsT, RunEndT]):
    async def run(
        self,
        ctx: GraphRunContext[StateT, DepsT, RunEndT],
    ) -> Union["BaseNode[StateT, DepsT, RunEndT]", End[RunEndT]]:
        raise NotImplementedError
```

### State
Stateは単なるDataclassであり、データコンテナの型を定義するだけになります。こちらはグローバルに定義しているため、値をどこからでも書き換えられます。このStateをGraph内で使えるようにGraphRunContextが必要になります。
```Python:
from dataclasses import dataclass, field

@dataclass
class MyState:
    """グラフ全体で共有される状態を定義するデータクラス"""
    counter: int = 0
    messages: list[str] = field(default_factory=list)
```

### GraphRunContext
GraphRunContextはStateなどを持った単なるDataclassですが、実行エンジンであるGraphRunが実行されるタイミングで実行されます。このオブジェクトは、現在のStateへの参照を保持しており、ノードはこのGraphRunContextを通じてState属性にアクセスし、共有データを操作します。また、Nodeが一つ実行されるたびに毎回新しくインスタンス化されます。
```Python
@dataclass
class GraphRunContext(Generic[StateT, DepsT]):
    """Context for a graph."""

    # TODO: Can we get rid of this struct and just pass both these things around..?

    state: StateT
    """The state of the graph."""
    deps: DepsT
    """Dependencies for the graph."""
```
GraphRunが次に実行すべきノード（node）のrunメソッドを呼び出す直前に生成されます。
```Python
# pydantic_graph/graph.py の GraphRun.next メソッドに相当する部分
class GraphRun(Generic[StateT, DepsT, RunEndT]):
    # ...
    async def next(
        self, node: BaseNode[StateT, DepsT, RunEndT] | None = None
    ) -> BaseNode[StateT, DepsT, RunEndT] | End[RunEndT]:
        ...

        with ExitStack() as stack:
            if self.graph.auto_instrument:
                stack.enter_context(_logfire.span('run node {node_id}', node_id=node_id, node=node))

            async with self.persistence.record_run(node_snapshot_id):
                ctx = GraphRunContext(self.state, self.deps) # <-
                self._next_node = await node.run(ctx)

        return self._next_node

```
この実装によって、各ノードは常にその実行時点での最新のStateを取得できます。

### Graph
GraphクラスはNodeのグループをまとめて、実行フロー全体を管理するオーケストレーターです。
Graph自身は実行ロジックを持たずに準備を行なって、実際の処理はGraphRunオブジェクトに任せます。
```Python:pydantic_graph/graph.py
@dataclass
class Graph(Generic[StateT, DepsT, RunEndT]):
    nodes: Sequence[type[BaseNode[StateT, DepsT, RunEndT]]]
    # ...

    async def run(
        self,
        start_node: BaseNode[StateT, DepsT, RunEndT],
        # ...
    ) -> GraphRunResult[StateT, RunEndT]:
        run = self.iter(start_node, ...)
        async for _ in run:
            pass
        return await run.result()

    def iter(
        self,
        start_node: BaseNode[StateT, DepsT, RunEndT],
        # ...
    ) -> GraphRun[StateT, DepsT, RunEndT]:
        return GraphRun(self, start_node, ...)
```
Graphの役割は実行に必要なGraphRunオブジェクトをセットアップすることになります。そして、サンプルコードで実行していたrunメソッドは、このGraphRunオブジェクトをasync forで回すためのラッパーになります。そして、IterationしたGraphRunの実行関数は先ほどGraphRunであげた`async def next`になるため、GraphRunContextを渡しつつNodeを実行できるという原理です。

## まとめ
本記事では、pydantic-graphの基本的な使い方と実装について見てみました。
pydantic-graphは、ノードの戻り値の型ヒントを利用してグラフの構造を定義し、IterationごとにNodeを実行する設計によって直感的なコードで複雑な非同期処理やステートマシンを構築できる強力なライブラリだということがわかりました。個々の状態（ノード）のロジックと、全体の遷移（グラフ）の管理を綺麗に分離できるため、見通しの良い設計が可能だなと思いました。

## 参考
- https://github.com/pydantic/pydantic-ai/tree/main/pydantic_graph
- https://ai.pydantic.dev/graph/
