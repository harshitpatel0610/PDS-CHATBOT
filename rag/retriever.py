import chromadb

from rag.embeddings import embedding_service


VECTOR_DB_DIR = "rag/vector_store"
COLLECTION_NAME = "pds_knowledge"


class Retriever:

    def __init__(
        self,
        vector_db_dir: str = VECTOR_DB_DIR,
        collection_name: str = COLLECTION_NAME
    ):
        self.vector_db_dir = vector_db_dir
        self.collection_name = collection_name
        self.client = None
        self.collection = None

    def initialize(self):
        if self.client is None:
            embedding_service.initialize()
            self.client = chromadb.PersistentClient(
                path=self.vector_db_dir
            )
            self.collection = self.client.get_or_create_collection(
                self.collection_name
            )

    def search(
        self,
        query: str,
        top_k: int = 5,
        intent: str = None,
        state: str = None,
        card_type: str = None
    ):
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
            
        if self.collection is None:
            self.initialize()

        query_embedding = embedding_service.embed_text(query)

        levels = []

        if intent:
            if state and card_type:
                levels.append({
                    "name": "state_card_type_intent",
                    "filter": {
                        "$and": [
                            {"intent": intent},
                            {"state": state},
                            {"card_type": card_type}
                        ]
                    }
                })
                
            if state:
                levels.append({
                    "name": "state_intent",
                    "filter": {
                        "$and": [
                            {"intent": intent},
                            {"state": state}
                        ]
                    }
                })
                
            levels.append({
                "name": "generic_intent",
                "filter": {"intent": intent}
            })

        levels.append({
            "name": "semantic_fallback",
            "filter": None
        })

        for level in levels:
            where_filter = level["filter"]
            
            try:
                if where_filter:
                    filtered = self.collection.get(
                        where=where_filter,
                        include=["metadatas"]
                    )
                    filtered_count = len(filtered["ids"])
                    if filtered_count > 0:
                        results = self.collection.query(
                            query_embeddings=[query_embedding],
                            n_results=min(top_k, filtered_count),
                            where=where_filter
                        )
                        results["retrieval_level"] = level["name"]
                        return results
                else:
                    results = self.collection.query(
                        query_embeddings=[query_embedding],
                        n_results=min(top_k, self.collection.count())
                    )
                    results["retrieval_level"] = level["name"]
                    return results
            except Exception as e:
                # If ChromaDB throws an error on a specific filter structure, fallback gracefully
                continue

        # Ultimate fallback
        return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]], "retrieval_level": "none"}

retriever = Retriever()