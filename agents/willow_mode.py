import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass
class WillowStep:
    name: str
    inputs: Dict[str, Any]
    output: Dict[str, Any]
    uncertainty: float


@dataclass
class WillowTrace:
    objective: str
    assumptions: List[str]
    evidence: List[str]
    steps: List[WillowStep]
    checksum: str


def _checksum(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _amplitude_score(step: WillowStep) -> float:
    # Quantum-inspired confidence collapse proxy in [0, 1].
    support = len(step.inputs.get("support", []))
    penalty = min(max(step.uncertainty, 0.0), 1.0)
    score = (1.0 / (1.0 + penalty)) * min(1.0, 0.2 * support + 0.4)
    return round(score, 4)


def build_trace(objective: str, assumptions: List[str], evidence: List[str]) -> WillowTrace:
    prep = WillowStep(
        name="prep",
        inputs={"assumptions": assumptions, "evidence_count": len(evidence), "support": evidence[:3]},
        output={"hypothesis": f"Solve objective: {objective}"},
        uncertainty=0.2,
    )
    infer = WillowStep(
        name="infer",
        inputs={"prior": prep.output["hypothesis"], "support": evidence, "support_count": len(evidence)},
        output={
            "draft_decision": f"Recommended action for '{objective}'",
            "dominant_factors": assumptions[:3],
        },
        uncertainty=0.35,
    )
    collapse = WillowStep(
        name="collapse",
        inputs={"candidate": infer.output["draft_decision"], "support": evidence[:5]},
        output={
            "decision": infer.output["draft_decision"],
            "confidence": _amplitude_score(infer),
        },
        uncertainty=0.25,
    )
    payload = {
        "objective": objective,
        "assumptions": assumptions,
        "evidence": evidence,
        "steps": [asdict(prep), asdict(infer), asdict(collapse)],
    }
    checksum = _checksum(payload)
    return WillowTrace(
        objective=objective,
        assumptions=assumptions,
        evidence=evidence,
        steps=[prep, infer, collapse],
        checksum=checksum,
    )


def reverse_engineer(trace: WillowTrace) -> Dict[str, Any]:
    last = trace.steps[-1]
    minimal_causes = trace.assumptions[:2] if trace.assumptions else []
    fragile_points = [
        s.name
        for s in trace.steps
        if s.uncertainty >= 0.3
    ]
    return {
        "decision": last.output.get("decision"),
        "minimal_causes": minimal_causes,
        "fragile_points": fragile_points,
        "trace_checksum": trace.checksum,
    }


def counterfactuals(trace: WillowTrace, max_items: int = 3) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    base = trace.steps[-1].output.get("decision", "")
    for i, assumption in enumerate(trace.assumptions[:max_items]):
        items.append(
            {
                "change": f"Negate assumption: {assumption}",
                "predicted_flip": f"Alternative path {i + 1} for '{trace.objective}'",
                "distance": round(0.2 + i * 0.15, 2),
                "from_decision": base,
            }
        )
    return items


def run_willow_mode(
    objective: str,
    assumptions: List[str],
    evidence: List[str],
    max_counterfactuals: int = 3,
) -> Dict[str, Any]:
    trace = build_trace(objective, assumptions, evidence)
    reverse = reverse_engineer(trace)
    cfs = counterfactuals(trace, max_items=max_counterfactuals)
    return {
        "trace": {
            "objective": trace.objective,
            "assumptions": trace.assumptions,
            "evidence": trace.evidence,
            "steps": [asdict(s) for s in trace.steps],
            "checksum": trace.checksum,
        },
        "reverse": reverse,
        "counterfactuals": cfs,
    }
