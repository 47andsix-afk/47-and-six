from typing import Any, Dict
from uuid import uuid4

from fastapi import APIRouter, Body, HTTPException, Query, status

from willow.counterfactual import CounterfactualEngine
from willow.operating_mirror_engine import simulate_graph
from willow.operating_mirror_models import (
    DecisionLedgerItem,
    ReverseEngineerRequest,
    WillowGraph,
    WillowSimulationRequest,
)
from willow.operating_mirror_seed import default_operating_mirror_graph
from willow.operating_mirror_store import (
    get_any_graph,
    get_decision,
    get_graph,
    get_latest_dashboard,
    init_store,
    save_dashboard,
    save_reverse_review,
    save_simulation,
    upsert_decision,
    upsert_graph,
)
from willow.trace import WillowTrace


router = APIRouter(prefix="/willow", tags=["Willow Mode"])

init_store()

_active_graph_id: str | None = None


def _impact_score(delta: float, positive: bool = True) -> int:
    mag = min(100.0, abs(delta) * 100.0)
    if positive:
        return int(min(100, 50 + mag))
    return int(max(1, 50 - mag))


def _build_dashboard(simulation: dict[str, Any]) -> dict[str, Any]:
    projected = simulation.get("projected_values", {})
    changes = {c["node_id"]: c for c in simulation.get("projected_changes", [])}
    top_paths = simulation.get("top_causal_paths", [])

    risk = projected.get("execution_risk", 0.0)
    margin = projected.get("gross_margin", 0.0)
    decision = "approve_with_controls" if margin >= 0.35 and risk <= 70 else "review_required"
    headline = "This scenario is viable with controls." if decision == "approve_with_controls" else "This scenario needs mitigation before approval."

    def _card(node_id: str, label: str, direction_positive: bool) -> dict[str, Any]:
        c = changes.get(node_id, {})
        baseline = c.get("baseline", projected.get(node_id, 0.0))
        value = c.get("projected", projected.get(node_id, baseline))
        delta = c.get("delta", 0.0)
        return {
            "id": node_id,
            "label": label,
            "value": value,
            "baseline": baseline,
            "delta": delta,
            "direction": "positive" if (delta >= 0 and direction_positive) or (delta < 0 and not direction_positive) else "negative",
            "impact_score": _impact_score(delta, positive=direction_positive),
        }

    fragility_candidates = []
    for node_id in ["prep_labor", "team_stress", "execution_risk", "proposal_acceptance", "brand_risk"]:
        c = changes.get(node_id)
        if not c:
            continue
        score = min(100, int(abs(c.get("delta", 0.0)) * 100))
        fragility_candidates.append({
            "node_id": node_id,
            "score": score,
            "message": f"{node_id.replace('_', ' ').title()} changed and should be watched.",
        })

    fragility_candidates = sorted(fragility_candidates, key=lambda x: x["score"], reverse=True)
    highest_risk = fragility_candidates[0] if fragility_candidates else {"node_id": "execution_risk", "score": int(risk), "message": "Execution risk is the current main watch item."}

    recommended_actions = []
    if projected.get("prep_labor", 0) > 45:
        recommended_actions.append(
            {
                "priority": 1,
                "title": "Add one prep block before event day",
                "impact": "Reduces labor compression and execution risk.",
                "estimated_kpi_effect": [
                    {"kpi": "Execution Risk", "change": "-3 to -6 pts"},
                    {"kpi": "Brand Risk", "change": "-1 to -4 pts"},
                ],
            }
        )
    if projected.get("proposal_acceptance", 1.0) < 0.68:
        recommended_actions.append(
            {
                "priority": 2,
                "title": "Strengthen premium value framing",
                "impact": "Protects acceptance while maintaining margin.",
                "estimated_kpi_effect": [
                    {"kpi": "Proposal Acceptance", "change": "+2 to +5 pts"},
                ],
            }
        )
    if projected.get("execution_risk", 0.0) > 60:
        recommended_actions.append(
            {
                "priority": 3,
                "title": "Assign strongest sous chef to high-complexity station",
                "impact": "Offsets complexity-driven execution pressure.",
                "estimated_kpi_effect": [
                    {"kpi": "Execution Risk", "change": "-2 to -5 pts"},
                    {"kpi": "Client Experience", "change": "+1 to +3 pts"},
                ],
            }
        )

    return {
        "dashboard_id": "willow_operating_mirror_dashboard",
        "title": "Willow Operating Mirror",
        "status": {
            "overall": decision,
            "confidence": 0.72,
            "headline": headline,
        },
        "kpi_cards": [
            _card("gross_margin", "Gross Margin", True),
            _card("future_revenue", "Future Revenue", True),
            _card("execution_risk", "Execution Risk", False),
            _card("proposal_acceptance", "Proposal Acceptance", True),
            _card("brand_risk", "Brand Risk", False),
        ],
        "top_causal_paths": top_paths,
        "risk_panel": {
            "highest_risk": highest_risk,
            "watchlist": fragility_candidates[1:4],
        },
        "recommended_actions": recommended_actions,
        "plain_english_summary": "Main tradeoff is margin upside versus labor and execution pressure.",
    }


def _graph_causal_weight(graph: WillowGraph | None, metric: str) -> float:
    if graph is None:
        return 0.4
    candidates = [e.weight for e in graph.edges if e.source == metric or e.target == metric]
    return max(candidates) if candidates else 0.4


def _node_confidence(graph: WillowGraph | None, metric: str) -> float:
    if graph is None:
        return 0.7
    for node in graph.nodes:
        if node.id == metric:
            return float(node.confidence)
    return 0.7


