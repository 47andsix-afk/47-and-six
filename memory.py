from typing import Any, Dict, List

from fastapi import APIRouter, Body


router = APIRouter(prefix="/memory", tags=["Memory"])

_memory: List[Dict[str, Any]] = []


@router.post("/store")
async def store_memory(payload: Dict[str, Any] = Body(...)):
    _memory.append(payload)
    return {"stored": True, "count": len(_memory)}


@router.get("/all")
async def all_memory():
    return {"memory": _memory}