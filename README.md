# AxionSys

## Local AI Systems Debugging Intelligence

---

## Overview

AxionSys is a local-first AI system that performs hybrid retrieval over codebases and logs, applies reranking for precision, and generates structured root-cause analysis and fixes.

It is designed to operate fully on consumer hardware with adaptive model routing.

---

## Key Capabilities

- Hybrid Retrieval (BM25 + Vector Search)
- Reranked context selection
- Structured root cause analysis
- Automated fix generation (diff output)
- Hardware-aware inference execution
- Full local deployment (no cloud dependency)

---

## Architecture

User Query  
→ Hybrid Retrieval (BM25 + FAISS)  
→ Reranking Layer  
→ Context Builder  
→ LLM Router (Mistral / Qwen 9B)  
→ Structured Output Engine  
→ Frontend Visualization  

---

## Models

- Mistral / LLaMA 3 → fast reasoning
- Qwen 9B → deep analysis & fixes

---

## Features

### 1. Code Understanding
Ask questions about any repository.

### 2. Log Analysis
Cluster and summarize system logs.

### 3. Root Cause Engine
Identify system failures with explanations.

### 4. Fix Generator
Generate code patches in diff format.

### 5. Hardware Panel
Show system usage and inference performance.

### 6. Execution Trace View
Visualize AI reasoning pipeline step-by-step.

---

## Technical Stack

- FastAPI
- FAISS
- BM25 (sparse retrieval)
- Sentence Transformers
- Ollama (local LLM runtime)
- Mistral / Qwen models

---

## Running Locally

```bash
ollama pull mistral:7b
ollama pull llama3:8b
ollama pull qwen:9b

uvicorn backend.main:app --reload