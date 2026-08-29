import json
import os
import hashlib
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

RAW_SOURCES_DIR = Path("rag/raw_sources")

def fetch_source(manifest_path):
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Support generic and state manifest formats
    source_id = manifest.get("source_id")
    if not source_id and manifest.get("state"):
        source_id = "states/" + manifest.get("state").lower().replace(" ", "_")
        
    url = manifest.get("url")
    if not url:
        url = manifest.get("official_portal_url")
        
    status_key = "status" if "status" in manifest else "acquisition_status"
    
    if not source_id or not url:
        # pending or no URL
        if manifest.get(status_key) == "pending":
            return False
        print(f"Invalid manifest: {manifest_path}")
        return False

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = RAW_SOURCES_DIR / source_id / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    
    metadata = {
        "source_id": source_id,
        "requested_url": url,
        "final_url": None,
        "retrieved_at": timestamp,
        "http_status": None,
        "sha256": None,
        "content_type": None,
        "error": None
    }
    
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 PDSKnowledgeBot/1.0'}
    )
    
    raw_content = b""
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            metadata["http_status"] = response.getcode()
            metadata["final_url"] = response.geturl()
            metadata["content_type"] = response.headers.get('Content-Type', '')
            raw_content = response.read()
            manifest[status_key] = "fetched"
            manifest["accessed_at"] = timestamp
    except urllib.error.HTTPError as e:
        metadata["http_status"] = e.code
        metadata["error"] = str(e)
        manifest[status_key] = "failed"
    except urllib.error.URLError as e:
        metadata["http_status"] = 0
        metadata["error"] = str(e.reason)
        manifest[status_key] = "failed"
    except Exception as e:
        metadata["http_status"] = 0
        metadata["error"] = str(e)
        manifest[status_key] = "failed"

    if raw_content:
        metadata["sha256"] = hashlib.sha256(raw_content).hexdigest()
        ext = ".pdf" if "pdf" in (metadata["content_type"] or "").lower() else ".html"
        content_path = out_dir / f"source{ext}"
        with open(content_path, "wb") as f:
            f.write(raw_content)
    
    with open(out_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
        
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
        
    print(f"[{manifest[status_key].upper()}] {source_id} -> {metadata['http_status']}")
    return manifest[status_key] == "fetched"

def main():
    manifests_dir = Path("rag/knowledge_sources")
    # Fetch generic manifests
    for mf in manifests_dir.glob("*.json"):
        fetch_source(mf)
    # Fetch state manifests
    for mf in (manifests_dir / "states").glob("*.json"):
        fetch_source(mf)

if __name__ == "__main__":
    main()
