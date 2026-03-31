# Multi-stage build for nanobot

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Install uv
RUN pip install uv

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy nanobot files
COPY --chown=nonroot:nonroot nanobot /app/nanobot

# Copy nanobot-websocket-channel for webchat plugin
COPY --chown=nonroot:nonroot nanobot-websocket-channel /app/nanobot-websocket-channel

# Install nanobot, webchat plugin and project dependencies
RUN cd /app/nanobot \
    && uv pip install nanobot --system \
    && uv pip install -e /app/nanobot-websocket-channel/nanobot-webchat --system \
    && uv pip install -e . --system

# Place executables in the environment at the front of the path
ENV PATH="/usr/local/bin:$PATH"
ENV PYTHONPATH="/app/nanobot"

# Use the non-root user
USER nonroot

# Use /app as the working directory
WORKDIR /app

# Run the nanobot gateway via entrypoint
CMD ["python", "/app/nanobot/entrypoint.py"]