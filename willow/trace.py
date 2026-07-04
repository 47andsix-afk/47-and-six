from typing import Any, Dict, List


class WillowTrace:
    def __init__(self):
        self.steps: List[Dict[str, Any]] = []

    def add(self, description: str, state: Dict[str, Any]):
        self.steps.append({
            "description": description,
            "state": state,
        })

    def reverse(self) -> List[Dict[str, Any]]:
        return list(reversed(self.steps))

    def minimal_causes(self) -> Dict[str, Any]:
        if not self.steps:
            return {}
        return self.steps[0]["state"]
