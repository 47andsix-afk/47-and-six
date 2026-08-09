from pathlib import Path
import sys

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main


@pytest.mark.asyncio
async def test_ollama_models_route_returns_models() -> None:
    token, _ = main.create_access_token("integration-tester", ["admin"])
    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/agents/models", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert "models" in body
    assert isinstance(body["models"], list)
    assert any(model["name"] == "llama3" for model in body["models"])


@pytest.mark.asyncio
async def test_gallery_route_returns_data() -> None:
    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/gallery")

    assert response.status_code == 200
    body = response.json()
    assert "categories" in body
    assert isinstance(body["categories"], list)
    assert any("items" in category for category in body["categories"])


@pytest.mark.asyncio
async def test_ollama_route_requires_auth() -> None:
    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/agents/ollama", json={"prompt": "Hello"})

    assert response.status_code == 401
    body = response.json()
    assert "detail" in body


@pytest.mark.asyncio
async def test_ollama_route_disabled_state() -> None:
    original_use_ollama = main.USE_OLLAMA
    main.USE_OLLAMA = False
    token, _ = main.create_access_token("integration-tester", ["admin"])

    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/agents/ollama",
            headers={"Authorization": f"Bearer {token}"},
            json={"prompt": "Hello"},
        )

    assert response.status_code == 503
    body = response.json()
    assert body["detail"] == "Ollama integration is disabled"
    main.USE_OLLAMA = original_use_ollama
