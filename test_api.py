import unittest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch
import uuid

class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.client.__enter__()
        
    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)
        
    def test_health(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "ok", "vector_store": "available"})

    def test_missing_session_id(self):
        res = self.client.post("/chat", json={"session_id": "", "message": "hello"})
        self.assertEqual(res.status_code, 200)
        self.assertIn("missing session_id", res.json()["reply"].lower())

    def test_empty_message(self):
        res = self.client.post("/chat", json={"session_id": "123", "message": "   "})
        self.assertEqual(res.status_code, 200)
        self.assertIn("empty message", res.json()["reply"].lower())

    def test_invalid_message(self):
        res = self.client.post("/chat", json={"session_id": "123"})
        self.assertEqual(res.status_code, 422)

    def test_new_session_and_multiturn(self):
        sid = str(uuid.uuid4())
        # 1. New Session
        res1 = self.client.post("/chat", json={"session_id": sid, "message": "How can I apply for a new ration card?"})
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["intent"], "ration_card_apply")
        
        # 2. Existing Session
        res2 = self.client.post("/chat", json={"session_id": sid, "message": "Gujarat"})
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["entities"]["states"], "Gujarat")
        
        # 3. Existing Session continued
        res3 = self.client.post("/chat", json={"session_id": sid, "message": "Sabarkantha"})
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(res3.json()["entities"]["districts"], "Sabarkantha")

    @patch('chatbot.llms.gemini.GeminiClient.generate_response')
    def test_non_pds_query(self, mock_llm):
        mock_llm.return_value = "I can only help with ration card queries."
        res = self.client.post("/chat", json={"session_id": "abc", "message": "What is the capital of France?"})
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(res.json()["intent"])

    @patch('chatbot.services.rag_service.retriever.search')
    def test_retriever_failure(self, mock_search):
        mock_search.side_effect = Exception("ChromaDB died")
        res = self.client.post("/chat", json={"session_id": "fail1", "message": "How can I apply for an APL ration card in Sabarkantha, Gujarat?"})
        self.assertTrue("error" in res.json()["reply"].lower() or "retriever" in res.json()["reply"].lower())

    @patch('chatbot.llms.gemini.GeminiClient.generate_response')
    def test_llm_failure(self, mock_llm):
        mock_llm.side_effect = Exception("429 RESOURCE_EXHAUSTED")
        res = self.client.post("/chat", json={"session_id": "fail2", "message": "How can I apply for an APL ration card in Sabarkantha, Gujarat?"})
        self.assertIn("traffic", res.json()["reply"].lower())

if __name__ == "__main__":
    unittest.main()
