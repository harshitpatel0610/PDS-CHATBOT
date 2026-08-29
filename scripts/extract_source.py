import os
import json
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

def extract_text_from_html(html_bytes):
    if not BeautifulSoup:
        return html_bytes.decode('utf-8', errors='ignore')
    
    soup = BeautifulSoup(html_bytes, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style", "noscript", "meta", "link", "header", "footer"]):
        script.decompose()

    # We want to preserve structure somewhat
    # Standard get_text() does a decent job if we use a separator
    return soup.get_text(separator='\n', strip=True)

def extract_source(snapshot_dir):
    snapshot_dir = Path(snapshot_dir)
    metadata_file = snapshot_dir / "metadata.json"
    
    if not metadata_file.exists():
        print(f"No metadata found in {snapshot_dir}")
        return
        
    with open(metadata_file, "r") as f:
        meta = json.load(f)
        
    content_type = meta.get("content_type", "")
    
    html_file = snapshot_dir / "source.html"
    pdf_file = snapshot_dir / "source.pdf"
    
    extracted_text = ""
    
    if html_file.exists():
        with open(html_file, "rb") as f:
            html_bytes = f.read()
        extracted_text = extract_text_from_html(html_bytes)
    elif pdf_file.exists():
        extracted_text = "[PDF Extraction Placeholder - Requires PyPDF2 or similar to preserve headings/tables]"
    else:
        print("No source file found.")
        return

    out_file = snapshot_dir / "extracted.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(extracted_text)
        
    print(f"Extracted {len(extracted_text)} characters to {out_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        extract_source(sys.argv[1])
    else:
        print("Usage: python extract_source.py <snapshot_dir>")
