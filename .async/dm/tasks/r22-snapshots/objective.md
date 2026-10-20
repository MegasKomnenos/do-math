# R22: 검토·위임·해석 근거 snapshot의 중복 저장 수리

r22-storage의 F1/F2를 생산·저장·봉인·복원 경계 한 묶음으로 해결한다. r22-storage와 r12-r13-fix가 선행이다. 후자는 실제 공개 위임 원결정/판단 생산과 현재 schema를 제공하므로 그 수용판에서 시작한다. r06-finish나 r15-r16의 종료는 필요하지 않다.

SESSION_JSON의 workspace, task.json, inputs/context.md/plan.md/seams.md를 읽는다. 사용자 원문은 C:/math/docs/do-math/continuous-development-2026-10-13/sources의 user-decisions.md/requirements-index.json/model-policy-2026-10-14.md/document-batching-2026-10-14.md다. 결함-범주.md의10-A, tracking-state R22/requirement-state10-A, tasks/r22-storage/report.json·evidence/judgment.md/family-table.md/family-judgment.json 및 managers/0020/review.md를 읽는다. 기존88가족 대응과 학술 해결 record 시험, r21-r22의100×10/37프로필·manifest·5선언/603폐포는 이미 마친 한정 성질로 재사용한다.

## 고칠 실제 결과

F1: review_cycle.start_review(previous)는 previous_reviews/turns/transcript_manifest를 복사하고 review_engine._start_identity_review는 이전 cycle도 보존한다. N개의 독립 P바이트 판본 원천 NP에 비해 작은 문자열 본문 하한이 P*N*(N+1)/2가 되는 정적 반례가 있다. 이전 cycle의 증거와 현재 검토의 접근을 함께 유지하면서 반복 snapshot을 줄인다. 이전 판본 삭제·revision 수 제한·원문 요약으로 비용을 맞추지 않는다.

F2: delegations._basis의 target/references, governance._knowledge_import_basis/_owner_basis의 record snapshot과 review_engine._build_review_context의 pending proposal/restored_messages가 같은 구조를 여러 번 저장한다. 큰 문자열 codec은 작은 leaf/row가 많은 M바이트 구조의 K참조 O(KM)을 해결하지 못한다. review_inputs는 수신/defer 시 제거되므로 영구 누적으로 잘못 확대하지 않는다. 같은 불변 구조 원천과 참조좌표 비용을 구분해 현행 저장 논리 바이트가 원천 대비 상수배로 유지되도록 고친다.

새 장치를 설계하기 전에 현재 중복 보존이 필요한지와 기존 ID/봉인 snapshot/원문 참조로 충분한지 판단한다. 현행 구현은 바꿀 수 있으며 범용 cache/nullable registry/새 버전 호환 저장체계는 전제가 아니다. 필요한 표현 변경은 producer·consumer·schema·테스트·실제 제품 설명을 이 task에서 함께 교체한다. 과거 실험 기록은 호환 대상이 아니지만 같은 연구의 다른 판본 이력과 정확 증거는 현재 의미이므로 보존한다.

소비자는 전체 원문/판본 순서/논리 슬롯과 transcript manifest, 독립 판단의 동일 봉인 입력, source/currentness/basis hash, 반려와 복원·재시작·record query의 현재 의미를 유지해야 한다. 저장량을 위해 검증·권한·복원 오류를 제거하거나 모든 입력을 trusted로 만들지 않는다. 표현을 바꾸면 원문/hash 불일치나 없는 참조가 현행 경계에서 명확히 반려되는 최소 사례도 확인한다. 같은 구조를 읽은 반환이 다른 record의 mutable 값에 공유되지 않는 계약을 유지한다.

## 단언과 완료 판단

먼저 실제 생산 경로와 충분한 기존 단언을 읽고 최소 수리를 선택한다. 검토 revision 누적과 위임/import/pending context의 동일 구조 다중 참조를 실제 producer→저장→load/read/restart로 확인할 가장 적은 입력을 사용한다. 새 실제 공개 위임은 수용된 r12-r13-fix 경로를 소비하고 원결정을 dict로 주입해 공개 성공으로 세지 않는다. 원천은 최초 독립 입력 bytes/구조로 고정하며 최종 instance/runtime의 중복을 분모에 넣지 않는다. 고정 overhead와 상수는 저장 구조/참조 계약에서 정하고 실제 측정 결과를 보고 키우지 않는다. 작은 문자열의 prefix 이력과 큰 구조의 반복 좌표가 모두 줄었는지 판정한다. 단순 큰 string dedup만으로 F1/F2 전체 완료를 선언하지 않는다.

새 실행은 현재 변경에 필요한 가장 작은 대표만 한다. 각 가족에5MB나 모든 과거 대형 fixture를 반복할 필요는 없다. 충분한 관계는 현행 코드로 설명하고 런타임 측정/정적 복잡도/현재 남김을 구별한다. unit.test_engine_storage_scale의 기존 독립 원천/전체 값 단언을 보존한다.

## 쓰기와 독립성

task.json writes가 정본이다. governance/delegations/review_cycle/review_engine, 관련 저장 codec/repository/state_contract/record_schemas 및 필요한 지정 시험/helper/제품 설명·미러를 맡는다. 기존 공용 source 정의를 가능하면 재사용한다. optional storage_snapshots.py는 실제 공유 규칙이 필요할 때만 만들고 새 모듈을 만드는 것이 완료 조건은 아니다.

governance_engine/core_engine/context_store/lifecycle/retention은 r06-finish의 소유로 읽기 전용이다. 현재 _governance_context 등은 만들어진 값을 전달하므로 해당 caller에 불필요한 표현 변경을 퍼뜨리지 않는다. 필요한 값 해석/복원은 실제 provider 경계에서 처리한다. r15-r16의 scheduler/parallel/call/formal 정산과 r19-r20의 corpus/parser도 읽기 전용이다. 직접 확인한 범위 밖 의존이 있으면 정확 이유/심볼을 보고하고 가능한 결과를 마친다. 진행 중 사본이나 중간 결과를 소비하지 않는다.

## 제출

AGENTS.md·시험-지침을 적용하고 공식 run_tests.py jobs1로 변경에 필요한 최소 ID만 실행한다. 최초 실패/fixture 오류·선택/실제row·exit·SHA·소프트초과·미확인을 보존한다. 공식 mirror build/check 완료와 변경쌍 bytes를 확인하며 비용캐시는 evidence 보존 후 own base로 복원한다. 실제 바뀐 schema/설명과 호출부의 불일치를 남기지 않는다. report.json은 F1/F2와 원문10-A의 정확 완료/남김을 설명하고 check.py report C:/math/.async/dm r22-snapshots PASS를 확인한다. 전체 관문·새 외부 호출·graphify·예약·공용 문서/queue/state·Git index·과거 원자료는 수정하지 않는다. G4~G8·L01·Windows1314는 별도 남김이다.
