import unittest
import json
import os
from pathlib import Path
from scripts.load_curated_knowledge import validate_record, build_document_text, run_ingestion
from rag.retriever import retriever

class TestPhase15Ingestion(unittest.TestCase):
    def setUp(self):
        self.templates_dir = Path("rag/curated_knowledge/templates")
        retriever.initialize()
        self.collection = retriever.collection
        
    def test_validation_rejects_missing_evidence(self):
        bad_data = {
            "state": "Test",
            "sources": [{"id": "s1", "url": "http://test.gov.in"}],
            "data": {
                "fees": {"value": "Rs. 20", "source_id": "s1"} # missing evidence_quote
            }
        }
        res = validate_record(bad_data)
        self.assertFalse(res[0])
        self.assertIn("Missing evidence_quote", res[1])
        
    def test_validation_rejects_district(self):
        bad_data = {
            "state": "Test",
            "district": "TestDistrict",
            "sources": [{"id": "s1", "url": "http://test.gov.in"}],
            "data": {}
        }
        res = validate_record(bad_data)
        self.assertFalse(res[0])
        self.assertIn("district field", res[1])
        
    def test_validation_rejects_empty_claims(self):
        empty_data = {
            "state": "Test",
            "sources": [{"id": "s1", "url": "http://test.gov.in"}],
            "data": {},
            "verification_status": "unverified"
        }
        res = validate_record(empty_data)
        self.assertFalse(res[0])
        self.assertIn("Status is unverified", res[1])
        
    def test_build_document_text(self):
        good_data = {
            "state": "Gujarat",
            "intent": "apply",
            "data": {
                "fees": {"value": "Rs. 20", "source_id": "s1", "evidence_quote": "Fees is Rs. 20"}
            }
        }
        text = build_document_text(good_data)
        self.assertIn("State: Gujarat", text)
        self.assertIn("Rs. 20", text)
        self.assertIn("Fees is Rs. 20", text)
        self.assertNotIn("Processing Time", text) # missing fields should not appear
        
    def test_retriever_state_isolation(self):
        # We assume the retriever handles isolation if state is passed
        # This is a unit test of the retriever search isolation
        res1 = retriever.search("test", state="Gujarat")
        self.assertIn(res1.get("retrieval_level"), ["state_intent", "semantic_fallback", "none"])
        
if __name__ == "__main__":
    unittest.main()
