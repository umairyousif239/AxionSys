from pipelines.ingest_repo import ingest
from backend.services.bm25_store import BM25Store
from backend.services.hybrid_retriever import hybrid_retrieve
from backend.services.reranker import rerank

# ------------------------
# CONFIG
# ------------------------
TOP_K = 5
SHOW_K = 3

ALPHA = 0.7   # retrieval weight
BETA = 0.3    # reranker weight

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
for q in queries:
    print("\n========================")
    print("QUERY:", q)
    print("========================")

    # ------------------------
    # HYBRID RETRIEVAL
    # ------------------------
    original = hybrid_retrieve(q, bm25, store, docs, top_k=TOP_K)

    for i, r in enumerate(original):
        r["orig_rank"] = i + 1
        r["hybrid_score"] = r["score"]
        r["rerank_score"] = 0.0  # default

    # ------------------------
    # RERANK (feature only)
    # ------------------------
    reranked = rerank(q, original)

    # ------------------------
    # FUSION SCORING (IMPORTANT FIX)
    # ------------------------
    for r in reranked:
        h = r["hybrid_score"]
        rr = r.get("rerank_score", h)

        r["final_score"] = (ALPHA * h) + (BETA * rr)

        # optional diagnostics
        r["score_delta"] = rr - h

    # ------------------------
    # SORT BY FUSED SCORE
    # ------------------------
    reranked = sorted(reranked, key=lambda x: x["final_score"], reverse=True)

    # ------------------------
    # BEFORE RERANK (compact)
    # ------------------------
    print("\n--- BEFORE RERANK (top 3) ---")
    for r in original[:SHOW_K]:
        print(f"[{r['orig_rank']}] score={r['score']:.3f}")

    # ------------------------
    # AFTER RERANK (compact)
    # ------------------------
    print("\n--- AFTER RERANK (top 3, FUSED) ---")
    for i, r in enumerate(reranked[:SHOW_K]):
        print(
            f"[{i+1}] "
            f"hybrid={r['hybrid_score']:.3f} "
            f"rerank={r.get('rerank_score', 0):.3f} "
            f"final={r['final_score']:.3f} "
            f"Δ={r['score_delta']:.3f}"
        )

    # LIGHTWEIGHT DIAGNOSTICS
    hybrid_scores = [r["score"] for r in original]
    rerank_scores = [r.get("rerank_score", r["score"]) for r in reranked]
    final_scores = [r["final_score"] for r in reranked]

    print("\n[Diagnostics]")
    print(f"Hybrid range: {min(hybrid_scores):.3f} → {max(hybrid_scores):.3f}")
    print(f"Rerank range: {min(rerank_scores):.3f} → {max(rerank_scores):.3f}")
    print(f"Final range:  {min(final_scores):.3f} → {max(final_scores):.3f}")

    print(f"Top-1 final score: {reranked[0]['final_score']:.3f}")

    print("\n========================\n")