# Use Python 3.12 slim image
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    git curl rclone ffmpeg libchromaprint1 && \
    rm -rf /var/lib/apt/lists/*

# Copy files
COPY app ./app
COPY tools ./tools

COPY config/.env.example ./config/.env
COPY config/log_config.json.example ./config/log_config.json

COPY alembic ./alembic
COPY alembic.ini .

COPY dockerentry.sh ./dockerentry.sh
RUN chmod +x ./dockerentry.sh


# Install Python dependencies
RUN pip install --upgrade pip && pip install app/. --no-warn-script-location

EXPOSE 8000
ENV PYTHONPATH=/app/app

# Run Command
ENTRYPOINT ["./dockerentry.sh"]