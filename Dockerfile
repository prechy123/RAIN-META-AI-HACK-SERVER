# Use Python 3.11 slim image as base
FROM python:3.14.0-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV MONGO_URL=mongodb+srv://admin:admin@cluster0.vvfdq9t.mongodb.net/?appName=Cluster0

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
