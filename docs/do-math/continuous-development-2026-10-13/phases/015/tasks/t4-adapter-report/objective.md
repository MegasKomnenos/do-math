## 목적과 역할

G7과 설계5.5의 T4 adapter 분기 보고를 완결한다. 현재 run_tests.main은 T3에만 Measurement를 생성하며 resource/lean 클래스의 _isolated에는 measure가 전달되지 않는다. T4의 실제 경계 시험이 성공해도 adapter 도달 보고는 없다. 기존 공식 runner·coverage 자료 처리·Job 격리를 재사용해 T4 단독 선택에서 실제 측정/보고를 만들고, 자료 누락을 드러내는 시험과 실제 T4 전건을 연결한다. 새 제품 동작이나 도달률 관문을 만드는 작업이 아니다.

## 완료 조건

### A1 현재 경로와 실패를 확정

014 manager source-inspected와 시작 판본을 대조한다. 설계5.1/5.5/8, gate-readiness의 T4 남김, 현재 TIERS·LAYERS·main/_isolated/_worker와 Measurement의 start/save/merge/finish를 읽고 무엇이 측정되지 않는지 실제 실행으로 재현한다. 작은 기존 boundary 선택에 --tier T4를 주어 시험 성공과 adapter 보고 부재를 구별하거나, 그 실제 경로를 소비하는 새 회귀의 red를 보존한다. 기대값은 LAYERS adapter 분류·현재 coverage 분석과 지정 시험이 실행한 분기에서 얻고 보고의 구현값을 그대로 복제하지 않는다.

관련 과거 runner/Measurement 도입은 git log로 이 변경에 필요한 slice만 좁혀 actual diff·현재 소비자·존재 원보고를 대조한다.002 정상 기준 수리와 기존 T3/D5/D6/D9/D11 의미를 유지하며 없는 역사 counts를 새 성공에 합산하지 않는다. 새 의미 문제는 해당 원문 G와 구체적 반례로 반환한다.

### A2 공식 T4의 실제 측정과 별도 보고

--tier T4 단독 실행에서 선택된 boundary의 인프로세스·lean/resource 격리 worker를 실제로 측정하고 부모가 해당 실행의 자료를 합친다. 현재 LAYERS에서 adapter로 분류한 파일 전부(현재5개)를 열거하고 파일/소스 판본·실행/미실행 분기·누락/제외 및 합계를 추적 가능하게 보고한다. 도달0인 파일도 사라지지 않는다. coverage의 실제 분석과 사유 있는 제외 계약을 사용하며 source에서 분모를 얻는다. 제품의 임의 외부 자식/PowerShell/Lean 내부까지 Python 측정됐다고 보고하지 않는다.

분기 도달률은 정보 보고이며 임계값이나 새로운 G로 만들지 않는다. 시험 성공·skip/fail/error/not_run과 측정의 완전성을 구별한다. 필요한 worker 자료의 부재·파손·다른 실행/판본 자료를 정상 측정 또는 도달0으로 숨기지 않고 불완전 사유와 원경로를 남긴다. 자료가 불완전한 실행을 완전한 T4 보고로 승인할 수 없게 한다. 실제 시험 실패와 runner exit의 기존 의미도 유지한다.

측정은 시험의 실제 실행을 관찰해야 한다. 부모의 보고 직렬화나 자체 파일 읽기를 시험이 실행한 분기로 세지 않는다. worker 자료는 자기 새 출력 폴더에 두고 Job/실제 종료·오류 보존·시간 자동 종료 없음의 계약을 유지한다. 새 옵션이나 중복 측정기를 늘리기 전에 기존 작은 정의를 재사용한다. 필요하면 허용된 adapter_coverage.py에 T4 전용 보고 정의를 두고 생산자와 소비자 시험이 같은 정본을 쓰게 한다.

T4 단독은 T3 gate·선택 색인·증분 저장소·pseudo_tested/변이 결과를 갱신하지 않는다. T3의 1/2/3층 gate 및 fresh 선택을 바꾸지 않는다. 여러 tier 합집합에서 T4 자료가 T3 분모/선택 색인에 섞이지 않는 동작을 명시하고 회귀로 확인한다. 기본 전체 일반 선택과 위치 인자/교집합·모르는 ID/빈 선택 반려·부분 T3 색인 보호도 유지한다. 새 보고 key/파일의 구체 형식은 구현 재량이며 실제 코드와 지침·검사가 정본이다.

### A3 실제 worker 반례와 관련 회귀

