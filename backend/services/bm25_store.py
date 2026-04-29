from rank_bm25 import BM25Okapi
import numpy as np

class BM25Store:
    def __init__(self):
        self.bm25 = None
        self.documents = []
    
    def build(self, documents):
        self.documents = documents
        
        tokenized_docs = [
            doc.lower().split() for doc in documents
        ]
        
        self.bm25 = BM25Okapi(tokenized_docs)
    
    def search(self, query, top_k=5):
        tokenized_query = query.lower().split()
        
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        return top_indices, scores[top_indices]