---
name: do-math
description: 수학 목표를 계획·연구·독립 검토 세션으로 이어 가는 무인 연구를 시작하고, 진행 조회·정지·입력·개별 세션 종료·재기동을 수행한다. Claude Code와 Codex 대화에서 사용한다.
---

# do-math 사용하기

이 문서는 사용자와 대화하는 세션의 진입점이다. 사용자가 수학 목표를 맡기면 목표 하나의 연구 인스턴스를 준비하고 실행기를 독립 프로세스로 시작한다. 기동을 확인한 뒤 인스턴스 위치를 사용자에게 전달하고 대화를 끝낸다. 이후 계획·연구·검토 세션이 공개 지식을 읽으며 목표 달성까지 연구를 이어 간다. 기존 연구의 조회나 운영 요청이면 해당 인스턴스에 아래 명령을 수행한다.

연구의 주 산출물은 사람이 이해할 수 있는 수학 해설이다. Lean 형식 결과는 해설을 뒷받침하고, 계산·반례·문헌 조사·부분 결과·실패한 접근과 남은 질문도 후속 연구에 쓰인다. 독립 검토는 Lean 수용, 해설과 Lean의 일치, 목표 달성을 구분한다. 목표를 달성한 뒤의 투고 원고·외부 재현 자료 꾸러미·외부 심사 대응은 이 연구의 범위 밖이다.

사용자가 정하는 것은 목표·필수조건·허가다. 이미 받은 조건을 보존하고, 과제 분해·방법·모델 선택 등 그 범위 안에서 판단할 일은 AI가 정한다. 의미 있는 기본 선택이 가능한 준비 작업에 별도 승인 단계를 만들지 않는다. 목표의 의미나 필요한 허가를 사용자만 정할 수 있는 경우에는 그 빠진 내용과 연구에 미치는 영향을 명확히 묻는다. 구현자가 고른 방법을 사용자 필수조건으로 기록하지 않는다.

## 새 연구 준비

1. 이 `SKILL.md`가 있는 실제 폴더를 `$skill`로 잡고 [RUNTIME.md](RUNTIME.md)의 준비·기동 계약을 읽는다. Python 3.12 이상, Git, 사용할 CLI의 설치 경로와 기존 로그인·모델 설정을 확인한다. PowerShell의 `Get-Command python, git, codex, claude -ErrorAction SilentlyContinue`로 경로를 찾을 수 있고 PATH에 없으면 알려진 설치 위치를 읽는다. CLI는 네이티브 실행 파일의 절대 경로를 쓰는 것이 편하다. 설정·도구는 현재 설치를 그대로 사용한다.
2. 사용자의 목표·필수조건·허가를 비어 있지 않은 UTF-8 `goal.md`에 쓴다. 목표에서 무엇이 달성되면 끝나는지 전달하되 연구 전략과 세부 과제는 계획 세션이 정하게 한다. 목표와 설정의 준비 파일은 인스턴스 밖에 둔다.
   증명이나 반증을 요구하는 목표는 기본적으로 Lean 증명이 있어야 달성으로 판정된다. 허용 공리 안의 Lean 정리가 독립 검토에서 수용되고, 그 해설이 Lean과 같은 수학이라고 판정되어야 한다. 정확한 기준은 [common.md](common.md)의 '목표 달성에 필요한 형식 증명'에 있다. 사용자가 비형식 증명으로 충분하다고 하거나 다른 보증 수준을 원하면 그 내용을 `goal.md`에 적는다. 목표 명제를 설정할 Lean 환경으로 진술하거나 증명하기 어려워 보이면(예: 필요한 라이브러리가 없음) 시작 전에 그 사정과 영향을 사용자에게 알리고 보증 수준을 정한다.
3. UTF-8 `settings.json`을 작성한다. [protocol.md](protocol.md) 1절의 JSON 예시와 설명이 필드 정본이다. 전체 동시 세션 상한 안에서 계획은 한 번에 하나만 실행한다. 사용할 수 있는 모델·경로를 그때 선택한다. 설정 형식 통과는 로그인이나 실제 모델 접근의 성공을 뜻하지 않는다.
4. **아직 없는** 인스턴스 경로를 고른다. 저장소 밖이나 상위 Git에서 제외된 `.skill-workspace/` 아래에 둔다. 저장소 안이라면 `git check-ignore` 등으로 제외 여부를 확인한다. `init`이 인스턴스 자체 `.git/`을 만들며, 이 Git이 저장소 본체 Git과 섞이지 않아야 한다.

