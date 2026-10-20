# 현재 수용판을 사용자 목표와 대조해 인도 가능 범위를 판단한다

사용자 목표는 do-math에서 결함이 시험을 빠져나가는 공백을 실제 제품 경로와 의미 있는 단언으로 막고, 원요구에 맞는 시험·코드 재편 결과를 사용할 수 있게 만드는 것이다. G1 원30의무, G2 K61/P2 12, G3 PR25/109slice의 현재판 연결과 G6 수리가 수용됐다. 이 작업은 모든 수용 work 이후의 제품수정없는 G8 최종 review다. 새 전수조사나 최종전체 실행을 뜻하지 않는다.

## 읽기 시작점과 권한

자기 task.json·inputs/context/plan/seams와 RECORDS/managers/0107/review.md·handoff-delta.json을 먼저 읽는다. RECORDS=C:/math/.async/dm, 공용소스=C:/math, 과거기록 P=C:/math/docs/do-math/continuous-development-2026-10-13이다. 제품은 자기 workspace의 고정판을 읽는다. source_repo의 Git branch/HEAD/index/작업트리는 인도판 대조에 필요한 읽기만 허용한다. 제품/미러·공용문서/queue/state·이전 task 기록을 변경하지 않는다. 자기 report/evidence만 작성한다.

원 user-decisions.md, 최신 sources/storage-scope-direction-2026-10-15.md·t3-targeted-direction-2026-10-16.md·mutation-recheck-direction-2026-10-17.md를 적용한다. 개별 의무와 역사판정은 이미 수용된 연결을 출발점으로 삼고 전체 옛context/역사로그를 다시 순회하지 않는다. 과거 코드가 꼭 필요하면 공식 workspaces.py restore RECORDS TASK baseline|result NEW_DIRECTORY PATH로 해당파일만 복원한다. 정리된 workspace 경로 부재는 증거 소실이 아니다.

## 맡은 결과

1. G1~G8과 원요구의 충족/미충족을 한 review 판단으로 연결한다. g1-close/evidence/obligation-state.json·gate-state.json과 g23-close/evidence/preservation-state.json·prior-review-state.json·accepted-delta-connections.json이 최신 연결이다. 원ID/원문·한정 수용 범위와 역사37/기반26 처분을 재사용하며 다시 전체 심볼/원로그를 검사하지 않는다. 연결 complete와 전체요구 충족은 구별한다. g23의 reference_roots.repo와 상속 fresh T3 문구는 manager0106의 해석 보완을 따른다.

2. g6-finish의 현재 제품·지침·공식미러가 실제 수용판/검증판과 어떻게 대응하는지 확인한다. manager0105의72통합bytes/36쌍 검수와 작업자의1388파일 공식mirror check는 재사용하고 이후 관련delta만 본다. g1/g23-close는 제품변경0이다. 정확 함수선택 CLI/API·오류 의미, Sim의 원오류 전파/유한초기화 및 기존 active/formal미호출 단언 등 변경된 계약의 설명과 실제 소비가 어긋나는 부분이 있으면 정확 파일·심볼·영향을 남긴다. 일반적인 개선 취향을 결함으로 만들지 않는다.

3. 원G4 성공과 현재판 실행 한계를 판정한다. 원general-b의4522passed/WinError1314 조건부skip1/exit0는 유효하다. 이후5runtime함수·Sim/helper·시험변경은 g1-close/evidence/edition-delta.json·post-g45-python-delta.json·post-g4-focused.diff에 연결됐다. 최종판의 단일 기본전체선택/실제행/fixture/소스전후/exit 보고는 없다. 원 '최종판 전체일반' 요구를 면제하거나 부분성공을 합산하지 않는다. 최신 일반회귀 정확ID/직접영향 조건 때문에 전체를 자동 실행하지도 않는다. 기존 근거로 충분한 성질, 실제 미확인 동작/입력, 한 전체보고의 부재를 구별하고, 필요한 후속이 있으면 구체적인 직접영향과 최소선택을 제시한다. 실행범위/요구 변경이 필요하다면 어느 원문 조건의 변경인지 밝힌다.

