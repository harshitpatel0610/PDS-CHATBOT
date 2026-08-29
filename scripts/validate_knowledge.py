import json
import os
from pathlib import Path

def validate():
    kb_dir = Path("rag/knowledge_base_verified")
    
    total = 0
    valid = 0
    invalid = 0
    verified = 0
    partially_verified = 0
    unverified = 0
    missing_provenance = 0
    missing_url = 0
    nullable_violations = 0
    
    REQUIRED_FIELDS = [
        "id", "intent", "category", "state", "card_type",
        "facts", "process", "required_documents", "fees",
        "processing_time", "online", "offline", "source"
    ]
    
    VALID_STATUSES = ["verified", "partially_verified", "unverified"]
    VALID_SOURCE_TYPES = ["official_government", "official_partner", "unknown"]
    
    errors = []
    
    if not kb_dir.exists():
        print("Directory does not exist.")
        return

    for file_path in kb_dir.rglob("*.json"):
        total += 1
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                invalid += 1
                errors.append(f"{file_path}: Invalid JSON")
                continue
                
        is_valid = True
        
        # 1. Required fields
        for field in REQUIRED_FIELDS:
            if field not in data:
                is_valid = False
                errors.append(f"{file_path}: Missing required field '{field}'")
                
        if not is_valid:
            invalid += 1
            continue
            
        # 2. Provenance presence
        source = data.get("source", {})
        if not isinstance(source, dict):
            is_valid = False
            missing_provenance += 1
            errors.append(f"{file_path}: 'source' must be an object")
        else:
            # 3. Source URL
            url = source.get("url")
            if not url or not isinstance(url, str) or not url.startswith("http"):
                is_valid = False
                missing_url += 1
                errors.append(f"{file_path}: Missing or invalid source URL")
                
            # 4. Valid status and source_type
            status = source.get("verification_status")
            if status not in VALID_STATUSES:
                is_valid = False
                errors.append(f"{file_path}: Invalid verification_status '{status}'")
            
            source_type = source.get("source_type")
            if source_type not in VALID_SOURCE_TYPES:
                is_valid = False
                errors.append(f"{file_path}: Invalid source_type '{source_type}'")
                
            if status == "verified":
                verified += 1
            elif status == "partially_verified":
                partially_verified += 1
            elif status == "unverified":
                unverified += 1
                
        # Count nullable fields correctly used (set to null)
        nullables_used = 0
        for field in ["fees", "processing_time", "online", "offline"]:
            if data.get(field) is None:
                nullables_used += 1
        nullable_violations += nullables_used 
        
        if is_valid:
            valid += 1
        else:
            invalid += 1

    report = {
        "Total records": total,
        "Valid records": valid,
        "Invalid records": invalid,
        "Verified records": verified,
        "Partially verified records": partially_verified,
        "Unverified records": unverified,
        "Missing provenance": missing_provenance,
        "Missing source URL": missing_url,
        "Nullable fields used instead of guessed values": nullable_violations,
        "Errors": errors
    }
    
    with open("reports/knowledge_validation_report.json", "w") as f:
        json.dump(report, f, indent=4)
        
    for k, v in report.items():
        if k != "Errors":
            print(f"{k}: {v}")

if __name__ == "__main__":
    validate()
