"""
Embedding and retrieval pipeline (Milestone 4).

Architecture:
  ingest.load_and_chunk_all()
      -> SentenceTransformer("all-MiniLM-L6-v2")  [embed]
      -> ChromaDB (persistent, cosine similarity)  [store]
      -> retrieve(query, k)                         [search]

Run this file directly to build the index:
    python embed.py           # build (skips if index already exists)
    python embed.py --force   # rebuild from scratch
"""

import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb

from ingest import load_and_chunk_all

# ── Configuration ─────────────────────────────────────────────────────────────
CHROMA_PATH = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "syllabi"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
# planning.md specifies top-k=3; starting at 5 per assignment guidance and
# tuning down after evaluating against the test questions.
TOP_K = 5

# ── Lazy singletons ────────────────────────────────────────────────────────────
_model: SentenceTransformer | None = None
_collection = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL} ...")
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


# ── Index building ─────────────────────────────────────────────────────────────

def build_index(force: bool = False) -> None:
    """
    Embed all chunks and store them in ChromaDB with source metadata.

    Skips if the collection is already populated unless force=True.
    """
    global _collection

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))

    if force:
        try:
            client.delete_collection(COLLECTION_NAME)
            print("Existing index deleted.")
        except Exception:
            pass
        _collection = None

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    _collection = collection

    if not force and collection.count() > 0:
        print(f"Index already contains {collection.count()} chunks. "
              "Pass force=True or --force to rebuild.")
        return

    print("Loading and chunking documents...")
    chunks = load_and_chunk_all()

    model = _get_model()
    texts = [c["text"] for c in chunks]

    print(f"Embedding {len(texts)} chunks with {EMBEDDING_MODEL} ...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)

    ids = [f"{c['source']}::{c['chunk_index']}" for c in chunks]
    metadatas = [
        {"source": c["source"], "chunk_index": c["chunk_index"]}
        for c in chunks
    ]

    # ChromaDB recommends batches ≤ 5 000; 500 is conservative and safe.
    batch_size = 500
    for start in range(0, len(chunks), batch_size):
        end = min(start + batch_size, len(chunks))
        collection.add(
            ids=ids[start:end],
            embeddings=embeddings[start:end].tolist(),
            documents=texts[start:end],
            metadatas=metadatas[start:end],
        )
        print(f"  Stored {end}/{len(chunks)} chunks")

    print(f"\nIndex built: {collection.count()} chunks stored at {CHROMA_PATH}/")


# ── Retrieval ──────────────────────────────────────────────────────────────────

def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """
    Embed query and return the top-k most semantically similar chunks.

    Each result dict contains:
        text        – chunk content
        source      – source PDF filename
        chunk_index – position of chunk within that document
        score       – cosine similarity (0–1, higher is more relevant)
    """
    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "text": text,
            "source": meta["source"],
            "chunk_index": int(meta["chunk_index"]),
            "score": round(1.0 - dist, 4),  # cosine distance → similarity
        })

    return hits


# ── CLI entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    force = "--force" in sys.argv
    build_index(force=force)

    # Smoke-test with the five evaluation questions from planning.md
    test_queries = [
        "What are the office hours for CSC 311?",
        "What happens if you submit a late assignment in CSC 311?",
        "What is the minimum grade for CSC 311 to count toward the CS major?",
        "What percentage of the DST 490 grade comes from the Data Visualization Project?",
        "What is the late homework policy in DST 490?",
    ]

    print("\n" + "=" * 60)
    print("Retrieval smoke test (planning.md evaluation questions)")
    print("=" * 60)

    for query in test_queries:
        print(f"\nQuery: {query!r}")
        hits = retrieve(query, k=TOP_K)
        for h in hits:
            print(f"  [{h['score']:.4f}] {h['source']}  chunk {h['chunk_index']}")
            print(f"          {h['text'][:120]!r}")
