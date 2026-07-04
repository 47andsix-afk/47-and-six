# pyright: reportMissingImports=false
import asyncio
import base64
from contextlib import asynccontextmanager
import hashlib
import hmac
import importlib
import json
import os
import time
from typing import Any, AsyncIterator, Optional

from fastapi import APIRouter, Body, Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

chromadb: Any = None
try:
    import chromadb as chromadb_module  # type: ignore[import-not-found, import-untyped]
    chromadb = chromadb_module
except ImportError:
    chromadb = None

Client: Any = None
types: Any = None
try:
    from google.genai import Client as GeminiClient, types as google_types  # type: ignore[import-not-found, import-untyped]
    Client = GeminiClient
    types = google_types
except ImportError:
    Client = None
    types = None

from dotenv import load_dotenv
load_dotenv()

try:
    from chef_knowledge.indexer import build_index
    from chef_knowledge.router import router as chef_knowledge_router
except ImportError:
    def build_index() -> None:
        return None

    chef_knowledge_router = None

try:
    from core.auth import (
        CurrentUser,
        authenticate_user,
        create_access_token,
        load_auth_users,
        require_roles,
    )
except ImportError:
    class CurrentUser:
        def __init__(self, username: str, roles: list[str]):
            self.username = username
            self.roles = roles


    class _AuthRecord(CurrentUser):
        def __init__(self, username: str, password: str, roles: list[str]):
            super().__init__(username, roles)
            self.password = password


    def load_auth_users() -> list[_AuthRecord]:
        users_json = os.getenv("AUTH_USERS_JSON")
        if users_json:
            try:
                parsed = json.loads(users_json)
                return [
                    _AuthRecord(
                        username=item["username"],
                        password=item["password"],
                        roles=list(item.get("roles", [])),
                    )
                    for item in parsed
                ]
            except (KeyError, TypeError, json.JSONDecodeError):
                return []

        username = os.getenv("AUTH_USERNAME")
        password = os.getenv("AUTH_PASSWORD")
        roles = [role.strip() for role in os.getenv("AUTH_ROLES", "admin").split(",") if role.strip()]
        if username and password:
            return [_AuthRecord(username=username, password=password, roles=roles or ["admin"])]
        return []


    def authenticate_user(username: str, password: str, users: list[_AuthRecord]) -> Optional[CurrentUser]:
        for user in users:
            if user.username == username and user.password == password:
                return CurrentUser(user.username, user.roles)
        return None


    def _auth_secret() -> str:
        return os.getenv("JWT_SECRET_KEY", "development-secret-change-me")


    def _encode_token(payload: dict[str, Any]) -> str:
        raw_payload = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        encoded_payload = base64.urlsafe_b64encode(raw_payload).decode("ascii").rstrip("=")
        signature = hmac.new(_auth_secret().encode("utf-8"), encoded_payload.encode("ascii"), hashlib.sha256).hexdigest()
        return f"{encoded_payload}.{signature}"


    def _decode_token(token: str) -> Optional[CurrentUser]:
        try:
            encoded_payload, signature = token.split(".", 1)
        except ValueError:
            return None

        expected_signature = hmac.new(
            _auth_secret().encode("utf-8"),
            encoded_payload.encode("ascii"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            return None

        padded_payload = encoded_payload + "=" * (-len(encoded_payload) % 4)
        try:
            payload = json.loads(base64.urlsafe_b64decode(padded_payload.encode("ascii")))
        except (ValueError, json.JSONDecodeError):
            return None

        expires_at = int(payload.get("exp", 0))
        if expires_at <= int(time.time()):
            return None

        username = payload.get("sub")
        roles = payload.get("roles", [])
        if not isinstance(username, str) or not isinstance(roles, list):
            return None
        return CurrentUser(username=username, roles=[str(role) for role in roles])


    def create_access_token(username: str, roles: list[str]) -> tuple[str, int]:
        expires_at = int(time.time()) + int(os.getenv("JWT_EXPIRE_MINUTES", "120")) * 60
        token = _encode_token({"sub": username, "roles": roles, "exp": expires_at})
        return token, expires_at


    def require_roles(*allowed_roles: str):
        async def dependency(authorization: Optional[str] = Header(default=None)) -> CurrentUser:
            if authorization is None or not authorization.startswith("Bearer "):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

            user = _decode_token(authorization.removeprefix("Bearer ").strip())
            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
            if allowed_roles and not any(role in user.roles for role in allowed_roles):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
            return user

        return dependency

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
USE_MOCK = os.getenv("USE_MOCK_RESPONSES", "false").lower() in ("1", "true", "yes")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")

client_genai = Client(api_key=API_KEY) if Client and API_KEY else None
AUTH_USERS = load_auth_users()

collection = None
if chromadb is not None:
    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = client.get_collection(name="operational_matrix")
    except Exception:
        collection = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    if os.getenv("BUILD_INDEX_ON_STARTUP", "false").lower() in ("1", "true", "yes"):
        try:
            build_index()
        except Exception:
            pass
    yield
    if hasattr(app.state, "aclose"):
        await app.state.aclose()


app = FastAPI(title="47-&-SIX Concierge API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def _retrieve_context(message: str) -> str:
    if collection is None:
        return "No specific local parameters found."

    try:
        results = collection.query(query_texts=[message], n_results=1)
    except Exception:
        return "No specific local parameters found."

    documents = results.get("documents", [])
    if documents and documents[0]:
        return documents[0][0]

    return "No specific local parameters found."


def _generate_text(
    prompt: str,
    *,
    response_mime_type: Optional[str] = None,
    tools: Optional[list[Any]] = None,
) -> str:
    if USE_MOCK:
        return "[MOCK] API not called: returning canned response for development."

    if client_genai is None:
        return "Google GenAI is not configured. Set GEMINI_API_KEY to enable responses."

    if types is None:
        return "Google GenAI is not available in this environment."

    config_kwargs: dict[str, Any] = {}
    if response_mime_type is not None:
        config_kwargs["responseMimeType"] = response_mime_type
    if tools is not None:
        config_kwargs["tools"] = tools

    config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None
    try:
        if config is None:
            response = client_genai.models.generate_content(model=MODEL_NAME, contents=prompt)
        else:
            response = client_genai.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=config,
            )
        return getattr(response, "text", "") or ""
    except Exception as exc:
        msg = str(exc)
        lowerm = msg.lower()
        if "resource_exhausted" in msg or "quota" in lowerm or "exceeded" in lowerm:
            return f"API quota exceeded: {msg}"
        return f"Generation failed: {msg}"


async def _generate_text_async(
    prompt: str,
    *,
    response_mime_type: Optional[str] = None,
    tools: Optional[list[Any]] = None,
) -> str:
    if USE_MOCK:
        return "[MOCK] API not called: returning canned response for development."

    return await asyncio.to_thread(_generate_text, prompt, response_mime_type=response_mime_type, tools=tools)


def _load_runtime_attr(module_name: str, attr_name: str, feature_name: str) -> Any:
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"{feature_name} is unavailable in this build") from exc

    try:
        return getattr(module, attr_name)
    except AttributeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"{feature_name} is unavailable in this build") from exc


