from chatbot.knowledge.loader import KnowledgeLoader

data = KnowledgeLoader.load(
    "ration_card",
    "apply"
)

print(data)