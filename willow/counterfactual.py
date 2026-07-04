from typing import Any, Dict

from willow.trace import WillowTrace


class CounterfactualEngine:
    def analyze(self, trace: WillowTrace) -> Dict[str, Any]:
        if not trace.steps:
            return {"counterfactual": "no data"}

        final = trace.steps[-1]["state"]
        minimal = trace.minimal_causes()
        uncertainty_map = self._compute_uncertainty_map(trace)
        branch_amplitudes = self._compute_branch_amplitudes(trace)
        causal_graph = self._compute_causal_graph(trace)

        return {
            "final_state": final,
            "minimal_cause_set": minimal,
            "fragility_points": self._compute_fragility(minimal, final),
            "uncertainty_map": uncertainty_map,
            "branch_amplitudes": branch_amplitudes,
            "causal_graph": causal_graph,
        }

    def _compute_fragility(self, minimal: Dict[str, Any], final: Dict[str, Any]):
        fragility = {}
        for key, value in minimal.items():
            fragility[key] = f"changing '{key}' may alter final output"
        return fragility

    def _compute_uncertainty_map(self, trace: WillowTrace) -> Dict[str, float]:
        total = len(trace.steps) or 1
        mapping: Dict[str, float] = {}
        for i, step in enumerate(trace.steps):
            # Lightweight deterministic score that grows with distance from initial state.
            mapping[step.get("description", f"step-{i}")] = round((i + 1) / (total + 1), 3)
        return mapping

    def _compute_branch_amplitudes(self, trace: WillowTrace) -> Dict[str, float]:
        amplitudes: Dict[str, float] = {}
        for i, step in enumerate(trace.steps):
            state = step.get("state", {})
            support = len(state) if isinstance(state, dict) else 1
            amplitudes[f"branch_{i + 1}"] = round(min(1.0, 0.3 + 0.15 * support), 3)
        return amplitudes

    def _compute_causal_graph(self, trace: WillowTrace) -> Dict[str, Any]:
        nodes = []
        edges = []
        for i, step in enumerate(trace.steps):
            node_id = f"n{i + 1}"
            nodes.append({"id": node_id, "label": step.get("description", node_id)})
            if i > 0:
                edges.append({"from": f"n{i}", "to": node_id, "type": "influences"})
        return {"nodes": nodes, "edges": edges}
