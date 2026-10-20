# 실제 저장 검증과 생산 결과·왕복 보존을 연결한다

사용자는 엔진 시험이 저장 검증을 우회해 잘못된 생산값을 통과시키지 않고, 게시된 원문·판본·검토 결말을 실제 저장소에서 확인할 수 있어야 한다. KEEP-STORAGE의 K-36/37/45/52/67/78과 같은 저장 경계의 R01(1-A/1-B)을 현행 정의·정확 단언·원보고에 연결한다. 충분한 수용 근거를 재사용하고 확인된 공백의 구현/시험 수리와 필요한 확인을 이 task에서 함께 마친다. 새로운 전수 감사나 전체 저장 성능 실행을 만드는 작업이 아니다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, do-math AGENTS.md와 시험-지침.md를 읽는다. C:/math/docs/do-math/continuous-development-2026-10-13의 sources/user-decisions.md·model-policy-2026-10-14.md·document-batching-2026-10-14.md 및 requirements-index.json, phases/001/tasks/closure-map/evidence의 requirement-state.json·tracking-state.json에서 지정 ID, prior-review-state.json의 직접 관련 PR05/PR06 slice를 읽는다. 원문은 C:/math/docs/do-math/시험-재편-2026-09-29/조사/대역-사각지대.md·결함-범주.md와 단계-전환표-2026-10-03.json의 preservation 및 storage_population_integration/storage_detail_integration/boundary_storage_guard_correction다. 거대한 전문 대신 필요한 키와 실제 소스를 읽는다. 과거 StateStore/NoRepository/Host/ReviewFakeEngine 이름과 지금 제공자를 구별하고 폐기 대역을 복원하지 않는다.

## 판정할 유한 질문

1. K-36/37: support.storage_records.engine_on·Sim이 실제 ResearchRepository/StateContract를 통해 저장하고, 저장된 artifact와 같은 snapshot reader를 소비하는지 판정한다. 현재 ResearchRepository.validate_candidate/save_with_state/published_state의 전체 정규화 views·게시 head·no-op 판단과 Unicode 및 bool/int 차이를 연결한다. 과거 대역의 무조건 읽기 반려/항상 None을 지금 실제 저장소의 요구로 확대하지 않는다. 계산 결과·원 bytes/해시는 fixture의 독립 원천에서 기대하고 실제 reload/read_record/read를 확인하는 기존 직접시험을 재사용한다.
2. R01/K-78: r22-storage의 기존 88가족 표와 수용된 r03-fix/r06-finish/r22-snapshots 결과를 출발점으로, 현재 저장 가족/생산 분기의 양방향 필드 대응과 검증 켜진 저장 receiver의 값·도달을 확인한다. 이름/등록/AST와 실제 분기 실행은 다른 근거다. 저장 guard를 대역으로 가리는 경로나 필수/선택 필드의 미생산·미선언 쓰기 누락이 있으면 그 가족/분기와 원인에 맞춰 최소 수리한다. 이미 충분한 가족을 다시 전건 실행하거나 큰 저장 fixture를 재실행하지 않는다. 공통 schema 표본만으로 실제 엔진 모든 분기 도달을 주장하지 않는다.
3. K-45: 옛 Host._save의 소유 스레드·게시 head·게시 후 stop 성질이 현재 CoreEngineMixin._save/_reload/_unchanged와 Calls owner 경계의 어디에 제공되는지 판정한다. 현재 _save 자체가 별도 thread 검사기를 갖는다고 미리 가정하지 않는다. r15-r16의 실제 Calls 정산 근거를 재사용하고 필요한 직접 caller의 공개 동작·게시/stop 순서를 작은 입력으로 확인한다. 진행 중 r49-startup의 core/engine/parallel 계약을 임의로 수정하지 않는다. 저장 owner 밖 수정이 실제로 필요하면 입력·관측·소유 파일을 명시해 인계한다.
4. K-52/67: KnowledgeRoundtripHarness.cycle, review_inputs.reviewed_candidate, knowledge_impact.seal_review와 review_research.defer_review_for_research의 현행 결말/입장/봉인·유예 단언을 실제 caller에서 확인한다. 순수 검토 fixture와 Sim 수송의 책임을 구별한다. 제품의 명명된 정의 import와 독립적으로 적을 기대 계산값을 구별하고, 저장 결과를 같은 생성 함수로 기대값으로 다시 만드는 순환 단언만 있다면 고친다. review_research와 역할 입력 helper는 시작판에서 읽기만 한다. K-67을 전체 시험 literal 전수 교체나 새 lint 정책으로 확대하지 않는다.

각 지정 K와 R01에 실제 제공/소비 심볼·정확 시험 ID/단언·원보고/판본·현행 충족 또는 구체적 남김을 남긴다. r22-storage의 크기 질문과 이번 저장 검증 질문은 구별하며, r22-snapshots의 수용된 구조 공유·state/10을 되돌리지 않는다. 수용된 요청/신뢰/관찰 pair의 실제 producer와 역방향 단언도 보존한다. PR05/PR06은 실제 관련 diff·현재 소비·원보고만 한정 판단하며 전체 완료로 확대하지 않는다.

## 쓰기 경계와 완료

task.json의 저장 runtime/직접 시험/helper·미러에 한해 필요한 수정이 가능하다. 제품 core/engine/lifecycle·role_answers/model/engine_purpose/review_research/scheduling_parallel 및 이들의 진행 중 소비시험은 읽기 전용이다. r49-startup/keep-inputs의 미수용 결과나 작업판을 소비하지 않는다. 현재 연구 자료나 과거 원보고를 수정하지 않는다. 공유 README/이음새 설명은 이 task에서 바꾸지 않고, 변경 계약의 정확 파일·심볼·입출력·오류 의미를 report에 남겨 manager가 공용 seams에 연결하게 한다.

정적으로 충분한 질문은 읽기로 끝낸다. 필요한 경우 workspace의 공식 run_tests.py --jobs 1로 실제 불확실성을 해결하는 최소 ID만 실행한다. 저장 단위/시뮬레이션은 실제 repository/contract 위의 Git 포트 대역을 사용하고, Git 실행 자체를 확인해야 할 때만 소유한 짧은 임시 저장소에서 기존 직접 경계시험을 사용한다. 전체 일반/fresh T3/변이/T4/T5·외부 공급자/실Lean/예약 호출이나 새 큰 비용 실행은 하지 않는다. 시간 경과를 강제종료·성공·변이 포착으로 바꾸지 않는다.

선택/실제 고유row·초기 실패와 fixture 오류·exit·source SHA·실행 중 변경·소프트 초과와 실제/대역 경계를 보존한다. 별도 판본의 부분 통과를 단일 최종판 성공으로 합산하지 않는다. 비용캐시 관측은 evidence에 보존한 뒤 own base로 복원하고 공식 미러 생성/check를 한다. report.json을 check.py report C:/math/.async/dm keep-storage PASS로 제출한다. 지정 질문 완료와 G1~G3 전체·G4~G8 최종관문 완료를 구별한다. 공용 소스/문서/queue/state·engine·Git index·graphify·기존 연구 운전은 수정하지 않는다.
