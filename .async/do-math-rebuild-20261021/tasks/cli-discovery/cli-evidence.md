# 설치된 Codex·Claude CLI 연결 근거

확인일: 2026-10-21, Windows 호스트, Python 3.12.10. 대상은 새 do-math 실행기의 CLI 연결이다. 이 문서의 기동 예와 탐지 방식은 **구현 제안**이며, 산출 프로토콜이나 확정된 제품 계약이 아니다. 제품 파일은 변경하지 않았다. 실제 모델 요청과 한도 소진 호출은 하지 않았고, 실제 한도 출력도 관찰하지 않았다. 아래 한도 근거는 설치 파일의 구현과 같은 버전의 공식 소스다.

## 1. 바로 사용할 기동 방법

실행기는 세션 폴더를 만든 뒤, 그 폴더를 프로세스 작업 디렉터리로 삼고 작업맥락을 UTF-8 프롬프트 파일로 전달할 수 있다. 두 CLI 모두 이전 대화 ID 없이 새 프로세스로 시작한다. 완료는 `Popen.poll()` 또는 `wait()`로 판단하고, 성공·실패 종료 코드와 관계없이 세션 폴더의 산출을 공식 검사기에 넘긴다. CLI 최종 답변이나 JSON 이벤트를 연구 산출로 취급하지 않는다.

| 항목 | Codex | Claude |
|---|---|---|
| 확인된 실행 파일 | `C:\Users\wogud\AppData\Local\Programs\OpenAI\Codex\bin\codex.exe` | `C:\Users\wogud\.local\bin\claude.exe` |
| `--version` 결과 | `codex-cli 0.163.0` | `2.1.306 (Claude Code)` |
| 비대화 실행 | `exec` | `--print` / `-p` |
| 프롬프트 | 위치 인자 또는 stdin. `-`는 stdin 지정 | 위치 인자 또는 stdin; 기본 input format은 text |
| 작업 디렉터리 | `--cd <DIR>` 및 프로세스 `cwd` | 프로세스 `cwd`; help에 `--cwd`는 없음 |
| 모델 | `--model <MODEL>` | `--model <model>`; 전체 이름 또는 `sonnet`, `opus`, `fable` 같은 별칭 |
| 노력 | `-c model_reasoning_effort="high"` | `--effort high`; help 허용값 low, medium, high, xhigh, max |
| 무인 승인 | `-c approval_policy="never"`; 최상위 CLI에는 `-a never`도 있음 | `--dangerously-skip-permissions` 또는 permission mode 선택; `--permission-prompts none`은 질문할 동작을 자동 거부 |
| 새 대화 | `exec`만 사용; resume/fork 하위 명령 생략 | continue/resume/fork-session/teleport 생략 |
| 대화 보존 생략 | `--ephemeral` | `--no-session-persistence` (`--print`에서만 사용) |
| 한도 수집용 출력 | `--json` (JSONL) | `--output-format stream-json --verbose` |

근거 원문은 [Codex exec help](codex-exec-help.txt), [Codex 최상위 help](codex-help.txt), [Claude help](claude-help.txt)다. Codex 설치의 bin은 `.codex\packages\standalone\current\bin`으로 연결돼 있다. 경로를 그대로 사용하면 현재 설치를 쓰게 되며 버전 고정 장치를 만들 필요가 없다.

Codex 노력 설정은 같은 버전 공식 [config.schema.json](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core/config.schema.json)의 `model_reasoning_effort`와 `ReasoningEffort`로 확인했다. 이 버전의 형식은 비어 있지 않은 문자열이다. CLI에서 문자열을 받는다는 사실이 모든 모델이 모든 노력 값을 지원한다는 뜻은 아니다. Claude 역시 모델별 지원 여부까지 실행 확인하지 않았다.

아래는 Python 실행기에 넣을 수 있는 argv와 프롬프트 전달 예다. `session_dir`, `prompt_path`, `stdout_path`, `stderr_path`는 실행기가 결정한 절대 경로로 채운다. 예의 모델은 형식 설명용이며 실제 선택은 범주 기본값/과제 지정을 사용한다.

