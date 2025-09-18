#!/bin/bash

# Setup script for API LLM service
set -e

echo "🚀 Setting up API LLM service..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Start services
echo "📦 Starting services with docker-compose..."
docker-compose up -d

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is ready!"
        break
    fi
    echo "   Waiting... ($((attempt + 1))/$max_attempts)"
    sleep 2
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Ollama failed to start within expected time"
    exit 1
fi

# Download default model
echo "📥 Downloading default model (llama2)..."
echo "   This may take several minutes depending on your internet connection..."
docker exec ollama ollama pull llama2

# Test the API
echo "🧪 Testing the API..."
sleep 5  # Give the API service time to start

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is healthy!"
else
    echo "⚠️  API might still be starting up. Check logs with: docker logs api-llm"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📚 Available endpoints:"
echo "   • Health check: http://localhost:8000/health"
echo "   • API docs: http://localhost:8000/docs"
echo "   • Models: http://localhost:8000/v1/models"
echo ""
echo "🔧 Useful commands:"
echo "   • View logs: docker-compose logs -f"
echo "   • Stop services: docker-compose down"
echo "   • Download more models: docker exec ollama ollama pull <model-name>"
echo ""
echo "💡 Test with:"
echo '   curl -X POST http://localhost:8000/v1/chat/completions \'
echo '     -H "Content-Type: application/json" \'
echo '     -d '"'"'{"model": "llama2", "messages": [{"role": "user", "content": "Hello!"}]}'"'"