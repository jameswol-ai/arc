import random


def score_design(architecture, structure):
    """
    Simple multi-factor scoring system
    """

    structural_score = 1.0 if structure.get("global_safe") else 0.3

    efficiency = architecture["design_profile"]["efficiency_score"]

    complexity_penalty = 0.1 if architecture["design_profile"]["structural_risk"] == "high" else 0.0

    score = (0.6 * structural_score) + (0.4 * efficiency) - complexity_penalty

    return {
        "score": round(score, 3),
        "rating": "good" if score > 0.75 else "average" if score > 0.5 else "poor"
    }
