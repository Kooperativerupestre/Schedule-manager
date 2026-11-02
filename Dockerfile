FROM python:3.14-slim AS base

# Copy the uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Configure uv behavior
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1

# Copy dependency definition files first for efficient caching
COPY pyproject.toml uv.lock ./
COPY alembic.ini ./
COPY migrations ./migrations
COPY src ./src
COPY tests ./tests

# Development stage (includes dev dependencies for linting, typing, and testing)
FROM base AS dev
COPY --from=node:22-slim /usr/local/bin/node /usr/local/bin/node
RUN uv sync --frozen
ENV PATH="/app/.venv/bin:$PATH"
CMD ["fastapi", "run", "src/schedule_manager/main.py", "--port", "8000", "--host", "0.0.0.0"]

# Production stage (only production dependencies)
FROM base AS prod
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["fastapi", "run", "src/schedule_manager/main.py", "--port", "8000", "--host", "0.0.0.0"]
