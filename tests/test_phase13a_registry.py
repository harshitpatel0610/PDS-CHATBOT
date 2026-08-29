import unittest
import json
import os
from pathlib import Path

STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", 
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", 
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", 
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", 
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
    "Uttar Pradesh", "Uttarakhand", "West Bengal"
]

UTS = [
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", 
    "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
]

class TestSourceRegistry(unittest.TestCase):
    
    def setUp(self):
        self.registry_dir = Path("rag/knowledge_sources/states")
        self.files = list(self.registry_dir.glob("*.json"))
        self.records = []
        for f in self.files:
            with open(f, "r", encoding="utf-8") as file:
                self.records.append(json.load(file))

    def test_no_district_field(self):
        for record in self.records:
            self.assertNotIn("district", record, "District field should not exist in the registry.")
            
    def test_all_states_uts_present(self):
        all_entities = set(STATES + UTS)
        found_entities = set(r.get("state") for r in self.records)
        self.assertEqual(all_entities, found_entities, "Not all States/UTs are represented in the registry.")
        
    def test_pending_sources_not_verified(self):
        for record in self.records:
            if record.get("acquisition_status") == "pending":
                self.assertNotEqual(record.get("verification_status"), "verified", "Pending sources cannot be verified.")
                
    def test_url_presence(self):
        for record in self.records:
            url = record.get("official_portal_url")
            if url:
                # Must be a government URL to be confidently populated in Phase 13A
                self.assertTrue(".gov.in" in url or ".nic.in" in url, f"URL {url} does not appear to be an official .gov.in/.nic.in domain.")
                self.assertIsNotNone(record.get("source_type"), "source_type must be set if URL is present.")
            else:
                self.assertEqual(record.get("acquisition_status"), "pending", "Records without URLs must be pending.")
                self.assertIn("notes", record)
                
    def test_schema_validation(self):
        required_keys = {
            "state", "official_department_name", "official_portal_url", 
            "source_type", "acquisition_status", "verification_status", 
            "accessed_at", "notes"
        }
        for record in self.records:
            self.assertTrue(required_keys.issubset(set(record.keys())), f"Missing keys in record {record.get('state')}")

if __name__ == "__main__":
    unittest.main()
