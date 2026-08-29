import json
from pathlib import Path
import sys

def validate_curated_knowledge(directory="rag/curated_knowledge/templates"):
    valid_count = 0
    invalid_count = 0
    
    for file_path in Path(directory).glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"[FAIL] {file_path.name}: Invalid JSON")
                invalid_count += 1
                continue
                
        errors = []
        
        # 1. State must exist
        if not data.get("state"):
            errors.append("Missing 'state'")
            
        # 2. District must NOT exist
        if "district" in data:
            errors.append("Forbidden field 'district' found")
            
        # 3. Sources validation
        source_ids = set()
        sources = data.get("sources", [])
        if not sources:
            errors.append("Missing 'sources' array")
            
        for idx, src in enumerate(sources):
            src_id = src.get("id")
            if not src_id:
                errors.append(f"Source at index {idx} missing 'id'")
            else:
                source_ids.add(src_id)
                
            url = src.get("url")
            if url:
                # Must be official
                if ".gov.in" not in url.lower() and ".nic.in" not in url.lower():
                    errors.append(f"Source {src_id} URL is not official (.gov.in/.nic.in)")
                    
        # 4. Data validation (Evidence linking)
        kb_data = data.get("data", {})
        for field in ["processing_time", "fees", "online_available", "offline_available", "application_url"]:
            val_obj = kb_data.get(field, {})
            if val_obj and val_obj.get("value") is not None:
                if not val_obj.get("source_id"):
                    errors.append(f"Field '{field}' has value but missing 'source_id'")
                elif val_obj.get("source_id") not in source_ids:
                    errors.append(f"Field '{field}' references unknown source_id '{val_obj.get('source_id')}'")
                    
                if not val_obj.get("evidence_quote"):
                    errors.append(f"Field '{field}' has value but missing 'evidence_quote'")
                    
        for idx, doc in enumerate(kb_data.get("required_documents", [])):
            if not doc.get("source_id"):
                errors.append(f"Document at index {idx} missing 'source_id'")
            elif doc.get("source_id") not in source_ids:
                errors.append(f"Document at index {idx} references unknown source_id")
            if not doc.get("evidence_quote"):
                errors.append(f"Document at index {idx} missing 'evidence_quote'")
                
        for idx, step in enumerate(kb_data.get("process_steps", [])):
            if not step.get("source_id"):
                errors.append(f"Process step at index {idx} missing 'source_id'")
            elif step.get("source_id") not in source_ids:
                errors.append(f"Process step at index {idx} references unknown source_id")
            if not step.get("evidence_quote"):
                errors.append(f"Process step at index {idx} missing 'evidence_quote'")
                
        if errors:
            print(f"[FAIL] {file_path.name}")
            for err in errors:
                print(f"  - {err}")
            invalid_count += 1
        else:
            print(f"[PASS] {file_path.name}")
            valid_count += 1
            
    print(f"\nTotal files: {valid_count + invalid_count}")
    print(f"Valid: {valid_count}")
    print(f"Invalid: {invalid_count}")
    
    if invalid_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    validate_curated_knowledge()
