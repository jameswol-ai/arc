def concept_stage(ctx):
    idea = ctx.get("input", "")

    return {
        "concept": f"Sustainable design derived from: {idea}",
        "materials": ["bamboo", "recycled steel"],
        "climate_strategy": "natural ventilation"
    }
