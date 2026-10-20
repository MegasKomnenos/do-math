# 복구 수용판의 전체 T4와 직접 결함 마무리

manager0089가 g5-core-recover를 수용해 core의 입구·적용·복구 계약 묶음을 마쳤다. 현재 수용판에서 공식 전체 T4를 완결하고, 발견한 직접 결함의 수리·최소 확인·설명·미러를 함께 마친다. 과거 phase018의 295passed나 부분 T3를 현재 전체 경계 성공으로 바꾸지 않는다. 실제 선행은 g5-core-recover 하나이며 다른 역사 review나 G4/G5/G6 전체를 기다리지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, 자기 workspace의 do-math AGENTS.md와 scripts/tests/시험-지침.md를 읽는다. 추가 입력의 records/docs/설치 경로는 읽기 전용이다. manager0089/review.md와 g7-boundary-scope/evidence/judgment.md의 실행안 A·현재성 한계, g7-scheduler의 별도 예약 수용을 구별한다. 저장범위 사용자 지시와 설계3.3/A22에 따라 충분한 codec·저장·업무 보장을 반복하지 않는다.

## 실행과 수리

이 task는 공유 실경계/전체관문 슬롯의 유일한 실행자다. 시험은 jobs1로 한 번에 한 명령이며, 병행하는 pr-base-ports/pr-base-tests는 시험슬롯0인 읽기 작업이다. 뒤 g45-final은 이 task의 수용판을 소비한다. 단순 자원 대기를 위해 임의 sleep·lock framework를 만들지 않는다.

자기 workspace/.claude/skills/do-math에서 다음 공식 명령을 실행한다.

`python -u -B scripts/run_tests.py --tier T4 --jobs 1 --output <새 짧은 외부 출력 경로>`

위치 인자나 --match로 전체 선택을 줄이지 않는다. 현재 boundary 모집단을 runner에서 얻으며 295를 고정 기대값으로 쓰지 않는다. 제품·시험·문서·미러는 실행 중 고정한다. TEMP/TMP/TMPDIR와 output은 공용 저장소 밖 짧은 자기 경로로 두고 실제 설치 자식 cwd까지 확인한다. 기존 GIT_CEILING_DIRECTORIES를 보존하고 자기 부모/외부 임시root를 추가한다. Git 없는 임시root는 상위 C:/math를 찾지 않아야 한다. 시간 경과만으로 종료·skip·재시작하지 않는다.

실Lean compiler를 소비하는 boundary에는 현재 시험지침의 DO_MATH_KNOWLEDGE_TEST_LEAN을 적용한다. C:/math/.skill-workspace/do-math-toolchains 안의 실제 lean.exe를 읽기 전용으로 찾아 명시하고 command·파일 신원을 기록한다. 다른 task의 제품 코드나 공용 제품을 실행 소스로 쓰지 않는다. compiler 한 개의 존재를 Lake/Mathlib 전체 설치 준비로 간주하지 않는다. 현재 코드가 요구하는 별도 설치 입력이 없으면 정확한 미실행/환경 사실을 남기며 다운로드·설치·신뢰 승인·호스트 정책 변경으로 메우지 않는다. 이미 관측된 symlink1314/WSL 제약을 재탐색하는 별도 probe는 추가하지 않는다.

원 report와 traceback으로 실제 제품 결함, 현행 계약과 다른 fixture/기대값, 외부 환경 부재를 구분한다. 직접 관련 소수 수리는 같은 task의 do-math 정본·소비 시험·설명·공식 미러에서 끝내고 가장 작은 공식 선택으로 확인한다. 수리 뒤 최종판의 전체 T4를 완결한다. 이미 통과한 불변판은 반복하지 않는다. 큰 독립 결함/범위 밖 제공자/외부 조건은 유효 결과·정확 원인·최소 다음 범위를 partial/blocked로 보고한다. 임계값 완화·새 skip·제품 내부 대역·단언 약화·구판 호환·무관 정리는 하지 않는다.

자기 workspace에 독립 .git이 실제 측정 계약상 필요할 때만 준비할 수 있다. g5-core-recover/evidence/prepare.py와 g4-final/objective.md의 바이트 보존 규칙을 참고하되 자기 경로로 한정한다. 실제 base bytes의 로컬 commit, 빈 template/hooks·local 설정·filter/text/ident 비활성화·NUL pathspec을 사용하고 전후 bytes/HEAD/blob을 남긴다. 이미 존재하는 .git은 소유/root부터 확인한다. 공용 Git/index/commit·다른 .git 복사·remote/push·가짜 HEAD는 허용되지 않는다.

## 완료 판단과 인계

command/cwd/필요한 비밀 아닌 환경·시각·관측exit·원 report/stdout/stderr를 보존한다. selected와 fixture 아닌 reports[].rows가 정확히 대응하는지, 중복/누락/여분·counts/fixture_counts·subTest·complete/successful·changed_during_run을 읽는다. t4_adapter.complete/problems, tests_complete/test_counts, worker의 request/run ID/source SHA와 실제 measurement 게시를 함께 판단한다. adapter-coverage.json과 원 worker report/branch 자료·게시 manifest는 실제 존재하는 범위에서 보존한다. branch 도달률은 정보이며 임계값이 아니다. T4 자료를 T3 분모·색인에 수동 합산하지 않는다.

공식 JobsContract/runner가 자기 Job의 root signal·active0·빈PID 뒤 close하도록 두고 남은 자원은 정확한 Job/PID/경로와 상태로 보고한다. 원 source_sha256과 제출판 Python을 연결하고 문서/미러는 별도 bytes와 공식 build_skill_mirrors.py check로 확인한다. 필요한 생성 자료를 evidence에 보존한 뒤 캐시는 base의 실제 bytes/부재로 복원한다. 미러 전체 T4를 자동 반복하지 않으며 별도 실행의 필요는 실제 차이로 설명한다.

evidence/judgment.md와 report.json에 전체 T4의 결과·수리·판본·확인 한계·남김을 작성하고 `python C:/math/services/async-development/check.py report C:/math/.async/dm g7-t4`를 통과시킨다. 제품 변경이 없으면 changes=[]다. 공급자 유료 호출·예약 T5·설치 변경·전체 일반/T3/변이·공용 문서/queue/state·graphify는 이번 범위 밖이다. 기존 예약/최소 실호출 성과와 L01/실원자료 조건을 유지하며 전체 G7 완료로 확대하지 않는다.
