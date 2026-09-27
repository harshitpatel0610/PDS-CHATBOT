import chromadb
from rag.retriever import retriever
import sys

retriever.initialize()
intent = "documents_required"
state = "Gujarat"
card_type = "APL"

where_filter = {
    "$and": [
        {"intent": intent},
        {"state": state},
        {"card_type": card_type}
    ]
}

try:
    filtered = retriever.collection.get(where=where_filter, include=["metadatas"])
    print(f"Filtered count: {len(filtered['ids'])}")
    if len(filtered['ids']) > 0:
        res = retriever.collection.query(
            query_embeddings=[[0.0]*384], # dummy embedding
            n_results=1,
            where=where_filter
        )
        print("Query success!")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
