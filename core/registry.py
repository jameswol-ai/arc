# core/registry.py

PIPELINE_REGISTRY = {}

def register_pipeline(name):

    def decorator(func):

        if name in PIPELINE_REGISTRY:
            raise ValueError(
                f"Duplicate pipeline registration: {name}"
            )

        PIPELINE_REGISTRY[name] = func
        return func

    return decorator


def get_pipeline(name):

    if name not in PIPELINE_REGISTRY:

        available = list(PIPELINE_REGISTRY.keys())

        raise ValueError(
            f"Pipeline '{name}' not registered.\n"
            f"Available pipelines: {available}"
        )

    return PIPELINE_REGISTRY[name]


def run_pipeline(name, *args, **kwargs):
    pipeline = get_pipeline(name)
    return pipeline(*args, **kwargs)
