from .steps import WORKFLOWS


class WorkflowManager:

    @staticmethod
    def next_question(session):

        workflow = WORKFLOWS.get(session.current_intent)

        if workflow is None:
            return None

        # Find first missing entity
        for step in workflow:

            entity = step["entity"]

            if entity not in session.entities:
                return step["question"]

        return None

    @staticmethod
    def is_complete(session):

        workflow = WORKFLOWS.get(session.current_intent)

        if workflow is None:
            return True

        for step in workflow:

            if step["entity"] not in session.entities:
                return False

        return True