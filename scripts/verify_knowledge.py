import json
import os
from pathlib import Path

def verify_record(kb_path, manifests, extracted_texts):
    with open(kb_path, "r", encoding="utf-8") as f:
        record = json.load(f)
        
    source = record.get("source", {})
    if source.get("source_type") != "official_government":
        return "unverified", "Not an official government source"
        
    # Get manifest
    # We match by URL or by source_id. We need source_id in evidence.
    
    # 1. Check all list fields (facts, process, required_documents) for evidence
    all_evidence_valid = True
    has_any_claims = False
    
    for field in ["facts", "process", "required_documents"]:
        items = record.get(field, [])
        if not items:
            continue
            
        for item in items:
            has_any_claims = True
            if not isinstance(item, dict) or "text" not in item or "evidence" not in item:
                return "unverified", f"Missing evidence structure in {field}"
                
            evidence = item["evidence"]
            source_id = evidence.get("source_id")
            quote = evidence.get("quote")
            
            if not source_id or not quote:
                return "unverified", f"Incomplete evidence in {field}"
                
            manifest = manifests.get(source_id)
            if not manifest:
                return "unverified", f"Source {source_id} not found"
                
            manifest_status = manifest.get("status") or manifest.get("acquisition_status")
            if manifest_status not in ["fetched", "verified"]:
                return "unverified", f"Source {source_id} is not successfully fetched"
                
            # Verify quote exists in extracted text
            ext_text = extracted_texts.get(source_id, "")
            if quote not in ext_text:
                # To be lenient with spacing:
                q_clean = " ".join(quote.split())
                t_clean = " ".join(ext_text.split())
                if q_clean not in t_clean:
                    return "partially_verified", f"Quote not found in extracted source text: '{quote}'"
                    
    # 2. Nullable fields check
    for field in ["fees", "processing_time", "online", "offline"]:
        val = record.get(field)
        if val is not None:
            # For this simple verification, if a nullable field is populated, it currently doesn't have an "evidence" dict attached (schema is simple), so technically it's unsupported unless we change schema to make fees a dict with evidence.
            # We will consider it partially verified if it has values but no evidence struct.
            return "partially_verified", f"Unsupported/No evidence for field {field}"
            
    if not has_any_claims:
        # Nothing to verify
        return "unverified", "No factual claims present"
        
    return "verified", "All claims backed by source evidence"

def verify_all():
    manifests = {}
    for mf in Path("rag/knowledge_sources").glob("*.json"):
        with open(mf, "r") as f:
            data = json.load(f)
            manifests[data.get("source_id", "")] = data
    for mf in Path("rag/knowledge_sources/states").glob("*.json"):
        with open(mf, "r") as f:
            data = json.load(f)
            source_id = "states/" + data.get("state").lower().replace(" ", "_")
            manifests[source_id] = data
            
    extracted_texts = {}
    for source_id in manifests.keys():
        sdir = Path("rag/raw_sources") / source_id
        if sdir.exists():
            # Get latest timestamp
            subdirs = sorted([d for d in sdir.iterdir() if d.is_dir()])
            if subdirs:
                ext_file = subdirs[-1] / "extracted.txt"
                if ext_file.exists():
                    with open(ext_file, "r", encoding="utf-8") as f:
                        extracted_texts[source_id] = f.read()

    kb_dir = Path("rag/knowledge_base_verified")
    
    report = {
        "total_sources": len(manifests),
        "fetched": sum(1 for m in manifests.values() if m.get("status") == "fetched" or m.get("acquisition_status") == "fetched"),
        "failed": sum(1 for m in manifests.values() if m.get("status") == "failed" or m.get("acquisition_status") == "failed"),
        "pending": sum(1 for m in manifests.values() if m.get("status") == "pending" or m.get("acquisition_status") == "pending"),
        "review_required": sum(1 for m in manifests.values() if m.get("status") == "review_required" or m.get("acquisition_status") == "review_required"),
        "verified": 0,
        "partially_verified": 0,
        "unverified": 0,
        "HTTP failures": sum(1 for m in manifests.values() if m.get("status") == "failed" or m.get("acquisition_status") == "failed"),
        "missing_evidence": 0,
        "unsupported_claims": 0
    }
    
    for kb_file in kb_dir.rglob("*.json"):
        status, reason = verify_record(kb_file, manifests, extracted_texts)
        
        with open(kb_file, "r", encoding="utf-8") as f:
            record = json.load(f)
            
        record["source"]["verification_status"] = status
        
        with open(kb_file, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=4)
            
        if status == "verified":
            report["verified"] += 1
        elif status == "partially_verified":
            report["partially_verified"] += 1
            if "Unsupported" in reason:
                report["unsupported_claims"] += 1
            else:
                report["missing_evidence"] += 1
        else:
            report["unverified"] += 1
            
    with open("reports/source_acquisition_report.json", "w") as f:
        json.dump(report, f, indent=4)
        
    print("Verification complete.")
    for k, v in report.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    verify_all()
