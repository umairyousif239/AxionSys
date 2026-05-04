import requests
from backend.config import QWEN_MODEL, MISTRAL_MODEL

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate(model: str, prompt: str, temperature: float = 0.2, think: bool = True):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 4096,
        },
        "think": think
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)

    if response.status_code != 200:
        raise RuntimeError(f"Ollama error: {response.text}")

    data = response.json()
    return data.get("response", "").strip()

def run_llm(task: str, prompt: str):
    if task == "root_cause":
        return generate(QWEN_MODEL, prompt, temperature=0.2, think=True)
    elif task == "fix":
        return generate(QWEN_MODEL, prompt, temperature=0.2, think=False)
    elif task == "rerank":
        return generate(QWEN_MODEL, prompt, temperature=0.3, think=False)
    else:
        return generate(MISTRAL_MODEL, prompt, temperature=0.3)