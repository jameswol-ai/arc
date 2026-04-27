# src/memory/memory_store.py

import json
from pathlib import Path

class MemoryStore:
    def __init__(self, path="memory.json"):
        self.path = Path(path)
        if not self.path.exists():
            self.path.write_text("{}")

    def load(self):
        return json.loads(self.path.read_text())

    def save(self, data):
        self.path.write_text(json.dumps(data, indent=2))

    def update(self, key, value):
        data = self.load()
        data[key] = value
        self.save(data)
