# Multi-stage build with uv (same pattern as backend/Dockerfile)

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Disable Python downloads
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy workspace pyproject.toml and uv.lock from the workspace context
COPY --from=workspace pyproject.toml uv.lock /app/
COPY pyproject.toml /app/nanobot/pyproject.toml

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --package nanobot

# Copy the rest of the application
COPY . /app/nanobot

# Finalize the sync
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package nanobot

# ---
# Stage 2: use a final image without uv
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy the application from the builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/nanobot"

# Use the non-root user
USER nonroot

# Use /app as the working directory
WORKDIR /app

# Run the nanobot gateway via entrypoint
CMD ["python", "/app/nanobot/entrypoint.py"]
