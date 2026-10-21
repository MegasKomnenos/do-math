# Windows 명령과 같은 파일 중복 패치 안내 수리

`references/공통-실행.md`의 실제 명령 작성 문맥에 PowerShell, cmd, JSON 전송 표기의 구분과 Codex `apply_patch` 수리 예시를 추가했다. 기존 common 지급 경로를 사용하며 문서 목록·입력 필드·역할의 일반 책임은 바꾸지 않았다. 공식 생성기로 Codex 사본을 생성했다.

## 원자료에서 확인한 실패 경계

읽기 전용 원자료는 `C:\math\.skill-workspace\parking-unimodality-20261021\audit\subcommand-failures.json`, `shell-quoting-reproduction.json`, `execution-audit.json`과 각 실행의 `work/runs/<실행 ID>/evidence/stdout.jsonl`, `stderr.txt`다. 선별한 실제 기록과 대조 스크립트는 task evidence에 보존했다.

| 실행 | 원 stdout 행 | 확인한 요청·반환 |
|---|---|---|
| `EX-01M5D0439H0A0Z9G78RQWMTX7E` | 15–18 | cmd의 `type` 파일 읽기 4건. 기록된 실제 command에 따옴표 앞 역슬래시가 남았으며 모두 exit 1, `The filename, directory name, or volume label syntax is incorrect.` |
| `EX-01M5D0AXEYDK81HN6VW4E9D6NY` | 7 | Python으로 지급된 읽기 도구를 호출한 1건. 실행파일 경로의 따옴표 앞 역슬래시가 남았으며 exit 1, `is not recognized as an internal or external command` |
| `EX-01M5CZCPZ17BXEM98HYMJ98B28` | stderr | `2026-10-20T15:42:17.699960Z`, `apply_patch verification failed: invalid patch: multiple operations target ...\activity-extensions.json` |
| `EX-01M5CZSKE82FXDZJHKDYYB393R` | stderr | `2026-10-20T16:01:06.305110Z`, 같은 오류의 대상이 `checkpoint.json` |

`collect_original.py`는 감사표의 5개 command·exit_code·output을 지목된 원 stdout 행의 `command_execution`과 각각 동일 비교했다. 이는 파일 읽기·Python 호출의 부분 실패이며, 실행 전체의 실패 판정은 아니다. 원 `shell-quoting-reproduction.json`도 잘못된 역슬래시가 남은 표기는 실패하고 정상 따옴표 표기는 성공한 대조를 담고 있다.

패치 2건은 원 stderr로 도구 이름·오류·대상을 확인했다. 원 stdout의 `file_change`는 path/kind/status만 담고 **거부된 패치의 요청 본문은 담지 않는다**. 해당 thread ID의 영구 rollout도 찾지 못했다. 현행 `worker_request.codex_argv()`는 `exec --ephemeral`을 사용한다. 따라서 과거 요청이 두 Update였는지, Delete+Add였는지는 확정하지 않는다. 뒤의 현재 도구 재현으로 확인한 계약과 과거에 관측한 오류를 구별한다.

## 무해한 명령 확인

확인은 이 task의 `evidence/공백 있는 폴더/`에서만 수행했다. `probe.txt`에는 `guidance probe` 한 줄을 쓰고, `version probe.py`는 `import sys; print(sys.version.split()[0]); print(sys.argv[1:])`만 수행한다. 공백 있는 실행파일 경로를 확인하기 위해 설치 Python 실행파일을 이 폴더의 `python probe.exe`로 복사했다. 사용자·원 연구 파일을 쓰는 확인은 하지 않았다.

다음은 도구 요청의 JSON을 해석한 뒤의 PowerShell 명령 문자열이다. `exec_command`의 `workdir`은 task evidence 절대 경로, `login=false`, 셸은 `C:\Program Files\PowerShell\7\pwsh.exe`였다.

```powershell
Get-Content -LiteralPath '공백 있는 폴더\probe.txt'
& '.\공백 있는 폴더\python probe.exe' --version
& '.\공백 있는 폴더\python probe.exe' -B '.\공백 있는 폴더\version probe.py' 'one argument'
```

각각 exit 0으로 `guidance probe`, `Python 3.12.10`, `3.12.10`과 `['one argument']`를 출력했다. 실행파일·스크립트 경로 모두 공백을 포함하며 마지막 문자열은 한 인수로 전달됐다.

cmd의 명령 문자열과 프로세스 호출 경계를 따로 확인했다. `probe_cmd.py`는 `shell=True`나 다른 셸을 거치지 않고 Windows raw process command line으로 cmd를 시작했다. 실행파일이 따옴표로 시작하는 경우의 실제 프로세스 표기는 다음 형태이며, `EXE`는 evidence의 복사한 실행파일 절대 경로로 치환했다.

```text
"C:\Windows\system32\cmd.exe" /d /s /c ""EXE" --version"
```

| cmd가 해석할 문자열 | exit | 실제 출력 |
|---|---|---|
| `type "<probe.txt 절대 경로>"` | 0 | `guidance probe` |
| `type \"<probe.txt 절대 경로>\"` | 1 | `The filename, directory name, or volume label syntax is incorrect.` |
| `"<Python 절대 경로>" --version` | 0 | `Python 3.12.10` |
| `\"<Python 절대 경로>\" --version` | 1 | `is not recognized as an internal or external command` |
| `"<Python 절대 경로>" -B "<스크립트 절대 경로>" "one argument"` | 0 | `3.12.10`과 `['one argument']` |

