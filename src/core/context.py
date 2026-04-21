# src/core/context.py

class Context:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def update(self, new_data: dict):
        self.data.update(new_data)
