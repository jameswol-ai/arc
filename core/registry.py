# =========================================================
# 🧠 RANDOM AUTO REGISTRY SYSTEM
# Prevents import breakage by centralizing module access
# =========================================================

class Registry:
    def __init__(self):
        self._modules = {}

    def register(self, name, module):
        self._modules[name] = module

    def get(self, name):
        if name not in self._modules:
            raise Exception(f"[REGISTRY ERROR] Module '{name}' not found")
        return self._modules[name]

    def list_modules(self):
        return list(self._modules.keys())


# GLOBAL REGISTRY INSTANCE
registry = Registry()
