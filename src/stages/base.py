# src/stages/base.py

class BaseStage:
    name = "base"

    def run(self, context, memory):
        raise NotImplementedError

    def next(self, context):
        return None
