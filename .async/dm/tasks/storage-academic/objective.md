# 목표 판정·학술 후속 저장 6가족을 실제 생산과 연결한다

사용자 목표는 실제 생산값이 검증 켜진 저장소를 통과하고, 수신 스키마에만 남은 필드나 검사되지 않는 쓰기가 시험을 빠져나가지 않게 만드는 것이다. R01/1-A·1-B/K-78의 남은 가족 중 목표 판정과 학술 후속이 공유하는 여섯 가족을 한 task에서 판정하고 필요한 제공자·수신자·시험 수리와 최소 확인까지 마친다. 가족별 작은 task나 새 등록체계를 만들지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, do-math AGENTS.md·시험-지침.md를 읽는다. 원요구는 C:/math/docs/do-math/continuous-development-2026-10-13/sources의 user-decisions.md·requirements-index.json·model-policy-2026-10-14.md·document-batching-2026-10-14.md와 C:/math/docs/do-math/시험-재편-2026-09-29/설계.md 3.3/A20이다. C:/math/.async/dm/tasks/keep-storage/evidence/families.json의 root/family 키를 유지하며 managers/0049/review.md, storage-authority와 execution-fields의 수용 보고/현행 코드를 읽는다. 원자료와 공용 소스는 읽기 전용이다.

## 대상과 실제 선행

- research.goal_judgments, research.goal_assessment_basis, research.goal_status.
- runtime.academic_assessments, runtime.external_rejections, runtime.academic_resolution_records.

execution-fields만 선행이다. 이 결과의 실행 저장 계약과 governance.validate_independent_execution의 실제 계보/독립성 판정은 목표감사 및 학술 판정의 실행 증거를 소비하는 본 작업의 입력이다. 중앙 record_schemas와 governance도 같은 수용판에서 필요한 수리를 함께 해야 하므로 두 task를 겹쳐 수정하지 않는다. storage-authority는 이 선행에 간접 포함된다. 독립 storage-metadata의 종료는 필요하지 않으며 그 배정·미수용 workspace를 바꾸거나 소비하지 않는다.

## 판정과 수리

1. 여섯 가족의 현재 shape·정본 checker/validator/references·실제 생산자·Repository 저장 caller를 확인한다. 기존 표의 group/required 수는 조사 당시 색인이며 현재 정의를 따른다. goal_judgments/external_rejections/academic_resolution_records는 list item, academic_assessments는 ID 없는 typed list 전체를 담는 singleton이다. goal_assessment_basis는 현재 TEXT singleton, goal_status는 metadata 값이다. 빈 properties를 빈 역방향 성공으로 세지 말고 scalar는 /value, typed list는 실제 item과 닫힌 중첩 내용을 검사한다.
2. 기존 충분한 실제 producer→검증된 Repository/StateContract 게시/load→독립 단언·정확 원보고를 먼저 재사용한다. 학술 저장/형식 증거와 목표감사/학술 후속의 기존 직접 시험·support academic_scenes/academic_assessment_cases/academic_resolution_cases/governance_goal_seal을 읽는다. helper가 만드는 봉인·실행 입장·현재성 근거와 외부 포트 대역을 구별한다. 수동 current_state나 저장 직전 필드 주입을 실제 생산 근거로 승격하지 않는다. 이미 수용한 긴 공개 승인/위임·검토 여정을 반복하지 않는다.
3. GovernanceEngineMixin._apply_governance_goal_audit가 만드는 judgment와 academic.apply_goal_assurance/current_solution_basis의 소비를 연결한다. scope·추가감사·formal/assessment/dependency refs·독립 슬롯/실행·동일 basis·현재성·완전한 기록된 judgment group 조건을 유지한다. unsolved/mathematically_solved와 후속 무효화의 실제 쓰기, basis 기록·새 판본과 옛 head를 검사한다. execution-fields에서 정리된 실행 계보를 재도입하거나 공급자 신원을 임의 복사하지 않는다.
4. academic.assess와 AcademicEngineMixin._record_academic_assessment의 실제 적용된 TASKS 평가를 저장 수신까지 연결한다. criterion마다 정확 한 번의 증거, 세 decision, 현재 solution/requirements 해시·task_assessment_sha256·실제 외부효과 receipt의 소비를 확인한다. singleton이라는 이유로 닫힌 item/solution_basis/evidence 필드 검사를 생략하지 않는다. task/queue 전체 역방향이나 외부 전송 전 과정을 이 범위로 확대하지 않는다.
5. _academic_control의 원 외부반려 actor/text/source_ref/created_at/solution_basis와 academic.record_resolution/_apply_academic_resolutions의 독립 해소 기록을 연결한다. 원 Unicode/CRLF bytes, 원반려 불변, 해결/미해결, exact rejection/evidence/requirements hash와 지정 planner의 실제 input_solution_basis를 보존한다. 실제 저장 증거 조회와 누락·변화 시 미해소, 복수 해소의 원자성은 충분한 기존 단언부터 재사용한다. 열린 evidence map에 임의 닫힌 필드 의무를 새로 만들지 않는다.
6. 수신 required+optional 전 필드마다 실제 작성 분기와 저장·내용 단언을 연결한다. 새 전용 storage_academic_pairs와 계약시험이 필요하면 contracts.pairs.assert_pair를 재사용한다. 기존 family helper를 소비할 수 있지만 shape가 다르면 작은 명시 투영을 두고 같은 순방향/역방향 알고리즘을 복제하지 않는다. 실제 미생산 optional과 빠진 표본을 구별하며, 필요 없는 허용/소비는 같은 task에서 schema·호출부·직접시험·설명·공식 미러와 함께 정리한다. 남는 정상 필드 삭제·구판 alias/default/자동변환·검증 우회로 통과시키지 않는다. 미생산 optional 추가 반례가 같은 역방향에서 실패함을 한 번 확인한다.
7. 대상 여섯 가족의 의미 대응 완료와 전체 쓰기지점/분기 실행 도달을 구별한다. 현재 생산/쓰기 심볼·소스 SHA·정확 시험 ID/판본을 남겨 최종 fresh T3가 소비하게 한다. 원래84가족 중 다른29미배정, 새 storage-conversation의5가족, execution1 및 이미 수용한43가족의 최종판은 이 결과로 종결하지 않는다.

