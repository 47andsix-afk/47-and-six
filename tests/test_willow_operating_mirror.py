from pathlib import Path
import sys

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main


def _sample_graph() -> dict:
    return {
        "graph_id": "willow_operating_mirror_v1",
        "name": "Willow Operating Mirror",
        "domain": "chef_operations",
        "version": "1.0.0",
        "nodes": [
            {
                "id": "menu_complexity",
                "label": "Menu Complexity",
                "type": "operational_driver",
                "unit": "score_0_100",
                "current_value": 68,
                "confidence": 0.82,
                "description": "Complexity score",
            },
            {
                "id": "prep_labor",
                "label": "Prep Labor",
                "type": "resource_load",
                "unit": "hours",
                "current_value": 42,
                "confidence": 0.78,
                "description": "Prep labor hours",
            },
            {
                "id": "gross_margin",
                "label": "Gross Margin",
                "type": "financial_outcome",
                "unit": "percentage",
                "current_value": 0.41,
                "confidence": 0.8,
                "description": "Projected gross margin",
            },
            {
                "id": "future_revenue",
                "label": "Future Revenue",
                "type": "business_outcome",
                "unit": "usd",
                "current_value": 12000,
                "confidence": 0.59,
                "description": "Projected future revenue",
            },
            {
                "id": "execution_risk",
                "label": "Execution Risk",
                "type": "risk",
                "unit": "score_0_100",
                "current_value": 57,
                "confidence": 0.76,
                "description": "Execution risk score",
            },
            {
                "id": "proposal_acceptance",
                "label": "Proposal Acceptance",
                "type": "sales_outcome",
                "unit": "probability",
                "current_value": 0.69,
                "confidence": 0.68,
                "description": "Acceptance probability",
            },
            {
                "id": "brand_risk",
                "label": "Brand Risk",
                "type": "risk",
                "unit": "score_0_100",
                "current_value": 24,
                "confidence": 0.65,
                "description": "Brand risk score",
            },
        ],
        "edges": [
            {
                "id": "menu_complexity_to_prep_labor",
                "source": "menu_complexity",
                "target": "prep_labor",
                "polarity": "positive",
                "weight": 0.74,
                "lag": "pre_event",
                "rationale": "Complex menu increases prep labor",
            },
            {
                "id": "prep_labor_to_execution_risk",
                "source": "prep_labor",
                "target": "execution_risk",
                "polarity": "positive",
                "weight": 0.58,
                "lag": "event_day",
                "rationale": "More labor pressure increases risk",
            },
            {
                "id": "execution_risk_to_brand_risk",
                "source": "execution_risk",
                "target": "brand_risk",
                "polarity": "positive",
                "weight": 0.76,
                "lag": "post_event",
                "rationale": "Execution failures increase brand risk",
            },
            {
                "id": "prep_labor_to_gross_margin",
                "source": "prep_labor",
                "target": "gross_margin",
                "polarity": "negative",
                "weight": 0.2,
                "lag": "proposal",
                "rationale": "Labor pressure can reduce margin",
            },
            {
                "id": "gross_margin_to_future_revenue",
                "source": "gross_margin",
                "target": "future_revenue",
                "polarity": "positive",
                "weight": 0.57,
                "lag": "future",
                "rationale": "Higher margin improves retained revenue",
            },
            {
                "id": "gross_margin_to_proposal_acceptance",
                "source": "gross_margin",
                "target": "proposal_acceptance",
                "polarity": "mixed",
                "weight": 0.3,
                "lag": "proposal",
                "rationale": "Margin and pricing can affect acceptance in mixed ways",
            },
        ],
        "metadata": {"created_by": "test"},
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_operating_mirror_graph_and_simulation_flow() -> None:
    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        seed = await client.post("/willow/operating-mirror/graph/seed")
        assert seed.status_code == 200

        store_graph = await client.post("/willow/operating-mirror/graph", json=_sample_graph())
        assert store_graph.status_code == 200

        read_graph = await client.get("/willow/operating-mirror/graph")
        assert read_graph.status_code == 200
        assert read_graph.json()["graph_id"] == "willow_operating_mirror_v1"

        simulation_payload = {
            "simulation_id": "sim_event_2026_001",
            "graph_id": "willow_operating_mirror_v1",
            "scenario_name": "Raise menu complexity",
            "context": {"event_type": "private_dinner"},
            "baseline": {
                "menu_complexity": 68,
                "prep_labor": 42,
                "execution_risk": 57,
                "gross_margin": 0.41,
                "future_revenue": 12000,
                "proposal_acceptance": 0.69,
                "brand_risk": 24,
            },
            "interventions": [
                {
                    "node_id": "menu_complexity",
                    "operation": "increase_by",
                    "value": 12,
                    "reason": "Client requested more ambitious menu",
                }
            ],
            "simulation_options": {
                "propagation_depth": 4,
                "include_counterfactuals": True,
                "include_fragility": True,
                "include_recommendations": True,
                "confidence_threshold": 0.6,
            },
        }

        simulation = await client.post("/willow/operating-mirror/simulate", json=simulation_payload)
        assert simulation.status_code == 200
        sim_body = simulation.json()
        assert sim_body["simulation_id"] == "sim_event_2026_001"
        assert "projected_values" in sim_body
        assert "projected_changes" in sim_body
        assert "top_causal_paths" in sim_body
        assert len(sim_body["top_causal_paths"]) >= 1

        dashboard = await client.get("/willow/operating-mirror/dashboard")
        assert dashboard.status_code == 200
        dash_body = dashboard.json()
        assert dash_body["dashboard_id"] == "willow_operating_mirror_dashboard"
        assert "kpi_cards" in dash_body
        assert len(dash_body["kpi_cards"]) >= 1
        assert "top_causal_paths" in dash_body
        assert "risk_panel" in dash_body
        assert "recommended_actions" in dash_body


@pytest.mark.asyncio
@pytest.mark.integration
async def test_operating_mirror_decision_ledger_and_reverse_engineer() -> None:
    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        decision = await client.post(
            "/willow/operating-mirror/decision-ledger",
            json={
                "decision_id": "decision_001",
                "decision_type": "event_pricing",
                "entity_type": "event",
                "entity_id": "event_001",
                "title": "Price private dinner",
                "recommendation": "Quote premium menu",
                "confidence": 0.76,
                "expected_value": 4800,
                "risk_score": 0.34,
                "inputs": {"guest_count": 24},
                "assumptions": [{"assumption": "Client accepts premium value framing"}],
                "alternatives": [{"label": "lower price"}],
            },
        )
        assert decision.status_code == 200

        read_decision = await client.get("/willow/operating-mirror/decision-ledger/decision_001")
        assert read_decision.status_code == 200
        assert read_decision.json()["decision_type"] == "event_pricing"

        reverse = await client.post(
            "/willow/operating-mirror/reverse-engineer",
            json={
                "entity_type": "event",
                "entity_id": "event_001",
                "decision_id": "decision_001",
                "predicted": {"gross_margin": 0.42, "prep_labor": 38},
                "actual": {"gross_margin": 0.34, "prep_labor": 46},
                "context": {"late_client_changes": True},
            },
        )
        assert reverse.status_code == 200
        rev_body = reverse.json()
        assert "review_id" in rev_body
        assert "variance" in rev_body
        assert "root_causes" in rev_body
        assert len(rev_body["variance"]) >= 1
        assert "recommended_fix" in rev_body["root_causes"][0]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_seed_graph_behavior_overwrite_toggle() -> None:
    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.post("/willow/operating-mirror/graph/seed")
        assert first.status_code == 200

        second = await client.post("/willow/operating-mirror/graph/seed")
        assert second.status_code == 200
        assert second.json()["status"] in {"exists", "seeded"}

        third = await client.post("/willow/operating-mirror/graph/seed?overwrite=true")
        assert third.status_code == 200
        assert third.json()["status"] == "seeded"
        assert third.json()["overwrite"] is True
