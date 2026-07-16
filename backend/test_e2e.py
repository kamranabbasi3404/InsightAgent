"""Quick end-to-end test of the chat API."""
import requests
import json
import sys

# Reconfigure stdout to use UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


url = "http://localhost:8000/api/chat"

# Test 1: No-retrieval query (greeting)
print("=" * 60)
print("TEST 1: Conversational query (no_retrieval route)")
print("=" * 60)
resp = requests.post(url, json={"query": "Hello, what can you do?"})
data = resp.json()

if resp.status_code == 200:
    print(f"Route: {data.get('route', 'N/A')}")
    print(f"Answer: {data.get('answer', 'N/A')[:300]}")
    print(f"Trace steps: {len(data.get('trace', []))}")
    for step in data.get("trace", []):
        print(f"  {step.get('icon', '')} {step.get('label', '')}: {step.get('summary', '')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {resp.status_code} - {data}")

print()

# Test 2: Web-only query
print("=" * 60)
print("TEST 2: Web search query (web_only route)")
print("=" * 60)
resp = requests.post(url, json={"query": "What is the current population of Pakistan in 2026?"})
data = resp.json()

if resp.status_code == 200:
    print(f"Route: {data.get('route', 'N/A')}")
    print(f"Answer: {data.get('answer', 'N/A')[:300]}")
    print(f"Citations: {len(data.get('citations', []))}")
    print(f"Trace steps: {len(data.get('trace', []))}")
    for step in data.get("trace", []):
        print(f"  {step.get('icon', '')} {step.get('label', '')}: {step.get('summary', '')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {resp.status_code} - {data}")