## 소유·최소 검증·제출

제품 수정은 task.json.writes의 자기 workspace에 한하며 여섯 가족에 필요한 변경으로 좁힌다. 중앙schema/governance는 execution-fields 수용 뒤의 판본을 사용하고 그 실행 계약·authority12필드 제거·knowledge27필드 제거·전이 basis 수리·state/10·원 SOURCE/restart·검토 결말·게시 뒤 stop을 보존한다. Repository/StateContract/initialization은 독립 storage-conversation의 소유이므로 읽기 전용이다. storage-metadata5가족은0050에서 수용됐고 그 단언을 보존한다. 그 경계의 실제 결함 때문에 수리가 막히면 최소 입력·원인·필요한 소유를 보고하고 독립 범위를 마친다. 가상의 의존성은 추가하지 않는다.

정적 분석과 유효한 원보고로 충분하면 실행하지 않는다. 수리의 남은 불확실성만 workspace 공식 scripts/run_tests.py --jobs 1의 가장 작은 관련 ID로 확인한다. 본 task는 execution-fields의 시험 슬롯을 이어받으며 storage-conversation과 동시에 실행돼도 두 task·각jobs1이다. 전체 상한3을 지킨다. 전체일반/fresh T3/전체변이/T4/T5, 새 모델/HTTP/Lean/Job/설치/OS예약·대형 저장 비용 실행은 하지 않는다. 실제 생산/저장/봉인과 외부 clock/Git/host/compiler/model 포트 대역을 보고에서 구별한다.

최초 실패·fixture 오류·교정 결과, selected/고유 실제 row·counts/fixture_counts·관측 exit·소스 SHA·changed_during_run·소프트초과를 보존한다. 다른 판본의 부분 성공을 합산하지 않는다. 필요한 확인 뒤 반복하지 않는다. 비용캐시는 관측을 evidence에 보존한 뒤 own base로 복원하고 공식 build_skill_mirrors.py 생성/check 및 쓰기 범위를 확인한다.

evidence는 기존 가족표의 대상6행과 필요한 현재 정의/생산/수신/단언/판본·유지/수리/제거 이유·정확 남김만 확장한다. 공용 context/plan/seams/queue/state·다른task·engine·Git index/commit·graphify·기존 연구는 변경하지 않는다. protocol 형식의 report.json을 작성하고 `python C:/math/services/async-development/check.py report C:/math/.async/dm storage-academic`을 통과시킨다. 통합·수용은 manager가 맡는다. 다른 원요구/K/P2·G4~G8·L01·Windows1314·최종 review는 남는다.
