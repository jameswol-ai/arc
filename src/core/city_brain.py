# src/core/city_brain.py

from core.city_intent import analyze_city_intent
from core.city_planner import generate_city_plan
from core.city_simulator import simulate_city

class CityBrain:
    def run(self, ctx):
        # 1. understand request
        intent = analyze_city_intent(ctx)
        ctx["intent"] = intent

        # 2. design systems
        systems = generate_city_plan(intent)

        # 3. simulate city behavior
        simulation = simulate_city(systems, intent)

        # 4. final synthesis
        return {
            "intent": intent,
            "systems": systems,
            "simulation": simulation,
            "summary": self.summarize(systems, simulation)
        }

    def summarize(self, systems, simulation):
        return f"""
CITY GENERATED

Systems:
- {', '.join(systems)}

Density: {simulation['urban_core']['density']}
Transport: {simulation['urban_core']['transport_flow']}
Sustainability Score: {simulation['sustainability_score']}
"""