class Inquiry(BaseModel):
    message: str


class JsonInquiry(Inquiry):
    pass


class EmbedRequest(BaseModel):
    text: str
    id: str


class MenuCostRequest(BaseModel):
    ingredients: list[str]
    portions: int


class EventRequest(BaseModel):
    event_type: str
    guest_count: int
    dietary: str


class InventoryRequest(BaseModel):
    items: list[str]


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: int
    roles: list[str]


# ---------------------------------------------------------
# Agent router
# ---------------------------------------------------------

agent_router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
    dependencies=[Depends(require_roles("chef", "admin"))],
)

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@agent_router.post("/ronin")
async def ronin_route(payload: dict):
    run_ronin = _load_runtime_attr("agents.orchestrator", "run_ronin", "RONIN orchestrator")
    task = payload.get("task", "")
    message = payload.get("message", "")
    prompt = run_ronin(task, message)
    if USE_MOCK:
        return {"reply": prompt}
    return {"reply": _generate_text(prompt)}


@agent_router.post("/menu-costing")
def menu_costing(payload: dict):
    run_menu_costing = _load_runtime_attr("agents.menu_cost_agent", "run_menu_costing", "menu costing agent")

    prompt = run_menu_costing(payload.get("message", ""))
    if USE_MOCK:
        return {"reply": prompt}
    return {"reply": _generate_text(prompt)}


