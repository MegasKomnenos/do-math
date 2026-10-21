# 통합된 do-math의 구조 잔여 수리와 최종 동작 확인

## 얻어야 할 결과

수용된 R1~R7 제품 변경을 함께 사용할 수 있는지 확인하고, 알려진 구조 연결 잔여 3건과 이번 통합에서 드러나는 관련 결함을 필요한 수정·확인까지 이 task에서 마친다. 전체 목표와 사용자 요구는 inputs/context.md, 현재 계획은 inputs/plan.md, 실제 공개 정의는 inputs/seams.md 11~14절을 따른다. 단순 시험 보고서 생성이나 무조건적인 통과 수 늘리기가 목적이 아니다.

`intent-check-evidence`, `batch-payload-reads`, `codex-refresh-diagnostics`의 결과가 수용된 뒤 시작한다. 이 의존관계는 role-question-flow와 그 선행 결과도 포함한다. 별도 구현자가 실행 중인 task는 없다. 정본 AGENTS.md, 제품 `scripts/이음새-정본.md`, `scripts/tests/시험-지침.md`를 읽는다.

docs는 snapshot_paths에 없으므로 공용 소스의 `C:\math\docs\do-math\flow-repair-20261021\` 아래 문서를 읽기 전용으로 사용한다. 특히 `intent-check-evidence.md`, `role-question-flow.md`, `shared-validation-hashes.md`, `codex-refresh-diagnostics.md`, `batch-payload-reads.md`, `windows-patch-guidance.md`, `role-flow-design.md`를 필요한 판단에 참조한다. 영구 report/evidence는 `C:\math\.async\dm-flow-repair-20261021\tasks\각-task-ID\`에 남아 있다. 정리될 workspace에 의존하지 않는다. 과거 정확 소스가 필요하면 서비스 `workspaces.py restore RECORDS TASK baseline|result NEW_DIRECTORY [PATH ...]`를 사용한다.

## 먼저 수리할 구조 연결 3건

`tasks/intent-check-evidence/evidence/final-scoped/report.json`의 실제 실패와 `baseline-structure-comparison.json`, `managers/0007/verification-summary.json`을 읽는다. manager는 관련 6파일이 시작판과 같은 SHA임을 확인했으며 시작판에서 시험을 재실행한 것은 아니다. 이미 저장된 실패를 다시 만들기 위해 같은 시험을 실행할 필요는 없다.

1. `structure.test_doc_code.DocumentCodeTests.test_all_dotted_document_fields_have_an_owner`: `references/CLI-실행-계약.md`의 source.offset/source.bytes/turn.failed가 실제 제공자에 연결되지 않았다.
2. 같은 클래스 `test_documented_scoped_fields_belong_to_their_actual_schema`: result artifact의 execution.collect.diagnostics/stderr를 실행 원장 schema 필드로 검사한다. 실제 공급자는 `codex_stream.stderr_diagnostics`, `codex_adapter.LocalCLIAdapter.collect`, 보존은 `call_engine._receive_call`이다. 문서의 원바이트·부가 색인·성공/실패와 별개인 의미를 보존하고 문서 검사기의 실제 소유 경계를 맞춘다. 전체 실행 원장 schema에 가짜 필드를 추가하거나 예외 허용 목록으로 검사를 우회하지 않는다. 코드에서 확인할 수 있으면 정적 근거로 충분하고 외부 CLI 재생은 불필요하다.
3. `structure.test_schema_builders.SchemaBuilderTests.test_every_schema_function_is_declared`: questions.obligation_schema/resolution_schema/route_schema/wait_schema 및 revisions.resolution_schema가 선언 모집단에서 빠졌다. 실제 인자별 shape와 기존 독립 가변 노드 검사의 계약에 맞게 등록·검사한다. 명칭을 바꾸거나 모집단에서 빼서 통과시키지 않는다.

수리 위치는 실제 원인에 따라 문서·검사기/fixture·제품을 함께 맞춘다. 동일 의미를 여러 검사기에 복제하지 않는다. 정상 요청·예외 재량·사용자 권위·독립 승인·봉인/현재성/권한 검사를 약화하지 않는다.

## 최소 통합 확인과 실패 정산

위 작은 수리를 마친 후 정본에서 공식 `run_tests.py`로 T2 모집단(structure/unit/contracts/sim)과 flows를 한 번 확인한다. `python scripts/run_tests.py structure unit contracts sim flows --jobs 3 --output 새-빈-짧은-경로` 같은 실제 선택을 사용한다. 다른 시험 작업자가 있으면 합계 3개 이하로 낮춘다. 긴 출력/임시 경로로 Windows 자체 실패를 만들지 않는다. 실행 중 소스를 편집하지 않는다. `.timings.json` 자동 갱신은 결과 재사용 근거가 아니며 무관한 제품 변경에 포함하지 않는다.

읽은 report의 ID/fixture/complete/successful/종료 코드/source_sha256/changed_during_run을 확인한다. 실패하면 원인부터 읽고 관련 구현·문서·실제 fixture를 이 task에서 수리한다. 수정 후에는 실패한 시험과 변경으로 새로 불확실해진 소비 경계만 확인한다. 앞서 통과한 전체 모집단을 이유 없이 반복하지 않는다. 서로 다른 판본의 통과를 마지막 판본 전체 회귀로 합산하지 않고 실행별 판본·남은 실패·선택 이유를 설명한다. 미수리 결함이 남으면 complete로 숨기지 않는다.

통합의 실제 Git/CLI/worker 경계 중 이 변경으로 아직 불확실한 부분만 작은 기존 boundary ID로 확인한다. 예를 들어 `boundary.test_storage_batch_process_counts`, `boundary.test_governance_cli_decision`, 제출 도구의 실제 설치 경계를 코드와 선행 근거에 대조해 필요한 선택을 정한다. 기존 원 snapshot의 Git 수·시간 쌍과 Windows 무해 명령·Codex 원자료 재생을 반복하지 않는다. OS 수명/adapter 자체를 추가 변경했다면 그 실제 경계를 필요한 범위에서 확인한다. 이번 목표는 새로운 coverage 측정·성능 실험·외부 환경 검증이 아니므로 T3 full/T5/live 모델·scholarly·Lean/설치 복구 호출을 일괄 추가하지 않는다.

새 action/wait/check 이력·실행 입력이 실제 producer에서 기존 저장 corpus와 첫 reader를 통과하는지 T2/flows 결과로 판단한다. 정본 문서·역할 지급·공통 검사 호출·입력/오류 의미·schema/참조/해시 투영·미러가 같은 현행 계약을 가리키는지 확인한다. 기존 선택 근거가 충분하면 재실행 대신 범위를 명시한다. `probe_cli.py --skill-only` 및 공식 writing-skills 미러 생성기의 최종 `--check`를 사용한다.

## 권한·보고

writes의 do-math 전체 디렉터리는 알려진 구조 수리와 통합 실패의 관련 생산자/소비자를 한 task에서 마칠 수 있게 준 범위다. 선택 개선·아키텍처 재설계·외부 서비스 수정까지 확대하지 않는다. 정본 변경을 공식 `.claude/skills/writing-skills/scripts/build_skill_mirrors.py`로 대응 미러에 반영하고 다른 스킬을 바꾸지 않는다. 서비스·공용 소스·다른 task·원 연구/감사/HOLD/예약·graphify는 수정하거나 재개하지 않는다. 제품 변경은 자기 workspace에서만 수행한다.

`docs/do-math/flow-repair-20261021/integration-repair-check.md`에 실제 수정·이유·검증/한계·남은 문제를 기록하고 report/evidence는 자기 task 디렉터리에 보존한다. 최종 review가 참고할 수 있도록 R1~R7의 수용 근거와 이번 실행의 보완 범위를 정확히 연결한다. report.json의 changes는 실제 변경만 적고 `python ENGINE/check.py report RECORDS integration-repair-check`로 제출을 확인한다. 최종 독립 review는 manager의 후속 배정이다.
