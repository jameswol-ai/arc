# src/core/system_architect.py

class SystemArchitect:
    def propose_changes(self, memory_analysis, performance_metrics):
        """
        Generates system-level evolution proposals.
        """

        if memory_analysis["growth"] == "increasing" and performance_metrics > 0.85:
            return {
                "action": "modular_split",
                "proposal": "Separate debate engine into micro-agents"
            }

        if performance_metrics < 0.6:
            return {
                "action": "simplify_core",
                "proposal": "Reduce agent complexity, merge roles"
            }

        return {
            "action": "stabilize",
            "proposal": "No structural changes required"
        }
