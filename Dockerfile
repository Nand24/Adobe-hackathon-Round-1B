# Adobe India Hackathon - PDF Intelligence Solution
# Multi-stage Docker build for AMD64 platform compatibility
FROM --platform=linux/amd64 python:3.11-slim

# Metadata
LABEL maintainer="Adobe Hackathon Team"
LABEL description="PDF Intelligence System for Document Outline Extraction and Persona-Driven Analysis"
LABEL version="1.0"

# Set working directory
WORKDIR /app

# Install system dependencies required for ML models and PDF processing
# gcc/g++: Required for compiling Python packages with C extensions
# wget: For downloading additional models if needed
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better Docker layer caching
# This allows pip install to be cached if requirements don't change
COPY requirements.txt .

# Install Python dependencies with optimizations
# --no-cache-dir: Reduces image size by not storing pip cache
# --upgrade: Ensures latest compatible versions
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download spaCy English language model (required for NLP processing)
# This is done in a separate layer for better caching
RUN python -m spacy download en_core_web_sm

# Copy source code (done after dependencies for better layer caching)
COPY src/ ./src/

# Create necessary directories with proper permissions
# models/: Cache directory for ML models (DistilBERT, Sentence-BERT)
# input/: Mount point for PDF input files
# output/: Mount point for JSON output files
RUN mkdir -p ./models /app/input /app/output && \
    chmod 755 ./models /app/input /app/output

# Set environment variables for Python optimization
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TOKENIZERS_PARALLELISM=false

# Health check to verify the application is ready
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import src.main; print('OK')" || exit 1

# Expose port for potential web interface (not used in hackathon)
EXPOSE 8080

# Default command for Round 1A (Adobe evaluation will override for Round 1B)
# The application supports both rounds with different parameters:
# Round 1A: Extract document outlines (title and headings H1, H2, H3)
# Round 1B: Persona-driven document analysis with insights
CMD ["python", "src/main.py", "--round", "1a", "--input", "/app/input", "--output", "/app/output"]

# =============================================================================
# DOCKER EXECUTION INSTRUCTIONS
# =============================================================================

# BUILD INSTRUCTIONS:
# docker build --platform linux/amd64 -t adobe-hackathon-solution .

# RUN INSTRUCTIONS FOR ROUND 1A (Document Outline Extraction):
# docker run --rm \
#   -v $(pwd)/input:/app/input \
#   -v $(pwd)/output:/app/output \
#   --network none \
#   adobe-hackathon-solution

# RUN INSTRUCTIONS FOR ROUND 1B (Persona-Driven Analysis):
# docker run --rm \
#   -v $(pwd)/input:/app/input \
#   -v $(pwd)/output:/app/output \
#   --network none \
#   adobe-hackathon-solution \
#   python src/main.py --round 1b --input /app/input --output /app/output --persona student

# AVAILABLE PERSONAS: student, researcher, professional

# VOLUME MOUNTS:
# - /app/input: Directory containing PDF files to process
# - /app/output: Directory where JSON results will be written

# NETWORK ISOLATION:
# --network none ensures completely offline operation as required

# PLATFORM COMPATIBILITY:
# Built specifically for linux/amd64 platform as per Adobe requirements
