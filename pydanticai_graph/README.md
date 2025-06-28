# pydanticai-graph

blog link: https://zenn.dev/hosimesi/articles/d7ee500add9b2e

## Overview
This repository contains the sample code for the Zenn article "pydantic-graphの中を見る".
It provides an implementation example to understand the core components and execution flow of pydantic-graph, a library for creating asynchronous graphs and state machines in Python.

## Features
A simple example demonstrating the state transitions of a traffic light using pydantic-graph.

Code that helps understand the roles and interactions of core components like Graph, BaseNode, State, and GraphRunContext.

A practical implementation for delving into the internal workings of how pydantic-graph executes nodes sequentially.

## Requirements
- uv
- Python 3.8+

## Installation
1. Clone the repository:

```Bash
git clone https://github.com/hosimesi/code-for-techblogs.git
cd code-for-techblogs/pydanticai_graph
```
2. Set up the virtual environment and install dependencies using uv:
```Bash
## Initialize the environment
uv init
# Install the required packages
uv add pydantic-graph
```
Note: asyncio is part of the standard library, so no separate installation is needed.

## Usage
To run the traffic light simulation example, execute the following command:

``` Bash
python sample.py
You will see the output of the signals changing in sequence, followed by the final result of the graph execution.
```

```Plaintext
青信号
黄信号
赤信号

最終結果: GraphRunResult(output='サイクル終了', state=TrafficState(current_color='green'))
```
