# 현재 HOLD·기동 근거 계약의 수리와 실제 예약 T5 연결

목표는 현재 동결 bootstrap/명시 manifest 연쇄가 Windows의 시험 소유 예약에서 발화하고, HOLD를 지킨 채 정상 종료·해제되는지를 실제로 확인하는 것이다. g7-boundary-scope의 재사용 판단은 이미 수용됐다. 이번에는 manager0081가 찾은 낡은 smoke 기대값을 고치고 필요한 실제 예약 한 선택까지 같은 작업에서 마친다. G7 전체·연구 엔진 실운전·다른 공급자/Lean/학술의 재확인은 맡지 않는다.

## 입력과 현재 사실

SESSION_JSON·task.json·inputs/context/plan/seams, 자기 workspace의 AGENTS.md·scripts/tests/시험-지침.md를 읽는다. managers/0081/review.md·verification-review.json·accepted-entry-diff.txt와 tasks/g7-boundary-scope/evidence/judgment.md의 예약 실행안 C를 소비한다. 그 judgment의 'helper 그대로 실행'은 이번 manager의 F1 보정으로 대체한다. 원 권한은 C:/math/docs/do-math/continuous-development-2026-10-13/phases/013/tasks/scheduler-smoke/objective.md의 판단과 경계다. 역사 phase 실행/전수 재검증 절차는 현재 ENGINE/protocol.md와 이번 objective로 대체한다.

실제 선행은 g5-entry-gate와 g7-boundary-scope다. g5-core-gaps·g1-handoff의 진행 중 사본/결과를 읽거나 기다리지 않는다. 현재 held 경로는 core 연구 처리를 시작하기 전에 반환하므로 그 수리는 이번 실제 예약의 선행이 아니다. 동료 배정과 공용 소스/문서/queue/state를 바꾸지 않는다.

manager가 정적으로 확인한 F1: support/scheduler_live.py:run_scheduler_smoke의 `all(r == {'outcome': 'held'} ...)`는 scheduled_operator.execute의 `{**result, 'startup': startup}`와 맞지 않는다. 현재 bootstrap.main은 manifest를 검증하고 원 installation_root/installation_manifest를 scheduled_operator.main→execute에 명시 전달한다. execute는 startup.json을 게시한 뒤 HOLD 결과와 startup을 반환한다. 실제 OS 실패 실행은 아직 없다. 이것은 시험 기대값의 공백이며 제품 반환을 옛 모양으로 되돌리는 요구가 아니다.

## 수행과 필요한 확인

1. 실제 caller·반환·현재 T4/sim의 기동 근거 단언을 읽어 F1을 확인한다. 기존 수용된 실제 child 원출력이나 작은 정적 대조로 실패 원인을 보일 수 있으면 그것을 사용한다. 이미 아는 dict 불일치를 재현하려고 고비용 예약 전체를 먼저 실행하지 않는다. 기존 시험/fixture를 재사용하고 새 범용 validator나 별도 registry를 만들지 않는다.
2. 배정된 helper와 직접 smoke에서 현재 held/startup 계약을 검사하도록 고친다. outcome만 읽어 추가 반환을 무시하는 식으로 단언을 약화하지 않는다. 실제 frozen manifest/원 설치 좌표·snapshot 신원, runtime 위치, 출력과 게시된 startup 근거를 해당 의미와 독립 입력에 연결한다. 실제 시각과 Git 관측의 선택 필드/오류는 현재 정의대로 판단하고 추정 성공값을 채우지 않는다. Git 없는 async snapshot에서 source_status=unavailable은 현 설치 근거의 지원된 관측이며 임의 commit을 만들거나 상위 C:/math를 자기판으로 쓰지 않는다. held·연구/복구 미생성·설치/소유·원출력·정리 단언은 보존한다.
3. 초기 준비는 실제 Windows/PowerShell/Python/pythonw·Task Scheduler/Interactive 로그인·등록/실행/해제 조건을 필요한 범위에서 확인한다. 외부 TEMP/TMP/TMPDIR와 output은 저장소 밖 짧은 자기 경로에 두고 생성될 실제 snapshot/child cwd를 확인한다. 자기 workspace 제품만 실행한다. 현재 환경 부재·권한 오류를 skip/성공/제품 회귀로 바꾸지 않고 원오류와 조건을 기록한다. 권한 상승·계정/서비스 정책 변경·도구 설치는 하지 않는다.
4. 수리한 고정 소스에서 아래 정확한 공식 T5 선택을 --jobs 1로 실행한다. 기존 run_scheduler_smoke의 실제 PS 포트·pythonw freeze/직접 held/OS start·one-shot wake·해제 경로를 사용한다. 새 시작 부재를 확인한 세 이름만 사용하고 ownership.json/requests.json을 변경 전에 보존한다. HOLD는 처음부터 끝까지 유지한다. 원 Task Scheduler status/XML/action·cwd/principal/interval과 실행 전후 ticks/exit0·직접 start 없는 wake 발화·마지막 세 null/자기프로세스0를 구별해 확인한다. OS task의 stdout을 관측한 것처럼 직접 pythonw 출력과 섞지 않는다.

