import asyncio
from typing import Callable

from agents.ops_agent import OpsAgent
from agents.economics_agent import EconomicsAgent
from agents.logistics_agent import LogisticsAgent
from agents.compliance_agent import ComplianceAgent
from agents.concierge_agent import ConciergeAgent
from agents.memory_agent import MemoryAgent


class RoninOrchestrator:
    def __init__(self, generate_func: Callable[[str], str], retrieve_context_func: Callable[[str], str]):
        self.generate = generate_func
        self.retrieve = retrieve_context_func

        # initialize agents with the appropriate callables
        self.memory = MemoryAgent(self.retrieve)
        self.ops = OpsAgent(self.generate)
        self.econ = EconomicsAgent(self.generate)
        self.logistics = LogisticsAgent(self.generate)
        self.compliance = ComplianceAgent(self.generate)
        self.concierge = ConciergeAgent(self.generate)

    async def route(self, inquiry: str) -> dict:
        # 1) get local context / memory
        local_context = await self.memory.retrieve(inquiry)

        # 2) fan-out to agents in parallel with failure tolerance
        tasks = [
            asyncio.create_task(self.ops.run(inquiry, local_context)),
            asyncio.create_task(self.econ.run(inquiry, local_context)),
            asyncio.create_task(self.logistics.run(inquiry, local_context)),
            asyncio.create_task(self.compliance.run(inquiry, local_context)),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        parsed_results = []
        for result in results:
            if isinstance(result, Exception):
                parsed_results.append({"parse_error": str(result)})
            else:
                parsed_results.append(result)

        ops_out, econ_out, logistics_out, compliance_out = parsed_results

        # 3) final concierge synthesis
        final_out = await self.concierge.synthesize(
            inquiry=inquiry,
            ops=ops_out,
            econ=econ_out,
            logistics=logistics_out,
            compliance=compliance_out,
            local_context=local_context,
        )

        return {
            "final": final_out,
            "components": {
                "ops": ops_out,
                "economics": econ_out,
                "logistics": logistics_out,
                "compliance": compliance_out,
                "local_context": local_context,
            },
        }
