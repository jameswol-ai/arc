# src/stages/agent_stage.py

class AgentStage:
    name = "agent"

    def run(self, context, memory):
        raise NotImplementedError

    def evaluate(self, context):
        """Return score of usefulness"""
        return 1.0

    def next(self, context):
        return None
