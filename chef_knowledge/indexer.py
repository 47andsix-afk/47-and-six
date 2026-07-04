import os
from typing import Dict, List

try:
    from chromadb import PersistentClient
except Exception:  # pragma: no cover
    PersistentClient = None  # type: ignore[assignment]

from .embeddings import ChefEmbeddings
from .loader import ChefKnowledgeLoader


class ChefKnowledgeIndexer:
    def __init__(self, db_path: str = "chroma_db", collection: str = "chef_knowledge"):
        self._enabled = PersistentClient is not None
        self._docs: List[Dict[str, str]] = []
        self.collection = None
        if self._enabled:
            client = PersistentClient(path=db_path)
            self.collection = client.get_or_create_collection(collection)

    def index(self, docs: List[Dict[str, str]], embeddings: List[List[float]]):
        self._docs = docs
        if not self.collection:
            return
        if not docs:
            return
        ids = [d["id"] for d in docs]
        texts = [d["text"] for d in docs]
        self.collection.upsert(ids=ids, documents=texts, embeddings=embeddings)

    def search(self, query: str, n: int = 5) -> Dict:
        if self.collection:
            return self.collection.query(query_texts=[query], n_results=n)

        lowered = query.lower()
        matches = [d for d in self._docs if lowered in d["text"].lower()]
        top = matches[:n]
        return {
            "ids": [[d["id"] for d in top]],
            "documents": [[d["text"] for d in top]],
            "distances": [[]],
        }


def build_index() -> None:
    school_dir = os.getenv("SCHOOL_DIR", "./chef_knowledge_data")
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    loader = ChefKnowledgeLoader(base_path=school_dir)
    docs = loader.load_all()
    if not docs:
        return

    embedder = ChefEmbeddings(api_key=api_key)
    # keep startup sync-friendly while build_index remains callable from lifespan
    import asyncio

    embeddings = asyncio.run(embedder.embed([d["text"] for d in docs]))
    indexer = ChefKnowledgeIndexer()
    indexer.index(docs, embeddings)
