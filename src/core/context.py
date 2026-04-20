class Dispatcher:
    def __init__(self, stages):
        self.stages = {stage["name"]: stage["func"] for stage in stages}

    def dispatch(self, stage_name, context):
        if stage_name not in self.stages:
            raise Exception(f"Stage {stage_name} not found in workflow")

        return self.stages[stage_name](context)