@agent_router.post("/recipe")
def recipe(payload: dict):
    run_recipe = _load_runtime_attr("agents.recipe_agent", "run_recipe", "recipe agent")

    prompt = run_recipe(payload.get("message", ""))
    if USE_MOCK:
        return {"reply": prompt}
    return {"reply": _generate_text(prompt)}


@agent_router.post("/client-intake")
def client_intake(payload: dict):
    run_client_intake = _load_runtime_attr("agents.client_intake_agent", "run_client_intake", "client intake agent")

    prompt = run_client_intake(payload.get("message", ""))
    if USE_MOCK:
        return {"reply": prompt}
    return {"reply": _generate_text(prompt)}


@agent_router.post("/menu-pricing")
def menu_pricing(payload: dict):
    run_menu_pricing = _load_runtime_attr("agents.menu_pricing_engine", "run_menu_pricing", "menu pricing engine")

    prompt = run_menu_pricing(payload.get("message", ""))
    if USE_MOCK:
        return {"reply": prompt}
    return {"reply": _generate_text(prompt)}


@agent_router.post("/concierge")
async def concierge_route(payload: dict):
    ConciergeAgent = _load_runtime_attr("agents.concierge_agent", "ConciergeAgent", "concierge agent")

    message = payload.get("message", "")
    agent = ConciergeAgent(generate_func=_generate_text_async)
    local_context = _retrieve_context(message)
    response = await agent.synthesize(
        inquiry=message,
        ops={},
        econ={},
        logistics={},
        compliance={},
        local_context=local_context,
    )
    return {"reply": response}


@agent_router.post("/ops")
async def ops_route(payload: dict):
    OpsAgent = _load_runtime_attr("agents.ops_agent", "OpsAgent", "ops agent")

    message = payload.get("message", "")
    agent = OpsAgent(generate_func=_generate_text_async)
    result = await agent.run(message, _retrieve_context(message))
    return {"reply": json.dumps(result, indent=2)}


@agent_router.post("/logistics")
async def logistics_route(payload: dict):
    LogisticsAgent = _load_runtime_attr("agents.logistics_agent", "LogisticsAgent", "logistics agent")

    message = payload.get("message", "")
    agent = LogisticsAgent(generate_func=_generate_text_async)
    result = await agent.run(message, _retrieve_context(message))
    return {"reply": json.dumps(result, indent=2)}


@agent_router.post("/economics")
async def economics_route(payload: dict):
    EconomicsAgent = _load_runtime_attr("agents.economics_agent", "EconomicsAgent", "economics agent")

    message = payload.get("message", "")
    agent = EconomicsAgent(generate_func=_generate_text_async)
    result = await agent.run(message, _retrieve_context(message))
    return {"reply": json.dumps(result, indent=2)}


@agent_router.post("/compliance")
async def compliance_route(payload: dict):
    ComplianceAgent = _load_runtime_attr("agents.compliance_agent", "ComplianceAgent", "compliance agent")

    message = payload.get("message", "")
    agent = ComplianceAgent(generate_func=_generate_text_async)
    result = await agent.run(message, _retrieve_context(message))
    return {"reply": json.dumps(result, indent=2)}


@agent_router.post("/memory")
async def memory_route(payload: dict):
    MemoryAgent = _load_runtime_attr("agents.memory_agent", "MemoryAgent", "memory agent")

    message = payload.get("message", "")
    agent = MemoryAgent(retrieve_func=_retrieve_context)
    result = await agent.retrieve(message)
    return {"reply": result}


