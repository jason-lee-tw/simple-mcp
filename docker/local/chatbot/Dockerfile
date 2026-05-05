FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

ENV PYTHONPATH=/app/src

# Install mcp-server dependencies
COPY mcp-server/pyproject.toml mcp-server/uv.lock /mcp-server/
RUN cd /mcp-server && uv sync --frozen --no-dev
COPY mcp-server/src /mcp-server/src

# Install chat-bot dependencies
COPY chat-bot/pyproject.toml chat-bot/uv.lock ./
RUN uv sync --frozen --no-dev

# Copy chat-bot source
COPY chat-bot/src ./src

ENV PORT=3001

ENV RELOAD=true

CMD ["sh", "-c", "uv run src/main.py"]
