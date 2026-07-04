import pytest

from agents.chef_agent import ChefAgent
from agents.menu_agent import MenuAgent
from agents.ops_agent import OpsAgent
from agents.orchestrator import Orchestrator
from agents.registry import AgentRegistry


class DummyGemini:
    async def call_functions(self, functions, user_input):
        return {
            "function_calls": [
                {
                    "name": "chef_agent.analyze_recipe",
                    "args": {
                        "recipe": "Test recipe",
                        "ingredients": ["a", "b"],
                    },
                },
                {
                    "name": "ops_agent.calculate_costs",
                    "args": {
                        "items": [{"name": "a", "cost": 1.0}],
                    },
                },
                {
                    "name": "menu_agent.menu_engineering",
                    "args": {
                        "menu": [{"name": "Test dish"}],
                    },
                },
            ]
        }


@pytest.mark.asyncio
async def test_parallel_multi_agent():
    registry = AgentRegistry()
    registry.register(ChefAgent())
    registry.register(OpsAgent())
    registry.register(MenuAgent())

    orch = Orchestrator(registry, DummyGemini())

    result = await orch.run("Test input")

    assert "chef_agent" in result
    assert "ops_agent" in result
    assert "menu_agent" in result
    assert "analyze_recipe" in result["chef_agent"]
    assert "calculate_costs" in result["ops_agent"]
    assert "menu_engineering" in result["menu_agent"]


@pytest.mark.asyncio
async def test_chaining_plan():
    registry = AgentRegistry()
    registry.register(ChefAgent())
    registry.register(OpsAgent())
    registry.register(MenuAgent())

    orch = Orchestrator(registry, DummyGemini())

    chaining_plan = [
        {
            "agent": "chef_agent",
            "function": "analyze_recipe",
            "args": {
                "recipe": "Chain recipe",
                "ingredients": ["x", "y"],
            },
            "depends_on": [],
        },
        {
            "agent": "ops_agent",
            "function": "calculate_costs",
            "args": {
                "items_from": "chef_agent.analyze_recipe",
            },
            "depends_on": ["chef_agent.analyze_recipe"],
        },
        {
            "agent": "menu_agent",
            "function": "profit_projection",
            "args": {
                "menu_from": "chef_agent.analyze_recipe",
                "costs_from": "ops_agent.calculate_costs",
            },
            "depends_on": [
                "chef_agent.analyze_recipe",
                "ops_agent.calculate_costs",
            ],
        },
    ]

    result = await orch.run(user_input="", chaining_plan=chaining_plan)

    assert "chef_agent" in result
    assert "ops_agent" in result
    assert "menu_agent" in result
    assert "analyze_recipe" in result["chef_agent"]
    assert "calculate_costs" in result["ops_agent"]
    assert "profit_projection" in result["menu_agent"]
