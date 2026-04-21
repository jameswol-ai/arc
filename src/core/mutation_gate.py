# src/core/mutation_gate.py

class MutationGate:
    def approve(self, proposal):
        dangerous_actions = ["delete_core", "unbounded_generation"]

        if proposal["action"] in dangerous_actions:
            return False

        return True
