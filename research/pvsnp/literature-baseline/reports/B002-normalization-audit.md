# B002 정규화·관계 색인 검사

검사일: 2026-09-04 KST

판정: **통과.** B002의 6,233개 출현을 전부 파싱했고, MR 키 기준 5,472개 후보 레코드와 378개 미검증 관계 후보 묶음을 만들었다. 원시 `intake/`는 수정하지 않았다.

## 1. 검사 대상과 방법

[`../catalog/B002-normalization-contract.md`](../catalog/B002-normalization-contract.md)에 따라 [`../scripts/build_b002_catalog.py`](../scripts/build_b002_catalog.py)를 검사 우선으로 작성했다. 파서는 중첩 중괄호·여러 줄 값·중복 비필수 필드와 MathSciNet의 실제 비정규 레코드를 처리한다. 정규화 값은 연결 신호일 뿐 원문 필드를 대체하지 않는다.

입력 검사는 보고서의 계수를 전사하지 않고 다음 실물을 다시 읽어 수행했다.

- `manifests/B002.json`의 63개 artifact 경로·바이트·SHA-256·레코드 수
- `batches/B002-queries.tsv`와 수집기 파일의 SHA-256
- 자동 수집 60개 분야의 `result.json` 전건
- 수동 수집 3개 분야의 manifest metadata
- `intake/B002/mathscinet/`에 실제 존재하는 123개 파일 전건

63개 BibTeX 파일의 바이트·해시·레코드 수, 60개 `result.json`의 분야·검색식·결과 수·export 수·정렬·상태가 모두 manifest와 일치했다. 예상하지 않은 파일과 누락 파일은 0개였다. 요청 MSC 코드와 분야 가족 일치 수도 BibTeX `MRCLASS`에서 다시 계산해 manifest와 일치했다.

## 2. 파싱과 고유 후보

| 항목 | 결과 |
|---|---:|
| 입력 분야 | 63 |
| BibTeX 출현 | 6,233 |
| 파싱 완료 | 6,233 |
| 파싱하지 못한 출현 | 0 |
| 고유 MR 후보 | 5,472 |
| 둘 이상의 분야에 나온 MR 후보 | 622 |
| 반복 출현 중 첫 출현을 뺀 수 | 761 |
| 같은 MR 키의 서지 필드 충돌 | 0 |

반복 후보의 분야 출현 횟수 분포는 2회 518개, 3회 80개, 4회 15개, 5회 7개, 6회 2개다. 같은 MR 키의 출현만 하나의 후보 레코드로 모았고, 원시 파일·파일 해시·MSC 분야·검색식·검색 내 순위·수집 방식을 모든 출현에 보존했다.

고유 후보의 출판형태는 단행본 4,776개, 논문 376개, 단행본 수록 글 302개, 학회록 수록 글 13개, 학회록 5개다. DOI가 있는 후보는 2,762개다. 이 분포는 B002가 `-00/-01/-02` 기준 전거 검색의 인용순 첫 페이지라는 성격을 반영한다. 논문·학회록이 적다는 사실은 해당 분야에 그런 문헌이 없다는 뜻이 아니다.

## 3. 관계 후보

서로 다른 MR 키는 한 레코드로 병합하지 않았다. 다음 세 종류의 검토 묶음만 만들었다.

| 관계 후보 | 묶음 수 | 판정 의미 |
|---|---:|---|
| `same_doi_candidate` | 14 | 같은 DOI를 가진 서로 다른 MR 레코드. DOI 재사용·다권본·중복·판본 관계를 실제 출판 기록에서 판정해야 한다. |
| `same_bibliographic_fingerprint_candidate` | 10 | 정규화 제목·저작자 역할과 목록·연도가 같다. 다권본처럼 같은 표면 서지가 다른 대상을 가리킬 수 있다. |
| `edition_or_version_candidate` | 354 | 제목·저작자 신호는 같고 연도·판본·출판 맥락 중 하나 이상이 다르다. 같은 저작 여부와 관계 종류는 아직 확정하지 않았다. |

예를 들어 같은 DOI `10.1090/gsm/014`를 가진 `MR1415616`과 `MR1817225`, 같은 제목·저작자의 여러 판본인 *The probabilistic method* 4개 MR 레코드는 모두 독립 후보로 남아 있다. 반대로 제목만 같거나 저작자만 같은 레코드는 자동 연결하지 않았다. 관계 파일의 모든 상태는 `unverified_candidate`다.

## 4. 원자료 예외

예외는 원문을 고쳐 숨기지 않고 후보 레코드와 manifest에 기록했다.