4. G5 원전체와 지정5모듈 추가판의 유효범위를 재사용한다. 비환경 원gap은 수용된 계약정리/성공관측에 연결됐으므로 이전15arc/16행을 다시 열지 않는다. 환경6arc/10행과 partial closing=false·전체index 미갱신·좌표/helper digest 자동store 제약을 보존한다. 단순 도구 상태를 제품결함으로 승격하거나 raw/index/closing을 편집하지 않는다. 다음측정은 지정5모듈 관련선택뿐이다. G6 원1677의1613killed+32trivial+이전10해결+동등1+정확21해결을 수용범위에서 재사용하고 전수변이/원증거 재검사0이다. repair-b09 부모 미완료와 세 개별결과 재사용, g6p-run cancelled/미수용을 유지한다.

5. G7 원T4의301passed/1error/2skip·exit1과 정확3수리passed·exit0를 별도판으로 유지한다. 실제예약T5와 Lean/Job/기본provider/학술의 한정 보장은 재사용한다. 현지원 native quota, 같은session 복수result/후속실패/절단/cleanup, 실제지급 역할 동적schema 원자료가 없는 조건은 정확하게 남긴다. L01 Q1 기존운전프로필·Q2원UTF-8 출력byte 권위/실제수신 조건은 g7-boundary-scope의 기존 질문을 유지한다. 같은질문/환경probe/한도실험/실호출/새세션/예약/설치0이다. 외부조건이 필요한 것과 로컬 코드로 처리할 수 있는 구체적 결함을 나눈다.

6. 인도판과 main의 관계를 읽기 전용으로 판단한다. manager0107이 본 공용 branch는 main, HEAD는54ff3e0e7fa5af9d3f7ff463044a43b07a52047d이며 작업트리/index 차이가 있다. worker 시작 시의 실제값을 기록한다. 통합된 현재 파일과 Git의 HEAD/index/검증판 일치를 혼동하지 않는다. 기존 사용자 변경/무관한 파일을 stage·commit·reset하지 않는다. 실제로 미반영된 제품 범위나 필요한 전달 작업이 있으면 후속 manager가 구체적으로 처리할 수 있게 적는다. 전체654파일의 역사diff 재감사나 모든 저장소 untracked 목록 덤프는 불필요하다.

## 완료 판단과 산출물

`evidence/judgment.md`에는 사용자 목표 기준으로 현재 인도 가능한 결과, 막는 정확 조건, 선택적 개선을 설명한다. `evidence/gate-verdicts.json`에는 G1~G8별 verdict·근거·유효판본/한계·남김·다음조건을 둔다. `evidence/delivery-state.json`은 검토한 현재판/인도판/main·지침/미러의 관계와 직접확인/재사용 범위를 남긴다. 별도관리 framework나 원30/K/P2/PR 전체JSON 복제본은 만들지 않는다.

review를 마쳤으면 report.status=complete가 가능하지만 이는 프로젝트전체충족 선언이 아니다. findings와 judgment에 목표완료 가능 여부와 이유를 명시한다. 후속은 (a) 로컬에서 가능한 정확수리/직접검증, (b) 외부입력이나 요구결정, (c) 이미 충분한 근거, (d) 선택적개선을 구별해 다음 manager가 action을 고를 수 있게 한다. 새 결함을 확인하면 원입력·실제코드·사용영향·최소수리범위를 함께 보고한다. 같은 인계문서 보완을 별도 task로 쪼개지 않는다.

정적대조와 기존 수용 근거로 충분한 범위에서 끝낸다. 제품 import·일반/T3/T4/T5·변이·실호출·환경probe를 새로 실행하지 않는다. 새실험이 필요해도 이 review에서 실행하거나 제품을 고치지 않고 정확 이유와 최소대상을 남긴다. 저장A22 공통보장을 재사용하며 가족별quota·새전수감사·push·graphify갱신·기존연구운전/삭제는 없다. 마지막 `python C:/math/services/async-development/check.py report C:/math/.async/dm g8-review`를 통과시킨다.
