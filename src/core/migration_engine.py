# src/core/migration_engine.py

import random

class MigrationEngine:
    def migrate(self, universe_a, universe_b):
        # 🧠 extract last ideas from both universes
        idea_a = universe_a.history[-1] if universe_a.history else {}
        idea_b = universe_b.history[-1] if universe_b.history else {}

        # 🔀 blend conceptual outputs
        return {
            "merged_idea": f"{idea_a} ⊕ {idea_b}",
            "origin": [universe_a.name, universe_b.name]
        }
