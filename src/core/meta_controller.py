# src/core/meta_controller.py

class MetaController:
    def __init__(self):
        self.history = []

    def observe(self, result):
        self.history.append(result)

    def should_create_new_role(self):
        recent = self.history[-3:]

        avg = sum(
            r["result"]["conversation"][0]["score"]
            for r in recent if r.get("result")
        ) / max(len(recent), 1)

        return avg > 0.85  # high performance = allow complexity growth

    def suggest_new_role(self):
        return {
            "name": "adaptive_architect",
            "traits": ["design", "analysis", "climate"]
        }
