# API LLM - OpenAI Compatible API with Ollama

A FastAPI-based service that provides an OpenAI-compatible API interface for interacting with Large Language Models through Ollama.

## Features

- 🔄 OpenAI-compatible API endpoints
- 🐳 Docker containerization with Ollama integration
- 🚀 FastAPI with automatic API documentation
- 🔧 Easy deployment with docker-compose
- 📊 Health check endpoints
- 🌐 CORS support for web applications

## Quick Start

### Prerequisites

- Docker and Docker Compose
- At least 4GB of RAM (8GB+ recommended for larger models)

### 1. Clone and Start Services

```bash
git clone <repository-url>
cd api-llm
docker-compose up -d
```

### 2. Download a Model

Once Ollama is running, download a model (this may take several minutes):

```bash
# Download a small model (recommended for testing)
docker exec ollama ollama pull llama2

# Or download other available models
docker exec ollama ollama pull mistral
docker exec ollama ollama pull codellama
```

### 3. Test the API

```bash
# Check health
curl http://localhost:8000/health

# List available models
curl http://localhost:8000/v1/models

# Send a chat completion request
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ]
  }'
```

## API Endpoints

### OpenAI Compatible Endpoints

- `GET /v1/models` - List available models
- `POST /v1/chat/completions` - Chat completions

### Additional Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## Usage Examples

### Python Client

```python
import httpx

# List models
response = httpx.get("http://localhost:8000/v1/models")
print(response.json())

# Chat completion
response = httpx.post("http://localhost:8000/v1/chat/completions", json={
    "model": "llama2",
    "messages": [
        {"role": "user", "content": "Explain quantum computing in simple terms"}
    ],
    "temperature": 0.7
})
print(response.json())
```

### Using with OpenAI Python SDK

```python
from openai import OpenAI

# Point to your local API
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-required"  # API key not required for local usage
)

response = client.chat.completions.create(
    model="llama2",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

### JavaScript/Node.js

```javascript
const response = await fetch('http://localhost:8000/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    model: 'llama2',
    messages: [
      { role: 'user', content: 'What is machine learning?' }
    ]
  })
});

const data = await response.json();
console.log(data.choices[0].message.content);
```

## Configuration

### Environment Variables

- `OLLAMA_BASE_URL`: Ollama service URL (default: `http://localhost:11434`)
- `DEFAULT_MODEL`: Default model to use (default: `llama2`)

### Docker Compose Configuration

Edit `docker-compose.yml` to customize:

- Ports
- Resource limits
- GPU support (uncomment the GPU section if you have NVIDIA GPU)
- Model volumes

## Development

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start Ollama separately:
```bash
# Install Ollama on your system or run in Docker
docker run -d -p 11434:11434 ollama/ollama
```

3. Run the API:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Building Docker Image

```bash
docker build -t api-llm .
```

## Available Models

Popular models you can use with Ollama:

- `llama2` - Meta's Llama 2 (7B parameters)
- `mistral` - Mistral 7B
- `codellama` - Code Llama for code generation
- `neural-chat` - Intel's neural chat model
- `starling-lm` - Starling language model

Download models with:
```bash
docker exec ollama ollama pull <model-name>
```

## API Documentation

Once the service is running, visit:
- Interactive API docs: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

## Troubleshooting

### Common Issues

1. **Ollama not responding**: Ensure Ollama container is running and healthy
2. **Model not found**: Download the model using `ollama pull <model-name>`
3. **Out of memory**: Use smaller models or increase available RAM
4. **Slow responses**: First requests may be slower as models load into memory

### Logs

```bash
# View API logs
docker logs api-llm

# View Ollama logs
docker logs ollama
```

## License

Apache License 2.0