# src/core/engine.py

from src.core.mock_llm import MockLLM
from src.core.llm_agent import LLMAgent
from src.core.debate_engine import DebateEngine
from src.core.architecture_memory import ArchitectureMemory
from src.core.system_architect import SystemArchitect
from src.core.mutation_gate import MutationGate
from src.core.architecture_evolver import ArchitectureEvolver


class WorkflowEngine:
    def __init__(self):
        self.llm = MockLLM()
        self.agent = LLMAgent(self.llm)

        self.debate = DebateEngine(self.agent)

        self.memory = ArchitectureMemory()
        self.architect = SystemArchitect()
        self.gate = MutationGate()
        self.evolver = ArchitectureEvolver(self.memory, self.gate)

        self.context = {}

    def set_context(self, key, value):
        self.context[key] = value

    def run_workflow(self, workflow_name=None):

        # 🧠 run system normally
        result = self.debate.run_debate(self.context)

        # 📦 record system state
        self.memory.record(result)

        # 🧠 analyze system behavior
        analysis = self.memory.analyze_trends()

        # 🏗️ propose system evolution
        proposal = self.architect.propose_changes(
            analysis,
            self._extract_score(result)
        )

        # 🔁 attempt self-modification
        evolution = self.evolver.evolve(proposal)

        return {
            "result": result,
            "architecture_analysis": analysis,
            "evolution_proposal": proposal,
            "evolution_result": evolution
        }

    def _extract_score(self, result):
        try:
            return result["conversation"][0].get("score", 0.5)
        except:
            return 0.5
