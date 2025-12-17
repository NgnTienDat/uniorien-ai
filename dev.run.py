import os
from dotenv import load_dotenv

from components.generation.openai_generator import OpenAIGenerator
from components.generation.ollama_generator import OllamaGenerator

from components.database.chroma_db import ChromaDB
from components.database.postgres_db import PostgresDatabase
from components.embedding.sentence_transformer_embedder import SentenceTransformerEmbedder

from components.manager import SQLDatabaseManager, EmbeddingManager, VectorDatabaseManager, GenerationManager
from services.ingestion.ingestion_service import IngestionService
from services.ingestion.sources.postgres_comments_source import PostgresCommentsSource
from services.ingestion.sources.postgres_information_source import PostgresInformationSource
from services.orchestrator.chat_orchestrator import ChatOrchestrator
from services.rag.rag_service import RAGService


load_dotenv()


# if __name__ == "__main__":
    # primary_llm = OpenAIGenerator()
    # fallback_llm = OllamaGenerator()
    # GenerationManager.instance().configure(
    #     primary=primary_llm,
    #     fallback=fallback_llm,
    # )
    #
    # embedder = SentenceTransformerEmbedder(
    #     model_name="AITeamVN/Vietnamese_Embedding"
    # )
    # EmbeddingManager.instance().configure(embedder)
    #
    # vector_db = ChromaDB()
    # VectorDatabaseManager.instance().configure(vector_db)
    #
    # sql_db = PostgresDatabase(
    #     db_uri=os.getenv("DATABASE_URI")
    # )
    # SQLDatabaseManager.instance().configure(sql_db)
#
#     orchestrator = ChatOrchestrator()
#     question = "Cho tôi một vài review, nhận xét về trường Đại học Kinh Tế Quốc Dân."
#     result = orchestrator.handle_query(question)

    # rag = RAGService(top_k=3)
    # result = rag.query(question)
    # print("Question:", question)
    # print("Answer:", result)

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



#==============Ingestion Script ==================
# if __name__ == "__main__":
#     primary_llm = OpenAIGenerator()
#     fallback_llm = OllamaGenerator()
#     GenerationManager.instance().configure(
#         primary=primary_llm,
#         fallback=fallback_llm,
#     )
#
#     embedder = SentenceTransformerEmbedder(
#         model_name="AITeamVN/Vietnamese_Embedding"
#     )
#     EmbeddingManager.instance().configure(embedder)
#
#     vector_db = ChromaDB()
#     VectorDatabaseManager.instance().configure(vector_db)
#
#     sql_db = PostgresDatabase(
#         db_uri=os.getenv("DATABASE_URI")
#     )
#     SQLDatabaseManager.instance().configure(sql_db)
#
#     # 4. Chạy ingestion
#     ingestion = IngestionService()
#     sources = [
#         PostgresCommentsSource(),
#         PostgresInformationSource(),
#         # PostgresNewsSource(),
#     ]
#     ingestion.ingest_sources(sources)


