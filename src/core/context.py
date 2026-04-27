# src/core/context.py

from dataclasses import dataclass, field

@dataclass
class Context:
    data: dict = field(default_factory=dict)

    def set(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)