```python
from pathlib import Path
import subprocess

session_dir = Path(session_dir).resolve()
codex_argv = [
    r"C:\Users\wogud\AppData\Local\Programs\OpenAI\Codex\bin\codex.exe",
    "exec", "--model", "gpt-6.1-sol",
    "-c", 'model_reasoning_effort="high"',
    "-c", 'approval_policy="never"',
    "--sandbox", "danger-full-access",
    "--cd", str(session_dir), "--skip-git-repo-check",
    "--ephemeral", "--color", "never", "--json", "-",
]
claude_argv = [
    r"C:\Users\wogud\.local\bin\claude.exe",
    "--print", "--model", "sonnet", "--effort", "high",
    "--dangerously-skip-permissions", "--permission-prompts", "none",
    "--no-session-persistence", "--input-format", "text",
    "--output-format", "stream-json", "--verbose",
]
argv = codex_argv  # 세션에 지정된 모델에 따라 선택
with open(prompt_path, "rb") as inp, open(stdout_path, "wb") as out, \
        open(stderr_path, "wb") as err:
    child = subprocess.Popen(
        argv, cwd=session_dir, stdin=inp, stdout=out, stderr=err,
        shell=False, creationflags=subprocess.CREATE_NO_WINDOW,
    )
# 실행기는 child.pid를 기록하고 다른 작업도 진행한다.
# child.poll() is None이면 실행 중이다. 종료 코드가 생기면 로그와 산출을 처리한다.
```

프롬프트 파일의 입력 예(꺾쇠 부분은 실제 절대 경로로 치환):

```text
당신은 do-math의 <계획/연구/검토> 세션이다.
공통요소 <공통 문서>와 <인스턴스 목표·조건>, 작업공통요소 <범주 문서>,
작업특정요소 <이번 세션 문서>를 읽고 작업하라.
축적 지식은 <축적 지식 폴더>에서 읽는다.
새 파일과 수정 파일은 모두 자기 세션 폴더 <session_dir> 안에만 둔다.
공용 지식과 스킬, 다른 세션 폴더를 수정하지 않는다.
산출을 정해진 형식으로 기록하고 <공식 검사기 실제 명령>으로 검사한 뒤 끝낸다.
```

이 예는 승인 대기로 무인 작업이 멈추지 않게 하는 **권한 선택 제안**이다. 두 실행 파일의 권한 우회는 세션 폴더만의 OS 쓰기 격리를 제공하지 않는다. 쓰기 범위는 위 지시로 전달되며, 실행 중 감시를 추가하지 않는 사용자 원칙에 따른다. 강제 격리가 필요한 경우의 대안으로 Codex help에는 `workspace-write`가 있으나 이 조사에서 Windows 격리와 외부 Lean/Mathlib 접근을 시험하지 않았다. `--add-dir`로 축적 지식이나 저장소를 쓰기 대상으로 추가할 필요는 없다. cwd를 지정했다는 사실만으로 파일 쓰기가 강제 제한됐다고 설명해서는 안 된다.

CLI 자체 인증·캐시·진단 파일의 저장은 연구 산출 쓰기와 별개다. ephemeral/no-session-persistence도 호스트의 모든 부수 쓰기를 차단한다는 뜻은 아니다. `CLAUDE.md`, `AGENTS.md`, 사용자 설정, hooks 등의 상속은 새 대화 여부와도 별개다. 새 세션이라는 요구 때문에 인증 저장소를 새로 만들거나 기존 로그인 정보를 복사할 필요는 없다. 이 호스트의 실제 로그인 성공·모델 접근 권한은 이번 조사에서 다시 시험하지 않았다.

Claude의 `--bare`는 help상 OAuth/keychain을 읽지 않고 API key 또는 settings의 apiKeyHelper로만 Anthropic 인증을 하므로, context가 설명한 claude.ai 구독 로그인을 사용하는 기본 기동에는 넣지 않는다. `stream-json`을 print mode에서 쓰려면 verbose가 필요하다는 오류 분기는 설치 구현에서 확인했다([원문](claude-source-excerpts.txt), byte offset 281410673). 권한 정책이 우회를 금지하거나 기존 환경 설정이 기동을 막는 경우는 일반 CLI 실패로 기록해야 하며 공급자 한도로 분류하지 않는다.

## 2. Codex의 사용 한도: 오류 메시지에서 읽는다

