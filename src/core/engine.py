class WorkflowEngine:
    def __init__(self, workflows):
        self.workflows = workflows
        self.context = {}

    def set_context(self, key, value):
        self.context[key] = value

    def get_context(self):
        return self.context

    def run_workflow(self, workflow_name):
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        steps = self.workflows[workflow_name]

        for step in steps:
            name = step["name"]
            func = step["function"]

            print(f"⚙️ Running stage: {name}")

            result = func(self.context)

            # Store result in context
            self.context[name] = result

        return self.context
