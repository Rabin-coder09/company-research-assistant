import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("OPENROUTER_API_KEY")
headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

models_to_check = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "deepseek/deepseek-chat:free",
    "deepseek/deepseek-r1:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
]

for m in models_to_check:
    payload = {"model": m, "messages": [{"role": "user", "content": "hi"}]}
    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    print(m, "->", r.status_code, r.text[:150])
    time.sleep(2)