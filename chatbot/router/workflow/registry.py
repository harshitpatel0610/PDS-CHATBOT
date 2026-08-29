import json

from pathlib import Path

WORKFLOW_DIR = Path(__file__).parent / "definitions"

WORKFLOWS = {}


def load_all():

    for file in WORKFLOW_DIR.glob("*.json"):

        with open(file, encoding="utf8") as f:

            workflow = json.load(f)

            WORKFLOWS[
                workflow["intent"]
            ] = workflow


load_all()


def get(intent):

    return WORKFLOWS.get(intent)