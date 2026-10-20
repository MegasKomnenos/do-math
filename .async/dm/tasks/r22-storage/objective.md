# R22/10-A에 남은 저장 가족의 원천 대비 크기

r21-r22의 F3를 이어 원문10-A의 저장 레코드 가족 크기 질문을 마친다. 가족별 별도 task나 대형 실행을 만들지 않고, 실제 생산 내용과 공통 저장 경계의 관계를 먼저 판단한 뒤 필요한 가까운 단언·수리·미러·최소 확인을 한 작업에서 수행한다. r21-r22만 선행이며 진행 중 null·관찰·위임 작업의 결과는 필요하지 않다.

## 목적과 현재 사실

SESSION_JSON의 workspace, 고정 inputs/context.md·plan.md·seams.md와 task.json을 읽는다. 사용자 원문은 C:/math/docs/do-math/continuous-development-2026-10-13/sources/user-decisions.md·requirements-index.json·model-policy-2026-10-14.md·document-batching-2026-10-14.md다. 원문10-A는 C:/math/docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md의10-A 및 단계-전환표-2026-10-03.json의 engine_population_integration, 이관 tracking-state R22/requirement-state 10-A에서 필요한 행만 읽는다. 과거 run:은 continuous-development 루트이며 C:/math/docs와 C:/math/.async/dm의 원자료/다른 task는 읽기 전용이다.

r21-r22는 역할25포장 상태·100과제×10이력·37프로필의 필수/원문 입력, 대형manifest, 4,286,783바이트 녹화·5선언/603폐포와 같은 폐포의1선언 투영, 공개 사전검사/원문회수 단언을 보완해 부분 수용됐다. report·evidence/judgment.md·producer-storage-symbols.json·start-consumers.json·runs.json 및 managers/0018/review.md·source-review.json을 재사용한다. 이 성질들을 다시 조사하거나 큰 fixture를 반복 실행하는 작업이 아니다.

원문 요구는 저장 논리 바이트가 원천 바이트의 상수배 이하이고 중복 인라인이 없는 것이다. 모든 가족에 같은5MB를 넣거나 모든 생산 경로를 새로 실행하는 것은 확정 요구가 아니다. 가족 전건의 관계를 정적으로 설명할 수 있으면 그 근거를 사용한다. 반대로 가족 이름 목록·빈 객체·codec 왕복 성공만으로 실제 생산 내용의 원천 대비 크기를 인증하지 않는다.

## 완료할 판단과 구현

1. 현재 default_state_contract().families()와 record_schemas.install의 실제 가족을 모집단으로 삼아, 기존 producer/record storage 시험과 r21-r22의 생산 경로에 대응한다. metadata/singleton/map/list의 공통 _encode_families→payloads.seal_large/encode→저장/load 성질과, 그 앞에서 원문을 복제할 수 있는 각 생산자의 책임을 구별한다. 같은 구조·같은 저장 규칙으로 충분한 가족은 함께 판단하고 새 제품 registry/생산자 완전성 체계는 만들지 않는다. 근거용 표에는 실제 정의·원천·저장 위치/단언·충족 또는 정확 남김을 연결한다.
2. 원천 바이트의 기준을 독립 입력에서 정한다. 이미 중복을 포함한 최종 instance/runtime를 분모로 쓰는2배 상한은 codec의 봉투 비용만 설명하며 생산자의 중복까지 잡지 못한다. r21-r22의 해당 단언은 이 한계 그대로 유지한다. 같은 불변 원문 여러 참조, record 수/이력 증가, JSON escape/UTF-8, root manifest/metadata/envelope 및 content-addressed payload의 비용을 실제 저장 정의로 구분한다. 상수·고정 overhead는 계약/구조에서 정하고 현재 출력값을 보고 키우지 않는다. 저장 논리 크기와 Git 압축·실제 디스크 용량도 구별한다.
3. 기존 evidence에서 빠진 goal_judgments·academic_resolution_records·self_check_responses·delegation_applications·review_cycles 등은 실제 생산/저장 코드와 기존 시험부터 읽는다. 이 예시가 새 전수 실행 목록은 아니다. 공통 규칙만으로 충분하지 않은 규모/중복 경계에만 실제 생산자를 사용하는 최소 입력과 내용 보존·바이트 단언을 전용 시험에 보완한다. 기존 Sim/record_builders/관찰/위임 fixture를 읽기 전용 재사용하되 생산 record를 사후 보충하거나 제품 호출을 대역으로 바꾸지 않는다. 선언된 실제 규모가 필요한 경계는 축소하지 않고, 무관한 가족에 억지로 큰 payload를 만들지 않는다.
4. 허용 범위의 직접 결함은 관련 수리까지 마친다. 충분한 기존 성질, 새로 보완한 성질, 미확인 생산 의미/범위 밖 결함을 구분한다. 위임의 공개 원결정 미생산은 이미 r12-r13-fix가 소유한다. 현재 수신·codec 성질을 판단할 수 있으며 그 기능을 직접 삽입해 공개 생산 성공으로 세지 않는다. 원래 F3를 작은 후속 조사로 반복 넘기지 않도록 정적 근거로 종료 가능한 관계는 종료한다.

