# src/core/mutation_engine.py

import random

class MutationEngine:
    def mutate(self, idea, critique):
        mutations = [
            "increase ventilation strategy",
            "optimize spatial layout",
            "improve structural efficiency",
            "reduce material cost impact"
        ]

        return idea + " + " + random.choice(mutations)