각 행의 정확한 경로·process command line·stdout·stderr와 JSON 직렬화/역직렬화 동일성은 `cmd-raw-probes.json`에 보존했다. 정상 wire 예 `{"cmd":"type \"공백 있는 폴더\\probe.txt\""}`는 `type "공백 있는 폴더\probe.txt"`로 해석된다. wire에 `\\\"`를 넣으면 해석 후 `\"`가 남는다. JSON의 표시를 셸 문법으로 다시 복사하지 않도록 안내했다.

추가로 PowerShell에서 `& $env:ComSpec /d /s /c 'type "공백 있는 폴더\probe.txt"'`와 `& $env:ComSpec /d /c '".\공백 있는 폴더\python probe.exe" --version'`은 각각 exit 0, 파일 내용과 Python 버전을 출력했다. 공백 있는 스크립트·문자열 인수를 포함한 같은 방식도 exit 0이었다.

반면 이번 `exec_command`에 `shell=cmd.exe`와 정상 cmd 문자열을 직접 준 시도 2건은 실패했다. PowerShell에서 cmd에 전달할 문자열에 raw process 호출용 바깥 따옴표를 추가한 시도 2건도 실패했다. 전자의 내부 wrapper argv는 관측하지 않았으므로 그 원인을 단정하지 않는다. 이 차이 때문에 안내는 cmd 명령 자체, 직접 프로세스 시작, PowerShell에서의 cmd 호출을 구분하고 도구별 무해한 확인을 요구한다. 모든 도구의 cmd 감싸기가 같은 방식으로 동작한다는 주장은 하지 않는다.

## 실제 패치 도구 계약과 수리 확인

현재 지급된 `tools.apply_patch(input: string)`는 JSON 편집 목록 대신 freeform 패치 텍스트를 받는다. task 전용 `evidence/patch-probe.txt`에 `alpha`, 세 문맥 행, `omega`를 두고 같은 요청에 이 경로의 Update 두 개를 제출했다. 실제 반환은 `apply_patch verification failed: invalid patch: multiple operations target <task evidence 절대 경로>\patch-probe.txt`였다.

거부 직후 `Get-Content`로 읽어 `alpha`와 `omega`가 그대로인 것을 확인했다. 현재 내용에 맞춰 Update 하나에 hunk 두 개를 합쳐 재제출했다.

```diff
*** Begin Patch
*** Update File: notes.txt
@@
-alpha
+ALPHA
@@
-omega
+OMEGA
*** End Patch
```

실제 요청에서는 `notes.txt`를 task evidence의 절대 경로로 바꿨다. 도구 호출은 성공했고 다시 읽은 파일은 `ALPHA`, 원래 세 문맥 행, `OMEGA`였다. 정확한 요청·도구 반환·거부 후 읽기와 성공 후 읽기를 `tool-probes.json`에 남겼다. Delete+Add 조합을 과거 오류의 원인이라고 추정하지 않았으며, 안내는 기존 파일의 변경을 한 Update로 작성하도록 한다. 다른 패치 도구에 이 문법을 일반화하지 않는다.

## 실제 역할 지급과 최소 검증

정본 AGENTS.md와 SKILL.md 읽기 대응표, `contracts.reading_map()`, `prompt_documents()`, `render_prompt()`를 확인했다. common 행은 이미 `references/공통-실행.md`를 지정하고, `reading_map()`은 이를 `contracts.ROLES`의 10개 역할 각각의 문서 순서에 합친다. `prompt_documents()`는 원바이트에서 path/sha256/content를 만들고, `render_prompt()`는 그 전문을 모델 입력에 포함한다. 새 필수 경로나 입력 필드를 추가할 이유가 없다.

`verify_delivery.py`로 정본과 생성된 Codex 사본 각각에 대해 10개 역할의 **실제** `prompt_documents`와 `render_prompt`를 호출했다. 총 20개 프롬프트에서 공통 문서의 바이트·SHA-256 일치, 전문 포함, 새 명령·패치 안내 포함을 확인했다. `prompt-delivery.json`은 역할·트리별 문서와 프롬프트 해시를 담는다. 독립 운영/설치 복구의 고정 프롬프트는 이 내부 역할 모집단에 포함하지 않는다.

기존 `unit.test_planning_reading_map`에 설치된 공통 문서 전문이 모든 내부 역할의 프롬프트에 도달하는 시험 하나를 추가했다. 셸·패치 예시는 task 전용 작은 확인으로 끝냈으며 제품 도구를 복제한 시험은 만들지 않았다.

```powershell
python .claude/skills/do-math/scripts/run_tests.py unit.test_planning_reading_map structure.test_doc_code --output ..\evidence\selected-tests
python .claude/skills/writing-skills/scripts/build_skill_mirrors.py --check
```

관련 선택 시험은 한 실행에서 54개 passed, `complete=true`, `successful=true`, exit 0이었다. 새 읽기 시험은 0.375초로 0.2초 권고 예산을 넘었다는 표시가 있으나 실패는 없었다. 시험 실행기가 갱신한 범위 밖 `.timings.json`은 task baseline에서 복원했다. 공식 생성기는 2개 사본 파일만 갱신했고 `--check`는 1388파일 드리프트 없음, exit 0이었다. `.agents/diff`와 다른 스킬의 변경은 없다.

이 결과는 안내의 실행 예시와 실제 지급을 확인한 것이다. 미래의 모든 역할이 안내를 준수한다거나 과거 실패를 다시 실행해 성공시켰다는 증거는 아니다. 원 연구·HOLD·예약·graphify와 역할의 일반 책임 개정은 이 작업에서 다루지 않았다.

영구 근거 위치: `C:\math\.async\dm-flow-repair-20261021\tasks\windows-patch-guidance\evidence\`. `original-boundaries.json`, `tool-probes.json`, `cmd-raw-probes.json`, `prompt-delivery.json`, `selected-tests/report.json` 및 재현 스크립트는 workspace 정리 뒤에도 이 위치에 남는다.
