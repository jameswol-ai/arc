# src/core/role_evolution.py

class RoleEvolution:
    def evolve(self, role_a, role_b):
        """
        Combines two roles into a new hybrid intelligence.
        """

        new_name = f"{role_a['name']}_{role_b['name']}_hybrid"

        new_traits = list(set(role_a["traits"] + role_b["traits"]))

        return {
            "name": new_name,
            "traits": new_traits
        }
