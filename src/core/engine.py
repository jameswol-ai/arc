# src/core/engine.py

from src.core.mock_llm import MockLLM
from src.core.llm_agent import LLMAgent
from src.core.role_factory import RoleFactory
from src.core.role_evolution import RoleEvolution
from src.core.meta_controller import MetaController
from src.core.debate_engine import DebateEngine


class WorkflowEngine:
    def __init__(self):
        self.llm = MockLLM()
        self.agent = LLMAgent(self.llm)

        self.factory = RoleFactory()
        self.evolver = RoleEvolution()
        self.meta = MetaController()

        self.debate = DebateEngine(self.agent)

        self.context = {}

    def set_context(self, key, value):
        self.context[key] = value

    def run_workflow(self, workflow_name=None):

        # 🧠 base debate run
        result = self.debate.run_debate(self.context)

        self.meta.observe(result)

        # 🧬 check if system should invent new intelligence
        if self.meta.should_create_new_role():
            new_role = self.meta.suggest_new_role()
            role_profile = self.factory.create_role(
                new_role["name"],
                new_role["traits"]
            )

            # 🧠 inject new intelligence into system
            dynamic_output = self.agent.run_dynamic(
                role_profile,
                self.context
            )

            result["emergent_role"] = dynamic_output

        return result
