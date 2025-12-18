# Use Python 3.11 slim image as base
# Start with a base image
FROM python:3.11.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Install necessary system dependencies for building Python packages:
# 1. build-essential/gcc: Needed for C extensions (like the non-binary parts of psycopg)
# 2. libpq-dev: The PostgreSQL client library (libpq) required by psycopg
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv $VIRTUAL_ENV


# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Expose port 8000
EXPOSE 80

# Run the application
CMD ["/opt/venv/bin/python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

# docker build -t rain-meta-hack-server:1.0.[X] .
# docker images
# docker tag rain-meta-hack-server:1.0.[X] ayomide100/rain-meta-hack-server:1.0.[X]
# docker push ayomide100/rain-meta-hack-server:1.0.[X]

# for macbook architecture
# docker build --platform linux/amd64 -t rain-meta-hack-server:1.0.[X] .
# docker tag rain-meta-hack-server:1.0.[X] ayomide100/rain-meta-hack-server:1.0.[X]
# docker push ayomide100/rain-meta-hack-server:1.0.[X]