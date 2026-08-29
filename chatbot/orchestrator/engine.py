from chatbot.router.service import RoutingService
from chatbot.entities.extractor import EntityExtractor
from chatbot.router.workflow.manager import WorkflowManager


class Orchestrator:

    def __init__(self):

        self.router = RoutingService()

        self.workflow = WorkflowManager()

    def process(self, query):

        # Step 1
        route = self.router.classify(query)

        # Step 2
        entities = EntityExtractor.extract(
            query,
            route.intent
        )

        # Step 3
        response = self.workflow.handle(
            route,
            entities
        )

        return response