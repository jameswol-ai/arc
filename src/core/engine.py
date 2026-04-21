# src/core/engine.py

class WorkflowEngine:
    def __init__(self, workflows, context=None):
        self.workflows = workflows
        self.context = context or {}

    def set_context(self, key, value):
        self.context[key] = value

    def run_workflow(self, workflow_name):
        workflow = self.workflows.get(workflow_name)

        if not workflow:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        for stage in workflow:
            stage_fn = stage["function"]

            # run stage with shared context
            result = stage_fn(self.context)

            # optionally store result back into context
            self.context[stage["name"]] = result

        return self.context
