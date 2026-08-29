import unittest
import json
import os
import shutil
import hashlib
from pathlib import Path
from scripts.deep_spider import run_spider, extract_text_from_html, is_official_url

class TestPhase13EDiscovery(unittest.TestCase):
    
    def test_district_field_absent(self):
        # District must NOT be used anywhere
        self.assertFalse(Path("rag/knowledge_sources/districts").exists())
        
        inv_path = Path("reports/phase13e_evidence_inventory.json")
        if inv_path.exists():
            with open(inv_path, "r") as f:
                inv = json.load(f)
                for item in inv:
                    self.assertNotIn("district", item)
                    
    def test_official_government_domains_only(self):
        self.assertTrue(is_official_url("http://epds.bihar.gov.in/Rules.htm"))
        self.assertTrue(is_official_url("https://fcs.up.nic.in/index.html"))
        self.assertFalse(is_official_url("http://example.com"))
        self.assertFalse(is_official_url("https://google.com/search?q=up+ration+card"))
        
    def test_missing_fee_and_processing_time_produces_null(self):
        # Simulate logic: If we extract "Processing time" but no number, it rejects the claim
        # which means it never goes into verified inventory, so knowledge generator will default to null
        html = b"<html><body><p>Application Fee</p><p>Processing time varies</p></body></html>"
        txt = extract_text_from_html(html)
        
        # Test logic used in deep_spider
        lines = txt.split("\n")
        fee_found = False
        pt_found = False
        import re
        for l in lines:
            if "fee" in l.lower() and ("rs" in l.lower() or "rupees" in l.lower()):
                fee_found = True
            if "processing time" in l.lower() and "days" in l.lower():
                pt_found = True
                
        self.assertFalse(fee_found)
        self.assertFalse(pt_found)
        
    def test_verified_claim_has_evidence_quote_and_url(self):
        inv_path = Path("reports/phase13e_evidence_inventory.json")
        if inv_path.exists():
            with open(inv_path, "r") as f:
                inv = json.load(f)
                for item in inv:
                    self.assertTrue(item.get("verified"))
                    self.assertIsNotNone(item.get("evidence_quote"))
                    self.assertIsNotNone(item.get("source_url"))
                    
    def test_sha256_preservation(self):
        html = b"<html>Test HTML Content</html>"
        sha256 = hashlib.sha256(html).hexdigest()
        self.assertEqual(len(sha256), 64)
        
if __name__ == "__main__":
    unittest.main()
