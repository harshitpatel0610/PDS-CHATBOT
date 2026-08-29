import json
from pathlib import Path

def generate_report():
    manifests_dir = Path("rag/knowledge_sources/states")
    raw_sources_dir = Path("rag/raw_sources/states")
    kb_dir = Path("rag/knowledge_base_verified")
    
    total = 0
    confirmed = 0
    pending = 0
    fetched = 0
    failed = 0
    extracted = 0
    duplicates = 0
    invalid = 0
    http_failures = 0
    
    verified = 0
    unverified = 0
    partially_verified = 0
    
    for f in manifests_dir.glob("*.json"):
        total += 1
        with open(f, "r", encoding="utf-8") as file:
            record = json.load(file)
            
        url = record.get("official_portal_url")
        status = record.get("acquisition_status")
        
        if url:
            confirmed += 1
        else:
            pending += 1
            
        if status == "fetched":
            fetched += 1
        elif status == "failed":
            failed += 1
            http_failures += 1
            
    # Count snapshots and extraction
    if raw_sources_dir.exists():
        for state_dir in raw_sources_dir.iterdir():
            if state_dir.is_dir():
                snaps = list(state_dir.iterdir())
                if len(snaps) > 1:
                    duplicates += (len(snaps) - 1)
                for snap in snaps:
                    if (snap / "extracted.txt").exists():
                        extracted += 1
                        
    # Count verified records
    if kb_dir.exists():
        for f in kb_dir.rglob("*.json"):
            with open(f, "r", encoding="utf-8") as file:
                try:
                    record = json.load(file)
                    vstatus = record.get("source", {}).get("verification_status")
                    if vstatus == "verified":
                        verified += 1
                    elif vstatus == "partially_verified":
                        partially_verified += 1
                    else:
                        unverified += 1
                except:
                    pass

    report = {
        "total jurisdictions": total,
        "confirmed sources": confirmed,
        "pending sources": pending,
        "successfully fetched": fetched,
        "failed fetches": failed,
        "extracted sources": extracted,
        "duplicate snapshots": duplicates,
        "invalid sources": invalid,
        "HTTP failures": http_failures,
        "verification status counts": {
            "verified": verified,
            "partially_verified": partially_verified,
            "unverified": unverified
        }
    }
    
    out_path = Path("reports/phase13b_acquisition_report.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    print(json.dumps(report, indent=4))

if __name__ == "__main__":
    generate_report()
