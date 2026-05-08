def interpret_intent(text: str) -> dict:
    return {
        "building_type": "Residential",
        "style": "Modern",
        "complexity": "Medium",
        "floors": 5 if "apartment" in text.lower() else 2
    }
