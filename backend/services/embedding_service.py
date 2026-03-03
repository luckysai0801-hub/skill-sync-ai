"""
services/embedding_service.py - Generates sentence embeddings using
sentence-transformers (all-MiniLM-L6-v2) for resumes and job descriptions.

Why semantic embedding over keyword matching:
  • Captures meaning, not just exact words (e.g., "Python dev" ≈ "software engineer (Python)")
  • Handles synonyms, paraphrasing, and domain language naturally
  • O(n) inference time per document; cosine similarity is O(d) per pair
  • all-MiniLM-L6-v2 produces 384-dim vectors; fast and lightweight.
"""

from typing import List

# Try to import the optional sentence-transformers + numpy implementation.
# If unavailable (quick run), provide a lightweight fallback so the app can start
# and produce deterministic but inexpensive embeddings for demo/testing.
_HAS_ST = False
_HAS_NUMPY = False
try:
    from sentence_transformers import SentenceTransformer  # type: ignore
    _HAS_ST = True
except Exception:
    _HAS_ST = False

try:
    import numpy as np  # type: ignore
    _HAS_NUMPY = True
except Exception:
    _HAS_NUMPY = False

# ─── Full model implementation (when available) ─────────────────────────────
_model = None

def _get_model():
    global _model
    if not _HAS_ST:
        return None
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def generate_embedding(text: str) -> List[float]:
    """Return a dense vector for `text`.

    If `sentence-transformers` is present we use the real model. Otherwise
    return a lightweight hashed bag-of-words vector (128 dims) that is
    deterministic and fast — sufficient for local runs and demos.
    """
    if _HAS_ST:
        model = _get_model()
        emb = model.encode(text, normalize_embeddings=True)
        return emb.tolist()

    # Fallback: produce a fixed-size hashed token frequency vector
    buckets = 128
    vec = [0.0] * buckets
    for tok in [t.lower() for t in text.split() if t.strip()]:
        idx = (hash(tok) % buckets)
        vec[idx] += 1.0

    # L2-normalize without numpy
    norm = sum(v * v for v in vec) ** 0.5
    if norm == 0:
        return vec
    return [v / norm for v in vec]


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity (dot product for normalized vectors).

    Works with either numpy arrays (if installed) or plain Python lists.
    Returns value clipped to [0,1].
    """
    if _HAS_NUMPY:
        a = np.array(vec_a, dtype=np.float32)
        b = np.array(vec_b, dtype=np.float32)
        sim = float(np.dot(a, b))
        return max(0.0, min(1.0, sim))

    # Pure-Python dot product
    dot = 0.0
    for x, y in zip(vec_a, vec_b):
        dot += (x or 0.0) * (y or 0.0)
    return max(0.0, min(1.0, dot))
