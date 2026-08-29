import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

KNOWLEDGE_DIR = BASE_DIR / "data" / "knowledge"

print("BASE_DIR:", BASE_DIR)
print("KNOWLEDGE_DIR:", KNOWLEDGE_DIR)

class KnowledgeLoader:

    @staticmethod
    def load(category, topic):

        file_path = KNOWLEDGE_DIR / category / f"{topic}.json"

        print("Looking for:", file_path)

        if not file_path.exists():
            print("❌ File not found")
            return None

        print("✅ File found")

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)