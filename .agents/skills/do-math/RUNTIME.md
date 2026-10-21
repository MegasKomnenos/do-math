# 연구 인스턴스 실행과 운영

[runner.py](runner.py)는 목표 하나의 연구를 계획·연구·독립 검토 세션으로 이어 간다. 사용자는 목표·필수조건·허가를 `goal.md`에 정하고, 실행 환경과 범주별 모델을 `settings.json`에 넣는다. 실행기는 첫 계획을 띄우고 게시된 요청을 수행하며, 반영된 목표 검토가 `achieved`라고 판정하면 완료한다. 공개 결과는 인스턴스의 `knowledge/`와 그 인스턴스 자체 Git에서 읽는다. 지식에 반영됐다는 것은 산출 형식을 통과했다는 뜻이다. 수학적 인정 여부는 공개된 독립 검토에서 판단한다.

Python 3.12 이상, Git, 실제 사용할 Codex·Claude CLI가 필요하다. CLI 인증과 모델 접근은 해당 호스트에 준비되어 있어야 한다. 모델 호출·한도 탐지의 세부 계약은 [CLI.md](CLI.md), 산출과 설정의 공용 정의는 [protocol.md](protocol.md)에 있다. 실행기의 프로세스 식별은 Windows와 Linux를 지원한다. Linux에서 세션 종료 명령은 Python의 `pidfd_open`과 `pidfd_send_signal`을 사용한다.

사용자 대화에서 시작해 목표·설정을 준비하고 기동 위치를 전달하는 순서는 [SKILL.md](SKILL.md)를 따른다. 공개 해설·독립 검토·목표 달성 근거를 읽는 경로도 그 진입점에 있다.

## 새 연구 준비

`settings.json`의 필드와 예시는 [protocol.md](protocol.md) 1절이 정본이다. 실행 파일 경로는 실제 설치 경로로 바꾸고, JSON의 Windows 경로에는 `/`를 쓰거나 역슬래시를 `\\`로 적는다. 실행기는 `max_sessions` 안에서 계획을 한 번에 하나만 실행한다. `lean` 설정은 세션이 읽어 Lean을 실행하며, 실행기가 Lean을 대신 실행하지 않는다.

`init`은 원문 두 파일을 복사하고 `knowledge/`, `sessions/`, `runner/`, `control/inputs/`와 자체 `.git/`을 만든다. 첫 Git 커밋에는 목표·설정·`.gitignore`가 들어간다. 세션·실행 상태·사용자 입력은 파일로 보존하되 Git에서는 제외한다. 공개 지식은 반영마다 따로 커밋한다. 커밋 작성자는 호출 명령에 지정한 `do-math <do-math@localhost>`다. `init` 실패 시 생성 도중인 폴더가 남을 수 있으므로 오류를 고친 뒤 새 경로로 준비한다. 기존 인스턴스는 덮어쓰지 않는다.

## 독립 기동과 재기동

`start`는 실행기를 대화와 수명이 분리된 프로세스로 띄운다. Windows에서는 `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`을 사용해 콘솔 창을 띄우지 않으며, stdin은 DEVNULL, stdout/stderr는 호출마다 새 로그 파일이다. Linux에서는 새 프로세스 세션을 만든다. 반환 JSON의 `pid`, `stdout`, `stderr`, `instance`를 기록하면 호출 대화는 종료할 수 있다.

성공을 반환하기 전 새 기동 토큰과 살아 있는 실행기의 OS 프로세스 식별값을 확인한다. stdout 로그에는 그 기동의 `started` 기록이 있다. 이미 완료됐고 처리할 세션이 없는 경우 실행기가 곧 종료할 수도 있다. 이 경우에는 해당 기동의 시작 기록과 완료 상태를 확인한다. 10초 안에 기동 확인을 마치지 못하면 오류와 로그 경로를 반환한다. 이 오류만으로 자식이 종료됐다는 뜻은 아니므로 먼저 로그와 `status`를 읽는다. 초기 설정·맥락 파일 오류나 중복 실행은 시작 오류 로그에서 확인한다.

