![Alt Text](resources/images/banner.gif)

> Local-first AI debugging intelligence. Drop in a repo and an error log — AxionSys tells you exactly what's broken, why, and gives you the fix.

## Overview

AxionSys is a local-first AI system that ingests codebases and error logs, performs hybrid retrieval across code chunks, applies LLM reranking for precision, and generates structured root-cause analysis with actionable code fixes.

Built and tested entirely on an AMD Radeon RX 9060 XT 16GB. No cloud. No NVIDIA. No compromise.

## How It Works

| Stage | Component |
|---|---|
| 1 | Log / Traceback / Error Message |
| 2 | Log Parser — query extraction |
| 3 | Hybrid Retrieval — BM25 + FAISS |
| 4 | LLM Reranker — Qwen 3.5 9B |
| 5 | Dynamic Fusion Scoring |
| 6 | Root Cause Engine — Qwen 3.5 9B |
| 7 | Fix Generator — unified diff |
| 8 | Structured JSON Output |

## Key Capabilities

- **Hybrid Retrieval** — combines dense vector search (FAISS) with sparse keyword search (BM25) for higher recall and precision than either alone
- **LLM Reranking** — reranks retrieved chunks using Qwen 3.5 9B with dynamic alpha/beta fusion scoring that adapts based on retrieval agreement
- **Multi-format Log Parsing** — accepts Python tracebacks, `.log` files, and free-form error messages and extracts structured queries automatically
- **Causal Chain Reasoning** — traces bug propagation across multiple files rather than identifying symptoms in isolation
- **Unified Diff Output** — generates git-style patches ready to apply directly to your codebase
- **Fully Local** — runs entirely on consumer AMD hardware with no cloud dependency

## Demo Flow

1. Point AxionSys at a repository
2. Paste an error log or traceback
3. Receive:
   - Root cause with causal chain reasoning
   - Affected files ranked by relevance
   - Concrete fix in unified diff format
   - Confidence scores for both diagnosis and fix

## Technical Stack

| Component | Technology |
|---|---|
| API | FastAPI |
| Vector Search | FAISS |
| Keyword Search | BM25 |
| Embeddings | Sentence Transformers |
| LLM Runtime | Ollama |
| Reasoning Model | Qwen 3.5 9B |
| Fast Tasks | Mistral 7B |
| Hardware | AMD Radeon RX 9060 XT 16GB |

## Architecture

```
backend/
├── services/
│   ├── loader.py               # repo file loading
│   ├── chunker.py              # code chunking
│   ├── embedding.py            # sentence transformer embeddings
│   ├── vector_store.py         # FAISS index
│   ├── bm25_store.py           # BM25 index
│   ├── hybrid_retriever.py     # fused retrieval
│   ├── reranker.py             # LLM reranking
│   ├── root_cause.py           # causal chain analysis
│   ├── fix_generator.py        # unified diff generation
│   ├── log_parser.py           # log/traceback parsing
│   └── llm.py                  # model router
pipelines/
├── ingest_repo.py              # repo ingestion pipeline
├── ingest_logs.py              # log ingestion pipeline
└── analyze.py                  # full analysis pipeline
```

## Running Locally

### Prerequisites

```bash
# Install Ollama — https://ollama.com
ollama pull qwen3.5:9b
ollama pull mistral:7b
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the API

```bash
uvicorn backend.main:app --reload
```

### Run Analysis Directly

```bash
python -m pipelines.analyze
```

## Sample Output

```
Error:   AttributeError: 'NoneType' object has no attribute 'cursor'

Root Cause:
  ConnectionPool.get_connection() returns None when the connections
  list is empty, causing connect_db() to attempt calling .cursor()
  on None, which raises an AttributeError

Affected Files: connection.py, pool.py
Confidence:     0.95

Fix (pool.py):
--- pool.py
+++ pool.py
@@ -1,8 +1,12 @@
 class ConnectionPool:
     def __init__(self):
         self.connections = []

     def get_connection(self):
-        if not self.connections:
-            return None  # BUG: should create connection instead
+        if not self.connections:
+            conn = self._create_connection()
+            self.connections.append(conn)
+            return conn

         return self.connections.pop()

Fix Confidence: 0.90
```

## Hardware

Built and daily-driven on **AMD Radeon RX 9060 XT 16GB**.  
All inference runs locally via Ollama with ROCm backend.  
No cloud API calls. No data leaves your machine.
