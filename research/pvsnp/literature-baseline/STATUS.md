# 문헌조사 상태

기준 시각: 2026-09-04 20:27 KST

## 현재 상태

- 단계: B002 정규화 완료·공개 자료원 분야별 핵심층 선별
- 현재 묶음: 없음
- 사용자 행동: 없음
- AI의 다음 행동: 5,472개 고유 후보를 분야별로 검토하면서 zbMATH Open·DBLP·arXiv·ECCC·DROPS와 공식 venue의 제목·초록·분류·판본을 대조해 기준 핵심층과 공개 누락 후보를 선별한다.
- 현재 결손: 사용자 입력 결손은 없다. B002에는 초록이 없고 60개 분야가 인용순 100건에서 잘렸으므로 공개 자료원 대조와 핵심층 판정이 남았다.

## 현재 판단

- 인증 B003 묶음은 열지 않는다. 현재 확인된 MathSciNet 공백은 공개 자료원과 공식 venue에서 먼저 조사할 수 있다.
- 공개 대조를 소진한 뒤에도 특정 핵심 문헌·학위논문·학회록·인용 관계가 재현되지 않을 때만 그 결손과 검색식을 근거로 B003을 연다.
- 이 판단은 문헌 집합 완료나 B003의 영구 불필요 판정이 아니다.

## 완료한 일

- KUDOS 공식 공개 목록 128개 항목 전수 확인
- KUDOS 제공 목록에서 핵심 이론 컴퓨터과학·수학 저널과 학회록의 실제 수록 확인
- 인증 후보 발견 자료원 여섯 인터페이스 선정
- 공개 자료원 역할과 중복·한계 조사
- 사용자–AI 역할 분담과 조사 완료 기준 확정
- 문헌조사 명세를 목표 보존형 합리화 절차로 개정
- B001의 20개 검색에서 20,746개 레코드를 수집하고 구조·검색 적합도·중복을 검사
- B001 검색식의 구두점·동음이의 잡음을 확인하고 후속 검색 분리 원칙 확정
- MathSciNet Playwright 수집 프로그램과 단위 검사 8건 작성
- 수동 00·01·03과 자동 probe의 레코드·MR 키 순서·정규화한 BibTeX 전체 바이트 일치 확인
- B002의 나머지 60개 분야를 자동 수집하고 63개 분야 6,233건 전수 구조 검사
- B002의 63개 BibTeX와 60개 metadata를 manifest의 경로·바이트·SHA-256·계수와 전수 대조
- 6,233개 출현을 전부 파싱해 MR 키 기준 5,472개 후보와 모든 분야·순위 provenance를 보존
- 같은 MR 키의 761개 반복 출현을 622개 후보에 모으고, 서로 다른 MR 키의 DOI·서지·판본 관계 후보 378묶음을 별도 생성
- 빈·비정규 연도, 중복 `EDITION`, 초과 중괄호, 저작자 부재와 미해석 TeX 명령을 원문 보존형 예외로 기록
- 공개 API와 공식 ECCC·DROPS·Theory of Computing·STOC·FOCS·CCC 자료를 실측해 학회록·기술보고·프리프린트 누락 보완 경로와 B003 미개설 판단 확정

## 닫힌 묶음

- [`B001`](batches/B001.md): 수용. 검사 결과는 [`reports/B001-audit.md`](reports/B001-audit.md)에 있음.
- [`B002`](batches/B002.md): 완료. 자동화 검증은 [`reports/B002-automation-audit.md`](reports/B002-automation-audit.md)에 있음.

## 현행 파생물과 검사

- 정규화 계약: [`catalog/B002-normalization-contract.md`](catalog/B002-normalization-contract.md)
- 후보 색인: `catalog/B002-candidates.jsonl` 5,472행
- 관계 후보: `catalog/B002-relations.jsonl` 378행
- 파생물 manifest: [`manifests/B002-normalized.json`](manifests/B002-normalized.json)
- 전수 검사와 분야 통계: [`reports/B002-normalization-audit.md`](reports/B002-normalization-audit.md)
- 공개 자료원 대조와 B003 판단: [`reports/B002-public-source-audit.md`](reports/B002-public-source-audit.md)
