# 원30의무를 G6 수용판과 기존 최종 증거에 연결한다

사용자의 목표는 결함이 시험을 빠져나가는 공백을 실제 제품 경로와 의미 있는 단언으로 막는 것이다. 기능과 검증 수리가 수용됐으므로, 기존 g1-handoff의 의무별 판단을 현재 판본에 연결해 무엇이 충족됐고 무엇이 실제로 남았는지 결정 가능하게 만든다. 새 전수 조사나 이전 작업 재검증이 아니다.

## 입력과 범위

자기 task.json·inputs/context/plan/seams, manager0105/review.md·handoff-delta.json을 읽는다. 제품은 자기 workspace에서 읽으며 writes=[]다. RECORDS=C:/math/.async/dm, 과거 P=C:/math/docs/do-math/continuous-development-2026-10-13이다. 기존 tasks/g1-handoff/evidence/obligation-state.json·judgment.md와 managers/0082/handoff-delta.json이 출발점이다. 원 모집단은 P/sources/requirements-index.json의 stage1 19개+stage2 11개다. 원문 요구/user-decisions와 현재 sources의 저장A22·지정5모듈T3·정확문제변이 재확인 지시를 우선한다.

manager0105/handoff-delta.json의 accepted_delta_records는 그 뒤 실제 수용된 변경·역사/기반review·관문 근거를 가리킨다. 전체 오래된 context를 순서대로 다시 읽거나 모든 task 원보고를 재해시하지 않는다. 각 기존행의 next_conditions/accepted_diff_check_only와 실제 영향 파일·심볼부터 대조한다. 관련 없는 수용 결과는 이유를 적어 기존판정을 재사용한다. 원task evidence와 integration은 보존돼 있고 필요한 과거 코드만 공식 workspaces.py restore RECORDS TASK baseline|result NEW_DIRECTORY PATH로 복원한다.

## 맡은 결과

1. 원30ID/원문 성질을 보존한 evidence/obligation-state.json을 작성한다. 기존 의미/수리 판단을 재사용하고 이후 수용diff가 바꾼 정확 성질만 현재 정의·소비 시험·보고 근거로 갱신한다. 처음부터30개 요구를 다시 시험하거나 기존 가족별 quota를 되살리지 않는다. 경로/심볼·필요한 현재 판본·확인범위·정확 남김·다음 조건을 연결한다.
2. 원G4와 전체T3, 지정5모듈 추가판본, 완료G6, 원T4/정확3수리 및 실경계의 기존 유효 근거를 구별해 evidence/gate-state.json에 간단히 연결한다. g45-final general-b는4522passed/1정당한WinError1314 skip/exit0의 원판본이다. G5-remainder의 Git CAS/정확core 변경과 G6의 시험/helper 변경이 기존 일반/경계 근거에 주는 직접 영향만 판단한다. 변화가 있다고 모든 근거를 폐기하거나 서로 다른 부분성공을 새 전체성공으로 합치지 않는다. 전체일반 자동반복은 하지 않으며, G4의 최종판 요구에 실제 남김이 있다면 어떤 실행/성질이 아직 부족한지 정확하게 남긴다.
3. G6는 원1677의 유효killed1613/trivial32·이전해결10·동등1·정확해결21로 처분됐다. manager0105가 새21의 실제실패/정상대응을 검수했으므로 변이·원모집단·원증거 전수감사를 반복하지 않는다. 최종전체 재실행과 판본별 재사용을 구별한다.
4. 환경6arc/10행, partial index/store 제약, G7 native quota/현지원 복수result/동적schema, L01 Q1/Q2·원출력UTF-8 byte의 실제 외부입력 조건은 g7-boundary-scope와 기존질문을 유지한다. 이미 끝난 scheduler/Lean/학술/기본provider 성질은 유효범위에서 재사용한다. 환경을 다시 probe하거나 새 실호출·새 세션·예약·설치를 하지 않는다. 최종 G8은 아직 수행되지 않았다.

완료는30행의 누락/중복이 없고, 의미수리 완료·유효재사용·정확한 미충족·최종review 대기가 구별돼 다음manager가 별도 재조사 없이 판단할 수 있는 상태다. report complete는 이 연결 배정 완료이며 G1~G8이 모두 충족됐다는 뜻이 아니다. evidence/judgment.md에는 바뀐 판단/재사용 이유와 바로 필요한 다음행동만 설명한다. 새 결함을 직접 확인하면 정확 코드/입력/영향을 보고하고 무관한 수리를 추측하지 않는다.

## 검증과 권한

정적 대조로 충분하다. 원ID와 행, 갱신된 실제 경로/심볼, 인용한 수용상태/보고/판본의 필요한 대응만 확인한다. 제품import·시험·G4/T3/T4/T5·변이·실공급자·환경probe는0이다. 공용문서/queue/state·이전task·제품/미러는 읽기전용이고 자기 report/evidence만 쓴다. g23-close와 독립이며 그 미완성 결과를 기다리거나 소비하지 않는다. 새 관리framework·장기감사·모든 역사원보고 재확인을 만들지 않는다. 마지막에 check.py report RECORDS g1-close를 통과시킨다.
