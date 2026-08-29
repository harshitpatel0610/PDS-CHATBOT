from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chatbot.api.routes import router

from contextlib import asynccontextmanager
from rag.retriever import retriever
import time

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize heavy RAG dependencies on startup
    print(">>> Initializing heavy dependencies...")
    t0 = time.perf_counter()
    retriever.initialize()
    t_total = (time.perf_counter() - t0) * 1000
    print(f">>> Initialization complete in {t_total:.2f} ms")
    yield
    print(">>> Shutting down...")

app = FastAPI(
    title="PDS AI Assistant",
    version="1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)