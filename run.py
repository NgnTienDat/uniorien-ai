import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from components.generation.openai_generator import OpenAIGenerator
from components.generation.ollama_generator import OllamaGenerator

from components.database.chroma_db import ChromaDB
from components.database.postgres_db import PostgresDatabase
from components.embedding.sentence_transformer_embedder import SentenceTransformerEmbedder

from components.manager import SQLDatabaseManager, EmbeddingManager, VectorDatabaseManager, GenerationManager


load_dotenv()
from fastapi import FastAPI



from app.chat_routes import router as chat_router
from app.ingestion_routes import router as ingestion_router


def initialize_app():
    primary_llm = OpenAIGenerator()
    fallback_llm = OllamaGenerator()
    GenerationManager.instance().configure(
        primary=primary_llm,
        fallback=fallback_llm,
    )

    embedder = SentenceTransformerEmbedder(
        model_name="AITeamVN/Vietnamese_Embedding"
    )
    EmbeddingManager.instance().configure(embedder)

    vector_db = ChromaDB()
    VectorDatabaseManager.instance().configure(vector_db)

    sql_db = PostgresDatabase(
        db_uri=os.getenv("DATABASE_URI")
    )
    SQLDatabaseManager.instance().configure(sql_db)


def create_app() -> FastAPI:
    uniorien_app = FastAPI(
        title="UniOrien AI",
        version="0.1.0",
    )

    uniorien_app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "x-admin-token"  # BẮT BUỘC phải có cái này để FE gửi được token
        ],
    )
    initialize_app()

    api_prefix = "/api/v1"

    uniorien_app.include_router(chat_router, prefix=api_prefix)
    uniorien_app.include_router(ingestion_router, prefix=api_prefix)


    return uniorien_app


app = create_app()

"""
    ENTER this command to run app: uvicorn run:app --reload
"""
