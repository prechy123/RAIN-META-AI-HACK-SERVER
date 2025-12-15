# Use Python 3.11 slim image as base
FROM python:3.11.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
# set on the server

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
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