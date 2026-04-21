# src/core/emergent_generator.py

from src.core.idea_explorer import IdeaExplorer
from src.core.system_variant import SystemVariant


class EmergentGenerator:
    def __init__(self):
        self.explorer = IdeaExplorer()

    def generate_new_system(self):
        idea = self.explorer.explore()

        # 🧬 translate abstract idea into system config
        config = {
            "architecture_type": idea,
            "reasoning_depth": 1 + len(idea) % 3,
            "agent_structure": "dynamic"
        }

        return SystemVariant(
            name=f"EMERGENT-{hash(idea) % 10000}",
            config=config,
            score=0.5
        )
