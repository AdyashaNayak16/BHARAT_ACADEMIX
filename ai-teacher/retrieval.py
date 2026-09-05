import numpy as np
import re

_model = None

def get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"[*] Warning: Could not load SentenceTransformer ({e}). Using lightweight fallback.")
            _model = "fallback"
    return _model

class LazyModelProxy:
    def encode(self, texts):
        m = get_model()
        if m != "fallback" and hasattr(m, "encode"):
            return m.encode(texts)
        # Fallback bag-of-words / TF-IDF style pseudo embeddings
        from sklearn.feature_extraction.text import TfidfVectorizer
        vec = TfidfVectorizer(stop_words='english')
        try:
            matrix = vec.fit_transform(texts if isinstance(texts, list) else [texts]).toarray()
            return matrix
        except Exception:
            return np.zeros((len(texts), 64))

model = LazyModelProxy()

def chunk_text(text, max_chars=500):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) <= max_chars:
            current += " " + sentence
        else:
            if current.strip():
                chunks.append(current.strip())
            current = sentence
    if current.strip():
        chunks.append(current.strip())
    if not chunks:
        chunks = [text[:max_chars]] if text else ["General lesson material."]
    return chunks

def search(chunks, chunk_embeddings, query, top_k=1):
    if not chunks:
        return ["No context available."]
    m = get_model()
    try:
        if m != "fallback" and hasattr(m, "encode") and hasattr(chunk_embeddings, "shape") and len(chunk_embeddings) == len(chunks):
            query_embedding = m.encode([query])[0]
            similarities = np.dot(chunk_embeddings, query_embedding)
            top_indices = np.argsort(similarities)[::-1][:top_k]
            return [chunks[i] for i in top_indices]
    except Exception as e:
        print(f"[*] Fallback search: {e}")
    
    # Fast keyword / BM25 fallback
    query_words = set(re.findall(r'\w+', query.lower()))
    scores = []
    for c in chunks:
        c_words = set(re.findall(r'\w+', c.lower()))
        overlap = len(query_words.intersection(c_words))
        scores.append(overlap)
    top_indices = np.argsort(scores)[::-1][:top_k]
    return [chunks[i] for i in top_indices]