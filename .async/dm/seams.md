# 공용 인터페이스와 작업 사본의 경계

제품의 정본은 각 workspace 안 `.claude/skills/do-math/scripts/do_math/`의 실제 정의와 `.claude/skills/do-math/scripts/tests/contracts/`, `.claude/skills/do-math/scripts/이음새-정본.md`다. 기존 상세 연결과 변경 이유는 sources/legacy/seams.md에 보존했다. 그 원문 속 run: 경로는 이전 실행 기록 루트 기준이다. 초기 세 읽기 작업 사이에 새 제공/소비 API는 없다.

- R02는 현재 역할 요청 생산자와 worker/정본 schema 수신자를, R07은 test_schema_builders의 실제 반환 경로와 소유 모집단을, R18은 현재 adapter/real port 호출과 실제 배선을 기존030 objective의 정확한 심볼로 연결한다. 서로의 미완성 결과를 소비하지 않는다.
- 새로운 인터페이스가 필요한 작업에서는 실제 정의의 파일·심볼, 입력·출력·실패·부수 효과와 소비 책임을 먼저 적는다. 기존 정의를 별도 문서 schema로 재발명하지 않는다.
- source_repo는 C:/math이고 manager가 통합하는 공용 판본이다. task는 workspace만 수정한다. task의 시작 inputs/base/baseline이 수행 중 고정되고, manager의 다른 결과 통합은 이미 실행 중인 workspace를 바꾸지 않는다.
- manager는 workspaces.py integrate의 충돌 결과를 존중한다. 같은 파일이 양쪽에서 달라졌다면 원본을 덮거나 workspace를 공용 소스에 통째로 복사하지 않고 필요한 조정 작업을 배정한다. 승인한 무변경 조사도 integrate의 변경 없음 기록 뒤 accepted에 넣는다.
- 정본 스킬과 대응 미러는 같은 task의 쓰기 범위에 함께 둔다. 공식 생성기가 자기 workspace에서 예상한 범위만 바꾸는지 확인한다. 공용 판본의 snapshot과 integration을 serialize하는 source.lock은 서비스가 관리하며 세션이 삭제하지 않는다.
- 실제 외부 자원·최종 전체 관문의 공유 경계는 manager가 충돌 없이 배정한다. 독립 workspace의 소규모 검증은 각jobs1로 수행할 수 있고 총시험worker3 이하를 유지한다. 제품 의미·판정·원자료 무결성을 줄여 속도를 맞추지 않는다.

## 이번 세 읽기의 실제 연결과 보고 경계

- r02: `do_math/model_runner.py:ModelRunner` 및 현재 adapter의 요청 조립, `worker_request.py`의 `check_codex_request`/`check_claude_request`, `codex_worker.py`/`claude_worker.py`의 load 경계가 대상이다. `tests/contracts/pairs.py:_worker_request_samples`와 `test_pairs.py`의 required/optional 역방향 단언이 실제 저장·수신까지 무엇을 입증하는지 구별한다. 이 문서는 새 요청 schema를 정의하지 않는다.
- r07: `tests/structure/test_schema_builders.py`의 `_calls`, `_composition_calls`, `_constant_object_calls`, `TRANSFORMERS`, `DELEGATED_SCHEMA_METHODS`가 현 등록이다. 실제 contracts/control/record schema와 engine·review_cycle·knowledge_io·planning 반환의 소유 계약에 대응한다. caller 입력을 빌리는 transformer나 read-only borrowed row를 임의 copy 의무로 바꾸지 않는다.
- r18: `tests/structure/test_boundary_invariants.py`의 `PROCESS_STARTS`, `INJECTED_STARTS`, `JOB_RUN_STARTS`, `INTERPRETER_USES`, `EXECUTABLE_IDENTITY` 및 발견 함수와 `file_io.py`의 소유 규칙을 실제 windows_job/git_process/cli_worker/formal/scheduler 및 최상위 도구 호출에 연결한다. 현재 누락과 장래 가상 우회 가능성을 구별한다.
- 세 task의 제품 경로는 자기 workspace 상대 경로다. `C:/math/docs/...`와 `C:/math/.async/dm/...` 입력은 읽기 전용 원자료다. 과거 문서 안 `run:`은 legacy 실행 루트, 과거 `repo:docs/...`는 공용소스의 원자료를 뜻한다. workspace에 없는 대형 기록을 제품 누락으로 판정하지 않는다.
- source 판본 비교는 task의 `baseline.json`과 자기 workspace를 기준으로 하고, 이관 기준은 `managers/0001/source-inspected.json`의 스킬2675파일과 교집합에서 대조한다. 실제 차이가 있으면 명시한다. 이후 manager가 공용소스에 다른 결과를 반영해도 이미 실행 중인 task는 자기 고정판으로 완료한다.
- 보고는 async protocol의 `status`, `summary`, 문자열 목록 `changes`/`findings`, `verification`을 사용한다. 제품 무변경 조사는 changes=[]이다. 각 finding 문자열에는 해당 요구·증거 파일/심볼·영향과 다음 행동을 함께 적고 자세한 표는 자기 evidence를 참조한다.
