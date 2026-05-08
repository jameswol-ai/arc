def evolve(previous_design: dict) -> dict:
    previous_design["efficiency_score"] *= 1.01
    return previous_design
