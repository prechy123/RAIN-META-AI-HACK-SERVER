FROM python:3.11.9-slim

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

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

# Create a non-root user first
RUN useradd -m -u 1000 appuser

# Create necessary directories (including static/charts to prevent permission error)
RUN mkdir -p static/charts logs data && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1    

# Expose port 8000
EXPOSE 8000


# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

# docker build -t rain-meta-hack-server:1.0.[X] .
# docker images
# docker tag rain-meta-hack-server:1.0.[X] ayomide100/rain-meta-hack-server:1.0.[X]
# docker push ayomide100/rain-meta-hack-server:1.0.[X]

# for macbook architecture
# docker build --platform linux/amd64 -t rain-meta-hack-server:1.0.[X] .
# docker tag rain-meta-hack-server:1.0.[X] ayomide100/rain-meta-hack-server:1.0.[X]
# docker push ayomide100/rain-meta-hack-server:1.0.[X]

