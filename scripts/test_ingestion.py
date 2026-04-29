from pipelines.ingest_repo import ingest
from backend.services.bm25_store import BM25Store
from backend.services.hybrid_retriever import hybrid_retrieve

# 1. INGEST (already builds FAISS internally)
store, docs, meta = ingest("data/repos/sample_repo")

print(f"Total chunks: {len(docs)}")

# 2. BUILD BM25 ONLY
bm25 = BM25Store()
bm25.build(docs)

# 3. TEST QUERY
results = hybrid_retrieve(
    "database connection error",
    bm25,
    store,
    docs
)

for r in results:
    print("\n---")
    print(r["content"][:200])
    print("Score:", r["score"])
    print("Sources:", r["sources"])