# B002 DOI-없는 후보 zbMATH 전수 matching 검사

검사일: 2026-09-04 KST

판정: **수집·형식 검사는 통과, 서지 연결은 검토 대기.** DOI가 없는 B002 후보 2,710개를 zbMATH citation matcher의 28개 순차 POST batch로 전수 대조했다. 28개 원시 응답과 2,710개 query/result 위치를 보존했으며 자동 병합은 하지 않았다.

## 수집과 무결성

[`../catalog/B002-zbmath-matching-contract.md`](../catalog/B002-zbmath-matching-contract.md)에 따라 batch당 최대 100, 동시성 1로 실행했다. `m=0`, `n=3`이므로 각 query에 검토 후보 3개, 총 8,130개 result가 돌아왔다. 이는 2,710개가 모두 zbMATH에 있다는 뜻이 아니라 matcher의 낮은 threshold 결과 전건을 보존했다는 뜻이다.

| 항목 | 결과 |
|---|---:|
| B002 DOI-없는 후보 | 2,710 |
| POST batch | 28 |
| 원시 envelope | 28 |
| query와 result-array 위치 | 2,710 / 2,710 |
| 반환 citation 후보 | 8,130 |
| manifest와 원시 경로 대칭차 | 0 |
| 파일 크기·SHA-256 불일치 | 0 |
| response-text SHA-256·배열 길이 불일치 | 0 |

초기 1초 간격 실행에서는 세 차례 HTTP 200 안의 per-query result가 배열이 아닌 형식 불완전 응답을 관찰했다. 이를 0건이나 부분 성공으로 저장하지 않았다. 실패 검사를 추가해 batch 전체를 재시도하고 요청 간격을 3초로 낮춘 뒤 28개를 완료했다. 완료 후 dry run은 `existing=28`, `pending=0`이었고, 같은 원시 입력에서 index와 manifest를 두 번 재생성한 SHA-256이 각각 변하지 않았다. 수집기 검사는 10건이다.

## 제목·연도 대기열

| 문자열 분류 | 후보 수 | 의미와 다음 대조 |
|---|---:|---|
| `exact_title_same_year` | 1,336 | 강한 후보 신호. creator·source·판본 확인 필요 |
| `exact_title_near_year` | 32 | online/print year 또는 판본 차이 가능 |
| `exact_title_other_or_missing_year` | 208 | 재발행·번역·다른 판본 또는 오탐 가능 |
| `title_containment` | 686 | 부제·series·권·언어 변형 또는 다른 저작 가능 |
| `fuzzy_candidates_only` | 448 | title exact/containment 없음; 자동 연결 금지 |
| **합계** | **2,710** | — |

예를 들어 `MR302944`는 1968년 *Special functions for scientists and engineers*와 같은 제목·연도의 Zbl `0167.34401`을 반환하고, 2004 Dover reprint도 별도 후보로 반환한다. 반대로 `MR295326` *Algebraic topology*는 다른 저자의 1989년 독일어 책을 첫 결과로 내므로 containment만으로 연결할 수 없다. 이 두 사례가 top score·문자열 하나로 병합하지 않는 이유다.

정확한 파생 index는 `catalog/B002-zbmath-matches.jsonl`, 계수·원시 파일 해시는 [`../manifests/B002-zbmath-matches.json`](../manifests/B002-zbmath-matches.json)에 있다. 다음 단계는 exact-title부터 creator·출판처·ISBN·판본을 대조하고, 448 fuzzy-only는 document search나 공식 publisher record로 재검색하는 것이다.
