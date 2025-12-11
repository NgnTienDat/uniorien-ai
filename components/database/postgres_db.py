import psycopg2
import psycopg2.extras
from components.interfaces import ISQLDatabase


class PostgresDatabase(ISQLDatabase):
    def __init__(self, db_uri: str, include_tables=None):
        self.db_uri = db_uri

    def _get_conn(self):
        return psycopg2.connect(self.db_uri)

    def run(self, query: str):
        """
        Trả về list[dict] thay vì string table.
        Đây là lựa chọn A2 – sạch, dễ dùng, không cần parse.
        """
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query)
                return cur.fetchall()  # list[dict]
        finally:
            conn.close()

    def get_table_info(self, table_names=None) -> str:
        # LangChain SQL Agent vẫn cần string schema → dùng SQLDatabase
        from langchain_community.utilities import SQLDatabase

        db = SQLDatabase.from_uri(self.db_uri, include_tables=table_names)
        return db.get_table_info(table_names)



# from __future__ import annotations
#
# import os
# import logging
# from functools import lru_cache
# from typing import Optional, List, Any
#
# from langchain_community.utilities import SQLDatabase
# from components.interfaces import ISQLDatabase
#
#
# # Setup logging nhẹ cho production
# logger = logging.getLogger("uniorien.postgres")
# if not logger.handlers:
#     handler = logging.StreamHandler()
#     handler.setFormatter(logging.Formatter("[PostgreSQL] %(message)s"))
#     logger.addHandler(handler)
#     logger.setLevel(logging.INFO)
#
#
# class PostgresDatabase(ISQLDatabase):
#     """
#     Production-ready wrapper cho PostgreSQL dùng trong UniOrien AI.
#     - Whitelist bảng chặt chẽ
#     - Fail-fast khi khởi tạo
#     - Cache schema info
#     - Logging rõ ràng
#     """
#
#     def __init__(
#         self,
#         db_uri: str | None = None,
#         include_tables: Optional[List[str]] = None,
#     ):
#         self.db_uri = db_uri or os.getenv("POSTGRES_URI")
#         if not self.db_uri:
#             raise ValueError("POSTGRES_URI không được để trống")
#
#         # Whitelist bảng được phép truy cập (bắt buộc)
#         default_tables = [
#             "university",
#             "admission_information",
#             "university_information",
#             "university_comments",
#             "major",
#             "major_for_group",
#             "news",
#             "benchmark",
#         ]
#         self.include_tables = include_tables or default_tables
#
#         logger.info(f"Đang kết nối PostgreSQL với {len(self.include_tables)} bảng được phép...")
#
#         try:
#             self.db = SQLDatabase.from_uri(
#                 self.db_uri,
#                 include_tables=self.include_tables,
#                 sample_rows_in_table_info=3,      # đủ để agent hiểu kiểu dữ liệu
#                 view_support=True,
#             )
#             # Kiểm tra kết nối ngay lập tức → fail-fast
#             self.db.run("SELECT 1")
#             logger.info("Kết nối PostgreSQL thành công")
#         except Exception as e:
#             raise ConnectionError(f"Không thể kết nối PostgreSQL: {e}")
#
#     def run(self, query: str) -> str:
#         """
#         Thực thi query và trả về chuỗi (đúng định dạng LangChain SQL Agent yêu cầu).
#         """
#         logger.info(f"Executing SQL: {query.strip()[:200]}{'...' if len(query) > 200 else ''}")
#         try:
#             result = self.db.run(query)
#             # LangChain đôi khi trả pandas DataFrame → ép về str
#             if not isinstance(result, str):
#                 result = str(result)
#             return result.strip()
#         except Exception as e:
#             logger.error(f"SQL query failed: {e}")
#             raise RuntimeError(f"Query thất bại: {e}")
#
#     @lru_cache(maxsize=1)
#     def get_table_info(self, table_names: Optional[List[str]] = None) -> str:
#         """
#         Lấy schema – có cache để tăng tốc SQL Agent.
#         """
#         try:
#             info = self.db.get_table_info(table_names)
#             return info
#         except Exception as e:
#             logger.error(f"Failed to get table info: {e}")
#             raise
#
#     # Bonus: phương thức tiện ích để lấy profile trường (dùng trong synthesis)
#     def get_university_profile(self, university_id: str) -> str:
#         query = f"""
#         SELECT
#             u.name,
#             ui.description,
#             ui.address,
#             ui.website
#         FROM university u
#         JOIN university_information ui ON u.id = ui.university_id
#         WHERE u.id = '{university_id}'
#         LIMIT 1
#         """
#         return self.run(query)