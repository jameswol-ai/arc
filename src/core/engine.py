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

# =========================================================
# 🧭 INTENT ENGINE (PREFERENCE FORMATION LAYER)
# =========================================================

class IntentEngine:
    def __init__(self, memory):
        self.memory = memory

    def derive_intent(self):
        scores = self.memory.get("node_scores", {})
        traffic = self.memory.get("traffic", {})

        if not scores:
            return {"intent": "explore", "confidence": 0.1}

        # 🧠 dominant behavior direction
        dominant_node = max(scores.items(), key=lambda x: x[1])[0]

        # 🚦 most reinforced transition
        strongest_route = None
        max_count = 0

        for a, paths in traffic.items():
            for b, count in paths.items():
                if count > max_count:
                    max_count = count
                    strongest_route = (a, b)

        # 🌱 system tendency inference
        avg = sum(scores.values()) / len(scores)

        if avg > 1.6:
            intent = "expand"
            confidence = 0.85
        elif avg > 1.2:
            intent = "stabilize"
            confidence = 0.7
        elif avg > 0.9:
            intent = "explore"
            confidence = 0.6
        else:
            intent = "repair"
            confidence = 0.8

        return {
            "intent": intent,
            "confidence": confidence,
            "dominant_node": dominant_node,
            "preferred_route": strongest_route
        }

    def bias_next_step(self, current, roads):
        """
        Slightly biases routing toward preferred behavior.
        """
        intent = self.derive_intent()

        if intent["intent"] == "expand":
            # prefer switching paths randomly (growth behavior)
            return None

        if intent["intent"] == "stabilize":
            # reinforce existing route
            return roads.get(current)

        if intent["intent"] == "repair":
            # avoid weak nodes
            weak = min(self.memory["node_scores"], key=self.memory["node_scores"].get)
            return weak if weak in roads else roads.get(current)

        return roads.get(current)
