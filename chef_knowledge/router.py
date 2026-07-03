from fastapi import APIRouter, Depends
from chromadb import PersistentClient
from chef_knowledge.indexer import DB_PATH, COLLECTION_NAME
from core.auth import require_roles

router = APIRouter(
    prefix="/chef/knowledge",
    tags=["Chef Knowledge"],
    dependencies=[Depends(require_roles("viewer", "chef", "admin"))],
)


@router.get("/files")
def list_indexed_files():
    client = PersistentClient(path=DB_PATH)
    try:
        coll = client.get_or_create_collection(COLLECTION_NAME)
    except Exception:
        coll = client.get_collection(name=COLLECTION_NAME)
    results = coll.get()
    return {"items": results}


@router.get("/portfolio")
def chef_portfolio():
    client = PersistentClient(path=DB_PATH)
    try:
        coll = client.get_or_create_collection(COLLECTION_NAME)
    except Exception:
        coll = client.get_collection(name=COLLECTION_NAME)
    results = coll.get()
    ids = results.get("ids", []) or []
    metadatas = results.get("metadatas", []) or []
    return {"total_docs": len(ids), "samples": metadatas[:10]}
