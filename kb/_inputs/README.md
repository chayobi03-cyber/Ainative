# 빌더 입력 (v1 / v2.3 원본 청크)

`tools/build_v3.py`가 요구하는 입력이다. **이 디렉터리가 없으면 청크를 재빌드할 수 없다.**

이전에는 Google Drive `Ainative/Rawdata`에만 있었고, 그 Drive는 개인 계정 소유였다.
접근이 끊기면 재빌드가 영구 불가해지므로 저장소로 반입했다
(`docs/HANDOVER.md` §A-1).

## 구성

| 경로 | 내용 | 출처 |
|---|---|---|
| `v1/rag_chunks/` | v1 청크 47개 | `ai_wiki_rag_complete-1.zip` |
| `v23/chunks/` | v2.3 청크 135개 | `Claude-Code-2026-베스트-프랙티스-RAG-지식-베이스-v2-3.zip` |
| `v23/chunk-manifest.jsonl` | v2.3 매니페스트 | 위와 동일 |

## 원본 아카이브 지문

반입은 zip을 풀어 필요한 부분만 담은 것이다. 원본과 대조가 필요하면 아래 SHA256으로
확인한다. 원본 zip 자체는 저장소에 넣지 않았다 — 풀린 파일이 diff 가능하고,
zip은 같은 내용을 두 번 갖는 것이기 때문이다.

```
b2f9228973d87884f934b7f771561748008b6c8e096e935e4658c23c76044591  ai_wiki_rag_complete-1.zip
4b79ca36240695392e374d65a4defffcbcfa82c9db15f396820b9e2f3ee6e61e  Claude-Code-2026-...-v2-3.zip
```

원본 zip에는 여기 담지 않은 것도 있다(v2.3 위키 문서 22종, 임베딩 가이드,
구 업로드 스크립트 6종). 위키 문서는 `kb/docs/`로, 원본 리서치는 `kb/sources/`로
이미 반입됐다. 구 업로드 스크립트는 `tools/upload_vectors.py`가 대체하므로 버렸다.

## 재빌드

```bash
python3 tools/build_v3.py \
  --v1 kb/_inputs/v1/rag_chunks \
  --v23-chunks kb/_inputs/v23/chunks \
  --v23-manifest kb/_inputs/v23/chunk-manifest.jsonl \
  --authored kb/authored \
  --out kb
./tests/run_checks.sh
```

## 주의

- **이 디렉터리는 색인 대상이 아니다.** `kb/ingestion.yaml`의 exclude에 있다.
  넣으면 v3 청크와 같은 내용이 두 번 색인된다.
- 여기 있는 청크는 **구 스키마**다(v1은 `rag-*-001`, v2.3은 `chunk.NNN`).
  직접 쓰지 말고 빌더를 통해서만 쓴다.
