# phase 013 scheduler-smoke 경계 검토

현재 `scheduled_operator.schedule` → `real_ports().scheduler` → 기본 `subprocess.run`을 사용하는 `PowerShellScheduler.run` → 실제 `operator_schedule.ps1`을 유지했다. Task Scheduler cmdlet, runner, bootstrap, clock, port 대역은 없다. 새 시험은 `resource` 격리에서 공식 scratch에 새 repository/workspace와 실제 시계의 RI를 만든다. `task_names`의 정확 세 이름을 실제 status로 조회해 모두 부재일 때만 install한다. 생성 전 `ownership.json`·`requests.json`에 좌표, HOLD SHA, 예정 동작과 cleanup 이름을 기록한다. 기존 예약이나 연구를 사용하지 않았다.

## HOLD와 설치

현재 `check`는 첫 `_held` 검사에서, `run_engine`과 `wake`는 `engine_start_guard`의 첫 `_held` 검사에서 held를 반환한다. 상태 조회/연구 Git/ModelRunner 이전이다. `operator_bootstrap.main`은 frozen 위치에서 실제 manifest와 모든 파일을 검증한 뒤 그 패키지의 scheduled_operator를 실행한다. 시험은 공개 `hold`로 시작하고 끝까지 동일 HOLD 바이트를 유지한다. 빈 시험 repository는 끝까지 비어 있고 engine/recovery 디렉터리는 생성되지 않았다.

install에 7200초 interval과 5400초 operator timeout을 명시했다. 현재 Interactive/Limited 사용자 principal, operator PT2H 반복·PT1H35M 실행 제한·IgnoreNew/Hidden, trigger 없는 engine·PT0S 무제한을 실제 OS 객체와 XML에서 확인했다. frozen action·pythonw·인자·WorkingDirectory는 manifest 좌표와 정확히 같다. manifest의 모든 snapshot 파일을 실제 소스와 SHA로 대조했다.

제품 install은 자체 `pythonw --freeze | Out-String`의 비어 있지 않은 JSON과 exit를 검사해 성공한 뒤 등록한다. 내부 파이프 stdout 자체를 관측했다고 주장하지 않는다. 설치된 같은 snapshot에 대한 별도의 실제 pythonw freeze 확인에서 JSON·exit 0·같은 entrypoint/manifest/SHA를 원바이트로 수집했다. 별도로 frozen bootstrap의 check/run-engine/wake를 pythonw에서 직접 실행해 세 정확 `{"outcome":"held"}`와 exit 0을 수집했다. 이 직접 stdout은 OS task stdout과 구별한다.

## 실제 OS 발화와 정리

새 operator와 engine에 실제 start를 요청했다. 각 작업은 요청 전 last_result=267011(미실행), 1999년 LastRunTime에서 새 ticks, Ready, LastTaskResult=0으로 바뀌었다. wake는 약 30초 뒤의 WakeAt과 RI를 포함한 WakeKey로 실제 등록했다. XML의 one-shot StartBoundary·description·live bootstrap action을 대조했고 wake에는 start 요청을 보내지 않았다. OS 시각 트리거 뒤 같은 미실행→새 ticks/Ready/0 전이를 관찰했다. `requests`와 감사 argv가 이 차이를 결속한다.

서비스 LastRunTime은 관찰자의 벽시계보다 앞선 값을 보고했다. live-final의 operator/engine/wake 값은 각 요청 시각과 -33/-40/-15초 차이였다. 원값을 수정하지 않았다. 비교는 같은 작업의 전후 ticks에 두고 요청/관찰 시각과 차이를 함께 보존한다. 이유는 확인하지 않았으며 특정 Windows 결함이나 시계 정책으로 단정하지 않는다. disabled 상태의 TaskScheduler Operational 로그를 활성화하지 않았다. 빠른 pythonw PID가 polling에 잡히지 않은 한계도 기록한다. OS stdout/내부 결과는 만들어 내지 않으며, 실제 종료 0과 검증된 held 진입 경로까지만 주장한다.

성공 경로에서 실제 cancel_wake로 wake를 제거했다. finally에서는 정확 action/workspace 소유를 재조회한 뒤 자기 세 이름만 uninstall한다. 마지막 실제 status 세 null, 자기 workspace를 인자로 가진 pythonw 부재, HOLD 불변, 연구·복구 미생성을 검사한다. 모든 완료/실패 실행의 원자료를 보존했다. live-03의 관찰 대기 중에는 소유 XML/action을 확인한 별도 도구로 자기 작업을 해제했고, 작업 소실을 본 시험이 실패 후 finally 정리를 완료했다. 권한 상승, 계정/서비스/로그 설정 변경, 기존 작업 중지·재등록·해제는 없다.

