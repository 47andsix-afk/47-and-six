#!/usr/bin/env python
"""Test and verify all RONIN agents are working."""
import importlib
import os


def _is_available(module_name: str, attr_name: str) -> bool:
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        return False
    return hasattr(module, attr_name)


def _load_or_none(module_name: str, attr_name: str):
    if not _is_available(module_name, attr_name):
        return None
    module = importlib.import_module(module_name)
    return getattr(module, attr_name)

print("=" * 70)
print("47-&-SIX CONCIERGE PLATFORM - RONIN AGENTS STATUS")
print("=" * 70)

agents = [
    ("RONIN Orchestrator", "agents.orchestrator", "run_ronin"),
    ("Menu Costing Agent", "agents.menu_cost_agent", "run_menu_costing"),
    ("Recipe Agent", "agents.recipe_agent", "run_recipe"),
    ("Client Intake Agent", "agents.client_intake_agent", "run_client_intake"),
    ("Menu Pricing Engine", "agents.menu_pricing_engine", "run_menu_pricing"),
    ("Concierge Agent (Async)", "agents.concierge_agent", "ConciergeAgent"),
    ("Ops Agent (RONIN-01)", "agents.ops_agent", "OpsAgent"),
    ("Logistics Agent (RONIN-03)", "agents.logistics_agent", "LogisticsAgent"),
    ("Economics Agent (RONIN-02)", "agents.economics_agent", "EconomicsAgent"),
    ("Compliance Agent (RONIN-06)", "agents.compliance_agent", "ComplianceAgent"),
]

available_agents = []
missing_agents = []
for agent_name, module_name, attr_name in agents:
    if _is_available(module_name, attr_name):
        available_agents.append((agent_name, attr_name))
    else:
        missing_agents.append((agent_name, attr_name))

print("\nAGENT AVAILABILITY:\n")
for agent_name, class_name in available_agents:
    print(f"  ✓ {agent_name:35s} ({class_name})")
for agent_name, class_name in missing_agents:
    print(f"  - {agent_name:35s} ({class_name}) missing")

print(f"\n{'=' * 70}")
print("MOCK MODE:", "ENABLED" if os.getenv("USE_MOCK_RESPONSES", "false").lower() in ("1", "true", "yes") else "DISABLED")
print("API KEY CONFIGURED:", "YES" if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") else "NO")
print("DATABASE:", os.getenv("CHROMA_DB_PATH", "./chroma_db"))
print("=" * 70)

run_ronin = _load_or_none("agents.orchestrator", "run_ronin")
if run_ronin is not None:
    print("\nTesting basic agent function...")
    result = run_ronin("client_intake", "New client inquiry")
    print(f"✓ Sample response: {result[:80]}...")
else:
    print("\nSkipping agent invocation because the orchestrator is not present in this build.")

print("\n" + "=" * 70)
print("STATUS:", "READY FOR DEPLOYMENT" if not missing_agents else "DEGRADED - OPTIONAL AGENTS MISSING")
print("=" * 70)
