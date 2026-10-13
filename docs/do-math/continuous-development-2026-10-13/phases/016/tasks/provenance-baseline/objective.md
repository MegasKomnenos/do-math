## 목적과 역할

G2/G3/G7의 P10/P11 두 exact-baseline 비교는 별도 pre-provenance-fix scripts 입력이 없어015에서 skip됐다. 이 task는 비교에 쓸 실제 과거 판본을 Git 원본과 원문 요구에 결속해 자기 evidence에 준비하는 한정 조사/입력 구축이다. 제품 실행이나 비교 통과를 맡지 않는다. 병렬 fixture 수리와 독립적으로 Git 불변 객체/015 원자료와 상대 쓰기 범위 밖의 shared-input 시험만 읽고 후속 연결 task가 사용할 입력을 반환한다.

## 완료 조건

### A1 비교 성질과 역사 판본 확정

test_shared_input_provenance.py의 assert_baseline_capture·두 exact_baseline 시험과 PROBE/SNAPSHOT/WORKER/merge를 읽고 보존할 ordinary outcome/read 횟수, literal entered/open/import_open·coverage의 파일/context/행/arc, 명시 marker 차이 및 두 worker 합집합을 설명한다. prior-review-state의 PR01 관련 slice와 requirement-state의 P10/P11 원문 경로, Git log/show의 도입 diff 및 존재 원보고를 따라 pre-fix 후보 commit을 확정한다. 단순히 현재보다 오래된 커밋이나 다른 디렉터리라는 이유로 baseline을 정하지 않는다. 고친 provenance 동작의 도입 직전 실제 API를 갖추는지 source로 대조하고 없어진 원보고의 위치/한계를 기록한다. 필요한 입력 판본을 해소할 수 없으면 blocked/partial과 정확 원인을 보고한다.

### A2 별도 과거 scripts 트리와 바이트 검증

선택한 불변 Git commit의 scripts 파일을 자기 evidence 아래 새 pre-provenance/scripts에 추출한다. checkout/reset/worktree·현재 제품 파일의 과거 교체는 하지 않는다. git ls-tree/show/cat-file/archive 등 읽기만 사용하며 저장소 밖 절대 경로/..·symlink 재분석 이탈을 허용하지 않는다. 전건 파일 경로·Git blob·SHA256·추출 명령/선택 commit과 도입 commit을 manifest로 기록하고 실제 추출 bytes를 Git 객체와 대조한다. 비교에 필요한 support/runner/제품 import 의존 파일은 원래 트리 그대로 포함하며 현재 파일을 섞거나 옛 코드를 현재 API에 맞게 고치지 않는다. 현재 root나 현재 사본을 pre-fix라고 이름만 바꾸지 않는다. 과거 연구 인스턴스·삭제된 사용자 자료를 복원하는 작업이 아니다.

tree가 현재 SCRIPTS와 다른 절대 경로이고 필수 run_tests.py·tests/support/branch_gate.py·t3_store.py 등 시험 소비 파일이 존재함을 검사한다. 정적 AST/텍스트/파일 해시 검사는 가능하지만 현재/과거 제품 import·시험 실행은 하지 않는다. tree와 manifest를 자기 evidence에 보존하며 원자료를 재작성하지 않는다.

### A3 실제 비교의 후속 책임과 실행 입력 인계

후속 연결 task가 설정할 SHARED_INPUT_BASELINE_SCRIPTS의 절대 경로, 정본/미러 공식 runner의 두 정확 ID 명령, 기대되는 skip0·실제 old/new 관측과 소스/도구 판본 기록 방법을 review.md에 준다. 코드에서 확인된 API 차이·비교 실패 가능성은 사실/가정으로 구별한다. 정상 도달이나 비교 성공은 실행 전에는 주장하지 않는다. 현재015 원자료의 skip·역사 raw 부재와 최종 G2/G7 미충족을 그대로 유지한다. 선택한 역사 입력이 정책상 제외되거나 바뀌어야 한다는 결론이면 원문·위임 근거와 상실되는 성질을 명시하고 임의로 skip을 승인하지 않는다.

## 판단과 경계

writes는 빈 목록이다. 자기 report/evidence의 트리·manifest·조사 자료만 만든다. 제품/시험·공용 context/plan/seams·다른 task/evidence·Git index·미러/캐시/설치·engine·기억을 수정하지 않는다. 상대가 수정하는 현재 fixture나 실행 결과를 읽어 판단하지 않는다. 현재 branch_gate/t3_store/shared-input 정의는 상대 writes 밖이고015 source-inspected와 해시를 대조해 읽을 수 있다. 그 외 현재 제품 의존을 조사할 때는 고정한 Git blob 또는015 보존 자료를 사용한다. 공식 시험·pytest/unittest·제품 import·실제 Job/Lean/예약·유료 호출을 실행하지 않아 공유 시험 자원을 점유하지 않는다. 모델은 사용자 지정 gpt-6.1-sol/high다.

## 검증 방법

cwd C:\math, Python C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe. git log/show/ls-tree/cat-file의 실제 argv·exit와 필요한 원출력, 추출 파일의 전건 blob/SHA 대응을 evidence에 기록한다. scripts 트리 파일 목록·선택 commit·현재 비교 대상의 고정 해시를 대조한다. 경계가 불확실하면 파일을 고치지 않고 finding으로 반환한다. 실행 성질은 후속 task의 공식 두 비교와 전체 T4가 확인하므로 이 작업의 완료는 입력 준비 완료다. 마지막 check.py report C:\math C:\math\docs\do-math\continuous-development-2026-10-13 016 provenance-baseline을 통과하고 report 경로/상태를 반환한다.