- `MR1351209`는 정오표 레코드이며 `YEAR={}`다. 정규화 연도는 `null`, 상태는 `missing_year`다.
- 105개 후보는 `[1991]`, `[1995?]`, `1981/82`, `[2020] \copyright 2020`과 같은 비정규 연도다. 유일한 네 자리 연도는 파생 값으로 보존하고 `noncanonical_year`를 붙였다.
- 21개 후보는 `EDITION` 필드가 두 번 나온다. 예를 들어 `MR961259`는 `Second`와 `Russian`을 함께 가진다. 두 값을 원문 순서대로 모두 보존했다.
- `MR603624`와 `MR949448`의 제목 값에는 MathSciNet export가 만든 초과 닫는 중괄호가 하나씩 있다. 파서는 원문 값을 보존하고 `extra_closing_brace:title` 복구 표지를 붙였다.
- 저자와 편집자가 모두 없는 후보는 `MR855244`, `MR1310114`, `MR2280306`, `MR3074972` 네 개다. 자동 저작자 기반 관계를 만들지 않았다.
- 232개 후보에는 정규화기가 의미를 확정하지 않은 TeX 명령이 있다. 주로 `\cyr`, `\cprime` 계열의 MathSciNet 키릴 문자 전사다. 명령 이름을 삭제하지 않고 평문 투영에 남겼으므로, 이 후보들의 제목·저자 기반 관계는 원문 대조가 필요하다.
- 65개 DOI 필드는 BibTeX가 underscore를 `\_`로 이스케이프했다. 정규화 DOI에서는 `_`로 복원하며 원시 필드는 그대로 보존한다. 오래된 Wiley DOI 한 건의 `;2-V`는 식별자 접미부이므로 DOI 분리자로 해석하지 않는다.

예외 후보는 [`../catalog/B002-candidates.jsonl`](../catalog/B002-candidates.jsonl)의 `parse_warnings`, `duplicate_fields`, `normalized.normalization_warnings`, `normalized.unrecognized_tex_commands`로 찾을 수 있다. 예외 집계는 [`../manifests/B002-normalized.json`](../manifests/B002-normalized.json)에 있다.

## 5. 분야별 검토 준비 통계

`export / total`은 B002가 저장한 수와 MathSciNet 검색 전체 hit 수다. `cross-field`는 같은 MR 후보가 다른 분야에도 나온 출현 수다. `requested / family`는 요청한 정확한 `-00/-01/-02` 코드와 해당 두 자리 분야 가족이 `MRCLASS`에 실제로 보인 수다. `type composition`은 원시 BibTeX 출현 기준이다.

