from typing import Any, Dict, List

from .operating_mirror_models import WillowGraph, WillowSimulationRequest


def apply_intervention(value: float, operation: str, amount: float) -> float:
    if operation == "set":
        return amount
    if operation == "increase_by":
        return value + amount
    if operation == "decrease_by":
        return value - amount
    if operation == "multiply_by":
        return value * amount
    raise ValueError(f"Unsupported operation: {operation}")


def clamp_value(value: float, unit: str) -> float:
    if unit == "score_0_100":
        return max(0.0, min(100.0, value))
    if unit in {"probability", "percentage"}:
        return max(0.0, min(1.0, value))
    return max(0.0, value)


def simulate_graph(graph: WillowGraph, request: WillowSimulationRequest) -> Dict[str, Any]:
    node_map = {node.id: node for node in graph.nodes}
    values = dict(request.baseline)

    for intervention in request.interventions:
        old_value = values.get(intervention.node_id, 0.0)
        values[intervention.node_id] = apply_intervention(
            old_value,
            intervention.operation,
            intervention.value,
        )

    changed = {intervention.node_id for intervention in request.interventions}

    for _ in range(request.simulation_options.propagation_depth):
        next_values = dict(values)
        for edge in graph.edges:
            if edge.source not in changed:
                continue

            source_node = node_map.get(edge.source)
            target_node = node_map.get(edge.target)
            if source_node is None or target_node is None:
                continue

            baseline_source = request.baseline.get(edge.source, source_node.current_value)
            source_delta = values.get(edge.source, baseline_source) - baseline_source
            if source_delta == 0:
                continue

            signed_weight = edge.weight if edge.polarity == "positive" else -edge.weight
            if edge.polarity == "mixed":
                signed_weight = edge.weight * 0.35

            target_delta = source_delta * signed_weight
            current_target = next_values.get(edge.target, target_node.current_value)
            next_values[edge.target] = clamp_value(current_target + target_delta, target_node.unit)

        changed = {
            node_id
            for node_id in next_values
            if next_values.get(node_id) != values.get(node_id)
        }
        values = next_values
        if not changed:
            break

    projected_changes = []
    for node in graph.nodes:
        baseline_value = request.baseline.get(node.id, node.current_value)
        projected_value = values.get(node.id, baseline_value)
        delta = projected_value - baseline_value
        if abs(delta) > 0.001:
            projected_changes.append(
                {
                    "node_id": node.id,
                    "label": node.label,
                    "baseline": baseline_value,
                    "projected": projected_value,
                    "delta": delta,
                    "unit": node.unit,
                }
            )

    top_causal_paths = trace_causal_paths(
        graph=graph,
        interventions=request.interventions,
        projected_values=values,
        baseline=request.baseline,
        max_depth=min(5, request.simulation_options.propagation_depth + 1),
        top_k=5,
    )

    return {
        "simulation_id": request.simulation_id,
        "scenario_name": request.scenario_name,
        "projected_values": values,
        "projected_changes": projected_changes,
        "top_causal_paths": top_causal_paths,
    }


def trace_causal_paths(
    graph: WillowGraph,
    interventions: List[Any],
    projected_values: Dict[str, float],
    baseline: Dict[str, float],
    max_depth: int = 5,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    adjacency: Dict[str, List[Any]] = {}
    node_labels = {n.id: n.label for n in graph.nodes}
    for edge in graph.edges:
        adjacency.setdefault(edge.source, []).append(edge)

    changed_nodes = {
        node_id
        for node_id, proj in projected_values.items()
        if abs(proj - baseline.get(node_id, proj)) > 0.001
    }

    starts = [i.node_id for i in interventions]
    paths: List[Dict[str, Any]] = []

    def _edge_direction_sign(edge: Any) -> int:
        if edge.polarity == "positive":
            return 1
        if edge.polarity == "negative":
            return -1
        return 1

    def _dfs(current: str, visited: List[str], strength: float, sign: int, depth: int) -> None:
        if depth >= max_depth:
            return

        for edge in adjacency.get(current, []):
            nxt = edge.target
            if nxt in visited:
                continue

            next_strength = strength * float(edge.weight)
            next_sign = sign * _edge_direction_sign(edge)
            new_path = visited + [nxt]

            if nxt in changed_nodes and len(new_path) >= 2:
                paths.append(
                    {
                        "path": new_path,
                        "strength": round(next_strength, 4),
                        "direction": "positive" if next_sign >= 0 else "negative",
                        "business_translation": f"{node_labels.get(new_path[0], new_path[0])} influences {node_labels.get(new_path[-1], new_path[-1])}.",
                    }
                )

            _dfs(nxt, new_path, next_strength, next_sign, depth + 1)

    for start in starts:
        _dfs(start, [start], 1.0, 1, 0)

    dedup: Dict[tuple[str, ...], Dict[str, Any]] = {}
    for p in paths:
        key = tuple(p["path"])
        existing = dedup.get(key)
        if existing is None or p["strength"] > existing["strength"]:
            dedup[key] = p

    ranked = sorted(dedup.values(), key=lambda x: x["strength"], reverse=True)
    return ranked[:top_k]
