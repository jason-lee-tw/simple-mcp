# simple-mcp

A hands-on practice for building a custom MCP server

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [uv](https://docs.astral.sh/uv/)
- [just](https://github.com/casey/just)

## Setup

```bash
just init
```

## Running the App

### Full stack (recommended)

Starts Phoenix

```bash
just up
```

### Individual services

```bash
just up-mcp        # MCP server only
just up-chatbot    # Chat-bot only
```

### MCP server with inspector UI

```bash
just up-mcp-with-inspector
```

## Testing

```bash
just test-mcp-unit       # MCP server unit tests
just test-chatbot-unit   # Chat-bot unit tests
```

## Evals (offline)

Requires Phoenix to be running (`just up`). Fetches traces and runs hallucination and relevance evaluations, writing results back to Phoenix as annotations.

```bash
cd chat-bot && uv run python src/evals/eval_runner.py
```

View results at [http://localhost:6006](http://localhost:6006).

## Cleanup

```bash
just clean        # Remove .venv and temp folders
just clean-python # Remove .venv folders only
just clean-temp   # Remove temp folders only
```
