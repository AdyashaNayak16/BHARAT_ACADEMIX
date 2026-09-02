from sentence_transformers import SentenceTransformer
import numpy as np
import re

model = SentenceTransformer('all-MiniLM-L6-v2')

def chunk_text(text, max_chars=500):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) <= max_chars:
            current += " " + sentence
        else:
            chunks.append(current.strip())
            current = sentence
    if current:
        chunks.append(current.strip())
    return chunks

def search(chunks, chunk_embeddings, query, top_k=1):
    query_embedding = model.encode([query])[0]
    similarities = np.dot(chunk_embeddings, query_embedding)
    top_indices = np.argsort(similarities)[::-1][:top_k]
    return [chunks[i] for i in top_indices]