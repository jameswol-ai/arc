from core.engine import WorkflowEngine
from stages.concept_stage import ConceptStage
from utils.logger import log

engine = WorkflowEngine()

engine.set_context(
    "input",
    "Eco-friendly school in tropical climate"
)

result = engine.run_workflow("basic_design")

print("\n".join(result["results"]))
print("\nFINAL OUTPUT:")
print(result["final"])
