# src/core/workflow_loader.py

import json
import os

WORKFLOW_DIR = "workflows"

def load_workflow(name):
    """
    Loads a workflow JSON file by name.
    Example: load_workflow("eco_building")
    """
    path = os.path.join(WORKFLOW_DIR, f"{name}.json")

    if not os.path.exists(path):
        raise FileNotFoundError(f"Workflow '{name}' not found at {path}")

    with open(path, "r") as f:
        return json.load(f)
