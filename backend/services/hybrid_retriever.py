from backend.services.embedding import embed_texts
import numpy as np

def normalize_list(values):
    if values is None or len(values) == 0:
        return values

    values = np.array(values, dtype=float)

    max_v = np.max(values)
    if max_v == 0:
        return values.tolist()

    return (values / (max_v + 1e-8)).tolist()


def invert_faiss_distances(distances):
    # Convert distance to similarity score
    return [1 / (1 + d) for d in distances]


def hybrid_retrieve(query, bm25_store, vector_store, documents, top_k=5):
    results = {}

    def add_result(idx, score, source):
        if idx < 0 or idx >= len(documents):
            return

        if idx not in results:
            results[idx] = {
                "content": documents[idx],
                "score": 0.0,
                "sources": []
            }

        results[idx]["score"] += score
        results[idx]["sources"].append(source)

    # BM25 (lexical signal)
    bm25_indices, bm25_scores = bm25_store.search(query, top_k)
    bm25_scores = normalize_list(bm25_scores)

    for i, s in zip(bm25_indices, bm25_scores):
        add_result(i, 0.6 * s, "bm25")

    # FAISS (semantic signal)
    query_vec = embed_texts([query]).astype("float32")
    faiss_indices, faiss_distances = vector_store.search(query_vec, top_k)

    faiss_scores = invert_faiss_distances(faiss_distances)
    faiss_scores = normalize_list(faiss_scores)

    for i, s in zip(faiss_indices, faiss_scores):
        add_result(i, 0.4 * s, "faiss")

    # Final ranking
    final = sorted(
        results.values(),
        key=lambda x: x["score"],
        reverse=True
    )

    return final[:top_k]