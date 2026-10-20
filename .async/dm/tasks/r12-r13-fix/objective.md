# 목적과 완료할 결과

수용된 r12-r13의 F3를 끝낸다. 현재 공개 review replacement 요청에는 위임 사례의 두 독립 판단을 실행하고 실제 검토 자리를 교체하는 소비자가 있으나, 그 위임이 요구하는 같은 종류의 실제 사용자 원결정 생산 경로가 연결되지 않았다. 사용자 목표는 선언된 위임 경로와 교차 전이 검사가 실제 공개 생산부터 끝까지 동작하는 것이다. 원결정을 내부 dict에 끼워 넣거나 반려 seed를 성공 도달 증거로 세지 않는다. 필요한 생산/소비 수리, 직접 시험, 설명과 미러를 한 작업에서 마친다.

## 입력과 소유 범위

SESSION_JSON의 workspace와 inputs/context.md·plan.md·seams.md, task.json이 현재 배정이다. C:/math 공용 소스와 다른 task 기록은 읽기 전용이다. 선행은 r12-r13과 r14-fix다. core_engine.py를 수정하던 r14-fix가 수용된 시작판을 사용하고 그 관찰/진행성 변경을 보존한다. r09나 r06·r23-r24의 중간 결과는 필요하지 않다.

tasks/r12-r13/evidence/review.md·product.diff·original-inputs.json·current-population.json·b129-cross-slice.json과 managers/0015/review.md·source-review.json을 읽는다. 역사 원문은 C:/math/docs/do-math/continuous-development-2026-10-13 및 C:/math/docs/do-math/시험-재편-2026-09-29의 7-A/2-D와 원래 R12/R13·PR16이다. 현재 기능의 의미는 GLOSSARY.md의 사례별 위임, 계약/의도-해석.md, references/입력-소비자.md·CLI-실행-계약.md와 실제 governance/delegations/core/review 경계에서 확인한다. 사용자 요구, 현재 확인 사실, 새 구현 선택을 구별한다.

task.json의 쓰기는 해당 governance/delegations·review recovery 경계와 직접 schema/시험/helper/제품 설명/미러다. 모든 파일을 바꿀 필요는 없다. core에서는 검토 복구·위임 적용에 필요한 부분만 바꾸고 r08 제어 수송 수리와 r14-fix 관찰/진행성은 보존한다. submission/integration, scheduler/parallel/관찰 runtime, 공통 Sim·record_builders·provider helper는 읽기 전용이다. 모델/실환경 호출이나 기존 연구 운전은 범위가 아니다.

## 판정과 구현

1. governance.apply_decision의 실제 사용자 결정 생산, CoreEngineMixin._review_recovery_control/_apply_delegation_judgment, delegations._basis/prepare_application/judgment_input/record_judgment 및 review replacement 권한·현재 자리 검사를 연결한다. 현재 seed는 review_replacement 원결정의 unsupported 반려와 미생산 원결정을 참조한 delegation 반려만 확인한다. support/governance_delegation.py:replacement_case도 ORIGINAL을 직접 삽입한다. 두 사실을 실제 공개 성공과 구별한다.
2. 기존 명시 사용자 검토 교체와 사례별 위임의 의미를 사용 가능하게 연결한다. 새 범용 승인 계층이나 별도 상태 기계를 추가하기 전에 이미 보존하는 공개 요청/원문/결정 경로로 필요한 근거를 생산할 수 있는지 판단한다. 원결정은 실제 사용자 선택의 종류·대상·효과·출처를 보존하고, 위임 승인은 그 결정과 포함/제외 범위·자원·외부 효과·만료를 정확히 묶어야 한다. 현재 코드의 특정 kind 문자열이나 새 public decision 형태는 구현 선택이며 이 objective가 새로운 문법을 확정하지 않는다. 단순히 근거 검사를 느슨하게 하거나 machine grant를 위임 판단의 대체물로 쓰지 않는다.
3. 실제 공개 생산→위임 승인→현재 사례 요청→동일 봉인 입력의 독립 interpret/check→적용 또는 정확 사용자 질문/반려→저장·재시작을 직접 연결한다. within_scope/outside_scope/unresolved를 실제 판단 생산자에서 각각 도달시키고, 양쪽 within_scope만 실제 교체 권한으로 이어지는지 확인한다. 판단 입력에 상대 판단을 노출하지 않고 원결정/승인/사례의 정확 해시·현재성, 검토 대상/slot/cycle, 기계 실행 허가와 사용자 pause/종결 권한을 유지한다. 중복 요청은 기존 결과를 재사용하며 같은 자리의 후속을 중복 생산하지 않아야 한다.
4. 원문과 현재 계약을 읽어 특정 죽은 표현이나 불필요한 중복 경로를 줄이는 것은 허용한다. 그러나 선언된 사례 위임과 세 판정값을 삭제해 도달 공백을 숨기거나, 현행 기능을 축소한 결정을 사용자 합의처럼 쓰지 않는다. 기존 지원 경로로 같은 결과를 충족하면 그 경로에 생산/소비/시험/문서를 함께 맞춘다. 추가 사용자 의미 결정이 실제로 필요하면 독립적으로 마친 수리와 정확 선택/영향을 보고하고 추측으로 권한을 만들지 않는다.
5. cross의 고정 seed와 실제 @rule/precondition을 현재 생산 경로에 연결하고 필요한 전용 fixture를 수리한다. runtime 내부 dict 주입이나 제품 함수 patch로 성공을 만들지 않는다. 기존 F1의 알려지지 않은 예외 전파와 F2 원 실패 보존, 원문a/b/c 불변식과 LONG 설정은 유지한다. 이 파일에서 만나는 가까운 정확 반려 단언 보완도 함께 처리한다.

## 최소 확인과 보고

정적으로 충분한 부분은 원문·정확 단언·원보고로 끝낸다. 새 기능의 정상 공개 경로, 각 판정값, 정확 권한/현재성 반려와 실제 저장·재시작에 필요한 가장 작은 공식 run_tests.py --jobs 1 선택을 사용한다. machine 소비가 바뀌면 해당 기존 LONG 소비 하나를 포함하되 모든 LONG이나 전체 관문을 반복하지 않는다. 기존 근거를 재사용할 때 정확 ID·판본·변경 영향을 명시한다.

정본을 고정하고 공식 build_skill_mirrors.py --target .agents 및 --check로 미러를 맞춘다. 비용 캐시는 evidence에 보존한 뒤 자기 base로 복원한다. 소스 SHA·선택/실제 row·exit·원 실패와 최종 결과를 기록한다. F3의 공개 생산과 판단/교체 도달 여부, 구현 선택과 이유, 남은 구체적 문제를 report에 적는다. 전체 R12/R13·PR16·G4~G8 및 다른 정산/대기 질문을 이 좁은 수리만으로 종결하지 않는다. check.py report C:/math/.async/dm r12-r13-fix로 제출 형식을 확인한다. 공용 문서/queue/state·다른 task·base/inputs·engine·Git index·graphify를 수정하지 않는다.
