import requests
from backend.config import QWEN_MODEL, MISTRAL_MODEL

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate(model: str, prompt: str):
    response = requests.post(OLLAMA_URL, json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })

    if response.status_code != 200:
        raise RuntimeError(f"Ollama error: {response.text}")

    data = response.json()
    return data.get("response", "")

def run_llm(task: str, prompt: str):
    if task in ["root_cause", "fix", "rerank"]:
        model = QWEN_MODEL
    else:
        model = MISTRAL_MODEL

    return generate(model, prompt)