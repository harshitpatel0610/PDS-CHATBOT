import os
from unittest.mock import patch

os.environ['LLM_PROVIDER'] = 'foundry'
os.environ['FOUNDRY_API_KEY'] = 'fake'
os.environ['FOUNDRY_BASE_URL'] = 'https://fake.azure.com/openai/v1'
os.environ['FOUNDRY_MODEL'] = 'fake-model-123'
os.environ['TESTING'] = '0'

# Ensure configs load properly with the above
import importlib
import chatbot.config
importlib.reload(chatbot.config)
import chatbot.llms.factory
importlib.reload(chatbot.llms.factory)
import chatbot.llms.foundry_client
importlib.reload(chatbot.llms.foundry_client)

from chatbot.services.chat_service import ChatService
from chatbot.conversation.session import ConversationSession

s = ConversationSession('test_manual')
s.history=[{'role': 'user', 'message': 'Is Aadhaar mandatory for everyone applying for a Gujarat ration card?'}]

with patch.object(chatbot.llms.foundry_client.FoundryClient, 'generate_response', return_value='MOCKED_FOUNDRY_RESPONSE') as mock_gen:
    res = ChatService.process(s, 'Is Aadhaar mandatory for everyone applying for a Gujarat ration card?')
    print('INTENT:', res['intent'])
    print('ENTITIES:', res['entities'])
    print('RESPONSE:', res['response'])
    if mock_gen.called:
        prompt = mock_gen.call_args[0][0]
        print('LLM_PROMPT_PREFIX:', prompt[:300])
        print('EVIDENCE_CONFLICT_PRESENT:', 'evidence_conflicts' in prompt.lower())
    else:
        print('LLM_PROMPT: NOT_CALLED')
    if mock_gen.called:
        prompt = mock_gen.call_args[0][0]
        print('LLM_PROMPT_PREFIX:', prompt[:300])
        print('EVIDENCE_CONFLICT_PRESENT:', 'evidence_conflicts' in prompt.lower())
    else:
        print('LLM_PROMPT: NOT_CALLED')
