# src/core/engine.py

from src.core.workflow_loader import WorkflowLoader
from src.knowledge.doc_loader import DocLoader
from src.knowledge.retriever import Retriever


class WorkflowEngine:
    def __init__(self):
        self.loader = WorkflowLoader()

        self.doc_loader = DocLoader()
        self.retriever = Retriever(self.doc_loader)

        self.context = {}

    def set_context(self, key, value):
        self.context[key] = value

    def run_workflow(self, workflow_name: str):

        # 🧠 inject knowledge into context
        input_text = self.context.get("input", "")
        knowledge = self.retriever.search(input_text)

        self.context["knowledge"] = knowledge

        workflow = self.loader.load(workflow_name)
        pipeline = workflow["pipeline"]

        results = []

        for stage in pipeline:
            output = stage(self.context)
            self.context["last_output"] = output
            results.append(output)

        return {
            "workflow": workflow["name"],
            "results": results,
            "final": results[-1] if results else None,
            "knowledge_used": knowledge
        }