계획이 연구·추가 검토·목표 검토 요청에 모델이나 노력을 지정하면 해당 필드만 기본값을 덮어쓰고 이유를 남긴다. 계획 자체와 자동 연구 검토에는 범주 기본값이 적용된다. CLI별 노력 값과 인증·무인 호출 방식은 [CLI.md](CLI.md)를 따른다. 세션은 자기 폴더에만 쓰도록 지시받으며 CLI의 무인 권한 옵션이 OS 수준의 폴더 격리를 제공하는 것은 아니다.

Mathlib이 필요하면 `lean.command`를 `["실제 lake.exe 경로", "env", "lean"]`, `cwd`를 사용할 Mathlib 프로젝트 절대 경로로 둔다. `version_command`도 같은 환경에서 판본을 얻도록 `["실제 lake.exe 경로", "env", "lean", "--version"]`으로 둘 수 있다. 필요한 `env.PATH`에는 실제 Lean bin 경로와 기존 PATH를 함께 담는다. JSON 안의 `$env:PATH`는 확장되지 않으므로 준비 시 실제 문자열로 쓴다. Mathlib이 필요 없는 목표는 설치된 core Lean을 직접 쓰면 된다. 컴파일은 세션이 수행하며 설정에 든 경로의 현재 도구를 사용한다.

다음은 Windows의 **경로 배치 예시**다. 현재 읽고 있는 스킬 경로와 준비한 파일·새 인스턴스 경로로 바꾸어 실행한다. 예시 디렉터리가 이미 있으면 새 이름을 고른다.

```powershell
$skill = 'C:/math/.agents/skills/do-math'
$instance = 'C:/math/.skill-workspace/do-math/add-zero'
$goalFile = 'C:/math/.skill-workspace/do-math-inputs/add-zero/goal.md'
$settingsFile = 'C:/math/.skill-workspace/do-math-inputs/add-zero/settings.json'
python "$skill/runner.py" init $instance --goal $goalFile --settings $settingsFile
```

작은 시작 예의 목표는 “모든 자연수 n에 대해 n + 0 = n임을 Lean으로 증명하고 그 증명에 충실한 해설을 작성한다. 자연수에는 0을 포함한다.”다. protocol.md의 기본 모델 예를 쓰면 Codex와 Claude가 서로 다른 범주에 참여한다. 실제 사용자의 목표가 있으면 그 목표를 기록한다.

`init` 성공은 종료 코드 0과 인스턴스 경로 JSON이다. 목표·설정 원문, `knowledge/`, `sessions/`, `runner/`, `control/inputs/`와 자체 Git을 만든다. 실패하면 오류를 해결한다. 생성 도중 남은 폴더를 기존 연구처럼 재사용하거나 덮어쓰지 말고 새 경로로 준비한다.

## 독립 기동을 확인하고 위치 전달하기

```powershell
$launchText = python "$skill/runner.py" start $instance
if ($LASTEXITCODE -ne 0) { throw '기동 오류와 반환된 로그 경로를 확인한다.' }
$launch = $launchText | ConvertFrom-Json
Get-Content -LiteralPath $launch.stdout -Encoding utf8
python "$skill/runner.py" status $instance
```

`start`는 Windows에서 창 없이 독립 실행기를 띄운다. 반환하기 전에 **이번 기동**의 토큰을 가진 시작 로그와 PID·OS 생성 식별값을 확인한다. 반환 JSON의 `pid`, `stdout`, `stderr`, `instance`를 보존하고 새 stdout의 `started` 기록 및 `status.runner_alive`를 확인한다. 예전 로그나 PID만으로 이번 기동의 성공을 판단하지 않는다. 이미 완료된 인스턴스가 곧 종료했다면 시작 기록과 `state.complete`를 함께 확인한다.

사용자에게 인스턴스 절대 경로, 실행기 PID, 새 시작 로그 경로, 현재 실행·대기 상태와 공개 결과 위치인 `<instance>/knowledge/`를 알려 주고 대화를 끝낸다. 연구 완료까지 반복 조회하거나 호출 대화를 유지할 필요가 없다. `run`은 종료까지 반환하지 않는 관찰용 명령이므로 이 시작 경로에서는 `start`를 사용한다.

기동 확인이 10초 안에 끝나지 않으면 오류에 나온 새 로그와 `status`부터 읽는다. 확인 시간 초과만으로 자식이 죽었다고 판단해 다시 띄우지 않는다. 설정·문서·Git 오류나 이미 실행 중인 인스턴스는 stderr를 읽어 처리한다. `status`의 종료 코드 0은 조회 성공이며 연구 성공 판정은 아니다.

