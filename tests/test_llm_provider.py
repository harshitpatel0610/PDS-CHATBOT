import unittest
import os
import sys
from unittest.mock import patch
import importlib

class TestLLMProvider(unittest.TestCase):
    def setUp(self):
        # We need to reload config to test environment variables
        pass

    def _reload_config_and_factory(self, env_vars, sys_args=["uvicorn"]):
        with patch.dict('os.environ', env_vars, clear=True), patch.object(sys, 'argv', sys_args):
            import chatbot.config
            importlib.reload(chatbot.config)
            
            # Also reload clients so they pick up new config
            import chatbot.llms.gemini
            importlib.reload(chatbot.llms.gemini)
            
            # Also reload factory so it picks up new config
            import chatbot.llms.factory
            importlib.reload(chatbot.llms.factory)
            
            return chatbot.llms.factory.get_llm, chatbot.config

    def test_provider_gemini_selected(self):
        # Test A
        get_llm, config = self._reload_config_and_factory({
            "LLM_PROVIDER": "gemini",
            "GOOGLE_API_KEY": "fake_gemini_key",
        })
        llm = get_llm()
        from chatbot.llms.gemini import GeminiClient
        self.assertIsInstance(llm, GeminiClient)

    def test_invalid_provider_error(self):
        # Test D
        with self.assertRaises(ValueError) as context:
            self._reload_config_and_factory({
                "LLM_PROVIDER": "invalid_provider",
            })
            # factory will evaluate on import or when get_llm is called
            # wait, get_llm is a function, so let's call it
            import chatbot.llms.factory
            chatbot.llms.factory.get_llm()
        self.assertIn("Unsupported model provider: invalid_provider", str(context.exception))

if __name__ == '__main__':
    unittest.main()
