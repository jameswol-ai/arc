import random

def generate_design_profile(intent: dict) -> dict:
    return {
        "efficiency_score": round(random.uniform(0.6, 0.95), 2),
        "spatial_logic": random.choice(["linear", "radial", "grid", "organic"]),
        "structural_risk": random.choice(["low", "medium", "high"])
    }
