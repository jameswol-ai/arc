#src/core/engine.py

def run_workflow(self, workflow_name):
    if workflow_name not in self.workflow:
        raise ValueError(f"Workflow '{workflow_name}' not found")

    stages = self.workflow[workflow_name]
    result = None

    for stage in stages:
        stage_func = stage["func"]
        stage_name = stage.get("name", stage_func.__name__)
        condition = stage.get("condition", None)

        # 🧠 check condition (if any)
        if condition:
            should_run = condition(self.context)
            if not should_run:
                print(f"⏭️ Skipping stage: {stage_name}")
                continue

        print(f"⚙️ Running stage: {stage_name}")

        result = stage_func(self.context)
        self.context[stage_name] = result

    return result
