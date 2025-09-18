# Multi-stage build to download Mistral model and create optimized image

# Stage 1: Download Mistral model
FROM ollama/ollama:latest as model-downloader

# Create directory for models
RUN mkdir -p /tmp/ollama

# Start Ollama in background and download Mistral model
RUN ollama serve & \
    sleep 10 && \
    ollama pull mistral && \
    sleep 5 && \
    pkill ollama

# Stage 2: Build API application
FROM python:3.11-slim as api-builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy application code
COPY app/ ./app/

# Stage 3: Final runtime image
FROM python:3.11-slim

WORKDIR /app

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash app

# Copy Python dependencies from builder
COPY --from=api-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=api-builder /usr/local/bin /usr/local/bin

# Copy application
COPY --from=api-builder /app /app

# Copy Ollama models from first stage
COPY --from=model-downloader /root/.ollama /app/.ollama

# Set ownership
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]