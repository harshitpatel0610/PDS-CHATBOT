import json
import os
from pathlib import Path
import chromadb
from rag.retriever import retriever
from rag.embeddings import embedding_service

def validate_record(data):
    if not data.get("state"):
        return False, "Missing state"
    if "district" in data:
        return False, "Contains district field"
    sources = data.get("sources", [])
    if not sources:
        return False, "Missing sources"
        
    source_ids = {s["id"] for s in sources if s.get("id")}
    for s in sources:
        url = s.get("url")
        if url and (".gov.in" not in url.lower() and ".nic.in" not in url.lower()):
            return False, "Non-official source URL"
            
    v_status = data.get("verification_status")
    if v_status in ["pending_manual_entry", "unverified"]:
        return False, f"Status is {v_status}"
        
    kb_data = data.get("data", {})
    verified_claims_count = 0
    for field in ["processing_time", "fees", "online_available", "offline_available", "application_url"]:
        v = kb_data.get(field, {})
        if v and v.get("value") is not None:
            if not v.get("source_id") or v.get("source_id") not in source_ids:
                return False, f"Invalid source_id in {field}"
            if not v.get("evidence_quote"):
                return False, f"Missing evidence_quote in {field}"
            verified_claims_count += 1
            
    for doc in kb_data.get("required_documents", []):
        if not doc.get("source_id") or not doc.get("evidence_quote"):
            return False, "Missing source_id/evidence in document"
        verified_claims_count += 1
        
    for step in kb_data.get("process_steps", []):
        if not step.get("source_id") or not step.get("evidence_quote"):
            return False, "Missing source_id/evidence in process step"
        verified_claims_count += 1
        
    if verified_claims_count == 0:
        return False, "No verified claims available"
        
    return True, "Valid", verified_claims_count

def build_document_text(data):
    state = data.get("state")
    intent = data.get("intent", "ration_card_apply")
    kb_data = data.get("data", {})
    
    # Extract official source URL for display
    source_urls = [s.get("url") for s in data.get("sources", []) if s.get("url")]
    source_url = source_urls[0] if source_urls else "Official Government Portal"
    
    text = f"State: {state}\nIntent: {intent}\n\n"
    
    val = kb_data.get("processing_time", {})
    if val and val.get("value") is not None:
        text += f"Processing Time: {val.get('value')}\nSource: {source_url}\nEvidence: {val.get('evidence_quote')}\n\n"
        
    val = kb_data.get("fees", {})
    if val and val.get("value") is not None:
        text += f"Fees: {val.get('value')}\nSource: {source_url}\nEvidence: {val.get('evidence_quote')}\n\n"
        
    val = kb_data.get("online_available", {})
    if val and val.get("value") is not None:
        text += f"Online application available: {'Yes' if val.get('value') else 'No'}\nSource: {source_url}\nEvidence: {val.get('evidence_quote')}\n\n"
        
    val = kb_data.get("offline_available", {})
    if val and val.get("value") is not None:
        text += f"Offline application available: {'Yes' if val.get('value') else 'No'}\nSource: {source_url}\nEvidence: {val.get('evidence_quote')}\n\n"
        
    val = kb_data.get("application_url", {})
    if val and val.get("value") is not None:
        text += f"Application portal: {val.get('value')}\nSource: {source_url}\nEvidence: {val.get('evidence_quote')}\n\n"
        
    docs = kb_data.get("required_documents", [])
    if docs:
        text += "Required Documents:\n"
        for d in docs:
            mandatory_str = "Mandatory" if d.get("is_mandatory") else "Optional"
            cond_str = f", Condition: {d.get('condition')}" if d.get("condition") else ""
            text += f"- {d.get('document_name')} [{mandatory_str}{cond_str}] (Evidence: {d.get('evidence_quote')})\n"
        text += f"Source: {source_url}\n\n"
            
    steps = kb_data.get("process_steps", [])
    if steps:
        text += "Process Steps:\n"
        for s in steps:
            text += f"{s.get('step_number')}. {s.get('description')} (Evidence: {s.get('evidence_quote')})\n"
        text += f"Source: {source_url}\n\n"
            
    return text.strip()

def run_ingestion():
    templates_dir = Path("rag/curated_knowledge/templates")
    
    report = {
        "eligible_records": 0,
        "inserted_records": 0,
        "updated_records": 0,
        "rejected_records": 0,
        "skipped_records": 0,
        "duplicate_records": 0,
        "district_fields_detected": 0,
        "verified_claims_ingested": 0,
        "unsupported_claims_ingested": 0,
        "retrieval_tests_passed": 0,
        "groundedness_tests_passed": 0,
        "regression_accuracy": 0,
        "status": "FAIL"
    }
    
    retriever.initialize()
    collection = retriever.collection
    
    existing_ids = set(collection.get()["ids"])
    
    docs_to_embed = []
    docs_metadata = []
    docs_ids = []
    
    for file_path in templates_dir.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if "district" in data:
            report["district_fields_detected"] += 1
            
        res = validate_record(data)
        if len(res) == 2:
            is_valid, reason = res
            verified_claims_count = 0
        else:
            is_valid, reason, verified_claims_count = res
            
        if not is_valid:
            print(f"[INGESTION REJECTED]\nFile: {file_path.name}\nReason: {reason}\n")
            if reason.startswith("Status is") or "No verified claims" in reason:
                report["skipped_records"] += 1
            else:
                report["rejected_records"] += 1
            continue
            
        report["eligible_records"] += 1
        report["verified_claims_ingested"] += verified_claims_count
        
        state = data.get("state")
        intent = data.get("intent", "ration_card_apply")
        card_type = data.get("card_type", "Generic")
        
        doc_id = f"{state}_{card_type}_{intent}".replace(" ", "_")
        doc_text = build_document_text(data)
        
        source_urls = [s.get("url") for s in data.get("sources", []) if s.get("url")]
        source_str = ", ".join(source_urls) if source_urls else "Official"
        
        metadata = {
            "state": state,
            "intent": intent,
            "card_type": card_type,
            "category": intent,
            "source": source_str
        }
        
        docs_to_embed.append(doc_text)
        docs_metadata.append(metadata)
        docs_ids.append(doc_id)
        
        if doc_id in existing_ids:
            report["updated_records"] += 1
            print(f"[UPDATED] {doc_id}")
        else:
            report["inserted_records"] += 1
            print(f"[INSERTED] {doc_id}")
            
    if docs_ids:
        embeddings = embedding_service.embed_texts(docs_to_embed)
        collection.upsert(
            ids=docs_ids,
            embeddings=embeddings,
            documents=docs_to_embed,
            metadatas=docs_metadata
        )
    else:
        print("Pipeline ready; no verified records available for production ingestion.")
        
    Path("reports").mkdir(parents=True, exist_ok=True)
    with open("reports/phase16b_production_ingestion_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

if __name__ == "__main__":
    run_ingestion()
