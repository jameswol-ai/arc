# src/core/meta_controller.py

class MetaController:
    def __init__(self):
        self.performance_log = []

    def observe(self, run_result):
        self.performance_log.append(run_result)

    def evaluate(self):
        """
        Decide if system structure should change
        """
        recent = self.performance_log[-5:]

        avg_score = sum(
            sum(a.get("score", 0.5) for a in r["conversation"])
            for r in recent
        ) / max(len(recent), 1)

        return avg_score

    def suggest_changes(self, avg_score):
        if avg_score < 0.6:
            return {
                "action": "simplify_pipeline",
                "reason": "low reasoning stability"
            }

        if avg_score > 0.85:
            return {
                "action": "add_complexity",
                "reason": "system can handle richer reasoning"
            }

        return {
            "action": "maintain",
            "reason": "stable system"
        }
