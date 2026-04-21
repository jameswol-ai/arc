# src/core/llm_agent.py

class LLMAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def debate(self, role, context, incoming_arguments):
        response = self.llm.generate(role, {
            **context,
            "debate": incoming_arguments
        })

        return {
            "speaker": role,
            "message": response.get("output"),
            "supports": response.get("supports", []),
            "challenges": response.get("challenges", [])
        }
