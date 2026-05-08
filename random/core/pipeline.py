from ai.intent_router import interpret_intent
from ai.design_brain import generate_design_profile
from ai.memory_bank import store_design
from ai.scoring_engine import score_design
from ai.evolution_engine import mutate_design

from architecture.grid_system import generate_grid
from architecture.room_generator import generate_rooms
from architecture.floor_stack import stack_floors

from structure.load_calculator import calculate_load
from structure.eurocode_engine import structural_assessment

from core.registry import registry

def run_pipeline(intent_text, site_area):

    result = {
        "current_design": {
            "architecture": {},
            "structure": {},
            "score": {},
            "intent": intent_text
        },
        "next_generation_seed": {},
        "bim": None,
        "parametric_engine": None
    }

    return result


# =========================================================
# AUTO REGISTER ON IMPORT
# =========================================================
registry.register("pipeline", run_pipeline)
