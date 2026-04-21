# src/core/system_mutator.py

import random

class SystemMutator:
    def mutate(self, variant):
        mutation = random.choice([
            "increase_reasoning_depth",
            "add_new_agent_role",
            "optimize_debate_loop"
        ])

        variant.config["mutation"] = mutation
        return variant