공식 `rust-v0.163.0` 태그의 다음 소스를 2026-10-21에 읽었고 같은 이름의 `upstream-*.rs` 사본을 이 기록 폴더에 보관했다.

- [protocol/src/error.rs](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/protocol/src/error.rs): `UsageLimitReachedError`, Display 구현(705–819행), `retry_suffix`, `retry_suffix_after_or`, `format_retry_timestamp`(822행 이후).
- [exec/src/exec_events.rs](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/exec/src/exec_events.rs): `ThreadEvent`, `ThreadErrorEvent`, `TurnFailedEvent`.
- [exec/src/event_processor_with_jsonl_output.rs](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/exec/src/event_processor_with_jsonl_output.rs): `ServerNotification::Error` 및 `TurnStatus::Failed` 처리. 서버 오류의 메시지와 추가 설명을 문자열로 합쳐 내보낸다.
- [exec/src/event_processor_with_human_output.rs](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/exec/src/event_processor_with_human_output.rs): 같은 오류를 stderr의 `ERROR:` 줄로 내보내는 분기.

**관찰 사실:** `--json`의 오류 레코드는 `{"type":"error","message":"..."}` 또는 `{"type":"turn.failed","error":{"message":"..."}}` 모양이다. `ThreadErrorEvent`에는 message만 있다. 내부 `UsageLimitReachedError.resets_at`이 UTC 시각이어도 exec JSON 오류에 별도 숫자 필드로 보존되지는 않는다. app-server의 resetsAt 필드를 exec stdout에 있다고 가정하면 안 된다.

설치 exe에서도 다음 한도 문구의 존재를 직접 확인했다([문구와 byte offset](codex-local-limit-strings.json)). 단순 문자열 존재를 출력 동작 증명으로 쓰지 않고, 위 같은 버전 소스의 출력 경로와 대조했다.

- `You’ve hit your usage limit` — 일반 한도 및 모델별 한도 문구의 공통 시작.
- `Your workspace is out of credits` — workspace 크레딧 소진.
- `You hit your spend cap` — workspace 지출 상한.

**탐지 제안:** JSON을 읽을 수 있는 줄 중 위 두 오류 이벤트의 메시지만 대상으로 공통 시작 문구를 찾는다. 곡선 아포스트로피 `’`와 ASCII `'`를 동일하게 취급한다. JSON이 아닌 진단 출력은 실제 CLI 오류 줄 `ERROR:`에서 같은 문구를 찾는 보조 경로를 둘 수 있다. 정상 assistant 답변, 도구가 출력한 문서, 일반 `item.completed` 내용에 문구가 등장했다는 이유로 한도를 판정하지 않는다.

**시각의 관찰 사실:** `format_retry_timestamp`는 CLI 호스트의 로컬 시간대로 변환한다. 같은 날짜면 `h:mm AM/PM`, 다른 날짜면 영문 월과 서수 일자·연도·시각을 출력한다. 예를 들어 `7:11 PM`, `Oct 22nd, 2026 7:11 PM`이다. 접두는 대소문자 차이가 있는 `Try again at` 또는 `or try again at`; 시간이 없으면 later 문구다. workspace 크레딧·spend cap 분기는 reset이 붙지 않을 수 있다.

**해석 제안:** 한도라고 식별한 같은 메시지에서만 retry 시각을 읽는다. 영문 월을 직접 매핑하고 일자의 st/nd/rd/th를 제거해 로컬 시각으로 해석한다. 시간만 있으면 메시지가 기록된 로컬 날짜를 사용한다. 종료 뒤 처음 로그를 읽는 구조에서 생성 날짜가 불명확하거나 자정을 넘긴 경우에는 날짜를 임의로 다음 날로 밀지 말고 시각 미확인으로 취급한다. 초가 출력되지 않으므로 표시된 분의 끝까지 약간의 여유를 두는 것은 구현 선택이다. 이미 지난 시각·잘못된 시각·later는 설정된 대기 간격을 적용한다. 표시된 미래 시각이 명확하면 그때까지 기다린다.

`429`, `rate_limit_reached` 같은 토막 문자열만 모든 로그에서 찾는 방식은 권하지 않는다. 일반 API throttling이나 원문 인용과 계정 사용 한도가 섞일 수 있다. 위 문구 밖의 API-key 오류 형식, 서비스 용량 부족, 모델 거절을 포괄적으로 확인한 것은 아니다.

