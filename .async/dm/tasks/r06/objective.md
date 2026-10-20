# 목적과 완료할 결과

R06/1-C의 남은 질문, 즉 현재 생산자가 명시 null을 쓰는 필드가 그 필드를 읽는 모든 소비자에서 의미에 맞게 처리되는지 판단한다. 이미 수용된 r04/r05의 값 영역·null slice를 재사용하고 실제 공백의 가까운 시험 수리·미러·최소 확인까지 한 task에서 마친다. 생산자 없는 가상 null 결함이나 새로운 전수 실행 의무를 만들지 않는다.

## 입력과 실제 범위

SESSION_JSON의 workspace, 고정 inputs/context.md·plan.md·seams.md와 task.json을 읽는다. 상대 제품 경로는 자기 workspace다. C:/math/docs/do-math/continuous-development-2026-10-13의 sources/user-decisions.md·requirements-index.json과 phases/001/tasks/closure-map/evidence의 requirement-state.json[1-C]·tracking-state.json[R06]·prior-review-state.json[PR06 B58]·evidence-catalog.json은 읽기 전용 원자료다. 큰 JSON은 해당 항목만 읽는다. 원문 repo:docs/...는 C:/math이고 run:은 위 continuous-development 루트다.

r04/r05 report와 r05 evidence/boundary-map.json·verification.json, managers/0009/review.md, r03-fix report 및 managers/0013/review.md가 재사용할 시작 근거다. r04의 실제 runner 결과8표본과 두 JSON 표현, r05의 native/runner·academic grant_id·extension null/부재, r03-fix의 현행 관찰 저장 계약을 새 반례 없이 다시 구현하거나 반복 실행하지 않는다. r09의 제출 수정·r12-r13의 교차 시험·r14-fix의 관찰 진행성은 별도 사본에서 진행할 수 있으며 그 미완성 결과를 소비하지 않는다. r06은 현재 고정판의 필드 소비 질문이라 이들의 종료를 선행으로 요구하지 않는다.

## 답할 유한 질문

1. do_math/와 최상위 제품 scripts의 현재 명시 null 필드 생산을 실제 파일·심볼·객체 가족·생산 조건으로 좁힌다. dict literal/대입/update 등은 발견 수단이며 AST나 rg 결과만으로 완전성을 주장하지 않는다. 함수 결과·조건식 등 간접 None을 필드에 담는 생산도 현재 값 흐름에서 확인한다. 단순 지역 변수/기본 인자/함수의 None 반환을 자동으로 JSON 필드 null에 합치지 않는다. 제외는 이유가 있어야 하며 schema에서 nullable인 목록을 실제 생산 목록으로 대신하지 않는다.
2. 각 실제 생산 필드가 저장/직렬화/반환을 지나 어디서 읽히는지 직접 소비자와 전달받은 값의 최종 사용을 연결한다. 같은 key 이름이라도 다른 객체의 필드는 구별한다. 명시 null·key 부재·빈 list/dict·정상 값의 의미를 현재 계약으로 판단한다. 단순 no-exception뿐 아니라 실제 계약상 반환/분기/보존을 확인하며 null이 잘못된 입력이면 명확한 반려 경계를 구별한다. 원래1-C의 모든 소비자 질문을 대표 한 곳으로 축소하지 않는다.
3. observations.observe의 deadline_only 반려는 followup 키를 생략한다. 과거 observed.get('followup', {}).get('kind')의 잠재 예외를 현재 생산 null의 도달 결함으로 보고하려면 실제 producer가 필요하다. 없는 필드를 억지로 생산시키거나 옛 계약을 복원하지 않는다. r04/r05에서 확인한 null slice는 정확 필드·소비자·판본 범위만 재사용하고 전체 R06 완료로 확대하지 않는다.
4. 실제 코드와 기존 정확 단언/유효 원보고로 충분하면 정적 판단으로 끝낸다. 남은 불확실성이 실행을 필요로 하면 실제 producer→consumer의 가장 작은 호출과 정상 대조군을 사용한다. 필요한 보완은 기존 producer/record storage 시험 또는 전용 null unit/sim에 묶는다. 기존 fixture/정본을 우선 쓰고 새 support/null_consumers.py는 실제 중복을 줄일 때만 만든다. evidence의 생산·소비표를 영구 제품 registry나 일반 정적 분석 프레임워크로 만들지 않는다.
5. PR06 B58/storage_detail_integration의 실제 관련 hunk→현재 caller/수신자→원보고의 정확 ID/판본을 같은 null/producer storage 질문에 한정해 연결한다. 다른 PR06과 원래K/P2 전체를 새로 종결하지 않는다. 현재 없는 Temp 원보고의 counts는 성공으로 합산하지 않는다. nullable 저장 자체와 다른 소비자의 실행 성공을 구별한다.

## 수정·확인·보고

task.json writes만 수정한다. 허용 시험은 tests/unit/test_producer_record_storage.py·test_record_family_storage.py, 필요할 때 unit/test_null_consumers.py·sim/test_null_consumers.py와 전용 support/null_consumers.py, 대응 미러·비용 캐시다. runtime·schema·공통helper·기존 provider/submission/scheduling/cross 시험은 읽기 전용이다. runtime 결함 또는 범위 밖 수리가 필요하면 실제 생산 입력→소비→기대/실제·심볼·필요 쓰기를 보고한다. 별도 runtime 소유 task와 충돌하지 않도록 유효한 조사/허용된 시험 보완을 마치고 미완료를 숨기지 않는다.

공식 실행이 필요한 경우 자기 workspace scripts/run_tests.py, jobs1로 최소 ID를 선택한다. 실제 producer/consumer/validator/Repository를 대역으로 가리지 않고 기존 외부 Job/CLI/Git/Lean 포트 fixture를 재사용한다. 새 외부 실호출·전체 일반/T3/변이/T4/T5는 배정하지 않는다. 이미 충분한 확인을 새 이유 없이 반복하지 않는다. 소스 고정·선택/실제row/exit/판본·fixture 오류·남김을 evidence에 보존한다. 현재성/삭제 전이와 R08의 역사 미결은 null 소비의 직접 영향이 있을 때만 연결하고 별도 정책을 만들지 않는다.

제품 변경이 있으면 공식 build_skill_mirrors.py --target .agents와 --check --target .agents로 미러를 생성·확인한다. 바이트 일치로 충분하면 미러 시험을 반복하지 않는다. 비용 캐시2개는 evidence에 보존한 뒤 base로 복원한다. 무변경이면 changes=[]이며 미러 생성/실행을 억지로 추가하지 않는다. report에는 실제 판정/수리·근거·정확 미결과 판본을 남기고 check.py report C:/math/.async/dm r06의 PASS를 확인한다. 모든 생산/소비 관계를 다 확인하지 못했으면 정확 남김을 적고 complete로 감추지 않는다. 공용소스/문서/queue/state·engine·다른task·과거원자료·Git index를 수정하지 않고 graphify도 갱신하지 않는다. G4~G8·L01·Windows1314 미검사는 유지한다.
