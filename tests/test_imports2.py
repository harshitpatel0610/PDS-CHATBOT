import sys
import logging
logging.basicConfig(level=logging.DEBUG)

print("importing chat_service")
from chatbot.services.chat_service import ChatService
print("done")
