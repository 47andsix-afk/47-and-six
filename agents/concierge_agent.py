import asyncio
import json

try:
    from chef_knowledge.indexer import query_chef_knowledge
except Exception:
    query_chef_knowledge = None

try:
    from core.config import is_mock_enabled
except Exception:
    def is_mock_enabled():
        return False

class ConciergeAgent:
    def __init__(self, generate_func):
        self.generate = generate_func

    async def synthesize(
        self,
        inquiry: str,
        ops: dict,
        econ: dict,
        logistics: dict,
        compliance: dict,
        local_context: str,
    ) -> str:
        ops_json = json.dumps(ops, indent=2)
        econ_json = json.dumps(econ, indent=2)
        logistics_json = json.dumps(logistics, indent=2)
        compliance_json = json.dumps(compliance, indent=2)

        # mock mode short-circuits to avoid external API use
        if is_mock_enabled():
            return "[MOCK] Concierge synthesis: mock response for development."

        # attempt to enrich prompt with indexed chef knowledge
        knowledge_text = ""
        if query_chef_knowledge is not None:
            try:
                results = query_chef_knowledge(inquiry, n_results=3)
                documents = results.get("documents", [])
                if documents and documents[0]:
                    # join top returned documents into a short snippet
                    snippets = [d for d in documents[0] if d]
                    knowledge_text = "\n" + "\n".join(snippets)
            except Exception:
                knowledge_text = ""

        prompt = f"""
RONIN-CONCIERGE // Client-facing synthesis

You are the concierge layer. Combine the component analyses into a clear, client-facing response that includes an executive summary, estimated costs, timeline, staffing, and any compliance notes.

User Inquiry: {inquiry}
Local Operational Rule: {local_context}

---- CHEF KNOWLEDGE ----
{knowledge_text}

---- OPS ANALYSIS ----
{ops_json}

---- ECONOMICS ----
{econ_json}

---- LOGISTICS ----
{logistics_json}

---- COMPLIANCE ----
{compliance_json}

Return a concise JSON-like summary and a short professional message for the client.
"""
        try:
            return await asyncio.wait_for(self.generate(prompt), timeout=6.0)
        except asyncio.TimeoutError:
            return "RONIN concierge synthesis timeout — final response unavailable."