| MSC | export / total | type composition | cross-field | DOI | requested / family | exceptions |
|---|---:|---|---:|---:|---:|---|
| `00` | 100 / 583 | article:3, book:95, incollection:2 | 34 | 42 | 100 / 100 | duplicate-field:5 |
| `01` | 100 / 1,118 | article:32, book:61, incollection:6, inproceedings:1 | 0 | 45 | 40 / 97 | year-noncanonical:1 |
| `03` | 100 / 1,749 | book:98, incollection:2 | 11 | 46 | 100 / 100 | — |
| `05` | 100 / 1,536 | article:1, book:96, incollection:3 | 33 | 41 | 100 / 100 | duplicate-field:1 |
| `06` | 100 / 223 | article:4, book:92, incollection:4 | 24 | 47 | 100 / 100 | year-noncanonical:1 |
| `08` | 100 / 145 | article:10, book:69, incollection:19, inproceedings:1, proceedings:1 | 21 | 36 | 100 / 100 | creator-empty:1, year-noncanonical:5 |
| `11` | 100 / 1,090 | article:1, book:96, incollection:3 | 16 | 64 | 100 / 100 | year-noncanonical:1, duplicate-field:1 |
| `12` | 100 / 314 | article:6, book:89, incollection:4, proceedings:1 | 22 | 37 | 100 / 100 | year-noncanonical:2, duplicate-field:2 |
| `13` | 100 / 407 | article:2, book:91, incollection:7 | 35 | 45 | 100 / 100 | year-noncanonical:1, duplicate-field:1 |
| `14` | 100 / 557 | article:2, book:97, incollection:1 | 22 | 57 | 100 / 100 | year-noncanonical:1, duplicate-field:3 |
| `15` | 100 / 1,076 | article:4, book:95, incollection:1 | 20 | 51 | 100 / 100 | — |
| `16` | 100 / 488 | article:2, book:96, incollection:2 | 27 | 40 | 100 / 100 | — |
| `17` | 100 / 232 | article:6, book:77, incollection:15, inproceedings:2 | 23 | 51 | 100 / 100 | creator-empty:1, year-noncanonical:2 |
| `18` | 100 / 280 | article:6, book:87, incollection:5, inproceedings:2 | 26 | 49 | 100 / 100 | — |
| `19` | 89 / 89 | article:10, book:40, incollection:36, inproceedings:3 | 6 | 41 | 89 / 89 | creator-empty:1, year-noncanonical:5 |
| `20` | 100 / 946 | book:100 | 18 | 36 | 100 / 100 | — |
| `22` | 100 / 421 | article:4, book:93, incollection:3 | 35 | 54 | 100 / 100 | — |
| `26` | 100 / 1,401 | article:4, book:96 | 46 | 43 | 100 / 100 | year-noncanonical:2 |
| `28` | 100 / 637 | book:100 | 47 | 38 | 100 / 100 | — |
| `30` | 100 / 859 | article:1, book:99 | 29 | 47 | 100 / 100 | year-noncanonical:2 |
| `31` | 100 / 156 | article:14, book:72, incollection:12, inproceedings:1, proceedings:1 | 18 | 55 | 100 / 100 | year-noncanonical:4 |
| `32` | 100 / 378 | article:4, book:93, incollection:3 | 15 | 50 | 100 / 100 | year-noncanonical:2 |
| `33` | 100 / 394 | article:7, book:88, incollection:5 | 22 | 48 | 100 / 100 | year-noncanonical:1, duplicate-field:3 |
| `34` | 100 / 1,570 | article:4, book:96 | 30 | 53 | 100 / 100 | — |
| `35` | 100 / 2,081 | article:3, book:97 | 20 | 57 | 100 / 100 | — |
| `37` | 100 / 646 | article:5, book:86, incollection:9 | 20 | 72 | 100 / 100 | year-noncanonical:1 |
| `39` | 100 / 244 | article:16, book:80, incollection:4 | 13 | 54 | 100 / 100 | — |
| `40` | 100 / 132 | article:17, book:80, incollection:3 | 4 | 33 | 100 / 100 | year-noncanonical:6, brace-recovery:1, duplicate-field:1 |
| `41` | 100 / 538 | article:7, book:88, incollection:5 | 14 | 51 | 100 / 100 | year-noncanonical:1 |
| `42` | 100 / 770 | article:7, book:90, incollection:3 | 29 | 53 | 100 / 100 | — |
| `43` | 100 / 156 | article:8, book:80, incollection:12 | 22 | 53 | 100 / 100 | year-noncanonical:2, duplicate-field:2 |
| `44` | 100 / 162 | article:7, book:86, incollection:7 | 8 | 30 | 100 / 100 | year-empty:1, year-noncanonical:2, duplicate-field:1 |
| `45` | 100 / 198 | article:2, book:96, incollection:2 | 9 | 49 | 100 / 100 | year-noncanonical:4 |
| `46` | 100 / 1,493 | article:1, book:99 | 59 | 40 | 100 / 100 | — |
| `47` | 100 / 1,248 | article:2, book:98 | 56 | 51 | 100 / 100 | duplicate-field:1 |
| `49` | 100 / 1,386 | book:100 | 40 | 57 | 100 / 100 | — |
| `51` | 100 / 784 | article:1, book:96, incollection:3 | 13 | 50 | 100 / 100 | year-noncanonical:1 |
| `52` | 100 / 369 | article:3, book:80, incollection:17 | 19 | 54 | 100 / 100 | year-noncanonical:1 |
| `53` | 100 / 948 | article:4, book:93, incollection:3 | 24 | 47 | 100 / 100 | — |
| `54` | 100 / 669 | article:3, book:91, incollection:6 | 25 | 43 | 100 / 100 | — |
| `55` | 100 / 430 | article:5, book:90, incollection:4, inproceedings:1 | 42 | 42 | 100 / 100 | year-noncanonical:1 |
| `57` | 100 / 512 | article:7, book:85, incollection:8 | 43 | 56 | 100 / 100 | — |
| `58` | 100 / 913 | article:2, book:96, incollection:2 | 42 | 52 | 100 / 100 | — |
| `60` | 100 / 2,323 | book:100 | 22 | 52 | 100 / 100 | duplicate-field:1 |
| `62` | 100 / 3,651 | article:8, book:92 | 10 | 52 | 100 / 100 | — |
| `65` | 100 / 2,808 | book:95, incollection:5 | 23 | 59 | 100 / 100 | duplicate-field:1 |
| `68` | 100 / 2,131 | book:100 | 23 | 48 | 100 / 100 | — |
| `70` | 100 / 781 | article:7, book:89, incollection:4 | 16 | 49 | 99 / 99 | year-noncanonical:1, brace-recovery:1 |
| `74` | 100 / 542 | article:4, book:95, incollection:1 | 11 | 63 | 100 / 100 | year-noncanonical:6 |
| `76` | 100 / 940 | article:6, book:91, incollection:3 | 24 | 52 | 100 / 100 | year-noncanonical:1 |
| `78` | 100 / 438 | article:3, book:96, incollection:1 | 16 | 48 | 100 / 100 | year-noncanonical:1, duplicate-field:3 |
| `80` | 100 / 157 | article:7, book:88, incollection:5 | 8 | 52 | 100 / 100 | creator-empty:1, year-noncanonical:4 |
| `81` | 100 / 4,313 | article:11, book:87, incollection:2 | 28 | 63 | 100 / 100 | — |
| `82` | 100 / 1,868 | article:15, book:78, incollection:7 | 18 | 58 | 100 / 100 | year-noncanonical:1 |
| `83` | 100 / 930 | article:12, book:84, incollection:3, inproceedings:1 | 10 | 52 | 100 / 100 | — |
| `85` | 85 / 85 | article:15, book:64, incollection:6 | 5 | 49 | 85 / 85 | year-noncanonical:15 |
| `86` | 100 / 210 | article:23, book:68, incollection:6, inproceedings:1, proceedings:2 | 11 | 56 | 73 / 73 | year-noncanonical:3 |
| `90` | 100 / 3,258 | article:4, book:95, incollection:1 | 32 | 46 | 100 / 100 | — |
| `91` | 100 / 1,759 | article:2, book:95, incollection:2, inproceedings:1 | 8 | 61 | 100 / 100 | year-noncanonical:1 |
| `92` | 100 / 708 | article:5, book:94, incollection:1 | 9 | 54 | 100 / 100 | year-noncanonical:1 |
| `93` | 100 / 2,930 | article:5, book:94, incollection:1 | 19 | 63 | 100 / 100 | — |
| `94` | 100 / 1,281 | article:4, book:73, incollection:23 | 7 | 57 | 100 / 100 | year-noncanonical:1 |
| `97` | 59 / 59 | article:30, book:15, incollection:14 | 1 | 33 | 59 / 59 | year-noncanonical:23 |

