uniorien-chatbot-service/
├── app
│   ├── __init__.py  # Khởi tạo Flask app
│   ├── routes.py    # API endpoints: /api/chat (xử lý query, intent, route đến agents)
│   └── utils.py     # Utility chung (nếu cần, ví dụ: format response)
├── components
│   ├── database
│   │   └── chroma_db.py  # VectorDB implementation, cung cấp phương thức truy vấn vector database
│   ├── embedding
│   │   ├── ollama_embedder.py         # Optional fallback
│   │   └── sentence_transformer_embedder.py  # Chính cho embedding text
│   ├── generation
│   │   ├── ollama_generator.py  # Fallback
│   │   └── openai_generator.py  # Chính
│   ├── interfaces.py  # Abstract classes cho Generator, Embedding, VectorDatabase
│   └── manager.py     # Singleton managers cho LLM, Embedding, DB, Prompt
├── prompt
│   ├── intent_classification.txt  # Prompt phân loại ý định (SQL, RAG, kết hợp)
│   ├── sql_query.txt              # Prompt cho SQL Agent (Text-to-SQL)
│   ├── rag_query.txt              # Prompt cho RAG query
│   └── synthesis.txt              # Prompt tổng hợp kết quả từ SQL + RAG
├── service
│   ├── guardrail_service.py  # Điều chỉnh cho Intent Classification
│   ├── rag_service.py   # RAG core (ingest text từ DB, query vector)
│   ├── sql_agent_service.py  # Mới: SQL Agent với LangChain
│   └── ingestion_service.py  # Mới: Ingest text fields từ PostgreSQL vào ChromaDB
├── .dockerignore
├── .gitignore
├── Dockerfile
├── README.md
├── requirements.txt  # Thêm langchain, langchain-community, psycopg2 (cho PostgreSQL)
└── run.py            # Khởi động Flask server

``` WORKFLOWS:
a. Khởi Động Hệ Thống (run.py):

    Khởi tạo managers (GenerationManager với OpenAI chính, Ollama fallback qua env var như LLM_PROVIDER='openai').
    Kết nối PostgreSQL (qua env: DB_HOST, DB_NAME, etc.).
    Chạy ingestion ban đầu nếu cần (ingestion_service.ingest_text_from_db() để embed reviews vào ChromaDB).
    Khởi động Flask server.

b. Ingestion Ban Đầu (ingestion_service.py):

    Kết nối PostgreSQL, query các bảng có text fields (ví dụ: SELECT id, review_text FROM reviews).
    Phân chia text (RecursiveCharacterTextSplitter), embed (EmbeddingManager), lưu vào ChromaDB với metadata 
        (ví dụ: {source: 'reviews', university_id: id}).
    Chạy một lần hoặc định kỳ (không watcher, có thể dùng cron job ngoài).

c. Xử Lý Query Người Dùng (routes.py: /api/chat):

    Nhận Request: Payload: { "query": "câu hỏi", "context": [{"user": "prev query", "assistant": "prev response"}, ...] } 
        (context từ FE để giữ lịch sử ngắn hạn).
    Intent Classification (guardrail_service.py):
    Sử dụng LLM (GenerationManager.generate với prompt intent_classification.txt, kết hợp query + context).
    Output: "SQL" (phân tích/thống kê), "RAG" (ý kiến/review), "HYBRID" (kết hợp).
    Nếu không rõ: Trả lỗi hoặc default RAG.

Thực Thi Agent:
    Nếu SQL: Gọi sql_agent_service.execute(query + context) → Sử dụng LangChain's create_sql_agent 
        (với SQLDatabase.from_uri cho PostgreSQL, prompt sql_query.txt) 
            → Tạo và chạy SQL query → Lấy kết quả bảng (ví dụ: danh sách trường, điểm chuẩn).
    Nếu RAG: Gọi mini_rag_service.query(query + context) 
            → Embed query → Query ChromaDB → Lấy chunks liên quan (reviews/mô tả).
    Nếu HYBRID: Chạy SQL trước → Lấy kết quả (ví dụ: danh sách trường lọc theo điểm) 
        → Sử dụng kết quả làm filter cho RAG query (ví dụ: query vector với where_filter={university_id: in list}) → Lấy reviews.

Tổng Hợp (GenerationManager):
    LLM nhận kết quả từ SQL/RAG (hoặc cả hai), kết hợp với context, sử dụng prompt synthesis.txt để tạo response cuối cùng 
        (hoàn chỉnh, tiếng Việt).
    
    Trả Response: { "answer": "response", "sources": ["SQL: table X", "RAG: chunk Y"] } (nếu cần trace).

d. Error Handling và Optimization:

    SQL Agent: Sử dụng agent executor với handle_parsing_errors=True để tự sửa query sai.
    RAG: Giới hạn n_results=5 để tránh overload.
    LLM Fallback: Nếu OpenAI lỗi (rate limit), switch sang Ollama.
    Security: Validate query để tránh SQL injection (LangChain xử lý phần nào).
    Scaling: Sử dụng async cho API nếu query DB chậm.
```
