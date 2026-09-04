# B002 공개 DOI 대조 계약

## 목적과 경계

이 단계는 B002 후보가 가진 DOI를 Crossref 공개 REST API의 실제 레코드와 대조해 식별자, 출판형태, 판본 관계, 정정·철회 표지와 공개 초록의 존재를 확인한다. Crossref 결과는 후보 발견·서지·판본 증거이며 핵심성이나 수학적 타당성을 판정하지 않는다.

입력은 `catalog/B002-candidates.jsonl`과 `manifests/B002-normalized.json`이다. 후보 원문과 정규화 manifest의 해시가 먼저 일치해야 한다. DOI가 없는 후보는 실패가 아니라 `not_queried_no_doi` 범위다.

공개 API는 인증이나 크리덴셜 없이 순차 호출한다. Crossref의 공개 pool 한도보다 낮은 초당 4회 이하를 사용하고, HTTP 429와 일시적 5xx는 `Retry-After` 또는 제한된 backoff 뒤 재시도한다. 응답 본문·헤더·DOI를 로그에 출력하지 않는다. PDF와 원문은 요청하지 않는다.

## 원시 응답과 재개

DOI 하나마다 `intake/B002-public/crossref/<doi_sha256>.json` 하나를 원자 저장한다. 파일에는 다음을 둔다.

- 요청한 정규화 DOI, 최초 endpoint와 HTTP redirect 뒤 최종 endpoint
- UTC 조회 시각과 HTTP 상태
- 응답 본문의 정확한 UTF-8 문자열과 그 SHA-256
- 응답의 `Content-Type`, `ETag`, `Last-Modified` 중 실제 존재하는 비민감 헤더

기존 파일은 DOI·상태·본문 해시·JSON 구조를 다시 검사한 뒤에만 건너뛴다. HTTP 200 응답은 원칙적으로 Crossref `message.DOI`가 요청 DOI와 같아야 한다. Crossref가 다른 `/works/<doi>`로 HTTP redirect했고 최종 endpoint의 DOI와 `message.DOI`가 일치하면 `found_alias`로 허용하며 요청 DOI와 반환 DOI를 모두 보존한다. HTTP 404는 Crossref 미등록으로 보존하지만 DOI 자체의 부재나 다른 등록기관 부재로 확대 해석하지 않는다. 깨진 기존 파일은 덮어쓰지 않고 중단한다.

## 파생 색인

전 DOI가 200 또는 404로 종결되면 다음 추적 산출물을 결정론적으로 만든다.

- `catalog/B002-crossref.jsonl`: DOI, 연결된 모든 MR 후보, 대조 상태, Crossref 제목·저자·유형·출판처·날짜·ISBN/ISSN·URL, relation/update 정보, 초록 존재 여부, 원시 응답 경로와 해시
- `manifests/B002-crossref.json`: 입력과 출력 해시, DOI·후보·응답 상태 계수, 필드 존재 계수와 예외
- `reports/B002-crossref-audit.md`: 실제 검색 범위, 일치·불일치 유형과 판본 조사에 미치는 영향

추적 색인은 Crossref 초록 전문을 복제하지 않는다. 공개 초록 전문은 Git에서 무시하는 원시 응답에만 남기고, 색인에는 존재 여부와 원시 응답 참조만 둔다.

Crossref 제목과 B002 제목의 대조는 별도 파생 검토다. JATS/MathML 태그를 평문으로 투영한 뒤 같은 정규화기를 적용하고, 정확 일치·한쪽 제목 포함·높은 유사도·검토 필요·Crossref 제목 없음·Crossref 미등록을 구별한다. 문자열 유사도는 검토 대상을 줄이는 신호일 뿐 DOI가 맞거나 틀렸다는 최종 판정이 아니다. 책 DOI가 장 제목을 반환하거나 다권본 제목을 줄일 수 있으므로 불일치를 자동 삭제·교정하지 않는다.

## 완료 조건

1. 입력 후보·manifest 해시가 유효하다.
2. 후보 DOI의 고유 집합과 DOI별 MR 후보 집합을 빠짐없이 계산했다.
3. 모든 DOI가 검증된 HTTP 200 또는 404 원시 응답을 가진다.
4. 200 응답의 DOI가 요청 DOI와 일치하거나 검증된 Crossref redirect로 연결되고, 404를 결과 없음 이상의 주장으로 바꾸지 않는다.
5. 파생 색인의 모든 MR·원시 파일 참조와 SHA-256이 유효하다.
6. 같은 입력과 원시 응답에서 파생물 바이트가 재생성된다.
