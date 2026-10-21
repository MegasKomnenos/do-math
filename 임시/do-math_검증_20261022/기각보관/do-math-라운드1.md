---
유형: 기각보관
출처: do-math
라운드: 1
항목: 6
---

# 기각 보관 — do-math 라운드1

## R1-02

### 원문
제목: RUNTIME.md와 SKILL.md가 lean 설정도 실행기 재기동 뒤에야 적용되는 것처럼 적는다

### 위치
.claude/skills/do-math/RUNTIME.md 64행의 "설정은 실행기 기동 때 읽으므로 설정을 바꾼 경우 다음 기동부터 적용된다."와 .claude/skills/do-math/SKILL.md 116행의 "설정은 실행기 기동 때 읽는다." 실제 동작은 둘로 갈린다. 실행기는 `max_sessions`·`defaults`·`cli`·`limit_wait_seconds`를 기동 때 한 번 읽는다(runner.py 264행 `self.settings = load_settings(self.instance)`). 반면 `lean` 설정은 각 세션이 기동 프롬프트의 안내에 따라 인스턴스의 `settings.json`에서 직접 읽는다(runner.py 317행 "Lean 등 설정은 {settings.json}에서 읽는다.", research.md 27행, review.md 27행).

### 기준
목적 진술은 문서와 실행 코드 사이의 정합성을 요구한다.
```
문서 사이, 문서와 실행 코드·검사기·시험 사이의 정합성을 확인하고 실제 결함·불필요한 중복·폐기된 계약의 잔재를 가장 간단한 수정으로 해소한다.
```
(임시/do-math_검증_20261022/동결.md 23행)

설계 원리는 세션이 그 시점의 설정 경로에 있는 도구를 그대로 쓴다고 정한다.
```
**환경은 있는 그대로 쓴다.** 설정한 경로에 있는 Lean, Mathlib, 파일, 도구를 그 시점의 모습 그대로 쓴다.
```
(.async/do-math-rebuild-20261021/context.md 69행)

### 영향
연구 도중 Lean 경로나 `cwd`·`env`를 바꾸는 운영자는 두 문서를 읽고, 실행기를 재기동해야 바뀐 값이 적용된다고 여긴다. 실제로는 재기동하지 않아도 그 뒤 새로 뜨는 연구·검토 세션이 바뀐 `lean` 값으로 컴파일한다. 반대로 실행기가 기동 때 하는 `load_settings`의 `lean` 형식 검사는 재기동 전까지 바뀐 값에 적용되지 않는다. 그래서 잘못 적은 `lean` 값도 곧바로 세션 컴파일에 쓰인다. 재현 경로는 이렇다. 실행 중인 인스턴스의 `settings.json`에서 `lean.command`를 바꾼다. 그러면 다음에 파견된 연구 세션이 실행기 재기동 없이 바뀐 명령으로 컴파일한다.

### 조각 1 — .claude/skills/do-math/RUNTIME.md 64~64행
원래:
```
재기동한 실행기는 기록된 세션의 PID와 OS 생성 식별값을 확인한다. 살아 있으면 기다리고, 죽었으면 남은 산출을 공식 검사·반영 또는 실패로 처리한다. 그 세션을 다시 띄우지 않는다. 게시된 미파견 요청과 아직 전달하지 않은 사건은 이어서 처리한다. 설정은 실행기 기동 때 읽으므로 설정을 바꾼 경우 다음 기동부터 적용된다. 세션은 새 프로세스로 현재 경로의 문서와 도구를 읽는다.
```
대체:
```
재기동한 실행기는 기록된 세션의 PID와 OS 생성 식별값을 확인한다. 살아 있으면 기다리고, 죽었으면 남은 산출을 공식 검사·반영 또는 실패로 처리한다. 그 세션을 다시 띄우지 않는다. 게시된 미파견 요청과 아직 전달하지 않은 사건은 이어서 처리한다. 실행기는 `max_sessions`, `defaults`, `cli`, `limit_wait_seconds`를 기동 때 읽고 검사하므로, 이 값들을 바꾸면 다음 기동부터 적용된다. `lean` 설정은 세션이 `settings.json`에서 직접 읽으므로, 바꾸면 그 뒤 새로 뜨는 세션부터 적용된다. 실행기는 바뀐 `lean` 값의 형식을 다음 기동 때 검사한다. 세션은 새 프로세스로 현재 경로의 문서와 도구를 읽는다.
```