## 쓰기와 독립성

task.json writes가 정본이다. tests/unit/test_engine_storage_scale.py·flows/test_engine_storage_scale.py와 필요한 support/engine_storage_scale.py, 관련 기존 크기 시험3개·engine_size_cases.py, 그리고 미러가 허용된다. 두 새 시험 층을 무조건 모두 만들 필요는 없고 실제 저장/producer 흐름에 맞는 최소 위치를 선택한다. runtime은 직접 재현한 해당 크기/중복 결함에 한해 payloads.py·knowledge_records.py만 수리할 수 있다. 다른 배정과 겹치지 않는 범위다.

repository.py는 r06-edges, producer/record storage 시험과 review_cycle/knowledge_io 등은 r06-domain, core/관찰은 r14-fix, 위임/정본schema/review_engine/공용 제품 설명은 r12-r13-fix 소유로 읽기 전용이다. 공통 fixture·state_contract·canonical·git_store·context_store·formal/tool/corpus 역시 읽기 전용이다. 현재 고정판을 소비하고 직접 읽는 함수/파일 SHA를 남긴다. 다른 task의 중간 workspace를 가져오거나 시작 배정을 바꾸지 않는다. 범위 밖 결함은 정확 생산 입력/관측/필요 파일·심볼을 보고하며 자기 결과를 마친다.

## 최소 확인과 제출

AGENTS.md와 scripts/tests/시험-지침.md를 따르고 제품 코드/단언/원보고 판본으로 충분하면 새 실행을 하지 않는다. 새 시험·수리의 불확실성에만 workspace 공식 scripts/run_tests.py jobs1로 가장 작은 관련 ID를 실행한다. 소프트 시간 초과는 보존하고 규모·내용 단언을 줄이거나 timeout을 성공으로 취급하지 않는다. 선택/실제row·exit·소스SHA·실행 중 변경·최초 실패/fixture 오류·재사용 한계를 evidence에 남긴다. 서로 다른 판본의 통과를 한 최종판 전체 성공으로 더하지 않는다.

공식 build_skill_mirrors.py --target .agents 및 --check --target .agents와 변경쌍 bytes를 확인한다. 비용 캐시2개는 evidence 보존 후 자기 base로 복원한다. report는 원문 질문의 충족/수리/정확 남김을 설명하고 check.py report C:/math/.async/dm r22-storage PASS를 확인한다. 새 전체일반/T3/변이/T4/T5·모델/Lean 실호출·graphify 갱신·예약·Git index/공용소스/공용문서 수정은 배정 밖이다. 전체10-A 및 G4~G8·L01·Windows1314의 별도 남김을 숨기지 않는다.
