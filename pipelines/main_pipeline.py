# core/pipelines/main_pipeline.py

from core.registry import register_pipeline

@register_pipeline("main")
def main_pipeline(input_data):
    return {
        "message": f"Pipeline executed successfully: {input_data}"
    }
