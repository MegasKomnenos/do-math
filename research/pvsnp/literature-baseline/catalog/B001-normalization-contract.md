# B001 정규화·연결 계약

## 목적

B001의 BibTeX·RIS·Scopus CSV 20,746개 출현을 하나의 형식으로 읽고, 같은 자료원 record의 반복 출현만 안전하게 모은다. B001은 탐색·교정 묶음이지만 그 레코드는 최종 문헌 후보에서 버리지 않는다.

## 식별과 보존

1. 원시 `intake/B001/` 파일은 읽기 전용이다. 각 출현은 source, query ID, 검색 내 rank, 원시 파일 경로·SHA-256, parsed-record SHA-256을 보존한다.
2. 같은 source의 안정 식별자만 한 후보로 모은다: MR number, ACM/IEEE BibTeX key, WoS UT, Scopus EID, PQDT AN/M1. 안정 식별자가 없으면 record hash를 사용하고 이를 예외로 센다.
3. 다른 자료원끼리는 DOI가 같아도 자동 병합하지 않는다. DOI 오류, chapter DOI, set DOI와 판본 재사용이 실제로 있으므로 `same_doi_candidate` 관계만 만든다.
4. 정규화 제목·저작자·연도가 모두 같은 서로 다른 source record도 `same_bibliographic_fingerprint_candidate`로 연결할 뿐 원 레코드를 없애지 않는다.
5. B001 MathSciNet과 B002가 같은 MR number를 가지면 동일 source 기본키의 직접 overlap으로 기록한다. B001의 추가 query provenance를 보존하고 두 MR을 별도 저작으로 세지 않는다.

## 필드와 권리 경계

추적 후보에는 제목·저작자/편집자·연도·출판형태·venue·권호·쪽·출판사·DOI·ISBN/ISSN과 원시 locator만 둔다. 인증 export의 초록과 참고문헌 전문은 복제하지 않고 존재 여부만 기록한다. 실제 내용 판독은 권한이 있는 원시 파일에서 후보별로 수행한다.

BibTeX의 손상된 초록 중괄호나 IEEE의 무개행 entry 경계 때문에 정상 서지 필드를 잃지 않도록 record/field 시작 경계를 사용한다. 파서가 받아들였다는 사실은 서지 동일성이나 문헌 핵심성을 승인하지 않는다.

## 산출물

- `B001-candidates.jsonl`: source 안정 ID 기준 후보와 모든 query provenance.
- `B001-relations.jsonl`: B001 내부 및 B002와의 DOI·서지 fingerprint 관계 후보.
- `B001-direct-title-queue.jsonl`: 제목 자체에 P-vs-NP 표현이 있는 source record의 중복 대조 cluster.
- `B001-direct-axis-queue.jsonl`: 초록·keyword의 P-vs-NP 문맥과 명시 복잡도 축이 함께 있는 후속 cluster.
- `manifests/B001-normalized.json`: 입력 전건의 해시·개수, 후보·관계 개수와 예외, 출력 해시.

관계와 review queue의 기본 상태는 `unverified_candidate` 또는 `unreviewed`다. 서로 다른 판본·발표형태·번역·학회판·저널판은 사람이 공식 record와 내용을 대조하기 전에는 합치지 않는다.
