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

CONFIDENT_URLS = {
    "Gujarat": "https://dcs-dof.gujarat.gov.in/",
    "Uttar Pradesh": "https://fcs.up.gov.in/",
    "Delhi": "https://nfs.delhi.gov.in/",
    "Bihar": "http://epds.bihar.gov.in/",
    "Jharkhand": "https://aahar.jharkhand.gov.in/"
}

def generate_registry():
    out_dir = Path("rag/knowledge_sources/states")
    
    for entity_name, is_state in [(s, True) for s in STATES] + [(u, False) for u in UTS]:
        # Formulate a safe filename
        filename = entity_name.lower().replace(" ", "_") + ".json"
        
        url = CONFIDENT_URLS.get(entity_name, None)
        
        manifest = {
            "state": entity_name,
            "is_ut": not is_state,
            "official_department_name": "Food and Civil Supplies Department" if url else None,
            "official_portal_url": url,
            "source_type": "official_government" if url else None,
            "acquisition_status": "pending",
            "verification_status": "unverified",
            "accessed_at": None,
            "notes": "URL confidently known." if url else "Official source URL needs manual verification/search before fetching."
        }
        
        with open(out_dir / filename, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=4)
            
if __name__ == "__main__":
    generate_registry()
