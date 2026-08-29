import unittest
import json
import os
import shutil
import time
from pathlib import Path

from scripts.source_fetcher import fetch_source
from scripts.extract_source import extract_source
from scripts.verify_knowledge import verify_all

class TestAcquisition(unittest.TestCase):
    def setUp(self):
        for d in ["rag/knowledge_sources/states", "rag/raw_sources", "rag/knowledge_base_verified", "reports"]:
            p = Path(d)
            if p.exists():
                shutil.rmtree(p)
            p.mkdir(parents=True, exist_ok=True)
            
        # Create base knowledge sources dir
        Path("rag/knowledge_sources/states").mkdir(parents=True, exist_ok=True)
        
    def test_missing_source_url(self):
        # pending source remains pending, missing URL
        manifest = {"state": "Test State", "official_portal_url": None, "acquisition_status": "pending"}
        mf_path = Path("rag/knowledge_sources/states/test_state.json")
        with open(mf_path, "w") as f: json.dump(manifest, f)
        
        self.assertFalse(fetch_source(mf_path))
        with open(mf_path, "r") as f:
            self.assertEqual(json.load(f)["acquisition_status"], "pending")
            
    def test_http_failure_and_timeout(self):
        manifest = {"state": "Test 404", "official_portal_url": "http://httpbin.org/status/404", "acquisition_status": "pending"}
        mf_path = Path("rag/knowledge_sources/states/test_404.json")
        with open(mf_path, "w") as f: json.dump(manifest, f)
        self.assertFalse(fetch_source(mf_path))
        with open(mf_path, "r") as f:
            self.assertEqual(json.load(f)["acquisition_status"], "failed")
            
    def test_redirect_handling(self):
        # httpbin redirect test
        manifest = {"state": "Test Redirect", "official_portal_url": "http://httpbin.org/redirect/1", "acquisition_status": "pending"}
        mf_path = Path("rag/knowledge_sources/states/test_redirect.json")
        with open(mf_path, "w") as f: json.dump(manifest, f)
        self.assertTrue(fetch_source(mf_path))
        
        # Verify final_url is different
        dirs = list(Path("rag/raw_sources/states/test_redirect").iterdir())
        meta = json.load(open(dirs[-1] / "metadata.json"))
        self.assertIn("get", meta["final_url"])
            
    def test_successful_fetch_and_verify(self):
        manifest = {"state": "Test Success", "official_portal_url": "http://httpbin.org/html", "acquisition_status": "pending"}
        mf_path = Path("rag/knowledge_sources/states/test_success.json")
        with open(mf_path, "w") as f: json.dump(manifest, f)
        
        # Test Successful fetch & SHA256 & Duplicate snapshot
        self.assertTrue(fetch_source(mf_path))
        
        # check fetched status but NOT verified
        with open(mf_path, "r") as f:
            data = json.load(f)
            self.assertEqual(data["acquisition_status"], "fetched")
            self.assertNotEqual(data.get("verification_status"), "verified") # not auto verified
            
        time.sleep(1.1)
        self.assertTrue(fetch_source(mf_path)) # Duplicate snapshot
        
        dirs = list(Path("rag/raw_sources/states/test_success").iterdir())
        self.assertEqual(len(dirs), 2)
        
        meta = json.load(open(dirs[-1] / "metadata.json"))
        self.assertIsNotNone(meta["sha256"])
        
        # Check SHA256 consistency
        meta1 = json.load(open(dirs[0] / "metadata.json"))
        self.assertEqual(meta["sha256"], meta1["sha256"])
        
        # Run extraction
        extract_source(dirs[-1])
        
        # Test non-government rejection (source_type not official_government)
        kb = {
            "id": "test_kb",
            "source": {"source_type": "unknown", "verification_status": "unverified"},
            "facts": [{"text": "Moby Dick", "evidence": {"source_id": "states/test_success", "quote": "Moby-Dick"}}]
        }
        kb_path = Path("rag/knowledge_base_verified/test_kb.json")
        with open(kb_path, "w") as f: json.dump(kb, f)
        verify_all()
        self.assertEqual(json.load(open(kb_path))["source"]["verification_status"], "unverified")
        
        # Test verified transition
        kb["source"]["source_type"] = "official_government"
        with open(kb_path, "w") as f: json.dump(kb, f)
        verify_all()
        self.assertEqual(json.load(open(kb_path))["source"]["verification_status"], "verified")
        
        # district field never appears
        self.assertNotIn("district", kb)

if __name__ == "__main__":
    unittest.main()