cwd는 자기 workspace/.claude/skills/do-math다. `<OUT>`은 실행 전에 선택해 기록한 새 절대 출력 폴더다.

```powershell
python -u -B scripts/run_tests.py --tier T5 smoke.test_scheduler_live.SchedulerLiveTests.test_held_pythonw_tasks_start_wake_and_uninstall --jobs 1 --output <OUT>
```

전체 T5를 실행하지 않는다. 성공 뒤 이유 없는 반복이나 양쪽 미러 실예약 반복도 하지 않는다. 실패하면 먼저 원자료/코드를 읽고 필요한 수정 뒤 해당 한 선택만 재확인한다. 자동 재시도/새 hard timeout/시간에 의한 성공·실패 판정은 없다. 정상 확인에는 한 번의 실제 실행이면 충분하며 시간은 소프트 기준이다. 실행 중 소스/시험/미러를 편집하지 않는다.

성공·실패 모두 existing finally의 소유 확인과 자기 세 task 정리를 끝낸다. 시작부터 존재한 예약은 덮어쓰지 않는다. cleanup 오류가 남으면 정확 task 이름·action/workspace·마지막 상태·자기 process/PID·오류와 필요한 행동을 최우선 finding으로 반환한다. 기존 연구나 다른 예약을 지우거나 중지하지 않는다. 이 권한은 원 phase013 objective가 명시한 시험 소유 OS task의 생성·발화·취소·해제 권한으로 이미 주어졌다. 새 승인을 기본 단계로 만들지 않는다.

공식 report의 selected/고유 실제 rows/counts/fixture_counts/complete/successful/changed_during_run, 관측 native exit·argv/cwd/필요환경·stdout/stderr·판본 SHA를 남긴다. 자기 smoke 원자료와 ownership/requests·snapshot/manifest·before/after/cleanup을 필요한 범위에서 보존한다. report counts만으로 OS 발화/정리를 인증하지 않는다. 기존 corpus의 의미/원bytes를 유지하며 동일 상태 녹화를 출하 corpus에 또 추가할 필요는 없다. 새 원증거는 task/evidence에 인계한다.

## 쓰기·자원·완료 경계

제품 writes는 정본/공식미러의 scripts/tests/support/scheduler_live.py, scripts/tests/smoke/test_scheduler_live.py, scripts/tests/시험-지침.md다. 현 runtime API는 읽기 전용으로 소비한다. 설명은 실제로 바뀐 계약과 확인 범위만 갱신한다. 공식 build_skill_mirrors.py로 이 변경의 미러만 생성/check하고 자기 정본/미러 변환 근거로 실행 재사용을 판단한다. 캐시 .timings.json 등은 관측 근거를 보존한 뒤 자기 base로 복원해 통합 대상에서 제외한다. 변경 없는 제품 코드를 광범위하게 다시 검사하지 않는다.

runtime 결함이 실제로 드러나면 반례·caller·최소 수정 파일과 필요한 확인을 보고한다. 쓰기 범위를 넘거나 성공을 위해 기대값을 약화하지 않는다. 직접 관련 helper·smoke 수리와 확인은 이 task에서 끝낸다. 전체 G4/T3/T4·변이·유료 호출·Lean/학술 재실행·L01/권한 probe는 추가하지 않는다.

시험 슬롯1, 한 번에 하나만 실행한다. 병행 core의1슬롯과 총2이며 현재 다른 실제 예약/설치 작업·전체 관문은 배정되지 않았다. 공유 OS 자원은 자기 세 task에만 한정한다. 준비/실행 가능성은 실제 확인 결과로 보고하며 원조사의 경로 존재를 성공으로 복사하지 않는다. 사용자 저장범위/A22에 따라 공통 저장·기존 업무 보장을 재사용하고 새 가족별 quota나 감사를 만들지 않는다.

evidence/judgment.md와 report.json에 F1 수리 이유, 실제 확인 범위/미확인, 원실패 또는 정적 반례, 현재 소비판/외부조건, OS 정리와 후속 판단을 남긴다. 수용 가능한 결과가 있어도 실환경 입력 부재로 목표를 마치지 못하면 partial/blocked로 정확히 보고한다. `python C:/math/services/async-development/check.py report C:/math/.async/dm g7-scheduler`를 통과시킨다. 이 배정 complete도 최종 전체 G7/G8 성공은 아니다.
