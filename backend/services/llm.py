import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate (model: str, prompt: str):
    response = requests.post(OLLAMA_URL, json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })
    
    return response.json()["response"]

def run_llm (task: str, prompt: str):
    if task in ["root_cause", "fix"]:
        model = "qwen3.5:9b"
    else:
        model = "mistral:7b"
    
    return generate (model, prompt)