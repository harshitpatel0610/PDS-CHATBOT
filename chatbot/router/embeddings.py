import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .models import RouteResult

# -----------------------------
# Load model once
# -----------------------------
MODEL = SentenceTransformer("BAAI/bge-m3")

DATA_DIR = Path(__file__).parent / "data"

# -----------------------------
# Load intents
# -----------------------------
with open(DATA_DIR / "pds_intents.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    PDS_INTENTS = data["intents"]
    
    print(">>> PDS INTENTS LOADED:", len(PDS_INTENTS))

    for intent in PDS_INTENTS:
        if intent["intent"] in [
            "ration_card_apply",
            "ration_card_online_offline"
        ]:
            print(
                ">>>",
                intent["intent"],
                "| priority =", intent.get("priority"),
                "| patterns =", len(intent.get("patterns", [])),
                "| examples =", len(intent.get("examples", [])),
                "| keywords =", len(intent.get("keywords", []))
            )

# -----------------------------
# Build one embedding per intent
# -----------------------------
pattern_embeddings = []

for intent in PDS_INTENTS:
    texts = intent["patterns"] + intent.get("examples", [])
    if not texts:
        continue

    # Batch encode all texts for this intent
    embeddings = MODEL.encode(
        texts,
        normalize_embeddings=True
    )

    for text, embedding in zip(texts, embeddings):
        pattern_embeddings.append(
            {
                "intent": intent["intent"],
                "text": text,
                "embedding": embedding
            }
        )

def classify_by_embeddings(query: str) -> RouteResult:

    query_embedding = MODEL.encode(
        query,
        normalize_embeddings=True
    )

    best_intent = None
    best_similarity = -1.0
    best_item = None
    
    for item in pattern_embeddings:

        similarity = cosine_similarity(
            [query_embedding],
            [item["embedding"]]
        )[0][0]

        if similarity > best_similarity:

            best_similarity = similarity
            best_intent = item["intent"]
            best_item = item

    #if best_item:
        #print(f"Matched Text : {best_item['text']}")
    
    
    EMBEDDING_THRESHOLD = 0.50

    return RouteResult(
    is_pds=best_similarity >= EMBEDDING_THRESHOLD,
    intent=best_intent if best_similarity >= EMBEDDING_THRESHOLD else None,
    confidence=float(best_similarity)
)