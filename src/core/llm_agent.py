# src/core/llm_agent.py

class LLMAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def run_dynamic(self, role_profile, context):
        role_name = role_profile["name"]
        traits = role_profile["traits"]

        response = self.llm.generate(role_name, {
            **context,
            "traits": traits
        })

        return {
            "role": role_name,
            "output": response.get("output"),
            "traits": traits,
            "confidence": response.get("confidence", 0.5)
        }
