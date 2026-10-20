# 현재 통합판의 남은 경계 입력 연결, 전체 일반 검사와 fresh 전체 T3

g7-t4r가 수용된 뒤 그 제품·시험·설명 수리까지 반영한 판본에서 G4와 G5를 이어서 확인한다. 두 관문의 공통 준비·같은 파일 수리·미러·인계를 한 task로 묶는다. 선행 g7-t4r는 실제 소비판과 공유 전체관문 자원을 위한 것이며 역사 review 전체나 G1~G3 완료를 기다리는 장벽이 아니다. 선행이 partial이면 보고된 정확한 남김을 먼저 읽고, 알려진 관련 제품 결함을 방치한 전체 반복은 하지 않는다. T4의 별도 외부 조건만 남았으면 이 task의 독립 검사를 진행한다.

SESSION_JSON/task.json/inputs 세 문서, 자기 workspace의 do-math AGENTS.md와 시험-지침.md, manager0089·0090의 판단과 선행 report/integration을 읽는다. g4-final/objective.md와 g5-full/objective.md는 측정 계약·준비의 참고이며 아래 현재 배정이 우선한다. 과거 선택 수4288이나 부분수리의 합을 현재 기대값으로 쓰지 않는다. 저장범위 지시와 설계3.3/A22·5.3/5.5를 적용하고 가족별 모든필드/새reader/옛head 시나리오를 다시 요구하지 않는다.

## manager0094 보완: 알려진 세 경계 입력을 먼저 연결한다

이 task는 아직 시작하지 않았으며 manager0094가 g7-t4r의 여섯 파일을 부분 수용했다. 최종 전체 T4의 원결과는 304선택/301passed·1error·2skipped/exit1이다. 실제 독립 Git fixture와 startup 기대값 수리의 9행은 통과했다. 남은 세 입력 문제는 현재 접근 가능한 자료로 준비할 수 있어 이 task의 기존 준비에 묶는다. manager0094/review.md·verification-review.json과 선행 evidence/judgment.md를 먼저 읽는다. 기존 전체 일반/fresh T3와 G6 입력 목표는 유지한다.

1. `boundary.test_knowledge_lean_verifier.LakeEnvironmentTests.test_lake_search_paths_are_observed_once_per_unchanged_project_input`는 workspace 기본 toolchain 경로를 직접 사용해 WinError2였다. 실제 설치 입력은 `C:/math/.skill-workspace/do-math-toolchains/lean-4.32.0/lean-4.32.0-windows/bin/lean.exe`와 같은 디렉터리의 `lake.exe`다. manager는 존재·크기·SHA만 확인했다. 기존 `support.provider_inputs.actual_command()`의 명시 compiler 입력과 실제 같은 설치의 Lake를 연결하는 가장 작은 시험 입력 수리·설명·공식 미러를 함께 마친다. 별도 Lake 입력이 더 적절하면 실제 현재 소비 계약을 설명한다. real Job/프로젝트/검색경로·불변 입력 관측1회/변경 뒤2회·toolchain 신원 단언을 유지한다. 제품 runtime의 기본 경로에 공용 저장소 fallback을 추가하거나 설치·다운로드·신뢰 승인으로 해결하지 않는다. Mathlib 전체 준비를 compiler/Lake 존재로 주장하지 않는다.
2. `SHARED_INPUT_BASELINE_SCRIPTS`는 `C:/math/docs/do-math/continuous-development-2026-10-13/phases/016/tasks/provenance-baseline/evidence/pre-provenance/scripts`로 명시한다. 같은 evidence의 review.md·baseline-manifest.json이 도입bbe64043f49d46fb7c3b6e768b99a8acbaa125cf의 첫 부모010b059700115f6d5d3df1bf24e931cf78eaa44a와 보존910파일을 연결한다. manager는 실제 첫 부모와 필수7파일 SHA를 확인했다. 기존 준비 근거를 재사용하며 구판 선정/전수 추출 감사를 처음부터 반복하지 않는다. 원자료는 읽기 전용이고 PYTHONDONTWRITEBYTECODE를 자식에도 유지한다. 과거 입력을 바꾸거나 현재판을 섞지 않는다.
3. Git/외부TEMP 준비 뒤, 아래 세 정확 ID만 공식 runner `--tier T4 --jobs 1`에 반복 `--match <정확 ID>`로 전달해 확인한다. Lake 입력 수리와 두 기존 비교가 실제 작동하는지 해소할 최소 범위다. 원 report/선택3↔실제행·exit·소스 SHA·실제 입력 신원을 보존한다. provenance의 기존 snapshot/coverage/entered/opened 등 raw는 기존 helper와 phase016 인계에 따라 teardown 전에 보존할 수 있는 최소 방식으로 남긴다. 다른 전체 T4와 미러 T4를 자동 반복하지 않는다.

   - `boundary.test_knowledge_lean_verifier.LakeEnvironmentTests.test_lake_search_paths_are_observed_once_per_unchanged_project_input`
   - `boundary.test_shared_input_provenance.SharedInputProvenanceTests.test_exact_baseline_literal_entries_opens_and_coverage_with_explicit_marker_differences`
   - `boundary.test_shared_input_provenance.SharedInputProvenanceTests.test_exact_baseline_two_worker_raw_union`

