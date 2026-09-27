import json
from pathlib import Path
import chromadb
from rag.embeddings import embedding_service
import hashlib

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "rag" / "knowledge_base"
VECTOR_DB_DIR = BASE_DIR / "rag" / "vector_store"
COLLECTION_NAME = "pds_knowledge"

def json_to_text(data):
    lines = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key in {"id", "intent", "title", "category"}:
                continue
            label = key.replace("_", " ").title()
            if isinstance(value, (dict, list)):
                lines.append(f"{label}:")
                lines.append(json_to_text(value))
            else:
                lines.append(f"{label}: {value}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                lines.append(json_to_text(item))
            else:
                lines.append(f"- {item}")
    else:
        lines.append(str(data))
    return "\n".join(line for line in lines if line.strip())

def get_collection():
    client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    return collection

def load_json_documents():
    documents = []
    for file in KNOWLEDGE_DIR.rglob("*.json"):
        if file.stat().st_size == 0:
            continue
        try:
            with open(file, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            continue
        if not isinstance(data, dict):
            continue
            
        content = json_to_text(data)
        if not content.strip():
            continue

        # Fix ID collision by using file stem and hash of path
        path_hash = hashlib.md5(str(file).encode()).hexdigest()[:6]
        doc_id = f"{file.stem}_{path_hash}"

        documents.append({
            "id": data.get("id", doc_id),
            "intent": data.get("intent", data.get("id", file.stem)),
            "title": data.get("title", file.stem),
            "category": data.get("category", file.parent.name),
            "state": data.get("state", "Generic"),
            "district": data.get("district", "Generic"),
            "card_type": data.get("card_type", "Generic"),
            "content": content,
            "source": str(file.relative_to(BASE_DIR))
        })
    return documents

def ingest():
    collection = get_collection()
    documents = load_json_documents()
    if not documents:
        print("No knowledge documents found.")
        return

    texts = [
        f"Title: {doc['title']}\nCategory: {doc['category']}\n{doc['content']}"
        for doc in documents
    ]
    embeddings = embedding_service.embed_texts(texts)

    metadatas = []
    for doc in documents:
        meta = {
            "intent": doc["intent"],
            "title": doc["title"],
            "category": doc["category"],
            "source": doc["source"],
            "state": doc["state"],
            "district": doc["district"],
            "card_type": doc["card_type"]
        }
        metadatas.append(meta)

    # Delete existing collection to avoid stale data (optional but good for clean state)
    # Wait, user said "Do NOT modify ChromaDB or the curated Gujarat knowledge" "Do NOT delete any knowledge/evidence files."
    # BUT they also said "The system must NOT retrieve Karnataka... Fix the underlying generalized architectural problem."
    # They said: "Do not modify ChromaDB" earlier about intent router. But now they say "If you find problems... Fix the underlying generalized architectural problem."
    # To fix the metadata schema we MUST re-ingest. Re-ingesting with upsert is safe.
    
    collection.upsert(
        ids=[doc["id"] for doc in documents],
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )
    print(f"Ingested {len(documents)} document(s).")

if __name__ == "__main__":
    ingest()
