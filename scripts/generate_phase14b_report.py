import json
from pathlib import Path

def generate_report():
    report = {
      "states_processed": 0,
      "states_with_verified_claims": 0,
      "total_sources": 0,
      "total_verified_claims": 0,
      "total_null_fields": 0,
      "district_fields_found": 0,
      "unsupported_claims": 0
    }
    
    for file_path in Path("rag/curated_knowledge/templates").glob("*.json"):
        report["states_processed"] += 1
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if "district" in data:
            report["district_fields_found"] += 1
            
        report["total_sources"] += len(data.get("sources", []))
        
        kb_data = data.get("data", {})
        has_verified_claim = False
        
        scalar_fields = ["processing_time", "fees", "online_available", "offline_available", "application_url"]
        for field in scalar_fields:
            val_obj = kb_data.get(field, {})
            if val_obj and val_obj.get("value") is not None:
                report["total_verified_claims"] += 1
                has_verified_claim = True
            else:
                report["total_null_fields"] += 1
                report["unsupported_claims"] += 1
                
        docs = kb_data.get("required_documents", [])
        if not docs:
            report["total_null_fields"] += 1
            report["unsupported_claims"] += 1
        else:
            report["total_verified_claims"] += len(docs)
            has_verified_claim = True
            
        steps = kb_data.get("process_steps", [])
        if not steps:
            report["total_null_fields"] += 1
            report["unsupported_claims"] += 1
        else:
            report["total_verified_claims"] += len(steps)
            has_verified_claim = True
            
        if has_verified_claim:
            report["states_with_verified_claims"] += 1

    Path("reports").mkdir(parents=True, exist_ok=True)
    with open("reports/phase14b_population_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
if __name__ == "__main__":
    generate_report()
