import asyncio
from typing import Any, Dict, List, Optional, Tuple

from .registry import AgentRegistry
from core.gemini_client import GeminiClient


class Orchestrator:
    def __init__(self, registry: AgentRegistry, gemini: Optional[GeminiClient] = None) -> None:
        self.registry = registry
        self.gemini = gemini

    async def run(
        self,
        user_input: str,
        chaining_plan: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        if chaining_plan:
            return await self._run_with_chaining(chaining_plan)
        return await self._run_with_gemini(user_input)

    async def _run_with_gemini(self, user_input: str) -> Dict[str, Any]:
        all_functions: List[Dict[str, Any]] = []
        for agent in self.registry.all().values():
            for fn in agent.list_functions():
                fn_decl = dict(fn)
                fn_decl["name"] = f"{agent.name}.{fn['name']}"
                all_functions.append(fn_decl)

        if self.gemini is None:
            return {}

        gemini_response = await self.gemini.call_functions(functions=all_functions, user_input=user_input)
        calls = gemini_response.get("function_calls", [])

        async def _execute(call: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
            full_name = call["name"]
            agent_name, fn_name = full_name.split(".", 1)
            args = call.get("args", {})

            agent = self.registry.get(agent_name)
            if agent is None:
                return agent_name, {fn_name: {"error": "agent not found"}}

            result = await agent.call_function(fn_name, **args)
            return agent_name, {fn_name: result}

        results = await asyncio.gather(*[_execute(c) for c in calls])
        return self._merge_results(results)

    async def run_parallel(self, calls: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        calls: list of {agent_name, function_name, kwargs}
        merge results by agent name (R1), dummy execution for now.
        """

        async def _run_call(call: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
            agent_name = call["agent_name"]
            function_name = call["function_name"]
            kwargs = call.get("kwargs", {})

            agent = self.registry.get(agent_name)
            if agent is None:
                return agent_name, {
                    "error": f"agent '{agent_name}' not found",
                }

            result = await agent.call_function(function_name, **kwargs)
            return agent_name, {function_name: result}

        results = await asyncio.gather(*[_run_call(c) for c in calls])

        return self._merge_results(results)

    async def _run_with_chaining(self, chaining_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        results: Dict[str, Dict[str, Any]] = {}

        def resolve_ref(ref: str) -> Any:
            agent_name, fn_name = ref.split(".", 1)
            return results.get(agent_name, {}).get(fn_name)

        remaining = list(chaining_plan)

        while remaining:
            ready = [
                step
                for step in remaining
                if all(
                    dep.split(".", 1)[0] in results
                    and dep.split(".", 1)[1] in results[dep.split(".", 1)[0]]
                    for dep in step.get("depends_on", [])
                )
            ]

            if not ready:
                break

            async def _execute_step(step: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
                agent_name = step["agent"]
                fn_name = step["function"]
                raw_args = step.get("args", {})

                args: Dict[str, Any] = {}
                for key, value in raw_args.items():
                    if isinstance(value, str) and "." in value:
                        args[key] = resolve_ref(value)
                    else:
                        args[key] = value

                agent = self.registry.get(agent_name)
                if agent is None:
                    return agent_name, {fn_name: {"error": "agent not found"}}

                result = await agent.call_function(fn_name, **args)
                return agent_name, {fn_name: result}

            wave_results = await asyncio.gather(*[_execute_step(s) for s in ready])

            for agent_name, payload in wave_results:
                results.setdefault(agent_name, {}).update(payload)

            remaining = [step for step in remaining if step not in ready]

        return results

    @staticmethod
    def _merge_results(results: List[Tuple[str, Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
        merged: Dict[str, Dict[str, Any]] = {}
        for agent_name, payload in results:
            if agent_name not in merged:
                merged[agent_name] = {}
            merged[agent_name].update(payload)
        return merged
