import json
import os
import hashlib
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

RAW_SOURCES_DIR = Path("rag/raw_sources/states")

# Deep source candidates
CANDIDATES = [
    {
        "state": "Bihar",
        "title": "Bihar RCMS Guidelines",
        "url": "http://epds.bihar.gov.in/Circulars.htm",
        "source_type": "official_government",
        "parent_portal": "http://epds.bihar.gov.in/"
    },
    {
        "state": "Uttar Pradesh",
        "title": "UP FCS Important Documents",
        "url": "https://fcs.up.gov.in/ImportantDocuments.aspx",
        "source_type": "official_government",
        "parent_portal": "https://fcs.up.gov.in/"
    },
    {
        "state": "Gujarat",
        "title": "Gujarat DCS Ration Card Rules",
        "url": "https://dcs-dof.gujarat.gov.in/ration-card.htm",
        "source_type": "official_government",
        "parent_portal": "https://dcs-dof.gujarat.gov.in/"
    }
]

def extract_text_from_html(html_bytes):
    if not BeautifulSoup:
        return html_bytes.decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html_bytes, 'html.parser')
    for script in soup(["script", "style", "noscript", "meta", "link", "header", "footer"]):
        script.decompose()
    return soup.get_text(separator='\n', strip=True)

def run_discovery():
    discovery_report = {
        "states_analyzed": 3,
        "sources_discovered": len(CANDIDATES),
        "sources_accepted": 0,
        "sources_rejected": 0,
        "html_sources": 0,
        "pdf_sources": 0,
        "application_sources": 0,
        "document_sources": 0,
        "fee_sources": 0,
        "processing_time_sources": 0,
        "evidence_bearing_sources": 0,
        "states_with_insufficient_evidence": 0,
        "total_evidence_claims_discovered": 0
    }
    
    evidence_inventory = []
    
    for candidate in CANDIDATES:
        state_slug = candidate["state"].lower().replace(" ", "_")
        url = candidate["url"]
        
        # Verify it's official government
        if ".gov.in" not in url and ".nic.in" not in url:
            candidate["discovery_status"] = "rejected"
            candidate["reason"] = "Not an official government domain"
            discovery_report["sources_rejected"] += 1
            continue
            
        candidate["discovery_status"] = "validated"
        discovery_report["sources_accepted"] += 1
        
        # Fetch
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out_dir = RAW_SOURCES_DIR / state_slug / timestamp
        out_dir.mkdir(parents=True, exist_ok=True)
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 PDSKnowledgeBot/1.0'})
        raw_content = b""
        http_status = 0
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                http_status = response.getcode()
                content_type = response.headers.get('Content-Type', '')
                raw_content = response.read()
        except Exception as e:
            pass
            
        if raw_content and http_status == 200:
            sha256 = hashlib.sha256(raw_content).hexdigest()
            ext = ".pdf" if "pdf" in content_type.lower() else ".html"
            
            if ext == ".pdf":
                discovery_report["pdf_sources"] += 1
                extracted_text = "[PDF Content]"
            else:
                discovery_report["html_sources"] += 1
                extracted_text = extract_text_from_html(raw_content)
                
            content_path = out_dir / f"deep_source{ext}"
            with open(content_path, "wb") as f:
                f.write(raw_content)
                
            with open(out_dir / "extracted_deep.txt", "w", encoding="utf-8") as f:
                f.write(extracted_text)
                
            # Naive classification and evidence extraction
            lines = extracted_text.split("\n")
            has_evidence = False
            
            for line in lines:
                l = line.lower()
                if "processing time" in l or "days" in l:
                    discovery_report["processing_time_sources"] = 1
                    evidence_inventory.append({
                        "state": candidate["state"],
                        "intent": "ration_card_apply",
                        "field": "processing_time",
                        "claim": line.strip(),
                        "source_url": url,
                        "source_file": str(content_path),
                        "evidence_quote": line.strip(),
                        "evidence_status": "supported"
                    })
                    has_evidence = True
                    discovery_report["total_evidence_claims_discovered"] += 1
                    break
                    
            if has_evidence:
                discovery_report["evidence_bearing_sources"] += 1
        else:
            # Failed to fetch or not 200
            pass

    # Check states with insufficient evidence
    states_with_evidence = set(e["state"] for e in evidence_inventory if e["evidence_status"] == "supported")
    discovery_report["states_with_insufficient_evidence"] = discovery_report["states_analyzed"] - len(states_with_evidence)
    
    Path("reports").mkdir(parents=True, exist_ok=True)
    with open("reports/phase13d_source_discovery_report.json", "w", encoding="utf-8") as f:
        json.dump(discovery_report, f, indent=4)
        
    with open("reports/phase13d_evidence_inventory.json", "w", encoding="utf-8") as f:
        json.dump(evidence_inventory, f, indent=4)

if __name__ == "__main__":
    run_discovery()