관련 소수 수리는 같은 task에서 가장 작은 선택으로 확인한다. 실제 외부 조건만 남으면 정확한 원인·요구 입력을 기록하고 독립 G4/G5는 진행한다. 큰 제품 결함으로 G4/G5도 무효가 될 경우 알려진 실패판의 전체 반복 대신 원인과 최소 다음 범위를 보고한다. 기존301passed 재사용과 새 세 선택은 별도 증거로 유지하며 g7-t4r 전체 보고의 successful=false를 뒤집거나 서로 다른 판본을 한 전체 성공으로 합산하지 않는다. 이 세 입력 확인은 G7 전체 인증이 아니다.

## 준비와 공식 전체 선택

자기 workspace 루트에만 독립 .git과 실제 사본 소스의 로컬 기준 commit을 준비할 수 있다. g4-final 또는 g5-core-recover의 evidence/prepare.py를 자기 task/짧은 외부 경로에 맞춘다. baseline.json/objects/inputs는 불변이며 새 task에는 base 디렉터리가 없다. 예전 prepare.py는 자기 새 ID와 경로에 맞춰 읽고 사용한다. 실제 시작 파일이 필요할 때만 `python C:/math/services/async-development/workspaces.py restore C:/math/.async/dm g45-final baseline <새 별도 디렉터리> <필요 상대경로 ...>`로 복원한다. 과거 결과 파일도 TASK와 baseline|result를 지정해 필요한 부분만 복원하고 이미 정리된 workspace/base를 영구 입력으로 사용하지 않는다. 빈 template/hooks·local 설정·info/attributes의 filter/text/ident 비활성화·NUL pathspec으로 실제 바이트를 기록하고 생성 cache는 제외한다. 전후 bytes와 commit blob/root/HEAD, 비밀 아닌 명령/환경을 남긴다. 기존 .git은 소유를 확인하며 재초기화하지 않는다. 기존 GIT_CEILING_DIRECTORIES를 보존하고 자기 부모/외부 임시root를 추가한다. 공용Git/index/commit·다른 .git 복사·전역설정·remote/push·가짜 HEAD는 하지 않는다.

이 task가 공유 전체관문 슬롯을 단독 사용하며 jobs3·한 번에 한 명령이다. 병행하는 읽기 review는 슬롯0이다. 현재 일반 jobs 종료 뒤 resource 클래스를 격리하는 배선에서 내부 meta jobs2가 겹치지 않는다는 전제를 코드로 확인한다. 배선이 달라졌으면 총시험worker3 이하로 jobs를 낮춘다. 출력/store/TEMP/TMP/TMPDIR는 저장소 밖 짧고 고유한 자기 경로에 둔다. 소스·시험·문서·미러를 실행 중 바꾸지 않는다.

