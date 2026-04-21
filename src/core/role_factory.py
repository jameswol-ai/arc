# src/core/role_factory.py

class RoleFactory:
    def __init__(self):
        self.generated_roles = {}

    def create_role(self, name, base_traits):
        """
        Dynamically generates a new agent role.
        """

        role_profile = {
            "name": name,
            "traits": base_traits,
            "behavior_modifier": self._derive_behavior(base_traits)
        }

        self.generated_roles[name] = role_profile
        return role_profile

    def _derive_behavior(self, traits):
        # 🧠 simplistic synthesis logic
        if "structural" in traits and "climate" in traits:
            return "environmental_structural_hybrid"

        if "design" in traits and "analysis" in traits:
            return "conceptual_optimizer"

        return "general_reasoner"
