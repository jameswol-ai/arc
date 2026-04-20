from stages.concept_stage import concept_stage
from stages.compliance_stage import compliance_stage
from stages.output_stage import output_stage

from core.helpers import validate_input

# Future stages
def climate_stage(ctx): return {"climate": "analyzed"}
def material_stage(ctx): return {"materials": ["eco materials"]}
def zoning_stage(ctx): return {"zones": ["residential", "commercial"]}
def infrastructure_stage(ctx): return {"roads": "planned"}
def sustainability_stage(ctx): return {"score": "high"}

FUNCTION_REGISTRY = {
    "validate_input": validate_input,
    "concept_stage": concept_stage,
    "climate_stage": climate_stage,
    "material_stage": material_stage,
    "compliance_stage": compliance_stage,
    "output_stage": output_stage,
    "zoning_stage": zoning_stage,
    "infrastructure_stage": infrastructure_stage,
    "sustainability_stage": sustainability_stage
}