@auth_router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    user = authenticate_user(req.username, req.password, AUTH_USERS)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    token, expires_at = create_access_token(user.username, user.roles)
    return TokenResponse(access_token=token, expires_at=expires_at, roles=user.roles)


@auth_router.get("/me")
async def me(user: CurrentUser = Depends(require_roles("viewer", "chef", "admin"))):
    return {"username": user.username, "roles": user.roles}


app.include_router(agent_router)
app.include_router(auth_router)

# ---------------------------------------------------------
# API routes
# ---------------------------------------------------------

@app.get("/")
async def read_root():
    return {"message": "47-&-SIX Concierge API is running"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "gemini_configured": client_genai is not None,
        "use_mock": USE_MOCK,
        "chromadb_available": collection is not None,
        "model": MODEL_NAME,
        "index_build_on_startup": os.getenv("BUILD_INDEX_ON_STARTUP", "false").lower() in ("1", "true", "yes"),
        "quota": {
            "used": os.getenv("GEMINI_QUOTA_USED"),
            "limit": os.getenv("GEMINI_QUOTA_LIMIT"),
        },
    }


@app.get("/status")
def status_check():
    return {
        "status": "ok",
        "routes": [
            "/",
            "/health",
            "/status",
            "/auth/login",
            "/auth/me",
            "/chef/credentials",
            "/chat",
            "/image",
            "/json",
            "/tools",
            "/embed",
            "/menu-cost",
            "/event-planning",
            "/inventory",
            "/chef-dashboard",
            "/agents/concierge",
            "/agents/ops",
            "/agents/logistics",
            "/agents/economics",
            "/agents/compliance",
            "/agents/memory",
            "/agents/menu-costing",
            "/agents/recipe",
            "/agents/client-intake",
            "/agents/menu-pricing",
            "/agents/ronin",
            "/chef/knowledge/files",
            "/chef/knowledge/portfolio",
        ],
        "gemini_configured": client_genai is not None,
        "chromadb_available": collection is not None,
        "use_mock": USE_MOCK,
    }


@app.get("/chef/credentials")
def chef_credentials(_: CurrentUser = Depends(require_roles("viewer", "chef", "admin"))):
    return {
        "name": "Chef Jesse",
        "title": "Executive Chef & Founder",
        "education": [
            "Culinary Institute of America",
            "Food Safety Certification",
            "Fine Dining Operations",
        ],
        "focus": [
            "Private chef experiences",
            "Event catering systems",
            "Menu engineering",
            "Operational efficiency",
        ],
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "gemini_configured": client_genai is not None,
        "use_mock": USE_MOCK,
        "chromadb_available": collection is not None,
        "model": MODEL_NAME,
        "index_build_on_startup": os.getenv("BUILD_INDEX_ON_STARTUP", "false").lower() in ("1", "true", "yes"),
        "quota": {
            "used": os.getenv("GEMINI_QUOTA_USED"),
            "limit": os.getenv("GEMINI_QUOTA_LIMIT"),
        },
    }


@app.post("/chat")
async def route_inquiry(inquiry: Inquiry, _: CurrentUser = Depends(require_roles("chef", "admin"))):
    local_context = _retrieve_context(inquiry.message)
    system_prompt = f"""
    You are the AI concierge for 47-&-SIX, an elite personal chef and catering business in El Paso, TX run by Executive Chef Jesse.
    Operations are strictly based on the 6-Minute Clock Cycle for extreme efficiency and margin control.

    Strict Local Operational Rule retrieved for this inquiry: {local_context}

    Answer the user's inquiry professionally, incorporating the strict local operational rule if it applies.
    If the inquiry is outside standard parameters, use your general culinary and hospitality knowledge to assist them while maintaining a precise, industrial, and highly professional tone.

    User Inquiry: {inquiry.message}
    """
    return {"response": _generate_text(system_prompt)}


@app.post("/image")
async def generate_image(prompt: str = Body(..., embed=True), _: CurrentUser = Depends(require_roles("chef", "admin"))):
    system_prompt = f"""
    Create a cinematic, chef-level image prompt for a private chef and catering business.

    Scene request: {prompt}
    """
    return {"description": _generate_text(system_prompt)}