## 역사와 유지 판단

`history-port.stdout`은 0dd16a5e의 실제 PowerShellScheduler 분리, scheduled_operator 효과 표면과 wiring 연결 diff다. 현재 `ports.scheduler.Scheduler`, `wiring.real_ports`, `scheduled_operator.schedule`, 실제/대역 공유 계약과 호출을 대조했다. 분리와 좁은 JSON 수신/오류/GUI 창 억제 의미를 유지한다. 다른 도메인/Lean/저장 hunk를 이번 검토 완료로 올리지 않는다.

`history-freeze.stdout`은 a0e6c2f4의 실제 `Out-String`, `$LASTEXITCODE`의 null/nonzero 반려, 빈 JSON 반려와 pythonw 시험 추가 diff다. 현재 adapter는 이 성질을 유지하며, 현재 boundary의 성공/실패 freeze 단언을 그대로 실행했다. boundary의 cmdlet 대역 등록 검사는 유지하고 새 T5가 실제 등록·발화를 더했다. 원문 `진행.md`의 1c (마) 기록과 M-0373은 역사 설명이며 원 raw report가 아니다. 해당 두 commit의 raw 원보고 위치를 이 입력/기록에서 확인하지 못했으므로 당시 counts를 새 성공에 합산하지 않는다. 두 hash는 단계-전환표의 직접 문자열 필드에서도 발견되지 않았다(`history-index.json`). 보고서가 존재하지 않는다고 전체 저장소에 대해 단정하지 않는다.

설계 3.3의 corpus 일반 검사, 4.5 원녹화, 5.1 T5/soft 시간 의미, 8의 status(T4)와 등록/시작/취소/해제(T5) 분리 및 결함 범주 9-C를 적용했다. 기존 A-32(trigger 없는 조회), B-01(pythonw 출력), 010 승인 host 성질을 보존한다. 새로운 등록/발화 요구를 status 성공이나 과거 counts로 대신하지 않았다.

## corpus·미러·검증 범위

실제 등록 상태와 uninstall 뒤 부재 상태의 추가 status stdout/stderr를 자르거나 재직렬화하지 않고 두 항목으로 복사했다. 정확 argv/cwd·판본·시각·exit·이름·원 SHA·녹화 때 파싱값은 provenance/manifest에 연결한다. `scheduler_json` reader는 변경하지 않았고 현재 PowerShellScheduler의 JSON 수신으로 전건을 재생했다. OS XML/발화/PID 보조자료·직접 freeze/held stdout은 출하 corpus에 넣지 않았다.

기존 19항목/verdict와 양쪽 비manifest 110경로의 바이트를 유지했다. 새 양쪽 21항목/62파일, 모든 명시 SHA·파일 선언·5MiB 상한·Git raw/clean·양쪽 생성 바이트를 대조한다. 생성 계획 11경로가 writes 안임을 먼저 확인했고 공식 생성기는 8개 생성/3개 갱신을 수행했다. 미러 실행 뒤 비용 캐시 한 경로만 공식 재동기화했으며 --check 1322파일과 skill-only가 통과했다.

최종 정본/미러에서 스모크와 지정 9모듈의 같은 33고유 시험이 모두 passed/exit 0이다. 선택/실제 row와 각 871 Python SHA, 실행 중 변경 부재/현재 판본을 대조한다. 초기 live-01은 Windows 감사 argv 문자열을 목록으로 읽은 보조 코드 오류, live-02는 XML이 기본 RunLevel을 생략하는데 요소 존재를 요구한 보조 코드 오류, live-03은 두 시계를 같은 시계로 가정한 대기 중 명시 정리 후 실패다. 이 세 원보고를 소급 성공으로 고치지 않는다. 관련 최종 실행은 corpus/지침이 추가된 현 판본의 freeze를 검증한 새 성공이다.

runtime 124개·공급자 입력 3개·host 입력 4개·Lean 시험/helper 4개와 host 원자료 8개, Python/pythonw/PowerShell·Lean/Lake 실행 파일 조건을 대조해 기존 승인된 성질만 재사용한다. 기존 PowerShell 역사 binary SHA 부재 한계는 유지한다. 유료 모델, Lean, 기존 host T5를 새로 호출하지 않았다. 전체 일반 검사, fresh T3, 전체 함수 변이, 학술·T4 별도 분기 보고·읽기 조건·최종 G7/G8 review와 Git 마감은 후속 manager 책임이다. graphify 갱신과 Git stage/commit/reset/checkout/push는 없다.
