# do-math 구현

`codex exec`과 기존 Codex 로그인을 사용하는 Windows 실행 어댑터다. 직접 API를 호출하거나 별도 API 키를 요구하지 않는다. 실행기 구현의 기준은 [통합 설계](../../../docs/do-math/통합-설계.md)이고, 전체 구현의 남은 범위는 [구현 진행](../../../docs/do-math/구현-진행.md)에 기록한다.

현재 제공하는 것은 CLI 실행 어댑터, Windows Job 프로세스 소유권, Git 상태 저장, 예산 계산과 구현 검증 도구다. 연구 역할과 인스턴스 운전 명령은 아직 제공하지 않는다. 설계의 `do-math run`을 구현 검증 명령으로 대신하지 않는다.

## 실제 CLI 검증

저장소 루트에서 다음 명령을 실행한다. 모델 호출을 수행하며, 원문 입력·JSONL·표준 오류·최종 응답·사용량·로컬 종료 관찰과 해시를 새 보고 디렉터리에 보존한다. `--output-dir`로 지정한 디렉터리는 새 경로여야 한다.

```powershell
python .claude/skills/do-math/scripts/probe_codex.py --model gpt-5.6-luna --windows-sandbox unelevated --cases text structured tool cancel
```

모델과 노력은 설치된 CLI에서 실제 사용할 값을 지정한다. Windows 샌드박스는 해당 호스트에 설정된 `unelevated` 또는 `elevated` 값을 명시한다. 검증을 위해 사용자 설정 파일을 변경하지 않는다. 샌드박스 설정이나 도구 실행이 실패하면 원인과 미수행 범위를 결과에 남긴다.

| 검사 | 실제 확인하는 것 |
|---|---|
| `text` | 임의 표식이 포함된 입력과 정확한 최종 응답, 완료 사건·종료 코드·로컬 종료 장벽 |
| `structured` | `--output-schema`로 지정한 JSON 구조와 임의 표식의 일치 |
| `tool` | 실제 `command_execution` 사건의 출력과 종료 코드 |
| `cancel` | 실행 중인 turn을 관찰한 뒤 Job 전체 종료와 빈 프로세스 목록 |

프로세스가 끝났다는 사실과 공급자 서버의 처리 상태는 구별한다. CLI에서 회수하지 못한 공급자별 호출 식별자·원격 종료·호출별 사용량은 `unknown`으로 남긴다. `turn.completed`의 사용량은 CLI turn 단위의 관찰값이다. 모델에 실제 전달한 전체 입력과 자동 압축 통제, 모든 파일·네트워크·IPC·비밀 접근 경계는 이 네 검사의 통과로 입증되지 않는다.

반환 JSON의 `passed`는 선택한 검사들의 통과 여부이고 `implementation_complete`는 전체 통합 설계의 완료 여부다. 두 값은 서로 다른 판단이다. 이 도구는 연구를 활성화하지 않는다.

## 원자료 현재성 검사

다음 명령은 모델을 호출하지 않고 설계·벡터 대응·스키마·기존 명세 보고의 바이트 현재성을 검사한다.

```powershell
python .claude/skills/do-math/scripts/probe_codex.py --spec-only
```

`verified`는 검사한 바이트와 대응이 일치한다는 뜻이다. `blocked`는 실제 불일치가 있고, `incomplete`는 필요한 입력을 읽거나 해석하지 못했다는 뜻이다. 의미 계약 동기화와 실행 권한은 별도로 검증해야 한다.

## 실행 어댑터 사용

`CodexExecAdapter.start()`는 새 출력 경로와 고정 입력을 검사하고 루트를 정지 상태로 생성한다. 호출자는 허가와 예약을 공개한 뒤 `resume()`을 호출한다. `inspect()`로 진행 중인 사건을 관찰하고, 중단 시 `stop()`을 호출한다. `collect()`는 루트 종료 신호·Job 활성 프로세스 수 0·빈 프로세스 목록을 모두 확인한 뒤 결과를 회수한다. 종료 장벽 전에는 결과를 확정하지 않는다.

`codex_worker.py`는 어댑터 내부에서만 실행한다. 직접 실행하면 Job 소유권과 시작 전 입력 검사를 거치지 않는다. 요청·입력·작업 공간·출력 경로는 실행기를 구현하는 호출자가 통제한다. 프로세스 Job만으로 그 파일의 접근 권한까지 확보되지는 않는다.

`GitStateStore`는 `research`와 `runtime`을 단일 상태 ref로 공개한다. `publish()`는 이전 머리를 비교해 갱신하고 다른 갱신이 먼저 일어났으면 충돌로 반환한다. 기존 산출 묶음의 수정·삭제를 거부한다. 기록 스키마·권한·의미 검사는 저장소 호출 전에 실행기가 수행해야 한다.

## 로컬 검사

```powershell
python .claude/skills/do-math/scripts/tests/test_windows_job.py
python .claude/skills/do-math/scripts/tests/test_codex_adapter.py
python .claude/skills/do-math/scripts/tests/test_git_store.py
python .claude/skills/do-math/scripts/tests/test_budget.py
python .claude/skills/do-math/scripts/tests/test_preflight.py
python .claude/skills/do-math/scripts/tests/test_probe_codex.py
```

Git 검사는 임시 저장소에서 수행한다. CLI 단위 검사는 시험용 실행 파일을 사용하며, 실제 CLI 검증은 위의 `probe_codex.py`가 수행한다. 명세 검사는 `docs/do-math/통합-설계-명세-v9/README.md`의 절차를 따른다.

스킬 정본과 Codex 사본의 위치·생성 절차는 [멀티런타임 동기화](../writing-skills/references/멀티런타임_동기화.md)를 따른다. Codex 사본을 직접 고치지 않는다.
