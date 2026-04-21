# src/core/engine.py

from src.core.workflow_loader import WorkflowLoader


class WorkflowEngine:
    def __init__(self):
        self.loader = WorkflowLoader()
        self.context = {}

    def set_context(self, key, value):
        self.context[key] = value

    def run_workflow(self, workflow_name: str):
        workflow = self.loader.load(workflow_name)
        pipeline = workflow["pipeline"]

        results = []

        for stage in pipeline:
            output = stage(self.context)
            self.context["last_output"] = output
            results.append(output)

        return {
            "workflow": workflow["name"],
            "results": results,
            "final": results[-1] if results else None
        }
