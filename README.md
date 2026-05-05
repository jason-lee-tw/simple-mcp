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

### Prerequisites

- Create `.env` in `./chatbot/` folder by following `./chatbot/.env.template`.

### Running application with docker (recommended)

Step 1 - Run the application

```bash
just up
```

Step 2 - Visit Services

- Visit chatbot Swagger page at `http://localhost:3001/docs`. Note that the port is listed in the `.env`.
  - You can use the endpoint `POST /chat` to send request to chatbot.
- Visit Pheonix dashboard at `http://localhost:6006`.

### Running MCP server with inspector UI

To inspect the MCP server only, you can use MCP inspector to run the MCP server.

```bash
just up-mcp
```

## Testing

```bash
just test-mcp-unit       # MCP server unit tests
just test-chatbot-unit   # Chat-bot unit tests
```

## Evals (offline)

Requires Phoenix to be running (`just up`). Fetches traces and runs hallucination and relevance evaluations, writing results back to Phoenix as annotations.

```bash
just test-llm-output
```

View results at [http://localhost:6006](http://localhost:6006).

## Clean Up

```bash
just clean        # Clean all resources
just clean-python # Remove .venv folders only
just clean-temp   # Remove temp folders only
just down-clean   # Stop & delete all docker containers from this project and clean up the docker volumes
```

## Other useful commands

### List all Just available commands

```sh
just help
```
