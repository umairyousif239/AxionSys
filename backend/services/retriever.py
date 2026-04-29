from backend.services.embedding import embed_texts

def retrieve(query, store, documents, top_k=5):
    query_vec = embed_texts([query])
    indices, distances = store.search(query_vec, top_k)
    
    results = []
    for i, d in zip(indices, distances):
        results.append({
            "content": documents[i],
            "score": float(d)
        })
    
    return results