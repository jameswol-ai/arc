# src/core/engine.py

 def run(self):
    log = []
    summary_points = []

    for name, stage_fn in self.workflow:
        try:
            result = stage_fn(self.context)

            if not isinstance(result, dict):
                result = {"output": result}

            for k, v in result.items():
                self.context.set(k, v)

            summary_points.append(f"{name} completed successfully")

            log.append({
                "stage": name,
                "status": "ok",
                "output": result
            })

        except Exception as e:
            summary_points.append(f"{name} failed")

            log.append({
                "stage": name,
                "status": "failed",
                "error": str(e)
            })

    return {
        "summary": {
            "title": "Random Execution Report",
            "insight": self._generate_insight(summary_points)
        },
        "timeline": log,
        "final_context": self.context.data
    }


def _generate_insight(self, points):
    if not points:
        return "No execution data available."

    success = len([p for p in points if "completed" in p])
    failed = len([p for p in points if "failed" in p])

    if failed == 0:
        return f"All systems stable. {success} stages executed smoothly."

    return f"{success} stages succeeded, {failed} encountered instability."
