---
title: "임베딩 모델별 입력 형식 가이드"
category: embedding
tags: [embedding, openai, cohere, voyage, jina, huggingface, rag]
created: 2026-08-05
sources:
  - https://developers.openai.com/api/docs/guides/embeddings
  - https://developers.openai.com/api/reference/resources/embeddings/methods/create
  - https://docs.voyageai.com/reference/embeddings-api
  - https://docs.voyageai.com/docs/embeddings
  - https://api.jina.ai/docs
  - https://docs.pinecone.io/models/jina-embeddings-v3
  - https://aws.amazon.com/marketplace/pp/prodview-b4mpgdxvpa3v6
  - https://qdrant.tech/documentation/embeddings/cohere/
  - https://docs.trychroma.com/docs/overview/getting-started
---

# 임베딩 모델별 입력 형식 가이드

본 가이드는 Claude Code RAG 지식 베이스의 135개 청크를 주요 임베딩 모델에 맞게 변환하는 방법을 설명합니다.

## 목차

1. [지원 임베딩 모델 비교](#1-지원-임베딩-모델-비교)
2. [OpenAI text-embedding-3](#2-openai-text-embedding-3)
3. [Cohere Embed v3](#3-cohere-embed-v3)
4. [Voyage AI](#4-voyage-ai)
5. [Jina Embeddings](#5-jina-embeddings)
6. [HuggingFace Sentence-Transformers](#6-huggingface-sentence-transformers)
7. [공통 데이터 로더](#7-공통-데이터-로더)
8. [모델 선택 가이드](#8-모델-선택-가이드)

---

## 1. 지원 임베딩 모델 비교

| 모델 | 차원 | 최대 토큰 | 다국어 | input_type 구분 | 가격 |
|------|------|-----------|--------|-----------------|------|
| OpenAI text-embedding-3-small | 1536 | 8,192 | 제한적 | 없음 | 공식 가격 페이지 확인 |
| OpenAI text-embedding-3-large | 3072 | 8,192 | 제한적 | 없음 | 공식 가격 페이지 확인 |
| Cohere embed-multilingual-v3.0 | 1024 | 512 | 100+ 언어 | 필수 | 공식 가격 페이지 확인 |
| Voyage voyage-4-large | 1024 | 32,000 | 100+ 언어 | 권장 | 공식 가격 페이지 확인 |
| Jina jina-embeddings-v3 | 1024 | 8,192 | 30+ 언어 | 선택 | 공식 가격 페이지 확인 |
| HuggingFace BAAI/bge-m3 | 1024 | 8,192 | 100+ 언어 | 없음 | 무료 (로컬) |

### 핵심 차이점

- **input_type 구분**: Cohere와 Voyage는 문서 색인용(`search_document`/`document`)과 쿼리 검색용(`search_query`/`query`)을 분리하여 임베딩 품질을 향상시킵니다.
- **다국어 지원**: 한국어 콘텐츠의 경우 Cohere embed-multilingual-v3.0, Voyage voyage-4-large, BGE-m3가 권장됩니다.
- **배치 제한**: OpenAI는 요청당 최대 300K 토큰, Cohere는 최대 1024개 텍스트, Voyage는 최대 1000개 텍스트까지 처리합니다.

---

## 2. OpenAI text-embedding-3

### 입력 형식

```python
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

# 단일 텍스트
response = client.embeddings.create(
    model="text-embedding-3-small",  # 또는 text-embedding-3-large
    input="임베딩할 텍스트",
    encoding_format="float",  # "float" 또는 "base64"
    # dimensions=256,  # text-embedding-3 시리즈에서만 차원 축소 가능
)
embedding = response.data[0].embedding  # List[float], 길이 1536 또는 3072
```

### 배치 입력

```python
# 여러 텍스트를 한 번에 처리 (최대 300K 토큰)
texts = [chunk["embedding_text"] for chunk in chunks]

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts,  # List[str], 최대 2048개
)
embeddings = [item.embedding for item in response.data]
```

### RAG 청크 변환 스크립트

```python
import json

# JSON 파일 로드
with open("chunk-embeddings.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# OpenAI 입력 형식으로 변환
texts = [chunk["embedding_text"] for chunk in chunks]

# 배치 처리 (2048개씩 분할)
batch_size = 2048
all_embeddings = []
for i in range(0, len(texts), batch_size):
    batch = texts[i:i + batch_size]
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=batch,
    )
    all_embeddings.extend([item.embedding for item in response.data])

# 결과 저장
for chunk, embedding in zip(chunks, all_embeddings):
    chunk["embedding"] = embedding

with open("chunk-embeddings-openai.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)
```

### 주의사항

- 입력당 최대 8,192 토큰, 요청당 총 300,000 토큰 제한 ([OpenAI API Reference](https://developers.openai.com/api/reference/resources/embeddings/methods/create))
- 빈 문자열은 허용되지 않음
- `dimensions` 파라미터는 text-embedding-3 시리즈에서만 지원 ([OpenAI Embeddings Guide](https://developers.openai.com/api/docs/guides/embeddings))

---

## 3. Cohere Embed v3

### 입력 형식

```python
import cohere

co = cohere.Client("YOUR_API_KEY")

# 문서 임베딩 (색인용)
response = co.embed(
    model="embed-multilingual-v3.0",  # 한국어 지원
    texts=["임베딩할 텍스트"],
    input_type="search_document",  # 필수: search_document | search_query | classification | clustering
    embedding_types=["float"],  # "float", "int8", "uint8", "binary", "ubinary"
    # truncate="END",  # NONE | START | END
)
embeddings = response.embeddings.float  # List[List[float]], 길이 1024
```

### 배치 입력

```python
# 최대 1024개 텍스트 per call
texts = [chunk["embedding_text"] for chunk in chunks]

batch_size = 96  # 안전한 배치 크기
all_embeddings = []
for i in range(0, len(texts), batch_size):
    batch = texts[i:i + batch_size]
    response = co.embed(
        model="embed-multilingual-v3.0",
        texts=batch,
        input_type="search_document",
    )
    all_embeddings.extend(response.embeddings.float)
```

### 쿼리 임베딩 (검색 시)

```python
# 검색 쿼리는 input_type을 search_query로 설정
query_response = co.embed(
    model="embed-multilingual-v3.0",
    texts=["Claude Code Hooks 설정 방법"],
    input_type="search_query",  # 검색 시 반드시 search_query 사용
)
query_embedding = query_response.embeddings.float[0]
```

### 주의사항

- `input_type`은 **필수** 파라미터입니다 ([Cohere API](https://aws.amazon.com/marketplace/pp/prodview-b4mpgdxvpa3v6))
- 문서 색인 시 `search_document`, 검색 쿼리 시 `search_query`를 사용해야 같은 벡터 공간에서 정확한 매칭이 가능합니다
- 한국어 지원을 위해 `embed-multilingual-v3.0` 모델을 사용하세요
- 텍스트당 권장 길이는 512 토큰 이하

---

## 4. Voyage AI

### 입력 형식

```python
import voyageai

vo = voyageai.Client(api_key="YOUR_API_KEY")

# 문서 임베딩
result = vo.embed(
    texts=["임베딩할 텍스트"],
    model="voyage-4-large",  # 최고 품질 다국어 모델
    input_type="document",  # None | "query" | "document"
    truncation=True,  # 초과 텍스트 자동 잘림
    # output_dimension=1024,  # 256, 512, 1024(기본), 2048
    # output_dtype="float",  # "float", "int8", "uint8", "binary", "ubinary"
)
embeddings = result.embeddings  # List[List[float]], 길이 1024
```

### 배치 입력

```python
texts = [chunk["embedding_text"] for chunk in chunks]

# 최대 1000개 텍스트 per call, 총 120K 토큰 (voyage-4-large 기준)
batch_size = 50
all_embeddings = []
for i in range(0, len(texts), batch_size):
    batch = texts[i:i + batch_size]
    result = vo.embed(
        texts=batch,
        model="voyage-4-large",
        input_type="document",
    )
    all_embeddings.extend(result.embeddings)
```

### 쿼리 임베딩 (검색 시)

```python
query_result = vo.embed(
    texts=["MCP 서버 설정 방법"],
    model="voyage-4-large",
    input_type="query",  # 검색 시 "query" 사용
)
query_embedding = query_result.embeddings[0]
```

### 주의사항

- `input_type`을 지정하면 자동으로 프롬프트가 추가됩니다 ([Voyage AI Docs](https://docs.voyageai.com/docs/embeddings))
  - `query`: "Represent the query for retrieving supporting documents: " 접두사
  - `document`: "Represent the document for retrieval: " 접두사
- `input_type`을 지정한 임베딩과 지정하지 않은 임베딩은 호환됩니다
- Voyage 4 시리즈 임베딩은 서로 호환됩니다
- 32K 토큰 컨텍스트로 긴 청크도 처리 가능

---

## 5. Jina Embeddings

### 입력 형식

```python
import requests

response = requests.post(
    "https://api.jina.ai/v1/embeddings",
    headers={
        "Authorization": "Bearer YOUR_JINA_API_KEY",
        "Content-Type": "application/json",
    },
    json={
        "model": "jina-embeddings-v3",
        "input": ["임베딩할 텍스트"],
        "task": "text-matching",  # text-matching | retrieval | separation | classification
        # "dimensions": 1024,  # Matryoshka: 256, 512, 768, 1024
    },
)
embeddings = [item["embedding"] for item in response.json()["data"]]
```

### task 타입

| task 값 | 용도 | RAG 사용 시점 |
|---------|------|---------------|
| `text-matching` | 일반적 유사도 매칭 | 기본값 |
| `retrieval.passage` | 문서 색인용 | 문서를 DB에 저장할 때 |
| `retrieval.query` | 검색 쿼리용 | 사용자 질의 검색 시 |
| `separation` | 클러스터링 | 문서 분류 |
| `classification` | 분류 | 텍스트 분류 |

### 배치 입력

```python
texts = [chunk["embedding_text"] for chunk in chunks]

batch_size = 100
all_embeddings = []
for i in range(0, len(texts), batch_size):
    batch = texts[i:i + batch_size]
    response = requests.post(
        "https://api.jina.ai/v1/embeddings",
        headers={
            "Authorization": "Bearer YOUR_JINA_API_KEY",
            "Content-Type": "application/json",
        },
        json={
            "model": "jina-embeddings-v3",
            "input": batch,
            "task": "retrieval.passage",
        },
    )
    all_embeddings.extend([item["embedding"] for item in response.json()["data"]])
```

### 주의사항

- Jina v3는 30개 이상 언어를 지원하며 한국어 처리 우수 ([Pinecone Docs](https://docs.pinecone.io/models/jina-embeddings-v3))
- `task` 파라미터로 검색 품질 향상 가능
- v5 시리즈: 32K 컨텍스트, 1024차원 지원
- 비동기 배치 처리: POST `/v1/batch/embeddings` (JSONL 입력/출력) ([Jina API](https://api.jina.ai/docs))

---

## 6. HuggingFace Sentence-Transformers

### 입력 형식

```python
from sentence_transformers import SentenceTransformer

# 로컬 모델 (API 키 불필요)
model = SentenceTransformer("BAAI/bge-m3")  # 다국어, 1024차원, 8K 컨텍스트

# 단일 텍스트
embedding = model.encode("임베딩할 텍스트")  # numpy.ndarray, shape (1024,)

# 배치 입력
texts = [chunk["embedding_text"] for chunk in chunks]
embeddings = model.encode(
    texts,
    batch_size=32,
    show_progress_bar=True,
    normalize_embeddings=True,  # 코사인 유사도용 정규화
)
# embeddings.shape = (135, 1024)
```

### 추천 다국어 모델

| 모델 | 차원 | 컨텍스트 | 특징 |
|------|------|----------|------|
| BAAI/bge-m3 | 1024 | 8,192 | 100+ 언어, 다기능(dense+sparse+colbert) |
| intfloat/multilingual-e5-large | 1024 | 512 | 100+ 언어, 검색 특화 |
| jinaai/jina-embeddings-v3 | 1024 | 8,192 | 30+ 언어, task 지정 |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | 384 | 128 | 경량, 50+ 언어 |

### 주의사항

- 로컬 실행으로 API 비용 없음
- GPU 사용 시 속도 대폭 향상 (`device="cuda"` 지정)
- `normalize_embeddings=True` 시 코사인 유사도 검색에 최적화
- BGE-m3의 경우 dense, sparse, colbert 벡터를 동시에 생성 가능

---

## 7. 공통 데이터 로더

모든 임베딩 스크립트에서 공통으로 사용하는 데이터 로더입니다.

```python
import json
import csv
from pathlib import Path
from typing import List, Dict, Any


def load_chunks_from_json(json_path: str = "chunk-embeddings.json") -> List[Dict[str, Any]]:
    """JSON 파일에서 청크 데이터를 로드합니다."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_chunks_from_csv(csv_path: str = "chunk-embeddings.csv") -> List[Dict[str, Any]]:
    """CSV 파일에서 청크 데이터를 로드합니다."""
    chunks = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 세미콜론 구분 필드를 리스트로 변환
            row["tags"] = row["tags"].split(";") if row["tags"] else []
            row["source_urls"] = row["source_urls"].split(";") if row["source_urls"] else []
            row["related_chunks"] = row["related_chunks"].split(";") if row["related_chunks"] else []
            chunks.append(row)
    return chunks


def prepare_metadata(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """벡터 DB 메타데이터로 사용할 필드를 추출합니다."""
    return {
        "chunk_id": chunk["chunk_id"],
        "title": chunk["title"],
        "section": chunk["section"],
        "section_id": chunk["section_id"],
        "category": chunk["category"],
        "source_file": chunk["source_file"],
        "tags": ",".join(chunk["tags"]) if isinstance(chunk["tags"], list) else chunk.get("tags", ""),
        "summary": chunk["summary"],
    }
```

---

## 8. 모델 선택 가이드

### 한국어 RAG 지식 베이스 추천 순위

> **참고**: 아래 스크립트별 지원 모델을 확인하세요. `voyage`는 Pinecone 스크립트에서만 지원됩니다. 나머지 스크립트에서 Voyage를 사용하려면 `embed_voyage()` 함수를 추가하세요.

### 스크립트별 지원 모델

| 스크립트 | openai | openai-large | cohere | voyage | huggingface | builtin |
|----------|--------|-------------|--------|--------|-------------|---------|
| upload_pinecone.py | O | O | O | O | X | X |
| upload_chromadb.py | O | O | O | X | O | O |
| upload_qdrant.py | O | O | O | X | O | X |
| upload_weaviate.py | O | O | O | X | O | X |
| upload_faiss.py | O | O | O | X | O | X |
| upload_incremental.py | O | O | O | O | O | X |

| 순위 | 모델 | 추천 이유 |
|------|------|-----------|
| 1 | BAAI/bge-m3 | 무료, 100+ 언어, 8K 컨텍스트, 다기능 벡터 |
| 2 | Cohere embed-multilingual-v3.0 | 100+ 언어, input_type 분리, 안정적 API |
| 3 | Voyage voyage-4-large | 32K 컨텍스트, 최고 검색 품질, 다국어 |
| 4 | OpenAI text-embedding-3-small | 저렴, 널리 사용됨, 한국어 무난 |
| 5 | Jina jina-embeddings-v3 | 저렴, 30+ 언어, task 지정 가능 |

### 선택 기준

- **비용 최소화**: HuggingFace BGE-m3 (무료, 로컬 실행)
- **최고 검색 품질**: Voyage voyage-4-large 또는 Cohere embed-multilingual-v3.0
- **기존 인프라 활용**: OpenAI (이미 API 키가 있는 경우)
- **긴 문서 처리**: Voyage voyage-4-large (32K 토큰)
- **경량/빠른 처리**: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

### 차원별 호환성

임베딩 차원은 벡터 DB 스키마와 일치해야 합니다. 동일 모델 내에서 차원 축소(Matryoshka)를 지원하는 경우:

```python
# OpenAI: dimensions 파라미터
client.embeddings.create(model="text-embedding-3-large", input=texts, dimensions=1024)

# Voyage: output_dimension 파라미터
vo.embed(texts=texts, model="voyage-4-large", output_dimension=512)

# Jina: dimensions 파라미터
{"model": "jina-embeddings-v3", "input": texts, "dimensions": 768}
```

> **주의**: 차원을 변경하려면 기존 임베딩을 모두 재생성해야 합니다. 서로 다른 차원의 벡터를 같은 인덱스에 혼용할 수 없습니다.

---

## 신규 청크 구성 (2026-08-05 보강)

원본 94개 청크에서 135개로 확장되었습니다. 신규 41개 청크(chunk.095~chunk.135)는 다음 7개 문서에서 생성되었습니다:

| 신규 문서 | 청크 범위 | 청크 수 | 카테고리 |
|----------|-----------|--------|----------|
| 07-tool-generation-agent.md | chunk.095~101 | 7 | concepts |
| 08-context-engineering.md | chunk.102~108 | 7 | concepts |
| 04-tool-generation-agent-setup.md | chunk.109~113 | 5 | setup |
| 04-quality-evaluation-ci.md | chunk.114~118 | 5 | operations |
| 05-cost-performance-optimization.md | chunk.119~123 | 5 | operations |
| 06-deployment-adoption-governance.md | chunk.124~128 | 5 | operations |
| 03-agent-frameworks-and-gateways.md | chunk.129~135 | 7 | catalog |

### 카테고리별 청크 분포 (총 135개)

| 카테고리 | 청크 수 | 기존 | 신규 추가 |
|----------|--------|------|----------|
| concept | 56 | 42 | +14 |
| operations | 30 | 15 | +15 |
| mcp-catalog | 15 | 15 | - |
| setup | 20 | 15 | +5 |
| catalog | 7 | 0 | +7 |
| exceptions | 7 | 7 | - |

### 임베딩 생성 시 주의사항 (신규 청크)

- 신규 청크에는 한국어+영어 혼합 콘텐츠가 다수 포함되어 있어 다국어 임베딩 모델(Cohere, Voyage, BGE-m3) 권장
- `embedding_text` 필드에 `"{title} - {section}\n\n{content}"` 형식으로 저장되어 있어 별도 전처리 없이 배치 임베딩 가능
- `chunk-embeddings.json` 파일에 모든 135개 청크의 `embedding_text`가 포함되어 있어 기존 스크립트 실행만으로 전체 재임베딩 수행
- 기존 94개 청크의 임베딩을 유지하면서 신규 41개만 추가하려면 `upload_incremental.py` 스크립트 사용

### 증분 임베딩 스크립트 (upload_incremental.py)

신규 청크만 필터링하여 임베딩을 생성하고 벡터 DB에 업로드합니다. 기존 임베딩은 그대로 유지됩니다.

```bash
# 신규 41개만 임베딩하여 파일로 저장 (검토용)
python upload_incremental.py --model openai --save embeddings_new.json

# 신규 41개만 Pinecone에 업로드 (기존 94개 유지)
python upload_incremental.py --model openai --target pinecone --index claude-code-kb

# 신규 41개만 ChromaDB에 업로드 (HuggingFace, 무료/로컬)
python upload_incremental.py --model huggingface --target chromadb --collection claude-code-kb

# 신규 41개만 FAISS 인덱스에 추가 (기존 인덱스에 병합)
python upload_incremental.py --model huggingface --target faiss --index-path ./faiss_index

# chunk.100부터 증분 (37개만)
python upload_incremental.py --model openai --target pinecone --from-chunk 100
```

지원 대상: file, pinecone, chromadb, qdrant, weaviate, faiss
지원 모델: openai, openai-large, cohere, voyage, huggingface

```python
# 프로그래밍 방식으로 신규 청크만 추출
import json

with open("chunk-embeddings.json", "r", encoding="utf-8") as f:
    all_chunks = json.load(f)

new_chunks = [c for c in all_chunks if int(c["chunk_id"].split(".")[1]) >= 95]
print(f"신규 청크 수: {len(new_chunks)}")  # 41

texts = [c["embedding_text"] for c in new_chunks]
# 기존 스크립트의 embed_* 함수에 texts 전달
```

---

## 출처

- [OpenAI Embeddings Guide](https://developers.openai.com/api/docs/guides/embeddings)
- [OpenAI API Reference - Create Embeddings](https://developers.openai.com/api/reference/resources/embeddings/methods/create)
- [Voyage AI - Text Embeddings](https://docs.voyageai.com/docs/embeddings)
- [Voyage AI - Embeddings API Reference](https://docs.voyageai.com/reference/embeddings-api)
- [Jina API Documentation](https://api.jina.ai/docs)
- [Pinecone - Jina Embeddings v3](https://docs.pinecone.io/models/jina-embeddings-v3)
- [Cohere Embed Model 3 - AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-b4mpgdxvpa3v6)
- [Qdrant - Cohere Embeddings](https://qdrant.tech/documentation/embeddings/cohere/)
- [ChromaDB Getting Started](https://docs.trychroma.com/docs/overview/getting-started)
