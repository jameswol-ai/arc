# src/stages/analysis_stage.py

class AnalysisStage:
    def run(self, context):
        layout = {
            "rooms": ["living room", "2 bedrooms", "kitchen"],
            "orientation": "east-west for airflow",
            "ventilation": "cross ventilation"
        }

        context.update_design("layout", layout)
        return context
