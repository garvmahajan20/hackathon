import os
import sys
import requests
import json

sys.path.insert(0, os.path.abspath("."))
from backend.config import load_dotenv
load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
models_to_test = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash", "gemini-2.5-flash"]

payload = {
    "contents": [{"parts": [{"text": "Return JSON: {\"status\": \"ok\"}"}]}],
    "generationConfig": {"responseMimeType": "application/json"}
}

for m in models_to_test:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
    print(f"Testing {m}...")
    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            print("  Response:", r.json()["candidates"][0]["content"]["parts"][0]["text"].strip())
        else:
            print("  Error:", r.text[:200])
    except Exception as e:
        print(f"  Exception: {e}")
