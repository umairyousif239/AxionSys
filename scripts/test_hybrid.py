from pipelines.ingest_repo import ingest

from backend.services.bm25_store import BM25Store
from backend.services.hybrid_retriever import hybrid_retrieve
from backend.services.reranker import rerank
from backend.services.root_cause import generate_root_cause
from backend.services.fix_generator import generate_fix

# ------------------------
# CONFIG
# ------------------------
TOP_K = 5
SHOW_K = 3

ALPHA = 0.7
BETA = 0.3

# ------------------------
# 1. INGEST
# ------------------------
store, docs, meta = ingest("data/repos/sample_repo")
print("\nTotal chunks:", len(docs))

# ------------------------
# 2. BUILD BM25
# ------------------------
bm25 = BM25Store()
bm25.build(docs)

# ------------------------
# HELPER
# ------------------------
def get_label(r, docs, meta):
    """Look up the filename for a result using its content to find its index."""
    content = r.get("content", "")
    try:
        idx = docs.index(content)
        path = meta[idx]["path"]
        return path.split("/")[-1].split("\\")[-1]
    except (ValueError, IndexError, KeyError):
        return "unknown"

# ------------------------
# 3. TEST QUERIES
# ------------------------
queries = [
    "database connection error",
    "why is database connection returning None",
    "why does cursor fail in connect_db",
    "http request failure",
    "user data retrieval failure"
]

# ------------------------
# 4. RUN TESTS
# ------------------------
for q_num, q in enumerate(queries, start=1):
    print("\n========================")
    print(f"QUERY {q_num}/{len(queries)}: {q}")
    print("========================")

    original = hybrid_retrieve(q, bm25, store, docs, top_k=TOP_K)

    for i, r in enumerate(original):
        r["orig_rank"] = i + 1
        r["hybrid_score"] = r["score"]
        r["rerank_score"] = 0.0

    reranked = rerank(q, original)

    for r in reranked:
        h = r["hybrid_score"]
        rr = r.get("rerank_score", h)
        delta = abs(rr - h)
        
        # If they broadly agree, trust hybrid more (it's faster/cheaper signal)
        # If they strongly disagree, give reranker more weight but cap its influence
        if delta < 0.2:
            alpha, beta = 0.7, 0.3
        elif delta < 0.5:
            alpha, beta = 0.5, 0.5
        else:
            alpha, beta = 0.4, 0.6  # reranker wins but doesn't dominate
        
        r["final_score"] = (alpha * h) + (beta * rr)
        r["score_delta"] = rr - h

    reranked = sorted(reranked, key=lambda x: x["final_score"], reverse=True)

    # ------------------------
    # BEFORE RERANK
    # ------------------------
    print("\n--- BEFORE RERANK (top 3) ---")
    for r in original[:SHOW_K]:
        label = get_label(r, docs, meta)
        print(f"[{r['orig_rank']}] {label:<35} score={r['score']:.3f}")

    # ------------------------
    # AFTER RERANK
    # ------------------------
    print("\n--- AFTER RERANK (top 3, FUSED) ---")
    for i, r in enumerate(reranked[:SHOW_K]):
        label = get_label(r, docs, meta)
        print(
            f"[{i+1}] {label:<35} "
            f"hybrid={r['hybrid_score']:.3f} "
            f"rerank={r.get('rerank_score', 0):.3f} "
            f"final={r['final_score']:.3f} "
            f"Δ={r['score_delta']:.3f}"
        )

    hybrid_scores = [r["score"] for r in original]
    rerank_scores = [r.get("rerank_score", r["score"]) for r in reranked]
    final_scores = [r["final_score"] for r in reranked]
    top = reranked[0]

    print("\n[Diagnostics]")
    print(f"Hybrid range: {min(hybrid_scores):.3f} → {max(hybrid_scores):.3f}")
    print(f"Rerank range: {min(rerank_scores):.3f} → {max(rerank_scores):.3f}")
    print(f"Final range:  {min(final_scores):.3f} → {max(final_scores):.3f}")
    print(f"Top-1: {get_label(top, docs, meta):<35} final={top['final_score']:.3f}")

    print("\n========================\n")
    
    # ------------------------
    # ROOT CAUSE + FIX GENERATION
    # ------------------------
    try:
        for r in reranked:
            r["file"] = get_label(r, docs, meta)
        rc = generate_root_cause(q, reranked, top_k=3)

        print("\n--- ROOT CAUSE ---")
        print(f"Cause:      {rc['root_cause']}")
        print(f"Files:      {', '.join(rc['affected_files'])}")
        print(f"Reasoning:  {rc['reasoning']}")
        print(f"Fix:        {rc['fix']}")
        print(f"Confidence: {rc['confidence']:.2f}")

        # ------------------------
        # FIX GENERATION
        # ------------------------
        fix = generate_fix(rc, reranked, top_k=3)

        print("\n--- FIX ---")
        if fix.get("diff"):
            print("Diff:")
            print(fix["diff"])
        else:
            if fix.get("diff_warning"):
                print(f"[!] {fix['diff_warning']}")

        print(f"\nExplanation: {fix['explanation']}")
        print(f"File:        {fix.get('affected_file', 'unknown')}")
        print(f"Confidence:  {fix['confidence']:.2f}")

    except Exception as e:
        print("\n[Pipeline Error]", str(e))