# src/knowledge/doc_loader.py

import os

class DocLoader:
    def __init__(self, docs_path="docs/building_codes"):
        self.docs_path = docs_path

    def load_doc(self, name: str):
        path = os.path.join(self.docs_path, name)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Doc not found: {name}")

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def load_all(self):
        docs = {}

        for file in os.listdir(self.docs_path):
            if file.endswith(".md"):
                docs[file] = self.load_doc(file)

        return docs
