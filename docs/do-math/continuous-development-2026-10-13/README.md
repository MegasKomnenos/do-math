# do-math 연속 개발 실행 준비

> 이 실행은 2026-10-15 async-development로 이관된 역사 기록이다. 현재 상태와 재개 지침은 [새 실행 기록](../../../.async/dm/README.md)을 따른다. phase 배정·report·manager 결론과 이미 추적된 선별 증거는 Git에 보존하고, 그 외 중간 파일·큰 원자료는 로컬 보관한다. 정리 과정에서 과거 보고를 새 성공으로 바꾸지 않았다.

이 디렉터리는 `services/continuous-development`를 사용하는 실제 실행 기록 루트다. 프로젝트 루트는 `C:/math`다. 공용 context·plan·seams와 첫 work phase 001이 준비돼 있다. 설정 준비만 했으며 Codex 개발 세션은 아직 시작하지 않았다.

## 시작

저장소 루트에서 먼저 형식·참조·미사용 phase 여부를 확인한다. 이 명령은 모델을 호출하지 않는다.

```powershell
python docs/do-math/continuous-development-2026-10-13/start.py --check-only
```

개발 실행을 시작하려면 다음 한 명령을 사용한다. 별도 콘솔 창을 띄우지 않고 Python controller를 시작한다. 이 명령부터 실제 Codex 세션과 이후 manager가 선택하는 작업들이 실행된다.

```powershell
& ./docs/do-math/continuous-development-2026-10-13/start.ps1
```

터미널에서 직접 기다리려면 `start.ps1 -Foreground` 또는 `python .../start.py`를 사용한다. 현재 환경과 같은 쓰기 권한 설정(`--sandbox danger-full-access -c 'approval_policy="never"'`)을 각 Codex 호출에 전달한다. 파일 소유 범위는 context/objective/protocol로 제한하며 서비스 자체가 모든 파일 쓰기를 강제 감시하는 것은 아니다. 작업자는 `gpt-6.1-sol/high`, manager는 settings.json의 `gpt-6-astra/xhigh`를 사용한다. 2026-10-14의 기존 실행기 교체 이후 상태는 `runtime/model-change.json`을 확인한다. 원 `launch-001.json`의 종료는 전체 목표 완료를 뜻하지 않는다. 자세한 전환 기록은 [모델 정책](sources/model-policy-2026-10-14.md)에 있다.

처음에는 3개 읽기 전용 task가 병렬로 요구별 상태, 문서 검사기 마감 범위, 최종 관문 준비도를 판단한다. 첫 phase부터 전체 일반/T3/변이를 돌리거나 기존 구현을 다시 쓰지 않는다. 모든 task가 끝나면 새로운 manager 세션이 보고를 검사하고 실제 다음 phase를 작성한다.

## 현재 상태와 결과

- `runtime/launch-001.json`: 실제 controller/runner PID, 시작/관찰/종료 상태. 파일이 running이라고 프로세스가 살아 있다고 단정하지 않는다.
- `runtime/runner-001.log`: 실행기 오류와 종료 진단. 다음 phase도 같은 실행기가 이어 간다.
- `runtime/controller-*.stdout.log`, `controller-*.stderr.log`: 숨긴 controller의 출력과 시작 실패. 백그라운드 시작 전에 확인 모드를 먼저 통과하며, 경합 등 이후 오류도 이 로그에 남는다.
- `phases/<phase>/logs/task-<task>.log`, `manager.log`: 각 Codex 세션의 실제 로그.
- `phases/<phase>/tasks/<task>/report.json`: 실제 작업 결과의 정본.
- `phases/<phase>/manager.json`: 해당 phase의 처분과 다음 배정/완료 결정.
- `context.md`, `plan.md`: 서비스 시작 후 현재 이해와 남김의 정본. 이전 대형 단계-전환표는 기준선/원증거로 보존하며 이중 현재판으로 갱신하지 않는다.

서비스는 report·handoff 검사를 자동 호출하지 않는다. 각 task/manager가 protocol과 objective에 따라 호출한다. manager는 `manager.pending.json`을 검사한 뒤 `manager.json`으로 게시한다. 실행기의 종료 코드 0이나 task의 complete만으로 전체 목표를 완료라고 하지 않는다. 마지막 review phase와 모든 G의 실제 근거를 확인한다.

원래 소스 해시와 요구 ID는 `sources/baseline.json`, `sources/requirements-index.json`에 있다. 이는 현재 파일을 강제 복원하거나 옛 규칙을 부활시키는 자료가 아니다. 바뀐 파일은 task가 실제 현재 원문과 대조한다.

## 중단과 재개

서비스에는 자동 재개가 없다. 같은 phase를 다시 지정하면 이미 수행한 task를 다시 실행하고 로그를 덮을 수 있다. start.py는 실행 흔적과 배타적 시작 기록을 확인하여 이를 거부한다. 기록 파일을 지워 강제로 재시작하지 않는다.

중단했다면 실제 runner와 그 자식 프로세스가 남아 있는지 먼저 확인한다. 짧은 관찰 대기 만료나 로그 침묵은 종료가 아니다. PID 숫자만 보지 말고 생성 시각·명령을 대조한다. 기존 task report와 로그를 읽어 완료/부분/누락을 구분한다.

- manager.json이 게시됐고 next phase가 아직 시작되지 않았다면 그 새 phase를 검사하고 `start.ps1 -Phase <새ID>`로 시작할 수 있다.
- manager가 끝나지 않았다면 완료한 task를 다시 실행하지 않는다. 운영자가 현재 보고와 질문을 확인한 뒤, protocol의 manager bootstrap으로 별도 새 manager 세션을 시작해 기존 phase의 처분을 마감한다. 재호출 로그는 이전 manager.log를 덮지 않는 새 파일에 보존한다. 그 뒤 새 next phase만 시작한다.
- 필수 외부 조건이 없으면 질문과 영향을 남기고 해결을 기다린다. `next:null`이나 가짜 성공 보고로 중단을 표현하지 않는다.

이 설정은 자동 복구기·타이머·추가 스케줄러를 서비스에 덧붙이지 않는다. start.py의 시작 기록은 중복 기동을 막고 실제 관찰을 남기는 용도다. 진행을 강제로 제한하는 시간 예산이나 최대 phase 수는 없다.

## 준비 검증의 범위

서비스의 기존 31개 테스트는 가짜 Codex로 30개 통과·Windows 권한 조건 symlink 1개 건너뜀을 확인했다. 첫 phase와 start.py의 check-only는 별도로 확인한다. 실제 모델 기동/인증/도구 호출 성공을 검증한 것은 아니며, 그 확인은 실행과 G7에 남는다. 서비스 본체는 사용자가 제공한 미추적 파일이며 이번 설정에서 수정하지 않았다.