### 조각 2 — .claude/skills/do-math/SKILL.md 116~116행
원래:
```
재기동한 실행기는 기록된 세션의 실제 프로세스 생존을 확인한다. 살아 있으면 기다리고 죽었으면 남은 산출을 공식 검사해 반영 또는 실패 처리한다. 종료한 세션을 다시 띄우지 않는다. 미파견 요청·미전달 사건은 이어 처리한다. 설정은 실행기 기동 때 읽는다. 단일 실행기 잠금은 OS가 관리하므로 `runner/lock`을 지우거나 상태 파일을 편집해 재기동하지 않는다.
```
대체:
```
재기동한 실행기는 기록된 세션의 실제 프로세스 생존을 확인한다. 살아 있으면 기다리고 죽었으면 남은 산출을 공식 검사해 반영 또는 실패 처리한다. 종료한 세션을 다시 띄우지 않는다. 미파견 요청·미전달 사건은 이어 처리한다. `lean`을 뺀 설정은 실행기가 기동 때 읽으므로 바꾸면 재기동해야 적용되고, `lean` 설정은 세션이 뜰 때마다 `settings.json`에서 읽는다. 단일 실행기 잠금은 OS가 관리하므로 `runner/lock`을 지우거나 상태 파일을 편집해 재기동하지 않는다.
```