## 3. Claude의 사용 한도: 계정 한도 표식을 먼저 읽는다

근거는 설치된 `claude.exe`에 포함된 읽을 수 있는 JavaScript 및 schema다. 네트워크 오류 응답이나 사용자 인증 파일은 읽지 않았다. 함수명은 축약되어 다른 chunk에서 중복될 수 있으므로 **byte offset과 문맥을 함께** 사용한다. 다음 발췌 파일은 원문 위치를 보존한다.

| 근거 | 확인한 내용 |
|---|---|
| [claude-semantic-excerpts.txt](claude-semantic-excerpts.txt), 246195868 부근 | `api_error: usage_limit_reached`는 계정 자신의 plan/session/weekly/per-model 한도 또는 usage credits spend cap으로 거절된 요청을 뜻한다. 일반 throttle·서비스 비활성화·API key/제3자 429는 같은 표식을 쓰지 않는다고 schema가 설명한다. |
| [claude-limit-details.txt](claude-limit-details.txt), 246164592 | `Ijr` schema: status = allowed / allowed_warning / rejected; 선택 필드 resetsAt, rateLimitType, overageStatus, overageResetsAt, isUsingOverage 등. window 설명은 reset 값을 Unix epoch seconds라고 명시한다. |
| [claude-limit-rendering.txt](claude-limit-rendering.txt), 251248087 | `xxs`는 거절 응답의 unified 헤더를 읽어 status=rejected, isUsingOverage=false를 설정하고 reset 숫자를 채운다. |
| [claude-limit-details.txt](claude-limit-details.txt), 254548522 및 [claude-source-excerpts.txt](claude-source-excerpts.txt), 254587118 | `fvr`가 시간·한도 필드를 직렬화한다. 429의 계정 한도 메시지 분기가 `apiError: usage_limit_reached`, `apiErrorParams.rate_limit_info`를 만든다. |
| [claude-assistant-shape.txt](claude-assistant-shape.txt), 261227600 | `Go` 및 `fOn`: assistant 출력의 **최상위** is_api_error_message, api_error, api_error_params, error에 관련 값을 전달한다. message 내부 필드가 아니다. |
| [claude-limit-details.txt](claude-limit-details.txt), 261232737 | `Ius`가 type=rate_limit_event, rate_limit_info, uuid, session_id를 만든다. schema상 정보가 바뀔 때 나오는 이벤트다. |

**권장 탐지 제안:** `type == "assistant"`, `is_api_error_message == true`, `api_error == "usage_limit_reached"`인 레코드는 계정 사용 한도가 실제 요청을 거절했다는 가장 구체적인 신호다. `api_error_params.rate_limit_info`에서 해제 정보를 읽는다. `error == "rate_limit"`만으로는 부족하다. 위 schema가 명시하듯 여러 다른 원인도 그 값을 공유한다.

다음은 필드 위치를 보여 주는 **합성 예**이며 실제 한도 로그가 아니다. 생략된 필드에 실행기가 의존할 필요는 없다.

```json
{"type":"assistant","is_api_error_message":true,"error":"rate_limit","api_error":"usage_limit_reached","api_error_params":{"rate_limit_info":{"status":"rejected","rateLimitType":"five_hour","resetsAt":1792598400,"isUsingOverage":false}}}
```

`rate_limit_event`도 보조 신호로 사용할 수 있다. 다만 이벤트 자체는 거절 전 경고와 정상 사용량 갱신도 포함한다. `allowed`, `allowed_warning`, utilization 숫자만으로 파견을 멈추지 않는다. rejected라도 paid overage가 사용 가능한 상황과 구분해야 한다. 최소 구현에서는 명시적인 usage_limit_reached를 우선하고, 상태 이벤트만 있으면 `status == rejected`이고 isUsingOverage가 true가 아니며 overageStatus가 allowed/allowed_warning이 아닌 경우에 한도 신호로 해석하는 방식을 제안한다. 이 보조 조건은 구현 정책이며 실제 출력으로 검증된 판정표는 아니다. unknown/누락 필드는 그 사실대로 처리한다.

