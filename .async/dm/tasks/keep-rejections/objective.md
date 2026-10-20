# 정확한 반려 원인 세 곳 마무리

수용된 keep-contracts의 K-71 F2/F3/F4를 한 작업에서 수리한다. 잘못된 입력을 주었을 때 무관한 예외도 시험 통과로 받아들이는 공백을 없애는 것이 목표다. 현재 정상 입력·실제 수신자·공통 Git 계약의 양측 소비를 유지하고 직접 단언·미러·필요한 최소 확인을 함께 끝낸다. 새로운 runtime 결함이 관측됐다는 배정은 아니다.

SESSION_JSON과 task.json, inputs/context.md·plan.md·seams.md, do-math AGENTS.md와 시험-지침.md를 읽는다. C:/math/.async/dm/managers/0044/review.md·source-review.json, tasks/keep-contracts/report.json·evidence/judgment.md·findings.json이 발견과 수용 범위다. 과거 원자료 루트는 C:/math/docs/do-math/continuous-development-2026-10-13이며 sources/user-decisions.md·model-policy-2026-10-14.md·document-batching-2026-10-14.md·requirements-index.json, phases/001/tasks/closure-map/evidence/requirement-state.json의 K-71과 tracking-state.json의 KEEP-TEST-CONTRACT를 필요한 부분만 확인한다. C:/math/docs/do-math/시험-재편-2026-09-29/조사/대역-사각지대.md도 같은 원질문이다. 공용 source와 다른 task는 읽기 전용이며 구현은 자기 workspace를 사용한다.

선행은 keep-contracts 하나다. keep-storage/keep-evidence는 이미 수용됐고 keep-contracts 원보고에 적힌 당시 미수용 상태를 현재 상태로 해석하지 않는다. storage-knowledge/storage-profiles/keep-proof는 독립 작업이므로 기다리거나 미완성 사본을 소비하지 않는다.

## 고칠 세 성질

1. **F2 — 수리보고의 누락한 필드.** tests/unit/test_operator_rules.py:InstallationEvidenceTests.test_repair_reports_require_both_version_and_source_commit_even_when_git_is_unavailable의 diagnosed=False/True × installation_version/source_commit 누락을 실제 repair_report_schema와 jsonschema.validate로 확인한다. 정상 validate와 required 목록 대조를 유지하며 ValidationError의 required validator, 루트 instance path, 누락한 정확 필드 진단을 묶는다. 다른 필드·유형·중첩 경로 오류를 필수성 성공으로 인정하지 않는다.
2. **F3 — 저장소 밖 경로.** tests/support/port_contracts/git_backend.py:GitBackendContract.test_project_without_git_has_empty_facts_and_outside_root_is_rejected의 정상 no-repository 빈 facts를 유지한다. 실제 outside와 self.repo.resolve() 입력이 Path.relative_to에서 반려되는 정확 경로/사유를 확인한다. 단순 ValueError 발생, 임의 문자열 nonempty, 무관한 값 반려를 성공으로 받아들이지 않는다. 실제 Python 표현을 먼저 읽고 플랫폼별 경로/대소문자 처리로 입력 정체성을 지우지 않는다.
3. **F4 — 손상된 동일 Git ref.** 같은 공통 계약의 test_broken_ref_text_is_an_error_but_missing_object_keeps_its_oid에서 두 malformed raw, SHA1/SHA256, fake/real 네 소비자를 유지한다. absent ref=None과 유효 OID이나 없는 object의 정상 대조를 보존하고, 손상 입력에는 같은 REF와 실제 backend 사유를 결박한다. 현재 fake.ref_oid는 'broken reference: '+REF를, GitProcessBackend.ref_oid/_fail은 rev-parse --verify --quiet REF의 실패와 stderr를 보고한다. 실제 표현 차이를 확인한 뒤 단언한다. 모든 backend에 같은 문구를 강요하거나 피검사 호출로 기대 예외를 다시 계산하지 않는다. 필요하면 양측 소비자의 작은 assertion 준비를 사용할 수 있으나 새 오류 체계나 범용 검사기는 만들지 않는다.

수정 권한은 task.json의 단위시험, 공통 Git 계약, contracts/boundary 양측 소비자와 미러다. 양측 소비자는 꼭 필요한 경우만 바꾼다. runtime/포트 정의/fake backend/smell_rules/run_tests/다른 helper·시험 지침은 읽기 전용이다. 실제 제품 결함이나 범위 밖 수정이 필요하면 정확 반례·심볼·영향을 보고하고 우회용 대역/문구 변경으로 덮지 않는다. 기존 winerror 반려와 원값 보존 단언을 약화하지 않는다.

## 최소 확인과 완료

정적으로 충분한 부분은 읽기로 끝낸다. 바뀐 성질은 workspace 공식 run_tests.py --jobs 1의 해당 단위 메서드 하나와 두 공통 메서드의 실제 inherited ID를 선택한다. 소비 클래스는 contracts.test_port_git_backend의 FakeGitBackendContract/FakeSha256GitBackendContract, boundary.test_port_git_backend의 GitProcessBackendContract/GitProcessSha256BackendContract다. 기본 최소 선택은 1+2×4=9ID이며 실제 수집 ID와 수정 범위에 맞춰 판단한다. 공통 mixin 자체를 runnable ID로 쓰지 않는다. 실제 Git은 저장소 밖 짧은 임시 fixture에서만 사용하고 공용 Git index·연구·예약은 건드리지 않는다. 전체 T4나 다른 경계 실행은 필요하지 않다.

실행 중 소스를 고정하고 selected/고유실제 row·관측exit·최종 SHA·fixture/최초 실패·실행 중 변경·소프트초과와 사유를 보존한다. 오류가 생기면 해당 원인을 고치고 필요한 최소 선택만 다시 확인한다. 새 무력화 실행이나 별도 전체 감사를 기본 완료조건으로 추가하지 않는다. 비용캐시 관측 bytes를 evidence에 보존한 뒤 own base로 복원하고 공식 build_skill_mirrors.py 생성/확인을 수행한다. 함수·단언 변경과 설명만의 변경을 구별한다.

report.json은 F2/F3/F4 각각의 실제 원인 단언, 정상 대조·양측 소비 보존, 실제 검증과 한계, 남김을 기록한다. 세 공백이 해소되면 K-71 지정 질문을 최종 통합판 증거 대기로 넘긴다. 다른 K/P2, R01/K-78 저장 가족, G4~G8·L01·Windows1314·최종review는 이 작업이 종결하지 않는다. check.py report C:/math/.async/dm keep-rejections PASS로 제출한다. 공용 context/plan/seams·queue/state, 다른 task, engine, Git index, graphify 및 기존 연구 운전은 수정하지 않는다.
