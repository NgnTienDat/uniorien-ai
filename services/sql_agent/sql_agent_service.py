from __future__ import annotations

from components.manager import SQLDatabaseManager, GenerationManager
from services.sql_agent.sql_result import SQLAgentResult


class SQLAgentService:
    """
    SQL Agent:
    - NL question → SQL
    - Execute SQL
    - Return structured SQLAgentResult
    """

    def __init__(self):
        self.db = SQLDatabaseManager.instance().get_db()
        self.schema = self.db.get_table_info()

        self.generator = GenerationManager.instance().primary
        if not self.generator:
            raise RuntimeError("GenerationManager is not configured.")

    def _build_system_prompt(self) -> str:
        schema_info = self.schema

        return f"""
            You are a senior data analyst working with a PostgreSQL database.
        
            Database schema:
            {schema_info}
        
            Rules:
            - Only generate SELECT queries.
            - NEVER generate INSERT, UPDATE, DELETE, DROP, ALTER.
            - Use explicit column names, never SELECT *.
            - Use table and column names EXACTLY as shown in the schema above.
            - Do NOT hallucinate tables or columns.
            
            String matching rules (IMPORTANT):
            - ALWAYS use ILIKE for matching text fields (names, majors, universities, methods).
            - Prefer patterns with % on both sides, e.g. ILIKE '%công nghệ thông tin%'.
            - NEVER use = for text fields unless the value is clearly an exact enum or year.
            
            - If the question cannot be answered with SQL, return an empty query.
        
            Return ONLY the SQL query. No explanation.
        """.strip()

    def generate_sql(self, question: str) -> str:
        """
        Dùng LLM sinh SQL từ câu hỏi tự nhiên.
        """

        sql = self.generator.generate(
            system_prompt=self._build_system_prompt(),
            user_prompt=question,
            temperature=0.0,
            max_tokens=512,
        )

        sql = sql.strip()

        if sql.startswith("```"):
            sql = sql.replace("```sql", "").replace("```", "").strip()

        return sql.rstrip(";")

    def _execute_sql(self, sql: str) -> SQLAgentResult:

        raw_result = self.db.run(sql)

        # Case 1: list[dict]
        if isinstance(raw_result, list):
            rows = raw_result
            columns = list(rows[0].keys()) if rows else []

        # Case 2: pandas DataFrame
        elif hasattr(raw_result, "to_dict"):
            rows = raw_result.to_dict(orient="records")
            columns = list(raw_result.columns)

        else:
            raise RuntimeError(
                f"Unsupported SQL result type: {type(raw_result)}"
            )

        return SQLAgentResult(
            sql=sql,
            columns=columns,
            rows=rows,
        )

    def query(self, question: str) -> SQLAgentResult:
        sql = self.generate_sql(question)
        print("=== GENERATED SQL ===")
        print(sql)
        return self._execute_sql(sql)

    def print_schema(self):
        print("=== DATABASE SCHEMA ===")
        print(self.schema)
