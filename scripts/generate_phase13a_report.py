import json
from pathlib import Path

def generate_report():
    registry_dir = Path("rag/knowledge_sources/states")
    files = list(registry_dir.glob("*.json"))
    
    total_states = 0
    total_uts = 0
    confirmed = 0
    pending = 0
    invalid = 0
    fabricated = 0
    
    for f in files:
        with open(f, "r", encoding="utf-8") as file:
            record = json.load(file)
            
        if record.get("is_ut"):
            total_uts += 1
        else:
            total_states += 1
            
        url = record.get("official_portal_url")
        status = record.get("acquisition_status")
        
        if url:
            if ".gov.in" in url or ".nic.in" in url:
                confirmed += 1
            else:
                invalid += 1
                fabricated += 1
        else:
            if status == "pending":
                pending += 1
            else:
                invalid += 1
                
    report = {
        "total States": total_states,
        "total UTs": total_uts,
        "total registry entries": len(files),
        "confirmed official sources": confirmed,
        "pending sources": pending,
        "invalid sources": invalid,
        "fabricated/unchecked sources detected": fabricated
    }
    
    out_path = Path("reports/phase13a_source_registry_report.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    print(json.dumps(report, indent=4))

if __name__ == "__main__":
    generate_report()
