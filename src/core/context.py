# src/core/context.py

class Context:
    def __init__(self, input_data):
        self.input = input_data
        self.data = {}
        self.history = []
        self.errors = []

    def log(self, message):
        self.history.append(message)

    def add_error(self, error):
        self.errors.append(str(error))
