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
