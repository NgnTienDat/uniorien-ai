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
