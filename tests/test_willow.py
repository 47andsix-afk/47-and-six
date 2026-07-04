import pytest

from willow.counterfactual import CounterfactualEngine
from willow.router import explain
from willow.trace import WillowTrace


def test_trace_reverse():
    t = WillowTrace()
    t.add("step1", {"a": 1})
    t.add("step2", {"b": 2})
    assert t.reverse()[0]["state"] == {"b": 2}


def test_counterfactual_minimal():
    t = WillowTrace()
    t.add("start", {"x": 10})
    t.add("end", {"y": 20})

    engine = CounterfactualEngine()
    result = engine.analyze(t)

    assert "minimal_cause_set" in result
    assert result["minimal_cause_set"] == {"x": 10}


def test_counterfactual_phase2_fields():
    t = WillowTrace()
    t.add("start", {"x": 10, "y": 20})
    t.add("agent", {"decision": "approve"})

    engine = CounterfactualEngine()
    result = engine.analyze(t)

    assert "uncertainty_map" in result
    assert "branch_amplitudes" in result
    assert "causal_graph" in result
    assert len(result["causal_graph"]["nodes"]) == 2
    assert len(result["causal_graph"]["edges"]) == 1


@pytest.mark.asyncio
async def test_explain_endpoint_payload_shape():
    payload = {
        "input": {"objective": "speed service"},
        "agents": {"ops": "trim setup"},
        "user_input": "optimize kitchen flow",
        "agent_calls": ["ops.optimize_schedule", "menu.price_menu"],
    }
    result = await explain(payload)

    assert "trace" in result
    assert "reverse_trace" in result
    assert "analysis" in result
    assert "uncertainty_map" in result["analysis"]
    assert "branch_amplitudes" in result["analysis"]
    assert "causal_graph" in result["analysis"]
