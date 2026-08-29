import unittest
import json
import os
from pathlib import Path
from scripts.validate_curated_knowledge import validate_curated_knowledge

class TestPhase14BPopulation(unittest.TestCase):
    def setUp(self):
        self.templates_dir = Path("rag/curated_knowledge/templates")
        
    def test_district_never_appears(self):
        for file_path in self.templates_dir.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertNotIn("district", data)
            
    def test_official_sources_only(self):
        for file_path in self.templates_dir.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for src in data.get("sources", []):
                url = src.get("url")
                if url:
                    self.assertTrue(".gov.in" in url.lower() or ".nic.in" in url.lower())
                    
    def test_evidence_presence(self):
        # Every non-null claim must have source_id and non-empty evidence_quote
        for file_path in self.templates_dir.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            kb_data = data.get("data", {})
            for field in ["processing_time", "fees", "online_available", "offline_available", "application_url"]:
                val_obj = kb_data.get(field, {})
                if val_obj and val_obj.get("value") is not None:
                    self.assertTrue(val_obj.get("source_id"))
                    self.assertTrue(val_obj.get("evidence_quote"))
                    self.assertGreater(len(val_obj.get("evidence_quote").strip()), 0)
                    
            for doc in kb_data.get("required_documents", []):
                self.assertTrue(doc.get("source_id"))
                self.assertTrue(doc.get("evidence_quote"))
                
            for step in kb_data.get("process_steps", []):
                self.assertTrue(step.get("source_id"))
                self.assertTrue(step.get("evidence_quote"))
                
    def test_validation_fails_on_missing_evidence(self):
        # We temporarily create a bad file and ensure validation throws or prints fail
        bad_file = self.templates_dir / "bad_test.json"
        with open(bad_file, "w") as f:
            json.dump({
                "state": "Test",
                "sources": [{"id": "s1", "url": "http://test.gov.in"}],
                "data": {
                    "fees": {"value": "Rs. 20"} # Missing evidence
                }
            }, f)
        
        try:
            with self.assertRaises(SystemExit):
                validate_curated_knowledge(str(self.templates_dir))
        finally:
            if bad_file.exists():
                bad_file.unlink()

if __name__ == "__main__":
    unittest.main()
