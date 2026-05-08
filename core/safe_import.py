from core.registry import registry


def get_pipeline():
    return registry.get("pipeline")


def get_module(name):
    return registry.get(name)
