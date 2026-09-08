23,755개 후보에 첫 원소부터 형식을 확인하고 같은 형식의 처리 가능한 원소를 제거하는 절차를 적용했다. 12회 반복 뒤 초록 추출 17,654건, 추가 자료 확보·판독 대상 6,101건으로 분리했고 `remaining.jsonl`은 비어 있다. 원본 `../paper-summary-candidates.jsonl`은 그대로 보존했다.

각 `groups/` 하위 디렉토리는 하나의 형식과 처리 결과를 담당한다. 여러 출처가 연결된 후보는 현재 묶음에 해당하는 출처에서 초록을 추출할 수 있으면 함께 처리한다. 추가 자료 대상으로 옮기는 조건은 확인한 로컬 출처 모두에서 사용할 초록을 얻지 못한 경우다. 먼저 처리한 묶음에 포함된 후보는 이후 묶음에서 다시 처리하지 않는다.

| 디렉토리 | 처리 | 후보 수 |
|---|---|---:|
| `groups/01-extracted-scopus-csv/` | Scopus CSV 초록 추출 | 15,364 |
| `groups/02-needs-source-mathscinet-fields-json/` | MathSciNet 필드 목록, 추가 자료·판독 | 5,138 |
| `groups/03-extracted-bibtex/` | ACM·IEEE BibTeX 초록 추출 | 1,265 |
| `groups/04-extracted-ris/` | WoS·ProQuest RIS 초록 추출 | 637 |
| `groups/05-needs-source-bibtex/` | BibTeX, 추가 자료·판독 | 382 |
| `groups/06-extracted-crossref-json/` | 저장된 Crossref JSON 초록 추출 | 386 |
| `groups/07-needs-source-scopus-csv/` | Scopus CSV, 추가 자료·판독 | 96 |
| `groups/08-needs-source-mathscinet-bibtex/` | MathSciNet BibTeX, 추가 자료·판독 | 304 |
| `groups/09-needs-source-ris/` | RIS, 추가 자료·판독 | 146 |
| `groups/10-needs-source-public-seed-json/` | 공개 서지 레코드, 추가 자료·판독 | 34 |
| `groups/11-extracted-captured-page/` | 저장된 웹 페이지의 Abstract 절 추출 | 2 |
| `groups/12-needs-source-author-page-evidence-json/` | 저자 페이지 근거 레코드, 추가 자료·판독 | 1 |

각 디렉토리의 파일은 다음과 같다.

- `members.jsonl`: 제거한 후보의 원래 JSONL 행. 같은 후보는 전체 묶음 중 한 곳에만 있다.
- `abstracts.jsonl`: 추출한 초록 값, 후보 ID, 원자료 필드와 위치, 출처 레코드 ID, 텍스트 SHA-256. 추출하지 않은 묶음에서는 빈 파일이다.
- `evidence.jsonl`: 실제 확인한 출처, 출처별 초록 수, 식별 불일치·HTTP 실패·추가 판독 사유.
- `format.py`: 해당 형식의 인식·추출 실행 파일. 공통 구현은 이 디렉토리 상위의 `partition.py`다.

같은 후보의 같은 형식에서 여러 내보내기 기록을 확보했으면 각 초록 값과 그 출처를 보존한다. 따라서 초록을 얻은 후보는 17,654개이고, 보존한 초록 값은 17,877개다.

초록 값은 원자료의 초록 필드 또는 경계가 확인된 Abstract 절에서 가져왔다. 필드 바깥의 구분자와 앞뒤 공백을 제거하고 본문을 보존한다. JSON 필드에 들어 있는 JATS/XML, HTML 엔터티, TeX 표기와 원자료의 수식 손상도 본문에 남는다. 메타데이터가 책의 설명이나 편집자 소개를 `abstract`로 제공했다면 그 값도 출처의 초록 필드로 보존한다. 이 결과는 각 값의 작성 주체나 원 논문과의 문자 단위 일치까지 확정하지 않는다.

BibTeX 구문 손상 7개 레코드는 실제 필드 경계를 확인했다. 그중 최종 BibTeX 추출 묶음에 사용된 4개 값에는 `source.parse_warning`이 있다. 자료에 이미 있는 `[EQUATION]` 같은 대체 표기도 원자료의 한계이며, 추출 과정에서 수식을 창작하지 않았다.

추가 자료·판독 묶음은 현재 확인한 자료로 초록을 확보하지 못했다는 뜻이다. 초록 필드 부재, 부재 안내문, 출처와 후보의 식별 미확정, 접근 실패, 로컬 원문의 명시적 초록 경계 부재를 `evidence.jsonl`에서 구별할 수 있다. 원 논문에 초록이 없다는 일반적 판정으로 사용하면 안 된다. 이번 실행은 추가 웹 수집을 하지 않았다.

`input.jsonl`은 기준 입력의 바이트 사본이고, `iterations.jsonl`은 각 반복의 첫 후보·제거 수·잔여 수를 기록한다. `observations.jsonl`은 전체 후보의 출처 관측값이며, `source-hashes.jsonl`은 확인한 로컬 파일 3,575개의 SHA-256이다. `verification.json`에는 모든 묶음의 거짓양성·거짓음성·추출문 불일치·보존 오류 검사 결과가 있다.

다음 명령은 `C:\math`에서 실행한다. 같은 저장소의 `scripts/build_b001_catalog.py`, `scripts/build_b002_catalog.py`와 기록된 로컬 원자료가 필요하다.

```powershell
# 전체 분할과 원자료 해시 검사
python research/pvsnp/literature-baseline/catalog/abstract-format-partition/partition.py verify

# 특정 묶음의 각 원소를 현재 원자료로 재검사
python research/pvsnp/literature-baseline/catalog/abstract-format-partition/groups/11-extracted-captured-page/format.py --check

# 지정한 후보 목록에서 해당 형식과 처리 조건에 맞는 모든 행 출력
python research/pvsnp/literature-baseline/catalog/abstract-format-partition/groups/01-extracted-scopus-csv/format.py --recognize --input research/pvsnp/literature-baseline/catalog/paper-summary-candidates.jsonl

# 해당 묶음의 초록을 원자료에서 다시 추출해 JSONL 출력
python research/pvsnp/literature-baseline/catalog/abstract-format-partition/groups/11-extracted-captured-page/format.py --extract

# 최초 입력부터 새 디렉토리에 전체 절차 재실행; 출력 디렉토리가 있으면 거절
python research/pvsnp/literature-baseline/catalog/abstract-format-partition/partition.py run --output research/pvsnp/literature-baseline/catalog/abstract-format-replay

# 기능·경계 사례와 실제 코퍼스 검사
python research/pvsnp/literature-baseline/catalog/abstract-format-partition/test_partition.py
python research/pvsnp/literature-baseline/catalog/abstract-format-partition/test_corpus.py
```

`tdd/`에 실패 확인과 통과 로그를 보존했다. 긴 CSV 필드, 초록 부재 안내문, 중복 출처, 손상된 BibTeX, RIS 연속행, 메타데이터 제목의 서식 태그, 잘린 웹 초록, 행 연결 오류와 결과 변조를 검사한다. 전수 검사는 원자료 필드와 추출 값을 대조하고, 기존 별도 초록 목록과의 가용성 대조 및 모든 후보의 보존을 확인한다. 현재 입력에 대한 검증을 통과했으며, 검사한 범위에서 거짓양성·거짓음성·추출문 불일치는 0건이다. 향후 다른 입력 형식까지 오류가 없다는 증명으로 확대하지 않는다.