## 진행과 결과 읽기

```powershell
python "$skill/runner.py" status $instance
```

`runner_alive`는 지금 실행기가 살아 있는지, `dispatch_blocks`는 새 파견을 막는 조건을 보여 준다. `state.sessions`에는 범주·모델·상태·요청이 있고 `state.requests`에는 게시된 요청 전체가 `status`(`pending` 미파견, `assigned` 배정, `finished` 반영 완료, `failed` 실패)와 함께 있다. 실행기가 죽어 있으면 저장된 세션 상태는 마지막 수집 시점의 값이다. [RUNTIME.md](RUNTIME.md)의 상태 표에서 필드와 사건의 뜻을 읽는다.

공개 결과는 `knowledge/<기록 ID>/output.json`에서 시작한다. 연구의 `results[].exposition`이 가리키는 해설, `verification`, 해당하는 `lean.sources`를 읽고 `failed_attempts`, `open_questions`도 확인한다. 같은 연구 기록을 `target.record`로 가리키는 `category: "review"` 기록에서 독립 판단과 이유를 읽는다. 공개됐다는 사실은 구조·참조 검사를 통과했다는 뜻이며 수학적 인정은 검토로 판단한다. 검토 전 결과는 작성자의 주장이고 현재 검토가 상충하면 인정된 결과로 쓰지 않는다.

`supersedes`는 기존 기록 전체를 대신한다. 대체 사슬 끝의 본문과 필요한 이력을 읽고, 가지가 갈리면 양쪽을 읽는다. 구 연구의 검토는 새 연구에 자동 승계되지 않는다. 자세한 읽기 규칙은 [common.md](common.md)의 ‘공개 지식을 읽는 판단’과 [protocol.md](protocol.md) 3절에 있다.

`state.complete`가 기록 ID이면 `knowledge/<그 ID>/output.json`의 목표 검토 `goal.verdict`와 `goal.reason`에서 달성 근거를 읽는다. 재검사·반영된 목표 검토의 `achieved`가 완료 신호다. 완료 뒤에는 계획·자동 검토도 새로 파견하지 않으며, 이미 돌던 세션은 끝난 산출을 검사·반영한 뒤 실행기가 종료한다. 완료 판정과 아직 남은 실행 세션을 구분해 사용자에게 전달한다.

## 정지, 입력, 한도 대기

| 사용자 요청 | 실행할 명령과 후속 행동 |
|---|---|
| 새 파견 정지 | `python "$skill/runner.py" stop $instance` — `control/STOP`을 만든다. 기존 세션은 계속 실행하며 종료·검사·반영된다. |
| 정지 해제 | `python "$skill/runner.py" resume $instance` — STOP만 제거한다. `status`에서 다른 대기 조건과 실행기 생존을 확인한다. 꺼져 있으면 `start`한다. |
| 정보·요청·답변 전달 | 원문을 비어 있지 않은 UTF-8 파일로 쓰고 `python "$skill/runner.py" input $instance --file 'C:/research-input/answer.txt'`를 실행한다. 경로는 실제 파일로 바꾼다. 반환된 입력 경로를 보존한다. |

입력은 `control/inputs/`에 고유 이름으로 보존되고 실행기가 다음 계획의 `user_input` 사건으로 전달한다. 명령 성공은 파일 전달 성공이며 계획이 이미 읽었다는 뜻은 아니다. 외부 입력 대기는 `state.wait.needed/reason`에서 필요한 답과 이유를 읽고 위 방법으로 입력하면 풀린다. 대기 중 실행기는 살아 있으므로 생존 중이면 추가 기동이 필요 없다. 꺼져 있으면 입력을 넣고 `start`한다. `state.seen_inputs`, `events`, 해당 계획의 입력으로 처리 상태를 볼 수 있다.

공급자 한도에서는 전체 범주의 새 파견이 `state.limit_until`까지 멈춘다. 값은 UTC Unix 초이며 해당 세션의 `limit.source`가 `provider`이면 공급자 해제 시각, `fallback`이면 처리 시각에 `limit_wait_seconds`를 더한 값이다. 실행기는 살아서 기다리며 이미 시작한 세션의 종료·산출 처리는 계속한다. 끝난 세션을 그대로 재시작하지 않고 이후 계획이 새 요청 여부를 정한다.

