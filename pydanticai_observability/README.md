# pydanticai-observability

blog link: https://zenn.dev/hosimesi/articles/4085071b920734

## Overview
A simple agent-based application using Pydantic AI with Logfire observability integration. This project demonstrates how to create an interactive chat agent that can search the web for information.

## Features
- Interactive chat interface
- Web search capabilities using Gemini 2.0 Flash Lite
- Logfire integration for observability
- Message history tracking

## Requirements
- uv

## Installation
1. Change directory
```bash
cd path/to/pydanticai_observability
```

2. Install dependencies
```bash
uv sync
```

3. Set up environment variables
Create a `.env` file with the following content:
```
LOGFIRE_TOKEN=your_logfire_token
GEMINI_API_KEY=your_api_key
```

## Usage
Run the main application:
```bash
uv run python src/main.py
```

The application will start an interactive chat session where you can enter queries. The agent will search the web for information and provide responses. The chat history is maintained throughout the session.

To exit the application, press Ctrl+C.