실행기가 죽거나 PC가 재부팅되면 같은 `start` 명령으로 다시 띄운다. 인스턴스의 파일 잠금은 OS가 유지하므로 프로세스가 죽으면 자동 해제된다. `runner/lock` 파일은 그대로 두며 지우지 않는다. 같은 인스턴스에 두 실행기가 동시에 상태를 바꾸지 못한다.

재기동한 실행기는 기록된 세션의 PID와 OS 생성 식별값을 확인한다. 살아 있으면 기다리고, 죽었으면 남은 산출을 공식 검사·반영 또는 실패로 처리한다. 그 세션을 다시 띄우지 않는다. 게시된 미파견 요청과 아직 전달하지 않은 사건은 이어서 처리한다. 실행기가 쓰는 `max_sessions`, `defaults`, `cli`, `limit_wait_seconds`는 기동 때 읽으므로 변경은 다음 기동부터 적용된다. `lean` 설정은 세션이 `settings.json`에서 직접 읽는 시점의 값으로 사용한다. 실행 중인 세션도 변경 뒤에 읽으면 바뀐 값을 쓰며, 실행기는 설정 형식을 기동 때 검사한다. 세션은 현재 경로의 문서와 도구를 읽는다.

콘솔에 붙여 문제를 관찰할 때는 `python <skill>/runner.py run <instance>`를 쓸 수 있다. 이 명령은 종료까지 반환하지 않으므로 사용자 대화가 새 연구를 시작할 때는 `start`를 사용한다.

## 상태 조회, 정지, 사용자 입력

`status`는 읽기 전용 JSON을 출력한다. `runner_alive`는 실행기 PID와 생성 식별값을 조회한 현재 결과다. `knowledge`는 공개 지식 위치다. `dispatch_blocks`에는 겹칠 수 있는 `STOP`, `external_input`, `usage_limit`, `halted`, `complete`가 나온다. `state`에는 아래 표의 상태 전체가 있다. 실행기가 죽었을 때 세션 상태는 마지막 저장 시점의 것이며, 재기동하면 실제 생존 여부와 대조해 갱신한다.

`stop`은 `control/STOP`을 만든다. 새 파견만 멈추고 이미 시작한 세션은 종료·검사·반영까지 진행한다. `resume`은 이 파일을 제거한다. 외부 입력 대기·공급자 한도·연속 계획 실패 정지(`halted`)·완료는 각각 별도 조건이므로 STOP을 지워도 남을 수 있다. `resume` 자체는 실행기를 시작하지 않는다. `status.runner_alive`가 false라면 `start`가 필요하다.

`input`은 비어 있지 않은 UTF-8 입력 파일의 원문 바이트를 `control/inputs/<고유이름>.txt`로 복사하고 그 경로를 반환한다. 실행 중인 실행기는 입력을 감지해 `user_input` 사건으로 다음 계획에 전달하고 외부 입력 대기를 해제한다. 대기 중에도 실행기는 살아 있으므로 추가 기동은 필요 없다. 실행기가 죽어 있으면 입력을 넣고 `start`한다. STOP이나 한도 대기가 남아 있으면 입력을 보존한 채 그 조건의 해제를 기다린다. `halted`는 입력으로 풀리지 않고 재기동으로 풀린다. 완료 상태는 사용자 입력으로 해제되지 않는다.

파일로 직접 입력할 수도 있다. `control/inputs/`에 고유 이름의 UTF-8 텍스트 파일 하나를 완성한 뒤 추가한다. 실행기는 파일 이름으로 한 번 소비하고 원문은 지우거나 수정하지 않는다. 아직 소비하지 않은 파일이 여럿이면 파일 수정 시각 순서(같으면 이름 순서)로 사건을 만든다. 이미 소비한 파일을 수정해도 새 입력으로 보지 않는다. 쓰는 중인 파일은 점으로 시작하는 임시 이름에 작성한 뒤 최종 이름으로 바꾼다. 점으로 시작하는 파일은 무시한다. 빈 파일·디코딩/읽기 실패는 `state.input_errors`에 남고 소비하지 않으므로 해당 파일을 고쳐 다시 읽게 할 수 있다.

