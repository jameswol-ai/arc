# src/models/council.py

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Opinion:
    agent: str
    proposal: Any
    score: float
    reasoning: str

    def to_dict(self):
        return {
            "agent": self.agent,
            "proposal": self.proposal,
            "score": self.score,
            "reasoning": self.reasoning
        }
