# 기존 보존·재검토 판단을 G6 수용판에 연결한다

사용자의 목표는 기존 개선과 기대값을 보존하면서 시험이 실제 제품 결함을 포착하도록 하는 것이다. g23-handoff가 남긴 K61/P2 12·PR25의 연결에 이후 수용된 역사/기반review와 현재 수리를 반영해 G2/G3의 충족 성질과 정확 남김을 마감한다. 수용된 의미 판단이나 역사 변경을 처음부터 다시 감사하는 작업이 아니다.

## 입력과 권위

자기 task.json·inputs/context/plan/seams와 manager0105/review.md·handoff-delta.json을 읽는다. 제품은 자기 workspace에서 읽으며 writes=[]다. RECORDS=C:/math/.async/dm, 과거 P=C:/math/docs/do-math/continuous-development-2026-10-13이다. tasks/g23-handoff/evidence/preservation-state.json·prior-review-state.json·judgment.md, 원 P/sources/requirements-index.json의 비연속K61/P2 12·PR25/109slice를 출발점으로 쓴다. 원문/user-decisions와 sources/storage-scope-direction-2026-10-15.md·t3-targeted-direction-2026-10-16.md·mutation-recheck-direction-2026-10-17.md가 옛 수단/전수재확인 문구보다 우선한다.

manager0105/handoff-delta.json의 accepted_delta_records가 이후 수용결과의 정확 진입점이다. 추가역사37구간은0086/0087에서 처분됐고 PR05의1931/1932 차이도 해명됐다. pr-base-tests의1a/1d BT01~BT09는0092, pr-base-ports-r의1b/1c 17질문은0093에서 수용됐다. 기존72한정검토와 이 결과를 재사용하며, 원자료 부재/당시실행 한계를 지우거나 별도1932전수강도감사를 새요건으로 만들지 않는다.

## 맡은 결과

1. 원K61/P2 12를 보존한 evidence/preservation-state.json과 원PR25/109slice를 보존한 evidence/prior-review-state.json을 작성한다. 이미 충분한 의미판정은 해당 수용근거로 연결하고 이후 실제diff가 바꾼 성질만 현재 producer/consumer/시험/보고로 갱신한다. mapping과 실제hunk 검토를 구별한다. 폐기된timeout·누적예산·호환수단은 최신요구와 현재계약에 따라 처리하고 과거수단 보존을 새목표로 만들지 않는다.
2. g5-core-tail/edge/apply/recover·g5-target/remainder의 실제수리, g45-final의 시험/문서교정, g6-inputs/mutation-parallel/g6-finish의 실제단언/fixture/도구 변경 중 보존성질에 영향을 주는 부분을 연결한다. manager0103/0104의 후보·단언보존과0105의 최종diff·실패/정상 대응검토를 재사용한다. 새helper를 전수재감사하거나 모든mutant/시험을 재실행하지 않는다.
3. G6의 예열오류를 실제소비시험으로 옮긴 변경, 유한 합성초기화, Job 정리와 직접단언, 정확함수선택이 원기대/실제경로·외부경계대역·실패판정에 미치는 의미를 필요한 현재코드로 확인한다. 단언 수나 파일 존재를 충분한 증거로 쓰지 않으며 이미 확인된31후보 전체검토를 다시 생성하지 않는다. 실제새공백을 발견하면 정확 입력/심볼/영향과 최소후속을 남긴다.
4. 원G4/전체T3와 부분수리·G6판본별 처분을 새단일전체성공으로 합치지 않는다. 환경6arc/10행·index/store제약·G7/L01 외부입력·G8은 공용현재상태대로 남긴다. G1의30의무는 g1-close 소유이며 독립 작업이다. 그 결과를 기다리거나 임시산출을 소비하지 않는다.

완료는 원모집단의 누락/중복 없이 기존검토/새수용diff/현재소비/정확남김이 연결돼 manager와최종review가 다음행동을 결정할 수 있는 상태다. evidence/judgment.md에 변경된판정·재사용이유·실제남김만 설명한다. 새로발견된 결함이 없다면 수용된 질문을 억지로 다시 열지 않는다. 보고 complete는 이 연결 배정의 완료이고 G2/G3/G8 전체성공을 자동뜻하지 않는다.

## 최소 확인과 권한

읽기와 필요한 JSON/AST/파일대조만 사용한다. 바뀐 참조·원ID·수용기록·심볼 연결을 확인하되 모든과거SHA/원로그/증거를 재수집하지 않는다. 제품import·공식시험·실호출·환경probe·graphify는0이다. 과거코드가 정말 필요하면 workspaces.py restore RECORDS TASK baseline|result NEW_DIRECTORY PATH를 사용한다. 공용문서/queue/state·옛task·제품/미러는 읽기전용이고 자기report/evidence만 쓴다. 마지막에 check.py report RECORDS g23-close를 통과시킨다.
