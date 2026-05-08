def calculate_load(area: float, floors: int):
    return {
        "dead_load": area * 3.5,
        "live_load": area * 2.0,
        "total_load": area * floors * 5.5
    }
