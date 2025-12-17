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

ENV MONGO_URL=mongodb+srv://admin:admin@cluster0.vvfdq9t.mongodb.net/?appName=Cluster0 \
    POSTGRES_DB_URL=postgresql://sharpchat:tKzGpx2fMJVef0RxMSYP37VkpSTsF5W3@dpg-d4v9n1qli9vc73djt790-a.oregon-postgres.render.com/sharpchat_ai \
    PINECONE_API_KEY=pcsk_5UNSG5_75jArK38MLscRAMioss7taqWLJKTPtUbTCmkwFedNbnfyaGaiEgKppFP4erHGjV \
    KB_INDEX=sharply-chat \
    PINECONE_CLOUD=aws \
    PINECONE_REGION=us-east-1 \
    TWILIO_ACCOUNT_SID=AC4571de225ede8776ca6f8809675c29f1 \
    TWILIO_AUTH_TOKEN=159a2589db0ac20ac56b44efd04f76b9 \
    TWILIO_FROM_NUMBER=+14155238886 \
    GROQ_API_KEY=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 \
    LLAMA_MODEL=llama-3.3-70b-versatile \
    TEMPERATURE=0.7 \
    MAX_TOKENS=2048 \
    HUGGINGFACE_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
    EMAIL_HOST=smtp.gmail.com \
    EMAIL_PORT=587 \
    EMAIL_USER=sharpchatai@gmail.com \
    EMAIL_PASSWORD=sdyafsniyuepodqm \
    EMAIL_FROM=sharpchatai@gmail.com \
    EMAIL_TO=giwaibrahim98@gmail.com,ibrahimgiwa.abiola@gmail.com \
    EMAIL_PORT_SSL=465 \
    ENDPOINT_AUTH_KEY=BH8ebZqeqrUehYIFnIubWciuNAmqS/uZ9RetIObuAoU=

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["/opt/venv/bin/python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# docker build -t rain-meta-hack-server:1.0.[X] .
# docker images
# docker tag rain-meta-hack-server:1.0.[X] ayomide100/rain-meta-hack-server:1.0.[X]
# docker push ayomide100/rain-meta-hack-server:1.0.[X]

# for macbook architecture
# docker build --platform linux/amd64 -t rain-meta-hack-server:1.0.[X] .
# docker tag rain-meta-hack-server:1.0.[X] ayomide100/rain-meta-hack-server:1.0.[X]
# docker push ayomide100/rain-meta-hack-server:1.0.[X]