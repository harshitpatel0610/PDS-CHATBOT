import os
import unittest
from unittest.mock import patch
import sys
import importlib

class TestApiKeySafety(unittest.TestCase):
    def setUp(self):
        self.original_environ = dict(os.environ)
        
    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_production_key_available_in_server_mode(self):
        # Requirement A: Production GOOGLE_API_KEY + manual/server mode => production key remains available
        os.environ["GOOGLE_API_KEY"] = "prod_key_123"
        if "TEST_GOOGLE_API_KEY" in os.environ:
            del os.environ["TEST_GOOGLE_API_KEY"]
            
        # Simulate running via uvicorn/main.py
        with patch.object(sys, 'argv', ['uvicorn']):
            with patch.dict('os.environ', {}, clear=True):
                os.environ["GOOGLE_API_KEY"] = "prod_key_123"
                import chatbot.config
                importlib.reload(chatbot.config)
                self.assertEqual(chatbot.config.GOOGLE_API_KEY, "prod_key_123")

    def test_production_key_suppressed_in_testing_mode(self):
        # Requirement B: Production GOOGLE_API_KEY + TESTING=1 => production key is suppressed
        os.environ["GOOGLE_API_KEY"] = "prod_key_123"
        if "TEST_GOOGLE_API_KEY" in os.environ:
            del os.environ["TEST_GOOGLE_API_KEY"]
            
        with patch.dict('os.environ', {"TESTING": "1"}):
            import chatbot.config
            importlib.reload(chatbot.config)
            self.assertIsNone(chatbot.config.GOOGLE_API_KEY)

    def test_test_key_used_in_testing_mode(self):
        # Requirement C: TESTING=1 + TEST_GOOGLE_API_KEY => only TEST_GOOGLE_API_KEY is used
        os.environ["GOOGLE_API_KEY"] = "prod_key_123"
        os.environ["TEST_GOOGLE_API_KEY"] = "test_key_456"
        
        with patch.dict('os.environ', {"TESTING": "1"}):
            import chatbot.config
            importlib.reload(chatbot.config)
            self.assertEqual(chatbot.config.GOOGLE_API_KEY, "test_key_456")

    def test_third_party_import_of_unittest_does_not_activate_testing(self):
        # Requirement D: Third-party import of unittest does NOT activate testing mode
        os.environ["GOOGLE_API_KEY"] = "prod_key_123"
        if "TEST_GOOGLE_API_KEY" in os.environ:
            del os.environ["TEST_GOOGLE_API_KEY"]
            
        # Simulate sys.modules having unittest (which it already does since we are in unittest!)
        # We need to simulate running via uvicorn again but with unittest in sys.modules
        with patch.object(sys, 'argv', ['uvicorn']):
            with patch.dict('os.environ', {}, clear=True):
                os.environ["GOOGLE_API_KEY"] = "prod_key_123"
                # sys.modules contains 'unittest' because this test suite uses it!
                self.assertIn("unittest", sys.modules)
                
                import chatbot.config
                importlib.reload(chatbot.config)
                self.assertEqual(chatbot.config.GOOGLE_API_KEY, "prod_key_123", "unittest in sys.modules incorrectly activated testing mode!")

if __name__ == "__main__":
    unittest.main()
