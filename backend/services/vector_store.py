import faiss
import numpy as np

class VectorStore:
    def __init__(self):
        self.index = None
        self.documents = []
    
    def build(self, texts):
        embeddings = np.array(texts)
        
        dim = embeddings.shape(1)
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
    
    def search(self, query_vec, top_k=5):
        distances, indices = self.index.search(query_vec, top_k)
        return indices[0], distances[0]