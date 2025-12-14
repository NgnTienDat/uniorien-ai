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


