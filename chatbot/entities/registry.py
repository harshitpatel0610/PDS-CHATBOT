import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

ENTITY_DATA = {}

for file in DATA_DIR.glob("*.json"):

    print(f"Loading {file.name}")

    with open(file, encoding="utf8") as f:
        data = json.load(f)

        # If JSON has a wrapper object
        if isinstance(data, dict):

            if file.stem in data:
                ENTITY_DATA[file.stem] = data[file.stem]

            else:
                ENTITY_DATA[file.stem] = data

            # If JSON is already a list
        else:
         ENTITY_DATA[file.stem] = data