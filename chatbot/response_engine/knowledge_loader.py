import json
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"


class KnowledgeLoader:

    @staticmethod
    def load(intent):

        path = KNOWLEDGE_DIR / f"{intent}.json"

        if not path.exists():
            return None

        with open(path, encoding="utf8") as f:
            return json.load(f)