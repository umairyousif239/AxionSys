from backend.services.bm25_store import BM25Store
from backend.services.hybrid_retriever import hybrid_retrieve
from backend.services.reranker import rerank
from backend.services.root_cause import generate_root_cause
from backend.services.fix_generator import generate_fix
from backend.services.log_parser import parse_log
from pipelines.ingest_repo import ingest

TOP_K = 5

def get_label(r, docs, meta):
    content = r.get("content", "")
    try:
        idx = docs.index(content)
        path = meta[idx]["path"]
        return path.split("/")[-1].split("\\")[-1]
    except (ValueError, IndexError, KeyError):
        return "unknown"

def fuse_scores(reranked):
    for r in reranked:
        h = r["hybrid_score"]
        rr = r.get("rerank_score", h)
        delta = abs(rr - h)

        if delta < 0.2:
            alpha, beta = 0.7, 0.3
        elif delta < 0.5:
            alpha, beta = 0.5, 0.5
        else:
            alpha, beta = 0.4, 0.6

        r["final_score"] = (alpha * h) + (beta * rr)
        r["score_delta"] = rr - h

    return sorted(reranked, key=lambda x: x["final_score"], reverse=True)

def run_retrieval(entry, bm25, store, docs, meta):
    queries = [entry["primary_query"]] + entry["secondary_queries"]

    all_retrieved = []
    seen_contents = set()

    for q in queries:
        retrieved = hybrid_retrieve(q, bm25, store, docs, top_k=TOP_K)
        for r in retrieved:
            content = r.get("content", "")
            if content not in seen_contents:
                seen_contents.add(content)
                all_retrieved.append(r)

    for i, r in enumerate(all_retrieved):
        r["orig_rank"] = i + 1
        r["hybrid_score"] = r["score"]
        r["rerank_score"] = 0.0

    reranked = rerank(entry["primary_query"], all_retrieved)
    reranked = fuse_scores(reranked)

    for r in reranked:
        r["file"] = get_label(r, docs, meta)

    return reranked

def format_top_files(reranked, docs, meta):
    return [
        {
            "file": get_label(r, docs, meta),
            "final_score": round(r["final_score"], 3),
            "hybrid_score": round(r["hybrid_score"], 3),
            "rerank_score": round(r.get("rerank_score", 0), 3)
        }
        for r in reranked[:3]
    ]

def analyze(repo_path: str, log_text: str, store=None, docs=None, meta=None, bm25=None) -> list[dict]:
    # only ingest if not provided
    if store is None or docs is None or meta is None:
        store, docs, meta = ingest(repo_path)

    if bm25 is None:
        bm25 = BM25Store()
        bm25.build(docs)

    parsed = parse_log(log_text)
    results = []

    for entry in parsed:
        reranked = run_retrieval(entry, bm25, store, docs, meta)
        rc = generate_root_cause(entry["primary_query"], reranked, top_k=3)
        fix = generate_fix(rc, reranked, top_k=3)

        results.append({
            "error": entry["error"],
            "type": entry["type"],
            "primary_query": entry["primary_query"],
            "secondary_queries": entry["secondary_queries"],
            "files_mentioned": entry["files_mentioned"],
            "top_files": format_top_files(reranked, docs, meta),
            "root_cause": rc,
            "fix": fix
        })

    return results

if __name__ == "__main__":
    with open("data/logs/sample.log") as f:
        log_text = f.read()

    results = analyze("data/repos/sample_repo", log_text)

    for r in results:
        print("\n========================")
        print(f"Error:   {r['error']}")
        print(f"Primary: {r['primary_query']}")
        print("\n--- ROOT CAUSE ---")
        print(f"Cause:      {r['root_cause']['root_cause']}")
        print(f"Files:      {', '.join(r['root_cause']['affected_files'])}")
        print(f"Reasoning:  {r['root_cause']['reasoning']}")
        print(f"Confidence: {r['root_cause']['confidence']:.2f}")
        print("\n--- FIX ---")
        if r['fix'].get('diff'):
            print(f"Diff:\n{r['fix']['diff']}")
        print(f"Explanation: {r['fix']['explanation']}")
        print(f"Confidence:  {r['fix']['confidence']:.2f}")
        print("========================\n")