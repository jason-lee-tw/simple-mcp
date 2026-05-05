help:
  @just -l


# Initialize the project
[group('Initialize')]
init:
  @cd mcp-server && \
    uv sync
  @cd chat-bot && \
    uv sync

# Run application with docker compose
[group('Docker Run App')]
up:
  @docker compose -f docker-compose.yml up --build

[group('MCP-Server: Run App')]
up-mcp:
  @cd mcp-server && \
    uv run src/main.py


# Run MCP server with MCP Inspector
[group('MCP-Server: Run App')]
up-mcp-with-inspector:
  @cd mcp-server && \
    pnpx @modelcontextprotocol/inspector uv run src/main.py

[group('Chat-Bot: Run App')]
up-chatbot:
  @cd chat-bot && \
    uv run src/main.py

# Run MCP unit tests
[group('Test')]
test-mcp-unit:
  @cd mcp-server && \
    uv run pytest src/

# Run Chatbot unit tests
[group('Test')]
test-chatbot-unit:
  @cd chat-bot && \
    uv run pytest src/

[group('Clean')]
clean-python:
  @rm -rf **/.venv
  @echo "'.venv' folders are deleted."
  @find . -not -path './.git/*' -type d \( -name "__pycache__" -o -name ".pytest_cache" \) -exec rm -rf {} + 2>/dev/null; find . -not -path './.git/*' -name "*.pyc" -delete
  @echo "All cached files are deleted."

[group('Clean')]
clean-temp:
  @rm -rf **/temp
  @echo "'temp' folders are deleted."

# Stop and remove docker containers and delete volumes
[group('Clean')]
down-clean:
  @docker compose -f docker-compose.yml down && \
    docker volume prune -af

[group('Clean')]
clean:
  @just clean-python clean-temp down-clean