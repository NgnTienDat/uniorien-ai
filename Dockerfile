# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /build

# Cài đặt công cụ build (Cần thiết cho hnswlib/chromadb)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt


# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy thư viện từ stage builder
COPY --from=builder /install /usr/local

# Tạo thư mục DB (dùng để mount volume sau này)
RUN mkdir -p chroma_store && chmod 777 chroma_store

COPY . .

ENV CHROMA_DB_PATH=/app/chroma_store \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "run:uniorien_app", "--host", "0.0.0.0", "--port", "8000"]