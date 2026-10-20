# 수용된 G4 판본의 fresh 전체 T3와 실제 도달 공백 처리

사용자가 요구한 G5는 최종 판본의 재사용 없는 전체 T3 측정이다. g4-final의 수용판을 받아 공식 `--tier T3 --full`을 실행하고, 실제 분기 합집합·함수 진입·선택 색인을 보존한다. 발견한 작은 관련 공백의 수리와 필요한 확인·설명·공식 미러까지 이 task에서 마친다. G4 통과를 T3 성공으로 가정하거나 저장 가족별 전수 시나리오를 새 선행조건으로 만들지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, 자기 workspace의 do-math AGENTS.md·scripts/tests/시험-지침.md를 먼저 읽는다. managers/0067/review.md·verification-review.json, g4-final/report.json·evidence/judgment.md와 사용자 저장 범위 교정을 소비한다. 원설계의 3.3/A22, 4.3, 5.3/5.5, A29/A30 및 시간 정책 정정을 필요한 범위에서 읽는다. C:/math/.async/dm와 docs의 추가 입력은 읽기 전용이며 repo 상대 경로는 자기 workspace의 정의다.

## 시작판과 Git 준비

수용된 G4는 동일 판본의 4288선택=고유4288행, 4287passed/WinError1314 조건부skip1, fixture오류·failed/error/not_run0·exit0이다. manager는 912Python SHA와 정본/미러2410파일이 공용판과 같음을 확인했다. 제품 변경은 없다. 원 G4의 선택·판본을 이번 시작판과 비교하고 이미 충분한 일반 검사를 측정 준비만을 위해 반복하지 않는다.

async snapshot에는 .git이 없다. 기존 `tests/support/branch_gate.py:repository_root/write_index`는 실제 Git root·HEAD·blob을 사용한다. **자기 workspace 루트에만 독립 .git 및 실제 사본 소스의 로컬 기준 commit을 준비할 수 있다.** g4-final/evidence/prepare.py의 TASK 자동 계산과 SHORT·commit 설명을 자기 task에 맞춰 복사해 사용한다. 이미 .git이 있으면 root/HEAD/소유를 먼저 확인하며 지우거나 재초기화하지 않는다. 다른 task의 .git은 복사하지 않는다.

기존 GIT_CEILING_DIRECTORIES를 보존하고 자기 task 부모·짧은 외부 임시루트를 추가한다. 외부 임시 cwd는 Git 탐색exit128, workspace는 정확한 자기 root여야 한다. Git redirection 환경을 확인하고 빈 template/hooks·local 설정·`.git/info/attributes`의 filter/text/ident 비활성화·NUL pathspec으로 실제 소스 바이트를 보존한다. 생성 캐시는 기준commit에서 제외하고 준비 전후 bytes·commit blob·실제 명령/환경/HEAD를 기록한다. 수리 뒤 최종 실제 소스의 로컬 commit을 추가할 수 있다. 이 .git/HEAD는 통합하지 않으며 공용main·성공 인증이 아니다. 공용Git/index/commit·전역설정·remote/push·새 비Git fallback·가짜 HEAD는 범위 밖이다.

## 공식 전체 측정과 필요한 수리

1. 현재 `run_tests.py:main/_finish_t3/closing_eligible`, `tests/support/branch_gate.py:Measurement/gate/write_index`, `t3_store.py`, `do_math/layers.py:LAYERS`에서 실제 측정 계약을 확인한다. 환경 준비는 정적 확인으로 충분한 범위에서 마친다. 선행의 adapter meta 7개나 전체 G4를 준비 확인만으로 다시 실행하지 않는다.
2. 제품·시험·문서·미러 판본을 고정하고 아래 명령을 한 번 완결한다. 출력/store/TEMP/TMP/TMPDIR는 저장소 밖 짧고 고유한 자기 경로다. 위치 인자·--match·다른 tier·--mutation-base를 추가하지 않는다.

   `python -u -B .claude/skills/do-math/scripts/run_tests.py --tier T3 --full --jobs 3 --t3-store <새 외부 store 경로> --output <새 외부 출력 경로>`

   이번 task가 기계 시험슬롯3개를 쓴다. 별도 시험·전체변이·실환경/예약/유료호출을 동시에 돌리지 않는다. 현재 일반jobs3 종료 뒤 resource 클래스를 순차 격리하는 배선에서는 meta 내부jobs2와 겹치지 않는다. 배선 변경 시 총시험worker3 이하를 다시 확인한다. 오래 걸리는 실행은 완료 알림/백그라운드 도구로 관리하고 시간 경과만으로 중단·skip·선택 축소하지 않는다. 실행 중 작업 사본을 바꾸지 않는다.
