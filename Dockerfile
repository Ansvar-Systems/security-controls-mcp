# Security Controls MCP Server
# Python-based MCP server with HTTP transport
# Compatible with Ansvar platform MCP client

FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy package files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install package in editable mode
RUN pip install --no-cache-dir -e .

# Install additional runtime dependencies
RUN pip install --no-cache-dir uvicorn starlette

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Security: create non-root user
RUN useradd -m -u 1001 -s /bin/bash mcp && \
    chown -R mcp:mcp /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code and data
COPY --chown=mcp:mcp src/ ./src/
COPY --chown=mcp:mcp pyproject.toml README.md ./

USER mcp

ENV PYTHONUNBUFFERED=1
ENV PORT=3000

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Start HTTP server
CMD ["python", "-m", "security_controls_mcp.http_server"]