`dispatch_blocks`에 `halted`가 있으면 계획 세션이 연달아 실패해 실행기가 새 파견을 멈춘 것이다. `state.halted.reason`과 실패한 계획 세션의 `sessions/<ID>/cli.stdout.jsonl`·`cli.stderr.log` 끝부분에서 원인을 확인한다. 로그인 만료, 설정의 모델 이름이나 CLI 경로 오류가 흔한 원인이다. 원인을 고친 뒤 `status`로 실행기 생존을 확인한다. 아직 살아 있으면 남은 세션의 종료·반영을 기다리고, 실행기가 종료한 뒤 `start`로 재기동하면 정지가 풀린다. 남은 세션이 모두 끝나면 실행기는 스스로 종료하므로 `runner_alive`가 거짓이어도 이상이 아니다.

STOP·외부 입력·한도·정지(`halted`)·완료는 별도 조건으로 겹칠 수 있다. 입력은 외부 입력 대기를 풀고, `resume`은 STOP을 풀며, 한도는 만료를 기다리고, `halted`는 재기동으로 풀린다. 완료 상태는 입력이나 `resume`으로 해제되지 않는다. 목표 달성 후 별개의 연구를 요청받으면 새 인스턴스를 준비한다.

## 멈춰 버린 세션 하나 종료하기

세션 실행 시간에는 상한이 없다. `status`의 `state.sessions`에서 범주·모델·`started_at`·요청을 읽어 사용자 요청에 해당하는 세션 ID를 식별한다. 요청의 지시는 `state.requests[요청 키].task`에서 읽을 수 있다. 사건을 받는 계획은 `request: null`이며 자기 `sessions/<ID>/input.json`에 지시와 사건이 있다.

```powershell
$sessionId = 's0123456789abcdef0123456789abcdef' # 실제 조회한 ID로 교체
python "$skill/runner.py" kill-session $instance $sessionId
python "$skill/runner.py" status $instance
```

명령은 최신 `sessions/<ID>/process.json`의 CLI PID와 OS 생성 식별값을 같은 핸들에서 확인하고 **그 CLI 하나**를 종료한다. 자손 프로세스 전체를 종료하는 명령은 아니다. CLI가 아직 기동되지 않아 정보가 없으면 오류를 읽고 현재 상태를 다시 확인한다.

실행기는 강제 종료·비정상 종료도 정상 종료와 같은 공식 검사로 판단한다. 남은 산출이 통과하면 공개 지식과 Git에 반영하고, 산출이 없거나 실패하면 다음 계획에 실패 사건을 넘긴다. 실행기가 꺼져 있으면 `start`로 이 처리를 이어 간다. 새 파견도 막으라는 요청이면 별도로 `stop`을 적용한다.

## 실행기 재기동하기

실행기가 죽거나 PC가 재부팅되면 사용자의 운영 대화에서 `status`로 확인하고 같은 인스턴스에 `python "$skill/runner.py" start $instance`를 실행한다. 위와 같이 새 PID·시작 기록을 확인하고 위치를 전달한다. 자동 재기동 감시 서비스는 두지 않는다.

재기동한 실행기는 기록된 세션의 실제 프로세스 생존을 확인한다. 살아 있으면 기다리고 죽었으면 남은 산출을 공식 검사해 반영 또는 실패 처리한다. 종료한 세션을 다시 띄우지 않는다. 미파견 요청·미전달 사건은 이어 처리한다. 실행기가 쓰는 설정은 기동 때 읽고, `lean` 설정은 각 세션이 `settings.json`을 직접 읽는 시점의 값을 쓴다. 단일 실행기 잠금은 OS가 관리하므로 `runner/lock`을 지우거나 상태 파일을 편집해 재기동하지 않는다.

## 실행 세션이 읽는 문서

실행기의 기동 프롬프트는 자기 세션 폴더·`input.json`·공식 검사 argv를 알려 준다. `input.json.context.common`은 [common.md](common.md), [protocol.md](protocol.md), 인스턴스의 `goal.md`이며 `context.category`는 [plan.md](plan.md), [research.md](research.md), [review.md](review.md) 중 하나다. 작업특정요소는 `task`의 지시·참조와 계획 사건, 연구의 대체 의도, 검토 대상이다.

계획은 [RUNTIME.md](RUNTIME.md)의 ‘계획이 읽을 미완료 요청과 사건’을 따라 기존 요청과 실패한 원 과제를 회수한다. 검토는 공개 `knowledge/`와 `task.target`으로 판단하고 작성자 폴더·로그를 근거로 받지 않는다. 세션은 자기 `output/`에 공개 산출 전체를 쓰고 `python <skill>/check.py <자기 세션 폴더>`로 형식·참조를 확인한 뒤 스스로 끝낸다. 실행기도 종료 방식과 무관하게 같은 검사를 다시 수행한다.
