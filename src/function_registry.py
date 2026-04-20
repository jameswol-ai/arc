# src/core/function_registry.py

from src.stages.concept_stage import concept_stage
from src.stages.compliance_stage import compliance_stage
from src.stages.output_stage import output_stage

FUNCTION_REGISTRY = {
    "concept_stage": concept_stage,
    "compliance_stage": compliance_stage,
    "output_stage": output_stage,
}