**해제 시각:** resetsAt 및 overageResetsAt은 Unix 초 단위다. `Date.now()` 비교에서 resetsAt에 1000을 곱하는 구현도 확인했다([rendering 발췌](claude-limit-rendering.txt), 255639238). UTC epoch로 비교하면 지역 시간대를 추정할 필요가 없다. 일반 limiting window는 resetsAt을 사용한다. 추가로 [overage 표시 구현](claude-overage-rendering.txt)의 `$t`를 확인했다. 일반 overageStatus=rejected 분기에서는 두 시각이 모두 있으면 더 이른 값을 표시하고, 하나만 있으면 그 값을 표시한다. 일부 조직 지출 한도 분기는 별도 표시를 하므로 모든 경우를 무조건 min으로 합치지 않는다. 구현 제안은 일반 분기에서 이 표시 선택을 따르고, 특수 한도는 rateLimitType/overageDisabledReason과 원문 메시지를 함께 보며 명확한 시간을 사용하는 것이다. 실제 계정의 다중 한도 해제는 관찰하지 않았다. 시간이 없거나 의미를 결정할 수 없으면 설정 간격만큼 기다린다. 다른 window의 예방적 사용량 통계를 더 늦은 차단 시각으로 합치지 않는다.

이 버전의 typed 표식은 @internal로 설명되어 있어 향후 CLI 변경에서 달라질 수 있다. `You've hit your limit` 류의 사람이 읽는 문구가 있다는 근거도 있지만, 설치 구현에 변형이 많으므로 문구 전체나 locale/time-zone 문자열을 고정 형식으로 의존하는 것보다 위 필드를 우선한다. 실제 API key 또는 cloud 공급자 환경의 한도 지원을 이 조사 결과만으로 보장하지 않는다. 이번 실행 환경은 context상 claude.ai 구독이다.

## 4. 출력 파서는 한도 신호만 읽는다

두 CLI에 JSON 계열 출력 옵션을 쓰는 이유는 **한도 메시지의 출처와 시간 필드만 구분하기 위해서**다. 전체 출력의 JSON 적합성, 완료 이벤트 존재, tool 출력 형식 등은 산출 승인 조건이 아니다.

최소 구현은 프로세스 종료 후 로그를 줄별로 읽고, `json.loads`가 성공한 객체 중 위에서 정한 한도 레코드만 살핀다. 객체가 아닌 값, 알 수 없는 type/field, JSON이 아닌 줄은 그대로 로그에 남기고 지나간다. 기본 Python JSON 처리처럼 중복 키를 이유로 전체 세션을 거부하지 않는다. 읽을 수 없는 레코드가 있어도 산출은 공식 검사기로 독립 평가한다. 진단 문구 보조 탐지를 추가한다면 위의 CLI 오류 위치에만 제한한다. 로그 전체에서 숫자 429나 usage limit 문자열을 찾는 것은 정상 연구 내용까지 오인할 수 있다.

식별한 한도는 새 세션 파견을 멈추는 데 사용한다. 끝난 세션은 다시 실행하지 않고 산출을 평소처럼 재검사한다. 유효한 미래 reset이 있으면 그때까지, 없으면 설정한 간격만큼 기다린 후 원래 흐름으로 돌아간다. 동시에 남아 있는 세션은 계속 돌게 둔다. 한도를 이유로 사용자의 stop이나 외부 입력 대기·완료 상태를 해제하지 않는다. 이 동작은 inputs/context.md의 불변식에 따른 요구다.

모델 이름의 CLI 선택 규칙은 아직 제품 계약이 아니다. 구현 제안으로 `claude-` 접두와 명시적으로 허용한 Claude 별칭(예: sonnet, opus, fable)은 Claude로, `gpt-` 접두는 Codex로 보낼 수 있다. 모르는 이름은 어느 쪽인지 추정해 비용을 발생시키지 말고 설정 오류로 설명하거나 명시 매핑을 받는다. Codex help에는 외부 provider/OSS 경로도 있으므로 모든 가능한 모델 이름을 이 단순 규칙으로 커버한다고 해서는 안 된다.

## 5. Windows 프로세스와 로그