## 멈춰 버린 세션 하나 종료

`kill-session`에는 조회한 실제 세션 ID를 준다. `state.sessions`에서 범주·모델·시작 시각·요청을 읽어 대상 세션을 선택한다. 실행기의 수집 전에는 CLI PID가 아직 상태에 안 들어 있을 수 있으나 `kill-session`은 해당 세션의 최신 `process.json`을 직접 읽는다. CLI 기동 자체가 아직 안 됐거나 프로세스 정보를 얻지 못했다면 종료 명령이 오류를 반환한다.

이 명령은 기록된 CLI의 PID뿐 아니라 OS 생성 식별값까지 같은 프로세스 핸들에서 대조해 종료한다. PID가 다른 프로세스에 재사용됐으면 종료하지 않는다. Windows에서는 `TerminateProcess`, Linux에서는 pidfd로 SIGKILL을 보낸다. 대상은 해당 CLI 프로세스 하나다. CLI가 별도로 띄운 자손 프로세스 전체를 종료하는 명령은 아니다. 실행기나 세션 호스트를 대신 종료하지 않는다.

세션 실행 시간에는 상한이 없다. 강제 종료 뒤에도 실행기는 남은 산출을 일반 종료와 같은 공식 검사로 판단한다. 통과하면 반영하고, 없거나 형식이 틀리면 실패 사건으로 다음 계획에 보낸다. 실행기가 꺼져 있으면 `start`로 이 처리를 이어 간다. 새 파견도 멈추려면 별도로 `stop`을 쓴다.

## 계획이 읽을 미완료 요청과 사건

계획의 기동 프롬프트는 이 문서와 **인스턴스의 `runner/state.json`**을 연결한다. `requests`는 이전 계획이 게시한 요청과 연구 뒤 자동 검토를 모두 보존한다. 새 계획은 `pending`과 `assigned` 요청의 지시·대체 의도를 읽고 중복 작업이나 같은 기록을 동시에 대신할 과제를 피한다. 새 계획의 빈 목록은 기존 요청을 취소하지 않는다.

| state 필드 | 의미 |
|---|---|
| `requests` | 요청 키 → 요청 객체. 계획 요청 키는 `<공개계획ID>:research:<0부터 인덱스>`, `:reviews:<인덱스>`, `:goal_review`. 자동 검토는 `<연구기록ID>:automatic_review`. |
| 요청의 `category`, `task` | 실제 파견할 범주와 작업특정요소. `task.instructions/references`와 연구의 `supersedes` 또는 검토의 `target`을 보존한다. |
| 요청의 `origin`, `selection` | 출처 공개 기록 ID와 요청이 덮어쓴 model/effort만 담은 객체. 선택 이유와 계획의 전체 판단은 `knowledge/<origin>/output.json`에서 읽는다. 자동 검토는 연구 기록이 origin이다. |
| 요청의 `status` | `pending`: 아직 파견하지 않음. `assigned`: 세션 ID에 배정·기동 중이거나 검사·반영 중. `finished`: 유효 산출 반영 완료. `failed`: 기동/산출 실패 처리 완료. |
| 요청의 `session`, `record` | 배정된 세션 ID(배정 전 null), 반영 후 공개 기록 ID. 실패 요청을 재시도하려면 계획이 새 요청을 낸다. |
| `sessions` | 세션 ID → 범주·요청 키·최종 model/effort·상태·프로세스·검사 결과. 상태는 `starting`, `running`, `publishing`, `integrated`, `failed`. `request: null`은 사건을 받은 계획이다. |
| 세션의 `host`, `cli`, `pid`, `started_at`, `cli_started_at` | 호스트와 CLI의 `{pid,birth}` 식별값, CLI PID, 파견 시작과 실제 CLI 시작의 UTC Unix 초. 아직 생성되지 않은 CLI 필드는 없을 수 있다. |
| 세션의 `record`, `reason`, `launch_error`, `log_error`, `exit_code`, `limit` | 공개 기록 ID, 검사 실패 이유, 기동 실패, 한도 로그 읽기 실패, 알 수 있는 종료 코드, 탐지한 한도와 그 출처. 해당할 때 기록한다. |
| `events` | 아직 계획에 전달하지 않은 사건. 기동할 계획의 `input.json.task.events`로 전부 옮기고 비운다. 실행 중 계획에 새 사건을 끼워 넣지 않는다. |
| `seen_inputs`, `input_errors` | 소비한 사용자 파일명 목록, 아직 소비할 수 없는 파일별 진단. 원문은 `control/inputs/`에 남는다. |
| `wait`, `limit_until`, `complete` | 외부 입력 대기 `{needed,reason}` 또는 null, 모든 새 파견의 한도 만료 UTC Unix 초, 완료를 판정한 공개 목표 검토 ID 또는 null. |
| `last_plan` | 마지막으로 반영된 계획의 기록 ID 또는 null. 다음 계획의 `task.previous_plan`으로 전달한다. |
| `plan_failures`, `halted` | 한도 탐지 없이 연달아 실패한 계획 수(계획이 반영되면 0), 그 수가 한도에 이르러 새 파견을 멈춘 표시 `{reason, at}` 또는 null. |

