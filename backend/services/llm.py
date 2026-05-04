import requests
from backend.config import QWEN_MODEL, MISTRAL_MODEL

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate(model: str, prompt: str, temperature: float = 0.2):
    response = requests.post(OLLAMA_URL, json={
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    })

    if response.status_code != 200:
        raise RuntimeError(f"Ollama error: {response.text}")

    data = response.json()
    return data.get("response", "")

def run_llm(task: str, prompt: str):
    """
    Router for different LLM tasks
    """
    if task in ["root_cause", "fix"]:
        model = QWEN_MODEL
        temperature = 0.2   # stable reasoning

    elif task == "rerank":
        model = QWEN_MODEL
        temperature = 0.0   # deterministic ordering

    else:
        model = MISTRAL_MODEL
        temperature = 0.3

    return generate(model, prompt, temperature)