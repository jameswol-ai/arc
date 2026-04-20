# src/stages/concept_stage.py

def concept_stage(ctx):
    user_input = ctx.get("input")

    concept = f"""
    Architectural Concept Generated:
    - Core Idea: Sustainable design inspired by {user_input}
    - Focus: Climate responsiveness, spatial efficiency, human comfort
    - Style Direction: Modern eco-architecture with passive cooling systems
    """

    ctx.set("concept", concept)
    return concept
