# 합성 증거와 외부 대역의 보존 성질

시험에서 합성 Lean·호스트 결과를 실제 검증으로 오인하지 않고, 대역의 기본 성공이 명시한 입력과 현행 제품 경계를 지키게 한다. KEEP-FAKE-EVIDENCE의 K-38/39/41/42/72/75 여섯 보존 질문을 현재 구현·소비자·기존 근거로 판정하고, 확인한 공백의 필요한 수정·최소 확인·미러까지 한 task에서 마친다. 옛 fixture 이름이나 결과 필드를 복원하는 작업이 아니다.

SESSION_JSON/task.json, inputs/context.md·plan.md·seams.md, do-math AGENTS.md·시험-지침.md를 읽는다. 원자료 루트 C:/math/docs/do-math/continuous-development-2026-10-13의 sources/user-decisions.md·model-policy-2026-10-14.md·document-batching-2026-10-14.md·requirements-index.json과 phases/001/tasks/closure-map/evidence/tracking-state.json의 KEEP-FAKE-EVIDENCE, requirement-state.json의 여섯 K가 원요구다. C:/math/docs/do-math/시험-재편-2026-09-29/조사/대역-사각지대.md와 단계-전환표-2026-10-03.json의 같은 ID도 필요한 부분만 읽는다. migration/dispositions/kernel.knowledge.json의 위치 표는 탐색 출발점이며 실제 원문·코드·단언으로 확인한다.

수용된 keep-templates의 Sim/drive·공개 활성화와 r03의 trust_inputs 실제 setup 생산 경로를 소비하므로 두 결과만 선행으로 둔다. keep-templates/report.json·evidence/judgment-matrix.json, r03/report.json과 직접 근거를 읽고 충분한 불변 성질은 재사용한다. r15-r16의 실제 Calls/공개 반환 정산과 keep-isolation의 Job 근거도 해당 부분만 재사용한다. 진행 중 keep-inputs/keep-storage의 미수용 변경은 소비하지 않는다.

## 판정할 유한 질문

1. K-38: support/lean.py의 LeanDouble.__init__/allow와 FakeLean.wait가 source의 정확 UTF-8 bytes·순서 있는 선언 목록으로 명시한 입력만 성공시키는지 확인한다. 두 기본 producer의 원문과 lean_default_facts.json 대응, preview-only와 evidence extraction, 누락/충돌/공유 입력·반환의 의미를 현재 contracts.test_doubles_follow_corpus.LeanDoubleOutputTests와 실제 formal/lean_evidence 소비에 연결한다. 원문·선언 변경이 묵시적 성공이 되지 않고 명시한 synthetic facts도 실제 signature/forbidden axiom 검사를 통과해야 한다. 표 조회는 증명기나 제2 Lean parser가 아니다. 충분한 기존 반려·원출력 단언을 반복 실행하지 않는다.
2. K-39/41: FakeHost.cli_describe, trust_inputs.validation_fixture/trust_fixture, state_builders의 합성 제어/증거와 LeanDouble.checks의 표지가 현재 실제 consumer/기록에도 의미를 보존하는지 판정한다. 옛 launch_not_created 문구와 현행 외부 spawn 대역의 사실을 구별하고, 실제 Job 시작을 하지 않은 증거를 native Lean/host 검증으로 보고하지 않는다. trust fixture의 checker는 실제 do_math/formal.py의 경로/해시를 사용하고 승인된 toolchain/검증 record의 생산·수신을 우회하지 않아야 한다. 과거 필드를 호환용으로 다시 넣거나 제품 저장 schema에 시험 전용 의미를 추가하지 않는다.
3. K-42/72: unit.test_knowledge_formal_engine의 승인 명령과 의도적으로 다른 config 명령, knowledge_installed_lean.adopt_installed가 보호하는 정확 명령 선택을 읽는다. 이 시험 파일은 keep-storage의 writes이므로 수정하지 않는다. FakeClock의 단조/UTC 독립 변화와 FakeJobs의 suspended/resume/poll/turn/terminate는 contracts.test_port_clock/test_port_jobs와 실제 포트 계약의 해당 단언으로 확인한다. 기본 상태가 실제로 가능한지와 의도적으로 합성한 입력 사실을 구별한다. 모든 fake의 완전성 전수 증명을 새 조건으로 만들지 않는다. 필요한 추가 단언은 배정된 직접 계약시험 또는 unit/test_synthetic_evidence.py에 둘 수 있다.
4. K-75: 현재 Lean 기본 입력·review_scene.ReviewScene.execute의 입장/실행 결말과 그 직접 소비자를 확인한다. Sim._programs·공개 활성화, engine_purpose.drive의 조기 종료와 빈 경로 solution은 keep-templates 수용 근거를 재사용한다. 준비 비용을 줄인 경로가 원래 검사할 시작 상태·실제 producer/consumer·후속 대역 검사를 보존하는지 해당 helper와 직접 caller의 범위에서 판정한다. 자동 caller 목록만으로 충족을 선언하거나 모든 시험을 새로 실행하지 않는다. 아직 진행 중인 역할 입력/저장 helper 수리는 맡지 않는다.

각 K에 현재 제공/소비 심볼, 보호 성질과 정확 단언, 직접 확인한 방법·원보고/판본, 충족·수리 또는 구체적 남김을 남긴다. P2/PR과 겹치는 성질은 원 ID에 한정 연결하고 전체 종료를 주장하지 않는다. 과거 원보고가 없으면 부재를 유지하고 counts를 현재 성공으로 합산하지 않는다.

## 수정·확인·종료

제품 변경은 task.json의 합성 Lean/호스트/시계/Job·trust/review fixture와 직접 계약시험·대응 미러에 한한다. runtime 전체, shared Sim, default_responder/purpose_answers/model/role_answers/engine_purpose/review_research, 저장 helper와 test_knowledge_formal_engine은 읽기 전용이다. 기본 Lean 원문과 facts 불일치가 이 범위 밖 producer에서 발생하면 정확 원인·consumer·필요 경로를 보고하고 임의 fallback 성공을 만들지 않는다. 공유 README/이음새/시험 지침은 바꾸지 않고 변경한 인터페이스의 입출력·오류·책임을 report에 남겨 manager가 seams에 연결하게 한다.

정적 확인으로 충분하면 거기서 끝낸다. 실행이 필요하면 자기 workspace의 공식 run_tests.py --jobs 1로 실제 불확실성을 해소하는 가장 작은 선택만 사용한다. 실 Lean/유료 공급자/HTTP/OS 예약·전체 일반/T3/변이/T4/T5는 실행하지 않는다. 실제 프로세스·파일/포트 대역·순수 계산·과거 녹화 재생이 입증하는 범위를 구별한다. 경과시간으로 성공/변이 포착을 판정하거나 timeout을 재도입하지 않는다.

초기 실패/fixture 오류·선택/실제 고유row·exit·source SHA·실행 중 변경·소프트 비용과 확인하지 않은 범위를 보존한다. 별도 판본 성공을 단일 최종 전체 성공으로 합산하지 않는다. 비용캐시 관측은 evidence에 보존한 뒤 own base로 복원하고 공식 미러 생성/check를 마친다. report.json을 check.py report C:/math/.async/dm keep-evidence PASS로 제출한다. 공용 소스/문서/queue/state·서비스 engine·Git index·graphify·기존 연구 운전은 수정하지 않는다.
