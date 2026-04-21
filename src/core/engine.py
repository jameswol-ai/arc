# src/core/engine.py

from src.core.function_registry import FUNCTION_REGISTRY
from src.core.workflow_loader import load_workflow

class WorkflowEngine:
    def __init__(self):
        self.context = {}

    def set_context(self, key, value):
        self.context[key] = value

    def _evaluate_condition(self, condition):
        """
        Very simple condition evaluator (v1 brain 🧠)
        Example: "climate == tropical"
        """
        if not condition:
            return True

        expr = condition.get("if", "")

        try:
            # Safe-ish evaluation using context only
            key, _, value = expr.partition("==")
            key = key.strip()
            value = value.strip()

            return str(self.context.get(key)) == value
        except Exception:
            return False

    def run_workflow(self, workflow_name):
        workflow = load_workflow(workflow_name)

        steps = workflow["basic_design"]
        result = None

        for step in steps:
            condition = step.get("condition")

            if not self._evaluate_condition(condition):
                continue  # skip this stage 🌿

            name = step["name"]

            if name not in FUNCTION_REGISTRY:
                raise ValueError(f"Step '{name}' not found")

            func = FUNCTION_REGISTRY[name]

            self.context["last_result"] = result
            result = func(self.context)

            self.context[f"{name}_output"] = result

        return result
