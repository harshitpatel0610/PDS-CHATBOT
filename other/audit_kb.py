import json
import os
from pathlib import Path

def audit_kb():
    kb_dir = Path("rag/knowledge_base")
    
    records = []
    
    for file_path in kb_dir.rglob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            source_info = data.get("source", {})
            if isinstance(source_info, dict):
                url = source_info.get("url", "")
                if not url and "references" in source_info:
                    url = source_info["references"][0] if source_info["references"] else ""
                org = source_info.get("organization", source_info.get("name", ""))
            else:
                url = ""
                org = source_info
                
            records.append({
                "file": str(file_path.relative_to(kb_dir)).replace('\\', '/'),
                "state": data.get("state", "N/A"),
                "district": data.get("district", "N/A"),
                "card_type": data.get("card_type", "N/A"),
                "intent": data.get("intent", "N/A"),
                "url": url if url else org if org else "None",
            })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
    total = len(records)
    print("=== KNOWLEDGE BASE AUDIT ===")
    print(f"Total JSON files: {total}")
    print(f"Verified: 0")
    print(f"Partially verified: 0")
    print(f"Unverified: {total}")
    print(f"Unknown: 0")
    print("\nFile | State | District | Card Type | Intent | Source | Source Verified | Status | Problems")
    print("---|---|---|---|---|---|---|---|---")
    for r in records:
        print(f"{r['file']} | {r['state']} | {r['district']} | {r['card_type']} | {r['intent']} | {r['url']} | False | UNVERIFIED | LLM-generated offline; Source URL not fetched; Facts not traceable to cited source")

if __name__ == "__main__":
    audit_kb()
