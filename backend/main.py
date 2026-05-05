from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import uuid
import os
import shutil
import subprocess

from pipelines.ingest_repo import ingest
from pipelines.analyze import analyze
from backend.services.bm25_store import BM25Store

app = FastAPI(
    title="AxionSys",
    description="Local-first AI debugging intelligence",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}

class IngestRequest(BaseModel):
    repo_path: str = ""
    github_url: str = ""

class AnalyzeRequest(BaseModel):
    session_id: str
    log_text: str

def clone_github_repo(url: str) -> str:
    repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
    clone_path = f"data/repos/{repo_name}_{uuid.uuid4().hex[:6]}"
    os.makedirs("data/repos", exist_ok=True)

    result = subprocess.run(
        ["git", "clone", url, clone_path],
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        raise RuntimeError(f"Git clone failed: {result.stderr}")

    return clone_path


@app.get("/health")
def health():
    return {"status": "ok", "service": "AxionSys"}


@app.post("/ingest", responses={
    400: {"description": "Invalid input or repo not found"},
    500: {"description": "Ingestion failed"}
})
def ingest_repo(req: IngestRequest):
    if not req.repo_path and not req.github_url:
        raise HTTPException(status_code=400, detail="Provide either repo_path or github_url")

    cloned_path = None

    try:
        if req.github_url:
            repo_path = clone_github_repo(req.github_url)
            cloned_path = repo_path
        else:
            repo_path = req.repo_path
            if not os.path.exists(repo_path):
                raise HTTPException(status_code=400, detail=f"Repo path not found: {repo_path}")

        store, docs, meta = ingest(repo_path)

        bm25 = BM25Store()
        bm25.build(docs)

        session_id = uuid.uuid4().hex
        sessions[session_id] = {
            "store": store,
            "docs": docs,
            "meta": meta,
            "bm25": bm25,
            "repo_path": repo_path,
            "cloned_path": cloned_path,
            "chunk_count": len(docs)
        }

        return {
            "session_id": session_id,
            "chunk_count": len(docs),
            "repo_path": repo_path,
            "status": "ingested"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze", responses={
    404: {"description": "Session not found"},
    500: {"description": "Analysis failed"}
})
def analyze_logs(req: AnalyzeRequest):
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found. Run /ingest first.")

    session = sessions[req.session_id]

    try:
        results = analyze(
            repo_path=session["repo_path"],
            log_text=req.log_text,
            store=session["store"],
            docs=session["docs"],
            meta=session["meta"],
            bm25=session["bm25"]
        )

        sessions[req.session_id]["results"] = results

        return {
            "session_id": req.session_id,
            "error_count": len(results),
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/results/{session_id}", responses={404: {"description": "Session not found"}})
def get_results(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]

    if "results" not in session:
        raise HTTPException(status_code=404, detail="No results yet. Run /analyze first.")

    return {
        "session_id": session_id,
        "results": session["results"]
    }


@app.delete("/session/{session_id}", responses={404: {"description": "Session not found"}})
def delete_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions.pop(session_id)

    if session.get("cloned_path") and os.path.exists(session["cloned_path"]):
        shutil.rmtree(session["cloned_path"], ignore_errors=True)

    return {"status": "deleted", "session_id": session_id}