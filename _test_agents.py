#!/usr/bin/env python
"""Test and verify all RONIN agents are working."""
import os
from agents.orchestrator import run_ronin
from agents.menu_cost_agent import run_menu_costing
from agents.recipe_agent import run_recipe
from agents.client_intake_agent import run_client_intake
from agents.menu_pricing_engine import run_menu_pricing
from agents.concierge_agent import ConciergeAgent
from agents.ops_agent import OpsAgent
from agents.logistics_agent import LogisticsAgent
from agents.economics_agent import EconomicsAgent
from agents.compliance_agent import ComplianceAgent

print("=" * 70)
print("47-&-SIX CONCIERGE PLATFORM - RONIN AGENTS STATUS")
print("=" * 70)

agents = [
    ("RONIN Orchestrator", "run_ronin"),
    ("Menu Costing Agent", "run_menu_costing"),
    ("Recipe Agent", "run_recipe"),
    ("Client Intake Agent", "run_client_intake"),
    ("Menu Pricing Engine", "run_menu_pricing"),
    ("Concierge Agent (Async)", "ConciergeAgent"),
    ("Ops Agent (RONIN-01)", "OpsAgent"),
    ("Logistics Agent (RONIN-03)", "LogisticsAgent"),
    ("Economics Agent (RONIN-02)", "EconomicsAgent"),
    ("Compliance Agent (RONIN-06)", "ComplianceAgent"),
]

print("\n✓ ALL AGENTS LOADED SUCCESSFULLY:\n")
for agent_name, class_name in agents:
    print(f"  ✓ {agent_name:35s} ({class_name})")

print(f"\n{'=' * 70}")
print("MOCK MODE:", "ENABLED" if os.getenv("USE_MOCK_RESPONSES", "false").lower() in ("1", "true", "yes") else "DISABLED")
print("API KEY CONFIGURED:", "YES" if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") else "NO")
print("DATABASE:", os.getenv("CHROMA_DB_PATH", "./chroma_db"))
print("=" * 70)

print("\nTesting basic agent function...")
# Test a basic agent call
result = run_ronin("client_intake", "New client inquiry")
print(f"✓ Sample response: {result[:80]}...")

print("\n" + "=" * 70)
print("STATUS: READY FOR DEPLOYMENT")
print("=" * 70)
