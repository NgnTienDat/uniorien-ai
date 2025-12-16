import os
from dotenv import load_dotenv

from components.generation.openai_generator import OpenAIGenerator
from components.generation.ollama_generator import OllamaGenerator

from components.database.chroma_db import ChromaDB
from components.database.postgres_db import PostgresDatabase
from components.embedding.sentence_transformer_embedder import SentenceTransformerEmbedder

from components.manager import SQLDatabaseManager, EmbeddingManager, VectorDatabaseManager, GenerationManager

load_dotenv()
from fastapi import FastAPI



from app.routes import router as chat_router


def create_app() -> FastAPI:
    uniorien_app = FastAPI(
        title="UniOrien AI",
        version="0.1.0",
    )

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

    uniorien_app.include_router(chat_router, prefix="/api")



    return uniorien_app


app = create_app()


















    # # 6. Debug output
    # print("===== SQL GENERATED =====")
    # print(result.sql)
    #
    # print("\n===== COLUMNS =====")
    # print(result.columns)
    #
    # print("\n===== ROW COUNT =====")
    # print(result.row_count())
    #
    # print("\n===== FIRST ROW =====")
    # print(result.first_row())


    # rag_service = RAGService(top_k=3)
    # response = rag_service.query(question)
    # print("Question:", question)
    # print("Answer:", response.answer)
    # print(response.debug_context())

    # include_tables = [
    #     "university",
    #     "admission_information",
    #     "university_information",
    #     "university_comments",
    #     "major",
    #     "major_for_group",
    #     "news",
    #     "benchmark",
    # ],

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






from components.manager import SQLDatabaseManager, EmbeddingManager, VectorDatabaseManager
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