분야 `19`, `85`, `97`만 전체 결과를 저장했다. 나머지 60개 분야는 상위 100에서 잘렸다. `01`, `70`, `86`은 각각 40, 99, 73개만 요청 코드가 그대로 보이고 분야 가족도 97, 99, 73개에 그친다. 이는 수집 오류가 아니라 MathSciNet 검색의 역사적 MSC·연결 분류 특성이므로 후속 공개 자료원 대조에서 실제 분류 이력을 확인해야 한다.

특히 `68`은 2,131개 결과 중 단행본 100개만 남았다. 이 표본은 표준서 후보를 주지만 학회록·기술보고·최신 프리프린트·핵심 원 논문을 대표하지 않는다. [`B002-public-source-audit.md`](B002-public-source-audit.md)는 DBLP, zbMATH Open, OpenAlex, arXiv, ECCC, DROPS/LIPIcs, Theory of Computing과 공식 STOC·FOCS·CCC 페이지에서 이 누락 유형을 실제 레코드로 확인했다.

## 6. 산출물 무결성과 한계

파생물은 다음과 같다. 현재 해시는 [`../manifests/B002-normalized.json`](../manifests/B002-normalized.json)이 정본이다.

- `catalog/B002-candidates.jsonl`: 5,472행
- `catalog/B002-relations.jsonl`: 378행
- `manifests/B002-normalized.json`: 입력·출력 해시, 계수, 예외와 분야별 통계

검사는 14건이며 실제 gitignored B002 입력이 있으면 6,233건 전수 통합 검사를 포함한다. 같은 입력으로 생성기를 다시 실행해 후보·관계·manifest 바이트가 변하지 않는지도 별도로 대조한다.

B002 BibTeX에는 초록이 없다. 따라서 이 단계는 실제 제목·저자·분류·서지·출판 맥락을 분야별로 검토할 수 있게 만들었지만 기준 핵심층 채택을 끝내지 않았다. 초록·원문 역할·후속 채택·비판과 venue 누락은 공개 자료원 조사에서 확인해야 한다. 인용순이나 이 색인의 자동 관계만으로 핵심층을 채택하지 않는다.

## 7. B003 판정과 재개 좌표

현재 증거로 인증 B003 묶음은 열지 않는다. B002의 확인된 공백은 공개 DB와 공식 venue가 먼저 조사할 수 있는 학회록·기술보고·프리프린트·역사적 분류·판본 관계다. 공개 경로를 소진하기 전에 Web of Science·Scopus·ACM DL·IEEE Xplore·PQDT 검색을 사용자 행동으로 여는 근거는 없다.

다음 AI 작업은 후보 색인을 분야별로 읽으면서 공개 자료원의 제목·초록·분류·venue 기록을 대조하고 기준 핵심층 후보를 판정하는 일이다. 공개 대조 뒤에도 특정 핵심 후보나 학위논문·학회록·인용 관계가 공개 경로에서 재현되지 않을 때만 그 결손을 검색식과 함께 B003으로 연다. 이는 B003이 영구히 불필요하다는 판정이나 문헌 집합 완료 판정이 아니다.
