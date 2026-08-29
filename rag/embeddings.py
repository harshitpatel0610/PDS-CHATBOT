from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-m3"


class EmbeddingService:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.model = None

    def initialize(self):
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)

    def embed_text(self, text: str) -> list[float]:
        """
        Convert a single text into a dense embedding vector.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")
            
        if self.model is None:
            self.initialize()

        embedding = self.model.encode(
            text,
            normalize_embeddings=True
        )

        return embedding.tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Convert multiple texts into dense embedding vectors.
        """
        if not texts:
            return []

        if any(not text or not text.strip() for text in texts):
            raise ValueError("Texts cannot contain empty values.")
            
        if self.model is None:
            self.initialize()

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        return embeddings.tolist()


embedding_service = EmbeddingService()