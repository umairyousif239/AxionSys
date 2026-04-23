from fastapi import FastAPI
from backend.services.llm import run_llm

app = FastAPI()

@app.get("/")
def root():
    return {"message": "AxionSys is Running!"}

@app.get("/test_llm")
def test_llm():
    prompt = "Explain what a null pointer exception is."
    response = run_llm("general", prompt)
    
    return {
        "response": response
    }