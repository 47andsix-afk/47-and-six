from agents.menu_cost_agent import run_menu_costing
from agents.recipe_agent import run_recipe


def run_menu_pricing(user_message: str) -> str:
    econ = run_menu_costing(f"Cost and margin for: {user_message}")
    recipe = run_recipe(f"Sourcing and recipe constraints for: {user_message}")
    return f"Pricing analysis:\n\n{econ}\n\nRecipe/logistics notes:\n\n{recipe}"
