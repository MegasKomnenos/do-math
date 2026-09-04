# B002 DOI-없는 후보의 zbMATH matching 계약

## 범위

`B002-candidates.jsonl`에서 정규화 DOI가 없는 2,710개 MR 후보만 대상으로 한다. zbMATH citation matcher는 발견·연결 후보를 주는 fuzzy matcher이며, 결과 점수·확률·순서를 동일 저작이나 핵심성 판정으로 쓰지 않는다.

## 요청과 저장

1. 후보는 MR 번호순으로 고정하고 title, 정규화 creator, year, `n=3`, `m=0`, `f=latex`를 구조화 query로 보낸다.
2. 공식 최대치에 맞춰 batch당 100개 이하, 동시성 1로 POST한다. HTTP 200이며 `results.length == queries.length`이고 각 result가 배열일 때만 batch 전체를 원자 저장한다.
3. 422·429·5xx·timeout과 형식 불완전 HTTP 200은 결과 없음이 아니라 batch 실패다. 부분 결과를 저장하지 않고 전체 payload를 backoff 후 재시도한다.
4. 원시 envelope는 batch 번호, candidate ID·query 순서, payload/response SHA-256, HTTP metadata, 조회 시각과 원 응답 문자열을 `intake/B002-public/zbmath-citation-matcher/`에 보존한다.
5. 파생 index는 zbMATH의 citation 필드만 싣고 review·abstract 전문은 복제하지 않는다.

`m=0`은 저점수의 참 양성을 놓치지 않기 위한 recall 우선 대기열 설정이다. 그러므로 빈 배열이 없더라도 전건 match를 뜻하지 않는다.

## 파생 분류

제목과 연도만으로 다음 검토 대기열을 만든다.

- `exact_title_same_year`
- `exact_title_near_year`
- `exact_title_other_or_missing_year`
- `title_containment`
- `fuzzy_candidates_only`
- `no_results`

동일 후보가 여러 zbMATH 결과를 가질 때 exact title+same year를 단순 top score보다 먼저 보여 주되, 저자·편집자·출판처·ISBN·쪽·판본을 사람이 대조하기 전에는 연결을 승인하지 않는다. 후보의 원시 MathSciNet provenance와 서로 다른 판본은 유지한다.
