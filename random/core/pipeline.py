from ai.intent_router import interpret_intent
from ai.design_brain import generate_design_profile

from architecture.grid_system import generate_grid
from architecture.room_generator import generate_rooms
from architecture.floor_stack import stack_floors

from structure.load_calculator import calculate_load
from structure.column_stack import generate_columns
from structure.eurocode_engine import structural_assessment


# =========================================================
# 🧠 FULL RANDOM BUILDING PIPELINE
# SITE → AI → ARCH → STRUCTURE → CHECK
# =========================================================

def run_pipeline(user_input: str, site_area: float):
    
    # 1. AI INTERPRETATION
    intent = interpret_intent(user_input)
    profile = generate_design_profile(intent)

    floors = intent.get("floors", 3)

    # 2. ARCHITECTURE GENERATION
    grid = generate_grid(floors)
    floors_stack = stack_floors(floors)
    rooms = generate_rooms(intent.get("building_type", "Residential"))

    architecture = {
        "grid": grid,
        "floors": floors_stack,
        "rooms": rooms,
        "design_profile": profile
    }

    # 3. STRUCTURAL LOGIC
    load = calculate_load(site_area, floors)
    columns = generate_columns(grid["axes"], floors)

    # take simplified assumptions for spans & height
    span = grid["spacing"] * 1.5
    height = 3.2 * floors

    structure = structural_assessment(
        span=span,
        dead=load["dead_load"],
        live=load["live_load"],
        height=height
    )

    return {
        "intent": intent,
        "architecture": architecture,
        "structure": structure,
        "status": "generated"
    }
