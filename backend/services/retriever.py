from backend.services.embedding import embed_texts

def retrieve(query, store, documents, top_k=5):
    top_k = min(top_k, len(documents))
    
    query_vec = embed_texts([query]).astype("float32")
    indices, distances = store.search(query_vec, top_k)

    results = []
    for i, d in zip(indices, distances):
        if i < 0 or i >= len(documents):
            continue
        
        results.append({
            "content": documents[i],
            "score": float(d)
        })

    return results