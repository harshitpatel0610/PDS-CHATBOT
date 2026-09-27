import chromadb
from rag.embeddings import embedding_service

VECTOR_DB_DIR = "rag/vector_store"
COLLECTION_NAME = "pds_knowledge"

class Retriever:
    def __init__(self, vector_db_dir: str = VECTOR_DB_DIR, collection_name: str = COLLECTION_NAME):
        self.vector_db_dir = vector_db_dir
        self.collection_name = collection_name
        self.client = None
        self.collection = None

    def initialize(self):
        if self.client is None:
            embedding_service.initialize()
            self.client = chromadb.PersistentClient(path=self.vector_db_dir)
            self.collection = self.client.get_or_create_collection(self.collection_name)

    def search(self, query: str, top_k: int = 5, intent: str = None, state: str = None, card_type: str = None):
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
        if self.collection is None:
            self.initialize()
        query_embedding = embedding_service.embed_text(query)

        # Map closely related intents to prevent strict metadata isolation from dropping relevant context.
        # e.g., documents required for applying are often stored in 'ration_card_apply' files.
        intent_mapping = {
            "documents_required": ["documents_required", "ration_card_apply", "ration_card_update", "ration_card_types"],
            "ration_card_apply": ["ration_card_apply", "documents_required"],
            "ration_card_update": ["ration_card_update", "documents_required"],
            "ration_card_types": ["ration_card_types", "documents_required"]
        }
        
        levels = []
        if intent:
            allowed_intents = intent_mapping.get(intent, [intent])
            
            if state and card_type:
                levels.append({
                    "name": "state_card_type_intent",
                    "filter": {
                        "$and": [
                            {"intent": {"$in": allowed_intents}},
                            {"state": state},
                            {"card_type": card_type}
                        ]
                    }
                })
            
            if state:
                # Include generic card types or matching card types
                levels.append({
                    "name": "state_intent",
                    "filter": {
                        "$and": [
                            {"intent": {"$in": allowed_intents}},
                            {"state": state}
                        ]
                    }
                })
                
                # Critical Fix: When user asks for a specific state, fallback should ONLY include
                # the requested state AND generic state (to avoid cross-state contamination).
                # We can't just drop the state filter.
                levels.append({
                    "name": "generic_intent_with_state_isolation",
                    "filter": {
                        "$and": [
                            {"intent": {"$in": allowed_intents}},
                            {"$or": [{"state": state}, {"state": "Generic"}]}
                        ]
                    }
                })
            else:
                # User did not specify a state, so any generic_intent is fine
                # Or we restrict to state="Generic" only so we don't accidentally return Gujarat for a generic question?
                # Actually, if they don't specify a state, returning Generic is safer than returning a random state.
                levels.append({
                    "name": "generic_intent",
                    "filter": {
                        "$and": [
                            {"intent": {"$in": allowed_intents}},
                            {"state": "Generic"}
                        ]
                    }
                })
                
        # If we still haven't found anything, we can use semantic_fallback
        # BUT again, we must restrict by state to avoid cross-state contamination.
        if state:
            levels.append({
                "name": "semantic_fallback_with_state_isolation",
                "filter": {
                    "$or": [{"state": state}, {"state": "Generic"}]
                }
            })
        else:
            levels.append({
                "name": "semantic_fallback",
                "filter": {"state": "Generic"}
            })

        for level in levels:
            where_filter = level["filter"]
            try:
                if where_filter:
                    filtered = self.collection.get(where=where_filter, include=["metadatas"])
                    filtered_count = len(filtered["ids"])
                    if filtered_count > 0:
                        results = self.collection.query(
                            query_embeddings=[query_embedding],
                            n_results=min(top_k, filtered_count),
                            where=where_filter
                        )
                        results["retrieval_level"] = level["name"]
                        return results
            except Exception as e:
                # If ChromaDB throws an error on a specific filter structure, fallback gracefully
                continue

        # Ultimate fallback
        return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]], "retrieval_level": "none"}

retriever = Retriever()
