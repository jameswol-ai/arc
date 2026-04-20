from src.core.context import Context
from src.core.engine import WorkflowEngine
from src.core.dispatcher import Dispatcher

from src.stages.concept_stage import concept_stage
from src.stages.compliance_stage import compliance_stage
from src.stages.analysis_stage import analysis_stage
from src.stages.output_stage import output_stage


def main():
    context = Context()
    context.set("input", "eco-friendly school in tropical climate")

    engine = WorkflowEngine(context)

    workflow = [
        concept_stage,
        compliance_stage,
        analysis_stage,
        output_stage
    ]

    result = engine.run(workflow)

    print("\n🏗️ FINAL RESULT:\n")
    print(result)


if __name__ == "__main__":
    main()


from core.doc_loader import DocLoader

doc_loader = DocLoader()

engine.set_context("building_codes", doc_loader.load_category("building_codes"))
engine.set_context("system_design", doc_loader.load_doc("system_design.md"))
engine.set_context("architecture_notes", doc_loader.load_doc("architecture_notes.md"))
