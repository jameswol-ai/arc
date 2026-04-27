# src/core/engine.py

class WorkflowEngine:
    def __init__(self, workflow, function_registry):
        self.workflow = workflow
        self.function_registry = function_registry
        self.context = {}

    def set_context(self, key, value):
        self.context[key] = value

    def get_context(self, key):
        return self.context.get(key)

    def run_workflow(self, workflow_name):
        stages = self.workflow.get(workflow_name, [])

        for stage in stages:
            func_name = stage.get("name")
            func = self.function_registry.get(func_name)

            if not func:
                raise ValueError(f"Function '{func_name}' not found")

            result = func(self.context)

            if "output_key" in stage:
                self.context[stage["output_key"]] = result

        return self.context
