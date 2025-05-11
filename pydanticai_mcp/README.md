# pydanticai-mcp

blog link: https://zenn.dev/articles/4fbd8d43d1f11a

## Overview
Implementation examples of Model Context Protocol (MCP) using PydanticAI. This project demonstrates how to use PydanticAI as an MCP client and how to implement PydanticAI within an MCP server.

## Features
- PydanticAI implementation as an MCP client
- PydanticAI implementation as an MCP server
- Integration with Notion MCP server
- Example implementation of an MCP server that responds in Kansai dialect

## Requirements
- uv
- Node.js (for Notion MCP server)

## Installation
1. Clone the repository
```bash
git clone https://github.com/hosimesi/code-for-techblogs.git
cd code-for-techblogs/pydanticai_mcp
```

2. Install dependencies
```bash
uv sync
```

3. Set up environment variables
Copy `.env.example` to create `.env` and set the required environment variables:
```bash
cp .env.example .env
```

Set the following in your `.env` file:

# Pre-requirements
1. Install kind, kubectl, kustomize, poetry
    ```bash
    $ pip list | grep poetry
    poetry                      1.7.1
    poetry-core                 1.8.1
    poetry-plugin-export        1.6.0
    ```
    ```bash
    $ brew install kind
    ```
    ```bash
    $ brew install kubectl
    ```
    ```bash
    $ brew install kustomize
    ```

# How to run in local.
1. Auth gcloud.
    ```Makefile
    $ make login
    ```
2. Create gcp resource.
    ```bash
    $ terraform apply -var-file=<variables file>
    ```
3. Build image.
    ```bash
    $ make build
    ```
4. Push image.
    ```bash
    $ make push
    ```
5. Create kind.
    ```bash
    $ make kind
    ```
6. Install argo.
    ```bash
    $ make argo-install
    ```
7. Create secret.
    ```bash
    $ make create-secret
    ```
8. Deploy workflow.
    ```bash
    $ make deploy
    ```
9. Set notify.
    ```bash
    $ make notify
    ```
10. Upload titanic files.
    ```bash
    $ make upload
    ```


