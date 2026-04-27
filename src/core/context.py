# src/core/context.py

class Context:
    def __init__(self, data=None):
        self.data = data or {}

    def update(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)
