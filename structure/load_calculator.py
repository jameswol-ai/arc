from structure.eurocode_engine import ultimate_limit_state

def calculate_load(area, floors):
    dead = area * 3.5 * floors
    live = area * 2.0

    uls = ultimate_limit_state(dead, live)

    return {
        "dead_load": dead,
        "live_load": live,
        "uls_load": uls
    }

def calculate_load(area: float, floors: int):
    return {
        "dead_load": area * 3.5,
        "live_load": area * 2.0,
        "total_load": area * floors * 5.5
    }
