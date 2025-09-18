#!/usr/bin/env python3

"""
Demo script for testing API LLM service with a mock Ollama response
"""

import httpx
import asyncio
import json

async def demo_chat_completion():
    """Demo chat completion functionality"""
    
    # Sample request that would work with a real Ollama instance
    request_data = {
        "model": "mistral",
        "messages": [
            {"role": "user", "content": "Hello! How are you today?"}
        ],
        "temperature": 0.7
    }
    
    print("🚀 Demo API LLM Chat Completion")
    print("=" * 50)
    print(f"📝 Request:")
    print(json.dumps(request_data, indent=2))
    print()
    
    print("💡 To test with real Ollama, run:")
    print("   docker-compose up -d")
    print("   docker exec ollama ollama pull mistral")
    print("   curl -X POST http://localhost:8000/v1/chat/completions \\")
    print("     -H 'Content-Type: application/json' \\")
    print(f"     -d '{json.dumps(request_data)}'")
    print()
    
    # Check if local API is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ API is running locally at http://localhost:8000")
                print("📚 Visit http://localhost:8000/docs for interactive documentation")
            else:
                print("⚠️  API is running but not healthy")
    except httpx.RequestError:
        print("ℹ️  API is not running. Start it with: uvicorn app.main:app --reload")
    
    print()
    print("🔗 OpenAI-compatible endpoints:")
    print("   GET  /v1/models           - List available models")
    print("   POST /v1/chat/completions - Chat completions")
    print("   GET  /health              - Health check")
    print("   GET  /docs                - API documentation")

if __name__ == "__main__":
    asyncio.run(demo_chat_completion())