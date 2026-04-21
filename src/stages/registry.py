# src/stages/registry.py

from src.stages.concept_stage import concept_stage
from src.stages.compliance_stage import compliance_stage
from src.stages.analysis_stage import analysis_stage
from src.stages.output_stage import output_stage

STAGE_REGISTRY = {
    "concept": concept_stage,
    "compliance": compliance_stage,
    "analysis": analysis_stage,
    "output": output_stage,
}


def get_stage(name: str):
    if name not in STAGE_REGISTRY:
        raise ValueError(f"Stage '{name}' not found in registry")
    return STAGE_REGISTRY[name]
