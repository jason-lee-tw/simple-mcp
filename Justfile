help:
  @just -l


[group('Initialize')]
init:
  @cd mcp-server && \
    uv venv --clear
  @cd chat-bot && \
    uv venv --clear

[group('Docker Run App')]
up:
  @docker compose -f docker-compose.yml up --build

[group('MCP-Server: Run App')]
up-mcp:
  @cd mcp-server && \
    uv run src/main.py


[group('MCP-Server: Run App')]
up-mcp-with-inspector:
  @cd mcp-server && \
    pnpx @modelcontextprotocol/inspector uv run src/main.py

[group('Chat-Bot: Run App')]
up-chatbot:
  @cd chat-bot && \
    uv run src/main.py

[group('MCP-Server: Test')]
test-mcp-unit:
  @cd mcp-server && \
    uv run pytest src/

[group('Chat-Bot: Test')]
test-chatbot-unit:
  @cd chat-bot && \
    uv run pytest src/

[group('Clean')]
clean-python:
  @rm -rf **/.venv
  @echo "'.venv' folders are deleted."

[group('Clean')]
clean-temp:
  @rm -rf **/temp
  @echo "'temp' folders are deleted."

[group('Clean')]
clean:
  @just clean-python clean-temp