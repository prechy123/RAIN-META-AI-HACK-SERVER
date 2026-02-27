FROM python:3.11.9-slim

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Set working directory
WORKDIR /app

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

# Expose port 8081
EXPOSE 8081


# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
# uvicorn main:app --host 0.0.0.0 --port 8081

# docker build -t alatchat-api:latest .
# docker images
# docker tag alatchat-api:latest giwabest/alatchat-api:latest
# docker push giwabest/alatchat-api:latest

# for macbook architecture
# docker build --platform linux/amd64 -t alatchat-api:latest .
# docker tag alatchat-api:latest giwabest/alatchat-api:latest
# docker push giwabest/alatchat-api:latest

