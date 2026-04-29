def chunk_code(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunks = text[start:end]
        chunks.append(chunks)
        start += chunk_size - overlap
    
    return chunks