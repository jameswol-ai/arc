# src/models/stage_contract.py

from typing import Dict, Any

class StageResult:
    def __init__(self, output, status="ok", signals=None):
        self.output = output
        self.status = status
        self.signals = signals or {}

    def to_dict(self):
        return {
            "output": self.output,
            "status": self.status,
            "signals": self.signals
        }


def stage_input(ctx: Dict[str, Any]):
    return {
        "input": ctx.get("input"),
        "knowledge": ctx.get("knowledge", []),
        "last_output": ctx.get("last_output")
    }
