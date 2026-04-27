# src/core/engine.py

from core.context import Context
import core.stages as stages

class WorkflowEngine:
    def __init__(self):
        self.context = Context()

        self.workflow = [
            ("concept_stage", stages.concept_stage),
            ("climate_check", stages.climate_check),
            ("eco_design", stages.eco_design),
        ]

    def run(self):
        machine_log = []
        narrative = []
        summary_points = []

        narrative.append("🧠 Random initializes dual-layer execution.\n")

        for name, stage_fn in self.workflow:
            try:
                result = stage_fn(self.context)

                if not isinstance(result, dict):
                    result = {"output": result}

                for k, v in result.items():
                    self.context.set(k, v)

                summary_points.append(name)

                # ⚙️ MACHINE LAYER ENTRY
                machine_log.append({
                    "stage": name,
                    "status": "ok",
                    "data": result
                })

                # 📖 NARRATIVE LAYER ENTRY
                narrative.append(self._narrate(name, result))

            except Exception as e:
                machine_log.append({
                    "stage": name,
                    "status": "failed",
                    "error": str(e)
                })

                narrative.append(f"⚠️ {name} encountered instability during execution.")

        reflection = self._reflect(summary_points)

        return {
            "machine_layer": {
                "context": self.context.data,
                "log": machine_log
            },
            "narrative_layer": {
                "story": narrative,
                "reflection": reflection
            }
        }

    # 📖 HUMAN LAYER
    def _narrate(self, stage, result):
        if stage == "concept_stage":
            return "📐 Concept layer formed: structural blueprint emerging from abstraction."

        if stage == "climate_check":
            return "🌍 Environmental scan complete: system aligned with climate constraints."

        if stage == "eco_design":
            return "🌱 Sustainability layer integrated into architectural logic."

        return f"⚙️ {stage} processed successfully."

    # 🧠 SYSTEM REFLECTION
    def _reflect(self, points):
        if len(points) == len(self.workflow):
            return "System stable. Dual-layer coherence maintained."

        return "Partial divergence detected between stages. System remains functional but uneven."
