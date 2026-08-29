from .registry import load_workflow


class WorkflowEngine:

    @staticmethod
    def start(intent):

        workflow = load_workflow(intent)

        return workflow["steps"][0]["question"]