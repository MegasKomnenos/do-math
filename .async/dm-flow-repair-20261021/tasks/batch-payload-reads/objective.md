# 정확한 snapshot 복원의 payload Git 읽기 묶기

## 결과

context.md R7.3을 구현·검증한다. 현재 `ResearchRepository._read_documents`는 state 파일을 한 번에 읽은 뒤 새 payload마다 `_store.read_bytes(head, path)`를 호출한다. 같은 정확 snapshot과 해시/바이트/정규 JSON/상태 계약 검사를 유지하면서 읽기를 묶거나 재사용해 실제 Git 하위 프로세스 호출 비용을 줄인다. 불필요한 모든 artifact 선읽기나 무한 캐시로 비용을 옮기지 않는다.

## 읽기와 수정

정본 AGENTS.md, `scripts/이음새-정본.md`의 봉인 artifact·snapshot 캐시 규칙, 시험 지침, 공용 seams를 읽는다. `repository._read_documents/_decode_families`, `payloads.decode/_decode_snapshot/_read_json_blob`, `GitStateStore.read_many/read_bytes`, git_process의 실제 batch protocol을 따라 읽는다. 이미 `read_many(commit, paths)`가 정확 bytes를 한 process로 읽는 정본이다. 필요한 경로 집합을 어디서 알 수 있는지, 중첩 snapshot/payload가 어떻게 참조되는지 확인해 적절한 수단을 고른다.

`C:\math\.skill-workspace\parking-unimodality-20261021\audit\records.json`, snapshot, status-profile.txt/pstats와 원 저장소의 정확 snapshot `811c4576af7fc8a5054181ad0208db42ddd329c6`는 읽기 전용 근거다. 실제 측정이 필요하면 보존 bytes/저장소를 새 임시 위치에 복사하거나 현행 계약의 별도 대표 인스턴스를 구성한다. 원 연구 저장소·work·감사 자료·HOLD·예약은 변경하지 않는다. 구 기록 운전을 위한 호환층/자동 변환은 만들지 않는다.

필요하면 허용된 repository, payloads, git_store, git_process를 함께 수정한다. 정확 OID/경로 검사, blob 길이와 타입, 봉인 hash·정규성, 잘못된 참조/누락/손상 반려, 검증 후 state 계약과 event 검사 의미를 보존한다. 기존 `sealed_bytes`와 payload JSON 변종 규칙을 재구현하지 않는다. protocol 포트를 바꾼다면 허용된 port contract/대역과 소비자도 맞추며 필요 없는 포트 확장은 피한다. 공통 이음새 문서의 이번 병렬 편집 소유자는 hash task이므로 이 task는 변경한 공개 정의와 정확한 문서 보완 내용을 자기 설명에 남겨 manager가 후속에 연결하게 한다.

## 최소 검증과 근거

기존 storage/payload 시험을 찾아 결함/보존할 성질을 최소 범위로 보강한다. 개선 전후를 같은 대표 데이터·정확 snapshot·캐시 조건의 별도 트리/프로세스에서 연달아 실제 명령으로 읽어, 복원된 값과 바이트/해시의 일치, Git 하위 호출 수와 경과 시간을 비교한다. 대표 입력 규모와 cold/warm 조건, 실행 명령, 판본, raw 결과를 `evidence/`에 남긴다. 측정 1쌍으로 얻은 수치를 전체 성능으로 일반화하지 않는다. 개선 전 입력이 현행 감사 snapshot과 같지 않으면 정확히 구별한다. Python 함수 mock 호출 수만으로 실제 Git 프로세스 감소를 주장하지 않는다.

정확 판본 분리, 참조 누락/손상 반려의 대표 확인과 변경 영역 선택 시험을 수행한다. 한 작업자는 시험 프로세스 하나만 사용하며 전체 회귀는 후속 통합에 맡긴다. 과거 38.717초·274건 관측을 자기 개선 전 재측정인 것처럼 쓰지 않는다.

`docs/do-math/flow-repair-20261021/batch-payload-reads.md`에 원인·설계·보존한 계약·실측 표·한계를 기록한다. 정본 변경은 writing-skills 공식 SKILL.md/생성기를 읽고 Codex 미러에 반영한다. 무관한 스킬·.agents/diff 변경은 포함하지 않는다. report.json에 실제 변경과 근거를 남기고 서비스 report 검사를 수행한다.
