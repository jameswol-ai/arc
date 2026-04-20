# src/core/engine.py

from src.core.function_registry import FUNCTION_REGISTRY

class WorkflowEngine:
    def __init__(self, workflow_definition):
        self.workflow = workflow_definition
        self.context = {}

    def set_context(self, key, value):
        self.context[key] = value

    def get_context(self):
        return self.context

    def run_workflow(self, workflow_name):
        if workflow_name not in self.workflow:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        steps = self.workflow[workflow_name]
        result = None

        for step in steps:
            step_name = step["name"]

            if step_name not in FUNCTION_REGISTRY:
                raise ValueError(f"Step '{step_name}' not registered")

            func = FUNCTION_REGISTRY[step_name]

            # pass context forward like a baton in a relay race 🏃‍♂️
            self.context["last_result"] = result
            result = func(self.context)

            self.context[f"{step_name}_output"] = result

        return result
