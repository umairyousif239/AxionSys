from backend.services.loader import load_repo
from backend.services.chunker import chunk_code
from backend.services.embedding import embed_texts
from backend.services.vector_store import VectorStore

def ingest(path):
    documents = []
    metadata = []
    
    repo_files = load_repo(path)
    
    for file in repo_files:
        chunks = chunk_code(file["content"])
        
        for chunk in chunks:
            documents.append(chunk)
            metadata.append({
                "path": file["path"]
            })
    
    embeddings = embed_texts(documents)
    
    store = VectorStore()
    store.build(embeddings)
    
    return store, documents, metadata

if __name__ == "__main__":
    store, docs, meta = ingest("data/repos/sample_repo")
    print(f"Indexed {len(docs)} chunks")