### 판정
확정: 기각 · 승인기 [1, 2] · 기각기 [3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 3: 관문 4·5 미충족. 원래 문면이 모든 설정을 실행기 재기동에 묶는 문제는 실재하지만, 대체 문면은 Lean 설정을 읽는 시점을 새 세션 기동으로 고정한다. SKILL.md의 “세션이 뜰 때마다”와 RUNTIME.md의 “그 뒤 새로 뜨는 세션부터 적용된다”는 현행 전달 계약이 보장하지 않는 경계를 만든다. 변경 전에 뜬 세션이 변경 뒤 처음 settings.json을 읽어 컴파일하는 경우에도 바뀐 값을 읽을 수 있다. 파일 경로 전달과 세션의 직접 읽기를 설명하는 데서 나아가 적용 시점을 단정하므로 새 부정확성이 생긴다.

## R1-04

### 원문
제목: protocol.md 설정 절이 계획이 지정할 수 있는 Claude 노력 값을 알리지 않아, 기동이 확정적으로 실패하는 요청이 검사를 통과한다

### 위치
.claude/skills/do-math/protocol.md 61행(1절 '설정'). 같은 문서 63행이 계획 요청의 `effort` 지정을 허용한다. 거부하는 구현은 .claude/skills/do-math/cli_adapter.py 61~62행이다.

### 기준
동결문 목적 진술(임시/do-math_검증_20261022/동결.md 23행):

```
문서 사이, 문서와 실행 코드·검사기·시험 사이의 정합성을 확인하고 실제 결함·불필요한 중복·폐기된 계약의 잔재를 가장 간단한 수정으로 해소한다.
```

형식의 존재 이유(.async/do-math-rebuild-20261021/context.md 67행):

```
**형식은 세션 사이의 전달과 해석을 위해서만 둔다.** 서로 다른 세션이 앞 세션의 산출을 받아 올바르게 해석하고 처리하려면, 어느 정도 정해진 형식(프로토콜)을 지켜야 한다.
```

### 영향
계획 세션이 받는 문서는 common.md, protocol.md, goal.md, plan.md이고, 기동 프롬프트로 RUNTIME.md가 더해진다(runner.py 309~324행). 이 가운데 노력 값의 범위를 적은 문서는 없다. protocol.md 61행은 "노력 문자열의 CLI별 전달 방식은 CLI 어댑터가 정한다"고만 말한다. plan.md 123행도 지정 조건만 다룬다.

어댑터는 `claude/` 모델에 대해 `low`, `medium`, `high`, `xhigh`, `max` 밖의 노력을 `ValueError`로 거부한다(cli_adapter.py 61~62행). 설치된 Claude Code 2.1.306의 `--help`도 `--effort`에 같은 다섯 값을 적는다. 반면 check.py 120~122행은 `effort`가 비어 있지 않은 문자열인지만 확인한다.

재현 경로는 다음과 같다.

1. 계획이 `{"model": "claude/opus", "effort": "minimal", "selection_reason": "..."}` 형태의 검토 요청을 게시한다. `minimal`처럼 Codex에서 쓰이는 값이 그 예다.
2. 공식 검사가 이 요청을 통과시키고, 실행기가 요청을 게시한다.
3. `Runner.dispatch`의 `build_command`가 `ValueError`를 낸다. 실행기는 이를 `launch_error`로 기록하고(runner.py 355~357행), 그 세션은 `session_failed`로 다음 계획에 간다.
4. plan.md 43행은 "`launch_error`처럼 과제 내용과 무관한 원인으로 실패했으면 같은 요청을 다시 게시한다"고 지시한다. 따라서 계획은 같은 지정을 다시 게시할 수 있다.
5. 연구·검토 실패는 `PLAN_FAILURE_LIMIT`에 세지 않으므로 이 반복은 실행기 정지로 끝나지 않는다.

허용 값을 계획이 읽는 protocol.md에 적으면, 계획은 지정을 만들 때와 실패 원인을 분류할 때 모두 이 사실을 알 수 있다.

### 조각 1 — .claude/skills/do-math/protocol.md 61~61행
원래:
```
위 경로·모델은 형식 예시이며 사용 가능한 설치·모델을 설정한다. `max_sessions`는 모든 범주를 합친 양의 정수 상한이고, `limit_wait_seconds`는 공급자 한도 해제 시각이 없을 때 기다릴 양수 초다. 모델 문자열은 `codex/<CLI에 넘길 모델>` 또는 `claude/<CLI에 넘길 모델>`이다. 실행기는 앞부분으로 CLI를 고르고 `/` 뒤 전체를 모델 인자로 넘긴다. 노력 문자열의 CLI별 전달 방식은 CLI 어댑터가 정한다.
```
대체:
```
위 경로·모델은 형식 예시이며 사용 가능한 설치·모델을 설정한다. `max_sessions`는 모든 범주를 합친 양의 정수 상한이고, `limit_wait_seconds`는 공급자 한도 해제 시각이 없을 때 기다릴 양수 초다. 모델 문자열은 `codex/<CLI에 넘길 모델>` 또는 `claude/<CLI에 넘길 모델>`이다. 실행기는 앞부분으로 CLI를 고르고 `/` 뒤 전체를 모델 인자로 넘긴다. 노력은 비어 있지 않은 문자열이다. `claude/` 모델의 노력은 `low`, `medium`, `high`, `xhigh`, `max` 중 하나여야 한다. 그 밖의 값이 설정의 기본값이면 `init`과 실행기 기동이 거부되고, 계획 요청의 지정이면 그 세션이 기동되지 않아 `launch_error`를 담은 `session_failed`가 된다. `codex/` 모델의 노력은 그대로 전달되며, 유효한 값인지는 CLI와 모델이 판단한다. CLI별 전달 방식은 [CLI.md](CLI.md)가 정한다.
```


### 판정
확정: 기각 · 승인기 [1, 3] · 기각기 [2] · 처분: 없음
최종 판정: 기각

### 근거
- 기 2: 관문 3에서 성립하지 않는다. 영향 칸은 잘못된 노력이 공식 검사를 통과해 기동 실패가 되고, 같은 요청의 재게시가 반복되는 손상을 기술한다. 대체 문면은 허용 값과 실패 결과를 알리지만 check.py의 허용 범위와 plan.md의 launch_error 재게시 지시는 그대로다. 영향 칸의 예시 요청이 게시된 경우를 따라가면, 수정 뒤에도 검사를 통과하고 동일한 기동 실패와 재게시 경로가 남는다. 문서의 허용 값 누락만으로 결함을 좁히면 개선이지만, 계약상 해결 판단의 잣대인 영향 칸 전체를 없애지는 못한다.

## R1-M1

### 원문
구성: R1-01 · R1-08 · R1-16

### 위치
.claude/skills/do-math/RUNTIME.md 150~155행과 .claude/skills/do-math/protocol.md 289~290행. RUNTIME.md 150행의 시험 설명은 test_runner.py의 연속 계획 실패 정지 시험(tests/test_runner.py 171행 `test_repeated_plan_failures_halt_until_restart`)과 단일 실행기 잠금 시험(215행 `test_lock_and_pending_requests_survive_empty_plan`)을 적지 않고, tests/test_state_write.py와 tests/test_check.py는 이름조차 내지 않는다. 152~155행의 명령은 `-p test_runner.py`와 `-p test_cli_adapter.py`만 실행한다. protocol.md 290행은 패턴 없는 `discover`로 시험 전체를 실행하면서 검사기 시험의 내용만 설명하며, 이 문서는 모든 세션의 공통요소로 실린다.

### 기준
동결문 불변식(임시/do-math_검증_20261022/동결.md 32행):
```
- 실행 가능한 검사: python -m unittest discover -s .claude/skills/do-math/tests -q; 미러 생성 후 python .claude/skills/writing-skills/scripts/build_skill_mirrors.py --check; git diff --check.
```

동결문 목적 진술(같은 파일 23행):
```
문서 사이, 문서와 실행 코드·검사기·시험 사이의 정합성을 확인하고 실제 결함·불필요한 중복·폐기된 계약의 잔재를 가장 간단한 수정으로 해소한다.
```

기억/layer1/M-0600.md 27행:
```
- **시험**: `test_repeated_plan_failures_halt_until_restart`를 먼저 추가했고 `KeyError: 'halted'`로 실패하는 것을 확인한 뒤 구현했다.
```

.async/do-math-rebuild-20261021/context.md 25행:
```
task가 실제 열린 파일로 동일 오류와 해제 후 저장을 재현했고 지속 거부의 이전 상태 보존까지 두 시험으로 확인했다.
```

### 영향
RUNTIME.md의 명령을 따라 실행기나 검사기를 고친 유지보수자는 test_check.py(공식 검사기)와 test_state_write.py(Windows 상태 교체 재시도)를 실행하지 않은 채 확인을 마친다. 그래서 두 영역의 회귀가 드러나지 않는다. 설명만 읽는 사람은 연속 계획 실패 정지, 단일 실행기 잠금, 상태 교체 재시도가 시험으로 확인되는지 알 수 없다. protocol.md 290행은 설명과 다른 범위를 실행하는 같은 안내를 한 번 더 적는다. 그런데 이 문서는 세션의 공통요소이고, 세션은 스킬의 시험을 실행하지 않는다. 그래서 시험 안내가 두 곳으로 갈라지고 서로 어긋난다.

### 근거
사본에서 다음을 확인했다. tests/에는 test_check.py, test_cli_adapter.py, test_runner.py, test_state_write.py 넷이 있다. test_state_write.py는 `@unittest.skipUnless(os.name == "nt", ...)`로 Windows에서만 실행되고, 시험 둘(`test_reader_releases_old_state`, `test_persistent_denial_remains_an_error`)을 가진다. test_check.py의 세 시험은 공개 전달과 CLI, 구조 누락과 검토 범위, 끊긴 참조를 다룬다. common.md 11행은 protocol.md를 모든 세션의 공통요소로 싣는다. protocol.md는 290행에서 끝나므로 289~290행을 지워도 뒤에 남는 문면이 없다. 기준 인용 넷은 원문에서 실재를 확인했다.

구성 항목이 어긋나는 지점은 protocol.md 290행의 처리다. R1-08은 `-p test_check.py`로 범위를 좁히자고 했고, R1-16은 행을 지우고 안내를 RUNTIME.md 한 곳에 모으자고 했다. R1-16을 취했다. 세션이 읽는 문서에 스킬 유지보수용 명령을 두는 것부터가 불필요한 중복이고, 동결문의 검사도 시험 전체를 한 명령으로 돌린다. 이 행이 설명하던 검사기 시험의 내용은 RUNTIME.md의 새 문면이 넘겨받으므로 사라지는 정보는 없다. R1-08이 근거로 든 "이웃 문서의 파일별 `-p` 관례"는 버렸다. RUNTIME.md의 그 관례가 바로 이번 결함이기 때문이다.

RUNTIME.md의 대체 문면은 R1-16의 네 시험 서술을 바탕으로 썼다. 여기에 R1-01이 적은 Windows 한정 실행과 거부 지속 시 이전 상태 보존을 더했다. test_cli_adapter.py가 `tomllib`을 요구하므로, 전체 실행에 Python 3.11 이상이 필요하다는 조건도 CLI.md 136행에 근거해 옮겼다. CLI.md 133~137행의 어댑터 전용 안내는 R1-16의 판단대로 그대로 둔다. 지급 키 밖에서 새로 찾은 결함은 없다.

### 조각 1 — .claude/skills/do-math/RUNTIME.md 150~155행
원래:
````
[tests/test_runner.py](tests/test_runner.py)는 가짜 CLI 프로세스와 실제 공식 검사기·Git으로 작은 완주, 비정상 종료 산출 반영, 실패·STOP·사용자 입력·합성 한도, 복구·완료 뒤 기존 세션 반영과 독립 기동을 확인한다. 작업맥락 문서는 시험용 임시 문서를 쓰므로 실제 문서의 판단 내용이나 실제 모델의 수행을 검증하는 시험은 아니다. 실제 Codex·Claude 모델 접근과 혼합 완주는 실제 인스턴스의 공개 결과·검토로 별도 확인한다.

```powershell
python -B -m unittest discover -s "$skill/tests" -p test_runner.py -v
python -B -m unittest discover -s "$skill/tests" -p test_cli_adapter.py -v
```
````
대체:
````
[tests/test_runner.py](tests/test_runner.py)는 가짜 CLI 프로세스와 실제 공식 검사기·Git으로 작은 완주, 비정상 종료 산출 반영, 실패·STOP·사용자 입력·합성 한도, 연속 계획 실패 정지와 재기동 해제, 단일 실행기 잠금, 복구·완료 뒤 기존 세션 반영과 독립 기동을 확인한다. 작업맥락 문서는 시험용 임시 문서를 쓰므로 실제 문서의 판단 내용이나 실제 모델의 수행을 검증하는 시험은 아니다. 실제 Codex·Claude 모델 접근과 혼합 완주는 실제 인스턴스의 공개 결과·검토로 별도 확인한다. [tests/test_state_write.py](tests/test_state_write.py)는 Windows에서만 실행되며, 독자가 상태 파일을 잠시 열고 있을 때 교체를 재시도해 성공하는지와 거부가 계속될 때 오류를 내고 이전 상태를 보존하는지를 확인한다. [tests/test_check.py](tests/test_check.py)는 공식 검사기로 각 범주와 목표 검토의 공개 전달, 필수 항목 누락, 끊긴 참조를 확인한다. [tests/test_cli_adapter.py](tests/test_cli_adapter.py)는 [CLI.md](CLI.md)의 명령 생성과 한도 탐지를 확인한다. 다음 명령이 네 시험을 모두 실행하며, `tomllib`이 있는 Python 3.11 이상이 필요하다.

```powershell
python -B -m unittest discover -s "$skill/tests" -v
```
````

### 조각 2 — .claude/skills/do-math/protocol.md 289~290행
원래:
```

작은 검증은 `python -m unittest discover -s C:/path/to/skill/tests -v`로 실행한다. 예시를 임시 인스턴스로 구성해 각 범주와 목표 검토, 필수 항목 누락, 끊긴 참조를 확인한다.
```
대체:
```

```


### 판정
확정: 기각 · 승인기 [2] · 기각기 [1, 3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 1: 관문 4·5를 통과하지 못한다. 어댑터 시험의 tomllib 하한을 전체 시험의 실행 환경으로 옮기면서, 공식 검사기와 실행기가 요구하는 Python 3.12 조건을 3.11로 낮추는 새 오류를 넣었다. Python 3.11에는 Path.is_junction이 없어 전체 시험은 안내된 하한 환경에서 실행되지 않는다. 현재의 두 패턴 제한이 시험 범위를 빠뜨린다는 지적 자체는 타당하지만, 그 지적을 고치는 대체 문면은 기존 환경 계약과 맞지 않는다. 변경본이나 시험을 실행하지 않고 문서·호출 코드를 대조해 판정했다.
- 기 3: 관문 4·5 미충족. 시험 전체를 모으는 방향과 누락된 시험 설명은 타당하지만, 대체 문면은 전체 실행에 Python 3.11 이상이면 된다는 새 안내를 넣는다. 이는 어댑터 시험의 tomllib 요구만 전체 시험에 확장한 것이다. 전체 시험에는 Python 3.12에서 제공되는 Path.is_junction을 쓰는 검사기 경로가 포함되므로 3.11에서 성공적으로 실행할 수 없다. 같은 RUNTIME.md 5행의 요구와도 어긋난다. 누락된 회귀 확인을 해결하면서 실행 환경 안내에 새 결함을 들인다.

## R1-05

### 원문
제목: protocol.md 2절에 작업맥락 문서 이름을 아직 정하지 않았던 단계의 문장이 남아 있다

### 위치
.claude/skills/do-math/protocol.md 87행(2절 `context` 설명)

### 기준
동결문 목적 진술(임시/do-math_검증_20261022/동결.md 23행):

```
문서 사이, 문서와 실행 코드·검사기·시험 사이의 정합성을 확인하고 실제 결함·불필요한 중복·폐기된 계약의 잔재를 가장 간단한 수정으로 해소한다.
```

구현자가 정할 것으로 남겨 두었던 항목(.async/do-math-rebuild-20261021/context.md 187행과 192행):

```
다음은 구현자가 정한다.
```

```
- 작업맥락 각 층의 파일 구성과 문면
```

### 영향
"구체적인 문서 이름은 문서 작성자가 정하며 실행기가 그 위치를 넣는다"는 protocol-checker 단계에서 작업맥락 문서가 아직 없을 때 쓴 문장이다. 지금은 이름이 정해져 있다. 실행기는 `common`에 스킬의 `common.md`·`protocol.md`와 인스턴스의 `goal.md`를, `category`에 스킬의 `<범주>.md`를 넣는다(runner.py 309~312행, RUNTIME.md 126행). 같은 절의 예시(76~77행)도 그 이름을 보여 준다.

모든 세션이 이 문서를 공통요소로 읽는다. 그런데 이 문장은 이름을 정할 주체로, 지금은 존재하지 않는 "문서 작성자"를 가리킨다. 그 결과 이름이 아직 유동적이라는 잘못된 신호를 준다. 세션의 판단과 행동에 쓰이는 정보는 없다.

### 조각 1 — .claude/skills/do-math/protocol.md 87~87행
원래:
```
`instance`는 존재하는 인스턴스의 절대 경로다. 검사기는 여기서 `knowledge/`를 찾는다. `category`는 `plan`, `research`, `review` 중 하나다. `context.common`은 공통요소 문서와 목표·조건 파일의 절대 경로 목록, `context.category`는 해당 범주의 작업공통요소 파일 절대 경로다. 이 경로의 파일은 존재해야 한다. 구체적인 문서 이름은 문서 작성자가 정하며 실행기가 그 위치를 넣는다. **작업특정요소는 이 input.json의 `task` 객체**다. `task.instructions`는 이번 지시, `task.references`는 사용할 공개 지식의 참조 목록이다(3절).
```
대체:
```
`instance`는 존재하는 인스턴스의 절대 경로다. 검사기는 여기서 `knowledge/`를 찾는다. `category`는 `plan`, `research`, `review` 중 하나다. `context.common`은 공통요소 문서와 목표·조건 파일의 절대 경로 목록, `context.category`는 해당 범주의 작업공통요소 파일 절대 경로다. 이 경로의 파일은 존재해야 한다. **작업특정요소는 이 input.json의 `task` 객체**다. `task.instructions`는 이번 지시, `task.references`는 사용할 공개 지식의 참조 목록이다(3절).
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 승인하되 고치지 않는다

## R1-12

### 원문
제목: common.md에 옛 설계의 환경 고정·해시 대조를 부정하는 흔적 문장이 남아 있다

### 위치
.claude/skills/do-math/common.md 25행 (「재량으로 판단하고 수행하기」 절 넷째 문단의 둘째 문장)

### 기준
동결문 목적 진술(임시/do-math_검증_20261022/동결.md 23행):
```
문서 사이, 문서와 실행 코드·검사기·시험 사이의 정합성을 확인하고 실제 결함·불필요한 중복·폐기된 계약의 잔재를 가장 간단한 수정으로 해소한다.
```
문서 작성 기준을 정한 사용자 원문(.async/do-math-rebuild-20261021/user-messages.md 117행, 15절):
```
모든 내용을 담겠다는 강박에 따라 그냥 흔적을 안 남기는 대신 '안하기로 했다' 는 식의 사족 등을 남기거나 하지 말고 자연스럽게 읽힐 흐름으로 전달해야 하는 내용을 잘 전달.
```
환경 원리의 정본(.async/do-math-rebuild-20261021/context.md 69행):
```
**환경은 있는 그대로 쓴다.** 설정한 경로에 있는 Lean, Mathlib, 파일, 도구를 그 시점의 모습 그대로 쓴다.
```

### 영향
"환경을 고정하거나 해시를 대조해 유지할 필요는 없다"는 세션이 할 일을 알려 주지 않습니다. 이 문장은 옛 구현의 신뢰 환경 고정과 파일 해시 대조를 걷어 낸 설계 결정을 부정문으로 남긴 흔적입니다(user-messages.md 3절). 세션에게 필요한 행동은 앞 문장 "지급된 도구와 현재 경로에 있는 파일·Lean·Mathlib을 사용한다"에 이미 있습니다. 판본 문자열을 정보로 남기는 일과 재사용 시 확인하는 일도 뒤 두 문장이 담고 있습니다. 이 문장은 옛 설계를 모르는 세션에게 장치의 존재를 처음 알려 주는 사족입니다. 그래서 사용자가 금지한 "'안하기로 했다' 는 식의 사족"에 해당하고, 동결문이 정리 대상으로 지목한 폐기 계약의 잔재입니다. 이 문장을 지워도 세션의 행동은 달라지지 않고 문단은 하나의 흐름으로 읽힙니다.

### 조각 1 — .claude/skills/do-math/common.md 25~25행
원래:
```
목표 달성에 필요한 일을 우선한다. 문제가 생기면 절차를 더하기 전에 문제를 만드는 전제를 줄이거나 다른 방법으로 연구를 진행할 수 있는지 살핀다. 지급된 도구와 현재 경로에 있는 파일·Lean·Mathlib을 사용한다. 환경을 고정하거나 해시를 대조해 유지할 필요는 없다. Lean 판본 문자열은 어느 환경에서 확인했는지를 설명하는 정보로 남긴다. 나중에 그 결과를 다시 쓰는 세션은 그때의 환경에서 필요한 확인을 한다.
```
대체:
```
목표 달성에 필요한 일을 우선한다. 문제가 생기면 절차를 더하기 전에 문제를 만드는 전제를 줄이거나 다른 방법으로 연구를 진행할 수 있는지 살핀다. 지급된 도구와 현재 경로에 있는 파일·Lean·Mathlib을 사용한다. Lean 판본 문자열은 어느 환경에서 확인했는지를 설명하는 정보로 남긴다. 나중에 그 결과를 다시 쓰는 세션은 그때의 환경에서 필요한 확인을 한다.
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 승인하되 고치지 않는다

## R1-17

### 원문
제목: settings.json의 JSON 예시와 필드 설명이 RUNTIME.md와 protocol.md에 겹쳐 있고 SKILL.md가 정본을 둘로 지목한다

### 위치
- .claude/skills/do-math/RUNTIME.md 21~47행: protocol.md 1절과 같은 JSON 예시와 필드 설명
- .claude/skills/do-math/SKILL.md 19행: 「RUNTIME.md의 JSON 예시와 protocol.md 1절이 필드 정본이다」

### 기준
임시/do-math_검증_20261022/동결.md 「목적 진술」:

```
문서 사이, 문서와 실행 코드·검사기·시험 사이의 정합성을 확인하고 실제 결함·불필요한 중복·폐기된 계약의 잔재를 가장 간단한 수정으로 해소한다. 새 감시 체계·호환 계층·검증 포장을 쌓는 방식은 피한다.
```

.async/do-math-rebuild-20261021/context.md 197행:

```
정할 때의 기준은 3절의 원리다. 목적에 기여하는 가장 단순한 방법을 고른다. 장치를 하나 더할 때마다 그것이 2절의 어느 요구에 기여하는지 설명할 수 있어야 한다. 정한 인터페이스는 manager가 `seams.md`에 기록해, 후속 task가 같은 계약을 쓰게 한다.
```

### 영향
사본 RUNTIME.md 23~43행의 JSON은 protocol.md 42~59행의 JSON과 값이 같다. RUNTIME.md 45·47행의 필드 설명도 protocol.md 61~65행과 같은 내용이다. 결국 같은 설정 계약이 두 문서에 따로 적혀 있다. SKILL.md 19행은 두 곳을 모두 정본이라 부른다. 그래서 설정 필드가 바뀔 때 한쪽만 고치면, 설정을 준비하는 대화 세션은 두 정본 가운데 어느 쪽을 따라야 할지 정할 수 없다. protocol.md는 모든 세션의 공통요소이고, research.md 27행이 Lean 설정의 세부를 이 문서 1절로 보낸다. 따라서 정본은 protocol.md 한 곳이어야 한다. RUNTIME.md에만 있는 사실은 Windows 경로 표기, 계획의 단일 실행, 실행기가 Lean을 실행하지 않는다는 점이다. 이 사실들은 RUNTIME.md에 짧게 남긴다.

### 조각 1 — .claude/skills/do-math/RUNTIME.md 21~47행
원래:
````
`settings.json`의 예시다. 실행 파일 경로는 실제 설치 경로로 바꾼다. JSON의 Windows 경로에는 `/`를 쓰거나 역슬래시를 `\\`로 적는다.

```json
{
  "max_sessions": 3,
  "defaults": {
    "plan": {"model": "codex/gpt-6.1-sol", "effort": "high"},
    "research": {"model": "codex/gpt-6.1-sol", "effort": "high"},
    "review": {"model": "claude/sonnet", "effort": "high"}
  },
  "cli": {
    "codex": "C:/tools/codex.exe",
    "claude": "C:/tools/claude.exe"
  },
  "limit_wait_seconds": 300,
  "lean": {
    "command": ["C:/tools/lean.exe"],
    "version_command": ["C:/tools/lean.exe", "--version"],
    "cwd": null,
    "env": {}
  }
}
```

`max_sessions`는 계획·연구·검토를 합친 동시 상한인 양의 정수다. 계획은 이 상한 안에서 한 번에 하나만 실행한다. `defaults`는 세 범주의 기본 모델·노력이며 계획이 요청에서 지정한 `model`·`effort`만 덮어쓴다. 계획 자신과 연구 반영 후 자동 검토에는 각 범주의 기본값을 쓴다. 공급자는 모델의 첫 `/` 앞에서 고르고 뒤 전체를 CLI 모델 인자로 전달한다.

`limit_wait_seconds`는 공급자 거절에서 해제 시각을 알 수 없을 때 기다릴 양의 초 수다. `lean.command`에는 원문 절대 경로를 마지막 인자로 붙이고, `version_command`로 얻은 판본 문자열을 연구 결과에 정보로 기록한다. `cwd: null`은 세션 폴더이며, Mathlib을 쓰면 `command`를 `[".../lake.exe", "env", "lean"]`, `cwd`를 Mathlib 프로젝트의 절대 경로로 설정할 수 있다. `env`는 Lean을 실행하는 세션이 상속 환경에 덮어쓸 문자열 매핑이다. 실행기가 Lean을 대신 실행하지 않는다.
````
대체:
````
`settings.json`의 필드와 예시는 [protocol.md](protocol.md) 1절의 설정이 정본이다. 실행 파일 경로는 실제 설치 경로로 바꾸고, JSON의 Windows 경로에는 `/`를 쓰거나 역슬래시를 `\\`로 적는다. 실행기는 `max_sessions` 안에서 계획을 한 번에 하나만 실행한다. 계획 자신과 연구 반영 후 자동 검토에는 각 범주의 기본값을 쓰고, 계획이 요청에서 지정한 `model`·`effort`는 그 필드만 기본값을 덮어쓴다. `lean` 설정은 세션이 읽어 Lean을 실행하며, 실행기가 Lean을 대신 실행하지 않는다.
````

### 조각 2 — .claude/skills/do-math/SKILL.md 19~19행
원래:
```
3. 아래 의미에 맞춰 UTF-8 `settings.json`을 작성한다. [RUNTIME.md](RUNTIME.md)의 JSON 예시와 [protocol.md](protocol.md) 1절이 필드 정본이다. 사용할 수 있는 모델·경로를 그때 선택한다. 설정 형식 통과는 로그인이나 실제 모델 접근의 성공을 뜻하지 않는다.
```
대체:
```
3. 아래 의미에 맞춰 UTF-8 `settings.json`을 작성한다. [protocol.md](protocol.md) 1절의 JSON 예시와 설명이 필드 정본이다. 사용할 수 있는 모델·경로를 그때 선택한다. 설정 형식 통과는 로그인이나 실제 모델 접근의 성공을 뜻하지 않는다.
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다
