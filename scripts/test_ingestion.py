from pipelines.ingest_repo import ingest
from backend.services.retriever import retrieve

store, docs, meta = ingest("data/repos/sample_repo")

print(f"Total chunks: {len(docs)}")

results = retrieve("database error", store, docs)

for r in results:
    print("\n---")
    print(r["content"][:200])
    print("Score:", r["score"])