@app.post("/json")
async def json_mode(inquiry: JsonInquiry, _: CurrentUser = Depends(require_roles("chef", "admin"))):
    prompt = f"""
    Respond strictly as JSON with:
    {{
      "intent": "string",
      "priority": "low|medium|high|critical",
      "operational_steps": ["step 1", "step 2"],
      "notes": "string"
    }}

    User inquiry: {inquiry.message}
    """
    return {"json": _generate_text(prompt, response_mime_type="application/json")}


@app.post("/tools")
async def tools_endpoint(inquiry: Inquiry, _: CurrentUser = Depends(require_roles("chef", "admin"))):
    prompt = f"""
    Provide a concise operational response for the following request and note the available tool-oriented actions.

    User inquiry: {inquiry.message}
    """
    return {"raw": _generate_text(prompt)}


@app.post("/embed")
async def embed_text(req: EmbedRequest, _: CurrentUser = Depends(require_roles("admin"))):
    if client_genai is None:
        return {"status": "not_configured", "id": req.id}

    try:
        embed = client_genai.models.embed_content(model="text-embedding-004", contents=req.text)
        embeddings = getattr(embed, "embeddings", None)
        vector = None
        if embeddings:
            first_embedding = embeddings[0]
            vector = getattr(first_embedding, "values", None)
        if collection is not None and vector is not None:
            collection.add(
                ids=[req.id],
                documents=[req.text],
                embeddings=[vector],
                metadatas=[{"source": "api"}],
            )
        return {"status": "embedded", "id": req.id}
    except Exception as exc:
        return {"status": "error", "id": req.id, "error": str(exc)}


@app.post("/menu-cost")
async def menu_cost(req: MenuCostRequest, _: CurrentUser = Depends(require_roles("chef", "admin"))):
    prompt = f"""
    You are a cost-control AI for a private chef business.

    Ingredients: {req.ingredients}
    Portions: {req.portions}

    Return a JSON object with:
    {{
      "total_cost": "float",
      "cost_per_portion": "float",
      "notes": "string"
    }}
    """
    return {"menu_cost": _generate_text(prompt, response_mime_type="application/json")}


@app.post("/event-planning")
async def event_planning(req: EventRequest, _: CurrentUser = Depends(require_roles("chef", "admin"))):
    prompt = f"""
    Build a catering plan for:

    Event Type: {req.event_type}
    Guest Count: {req.guest_count}
    Dietary Needs: {req.dietary}

    Respond as JSON:
    {{
      "menu": ["item 1", "item 2"],
      "staffing": ["role 1", "role 2"],
      "timeline": ["step 1", "step 2"],
      "equipment": ["item 1", "item 2"]
    }}
    """
    return {"event_plan": _generate_text(prompt, response_mime_type="application/json")}


@app.post("/inventory")
async def inventory(req: InventoryRequest, _: CurrentUser = Depends(require_roles("chef", "admin"))):
    prompt = f"""
    Build an inventory status report for the following items:

    {req.items}

    Respond as JSON:
    {{
      "low_stock": ["item"],
      "reorder": ["item"],
      "par_levels": {{"item": "value"}},
      "notes": "string"
    }}
    """
    return {"inventory": _generate_text(prompt, response_mime_type="application/json")}


@app.post("/chef-dashboard")
async def chef_dashboard(inquiry: Inquiry, _: CurrentUser = Depends(require_roles("chef", "admin"))):
    prompt = f"""
    Build an executive chef dashboard summary for the inquiry:

    {inquiry.message}

    Respond as JSON:
    {{
      "operational_focus": "string",
      "cost_risk": "low|medium|high",
      "menu_actions": ["action 1", "action 2"],
      "staffing_actions": ["action 1", "action 2"],
      "inventory_actions": ["action 1", "action 2"],
      "notes": "string"
    }}
    """
    return {"dashboard": _generate_text(prompt, response_mime_type="application/json")}


if chef_knowledge_router is not None:
    app.include_router(chef_knowledge_router)