1. 현재 판본을 고정해 workspace 루트에서 `python -u -B .claude/skills/do-math/scripts/run_tests.py --jobs 3 --output <새 일반 출력 경로>`를 실행한다. 위치 인자·--match·--tier 없이 기본 전체를 사용한다. 관련 실제 실패는 원자료/현재 계약으로 판단하고 소수 수리·최소 확인·설명/미러를 같은 task에서 마친다. 수리했으면 최종 고정판의 전체 일반을 완결한다. 큰 독립 수리가 남으면 정확한 원인·소유를 partial로 넘기고 알려진 실패판을 반복하지 않는다.
2. 일반 결과가 기능상 정리되면 `python -u -B .claude/skills/do-math/scripts/run_tests.py --tier T3 --full --jobs 3 --t3-store <새 빈 외부 store> --output <새 T3 출력 경로>`를 실행한다. 위치/--match/다른tier/--mutation-base 없이 fresh 전체를 사용한다. 현재 전체gap과 실제 함수 진입·선택 색인을 얻는 것이 목적이다. 과거 원arc 좌표나 부분측정을 합산하지 않는다. 알려진 환경6arc/10행은 그대로 남을 수 있으며 임의 제외·층/분모/임계값 완화·환경 가짜 입력으로 닫지 않는다.
3. 기능 실패·측정자료 부재·실제 미도달을 구별한다. 작은 관련 공백은 실제 생산/호출 계약과 기존 가장 싼 시험에서 해결하고 필요한 최소 선택으로 확인한다. 충분한 정적 불변식은 재사용하고 새시험 수를 quota로 만들지 않는다. 수리 뒤 최종판의 fresh 전체 T3가 필요하다. 여러 독립 영역이나 외부 조건만 남으면 원측정/최종소스/정확 좌표·원인·필요입력을 보존해 partial로 보고하고 같은 전제의 전체를 반복하지 않는다.
4. T3 중 소스를 바꿨고 최종 G5가 충족된 경우, 그 최종판이 G4 판과 다르면 기본 전체 일반도 같은 task에서 한 번 마친다. G5 미충족 중간판에 G4를 계속 반복하지 않는다. 불변판의 기존 전체 결과는 재사용한다. 시간 경과는 종료·skip·선택축소·변이포착의 근거가 아니다.

writes는 위 관문에서 발견한 직접 결함의 수리를 허용하는 do-math 정본/미러 범위다. 새 skip·단언 약화·제품 내부 대역·근거 없는 no-cover·구판 호환·무관 최적화·새 검증 framework는 하지 않는다. 실제 제외는 원설계5.5와 같은 행의 이유·현재 caller로 검토한다. 공식 build_skill_mirrors.py로 대응 미러를 생성/check한다. 생성기·다른 스킬·서비스는 수정하지 않는다.

## 증거와 완료 판단

각 원 command/cwd/필요환경/시각/관측exit·stdout/stderr/report, 고정 source_sha256과 최종 bytes를 보존한다. selected↔고유 actual rows, counts/fixture_counts·subTest·complete/successful·changed_during_run을 대조한다. G4의 skip/expected_failure는 정확 ID와 원문상 정당성을 별도로 판단하고 passed로 세지 않는다. Windows1314 조건부skip는 실제 outside_symlink 반려의 실행 인증이 아니다.

G5의 closing_eligible은 전체·불변·자료부재없음·재사용0의 자격이며 branch gate 성공과 다르다. measurement_missing=[], store 재사용0, closing_eligible=true, branch_gate.passed=true와 기능 결과·실제 대상/제외 판정이 함께 있어야 G5를 충족한다. 함수진입/selection index/store·원coverage/worker 자료는 실제 생성된 경로와 SHA로 보존한다. T4 자료를 합치거나 색인을 수동 보정하지 않는다. 최종 stable fresh 측정과 색인이 있으면 관문의 미충족 이유와 별도로 G6가 소비 가능한 판본/함수 모집단 입력인지 명시한다.

생성 cache/timing/selection index는 필요한 원자료를 task evidence/자기 외부 경로에 보존한 뒤 baseline.json과 objects의 시작 bytes/부재로 복원한다. 시작 목록에 없던 생성 파일은 자기 쓰기 범위에서 제거한다. 서로 다른 판의 부분성공을 한 전체로 합치지 않는다. evidence/judgment.md에는 세 경계 입력의 직접 결과와 G4/G5 각각의 충족 여부·수리 이유·최종판·원증거·남김·G6 입력을 적고 report.json을 작성한다. `python C:/math/services/async-development/check.py report C:/math/.async/dm g45-final`을 통과시킨다. 제품 무변경은 changes=[]다. G6 실행·위 세 선택 밖의 무관한 T4/T5 반복·실모델/예약/설치·공용 문서/queue/state·graphify는 이 task에서 하지 않는다. G1~G3의 최종 연결·남은 G7 외부조건·G8은 별도로 유지한다.