첫 사건은 `start`다. 유효 검토 반영은 `review_finished`, 산출 부재·검사 실패·기동 실패는 `session_failed`, 사용자 원문은 `user_input`이다. 정상 연구 반영 자체는 계획 사건이 되지 않고 자동 검토 요청을 만든다. 새 계획은 빈 슬롯이 생기면 게시 요청보다 먼저 파견되며, 남은 슬롯에는 게시 순서대로 요청을 파견한다. 계획 중 도착한 사건은 다음 계획에 남긴다. 계획이 실패하면 그 계획이 받았던 사건은 실패 사건의 `task.events`에 담겨 다음 계획에 간다. 다음 계획에는 실패 사건과 그 이후 아직 전달하지 않은 사건이 온다.

`session_failed`에는 실행기가 실패 세션의 `category`, 요청 키 `request`, 받은 `task` 원문, 요청의 `origin`, 탐지한 `limit`, `exit_code`, `launch_error`를 함께 담는다. 계획은 실행 상태의 `sessions` 필드를 뒤지지 않고 이 사건에서 원 지시·대체 의도·검토 대상과 실패 원인의 단서를 읽는다. 사건 형식은 [protocol.md](protocol.md) 2절이 정한다.

외부 입력 대기를 선언한 계획이 실행되는 동안 사용자 입력이 이미 도착했다면, 그 입력을 다음 계획에 전달할 수 있도록 대기를 유지하지 않는다. 동일 계획에 요청과 wait가 함께 있으면 요청은 게시되지만 새 입력이 오기 전까지 새 파견은 멈춘다. 실행기는 동시 대체 의도를 판정하지 않으며, 공개 기록의 현재성·상충 검토를 해석할 책임은 계획에 있다.

## 세션 전달, 반영, 복구

모든 세션의 `input.json.context.common`에는 스킬의 `common.md`, `protocol.md`, 인스턴스의 `goal.md`가 들어간다. `context.category`는 스킬의 `plan.md`, `research.md`, `review.md` 중 하나이고 `task`가 이번 작업특정요소다. 기동 프롬프트는 자신의 세션 폴더와 input.json, 지식·설정 위치, 실제 Python·공식 검사기 경로를 담은 argv를 알려 준다. 계획에만 실행 상태 읽기 경로를 추가한다. 검토에는 공개 대상 기록과 자기 입력을 전달하며 작성자의 세션 폴더나 로그 경로를 넣지 않는다.

