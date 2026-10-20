# 원래 30개 의무를 수용된 결과와 남은 관문에 연결

사용자 목표는 do-math 시험·코드 재편을 실제로 사용할 수 있는 상태로 마치는 것이다. 현재 수리 결과는 여러 task와 manager 판단에 수용돼 있지만, 원래 1단계19·2단계11 의무의 상태표는 초기 조사판에 머물러 있다. 이번 작업은 이미 판단한 내용을 재감사하지 않고 그 30개 의무에 현재 수용 결과·구체적 남김·필요한 최종 관문을 연결한다. 무엇을 더 해야 하는지와 이미 충분한 부분을 구별할 수 있는 인계 자료가 결과다. 전체 G1 완료 인증이나 제품 수정 없는 최종 G8 review가 아니다.

## 입력과 범위

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md와 자기 workspace의 do-math AGENTS.md를 먼저 읽는다. 현재 상태는 manager0080 기준이다. 실제 선행은 g5-entry-gate·g5-trust-rest·g5-core-rest의 수용 결과다. g5-core-gaps와 g7-boundary-scope는 진행 중이며 그 workspace/미완성 보고를 소비하거나 배정을 바꾸지 않는다. 시작 시 복사된 소스와 입력을 판단 기준으로 삼는다.

원문과 모집단은 C:/math/docs/do-math/continuous-development-2026-10-13/sources/requirements-index.json의 group=stage1/stage2 30행이다. 같은 실행의 phases/001/tasks/closure-map/evidence/requirement-state.json에서 그 30행만 출발점으로 읽고, original/source·당시 질문·원근거와 현재 결과를 구별한다. 초기 classification을 현재 사실로 복사하지 않는다. user-decisions.md, 원설계 설계.md, records/sources/storage-scope-direction-2026-10-15.md의 후속 사용자 판단이 우선한다. run: 참조는 C:/math/docs/do-math/continuous-development-2026-10-13 기준이고 repo:는 자기 workspace의 제품 또는 명시된 원자료다.

공용 plan의 수용표/남은 질문과 context의 G1~G8을 먼저 사용해 관련 task를 찾는다. records/tasks/ID/report.json·evidence/judgment.md 및 해당 manager 검토는 읽기 전용이다. 수용 여부는 시작 입력에 설명된 accepted 결과와 integration 기록으로 확인한다. 필요한 원보고/관련 현재 정의·시험만 좁게 따라가며 모든 과거 로그·모든 파일 SHA·과거 diff를 재수집하지 않는다. 부족한 연결 때문에 추가 코드 읽기가 필요한 경우에만 그 근거를 확인한다. 파일 존재나 task.complete만으로 의무가 충족됐다고 판단하지 않는다.

## 맡은 결과

1. evidence/obligation-state.json에 원모집단 30개 ID를 중복·누락 없이 연결한다. 각 행은 원문 위치와 요구 성질, 관련 accepted task, 현재 제품/시험의 정확한 파일·심볼, 판단을 뒷받침하는 수용 검토/원보고 위치와 확인된 범위, 구체적 남김, 다음 판단에 필요한 조건을 담는다. 이전 전체판·부분 실행·현재 소스판과 최종 관문 대기를 구분한다. 원문 전문·거대한 이력 복제나 새 framework는 필요 없다.
2. 이미 수리·판정된 질문은 수용 근거를 재사용해 다시 열지 않는다. 현재 의미/수리 완료 후 최종판 실행만 남은 상태, 진행 중 task의 실제 결과가 필요한 상태, 외부 조건이 필요한 상태, 아직 근거가 부족한 구체적 질문을 구별한다. 미해결로 남길 때는 정확한 의무/성질과 부족한 근거, 현재 영향, 필요한 최소 다음 행동을 쓴다. 원문에 없는 무한 입력 전수 입증을 새 종료조건으로 만들지 않는다.
3. 저장 관련 1-A/1-B/1-D는 A22와 사용자 저장범위 지시를 함께 적용한다. 공통 codec·입력/저장 검증·기존 업무 보장과 최종 T3의 쓰기분기 책임을 재사용한다. 과거 가족별 전필드/새 reader/옛 head quota는 철회됐으며 이를 다시 남김으로 만들지 않는다. 실제 수리된 참조/게시/미생산 필드 결함과 반복 입증을 구별한다.
4. g5-core-gaps가 영향을 줄 수 있는 행은 현재 수용판의 한계를 쓰고 그 task의 수용 diff/결과에서 무엇만 다시 확인하면 되는지 표시한다. g7-boundary-scope가 소유한 실경계/L01 조건은 그 소유와 기존 미충족만 연결하고 새 실환경 조사·probe를 중복 수행하지 않는다. 두 동료의 완료를 기다리는 장벽은 두지 않는다.
5. evidence/judgment.md에는 이미 충분해 재사용한 묶음과 실제 남김만 요약한다. 기존 r/keep/storage 검토의 전체 재수행, K61/P2 12/PR25 영역의 전수 재검토는 범위 밖이다. 이들의 공유 증거가 30의무 판단에 직접 필요한 경우만 참조한다. 전체 G2·G3·G4~G8의 완료율이나 새로운 종합 통과를 만들지 않는다.

## 최소 확인과 제출

writes=[]·시험슬롯0이다. 제품·시험·설명·미러·공용 문서·queue/state·다른 task·기존 원자료는 수정하지 않는다. 제품 실행·새 시험·전체 관문·실호출·환경/권한 변경·graphify 갱신은 하지 않는다. 새 결함을 발견하면 정확한 경로/근거와 최소 수리 범위만 보고한다. 구현이 필요한 후속은 manager가 별도 work task로 배정한다.

원모집단 19+11과 결과 ID의 일치, 각 판단의 참조 경로·심볼과 적용 범위, 진행 중/최종판/외부 조건의 누락 여부를 정적으로 확인하면 충분하다. 현재 모르는 사실은 모른다고 남긴다. 자료 형식을 검증하기 위한 새 제품 테스트를 만들지 않는다. report.json은 수행한 연결과 이유, 읽어 직접 확인한 범위, 미완료 사항을 담고 changes=[]로 제출한다. python C:/math/services/async-development/check.py report C:/math/.async/dm g1-handoff를 통과시킨다.
