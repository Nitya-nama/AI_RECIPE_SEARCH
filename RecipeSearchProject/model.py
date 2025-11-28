from sentence_transformers import SentenceTransformer
import numpy as np

# Load embedding model once
print("⏳ Loading recipe embedding model (MiniLM)...")
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("✅ Recipe embedding model loaded!")


def get_embedding(text: str):
    """Return embedding list for a given text."""
    text = (text or "").strip()
    if not text:
        return None
    vec = embedding_model.encode([text])[0]
    return vec.astype(float).tolist()


def cosine_similarities(query_emb, doc_embs):
    """
    Compute cosine similarity between query_emb and list of doc embeddings.
    Returns a list of floats (similarity scores).
    """
    if query_emb is None:
        return [0.0 for _ in doc_embs]

    q = np.array(query_emb, dtype=float)
    q_norm = np.linalg.norm(q) or 1e-8

    sims = []
    for emb in doc_embs:
        if not emb:
            sims.append(0.0)
            continue
        v = np.array(emb, dtype=float)
        denom = (np.linalg.norm(v) or 1e-8) * q_norm
        sims.append(float(np.dot(q, v) / denom))
    return sims
