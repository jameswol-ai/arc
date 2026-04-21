# src/core/llm_agent.py

class LLMAgent:
    def __init__(self, llm_client, metrics):
        self.llm = llm_client
        self.metrics = metrics

    def debate(self, role, context, conversation):
        weight = self.metrics.get_weight(role)

        response = self.llm.generate(role, {
            **context,
            "conversation": conversation,
            "weight": weight
        })

        return {
            "speaker": role,
            "message": response.get("output"),
            "score": response.get("confidence", 0.5) * weight
        }
