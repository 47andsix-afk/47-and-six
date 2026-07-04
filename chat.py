from typing import Any, Dict

from fastapi import APIRouter, Body, HTTPException, Request, status


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/agentic")
async def chat_agentic(request: Request, payload: Dict[str, Any] = Body(...)):
    user_input = payload.get("user_input", "")
    orchestrator = getattr(request.app.state, "orchestrator", None)
    if orchestrator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="agent orchestrator is unavailable in this build",
        )

    result = await orchestrator.run(user_input=user_input)
    return {"user_input": user_input, "agents": result}
