# ---------- 1) Builder: resolve & install deps ----------
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
WORKDIR /app

# Faster, deterministic builds
# Tells uv to compile Python files to bytecode for faster startup
# Ensures uv copies files instead of creating symlinks
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copy only project metadata first to maximize layer caching
COPY pyproject.toml ./

# Install dependencies (with caching)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --no-dev

# Now bring in your app code (doesn't bust dep cache unless these files change)
COPY app/ ./app/

# After copying the full application, we install the project itself
# This may not be necessary if we don't have a local package to install
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# ---------- 2) Final runtime: minimal image with only deps + app ----------
FROM python:3.13-slim-bookworm AS runtime

# Set Python environment variables for runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a non-root user with proper shell
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m -d /app -s /bin/bash appuser

WORKDIR /app

# Copy the virtual environment and application from builder
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appgroup /app /app

USER appuser

# Health check using curl (lightweight)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Expect PORT provided by runtime (default 8080)
ENV PORT=8080
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
