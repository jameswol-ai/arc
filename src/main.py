#random/src/main.py

import sys, os
sys.path.append(os.path.abspath("src"))

from core.engine import WorkflowEngine
import json

if __name__ == "__main__":
    with open("../workflows/basic_design.json") as f:
        config = json.load(f)

    engine = WorkflowEngine(config)

    result = engine.run_workflow({
        "input": "Design a tropical eco house"
    })

    print(result)