네이티브 exe를 argv 목록과 `shell=False`로 호출하면 PowerShell/cmd를 한 겹 더 거치지 않는다. 긴 한국어 작업맥락을 명령 문자열에 넣지 않고 UTF-8 파일 stdin으로 전달하면 따옴표·줄바꿈·Windows 명령행 길이 문제를 피할 수 있다. stdout/stderr를 파일로 직접 연결하면 실행기가 출력 PIPE를 비우지 않아 child가 막히는 문제도 피할 수 있다. 로그는 bytes로 보관하고 조사할 때 UTF-8 `errors="replace"`로 읽을 수 있다. 동시 세션에는 서로 다른 로그 파일을 사용한다.

세션 종료 판단에는 실행한 **CLI 프로세스의 핸들**을 사용한다. 중간에 뜬 PowerShell wrapper의 종료나 텍스트 완료 문구를 대신 쓰지 않는다. 프로세스 exit code가 0이 아니어도 산출은 검사한다. 일반적으로 spawn 실패는 종료된 세션과 구별해 원인을 기록한다. 세션 실행 시간 상한은 두지 않는다. 사용자가 멈춘 세션의 프로세스를 종료하는 운영 안내는 후속 실행기/SKILL 작업에서 실제 PID 기록 인터페이스에 맞춘다.

실행기 자체를 대화와 분리해 시작하는 Python 기동 예:

```python
import subprocess, sys
with open(runner_stdout, "ab") as out, open(runner_stderr, "ab") as err:
    runner = subprocess.Popen(
        [sys.executable, runner_script, *runner_args],
        cwd=instance_dir,
        stdin=subprocess.DEVNULL, stdout=out, stderr=err,
        close_fds=True,
        creationflags=(subprocess.DETACHED_PROCESS |
                       subprocess.CREATE_NEW_PROCESS_GROUP),
    )
# PID와 시작 로그를 확인한 뒤 호출 대화는 끝낼 수 있다.
```

실행기 자식 세션은 앞 절의 CREATE_NO_WINDOW 예를 사용한다. detached 실행기와는 별도 호출이다. CREATE_NO_WINDOW를 위 DETACHED_PROCESS와 함께 묶을 필요는 없다. PowerShell Start-Process를 선택한다면 `-WindowStyle Hidden`, 명시적인 작업 폴더·로그 리다이렉션을 사용해야 하고 ArgumentList 재인용에 유의한다. 위 Python argv 방식이 단순하다.

**직접 확인한 범위:** [detach-probe.py](detach-probe.py)를 DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, stdin DEVNULL, stdout/stderr 파일로 띄웠다. launcher Python은 PID 16104에서 즉시 반환했고, 도구 호출도 끝났다. child PID 2868은 3초 뒤 [완료 파일](detach-probe.done.json)과 [stdout](detach-probe.stdout.txt)을 남겼으며 stderr는 비어 있었다. [기동 기록](detach-probe-launch.json)의 시작 시 poll 값은 null이었다. 이는 이 도구 호출의 부모 프로세스 종료 뒤 별도 Python 프로세스가 살아서 파일 출력을 마치는 작은 확인이다. 호스트 재부팅, 사용자 로그오프, 외부 job-object 강제 종료 뒤 생존까지 확인한 것은 아니다. 감시 서비스·자동 재기동 장치는 추가하지 않는다.

## 6. 후속 구현자가 이어서 확인할 부분

이 조사만으로 실행 명령의 옵션과 한도 탐지 경로는 구현할 수 있다. 실제 모델 요청, 자율 파일 작업, Windows sandbox, 설치된 사용자 설정과 hooks의 영향은 시험하지 않았다. 따라서 제품의 실제 Codex·Claude 혼합 완주 시험에서 각 CLI가 프롬프트를 읽고 자기 폴더에 산출을 남기는지 확인해야 한다. 이 조사를 위해 별도의 유료 OK 호출을 반복할 필요는 없다.

한도 발생은 유도하지 않았다. 한도 탐지 시험은 위 근거에서 만든 합성 레코드로 작게 확인할 수 있으며 이를 실측 로그라고 부르면 안 된다. Codex의 날짜 생략, Claude의 다중 overage reset, typed 필드의 향후 변경 및 generic API-key 429는 남은 불확실성이다. 명확한 시간을 못 얻었을 때 설정된 간격으로 기다리는 요구가 이 불확실성의 기본 처리다. 인증 토큰·쿠키·비밀 설정은 수집하지 않았다.
