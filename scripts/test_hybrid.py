from pipelines.ingest_repo import ingest
from backend.services.bm25_store import BM25Store
from backend.services.hybrid_retriever import hybrid_retrieve

# 1. INGEST
store, docs, meta = ingest("data/repos/sample_repo")

print("\nTotal chunks:", len(docs))

# 2. BUILD BM25
bm25 = BM25Store()
bm25.build(docs)

# 3. TEST QUERIES (IMPORTANT: use multiple)
queries = [
    "database connection error",
    "query user function",
    "log error handling",
]

# 4. RUN TESTS
for q in queries:
    print("\n========================")
    print("QUERY:", q)
    print("========================")

    results = hybrid_retrieve(q, bm25, store, docs)

    for r in results:
        print("\n---")
        print(r["content"][:200])
        print("Score:", r["score"])
        print("Sources:", r["sources"])