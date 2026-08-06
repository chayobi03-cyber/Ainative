#!/usr/bin/env python3
"""v3.0 청크를 벡터 DB에 적재한다.

왜 v2.3 업로드 스크립트를 그대로 못 쓰는가
    v2.3 스크립트는 `chunk-embeddings.json`(JSON 배열, 평면 메타데이터)을 기대한다.
    v3.0은 `embeddings.jsonl`(JSONL, `metadata` 중첩)을 낸다. 형식이 다르고,
    더 중요한 건 **벡터 DB마다 메타데이터 타입 제약이 다르다**는 점이다.

    - ChromaDB: str/int/float/bool만. **리스트 불가** → 쉼표 결합 필요
    - Pinecone: str/num/bool/list[str]. 중첩 객체 불가
    - Qdrant/Weaviate: 비교적 관대하나 스키마 선언이 필요

    이 어댑터가 그 평탄화를 담당한다. 이걸 안 하면 적재 시점에 조용히 실패하거나
    메타데이터 필터가 동작하지 않는다.

폐쇄망 주의
    임베딩 모델·DB 클라이언트는 지연 임포트한다. `--dry-run`은 어떤 외부 패키지도
    필요 없으므로 CI에서 페이로드 형태만 검증할 수 있다.

사용법:
    # 외부 의존성 없이 페이로드 검증만 (CI에서 이것만 돈다)
    python3 tools/upload_vectors.py --dry-run --target chromadb

    # 실제 적재 (해당 클라이언트·모델 패키지 필요)
    python3 tools/upload_vectors.py --target chromadb --model bge-m3 --collection ainative-v3
    python3 tools/upload_vectors.py --target qdrant   --model bge-m3 --collection ainative-v3
    python3 tools/upload_vectors.py --target faiss    --model bge-m3 --index-path ./faiss_index

    # 임베딩만 뽑아 파일로 (검토용)
    python3 tools/upload_vectors.py --target jsonl --model bge-m3 --out vectors.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 벡터 DB별 메타데이터 타입 제약. 위반 시 적재가 조용히 깨지므로 명시적으로 둔다.
TARGET_RULES = {
    "chromadb": {"lists": False, "nested": False},
    "pinecone": {"lists": True, "nested": False},
    "qdrant": {"lists": True, "nested": True},
    "weaviate": {"lists": True, "nested": False},
    "faiss": {"lists": True, "nested": True},
    "jsonl": {"lists": True, "nested": True},
}

# 검색 프리필터에 실제로 쓰는 필드만 싣는다. 전부 넣으면 인덱스만 커진다.
METADATA_FIELDS = ["category", "tags", "priority", "audience", "confidence", "freshness", "origin"]


def load_records(kb: Path) -> list[dict]:
    emb = {}
    for line in (kb / "embeddings.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            emb[r["chunk_id"]] = r
    out = []
    for line in (kb / "manifest.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        m = json.loads(line)
        e = emb.get(m["chunk_id"])
        if e is None:
            raise SystemExit(f"embeddings.jsonl에 {m['chunk_id']}가 없습니다. 재빌드하십시오.")
        out.append({"manifest": m, "embedding": e})
    if len(out) != len(emb):
        raise SystemExit(f"매니페스트 {len(out)}건 vs 임베딩 {len(emb)}건 — 불일치. 재빌드하십시오.")
    return out


def flatten_metadata(m: dict, rules: dict) -> dict:
    """벡터 DB 제약에 맞춰 메타데이터를 평탄화한다."""
    out: dict = {}
    for k in METADATA_FIELDS:
        v = m.get(k)
        if v is None or v == [] or v == "":
            continue
        if isinstance(v, list):
            out[k] = v if rules["lists"] else ", ".join(str(x) for x in v)
        elif isinstance(v, dict):
            if rules["nested"]:
                out[k] = v
            else:
                out[k] = json.dumps(v, ensure_ascii=False)
        else:
            out[k] = v

    # 원문 앵커는 제시 단계에서 원본을 되찾는 데 쓴다. 중첩 불가 DB에서는
    # 개별 스칼라로 펼쳐 둬야 검색 결과에서 바로 읽을 수 있다.
    anchor = m.get("source_anchor") or {}
    if anchor:
        if rules["nested"]:
            out["source_anchor"] = anchor
        else:
            for k, v in anchor.items():
                if isinstance(v, (str, int, float, bool)):
                    out[f"anchor_{k}"] = v
    assets = m.get("assets") or []
    if assets:
        paths = [str(a.get("path")) for a in assets if isinstance(a, dict) and a.get("path")]
        out["asset_paths"] = paths if rules["lists"] else ", ".join(paths)
        out["asset_count"] = len(paths)

    out["file_path"] = m.get("file_path", "")
    return out


def validate(payload: list[dict], target: str) -> list[str]:
    """적재 전 페이로드 검증. 외부 패키지 없이 돈다."""
    rules = TARGET_RULES[target]
    errs = []
    seen = set()
    for p in payload:
        cid = p["id"]
        if cid in seen:
            errs.append(f"{cid}: 중복 id")
        seen.add(cid)
        if not p["text"].strip():
            errs.append(f"{cid}: 빈 embedding_text")
        for k, v in p["metadata"].items():
            if isinstance(v, list):
                if not rules["lists"]:
                    errs.append(f"{cid}.{k}: {target}는 리스트 메타데이터를 지원하지 않음")
                elif any(not isinstance(x, str) for x in v):
                    errs.append(f"{cid}.{k}: 리스트 원소가 문자열이 아님")
            elif isinstance(v, dict) and not rules["nested"]:
                errs.append(f"{cid}.{k}: {target}는 중첩 객체를 지원하지 않음")
            elif not isinstance(v, (str, int, float, bool, list, dict)):
                errs.append(f"{cid}.{k}: 지원하지 않는 타입 {type(v).__name__}")
    return errs


def build_payload(kb: Path, target: str) -> list[dict]:
    rules = TARGET_RULES[target]
    return [
        {
            "id": r["manifest"]["chunk_id"],
            "text": r["embedding"]["embedding_text"],
            "metadata": flatten_metadata(r["manifest"], rules),
        }
        for r in load_records(kb)
    ]


def embed(texts: list[str], model: str) -> list[list[float]]:
    """지연 임포트. 폐쇄망 기본값은 로컬 bge-m3 (근거: kb/chunks/v3-korean-rag.md)."""
    if model == "bge-m3":
        from sentence_transformers import SentenceTransformer  # noqa: PLC0415

        return SentenceTransformer("BAAI/bge-m3").encode(
            texts, normalize_embeddings=True, show_progress_bar=True
        ).tolist()
    if model.startswith("openai"):
        import openai  # noqa: PLC0415

        name = "text-embedding-3-large" if model.endswith("large") else "text-embedding-3-small"
        cli = openai.OpenAI()
        out = []
        for i in range(0, len(texts), 128):
            out += [d.embedding for d in cli.embeddings.create(model=name, input=texts[i : i + 128]).data]
        return out
    if model == "cohere":
        import cohere  # noqa: PLC0415

        cli = cohere.Client()
        out = []
        for i in range(0, len(texts), 96):
            out += cli.embed(
                texts=texts[i : i + 96], model="embed-multilingual-v3.0", input_type="search_document"
            ).embeddings
        return out
    raise SystemExit(f"지원하지 않는 모델: {model}")


def upload(payload: list[dict], vectors, target: str, args) -> None:
    ids = [p["id"] for p in payload]
    texts = [p["text"] for p in payload]
    metas = [p["metadata"] for p in payload]

    if target == "jsonl":
        out = Path(args.out or "vectors.jsonl")
        with out.open("w", encoding="utf-8") as f:
            for p, v in zip(payload, vectors):
                f.write(json.dumps({**p, "vector": v}, ensure_ascii=False) + "\n")
        print(f"{len(payload)}건 → {out}")
        return

    if target == "chromadb":
        import chromadb  # noqa: PLC0415

        col = chromadb.PersistentClient(path=args.path or "./chroma").get_or_create_collection(
            args.collection
        )
        col.upsert(ids=ids, documents=texts, metadatas=metas, embeddings=vectors)
    elif target == "qdrant":
        from qdrant_client import QdrantClient  # noqa: PLC0415
        from qdrant_client.models import Distance, PointStruct, VectorParams  # noqa: PLC0415

        cli = QdrantClient(url=args.url or "http://localhost:6333")
        cli.recreate_collection(
            args.collection,
            vectors_config=VectorParams(size=len(vectors[0]), distance=Distance.COSINE),
        )
        cli.upsert(
            args.collection,
            points=[
                PointStruct(id=i, vector=v, payload={**m, "chunk_id": cid, "text": t})
                for i, (cid, t, m, v) in enumerate(zip(ids, texts, metas, vectors))
            ],
        )
    elif target == "pinecone":
        from pinecone import Pinecone  # noqa: PLC0415

        idx = Pinecone().Index(args.collection)
        for i in range(0, len(ids), 100):
            idx.upsert(
                [
                    {"id": c, "values": v, "metadata": m}
                    for c, v, m in zip(ids[i : i + 100], vectors[i : i + 100], metas[i : i + 100])
                ]
            )
    elif target == "faiss":
        import faiss  # noqa: PLC0415
        import numpy as np  # noqa: PLC0415

        arr = np.array(vectors, dtype="float32")
        index = faiss.IndexFlatIP(arr.shape[1])
        index.add(arr)
        p = Path(args.index_path or "./faiss_index")
        p.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(p / "index.faiss"))
        (p / "meta.jsonl").write_text(
            "\n".join(json.dumps({"id": c, **m}, ensure_ascii=False) for c, m in zip(ids, metas)),
            encoding="utf-8",
        )
    elif target == "weaviate":
        import weaviate  # noqa: PLC0415

        cli = weaviate.connect_to_local()
        col = cli.collections.get(args.collection)
        with col.batch.dynamic() as b:
            for c, t, m, v in zip(ids, texts, metas, vectors):
                b.add_object(properties={**m, "chunk_id": c, "text": t}, vector=v)
        cli.close()
    print(f"{len(payload)}건 적재 완료 → {target}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kb", type=Path, default=Path("kb"))
    ap.add_argument("--target", choices=sorted(TARGET_RULES), required=True)
    ap.add_argument("--model", default="bge-m3")
    ap.add_argument("--collection", default="ainative-v3")
    ap.add_argument("--dry-run", action="store_true", help="외부 패키지 없이 페이로드만 검증")
    ap.add_argument("--path")
    ap.add_argument("--url")
    ap.add_argument("--index-path")
    ap.add_argument("--out")
    a = ap.parse_args()

    payload = build_payload(a.kb, a.target)
    errs = validate(payload, a.target)
    if errs:
        print(f"페이로드 검증 실패 {len(errs)}건:", file=sys.stderr)
        for e in errs[:20]:
            print(f"  {e}", file=sys.stderr)
        return 1

    keys = sorted({k for p in payload for k in p["metadata"]})
    print(f"[{a.target}] 청크 {len(payload)}건 검증 통과")
    print(f"  메타데이터 필드: {', '.join(keys)}")
    print(f"  리스트 허용={TARGET_RULES[a.target]['lists']} 중첩 허용={TARGET_RULES[a.target]['nested']}")
    if a.dry_run:
        print("  dry-run — 임베딩·적재는 건너뜁니다")
        return 0

    vectors = embed([p["text"] for p in payload], a.model)
    upload(payload, vectors, a.target, a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
