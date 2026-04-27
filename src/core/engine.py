# src/core/engine.py

from src.core.registry import StageRegistry

class WorkflowEngine:
    def __init__(self, memory=None):
        self.registry = StageRegistry()
        self.memory = memory

    def run(self, workflow_name, context):
        workflow = self.registry.get_workflow(workflow_name)

        current_stage = workflow["start"]

        trace = []

        while current_stage:
            stage = self.registry.get_stage(current_stage)

            context = stage.run(context, self.memory)

            trace.append({
                "stage": current_stage,
                "output": context.data
            })

            current_stage = stage.next(context)

        return context, trace
