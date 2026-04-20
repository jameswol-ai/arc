from core.dispatcher import Dispatcher
from core.context import Context

class WorkflowEngine:
    def __init__(self, workflow):
        self.workflow = workflow
        self.context = Context()
        self.dispatcher = Dispatcher(workflow["stages"])

    def set_context(self, key, value):
        self.context.set(key, value)

    def run_workflow(self, workflow_name):
        steps = self.workflow[workflow_name]

        for step in steps:
            stage_name = step["name"]

            result = self.dispatcher.dispatch(
                stage_name,
                self.context
            )

            # store output of each stage like layers of a blueprint
            self.context.set(stage_name, result)

        return self.context.dump()
