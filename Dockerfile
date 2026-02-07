# Security Controls MCP Server
# Python-based MCP server with HTTP transport
# Compatible with Ansvar platform MCP client
#
# Using Alpine for minimal CVE footprint

FROM python:3.11-alpine@sha256:6ce68f8bfbb40866c43b271be97d7fccc4f700c0af2a07d2ef3c7c7da93e1f8a AS builder

WORKDIR /app

# Install build dependencies (Alpine uses apk, not apt)
RUN apk add --no-cache gcc musl-dev

# Copy package files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Upgrade pip to fix CVE-2026-1703, install package, and fix known CVEs
RUN pip install --no-cache-dir "pip>=26.0" && \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir "jaraco.context>=6.1.0" "wheel>=0.46.2"

# Install additional runtime dependencies
RUN pip install --no-cache-dir uvicorn starlette

# Production stage - minimal Alpine image
FROM python:3.11-alpine@sha256:6ce68f8bfbb40866c43b271be97d7fccc4f700c0af2a07d2ef3c7c7da93e1f8a

WORKDIR /app

# Install curl for health checks (minimal addition)
RUN apk add --no-cache curl

# Security: create non-root user
RUN adduser -D -u 1001 mcp && \
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
