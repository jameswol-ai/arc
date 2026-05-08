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


def run_pipeline(user_input: str, site_area: float):

    # 1. INTENT
    intent = interpret_intent(user_input)
    profile = generate_design_profile(intent)
    intent["design_profile"] = profile

    # 2. ARCHITECTURE
    floors = intent.get("floors", 3)

    grid = generate_grid(floors)
    rooms = generate_rooms(intent.get("building_type", "Residential"))
    floor_stack = stack_floors(floors)

    architecture = {
        "grid": grid,
        "rooms": rooms,
        "floors": floor_stack,
        "design_profile": profile
    }

    # 3. STRUCTURE
    load = calculate_load(site_area, floors)

    span = grid["spacing"] * 1.5
    height = 3.2 * floors

    structure = structural_assessment(
        span=span,
        dead=load["dead_load"],
        live=load["live_load"],
        height=height
    )

    # 4. SCORING
    score = score_design(architecture, structure)

    # 5. STORE DESIGN MEMORY
    design_package = {
        "intent": intent,
        "architecture": architecture,
        "structure": structure,
        "score": score
    }

    stored = store_design(design_package)

    # 6. EVOLUTION STEP (NEXT GENERATION IDEA)
    next_intent = mutate_design(intent)

    return {
        "current_design": design_package,
        "stored_id": stored["id"],
        "next_generation_seed": next_intent
                 }

from core.bim_builder import build_bim_model
from core.bim_relations import connect_rooms_to_structure


def run_pipeline(user_input, site_area):

    ...
    # existing architecture + structure logic

    bim_model = build_bim_model(architecture, structure)
    connect_rooms_to_structure(bim_model)

    return {
        "architecture": architecture,
        "structure": structure,
        "bim": bim_model
    }