def _recommended_fix(metric: str) -> str:
    mapping = {
        "prep_labor": "Add a plating and prep complexity multiplier to labor estimates.",
        "gross_margin": "Trigger repricing when cost variance exceeds threshold.",
        "ingredient_cost": "Add vendor substitution review before final ordering.",
        "execution_risk": "Increase pre-event control checks and staffing guardrails.",
    }
    return mapping.get(metric, "Review this metric in the decision ledger and adjust assumptions.")


@router.post("/explain")
async def explain(payload: Dict[str, Any] = Body(...)):
    trace = WillowTrace()
    trace.add("input received", payload.get("input", {}))
    trace.add("agent output", payload.get("agents", {}))
    if "user_input" in payload:
        trace.add("user input", {"value": payload.get("user_input")})
    if "agent_calls" in payload:
        trace.add("agent call list", {"calls": payload.get("agent_calls", [])})

    engine = CounterfactualEngine()
    analysis = engine.analyze(trace)

    return {
        "trace": trace.steps,
        "reverse_trace": trace.reverse(),
        "analysis": analysis,
    }


@router.get("/operating-mirror/graph")
async def get_operating_mirror_graph():
    graph_payload = None
    if _active_graph_id is not None:
        graph_payload = get_graph(_active_graph_id)
    if graph_payload is None:
        graph_payload = get_any_graph()
    if graph_payload is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active operating mirror graph is set.",
        )
    return WillowGraph.model_validate(graph_payload)


@router.post("/operating-mirror/graph")
async def set_operating_mirror_graph(graph: WillowGraph):
    global _active_graph_id
    upsert_graph(graph.model_dump())
    _active_graph_id = graph.graph_id
    return {"status": "stored", "graph_id": graph.graph_id}


@router.post("/operating-mirror/graph/seed")
async def seed_operating_mirror_graph(overwrite: bool = Query(default=False)):
    global _active_graph_id

    existing = get_graph("willow_operating_mirror_v1")
    if existing is not None and not overwrite:
        _active_graph_id = existing["graph_id"]
        return {"status": "exists", "graph_id": existing["graph_id"]}

    graph = default_operating_mirror_graph()
    upsert_graph(graph)
    _active_graph_id = graph["graph_id"]
    return {"status": "seeded", "graph_id": graph["graph_id"], "overwrite": overwrite}


@router.post("/operating-mirror/simulate")
async def simulate_operating_mirror(request: WillowSimulationRequest):
    graph_payload = get_graph(request.graph_id)
    if graph_payload is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested graph is not active.",
        )
    graph = WillowGraph.model_validate(graph_payload)

    simulation = simulate_graph(graph, request)
    dashboard = _build_dashboard(simulation)

    save_simulation(
        simulation_id=request.simulation_id,
        graph_id=request.graph_id,
        scenario_name=request.scenario_name,
        request=request.model_dump(),
        response=simulation,
    )
    save_dashboard(snapshot_id=str(uuid4()), simulation_id=request.simulation_id, dashboard=dashboard)

    return simulation


@router.post("/operating-mirror/reverse-engineer")
async def reverse_engineer_operating_mirror(request: ReverseEngineerRequest):
    graph_payload = get_any_graph()
    graph = WillowGraph.model_validate(graph_payload) if graph_payload is not None else None
    variance = []
    root_causes = []
    for key, pred in request.predicted.items():
        actual = request.actual.get(key)
        if actual is None:
            continue
        delta = actual - pred
        severity = "high" if abs(delta) >= max(1.0, abs(pred) * 0.2) else ("medium" if abs(delta) >= max(0.25, abs(pred) * 0.1) else "low")
        variance.append({"metric": key, "predicted": pred, "actual": actual, "delta": delta, "severity": severity})

        severity_multiplier = 1.3 if severity == "high" else (1.0 if severity == "medium" else 0.7)
        causal_weight = _graph_causal_weight(graph, key)
        confidence = _node_confidence(graph, key)
        score = min(1.0, abs(delta) * causal_weight * confidence * severity_multiplier)

        if abs(delta) > 0:
            root_causes.append(
                {
                    "cause": f"variance_in_{key}",
                    "affected_metrics": [key],
                    "estimated_contribution": round(score, 4),
                    "recommended_fix": _recommended_fix(key),
                }
            )

    review = {
        "entity_type": request.entity_type,
        "entity_id": request.entity_id,
        "decision_id": request.decision_id,
        "variance": variance,
        "root_causes": sorted(root_causes, key=lambda x: x["estimated_contribution"], reverse=True)[:5],
        "summary": "Predicted vs actual variance computed with weighted root-cause scoring.",
    }

    review_id = str(uuid4())
    save_reverse_review(
        review_id=review_id,
        entity_type=request.entity_type,
        entity_id=request.entity_id,
        decision_id=request.decision_id,
        review=review,
    )

    return {"review_id": review_id, **review}


@router.get("/operating-mirror/dashboard")
async def get_operating_mirror_dashboard():
    dashboard = get_latest_dashboard()
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No dashboard available. Run a simulation first.",
        )
    return dashboard


@router.post("/operating-mirror/decision-ledger")
async def create_decision_ledger_item(item: DecisionLedgerItem):
    upsert_decision(item.model_dump())
    return {"status": "stored", "decision_id": item.decision_id}


@router.get("/operating-mirror/decision-ledger/{decision_id}")
async def get_decision_ledger_item(decision_id: str):
    item = get_decision(decision_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")
    return item
