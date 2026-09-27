import unittest
import uuid
import time
from unittest.mock import patch, MagicMock

from chatbot.services.cache_service import cache_service
from chatbot.services.rag_service import RAGService


class MockSession:
    def __init__(self, sid):
        self.session_id = sid
        self.entities = {}
        self.current_intent = "ration_card_apply"
        self.history = []

class TestCacheService(unittest.TestCase):
    
    def setUp(self):
        # Clear cache before each test
        cache_service.cache.clear()

    def test_cache_key_deterministic(self):
        # 8, 9, 10, 11: Different states/districts/contexts produce different keys
        k1 = cache_service._generate_key("intent", {"states": "A"}, "level", ["doc1"], "ctx", [{"msg":"hi"}])
        k2 = cache_service._generate_key("intent", {"states": "B"}, "level", ["doc1"], "ctx", [{"msg":"hi"}])
        k3 = cache_service._generate_key("intent", {"states": "A", "districts": "D1"}, "level", ["doc1"], "ctx", [{"msg":"hi"}])
        k4 = cache_service._generate_key("intent", {"states": "A", "card_types": "C1"}, "level", ["doc1"], "ctx", [{"msg":"hi"}])
        k5 = cache_service._generate_key("intent", {"states": "A"}, "level", ["doc1", "doc2"], "ctx2", [{"msg":"hi"}])
        
        self.assertNotEqual(k1, k2)
        self.assertNotEqual(k1, k3)
        self.assertNotEqual(k1, k4)
        self.assertNotEqual(k1, k5)

    def test_cache_store_and_hit(self):
        # 6. Cache hit
        # 13. Successful response IS cached
        cache_service.set("intent", {"s": "A"}, "lvl", ["d1"], "ctx", [], "Success Answer")
        res = cache_service.get("intent", {"s": "A"}, "lvl", ["d1"], "ctx", [])
        self.assertEqual(res, "Success Answer")

    def test_cache_miss(self):
        # 5. Cache miss
        res = cache_service.get("intent", {"s": "MISS"}, "lvl", ["d1"], "ctx", [])
        self.assertIsNone(res)

    def test_cache_expiry(self):
        # 7. Cache expiry
        old_ttl = cache_service.ttl_seconds
        cache_service.ttl_seconds = 0.1
        cache_service.set("intent", {"s": "A"}, "lvl", ["d1"], "ctx", [], "Expiring Answer")
        time.sleep(0.2)
        res = cache_service.get("intent", {"s": "A"}, "lvl", ["d1"], "ctx", [])
        self.assertIsNone(res)
        cache_service.ttl_seconds = old_ttl

    def test_no_cache_for_errors(self):
        # 12. 429 fallback is NOT cached
        cache_service.set("i", {}, "l", [], "c", [], "Our system is currently experiencing high traffic. Please try again.")
        res = cache_service.get("i", {}, "l", [], "c", [])
        self.assertIsNone(res)
        
        # 4. generic failure
        cache_service.set("i", {}, "l", [], "c", [], "I apologize, but I encountered an LLM_ERROR.")
        res = cache_service.get("i", {}, "l", [], "c", [])
        self.assertIsNone(res)

if __name__ == '__main__':
    unittest.main()
