from agents.willow_mode import run_willow_mode


def test_willow_mode_has_reversible_trace():
    result = run_willow_mode(
        objective="Reduce prep-time variance",
        assumptions=["station discipline", "batching works", "supplier stable"],
        evidence=["ticket logs", "waste logs", "labor report"],
    )

    assert "trace" in result
    assert "reverse" in result
    assert "counterfactuals" in result
    assert result["reverse"]["trace_checksum"] == result["trace"]["checksum"]
    assert isinstance(result["counterfactuals"], list)
    assert len(result["counterfactuals"]) >= 1
