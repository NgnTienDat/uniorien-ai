```
graph TB
    subgraph FRONTEND["NextJS Frontend"]
        ChatUI["Chat Interface"]
    end

    subgraph FLASK["Flask AI Service"]
        direction TB
        Endpoint["/chat Endpoint"]
        
        subgraph ROUTER["Smart Router"]
            Classifier["Query Classifier<br>(Regex + LLM)"]
        end
        
        subgraph SQL_PATH["SQL Path (90% of queries)"]
            SQLAgent["LangChain SQL Agent"]
            SQLTool["SQL Database Toolkit"]
        end
        
        subgraph RAG_PATH["RAG Path (10% of queries)"]
            Retriever["Vector Retriever"]
            RAGChain["RAG Chain"]
        end
        
        Formatter["Response Formatter"]
    end
    
    subgraph DATA["Data Layer"]
        PG[(PostgreSQL<br>Universities<br>Admissions<br>Reviews)]
        Chroma[(ChromaDB<br>Review Embeddings Only)]
    end
    
    subgraph LLM["LLM"]
        Gemini["Gemini 2.5 Flash"]
    end
    
    ChatUI -->|"User Question"| Endpoint
    Endpoint --> Classifier
    
    Classifier -->|"Factual Query"| SQLAgent
    Classifier -->|"Opinion Query"| Retriever
    
    SQLAgent --> SQLTool
    SQLTool --> PG
    
    Retriever --> Chroma
    RAGChain --> Gemini
    
    SQLAgent --> Gemini
    
    Gemini --> Formatter
    Formatter --> ChatUI

```