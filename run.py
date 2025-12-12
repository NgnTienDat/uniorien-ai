import os
from dotenv import load_dotenv
load_dotenv()
from components.manager import (
    SQLDatabaseManager,
    EmbeddingManager,
    VectorDatabaseManager,
    GenerationManager,
)
from components.database.postgres_db import PostgresDatabase
from components.embedding.sentence_transformer_embedder import SentenceTransformerEmbedder
from components.generation.openai_generator import OpenAIGenerator
from components.generation.ollama_generator import OllamaGenerator
from components.database.chroma_db import ChromaDB

from services.ingestion.ingestion_service import IngestionService
from services.ingestion.sources.postgres_comments_source import PostgresCommentsSource
from services.ingestion.sources.postgres_information_source import PostgresInformationSource
from services.rag.rag_service import RAGService

if __name__ == "__main__":

    primary_llm_model = OpenAIGenerator()
    ollama_model = OllamaGenerator()
    GenerationManager.instance().configure(primary=primary_llm_model, fallback=ollama_model)

    embedder = SentenceTransformerEmbedder(
            model_name="AITeamVN/Vietnamese_Embedding"
        )
    EmbeddingManager.instance().configure(embedder)

    vector_db = ChromaDB()
    VectorDatabaseManager.instance().configure(vector_db)

    rag_service = RAGService(top_k=3)
    question = "Trường Đại học Bách Khoa Hà Nội thành lập năm bao nhiêu?"
    response = rag_service.query(question)
    print("Question:", question)
    print("Answer:", response.answer)
    # print(response.debug_context())



    # # 1. Configure SQL Database
    # db_uri = "postgresql://uniorien_chatbot_readonly:Tiendat964@localhost:5432/uniorien"
    # sql_db = PostgresDatabase(db_uri=db_uri)
    # SQLDatabaseManager.instance().configure(sql_db)
    #
    # # 2. Configure Embedding Manager
    # embedder = SentenceTransformerEmbedder(
    #     model_name="AITeamVN/Vietnamese_Embedding"
    # )
    # EmbeddingManager.instance().configure(embedder)
    #
    # # 3. Configure Chroma Vector DB (bạn tự tạo chroma_db.py theo interface)
    # vector_db = ChromaDB()
    # VectorDatabaseManager.instance().configure(vector_db)
    #
    # # 4. Chạy ingestion
    # ingestion = IngestionService()
    # sources = [
    #     PostgresCommentsSource(),
    #     PostgresInformationSource(),
    #     # PostgresNewsSource(),
    # ]
    # ingestion.ingest_sources(sources)






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
