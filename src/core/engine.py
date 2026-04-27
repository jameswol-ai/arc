# src/core/engine.py

from core.context import Context
from core.dispatcher import Dispatcher

class WorkflowEngine:
    def __init__(self, workflow_config):
        self.dispatcher = Dispatcher(workflow_config)

    def run_workflow(self, input_data):
        context = Context(input_data)

        for stage in self.dispatcher.get_stages():
            context = stage.run(context)

        return context.data
