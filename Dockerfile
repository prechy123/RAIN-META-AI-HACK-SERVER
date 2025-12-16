# Use Python 3.11 slim image as base
# Start with a base image
FROM python:3.11.9-slim

# Install necessary system dependencies for building Python packages:
# 1. build-essential/gcc: Needed for C extensions (like the non-binary parts of psycopg)
# 2. libpq-dev: The PostgreSQL client library (libpq) required by psycopg
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
# Using --no-cache-dir is good practice in Docker to keep the image small
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# docker build -t rain-meta-hack-server:1.0.[X] .
# docker images
# docker tag rain-meta-hack-server:1.0.[X] ayomide100/rain-meta-hack-server:1.0.[X]
# docker push ayomide100/rain-meta-hack-server:1.0.[X]

# for macbook architecture
# docker build --platform linux/amd64 -t rain-meta-hack-server:1.0.[X] .
# docker tag rain-meta-hack-server:1.0.[X] ayomide100/rain-meta-hack-server:1.0.[X]
# docker push ayomide100/rain-meta-hack-server:1.0.[X]