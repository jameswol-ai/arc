# core/registry.py

PIPELINE_REGISTRY = {}

def register_pipeline(name: str):
    def decorator(func):
        PIPELINE_REGISTRY[name] = func
        return func
    return decorator


def get_pipeline(name: str):
    if name not in PIPELINE_REGISTRY:
        raise ValueError(f"Pipeline '{name}' not registered.")
    return PIPELINE_REGISTRY[name]


def run_pipeline(name: str, *args, **kwargs):
    return get_pipeline(name)(*args, **kwargs)

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
