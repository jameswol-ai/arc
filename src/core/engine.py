#ssr/core/engine.py

from src.core.function_registry import FUNCTION_REGISTRY
from src.core.workflow_loader import load_workflow
from src.core.memory import memory  # if you're using learning system

class WorkflowEngine:
    def __init__(self):
        self.context = {}

    def set_context(self, key, value):
        self.context[key] = value

    def run_workflow(self, workflow_name):
        workflow = load_workflow(workflow_name)
        steps = workflow["basic_design"]

        result = None

        for step in steps:
            name = step["name"]

            if name not in FUNCTION_REGISTRY:
                raise ValueError(f"Step '{name}' not found in registry")

            func = FUNCTION_REGISTRY[name]

            self.context["last_result"] = result
            result = func(self.context)
            self.context[f"{name}_output"] = result

            # 🧠 optional learning hook (only if memory exists)
            try:
                memory.record(name, True)
            except Exception:
                pass

        return result
