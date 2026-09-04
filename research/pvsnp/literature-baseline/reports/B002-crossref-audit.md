# B002 Crossref DOI 전수 대조 검사

검사일: 2026-09-04 KST

판정: **DOI 2,748개 전수 수집·무결성 검사 완료. 제목 불일치 49건, 유사 제목 49건, 포함형 제목 148건의 상세 처분도 완료했다.**

## 1. 범위와 이용 경계

B002의 5,472개 MR 후보 중 DOI가 있는 후보는 2,762개다. 한 DOI를 공유하는 서로 다른 MR 묶음이 14개이므로 고유 DOI는 2,748개다. [`../catalog/B002-public-enrichment-contract.md`](../catalog/B002-public-enrichment-contract.md)에 따라 Crossref 공개 REST API를 초당 4회 이하, 동시 요청 1개로 호출했다. Crossref의 [공식 REST 설명](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)과 [현행 rate-limit 안내](https://www.crossref.org/blog/announcing-changes-to-rest-api-rate-limits/)의 공개 pool 경계 안에서 수행했다.

원시 API 응답은 `intake/B002-public/crossref/`에 DOI별로 원자 저장했고 Git에서 추적하지 않는다. PDF·원문을 요청하지 않았고 크리덴셜을 사용하지 않았다. 일부 Crossref metadata에 포함된 초록 전문도 추적 색인에는 복제하지 않고 존재 여부만 기록했다.

## 2. 수집 결과와 무결성

| 항목 | 결과 |
|---|---:|
| DOI가 있는 MR 후보 | 2,762 |
| 고유 DOI | 2,748 |
| 원시 응답 파일 | 2,748 |
| `found` | 2,693 |
| `found_alias` | 55 |
| 현행 `crossref_not_found` | 0 |
| 임시 파일·깨진 envelope | 0 |

`found_alias`는 요청 DOI가 Crossref의 HTTP redirect를 거쳐 다른 정규 DOI로 반환된 경우다. 최초 endpoint, 최종 endpoint, 요청 DOI와 반환 DOI를 모두 보존했다. redirect 대상 DOI와 응답 `message.DOI`가 일치할 때만 alias로 허용한다.

원시 파일 2,748개의 파일 SHA-256·바이트·HTTP 상태를 [`../manifests/B002-crossref.json`](../manifests/B002-crossref.json)의 artifact 전건과 독립 대조했다. 각 envelope의 응답 문자열 SHA-256, 파생 색인의 원시 파일 참조와 candidate ID도 다시 검사했으며 결함은 0건이었다. 같은 입력에서 [`../catalog/B002-crossref.jsonl`](../catalog/B002-crossref.jsonl)과 manifest를 재생성했을 때 바이트가 변하지 않았다.

Crossref 유형은 book 1,357, monograph 806, journal article 313, book chapter 121, edited book 103, other 24, reference book 17, proceedings article 6, report 1이다. 349개 응답에는 초록이 있었고, 18개에는 명시 relation, 56개에는 assertion이 있었다.

## 3. 정규화 결함 두 건의 수리

전수 실행은 파생 DOI의 두 결함을 실제 요청에서 드러냈다.

1. 오래된 Wiley DOI `10.1002/(SICI)…;2-V`의 세미콜론은 여러 DOI의 구분자가 아니라 식별자 일부다. DOI 필드 하나를 식별자 하나로 고쳤다.
2. BibTeX가 underscore를 `\_`로 이스케이프한 DOI 65개는 처음에 Crossref 404를 반환했다. `_`로 복원하면 65/65가 Crossref agency와 work endpoint에서 성공했다.

두 사례를 선행 실패 검사로 고정하고 후보·manifest·Crossref 색인을 전부 재생성했다. 잘못된 `\_` 요청 응답 65개는 삭제하지 않고 `intake/B002-public/crossref-invalid-doi-escape/`에 격리했다. 현행 효과와 집합 검산은 [`B002-crossref-not-found-review.md`](B002-crossref-not-found-review.md)에 있다.

## 4. 제목 대조

Crossref의 JATS/MathML 태그를 평문으로 투영한 뒤 B002와 같은 제목 정규화기를 사용했다. 문자열 결과는 검토 대기열을 나눌 뿐 DOI 정확성을 자동 판정하지 않는다.

| 자동 분류 | DOI 수 | 현재 처분 |
|---|---:|---|
| `exact_title` | 2,501 | 서지 일치 신호. 저자·판본 검토를 대신하지 않음 |
| `title_containment` | 148 | 148/148 DOI, 153 candidate link 상세 검토 완료 |
| `similar_title` | 49 | 49/49 상세 검토 완료 |
| `title_mismatch_review` | 49 | 49/49 상세 검토 완료 |
| `missing_crossref_title` | 1 | 독립 공식 record로 1/1 대조 완료 |

파생 대기열은 [`../catalog/B002-crossref-title-review.jsonl`](../catalog/B002-crossref-title-review.jsonl), 계수와 해시는 [`../manifests/B002-crossref-title-review.json`](../manifests/B002-crossref-title-review.json)에 있다.

### 불일치 49건

실제 원 필드·container·ISBN·저자와 공식 record를 대조한 결과는 다음과 같다.

| 처분 | 수 |
|---|---:|
| 후보 책의 장·index·appendix DOI | 24 |
| 후보와 무관한 잘못된 DOI | 16 |
| 관련되지만 별도 작업 | 7 |
| Crossref deleted-DOI placeholder | 1 |
| 같은 작업의 제목 변형 | 1 |

예를 들어 `MR2981171`의 *Category theory for computing science*에 붙은 DOI는 Crossref에서 ATLAS diphoton 물리 논문을 가리켜 `wrong_identifier`로 판정했다. 반대로 SIAM·Elsevier·De Gruyter 책에서 Crossref 제목이 장이나 index인 경우에는 container와 ISBN이 후보 책과 일치해 `component_of_candidate_work`로 보존했다. 49행과 근거는 [`B002-crossref-title-mismatch-review.md`](B002-crossref-title-mismatch-review.md)에 있다.

### 유사 제목 49건

상세 대조 결과 title/TeX 표기 변형 41, 재발행·새 판 3, 책 component 2, 관련 별도 작업 1, 다른 권 DOI 충돌 1, 미확정 1이다. `10.1090/gsm/117`은 Crossref의 *An Epsilon of Room I*와 B002 `MR2780010`의 *II*가 달라 권 충돌로 판정했다. Featherstone 저작 1건은 Crossref의 *Robot Dynamics Algorithms*와 B002의 *Rigid Body Dynamics Algorithms* 관계를 현재 근거로 확정하지 않았다. 상세 묶음과 전건 검산은 [`B002-crossref-similar-title-review.md`](B002-crossref-similar-title-review.md)에 있다.

### 포함형 제목 148건

공유 DOI 때문에 148 DOI는 153 candidate link를 만든다. 전건에서 저자·ISBN·container·권·판본을 대조한 결과 title variant 89, 재발행·판본 23, 책 component 30, 다른 권·부분 식별자 충돌 5, wrong identifier 3, set/generic DOI 2, 관련 별도 작업 1로 처분했고 미확정은 0이다. 권·판본·component는 원 MR 레코드를 합쳐 없애지 않는다. 세 slice의 DOI 집합과 집계는 [`B002-crossref-containment-review.md`](B002-crossref-containment-review.md)에 있다.

### Crossref 제목 누락 1건

`MR1784729`의 DOI `10.1070/RD2000v005n01ABEH000123`은 Crossref work record에 title이 없지만, MathNet과 저널 공식 페이지가 B002와 같은 제목·저자·연도·쪽·DOI를 제공한다. 따라서 외부 record 일치로 처분했다. 근거는 [`B002-crossref-missing-title-review.md`](B002-crossref-missing-title-review.md)에 있다.

## 5. Crossref relation

relation이 있는 source DOI는 18개이며 23개 assertion을 가진다.

| 관계 | source DOI 수 | assertion 수 |
|---|---:|---:|
| correction | 4 | 4 |
| is-translation-of | 2 | 3 |
| new_version | 1 | 1 |
| is-identical-to | 10 | 12 |
| has-preprint | 1 | 1 |
| is-same-as | 1 | 2 |

correction 4건과 new version 1건은 해당 후보를 실제 사용하기 전에 target을 먼저 대조할 의무를 만든다. relation 자체를 내용 동일성이나 최신 권위로 해석하지 않는다. source 18행과 target 22개의 대조 결과는 [`B002-crossref-relations-review.md`](B002-crossref-relations-review.md)에 있다.

## 6. 남은 작업과 B003 영향

- exact-title도 자동 핵심층 승인이 아니다. 최종 후보는 실제 초록·목차·원문 역할과 후속 채택·비판을 확인한다.
- DOI 없는 2,710개 후보는 zbMATH·DBLP·arXiv·ISBN·제목/저자 및 공식 publisher 경로로 계속 대조한다.
- correction/new-version 5건은 판독 전에 target 범위를 확인한다.

Crossref 공개 대조는 인증 B003을 요구하지 않고 진행됐다. 오히려 MathSciNet DOI 필드의 실제 오류·component DOI·alias를 공개 자료로 구별했다. 현재도 사용자 행동을 열 근거는 없으며, 공개 자료원 대조를 계속한다.
