# src/core/ecosystem_engine.py

from src.core.evolution_manager import EvolutionManager
from src.core.system_mutator import SystemMutator
from src.core.emergent_generator import EmergentGenerator
from src.core.genetic_crossover import GeneticCrossover


class EcosystemEngine:
    def __init__(self):
        self.evolver = EvolutionManager()
        self.mutator = SystemMutator()

        self.generator = EmergentGenerator()
        self.crossover = GeneticCrossover()

    def run_cycle(self):
        # 🌱 normal evolution step
        self.evolver.evaluate()

        top = self.evolver.select_top()

        # 🔀 normal breeding
        child = self.evolver.breed(top[0], top[1])
        mutated = self.mutator.mutate(child)

        # 🌌 emergent generation (NEW)
        emergent = self.generator.generate_new_system()

        # 🧬 cross-breed old + new intelligence
        hybrid_config = self.crossover.combine(top[0], emergent)

        hybrid = type(top[0])(
            name="HYBRID-EXPLORER",
            config=hybrid_config,
            score=0.6
        )

        self.evolver.population.append(hybrid)

        return {
            "population": [v.snapshot() for v in self.evolver.population],
            "emergent_system": emergent.snapshot(),
            "hybrid_system": hybrid.snapshot()
        }
