def validate_structure(load: float, capacity: float):
    return {
        "safe": capacity > load,
        "utilization": load / capacity if capacity else 0
    }
