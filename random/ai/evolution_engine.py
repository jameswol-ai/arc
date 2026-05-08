import random


def mutate_design(intent):
    """
    Slightly changes parameters to improve next generation
    """

    mutation = intent.copy()

    # evolve floors slightly
    mutation["floors"] = max(1, mutation.get("floors", 3) + random.choice([-1, 0, 1]))

    # evolve style bias
    mutation["style"] = random.choice([
        "Modern",
        "Brutalist",
        "Organic",
        "Parametric",
        "Minimal"
    ])

    return mutation

def evolve(previous_design: dict) -> dict:
    previous_design["efficiency_score"] *= 1.01
    return previous_design
