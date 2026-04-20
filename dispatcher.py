# src/core/dispatcher.py

class Dispatcher:
    def __init__(self, workflows):
        self.workflows = workflows

    def get_workflow(self, name):
        return self.workflows.get(name, [])
