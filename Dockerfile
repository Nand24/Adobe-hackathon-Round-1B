FROM --platform=linux/amd64 python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy source code
COPY src/ ./src/

# Create models directory for ML model cache
RUN mkdir -p ./models

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command - Adobe will specify round when running
CMD ["python", "src/main.py", "--input", "/app/input", "--output", "/app/output"]
