# Use Python 3.11 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install basic dependencies (if needed)
RUN apt-get update && apt-get install -y \
    git curl rclone ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency files first for caching
COPY pyproject.toml ./
COPY .python-version ./

# Install Python dependencies
RUN pip install --upgrade pip && pip install .

# Copy the rest of the code
COPY covers ./covers
COPY scripts ./scripts
COPY *.py ./

# Expose port if your server runs HTTP
EXPOSE 8000

# Run Command
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
