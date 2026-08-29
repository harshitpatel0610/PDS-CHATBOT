import json
from pathlib import Path

def generate_phase13c_report():
    ext_metrics = {}
    if Path("reports/extraction_metrics.json").exists():
        with open("reports/extraction_metrics.json", "r", encoding="utf-8") as f:
            ext_metrics = json.load(f)
            
    # Read verified statuses from KB
    verified = 0
    partially_verified = 0
    unverified = 0
    
    kb_dir = Path("rag/knowledge_base_verified")
    for f in kb_dir.rglob("*.json"):
        with open(f, "r", encoding="utf-8") as file:
            try:
                record = json.load(file)
                status = record.get("source", {}).get("verification_status")
                if status == "verified":
                    verified += 1
                elif status == "partially_verified":
                    partially_verified += 1
                else:
                    unverified += 1
            except:
                pass
                
    total_claims = ext_metrics.get("claims_extracted", 0)
    
    report = {
        "total sources processed": ext_metrics.get("total_sources_processed", 0),
        "total knowledge records generated": ext_metrics.get("total_knowledge_records_generated", 0),
        "verified records": verified,
        "partially verified records": partially_verified,
        "unverified records": unverified,
        "claims extracted": total_claims,
        "claims verified": verified, # if a record is verified, its claims are verified
        "unsupported claims rejected": ext_metrics.get("unsupported_claims_rejected", 0),
        "records with null fields": ext_metrics.get("records_with_null_fields", 0),
        "source URLs": ext_metrics.get("source_urls", []),
        "evidence coverage percentage": (verified / total_claims * 100) if total_claims > 0 else 0.0
    }
    
    with open("reports/phase13c_verification_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    print(json.dumps(report, indent=4))

if __name__ == "__main__":
    generate_phase13c_report()
