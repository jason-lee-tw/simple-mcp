help:
  @just -l


[group('Initialize')]
init:
  @cd mcp-server && \
    uv venv

[group('Run MCP Server')]
up-mcp:
  @cd mcp-server && \
    uv run src/main.py


[group('Run MCP Server')]
up-mcp-with-inspector:
  @cd mcp-server && \
    pnpx @modelcontextprotocol/inspector uv run src/main.py

[group('Test')]
test-mcp-unit:
  @cd mcp-server && \
    uv run pytest src/

[group('Clean')]
clean-python:
  @rm -rf **/.venv
  @echo "\`.venv\` folder is deleted."