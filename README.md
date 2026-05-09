![Alt Text](resources/images/banner.gif)

> Local-first AI debugging intelligence. Drop in a repo and an error log — AxionSys tells you exactly what's broken, why, and gives you the fix.

## Overview

AxionSys is a local-first AI system that ingests codebases and error logs, performs hybrid retrieval across code chunks, applies LLM reranking for precision, and generates structured root-cause analysis with actionable code fixes.

Built and tested entirely on an AMD Radeon RX 9060 XT 16GB. No cloud. No NVIDIA. No compromise.

## How It Works

| Stage | Component |
|---|---|
| 1 | Log / Traceback / Error Message |
| 2 | Log Parser — traceback, log error, and free-form parsing with query extraction |
| 3 | Traceback-aware file pinning — files mentioned in the traceback are prioritised |
| 4 | Hybrid Retrieval — BM25 + FAISS across all code chunks |
| 5 | LLM Reranker — Qwen 3.5 9B |
| 6 | Dynamic Fusion Scoring — adaptive alpha/beta weighting |
| 7 | Root Cause Engine — Qwen 3.5 9B with causal chain reasoning |
| 8 | Fix Generator — unified diff output |
| 9 | Structured JSON Output |

## Key Capabilities

- **Hybrid Retrieval** — combines dense vector search (FAISS) with sparse keyword search (BM25) for higher recall and precision than either alone
- **Traceback-aware Pinning** — files explicitly mentioned in the traceback are pinned to the top of retrieval results with maximum score, ensuring ground-truth files always reach the LLM
- **LLM Reranking** — reranks retrieved chunks using Qwen 3.5 9B with dynamic alpha/beta fusion scoring that adapts based on agreement between hybrid and rerank scores
- **Multi-format Log Parsing** — accepts Python tracebacks (including Python 3.11+ `~~~`/`^^^` markers), `.log` files, and free-form error messages, extracting structured queries automatically
- **Causal Chain Reasoning** — traces bug propagation across multiple files with call chain visualization showing OK / BUG / CRASH status per node
- **Unified Diff Output** — generates git-style patches ready to apply directly to your codebase
- **GitHub URL Ingestion** — paste a GitHub URL directly; repos are cloned once and cached locally so repeated runs skip the download
- **Session Management** — each ingestion creates an isolated session with its own vector index, BM25 store, and results
- **Fully Local** — runs entirely on consumer AMD hardware with no cloud dependency

## Demo Flow

1. Point AxionSys at a local repository path or GitHub URL
2. Paste an error log or traceback
3. Receive:
   - Root cause with causal chain reasoning
   - Call chain visualization across affected files
   - Concrete fix in unified diff format
   - Confidence scores for both diagnosis and fix
   - Top retrieved files ranked by hybrid, rerank, and final score
   - Full pipeline execution trace

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
| Frontend | React + Vite |
| Hardware | AMD Radeon RX 9060 XT 16GB |

## Architecture

```
backend/
├── services/
│   ├── loader.py               # repo file loading
│   ├── chunker.py              # code chunking with overlap
│   ├── embedding.py            # sentence transformer embeddings
│   ├── vector_store.py         # FAISS index
│   ├── bm25_store.py           # BM25 index
│   ├── hybrid_retriever.py     # fused BM25 + FAISS retrieval
│   ├── reranker.py             # LLM reranking
│   ├── root_cause.py           # causal chain analysis
│   ├── fix_generator.py        # unified diff generation
│   ├── log_parser.py           # traceback + log + free-form parsing
│   └── llm.py                  # model router
pipelines/
├── ingest_repo.py              # repo ingestion pipeline
├── ingest_logs.py              # log ingestion pipeline
└── analyze.py                  # full analysis pipeline
frontend/
└── src/
    ├── App.jsx
    └── components/
        ├── IngestStep.jsx      # repo ingestion UI
        ├── AnalyzeStep.jsx     # log input + execution trace
        └── ResultsStep.jsx     # root cause, chain, fix, files, trace tabs
```

## Running Locally

### Prerequisites

```bash
# Install Ollama — https://ollama.com
ollama pull qwen3:9b
ollama pull mistral:7b
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start the API

```bash
uvicorn backend.main:app --reload
```

### Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

### Run Analysis Directly

```bash
python -m pipelines.analyze
```

## Sample Output

```
Error:   AttributeError: 'NoneType' object has no attribute 'get'

Root Cause:
  In cache.py, self.store is initialized to None in __init__,
  but get() calls self.store.get(key) without checking if store
  exists. When get() is called on an uninitialized Cache instance,
  it raises AttributeError.

Affected Files: cache.py, db.py
Confidence:     0.95

Call Chain:
  [OK]    db.py        __init__()
  [OK]    cache.py     __init__()
  [BUG]   cache.py     get()
  [CRASH] cache.py     get()

Fix (cache.py):
--- cache.py
+++ cache.py
@@ -1,7 +1,7 @@
 class Cache:
     def __init__(self):
-        self.store = None
+        self.store = {}

     def get(self, key):
         return self.store.get(key)

Fix Confidence: 0.90
```

## Hardware

Built and daily-driven on **AMD Radeon RX 9060 XT 16GB**.  
All inference runs locally via Ollama with ROCm backend.  
No cloud API calls. No data leaves your machine.