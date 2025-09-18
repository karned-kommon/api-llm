#!/usr/bin/env python3

"""
Test script for API LLM service
"""

import sys
import asyncio
import json
from app.main import app
from fastapi.testclient import TestClient

def test_basic_endpoints():
    """Test basic API endpoints"""
    client = TestClient(app)
    
    print("🧪 Testing API endpoints...")
    
    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200
    print("✅ Root endpoint working")
    
    # Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    print("✅ Health endpoint working")
    
    # Test models endpoint (will fail without Ollama, but should return proper error)
    response = client.get("/v1/models")
    print(f"📋 Models endpoint status: {response.status_code}")
    
    print("✅ All basic tests passed!")

if __name__ == "__main__":
    try:
        test_basic_endpoints()
        print("🎉 API tests completed successfully!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)