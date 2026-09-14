# do-math 구현

`codex exec`과 기존 Codex 로그인을 사용하는 Windows 수학 연구 실행기다. 후보 준비, 계약 검토, 작업 선택·수행, Lean 검사, 독립 검토, 목표 감사와 다음 연구를 연결하고 입력·결과·상태를 Git에 보존한다. 별도 OpenAI API 키를 요구하지 않는다.

구현 판단은 [통합 설계 0절의 위임](../../../docs/do-math/통합-설계.md#implementation-judgment)을 따른다. 현재 운전과 기록의 계약은 [CLI 실행 계약](references/CLI-실행-계약.md)이며, `do-math-cli/1` 기록을 과거 `do-math-draft/*/9` 명세 기록과 섞지 않는다. [구현 진행](../../../docs/do-math/구현-진행.md)은 실제 검증 범위를 기록한다.

## 연구 인스턴스 실행

Python 3.12, Git, 로그인한 Codex CLI와 `requirements.txt`의 Python 의존성이 필요하다. 이 호스트에는 Codex Windows backend와 portable Lean 4.32.0을 설치해 검증했다. Lean은 PATH에서 찾고, 없으면 이 저장소 `.skill-workspace/do-math-toolchains/lean-4.32.0/lean-4.32.0-windows/bin/lean.exe`를 사용한다. 다른 설치는 설정의 `lean_command`에 argv 배열로 지정한다. Lean을 찾지 못하면 형식 결과를 인증하지 않고 원인을 보존한다.

저장소 루트에서 새 연구 저장소와 작업 공간을 지정한다. 아래 예제는 작은 정리 하나의 전체 흐름을 실행한다.

```powershell
python .agents/skills/do-math/scripts/do_math.py init --create-repository --repository .skill-workspace/my-math/repo --workspace .skill-workspace/my-math/work --goal-file .agents/skills/do-math/examples/nat-add-zero.txt --model gpt-5.6-luna --effort low
```

반환된 `instance_id`를 다음 명령의 `RI-...` 자리에 넣는다.

```powershell
python .agents/skills/do-math/scripts/do_math.py run --repository .skill-workspace/my-math/repo --instance RI-...
python .agents/skills/do-math/scripts/do_math.py status --repository .skill-workspace/my-math/repo --instance RI-... --json
python .agents/skills/do-math/scripts/do_math.py check --repository .skill-workspace/my-math/repo --instance RI-...
```

`run --max-steps 1`은 한 단계만 진행하고 상태를 보존한다. 제한 없이 호출해도 인스턴스의 실행 횟수·시간·회차 한도 안에서만 진행한다. 종료된 같은 프로세스를 되살리지 않고 다음 실행에 저장된 결과와 남은 일을 제공한다. 비형식 조사나 설명 작성이 목표라면 `init --goal-kind research`를 사용한다. 그 완료는 수학적 해결과 구별한다.

| 명령 | 효과 |
|---|---|
| `pause`, `resume`, `close` | 정지·재개·종결 요청을 기록한다. 실행 중 pause는 현재 Job의 정지를 요청한다. resume 뒤 run으로 진행한다 |
| `input --text ...` 또는 `--file ...` | 사용자 원문을 보존하고 의도 해석과 다음 준비에 전달한다 |
| `configure --config-file ...` | 명시한 모델·예산·시간·검토 구성을 변경한다. 과거 사용량과 판정을 지우지 않는다 |
| `request --role ... --target ... --reason ...` | 준비·계획·보충 조사·운영 점검·유지보수 활동을 요청한다. 요청 자체는 모델을 호출하지 않는다 |
| `query --kind knowledge` | 고정 snapshot의 기록을 조회한다. `--related-to`와 `--direction`으로 관계 방향을 선택한다 |
| `read --id ...` 또는 `--path ...` | 정확한 기록 또는 보존한 파일을 회수한다 |
| `export --destination ... --all` | 비어 있는 새 대상에 연구·실행 기록과 산출물을 회수한다 |
| `profile` | 설치된 CLI 명령 표면과 미확인 능력을 보고한다 |

`profile`을 제외한 위 명령에도 `--repository`와 `--instance`를 붙인다. 상세 인자는 각 명령의 `--help`에 있다. 보충 조사는 검토된 ready 과제 ID를, 운영 점검은 기존 실행 ID를 대상으로 한다. paused 상태의 활동 요청은 재개 전까지 실행하지 않는다.

`init --config-file`과 `configure --config-file`은 같은 설정 키를 쓴다. 예를 들어 아래 파일은 작업·운영 실행 시도 횟수와 호출 시간을 정한다. 실패·중단된 시도도 횟수에 포함하며, 이 값은 공급자 내부의 개별 모델 호출 수와 다르다.

```json
{"work_calls": 40, "operations_calls": 30, "call_timeout_seconds": 600, "run_timeout_seconds": 7200, "max_cycles": 5, "reviewers": 2, "goal_auditors": 2}
```

`role_models`로 역할별 모델을 선택할 수 있다. 모델 사용 가능 여부는 실제 CLI 응답으로 확인한다. `reviewers`는 새 수학 제안의 독립 검토 수, `goal_auditors`는 새 목표 감사 묶음의 판정 수다. 기존 제안은 생성 시점에 고정한 검토 수를 유지한다.

## 실제 CLI 검증

저장소 루트에서 다음 명령을 실행한다. 모델 호출을 수행하며, 원문 입력·JSONL·표준 오류·최종 응답·사용량·로컬 종료 관찰과 해시를 새 보고 디렉터리에 보존한다. `--output-dir`로 지정한 디렉터리는 새 경로여야 한다.

```powershell
python .agents/skills/do-math/scripts/probe_codex.py --model gpt-5.6-luna --windows-sandbox elevated --cases text structured tool cancel
```

모델과 노력은 설치된 CLI에서 실제 사용할 값을 지정한다. Windows 샌드박스는 해당 호스트에 설정된 `unelevated` 또는 `elevated` 값을 명시한다. 검증을 위해 사용자 설정 파일을 변경하지 않는다. 샌드박스 설정이나 도구 실행이 실패하면 원인과 미수행 범위를 결과에 남긴다.

이 호스트에는 사용자 승인으로 `elevated` backend를 설정했다. 단일 프로필의 허용 읽기·쓰기와 금지 접근은 확인했지만, 서로 다른 프로필을 순차·동시에 적용하면 공유 그룹 ACL이 남거나 교체되어 읽기 범위가 섞였다. 명시적 `deny`도 동시 실행의 독립성을 제공하지 못했다. 따라서 이 backend를 실행별 비공개 입력의 동시 격리 근거로 사용하지 않는다. 실제 원문과 결과는 [구현 진행](../../../docs/do-math/구현-진행.md)에서 확인한다.

| 검사 | 실제 확인하는 것 |
|---|---|
| `text` | 임의 표식이 포함된 입력과 정확한 최종 응답, 완료 사건·종료 코드·로컬 종료 장벽 |
| `structured` | `--output-schema`로 지정한 JSON 구조와 임의 표식의 일치 |
| `tool` | 실제 `command_execution` 사건의 출력과 종료 코드 |
| `cancel` | 실행 중인 turn을 관찰한 뒤 Job 전체 종료와 빈 프로세스 목록 |

프로세스가 끝났다는 사실과 공급자 서버의 처리 상태는 구별한다. CLI에서 회수하지 못한 공급자별 호출 식별자·원격 종료·호출별 사용량은 `unknown`으로 남긴다. `turn.completed`의 사용량은 CLI turn 단위의 관찰값이다. 모델에 실제 전달한 전체 입력과 자동 압축 통제, 모든 파일·네트워크·IPC·비밀 접근 경계는 이 네 검사의 통과로 입증되지 않는다.

반환 JSON의 `passed`는 선택한 검사들의 통과 여부이고 `implementation_complete`는 전체 통합 설계의 완료 여부다. 두 값은 서로 다른 판단이다. 이 도구는 연구를 활성화하지 않는다.

native 프로필의 읽기 격리는 모델 호출 없이 별도로 재현한다. 새 검사 디렉터리의 ACL을 설정하며 기존 디렉터리는 사용하지 않는다.

```powershell
python .agents/skills/do-math/scripts/probe_native_isolation.py
```

현재 호스트에서는 프로필 간 읽기 격리 결함을 재현해 exit 1을 반환한다. 이는 진단 도구가 발견한 backend의 불통과이며, 검사 프로그램이 실행되지 않은 경우와 보고에서 구별한다. 순차 결과만으로 동시 격리를 승인하지 않는다.

## 원자료 현재성 검사

다음 명령은 모델을 호출하지 않고 설계·벡터 대응·스키마·기존 명세 보고의 바이트 현재성을 검사한다.

```powershell
python .agents/skills/do-math/scripts/probe_codex.py --spec-only
```

`verified`는 검사한 바이트와 대응이 일치한다는 뜻이다. `blocked`는 실제 불일치가 있고, `incomplete`는 필요한 입력을 읽거나 해석하지 못했다는 뜻이다. 의미 계약 동기화와 실행 권한은 별도로 검증해야 한다.

## 실행 어댑터 사용

`CodexExecAdapter.start()`는 새 출력 경로와 고정 입력을 검사하고 루트를 정지 상태로 생성한다. 호출자는 허가와 예약을 공개한 뒤 `resume()`을 호출한다. `inspect()`로 진행 중인 사건을 관찰하고, 중단 시 `stop()`을 호출한다. `collect()`는 루트 종료 신호·Job 활성 프로세스 수 0·빈 프로세스 목록을 모두 확인한 뒤 결과를 회수한다. 종료 장벽 전에는 결과를 확정하지 않는다.

`codex_worker.py`는 어댑터 내부에서만 실행한다. 직접 실행하면 Job 소유권과 시작 전 입력 검사를 거치지 않는다. 요청·입력·작업 공간·출력 경로는 실행기를 구현하는 호출자가 통제한다. 프로세스 Job만으로 그 파일의 접근 권한까지 확보되지는 않는다.

worker 요청은 `sandbox` 또는 `filesystem` 중 하나를 가진다. `filesystem`은 `read_roots`, `write_roots`, `deny_roots`의 절대 경로 목록이며 `windows_sandbox="elevated"`를 요구한다. 쓰기 루트는 모델 작업 공간 안에 두고 고정 입력·출력·상태 파일을 포함할 수 없다. 이 필드는 CLI의 명시적 프로필 구성을 생성한다. 그 구성을 검증된 읽기 격리로 표시하지 않는다. 현재 `describe().verified`의 범위도 `cli_command_surface_only`이며 D01 통과를 뜻하지 않는다.

`GitStateStore`는 `research`와 `runtime`을 단일 상태 ref로 공개한다. `publish()`는 이전 머리를 비교해 갱신하고 다른 갱신이 먼저 일어났으면 충돌로 반환한다. 기존 산출 묶음의 수정·삭제를 거부한다. 기록 스키마·권한·의미 검사는 저장소 호출 전에 실행기가 수행해야 한다.

## 로컬 검사

전체 구현 검사는 모델을 호출하지 않는 임시 Git·모의 실행 검사와 실제 Windows 프로세스 검사를 실행한다.

```powershell
python -m unittest discover -s .agents/skills/do-math/scripts/tests -p "test_*.py" -v
```

개별 기반 기능도 따로 검사할 수 있다.

```powershell
python .agents/skills/do-math/scripts/tests/test_windows_job.py
python .agents/skills/do-math/scripts/tests/test_codex_adapter.py
python .agents/skills/do-math/scripts/tests/test_git_store.py
python .agents/skills/do-math/scripts/tests/test_budget.py
python .agents/skills/do-math/scripts/tests/test_preflight.py
python .agents/skills/do-math/scripts/tests/test_probe_codex.py
python .agents/skills/do-math/scripts/tests/test_native_probe.py
```

Git 검사는 임시 저장소에서 수행한다. CLI 단위 검사는 시험용 실행 파일을 사용하며, 실제 CLI 검증은 위의 `probe_codex.py`가 수행한다. 명세 검사는 `docs/do-math/통합-설계-명세-v9/README.md`의 절차를 따른다.

스킬 정본과 Codex 사본의 위치·생성 절차는 [멀티런타임 동기화](../writing-skills/references/멀티런타임_동기화.md)를 따른다. Codex 사본을 직접 고치지 않는다.
