from agents.menu_cost_agent import run_menu_costing
from agents.recipe_agent import run_recipe
from agents.client_intake_agent import run_client_intake
from agents.menu_pricing_engine import run_menu_pricing


def run_ronin(task: str, message: str) -> str:
    t = (task or "").lower()
    if t == "client_intake":
        return run_client_intake(message)
    if t == "menu_costing":
        return run_menu_costing(message)
    if t == "recipe":
        return run_recipe(message)
    if t == "menu_pricing":
        return run_menu_pricing(message)
    return "Unknown RONIN task."
