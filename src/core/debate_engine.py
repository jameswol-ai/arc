# src/core/debate_engine.py

class DebateEngine:
    def __init__(self, agent):
        self.agent = agent

    def run_debate(self, context):
        roles = [
            "architect",
            "structural_engineer",
            "climate_specialist",
            "compliance_officer"
        ]

        # 🧠 initial idea seed from architect
        architect_first = self.agent.debate("architect", context, [])

        conversation = [architect_first]

        # 🔁 iterative argument exchange
        for role in roles[1:]:
            response = self.agent.debate(role, context, conversation)
            conversation.append(response)

        # 🔄 second round: reactions
        refined = []
        for role in roles:
            response = self.agent.debate(role, context, conversation)
            refined.append(response)

        return {
            "initial_round": conversation,
            "refined_round": refined,
            "final_state": self._merge(refined)
        }

    def _merge(self, responses):
        # 🧠 simplified consensus merge
        return {
            "final_design": responses[0]["message"],
            "contributors": [r["speaker"] for r in responses]
        }