세션은 자기 폴더에만 쓰도록 지시받는다. CLI 권한 옵션은 무인 실행을 위한 것이며 OS 수준의 폴더 쓰기 격리는 아니다. Codex·Claude 모두 새 대화로 기동한다. UTF-8 `prompt.txt`를 stdin 파일로, 각각의 `cli.stdout.jsonl`·`cli.stderr.log`를 출력 파일로 연결하고 shell 없이 실행한다.

각 세션에는 작은 Python **세션 호스트**가 CLI 핸들을 보유하고 종료를 기다린다. 이 호스트는 AI 세션이나 재기동 서비스가 아니다. 실행기 프로세스가 죽어도 기존 CLI의 종료를 확인해 기록하기 위한 한 번짜리 부모 프로세스다. 실행기는 먼저 배정·사건 소비를 상태에 저장하고, 호스트의 프로세스 식별값을 저장한 후 `GO` 파일로 CLI 시작을 허용한다. 그 사이 중단돼 시작 허가를 못 받은 호스트는 CLI를 띄우지 않는다. 복구 시 그 배정을 검사/실패 처리하며 동일 요청을 재파견하지 않는다.

호스트의 `process.json`은 실제 CLI의 식별값·시작 시각을, `exit.json`은 종료 코드나 기동 오류를 담는다. 실행기는 정상 실행 중 호스트가 보유한 CLI 핸들의 종료를 따르고, 재기동 시 호스트와 기록된 CLI의 생존을 함께 확인한다. 재부팅으로 모두 사라졌으면 남은 산출을 처리한다. 프로세스 조회 권한 오류는 죽은 것으로 간주하지 않고 실행기 오류로 남긴다.

종료 코드·종료 방식과 관계없이 공식 [check.py](check.py)의 `check_session`으로 재검사한다. 통과하면 `output/` 전체를 새로운 `knowledge/k<고유ID>/`로 복사하고 Git 커밋을 남긴다. `input.json`, 중간 작업, 로그는 공개 지식으로 복사하지 않는다. 복사 도중에는 `runner/stage-<기록ID>/`에 두고 완성된 디렉터리를 공개 위치로 옮긴다. 상태에 먼저 기록 ID를 저장하며, 재기동 시 이미 옮긴 기록과 Git 커밋을 확인해 이어 처리하므로 같은 산출을 새 ID로 다시 반영하지 않는다. 기존 공개 기록은 덮어쓰지 않는다.

반영한 계획의 요청 게시, 연구의 자동 검토, 검토의 다음 계획 사건과 세션 처리 완료 표시는 하나의 원자적 상태 교체로 저장한다. Windows에서 다른 독자의 열린 파일 때문에 교체가 잠시 거부되면 같은 교체를 최대 1초 동안 재시도한다. 그동안 독자는 이전의 완전한 상태를 읽으며, 계속되는 접근 거부와 다른 저장 오류는 그대로 드러난다. Git·디스크 오류로 실행기가 종료되면 새 시작 로그의 오류를 해결한 뒤 재기동한다. Git 반영 실패를 수학적 세션 실패로 바꾸지 않는다. `runner/`의 내부 파일이나 공개 기록을 손으로 지우거나 되돌리면 이 복구 경로의 전제가 사라지므로 운영 명령을 통해 진행한다.

공급자 로그에서는 한도 신호만 읽는다. 한도가 있으면 `limit_until`까지 **전체 범주의 새 파견**을 막으며, 진행 중 세션과 종료 산출 처리는 계속한다. 로그 읽기 OSError는 `log_error`로 남겨도 공식 산출 검사를 계속한다. CLI 로그의 일반 문구·JSON 형식·종료 코드는 공개 산출 승인 조건이 아니다. 한도 만료는 STOP·외부 입력 대기·`halted`·완료를 해제하지 않는다.

