# Use Python 3.12 slim image
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    git curl rclone ffmpeg libchromaprint1 && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency files first for caching
COPY pyproject.toml ./
COPY .python-version ./

# Install Python dependencies
RUN pip install --upgrade pip && pip install . --root-user-action=ignore

# Copy the rest of the code
COPY covers ./covers
COPY scripts ./scripts
COPY *.py ./

EXPOSE 8000

# Run Command
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
