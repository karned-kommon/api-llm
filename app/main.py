from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import asyncio

app = FastAPI(
    title="API LLM - OpenAI Compatible API",
    description="OpenAI-compatible API service using Ollama",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama2")

# Pydantic models for OpenAI compatibility
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "ollama"

@app.get("/")
async def root():
    return {"message": "API LLM - OpenAI Compatible API using Ollama"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                return {"status": "healthy", "ollama": "connected"}
            else:
                return {"status": "unhealthy", "ollama": "disconnected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/v1/models")
async def list_models():
    """List available models - OpenAI compatible endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                ollama_models = response.json()
                models = []
                for model in ollama_models.get("models", []):
                    models.append(ModelInfo(
                        id=model["name"],
                        created=0  # Ollama doesn't provide creation timestamp
                    ))
                return {"object": "list", "data": models}
            else:
                raise HTTPException(status_code=503, detail="Ollama service unavailable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching models: {str(e)}")

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Chat completions endpoint - OpenAI compatible"""
    try:
        # Convert OpenAI format to Ollama format
        ollama_messages = []
        for msg in request.messages:
            ollama_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        ollama_request = {
            "model": request.model,
            "messages": ollama_messages,
            "stream": False,
            "options": {}
        }
        
        if request.temperature is not None:
            ollama_request["options"]["temperature"] = request.temperature
        
        if request.max_tokens is not None:
            ollama_request["options"]["num_predict"] = request.max_tokens

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=ollama_request
            )
            
            if response.status_code == 200:
                ollama_response = response.json()
                
                # Convert Ollama response to OpenAI format
                openai_response = {
                    "id": f"chatcmpl-{hash(str(ollama_response))}"[:29],
                    "object": "chat.completion",
                    "created": int(ollama_response.get("created_at", 0)),
                    "model": request.model,
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": ollama_response["message"]["content"]
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": ollama_response.get("prompt_eval_count", 0),
                        "completion_tokens": ollama_response.get("eval_count", 0),
                        "total_tokens": ollama_response.get("prompt_eval_count", 0) + ollama_response.get("eval_count", 0)
                    }
                }
                
                return openai_response
            else:
                error_detail = response.text if response.text else "Ollama service error"
                raise HTTPException(status_code=response.status_code, detail=error_detail)
                
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Cannot connect to Ollama: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)