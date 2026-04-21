# src/core/debate_engine.py

class DebateEngine:
    def __init__(self, agent):
        self.agent = agent

    def run_debate(self, context):
        concept = self.agent.run("concept", context)
        critic = self.agent.run("critic", {
            **context,
            "last_output": concept
        })

        return {
            "concept": concept,
            "critique": critic,
            "final": self._resolve(concept, critic)
        }

    def _resolve(self, concept, critic):
        return {
            "output": f"Refined Design:\n{concept['output']}",
            "review": critic.get("output"),
            "confidence": 0.85
        }