기존 공식 runner를 거치는 작은 실제 child/격리 표본으로 측정이 worker의 알려진 분기를 포함하는지 확인한다. T4 측정 부재 red와 교정 green을 보존한다. 자료 누락/파손 또는 판본 불일치에서 완전 보고가 나오지 않는 음성 사례, 미도달 파일 포함, 보고 작업에 의한 거짓 도달 방지, 시험 실패/건너뜀·실행 누락을 가리지 않는 결과를 검증한다. 대역이 필요하면 외부 실패 주입에 한정하고 실제 측정·병합·보고를 대역으로 가리지 않는다.

공식 runner로 unit.test_runner_tiers, unit.test_runner_regressions, unit.test_branch_gate와 새 unit.test_adapter_coverage(만들었을 때)를 실행한다. 관련 T3 store/index/정상 기준 회귀는 이 모듈의 기존 선택을 재사용하며 변경이 직접 영향을 주는 정확 ID만 추가한다. 전체 T3/변이를 회귀 대신 실행하지 않는다. jobs1 및 작은 jobs2 경로를 실제 지원 범위에 맞춰 확인하되 전체 동시 worker3 이하·한 묶음씩 지킨다. 제품 do_math와 기존 boundary 시험은 이번 writes 밖이므로 외부 결함이면 원자료와 후속 범위를 반환하고 억지 기대값 수리는 하지 않는다.

### A4 T4 전건·미러·인도 근거

교정 뒤 정본과 공식 미러 각각 --tier T4 --jobs 1의 전체 기본 boundary 선택을 완결한다. --list 모집단, 실행 선택/고유row/실제exit, 정상/오류/skip/not_run과 실행 전후 소스, 측정 worker 목록과 보고된 adapter 모집단을 대조한다. 원자료와 실제 보고 파일을 자기 evidence에 보존한다. 환경 때문에 실행할 수 없는 항목은 정확 조건을 밝히고 해당 A를 통과로 만들지 않는다. 필요한 수리 없이 이미 성공한 전건을 반복하지 않는다.

지침에 T4 측정 범위·격리/병합·미도달/불완전 해석·T3와의 구분을 적는다. 공식 미러 생성의 사전 변경 범위를 writes에 맞추고 생성한다. 양쪽 지정 runner/branch 회귀와 T4를 확인한 뒤 마지막 비용 캐시만 동기화하고 --check/skill-only를 통과한다. 기존 runtime/공급자·host·Lean·예약·학술 입력/녹화 바이트의 보존을 확인해 승인된 실제 호출의 재사용 범위를 명시한다. runner 변경은 최종 G4/G5 실행 판본과 증분 T3 무효화 판단에 영향을 준다는 점을 기록한다. 최종 일반/fresh T3/전체 변이·문서/의미 질문·L01·최종 review는 후속 manager 책임이다.

## 판단과 경계

phase.json의 runner·측정/보고 지원 정의·정확 회귀 파일·시험 지침·비용 캐시와 대응 미러만 수정한다. do_math runtime/layers·기존 boundary/smoke·corpus·설정/설치·engine·공용 문서·원보고는 고치지 않는다. 정본 문서의 요구를 낮추거나 adapter 도달률을 관문으로 바꾸지 않는다. 기존 도구/실제 포트/Job 및 T4의 읽기 status·시험 전용 임시 자원은 사용한다. 새 유료 모델/학술 검색·실예약 변경·기존 연구 재개·권한 상승·Git stage/commit/reset/checkout/push·graphify 갱신은 하지 않는다. 원문과 구현의 차이가 쓰기 범위를 넘으면 최소 반례·정확 파일·필요 조치를 보고하고 독립 가능한 나머지는 완결한다.

## 검증 방법

cwd C:\math, Python C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe. 모든 시험은 공식 정본/미러 run_tests.py에 -u -B와 정확 ID 또는 --tier T4, --jobs 1, --output <자기 evidence의 새 폴더>를 사용한다. 작은 병렬 확인은 --jobs 2이며 전체 worker3 이하다. 한 검사 묶음씩 실행하고 실행 중 제품/시험 트리를 고정한다. 실제 command/PID/시작/종료/exit·선택/row·원로그와 소스 SHA를 보존한다. 대기 도구의 yield는 실행 실패가 아니다. 진행 result.json은 기존 read_bytes_shared로 읽는다. 시간은 소프트 기준이며 timeout/재시도/측정 누락을 성공으로 바꾸지 않는다.

마지막 Python -B services/continuous-development/check.py report C:\math C:\math\docs\do-math\continuous-development-2026-10-13 015 t4-adapter-report를 통과하고 report 경로와 상태를 반환한다.
