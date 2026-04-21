# src/models/debate.py

from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class Argument:
    speaker: str
    message: str
    supports: List[str]
    challenges: List[str]

    def to_dict(self):
        return {
            "speaker": self.speaker,
            "message": self.message,
            "supports": self.supports,
            "challenges": self.challenges
        }
