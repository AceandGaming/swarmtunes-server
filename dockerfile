# Use Python 3.12 slim image
FROM python:3.12-slim

# UV
COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /uvx /bin/

WORKDIR /app

# Configer UV
ENV UV_NO_DEV=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install dependencies
RUN apt-get update && apt-get install -y \
    git curl rclone ffmpeg libchromaprint1 && \
    rm -rf /var/lib/apt/lists/*

# Copy files
COPY src ./src

COPY pyproject.toml .
COPY uv.lock .
COPY .python-version .

COPY config/.env.example ./config/.env
COPY config/log_config.json.example ./config/log_config.json

COPY alembic ./alembic
COPY alembic.ini .

COPY dockerentry.sh ./dockerentry.sh
RUN chmod +x ./dockerentry.sh


# Install Python dependencies
RUN uv sync --locked

EXPOSE 8000

# Run Command
ENTRYPOINT ["./dockerentry.sh"]