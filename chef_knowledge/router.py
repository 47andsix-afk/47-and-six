import os
from typing import Any, Dict

from fastapi import APIRouter, Body

from .embeddings import ChefEmbeddings
from .indexer import ChefKnowledgeIndexer
from .loader import ChefKnowledgeLoader


router = APIRouter(prefix="/chef/knowledge", tags=["Chef Knowledge"])

_loader = ChefKnowledgeLoader(base_path=os.getenv("SCHOOL_DIR", "./chef_knowledge_data"))
_embedder = ChefEmbeddings(api_key=os.getenv("GEMINI_API_KEY", ""))
_indexer = ChefKnowledgeIndexer(
    db_path=os.getenv("CHROMA_DB_PATH", "./chroma_db"),
    collection="chef_knowledge",
)


@router.get("/files")
async def list_files() -> Dict[str, Any]:
    docs = _loader.load_all()
    return {"files": [d["id"] for d in docs]}


@router.get("/portfolio")
async def portfolio_summary() -> Dict[str, Any]:
    docs = _loader.load_all()
    return {
        "count": len(docs),
        "sample": [d["id"] for d in docs[:5]],
    }


@router.post("/search")
async def search(payload: Dict[str, Any] = Body(...)):
    query = payload.get("query", "")
    n = int(payload.get("n", 5))

    docs = _loader.load_all()
    if docs:
        embeddings = await _embedder.embed([d["text"] for d in docs])
        _indexer.index(docs, embeddings)

    return _indexer.search(query, n)
