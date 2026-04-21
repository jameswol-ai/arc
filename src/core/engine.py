# src/core/engine.py

from src.core.function_registry import FUNCTION_REGISTRY
from src.core.workflow_loader import load_workflow
from src.core.router import choose_next_steps

class WorkflowEngine:
    def __init__(self):
        self.context = {}

    def set_context(self, key, value):
        self.context[key] = value

    def run_workflow(self, workflow_name):
        workflow = load_workflow(workflow_name)
        base_steps = workflow["basic_design"]

        result = None

        i = 0
        while i < len(base_steps):

            step = base_steps[i]
            name = step["name"]

            # execute step
            if name in FUNCTION_REGISTRY:
                func = FUNCTION_REGISTRY[name]
                self.context["last_result"] = result
                result = func(self.context)
                self.context[f"{name}_output"] = result

            # 🧠 ask router AFTER key steps
            new_steps = choose_next_steps(self.context)

            for ns in new_steps:
                if ns not in [s["name"] for s in base_steps]:
                    base_steps.insert(i + 1, {"name": ns})

            i += 1

        return result
