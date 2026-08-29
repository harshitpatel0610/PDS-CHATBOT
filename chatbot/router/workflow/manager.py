from .registry import get
from .state import ConversationState


class WorkflowManager:

    def start(self, intent):

        workflow = get(intent)

        state = ConversationState()

        state.intent = intent

        return state, workflow["steps"][0]["question"]