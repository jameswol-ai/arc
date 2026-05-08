import random

def generate_rooms(floor_type="Residential"):
    base_rooms = ["Bedroom", "Kitchen", "Living Room"]

    if floor_type == "Commercial":
        base_rooms = ["Office", "Meeting Room", "Lobby"]

    return [{"room": r, "area": random.randint(12, 40)} for r in base_rooms]
