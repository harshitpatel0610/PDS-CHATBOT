from chatbot.knowledge.loader import KnowledgeLoader
from chatbot.knowledge.mapper import KNOWLEDGE_MAP


class ResponseGenerator:

    @staticmethod
    def generate(intent, entities):

        print(">>> ResponseGenerator CALLED <<<")
        print("Intent:", intent)
        print("Entities:", entities)

        if intent not in KNOWLEDGE_MAP:
            return "Sorry, I don't have knowledge for this request."

        category, topic = KNOWLEDGE_MAP[intent]

        print("Loading:", category, topic)

        knowledge = KnowledgeLoader.load(
            category,
            topic
        )

        print("Knowledge:", knowledge)

        if knowledge is None:
            return "Knowledge not found."

        response = []

        response.append(
            f"📌 {knowledge['title']}"
        )

        response.append(
            knowledge["summary"]
        )

        response.append("\n📄 Required Documents")

        for doc in knowledge["required_documents"]:
            response.append(f"• {doc}")

        response.append("\n📝 Application Steps")

        for i, step in enumerate(
            knowledge["application_steps"],
            start=1
        ):
            response.append(f"{i}. {step}")

        response.append(
            f"\n⏳ Processing Time: "
            f"{knowledge['processing_time']}"
        )

        response.append(
            f"💰 Fees: {knowledge['fees']}"
        )

        return "\n".join(response)