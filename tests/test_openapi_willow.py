from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main


def test_openapi_contains_willow_paths() -> None:
    schema = main.app.openapi()
    paths = schema.get("paths", {})

    assert "/willow/explain" in paths
    assert "/agents/willow" in paths


def test_openapi_willow_explain_contract() -> None:
    schema = main.app.openapi()
    post = schema["paths"]["/willow/explain"]["post"]

    assert "requestBody" in post
    assert "responses" in post
    assert "200" in post["responses"]
    assert "422" in post["responses"]

    content = post["requestBody"]["content"]
    assert "application/json" in content


def test_openapi_agents_willow_contract() -> None:
    schema = main.app.openapi()
    post = schema["paths"]["/agents/willow"]["post"]

    assert "requestBody" in post
    assert "responses" in post
    assert "200" in post["responses"]
    assert "422" in post["responses"]

    params = post.get("parameters", [])
    names = [p.get("name") for p in params]
    assert "authorization" in names
