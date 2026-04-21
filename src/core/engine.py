# src/core/engine.py

from src.core.mock_llm import MockLLM
from src.core.llm_agent import LLMAgent
from src.core.council_engine import CouncilEngine
from src.core.iteration_engine import IterationEngine


class WorkflowEngine:
    def __init__(self):
        self.llm = MockLLM()
        self.agent = LLMAgent(self.llm)

        self.council = CouncilEngine(self.agent)
        self.iteration = IterationEngine(self.council)

        self.context = {}

    def set_context(self, key, value):
        self.context[key] = value

    def run_workflow(self, workflow_name=None):
        return self.iteration.run_iterations(self.context, rounds=3)
