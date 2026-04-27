# src/stages/output_stage.py

class OutputStage:
    def run(self, context):
        design = context.get_design()

        summary = f"""
        Concept: {design['concept']}
        Rooms: {design['layout'].get('rooms')}
        Compliance: {design['compliance']}
        """

        context.update_design("output_summary", summary.strip())
        return context
