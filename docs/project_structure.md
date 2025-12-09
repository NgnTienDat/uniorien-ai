uniorien-chatbot-service/
├── app/
│   ├── __init__.py          # Khởi tạo Flask app instance
│   │
│   ├── api/                 # Lớp giao tiếp (API Layer)
│   │   ├── __init__.py
│   │   ├── routes.py        # Định nghĩa endpoint `/chat`
│   │   └── schemas.py       # Pydantic models (Input/Output validation)
│   │
│   ├── core/                # Cấu hình cốt lõi
│   │   ├── config.py        # Load biến môi trường (Gemini Key, DB URI)
│   │   └── llm.py           # Khởi tạo Gemini 1.5 Flash (dùng chung)
│   │
│   ├── logic/               # "Bộ não" chính (Business Logic)
│   │   ├── __init__.py
│   │   ├── router.py        # ✨ Smart Router (Logic phân loại Query)
│   │   │
│   │   ├── sql_path/        # 🛠️ SQL Path (90% queries)
│   │   │   ├── __init__.py
│   │   │   ├── agent.py     # Cấu hình LangChain SQL Agent
│   │   │   └── toolkit.py   # Custom tools cho SQL (nếu cần)
│   │   │
│   │   └── rag_path/        # 📚 RAG Path 
│   │   │   ├── __init__.py
│   │   │   ├── chain.py     # Cấu hình RAG Chain
│   │   │   └── retriever.py # Logic kết nối ChromaDB & Retriever
│   │
│   ├── services/            # Kết nối Infrastructure bên ngoài
│   │   ├── database.py      # Kết nối PostgreSQL (SQLAlchemy)
│   │   └── vector_db.py     # Kết nối ChromaDB Client
│   │
│   ├── scripts/             # Script tiện ích (chạy 1 lần hoặc định kỳ)
│   │   ├── __init__.py
│   │   └── ingest_data.py   # Chạy file này để embedding reviews vào ChromaDB
│   │
│   └── utils/               # Tiện ích bổ trợ
│       ├── formatters.py    # ✨ Response Formatter (Định dạng câu trả lời cuối)
│       ├── memory.py        # 🧠 Xử lý In-Memory Context (Parse từ request)
│       └── prompts.py       # Tập trung tất cả Prompt Template ở đây
│
├── data/                    # (Optional) Chứa dữ liệu ChromaDB local khi dev
├── .gitignore
├── requirements.txt         # Các thư viện Python (langchain, flask, google-generativeai...)
└── run.py                   # Entry point để chạy server (python run.py)


``` Giải thích từng phần chính trong cấu trúc trên:
1. app/api/routes.py (Endpoint Layer)
Đây là nơi nhận request từ Next.js.
    Nhiệm vụ: Nhận JSON payload (chứa question và chat_history).
    Xử lý: Gọi logic.router.route_query(question, history) để lấy câu trả lời.
    Không lưu DB: Nó chỉ lấy lịch sử chat từ request, truyền vào logic xử lý, rồi trả kết quả về.

2. app/logic/router.py (Smart Router)
Tương ứng với node Smart Router trong biểu đồ.
    Logic: Chứa hàm classify_query(question). Sử dụng Regex hoặc gọi nhẹ LLM để quyết định xem 
    nên gọi sql_path.agent hay rag_path.chain.

3. app/logic/sql_path/agent.py
Tương ứng với node SQL Agent.
    Logic: Khởi tạo create_sql_agent của LangChain.
    Kết nối: Import engine từ services/database.py và LLM từ core/llm.py.

4. app/logic/rag_path/chain.py
Tương ứng với node RAG Chain.
    Logic: Định nghĩa chuỗi: Retriever | Prompt | LLM.
    Kết nối: Import retriever từ rag_path/retriever.py.

5. app/utils/memory.py (Quan trọng: Thay thế DB History)
Vì bạn bỏ DB History, file này sẽ chứa các hàm tiện ích để xử lý lịch sử chat "tạm thời".
    Ví dụ: Hàm format_history_for_llm(raw_history_list) để chuyển đổi mảng JSON từ Frontend 
    thành định dạng mà LangChain/Gemini hiểu được (ví dụ: list các HumanMessage, AIMessage).

6. app/utils/prompts.py
Đừng hardcode prompt trong file logic. Hãy để hết vào đây.
    Ví dụ:
        ROUTER_SYSTEM_PROMPT: "Bạn là bộ phân loại câu hỏi..."
        SQL_AGENT_PROMPT: "Bạn là chuyên gia SQL..."

💡 Lời khuyên khi bắt đầu code
    Bắt đầu từ run.py và app/__init__.py: Dựng server Flask lên trước để đảm bảo "Hello World" chạy được.
    Setup services/: Kết nối thành công vào PostgreSQL và ChromaDB.
    Build sql_path trước: Vì nó chiếm 90% use-case, hãy làm cho SQL Agent chạy tốt trước.
    Thêm router: Sau khi SQL chạy ổn, mới làm Router để điều hướng sang RAG sau.
```


uniorien-chatbot-service/
├── app/
│   ├── __init__.py          # Initialize Flask app instance
│   │
│   ├── api/                 # API Layer (Communication Layer)
│   │   ├── __init__.py
│   │   ├── routes.py        # Defines `/chat` endpoint
│   │   └── schemas.py       # Pydantic models (Input/Output validation)
│   │
│   ├── core/                # Core configuration
│   │   ├── config.py        # Load environment variables (Gemini Key, DB URI)
│   │   └── llm.py           # Initialize Gemini 1.5 Flash (shared instance)
│   │
│   ├── logic/               # Main “Brain” (Business Logic)
│   │   ├── __init__.py
│   │   ├── router.py        # ✨ Smart Router (Classifies user queries)
│   │   │
│   │   ├── sql_path/        # 🛠️ SQL Path (handles ~90% of queries)
│   │   │   ├── __init__.py
│   │   │   ├── agent.py     # LangChain SQL Agent configuration
│   │   │   └── toolkit.py   # Custom SQL tools (if needed)
│   │   │
│   │   └── rag_path/        # 📚 RAG Path (~10% of queries)
│   │       ├── __init__.py
│   │       ├── chain.py     # RAG Chain configuration
│   │       └── retriever.py # Logic connecting ChromaDB & Retriever
│   │
│   ├── services/            # External infrastructure connectors
│   │   ├── database.py      # PostgreSQL connection (SQLAlchemy)
│   │   └── vector_db.py     # ChromaDB Client connection
│   │
│   ├── scripts/             # Utility scripts (run once or scheduled)
│   │   ├── __init__.py
│   │   └── ingest_data.py   # Script to embed and ingest data into ChromaDB
│   │
│   └── utils/               # Helper utilities
│       ├── formatters.py    # ✨ Response Formatter (format final output)
│       ├── memory.py        # 🧠 Handle in-memory context (parsed from request)
│       └── prompts.py       # Centralized Prompt Templates
│
├── data/                    # (Optional) Local ChromaDB data during development
├── .gitignore
├── requirements.txt         # Python dependencies (langchain, flask, google-generativeai...)
└── run.py                   # Entry point to start the server (python run.py)
