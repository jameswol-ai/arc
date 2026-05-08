import json
import os
import uuid

MEMORY_FILE = "design_memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def store_design(design):
    memory = load_memory()

    design_entry = {
        "id": str(uuid.uuid4()),
        "design": design,
    }

    memory.append(design_entry)
    save_memory(memory)

    return design_entry
