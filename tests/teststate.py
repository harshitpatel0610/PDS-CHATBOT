from chatbot.conversation.manager import ConversationManager

session, result = ConversationManager.process(

    "user123",

    "I want to apply for BPL ration card in Karnataka"

)

print()

print("Intent:", session.current_intent)

print()

print("Entities:")

print(session.entities)

print()

print("History:")

for msg in session.history:

    print(msg)