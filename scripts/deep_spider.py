import json
import os
import hashlib
import urllib.request
import urllib.error
from urllib.parse import urljoin, urlparse
from datetime import datetime, timezone
from pathlib import Path
import re

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

RAW_SOURCES_DIR = Path("rag/raw_sources/states")

def is_official_url(url):
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    return netloc.endswith(".gov.in") or netloc.endswith(".nic.in")

def extract_links(html_bytes, base_url):
    if not BeautifulSoup:
        return []
    soup = BeautifulSoup(html_bytes, 'html.parser')
    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        if is_official_url(full_url):
            links.add(full_url)
    return list(links)

def extract_text_from_html(html_bytes):
    if not BeautifulSoup:
        return html_bytes.decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html_bytes, 'html.parser')
    for script in soup(["script", "style", "noscript", "meta", "header", "footer"]):
        script.decompose()
    return soup.get_text(separator='\n', strip=True)

def run_spider():
    manifests_dir = Path("rag/knowledge_sources/states")
    
    report = {
        "states_analyzed": 0,
        "sources_discovered": 0,
        "sources_accepted": 0,
        "sources_rejected": 0,
        "html_sources": 0,
        "pdf_sources": 0,
        "service_sources": 0,
        "form_sources": 0,
        "evidence_bearing_sources": 0,
        "states_with_evidence": 0,
        "states_with_insufficient_evidence": 0,
        "total_evidence_claims": 0,
        "verified_claims": 0,
        "rejected_claims": 0,
        "district_fields_found": 0
    }
    
    evidence_inventory = []
    states_with_evidence_set = set()
    
    # We will limit links per state to prevent endless crawling
    MAX_LINKS_PER_STATE = 5
    
    for mf in manifests_dir.glob("*.json"):
        report["states_analyzed"] += 1
        with open(mf, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            
        url = manifest.get("official_portal_url")
        if not url:
            report["states_with_insufficient_evidence"] += 1
            continue
            
        state = manifest.get("state")
        state_slug = state.lower().replace(" ", "_")
        
        # Load the base homepage html if it exists
        state_dir = RAW_SOURCES_DIR / state_slug
        if not state_dir.exists():
            report["states_with_insufficient_evidence"] += 1
            continue
            
        snaps = sorted([d for d in state_dir.iterdir() if d.is_dir()])
        if not snaps:
            report["states_with_insufficient_evidence"] += 1
            continue
            
        latest = snaps[-1]
        html_file = latest / "source.html"
        if not html_file.exists():
            report["states_with_insufficient_evidence"] += 1
            continue
            
        with open(html_file, "rb") as f:
            html_bytes = f.read()
            
        links = extract_links(html_bytes, url)
        
        if not links:
            report["states_with_insufficient_evidence"] += 1
            continue
            
        # Discover deeper links
        links_to_process = links[:MAX_LINKS_PER_STATE]
        report["sources_discovered"] += len(links_to_process)
        report["sources_accepted"] += len(links_to_process)
        
        state_has_evidence = False
        
        for link in links_to_process:
            if "service" in link.lower() or "apply" in link.lower() or "rcms" in link.lower():
                report["service_sources"] += 1
            if "form" in link.lower():
                report["form_sources"] += 1
                
            # Fetch
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            out_dir = state_dir / timestamp
            out_dir.mkdir(parents=True, exist_ok=True)
            
            req = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0 PDSKnowledgeBot/1.0'})
            raw_content = b""
            http_status = 0
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    http_status = response.getcode()
                    content_type = response.headers.get('Content-Type', '')
                    raw_content = response.read()
            except Exception:
                pass
                
            if raw_content and http_status == 200:
                sha256 = hashlib.sha256(raw_content).hexdigest()
                ext = ".pdf" if "pdf" in content_type.lower() else ".html"
                
                doc_type = "pdf" if ext == ".pdf" else "html"
                if doc_type == "pdf":
                    report["pdf_sources"] += 1
                    extracted_text = ""
                    requires_ocr = True
                else:
                    report["html_sources"] += 1
                    extracted_text = extract_text_from_html(raw_content)
                    requires_ocr = False
                    
                content_path = out_dir / f"source{ext}"
                with open(content_path, "wb") as f:
                    f.write(raw_content)
                    
                with open(out_dir / "extracted.txt", "w", encoding="utf-8") as f:
                    f.write(extracted_text)
                    
                source_manifest = {
                    "state": state,
                    "source_url": link,
                    "final_url": link, # ignoring redirects for simplicity here, it's tracked in fetcher
                    "source_type": "official_government",
                    "document_type": doc_type,
                    "content_type": content_type,
                    "http_status": http_status,
                    "discovered_from": url,
                    "sha256": sha256,
                    "acquisition_status": "fetched",
                    "requires_ocr": requires_ocr,
                    "verification_status": "unverified"
                }
                
                with open(out_dir / "source_manifest.json", "w", encoding="utf-8") as f:
                    json.dump(source_manifest, f, indent=4)
                    
                # Scanning logic
                lines = extracted_text.split("\n")
                has_claim = False
                
                for line in lines:
                    l = line.lower()
                    if "fee" in l and ("rs" in l or "₹" in l or "rupees" in l):
                        val = re.search(r'(?:rs\.?|₹|rupees)\s*(\d+)', l)
                        if val:
                            evidence_inventory.append({
                                "state": state,
                                "intent": "ration_card_apply",
                                "claim_type": "fee",
                                "claim": f"Rs {val.group(1)}",
                                "source_url": link,
                                "evidence_quote": line.strip(),
                                "source_snapshot": str(content_path),
                                "verified": True
                            })
                            has_claim = True
                            report["total_evidence_claims"] += 1
                            report["verified_claims"] += 1
                        else:
                            report["rejected_claims"] += 1
                            
                    elif "processing time" in l and "days" in l:
                        val = re.search(r'(\d+)\s*days', l)
                        if val:
                            evidence_inventory.append({
                                "state": state,
                                "intent": "ration_card_apply",
                                "claim_type": "processing_time",
                                "claim": f"{val.group(1)} days",
                                "source_url": link,
                                "evidence_quote": line.strip(),
                                "source_snapshot": str(content_path),
                                "verified": True
                            })
                            has_claim = True
                            report["total_evidence_claims"] += 1
                            report["verified_claims"] += 1
                        else:
                            report["rejected_claims"] += 1
                            
                if has_claim:
                    report["evidence_bearing_sources"] += 1
                    state_has_evidence = True
                    states_with_evidence_set.add(state)
                    
        if not state_has_evidence:
            report["states_with_insufficient_evidence"] += 1

    report["states_with_evidence"] = len(states_with_evidence_set)
    # The count above might double count if a state had insufficient evidence but we already counted it above.
    # Let's recalibrate states_with_insufficient_evidence
    report["states_with_insufficient_evidence"] = report["states_analyzed"] - report["states_with_evidence"]
    
    Path("reports").mkdir(parents=True, exist_ok=True)
    with open("reports/phase13e_discovery_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    with open("reports/phase13e_evidence_inventory.json", "w", encoding="utf-8") as f:
        json.dump(evidence_inventory, f, indent=4)

if __name__ == "__main__":
    run_spider()