재검사·Git 반영된 목표 검토의 `goal.verdict == "achieved"`만 완료를 만든다. 완료 뒤 자동 검토·계획을 포함해 새 파견은 모두 막는다. 기존 세션은 계속 종료·반영 처리하고, 모두 끝나면 실행기가 정상 종료한다. 이때 미파견 요청과 남은 사건은 이력으로 남는다. 끝나지 않는 기존 세션이 있으면 실행기도 기다리므로 필요하면 `kill-session`을 사용한다.

계획이 공급자 한도 탐지 없이 연달아 `PLAN_FAILURE_LIMIT`(runner.py 상수, 기본 3)번 실패하면 실행기는 `halted`를 기록하고 모든 새 파견을 멈춘다. 로그인 만료, 쓸 수 없는 모델 이름, 깨진 CLI 경로처럼 계획을 다시 띄워도 같은 실패가 반복되는 원인이 실패와 재계획의 무한 고리를 만들지 않게 하는 장치다. 기존 세션은 계속 종료·반영 처리하고, 모두 끝나면 실행기가 종료한다. 사람이 원인을 고친 뒤 `start`나 `run`으로 재기동하면 `halted`와 실패 수가 풀린다. 연구·검토 실패는 이 수에 들지 않고 사건으로 계획에 간다.

## 명령 결과와 구현 진입점

명령 성공은 종료 코드 0과 stdout JSON이다. `run`은 시작 JSON을 출력하고 실행을 계속하며, 완료나 `halted` 뒤 남은 세션을 배출하면 0으로 종료한다. 명령 실행 오류는 stderr의 `{"error":"설명"}`과 종료 코드 1, 잘못된 인자 사용은 argparse 설명과 종료 코드 2다. `status`는 실행기가 꺼져 있거나 연구가 대기 중이어도 읽기에 성공하면 0이다. `stop/resume/input`은 파일을 전달한 성공이며 세션이 이미 처리했다는 확인은 `status`에서 한다.

실제 정의는 모두 [runner.py](runner.py)에 있다. `initialize/load_settings`는 초기화·설정, `start/Runner.run/InstanceLock`은 독립 기동·단일 실행기·재기동 때의 정지 해제, `Runner.dispatch/session_host`는 입력·CLI 프로세스 전달, `Runner.collect/finish/apply_output`은 종료·검사·Git·후속 흐름, `Runner.ingest_inputs/tick`과 `dispatch_blocks`는 사건·파견·대기, `status/submit_input/terminate_process/main`은 운영 명령이다. `process_identity`의 Windows 생성 시각 및 Linux boot ID+생성 tick은 PID 재사용을 구별하기 위한 프로세스 식별값이다.

[tests/test_runner.py](tests/test_runner.py)는 가짜 CLI 프로세스와 실제 공식 검사기·Git으로 작은 완주, 비정상 종료 산출 반영, 실패·STOP·사용자 입력·합성 한도, 연속 계획 실패 정지와 재기동, 단일 실행기 잠금, 복구·완료 뒤 기존 세션 반영과 독립 기동을 확인한다. [tests/test_state_write.py](tests/test_state_write.py)는 Windows에서 상태 파일 교체 재시도와 지속되는 거부의 오류·이전 상태 보존을 확인한다. [tests/test_check.py](tests/test_check.py)는 산출 구조·참조를, [tests/test_cli_adapter.py](tests/test_cli_adapter.py)는 CLI 명령 생성·한도 탐지를 확인한다.

작업맥락 문서는 시험용 임시 문서를 쓰므로 실제 문서의 판단 내용이나 실제 모델의 수행을 검증하는 시험은 아니다. 실제 Codex·Claude 모델 접근과 혼합 완주는 실제 인스턴스의 공개 결과·검토로 별도 확인한다. 다음 명령은 위의 Python 3.12 이상 환경에서 시험 전체를 실행한다. 상태 파일 교체 시험은 Windows에서만 실행된다.

```powershell
$skill = 'C:/math/.agents/skills/do-math' # 실제 설치 경로
python -B -m unittest discover -s "$skill/tests" -v
```
