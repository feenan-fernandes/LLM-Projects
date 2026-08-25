"""
chroma_client.py — Phase 7: Adaptive CRAG routing
Routes queries between three strategies based on Librarian-assessed complexity.
Complexity levels: SIMPLE → vector only | MEDIUM → vector + BM25 | COMPLEX → multi-hop

Uses existing ChromaDB collections + pre-built BM25 pkl files already on disk.
Inspired by Adaptive-RAG (arXiv:2403.14403).
"""
import os
import pickle
import math

import chromadb
from chromadb.config import Settings

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
CHROMA_DB_PATH = os.path.join(_REPO_ROOT, 'chroma_db')
BM25_DIR = _REPO_ROOT  # pkl files live in the repo root

_client = None
_collections: dict = {}
_bm25_indexes: dict = {}


# ── ChromaDB ───────────────────────────────────────────────────────────────

def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
    return _client


def list_collections() -> list[str]:
    return [c.name for c in _get_client().list_collections()]


def get_collection(name: str):
    if name not in _collections:
        _collections[name] = _get_client().get_collection(name)
    return _collections[name]


def vector_search(query_text: str, collection_name: str, n_results: int = 5) -> list[dict]:
    col = get_collection(collection_name)
    results = col.query(query_texts=[query_text], n_results=n_results)
    docs = results.get('documents', [[]])[0]
    ids = results.get('ids', [[]])[0]
    metas = results.get('metadatas', [[]])[0]
    distances = results.get('distances', [[]])[0]
    return [
        {'id': ids[i], 'document': docs[i], 'metadata': metas[i],
         'distance': distances[i], 'source': 'vector'}
        for i in range(len(docs))
    ]


# ── BM25 ───────────────────────────────────────────────────────────────────

def _load_bm25(collection_name: str):
    if collection_name in _bm25_indexes:
        return _bm25_indexes[collection_name]
    pkl_path = os.path.join(BM25_DIR, f"bm25_index_{collection_name}.pkl")
    if not os.path.exists(pkl_path):
        return None
    try:
        with open(pkl_path, 'rb') as f:
            idx = pickle.load(f)
        _bm25_indexes[collection_name] = idx
        return idx
    except Exception:
        return None


def bm25_search(query_text: str, collection_name: str, n_results: int = 5) -> list[dict]:
    idx = _load_bm25(collection_name)
    if idx is None:
        return []
    try:
        tokens = query_text.lower().split()
        scores = idx.get_scores(tokens)
        top_n = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n_results]
        corpus = getattr(idx, 'corpus', [])
        return [
            {'id': str(i), 'document': corpus[i] if i < len(corpus) else "",
             'metadata': {}, 'distance': float(scores[i]), 'source': 'bm25'}
            for i in top_n
        ]
    except Exception:
        return []


def hybrid_search(query_text: str, collection_name: str, n_results: int = 5) -> list[dict]:
    """Merges vector + BM25 results with reciprocal rank fusion."""
    vec = vector_search(query_text, collection_name, n_results * 2)
    bm = bm25_search(query_text, collection_name, n_results * 2)

    # Reciprocal rank fusion
    scores: dict[str, float] = {}
    docs_by_id: dict[str, dict] = {}
    k = 60

    for rank, r in enumerate(vec):
        rid = r['id']
        scores[rid] = scores.get(rid, 0) + 1 / (k + rank + 1)
        docs_by_id[rid] = r

    for rank, r in enumerate(bm):
        rid = r['id']
        scores[rid] = scores.get(rid, 0) + 1 / (k + rank + 1)
        docs_by_id[rid] = r

    merged = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n_results]
    return [docs_by_id[rid] for rid, _ in merged if rid in docs_by_id]


# ── Adaptive CRAG routing ──────────────────────────────────────────────────

def _classify_complexity(query: str) -> str:
    """
    Lightweight heuristic complexity classifier (replaces a trained model
    to avoid extra inference overhead on a 7B system).
    SIMPLE  < 6 tokens, no connectors
    COMPLEX contains multi-hop indicators
    MEDIUM  everything else
    """
    q = query.lower()
    multi_hop = any(k in q for k in ["and", "compare", "difference between", "how does", "why does", "relationship"])
    token_count = len(q.split())

    if token_count < 6 and not multi_hop:
        return "SIMPLE"
    if multi_hop or token_count > 20:
        return "COMPLEX"
    return "MEDIUM"


def adaptive_search(
    query_text: str,
    collection_name: str,
    n_results: int = 5,
    force_strategy: str = None,  # "SIMPLE" | "MEDIUM" | "COMPLEX"
) -> tuple[list[dict], str]:
    """
    Adaptive CRAG retrieval. Returns (results, strategy_used).
    """
    strategy = force_strategy or _classify_complexity(query_text)

    if strategy == "SIMPLE":
        return vector_search(query_text, collection_name, n_results), "SIMPLE"
    elif strategy == "MEDIUM":
        return hybrid_search(query_text, collection_name, n_results), "MEDIUM"
    else:
        # COMPLEX: decompose into sub-queries, merge
        words = query_text.split()
        mid = len(words) // 2
        q1 = " ".join(words[:mid])
        q2 = " ".join(words[mid:])
        r1 = hybrid_search(q1, collection_name, n_results)
        r2 = hybrid_search(q2, collection_name, n_results)
        seen = set()
        merged = []
        for r in r1 + r2:
            if r['id'] not in seen:
                seen.add(r['id'])
                merged.append(r)
        return merged[:n_results], "COMPLEX"
