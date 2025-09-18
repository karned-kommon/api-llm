#!/usr/bin/env python3

"""
Test script specifically for /v1/chat/completions endpoint on port 9010
"""

import httpx
import asyncio
import json
import time

async def test_chat_completions():
    """Test the chat completions endpoint"""

    print("🚀 Testing /v1/chat/completions endpoint on port 9010")
    print("=" * 60)

    # Test data
    test_cases = [
        {
            "name": "Simple greeting",
            "data": {
                "model": "mistral",
                "messages": [
                    {"role": "user", "content": "Hello! How are you?"}
                ],
                "temperature": 0.7,
                "max_tokens": 50
            }
        },
        {
            "name": "Code question",
            "data": {
                "model": "mistral",
                "messages": [
                    {"role": "user", "content": "Write a simple Python function to add two numbers"}
                ],
                "temperature": 0.3,
                "max_tokens": 100
            }
        },
        {
            "name": "Multi-turn conversation",
            "data": {
                "model": "mistral",
                "messages": [
                    {"role": "user", "content": "What is the capital of France?"},
                    {"role": "assistant", "content": "The capital of France is Paris."},
                    {"role": "user", "content": "What is its population?"}
                ],
                "temperature": 0.5,
                "max_tokens": 80
            }
        }
    ]

    async with httpx.AsyncClient() as client:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. {test_case['name']}")
            print("-" * 40)

            # Show request
            print("📤 Request:")
            print(json.dumps(test_case['data'], indent=2))
            print()

            try:
                start_time = time.time()

                response = await client.post(
                    "http://localhost:9010/v1/chat/completions",
                    json=test_case['data'],
                    timeout=60.0
                )

                end_time = time.time()
                response_time = end_time - start_time

                print(f"📥 Response ({response_time:.2f}s):")
                print(f"Status Code: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    print("✅ Success!")
                    print(f"Model: {result.get('model', 'N/A')}")
                    print(f"ID: {result.get('id', 'N/A')}")

                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content']
                        print(f"Assistant: {content}")

                    if 'usage' in result:
                        usage = result['usage']
                        print(f"Usage - Prompt: {usage.get('prompt_tokens', 0)}, "
                              f"Completion: {usage.get('completion_tokens', 0)}, "
                              f"Total: {usage.get('total_tokens', 0)}")
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"Response: {response.text}")

            except httpx.TimeoutException:
                print("⏰ Request timed out")
            except Exception as e:
                print(f"❌ Exception: {str(e)}")

            print()

if __name__ == "__main__":
    asyncio.run(test_chat_completions())
