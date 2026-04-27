# src/core/evolver.py

class WorkflowEvolver:

    def apply(self, workflow, changes):
        for change in changes:
            if change["action"] == "remove":
                workflow["stages"] = [
                    s for s in workflow["stages"]
                    if s != change["stage"]
                ]
        return workflow
