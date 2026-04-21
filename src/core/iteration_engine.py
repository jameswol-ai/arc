# src/core/iteration_engine.py

class IterationEngine:
    def __init__(self, council_engine):
        self.council = council_engine

    def run_iterations(self, context, rounds=2):
        history = []

        current_context = context.copy()

        for i in range(rounds):
            result = self.council.deliberate(current_context)

            history.append(result)

            # 🔁 feed decision back into next round
            current_context["input"] = result["final_decision"]
            current_context["last_output"] = result

        return {
            "final": history[-1],
            "history": history
        }