3. 원보고의 기능 실패, 측정자료 누락, 실제 미도달 분기를 구별한다. source의 정확한 분기·현재 계약·기존 시험을 읽고 같은 성질의 가장 싼 기존 시험에 필요한 입력/단언을 더하거나 실제 결함을 수리한다. 저장은 기존 검증/codec·업무 근거를 재사용한다. 이름 검사 한계를 이유로 전가족/전필드/새reader/옛head 의무를 부활시키지 않는다. 도달만 하고 결과를 확인하지 않는 호출, 내부 대역, 임계값 완화·층 재분류·새 skip·근거 없는 no-cover, 구판 호환, 무관 최적화·새 측정 프레임워크는 해결책이 아니다. 실제로 의도적 제외가 정당하면 원설계와 현재 코드의 이유를 함께 남기고 기존 구조 검사를 따른다.
4. 소수의 관련 결함/공백은 제공자·소비자·시험·설명·미러를 같은 task에서 수리하고 필요한 가장 작은 공식 선택으로 확인한다. 소스를 바꿨으면 최종 고정판의 fresh 전체 T3를 마친다. 여러 독립 영역으로 퍼져 한 작업에서 끝낼 수 없는 공백이나 외부 조건은 원측정·유효수리·정확한 모듈/분기/원인과 다음 소유 범위를 보존해 partial/blocked로 보고한다. 알려진 미수리를 둔 전체 실행 반복이나 부분합으로 성공을 만들지 않는다.

G4 이후 제품/시험/문서를 바꾼 경우 그 판본 차이와 영향, 수리의 직접 검증을 명확히 보고한다. G5를 실제 충족한 최종판이 G4 수용판과 다르면 같은 task에서 최종 기본 전체 일반 검사도 한 번 마쳐 G4/G5를 같은 판본으로 연결한다. G5가 여전히 미충족인 중간 수리판에 전체 G4를 반복하지 않는다. 소스가 불변이면 기존 G4를 재사용한다.

## 측정 의미와 인계

`closing_eligible`은 전체·소스불변·자료누락없음·재사용0이라는 측정 자격이다. branch gate 통과나 기능 성공의 대체값이 아니다. `branch_gate.gate`는 LAYERS의 1·2·3층을 판단하며 대상 모듈 부재도 미측정 실패다. `selection_index`가 쓰였다는 사실도 gate 통과를 뜻하지 않는다. G5 충족에는 실제 전체 행/fixture/종료값·불변판본, measurement_missing=[], store 재사용0, closing_eligible=true, branch_gate.passed=true와 정확한 대상·제외의 판단이 함께 필요하다. index는 runner가 생성한 원본을 보존하며 수동 보정하지 않는다. T4 adapter 자료를 T3 분모/도달/함수진입에 합치지 않는다. Windows1314 조건부skip는 G4의 원계약대로 구별하되, 그 분기 미도달이 있으면 G5를 자동 통과시키지 않는다. 호스트 권한은 변경하지 않는다.

command/cwd/필요한 비밀 아닌 환경·시각·관측exit·원 report/stdout/stderr와 실제 worker의 측정/요청/결과 파일을 보존한다. selected 대 실제 고유row, counts/fixture_counts·subTest·complete/successful·changed_during_run과 source_sha256을 직접 대조한다. coverage 보고/원data·함수진입/input 자료·생성 selection index·store 보고의 원경로/SHA를 남겨 G6가 현재 함수 모집단/선택 시험/정상 기준을 결정할 수 있게 한다. 소프트 예산과 초과·첫 실패·부분 측정도 그대로 보존한다. 기존 cleanup으로 없는 자식 파일은 보존했다고 주장하지 않는다.

생성 `.selection-index*`·`.timings*`·`.t3-store`는 필요한 원자료를 evidence 또는 자기 외부 경로에 보존한 뒤 자기 base 바이트/부재로 복원해 제품 변경에서 제외한다. 생성 파일 삭제가 필요하면 자기 workspace의 정확한 절대 경로·소유를 먼저 확인한다. base/baseline/inputs와 다른 task는 변경하지 않는다. 제품 수정이 있으면 공식 build_skill_mirrors.py로 대응 미러를 생성/check한다. 불변이면 공식 check만 연결하며 미러에서 전체 측정을 반복하지 않는다.

evidence/judgment.md에 G5의 충족/정확 남김, 수리와 제외의 이유, G4 재사용 또는 새 확인, 최종판·원근거·G6 인계 경로를 적는다. report.json의 changes는 실제 제품 변경만 적고 `python C:/math/services/async-development/check.py report C:/math/.async/dm g5-full`을 통과시킨다. G6 전체 변이·G7 T4/T5/실경계·G1~G3 최종연결·L01/Windows1314·G8 review는 별도 남김이다. 공용 source/context/plan/seams/queue/state·engine·다른 스킬·기존 연구는 수정하지 않으며 graphify 갱신은 하지 않는다.
