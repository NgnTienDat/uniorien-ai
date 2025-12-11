import os
from components.manager import (
    SQLDatabaseManager,
    EmbeddingManager,
    VectorDatabaseManager,
)
from components.database.postgres_db import PostgresDatabase
from components.embedding.sentence_transformer_embedder import SentenceTransformerEmbedder
from components.database.chroma_db import ChromaDB

from services.ingestion.ingestion_service import IngestionService
from services.ingestion.sources.postgres_comments_source import PostgresCommentsSource
# from services.ingestion.sources.postgres_information_source import PostgresInformationSource
# from services.ingestion.sources.postgres_news_source import PostgresNewsSource


if __name__ == "__main__":
    # 1. Configure SQL Database
    db_uri = "postgresql://uniorien_chatbot_readonly:Tiendat964@localhost:5432/uniorien"
    sql_db = PostgresDatabase(db_uri=db_uri)
    SQLDatabaseManager.instance().configure(sql_db)

    # 2. Configure Embedding Manager
    embedder = SentenceTransformerEmbedder(
        model_name="AITeamVN/Vietnamese_Embedding"
    )
    EmbeddingManager.instance().configure(embedder)

    # 3. Configure Chroma Vector DB (bạn tự tạo chroma_db.py theo interface)
    vector_db = ChromaDB()
    VectorDatabaseManager.instance().configure(vector_db)

    # 4. Chạy ingestion
    ingestion = IngestionService()
    sources = [
        PostgresCommentsSource(),
        # PostgresInformationSource(),
        # PostgresNewsSource(),
    ]
    ingestion.ingest_sources(sources)











from components.manager import SQLDatabaseManager
from components.database.postgres_db import PostgresDatabase

from components.manager import GenerationManager
from components.generation.openai_generator import OpenAIGenerator
from components.generation.ollama_generator import OllamaGenerator


# def bootstrap_system():
#     db = PostgresDatabase(
#         db_uri="postgresql://user:pass@localhost:5432/uniorien",
#         include_tables=[
#             "university",
#             "admission_information",
#             "university_information",
#             "university_comments",
#             "major",
#             "major_for_group",
#             "news",
#             "benchmark",
#         ],
#     )
#
#     SQLDatabaseManager.instance().configure(db)
#





# def init_llm():
#     llm_main = OpenAIGenerator(model="gpt-4o-mini")
#     llm_fallback = OllamaGenerator(model="llama3.1:8b")
#
#     GenerationManager.instance().configure(
#         primary=llm_main,
#         fallback=llm_fallback
#     )
