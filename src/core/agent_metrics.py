# src/core/agent_metrics.py

class AgentMetrics:
    def __init__(self):
        self.scores = {
            "architect": 1.0,
            "structural_engineer": 1.0,
            "climate_specialist": 1.0,
            "compliance_officer": 1.0
        }

    def update(self, agent, feedback_score):
        current = self.scores.get(agent, 1.0)
        self.scores[agent] = (current + feedback_score) / 2

    def get_weight(self, agent):
        return self.scores.get(agent, 1.0)
