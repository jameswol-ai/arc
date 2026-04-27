# src/core/engine.py

class WorkflowEngine:
    def __init__(self):
        self.stages = [
            self.analyze,
            self.plan,
            self.generate
        ]

    def run_workflow(self, context):
        for stage in self.stages:
            context = stage(context)
        return context

    def analyze(self, context):
        context["analysis"] = f"Analyzed: {context['input']}"
        return context

    def plan(self, context):
        context["plan"] = "Basic plan created"
        return context

    def generate(self, context):
        context["output"] = "Architecture generated"
        return context
