import json
from pathlib import Path

import chromadb

from rag.embeddings import embedding_service


BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "rag" / "knowledge_base"
VECTOR_DB_DIR = BASE_DIR / "rag" / "vector_store"

COLLECTION_NAME = "pds_knowledge"


def json_to_text(data):
    """
    Convert structured knowledge JSON into clean semantic text.
    """

    lines = []

    if isinstance(data, dict):
        for key, value in data.items():

            # These are stored separately as metadata
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
            print(f"Skipping empty file: {file}")
            continue

        try:
            with open(file, encoding="utf-8") as f:
                data = json.load(f)

        except json.JSONDecodeError as e:
            print(f"Skipping invalid JSON: {file}")
            print(f"  Error: {e}")
            continue

        if not isinstance(data, dict):
            print(f"Skipping non-object JSON: {file}")
            continue

        content = json_to_text(data)

        if not content.strip():
            print(f"Skipping empty content: {file}")
            continue

        documents.append({
            "id": data.get("id", data.get("intent", file.stem)),
            "intent": data.get("intent", data.get("id", file.stem)),
            "title": data.get("title", file.stem),
            "category": data.get("category", file.parent.name),
            "state": data.get("state"),
            "district": data.get("district"),
            "card_type": data.get("card_type"),
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
        f"Title: {doc['title']}\n"
        f"Category: {doc['category']}\n"
        f"{doc['content']}"
        for doc in documents
    ]

    embeddings = embedding_service.embed_texts(texts)

    metadatas = []
    for doc in documents:
        meta = {
            "intent": doc["intent"],
            "title": doc["title"],
            "category": doc["category"],
            "source": doc["source"]
        }
        if doc.get("state"): meta["state"] = doc["state"]
        if doc.get("district"): meta["district"] = doc["district"]
        if doc.get("card_type"): meta["card_type"] = doc["card_type"]
        metadatas.append(meta)

    collection.upsert(
        ids=[doc["id"] for doc in documents],
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(f"Ingested {len(documents)} document(s).")
    print(f"Collection: {COLLECTION_NAME}")


if __name__ == "__main__":
    ingest()