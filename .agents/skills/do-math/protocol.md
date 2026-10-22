# do-math의 인스턴스와 산출 계약

이 문서는 실행기와 계획·연구·검토 세션이 파일을 주고받는 계약이다. 목표 하나를 연구하는 **인스턴스** 안에서 세션은 자기 폴더에 결과를 쓰고, 실행기가 공개 산출만 **축적 지식**으로 복사한다. 다음 세션은 이 지식을 읽고 연구를 이어 간다. 사람이 읽는 수학 해설이 주 산출물이며 Lean 원문은 해당하는 결과의 근거다.

구현의 진입점은 [check.py](check.py)의 `check_session`과 `main`이다. 이 문서의 형식과 작은 예시는 해당 검사기의 계약이다. 연구 방법과 판단 원리는 범주별 작업맥락에서 다루며, 실행기의 사용자 명령과 프로세스 상태 내부 형식은 실행기에서 정한다.

## 1. 인스턴스와 파일 책임

인스턴스는 저장소 본체 Git에서 제외되는 폴더(예: `.skill-workspace/do-math/<이름>/`)나 저장소 밖에 둔다. 인스턴스 자체의 Git은 실행기의 `init` 명령이 인스턴스를 만들 때 그 루트에 함께 만든다. 상위 저장소를 인스턴스 Git으로 사용하지 않는다.

```text
INSTANCE/
  .git/                     인스턴스 자체의 기록
  goal.md                   사용자의 목표, 필수조건, 허가
  settings.json             실행 설정
  knowledge/
    k0001/                  실행기가 새로 부여한 기록 ID
      output.json           공개 산출의 분류와 참조
      exposition.md         산출이 제공한 파일(이름은 자유)
      Proof.lean
  sessions/
    s0001/                  실행기가 새로 부여한 세션 ID
      input.json            실행기가 주는 세 층 작업맥락과 작업 대상
      output/               세션이 공개할 모든 파일
        output.json
      work/                 선택적인 중간 작업 디렉터리
      ...                   CLI 로그 등 실행기·세션의 기록
  runner/                   실행기 상태, 사건 대기열, 프로세스 정보
  control/
    STOP                    존재하면 새 세션 파견을 멈추는 표시
    inputs/                 사용자 입력을 고유 이름의 UTF-8 텍스트 파일로 추가
```

세션은 자기 `sessions/<ID>/` 안에만 쓴다. `input.json`은 실행기가 준비하고 세션이 읽는다. 세션의 `output/` 밖 파일은 공개 산출에 포함되지 않는다. 실행기만 `knowledge/`에 새 기록을 추가하고 반영마다 Git 커밋을 남긴다. `runner/`의 내부 스키마와 입력 소비 추적은 실행기의 책임이다. 예외는 `runner/state.json`의 `requests` 하나다. 계획은 이미 게시된 일과 겹치지 않으려고 이 필드를 읽으며, 그 형식과 뜻은 [RUNTIME.md](RUNTIME.md)의 '계획이 읽을 미완료 요청과 사건'이 정하는 계약이다. 계획은 그 밖의 실행 상태 필드에 기대지 않는다. `control/inputs/`의 입력 원문은 보존하고, 실행기가 아직 넘기지 않은 내용을 다음 계획의 사건에 담는다. `STOP`은 이미 돌고 있는 세션을 종료시키지 않는다.

JSON은 UTF-8(BOM도 읽음)이다. 경로 외 문자열은 사람이 읽는 설명을 담을 수 있다. ID는 영문·숫자로 시작하고 영문·숫자·`_`·`-`만 사용한다. 세션 ID와 기록 ID는 서로 다른 이름 공간이며 실행기가 각각 인스턴스 안에서 중복 없이 부여한다. 결과 ID는 연구 산출 하나 안에서만 고유하다. 배열의 빈 값은 `[]`, 선택 결과의 부재는 아래에 지정한 `null`로 쓴다. 필수 설명 문자열은 비어 있지 않아야 한다. 알 수 없는 추가 JSON 필드는 무시한다. 추가 필드만으로 새 실행 동작이 생기지는 않는다.

### 설정

`settings.json`은 다음 필드를 제공한다. 공식 산출 검사는 이 파일을 검사하지 않으며, 실행기는 설정을 읽어 사용한다.

```json
{
  "max_sessions": 8,
  "defaults": {
    "plan": {"model": "codex/gpt-6.1-sol", "effort": "high"},
    "research": {"model": "codex/gpt-6.1-sol", "effort": "high"},
    "review": {"model": "claude/sonnet", "effort": "high"}
  },
  "cli": {"codex": "C:/tools/codex.exe", "claude": "C:/tools/claude.exe"},
  "limit_wait_seconds": 300,
  "lean": {
    "command": ["C:/tools/lean.exe"],
    "version_command": ["C:/tools/lean.exe", "--version"],
    "cwd": null,
    "env": {}
  }
}
```

위 경로·모델은 형식 예시이며 사용 가능한 설치·모델을 설정한다. `max_sessions`는 모든 범주를 합친 양의 정수 상한이다. 사용자가 동시성 상한을 따로 지정하지 않으면 새 인스턴스의 `settings.json`에 기본값 8을 명시한다. `limit_wait_seconds`는 공급자 한도 해제 시각이 없을 때 기다릴 양수 초다. 모델 문자열은 `codex/<CLI에 넘길 모델>` 또는 `claude/<CLI에 넘길 모델>`이다. 실행기는 앞부분으로 CLI를 고르고 `/` 뒤 전체를 모델 인자로 넘긴다. 노력은 비어 있지 않은 문자열이며 `claude/` 모델에는 `low`, `medium`, `high`, `xhigh`, `max` 중 하나를 쓴다. `codex/` 모델에는 문자열을 그대로 전달하며 지원 여부는 CLI와 모델이 정한다. 모델·노력을 지정할 때는 기본값과 합쳐 실제로 사용할 두 값을 함께 확인한다. 전달 방식은 [CLI.md](CLI.md)에 있다.

계획이 게시한 요청에 `model` 또는 `effort`가 있으면 그 필드만 범주 기본값을 덮어쓴다. 하나라도 지정하면 `selection_reason`에 이유를 적는다. 계획 세션 자체와 자동 결과 검토는 범주 기본값을 쓴다.

`lean.command`는 원문 파일의 절대 경로를 마지막 인자로 붙여 실행할 명령 배열이다. `version_command`의 출력이 산출의 `lean.version`에 들어간다. `cwd`는 절대 작업 폴더 또는 `null`(검사를 수행하는 세션 폴더), `env`는 상속 환경에 덮어쓸 문자열 환경변수다. Mathlib을 쓴다면 `command`를 `[".../lake.exe", "env", "lean"]`, `cwd`를 Mathlib 프로젝트로 두고 필요하면 `env.PATH`에 Lean bin과 기존 PATH를 포함한다. 세션이 이 설정을 읽어 컴파일한다. 설치 상태는 실행 시점의 것을 사용한다.

## 2. 실행기가 세션에 주는 input.json

`input.json`은 세션 폴더의 고정 이름이다. 다음 공통 필드는 모두 필수다.

```json
{
  "instance": "C:/research/example",
  "category": "research",
  "context": {
    "common": ["C:/skill/common.md", "C:/skill/protocol.md", "C:/research/example/goal.md"],
    "category": "C:/skill/research.md"
  },
  "task": {
    "instructions": "모든 자연수 n에 대해 n + 0 = n을 증명하고 해설하라.",
    "references": [],
    "supersedes": []
  }
}
```

`instance`는 존재하는 인스턴스의 절대 경로다. 검사기는 여기서 `knowledge/`를 찾는다. `category`는 `plan`, `research`, `review` 중 하나다. `context.common`은 공통요소 문서와 목표·조건 파일의 절대 경로 목록, `context.category`는 해당 범주의 작업공통요소 파일 절대 경로다. 이 경로의 파일은 존재해야 한다. **작업특정요소는 이 input.json의 `task` 객체**다. `task.instructions`는 이번 지시, `task.references`는 사용할 공개 지식의 참조 목록이다(3절).

범주별로 `task`에 다음 항목을 더한다.

| 범주 | 실행기가 주는 항목과 의미 |
|---|---|
| research | `supersedes`: 이번 과제가 대신할 기존 기록 ID 목록. 없으면 `[]`. 계획의 연구 요청에서 복사한다. |
| review | `target`: `{"kind":"research","record":"k0001"}` 또는 `{"kind":"goal"}`. 자동 검토는 대상과 기본 지시를, 추가 검토는 계획의 지시·참조도 받는다. |
| plan | `events`: 이번 계획이 받는 사건 객체 목록. 아래 네 종류를 사용한다. `previous_plan`: 직전에 반영된 계획의 기록 ID이며 아직 없으면 `null`이다. 실행기는 이 필드를 항상 넣는다. 검사기는 필드 생략과 `null`을 모두 허용하고, 그 밖의 값이면 실재하는 계획 기록 ID인지 확인한다. |

계획 사건의 구조 예시다. 검사기는 모든 사건의 `kind`와, `review_finished`의 `record`, `session_failed`의 `session`·`reason`, `user_input`의 `text`를 확인한다. 실패 사건의 나머지 필드는 실행기가 함께 담는 사실이다.

```json
[
  {"kind": "start"},
  {"kind": "review_finished", "record": "k0002"},
  {"kind": "session_failed", "session": "s0003", "reason": "output/output.json이 없음",
   "category": "research", "request": "k0001:research:0",
   "task": {"instructions": "...", "references": [], "supersedes": []},
   "origin": "k0001", "limit": null, "exit_code": 1, "launch_error": null},
  {"kind": "user_input", "text": "자연수에는 0을 포함합니다."}
]
```

이 목록은 사건 종류의 예시다. 실제 첫 계획에는 시작 사건만 있을 수 있다. `review_finished.record`는 재검사를 통과해 반영된 검토 기록이다. 실패는 산출이 없거나 재검사에 실패한 세션이며 계획·검토 실패도 포함한다. 실패 사건에는 실행기가 아는 사실을 함께 담는다. `category`와 `request`는 실패한 세션의 범주와 요청 키이고, 사건을 받은 계획이면 `request`가 `null`이다. `task`는 그 세션이 받은 작업특정요소 원문이다. 실패한 계획의 `task.events`에는 그 계획이 받았다가 처리하지 못한 사건이 그대로 들어 있다. `origin`은 요청을 만든 공개 기록 ID이고 계획이면 `null`이다. `limit`은 탐지한 공급자 한도 `{retry_at, source, provider}`, `exit_code`는 알 수 있는 CLI 종료 코드, `launch_error`는 기동 실패 문구이며, 해당하지 않으면 `null`이다. 실행기는 아직 어느 계획에도 주지 않은 사건 전부를 한 계획에 전달하고, 그 계획 실행 중 생긴 사건은 다음 계획에 전달한다. 정상 연구 종료는 사건이 아니다. 연구 반영은 자동 검토 요청을 만들고, 그 검토의 반영이 계획 사건이 된다.

실행기는 기동 프롬프트에서 세션 폴더, 이 `input.json`, 공식 검사 명령의 위치를 알려 준다. 검토 입력이나 기동 프롬프트에는 작성자 세션의 폴더·로그·중간 파일 위치를 넣지 않는다. 검토는 `knowledge/` 전체와 공개된 대상 기록을 읽는다. 이는 전달 규칙이며 파일 읽기를 감시하는 장치가 아니다.

## 3. 공개 파일, 참조, 대체 기록

각 세션은 `output/output.json`에 산출을 쓰고 그 안에서 가리키는 자기 파일도 `output/` 아래에 둔다. 해설·Lean·계산 자료의 이름과 하위 폴더는 자유다. 출력 안의 파일 경로는 그 `output/`를 기준으로 한 `/` 구분 상대 경로다. 절대 경로, `..`, 파일시스템 링크는 공개 파일 참조로 쓰지 않는다. 반영 후 같은 경로는 `knowledge/<기록 ID>/` 기준이 된다.

모든 범주의 `output.json`에 다음 세 항목이 필수다.

```json
{"category": "research", "references": [], "supersedes": []}
```

`category`는 입력과 같아야 한다. `references`는 실제로 사용한 축적 지식의 참조 배열이다. 각 참조는 `record`가 필수이며 `file`, `result`는 선택 항목이다. 둘을 함께 쓸 수도 있다.

```json
[
  {"record": "k0001"},
  {"record": "k0001", "file": "exposition.md"},
  {"record": "k0001", "result": "r1", "file": "Proof.lean"}
]
```

`record`는 `knowledge/<ID>/output.json`이 있는 기록, `file`은 그 기록 폴더 안의 실제 파일, `result`는 그 연구 기록의 `results[].id`다. 같은 인스턴스의 기록을 참조한다. 자기 산출 파일은 결과의 `exposition`·`lean.sources`나 해설의 상대 링크로 연결한다. 추가 증거 파일도 `output/`에 두고 해설에서 읽는 경로를 설명한다. 공개 해설에 사용한 기존 지식의 의존은 `references`에도 적는다. 웹 문헌은 해설에 서지·인용 URL을 적는다. 검사기는 해설 본문과 Markdown 링크·웹 URL을 해석하지 않으므로, 그 근거의 충분성과 실제 사용 가능성은 작성자와 검토자가 확인한다. 검토자가 작성자의 `work/`나 로컬 절대 경로를 찾아가야 하는 산출은 전달을 마친 것이 아니다.

`supersedes`는 이 새 기록이 **전체를 대신하는** 기존 기록 ID 목록이다. 부분 수정이라면 새 기록에 유지할 결과·근거까지 포함해 읽을 수 있는 전체 산출을 만들고 원 기록을 참조한다. 과제의 `supersedes`는 계획 의도, 산출의 `supersedes`는 실제 대체 선언이다. 실제 연구 결과에 따라 달라질 수 있으며 검사기는 둘을 같게 강제하지 않는다.

현재 내용을 읽는 규칙은 다음과 같다. 같은 주제의 기록 A를 B가 `supersedes`로 대신하면 본문은 B에서 시작하고 A는 이력·근거로 읽는다. B를 C가 대신하면 C에서 시작한다. 다른 주제의 기록은 함께 현재 지식으로 남는다. 같은 기록을 대신하는 가지가 둘이면 어느 쪽도 자동 선택하지 않고 둘 다 읽어 다음 계획이 정리한다. 시간·ID의 크기로 승자를 고르지 않는다. 계획은 같은 기록을 대신할 과제 둘을 동시에 배정하지 않는다. 현재성·가지 충돌은 세션이 읽고 판단하며 실행기와 검사기는 판정하지 않는다.

대체와 수학적 인정은 다르다. 새 결과는 검토 전에는 작성자의 주장이다. 구 기록의 검토가 새 기록으로 자동 승계되지 않는다. 연구 기록 R의 검토는 `category=review`, `target={"kind":"research","record":R}`인 공개 기록에서 찾는다. 검토가 대체됐다면 그 이력을 따라 현재 검토를 읽는다. 한 결과의 같은 항목에 현재 검토들의 긍정 판정과 부정 판정이 함께 있으면(상충) 인정된 결과로 쓰지 않는다. 상충의 정의와 확인을 마치지 못한 판정을 읽는 방법은 [common.md](common.md)의 '공개 지식을 읽는 판단'이 정한다. 계획은 추가 검토 또는 수정 연구를 정한다. Lean 수용, 해설과 Lean의 일치, 목표 충족은 서로 대신하는 판단이 아니다.

## 4. 연구 산출

공통 세 필드에 `results`, `failed_attempts`, `open_questions` 배열을 더한다. 결과 없이 실패·남은 질문만 낼 수도 있다. 실패한 접근은 버리지 않고 다음 계획의 판단 근거로 남긴다.

작은 유효 `output/output.json`:

```json
{
  "category": "research",
  "references": [],
  "supersedes": [],
  "results": [{
    "id": "r1",
    "exposition": "exposition.md",
    "verification": "core Lean 파일을 컴파일했다. #print axioms add_zero_example은 공리에 의존하지 않는다고 출력했다. 자연수 전칭 명제이며 Mathlib은 사용하지 않았다.",
    "lean": {"sources": ["Proof.lean"], "version": "Lean (version 4.32.0)"}
  }],
  "failed_attempts": [],
  "open_questions": []
}
```

이 예시의 `output/exposition.md`:

```markdown
# 자연수의 오른쪽 영 덧셈
자연수 n은 0을 포함한다. 주장: 모든 자연수 n에 대해 n + 0 = n.
Lean의 Nat 덧셈에서 오른쪽 인자가 0인 경우는 n으로 계산된다.
따라서 두 변은 정의에 의해 같으며, Proof.lean의 rfl이 이 사실을 증명한다.
이 해설이 주장하는 것은 자연수 덧셈에 관한 명제다.
```

`output/Proof.lean`:

```lean
theorem add_zero_example (n : Nat) : n + 0 = n := by rfl
```

위 확인·판본 문자열은 작성 형식 예시다. 실제 산출에는 직접 수행한 확인과 도구의 실제 출력 문자열을 적는다. `verification`에는 명령·입력 범위·관측 결과·확인하지 못한 범위를 사람이 이해하도록 적는다. 해설에는 정의·가정·주장·논증이 있어야 한다. 검사기는 파일 존재와 문자열 형식만 확인한다.

Lean을 쓰지 않은 계산·문헌 결과의 `lean`은 `null`이다. Lean을 쓴 경우 `sources`는 하나 이상의 공개 원문 경로, `version`은 그때의 `lean --version` 문자열이다. 의존하는 자체 원문도 함께 공개하거나 지식 참조로 연결하고 컴파일 방법을 해설에 남긴다. 세션은 원문을 컴파일하며, 컴파일하지 못했거나 실패했다면 그 사실을 `verification`에 적는다. 버전 문자열은 정보이며 실행을 차단하는 비교 값이 아니다.

`failed_attempts`의 항목은 `{"description":"시도와 실패 내용", "verification":"어디까지 실제로 확인했고 무엇은 모르는가"}`다. `open_questions`는 남은 질문 문자열 목록이다. 빈 목록은 해당 산출에 기록할 항목이 없다는 뜻이다.

## 5. 검토 산출

검토 대상은 입력의 `task.target`과 일치해야 한다. 연구 검토는 연구 세션 하나의 공개 산출 전체를 대상으로 하고 그 안의 모든 결과 ID를 정확히 한 번씩 판단한다. 결과가 없는 산출은 `results: []`와 `summary`로 실패 접근·남은 질문에 대한 검토를 남긴다.

앞의 연구가 `knowledge/k0001/`에 반영됐을 때의 유효 예시:

```json
{
  "category": "review", "references": [], "supersedes": [],
  "target": {"kind": "research", "record": "k0001"},
  "results": [{
    "result": "r1",
    "assessment": {"verdict": "supported", "reason": "자연수 오른쪽 영 덧셈 주장이 제시한 정의와 증명으로 성립한다."},
    "lean": {"verdict": "accepted", "reason": "공개된 Proof.lean의 사본을 다시 컴파일해 종료 코드 0을 확인했고, #print axioms add_zero_example이 공리에 의존하지 않는다고 출력했다."},
    "alignment": {"verdict": "matches", "reason": "해설과 Lean 모두 모든 자연수 n의 n + 0 = n을 말한다."}
  }],
  "summary": "이 연구 산출의 결과 r1과 확인 범위를 검토했다."
}
```

각 판단은 `verdict`와 비어 있지 않은 `reason`을 가진다. 예시의 판정은 실제 검토를 대신하지 않는다.

| 항목 | 허용 verdict | 의미 |
|---|---|---|
| `assessment` | `supported`, `not_supported`, `undetermined` | 주장하는 결과를 제시한 근거가 뒷받침함 / 뒷받침하지 못함 / 판단을 마치지 못함 |
| `lean` | `accepted`, `rejected`, `not_checked`, `not_applicable` | 공개 원문 재컴파일과 [common.md](common.md)의 공리 기준 통과 / 컴파일 실패 또는 허용 밖 공리 / 미확인 / Lean 없는 결과 |
| `alignment` | `matches`, `differs`, `not_checked`, `not_applicable` | 해설과 Lean의 수학이 일치 / 다름 / 미확인 / Lean 없는 결과 |

검토자는 Lean 수용만으로 결과나 해설이 맞다고 결론 내리지 않는다. 계산은 재현하거나 방법을 점검하고 문헌은 원문과 대조해 `assessment.reason`에 근거와 한계를 적는다. 검토자가 만든 보충 자료 역시 자기 `output/`에 두어 함께 공개할 수 있다.

목표 검토는 특정 결과가 아닌 인스턴스 전체를 대상으로 한다. 같은 review 범주에서 다음 형식을 쓴다. `results`와 `summary` 대신 `goal`이 필수다.

```json
{
  "category": "review",
  "references": [{"record": "k0001"}, {"record": "k0002"}],
  "supersedes": [],
  "target": {"kind": "goal"},
  "goal": {"verdict": "achieved", "reason": "목표의 자연수 전칭 명제가 공개 증명과 해설로 충족됐고 독립 검토도 일치한다."}
}
```

`goal.verdict`는 `achieved`, `not_achieved`, `undetermined` 중 하나다. 실행기는 **반영된 목표 검토의 `goal.verdict == "achieved"`**를 읽어 완료한다. 연구 검토의 `supported`나 `accepted`로 완료하지 않는다. 목표 검토자는 목표·사용자 조건과 축적 지식 전체를 대조하고 근거를 `references`와 `reason`에 남긴다.

## 6. 계획 산출과 파견

공통 세 필드 외에 `reason`, `research`, `reviews`, `goal_review`, `wait`가 필수다. 아래는 첫 연구 하나를 게시하는 유효 예시다.

```json
{
  "category": "plan", "references": [], "supersedes": [],
  "reason": "목표의 기본 명제부터 증명과 해설을 얻는다.",
  "research": [{
    "instructions": "모든 자연수 n에 대해 n + 0 = n을 Lean으로 증명하고 충실한 해설을 써라.",
    "references": [], "supersedes": []
  }],
  "reviews": [],
  "goal_review": null,
  "wait": null
}
```

배열 항목의 정체성은 **계획 기록 ID + 배열 이름 + 0부터 시작하는 위치**로 식별할 수 있다. 실행기는 각 요청을 한 번씩 새 세션으로 파견하고, 세션이 끝나 실패했을 때 다시 할지는 다음 계획이 새 요청으로 정한다. 이후 계획의 빈 목록이 이미 게시된 다른 요청을 취소하지 않는다.

`research[]`는 `instructions`, `references`, `supersedes`를 가진다. 실행기는 이 세 필드를 연구의 `task`로 복사한다. `reviews[]`는 `instructions`, `references`, 연구 `target`을 가진다. 이미 반영된 연구 산출의 추가 검토 요청이다. `goal_review`는 `null` 또는 `instructions`, `references`를 가진 객체이고, 실행기가 `target: {"kind":"goal"}`을 붙여 검토를 만든다. 세 종류 요청 모두 선택적으로 `model`, `effort`, 그리고 지정 이유 `selection_reason`을 가질 수 있다. 예:

```json
{
  "instructions": "기존 검토와 별개로 해설의 전칭 범위를 확인하라.",
  "references": [{"record": "k0002"}],
  "target": {"kind": "research", "record": "k0001"},
  "model": "claude/sonnet",
  "selection_reason": "다른 모델에서 같은 범위를 독립적으로 확인한다."
}
```

자동으로 붙는 검토는 연구 반영 자체에서 생성되므로 계획이 `reviews`에 반복해서 넣을 필요가 없다. 추가 검토는 계획이 필요하다고 판단할 때 요청한다.

`wait`는 `null` 또는 `{"needed":"사용자가 줄 입력", "reason":"왜 그것이 필요한가"}`다. 대기가 선언되면 실행기는 모든 새 파견을 멈춘다. 같은 산출에 요청이 있더라도 게시된 채 대기하고, 기존 실행 중 세션은 끝까지 둔다. 사용자 입력이 들어오면 대기를 풀고 입력 사건을 다음 계획에 전달한다. 계획은 대기 중 예상 작업이 필요하면 요청을 남길 수 있지만 실제로 수행할 의미가 있는지 스스로 판단해야 한다. 검사는 그 연구 가치를 판단하지 않는다.

## 7. 공식 검사와 반영 순서

Python 3.12 이상, 표준 라이브러리만 사용한다. 세션은 다음 명령을 실행하고, 실행기는 아래의 `check_session` 함수로 **같은 검사**를 다시 수행한다. 인자는 인스턴스나 `output/`가 아닌 **세션 폴더 하나**다.

```powershell
python C:/path/to/skill/check.py C:/research/example/sessions/s0001
```

성공은 종료 코드 `0`, 표준 출력 `{"ok":true,"errors":[]}`다. 형식·참조 실패는 종료 코드 `1`, 표준 출력에 `{"ok":false,"errors":["output.json.results[0].exposition: ..."]}`처럼 첫 오류의 위치·이유를 담는다. 그 오류를 고치고 같은 명령을 다시 실행한다. 명령 인자 사용 오류는 argparse의 설명과 종료 코드 `2`다. 검사 결과는 파일을 변경하지 않는다.

Python 소비자는 `check_session(session: str | pathlib.Path) -> list[str]`을 호출할 수 있다. 빈 목록은 통과, 원소 하나의 목록은 첫 실패 이유다. JSON 해석·인코딩·일반 파일 접근 오류도 이 진단으로 돌아온다. 프로그래밍 오류까지 삼키지는 않는다. CLI와 함수는 `Checker.run()`의 동일 검사를 사용한다.

검사기는 입력·산출 필수 항목과 형식, 범주의 일치, 파일·기록·결과 참조의 존재, 연구 검토의 대상 및 결과별 항목 완결성을 확인한다. 참조한 기록 전체를 재귀 검사하거나 기존 기록의 현재성을 판단하지 않는다. Lean을 실행하지 않고, 해설·근거의 옳고 그름, 목표 충족, 검토 판정 사이의 수학적 타당성, 계획의 가치를 판단하지 않는다. 사용한 지식을 빠짐없이 참조했는지는 세션의 책임이다.

실행기는 다음 순서로 이 계약을 소비한다.

1. `input.json`을 준비하고 새 세션을 띄운다. 세션은 공개 산출을 작성하고 위 검사로 확인한 뒤 끝난다. 별도 승인·종료 필드는 없다.
2. 프로세스가 끝나면 종료 코드나 종료 방식과 무관하게 위 검사를 다시 실행한다. 산출이 없거나 실패하면 반영하지 않고 `session_failed` 사건으로 다음 계획에 넘긴다.
3. 통과하면 새로운 기록 ID를 부여하고 **`sessions/<ID>/output/`의 내용 전부**를 새 `knowledge/<기록 ID>/`에 복사한다. `output.json`도 함께 복사하며 내부 경로를 바꾸지 않는다. 대상 디렉터리는 새것이어야 하며 기존 파일은 덮어쓰지 않는다. 입력·작업 폴더·로그는 복사하지 않는다. 세션 폴더도 그대로 남긴다. 새 기록을 인스턴스 Git에 커밋한다.
4. 반영된 계획에서 요청을 읽는다. 반영된 연구에는 기본 검토 하나를 붙인다. 반영된 검토는 계획 사건이 된다. 반영된 목표 검토가 달성이면 완료한다. 완료 뒤에는 자동 검토·계획을 포함해 새 세션을 띄우지 않지만, 이미 돌던 세션의 산출은 종료 시 같은 재검사·반영을 거친다.

실행기는 단일 실행기, 동시 상한, 한 번에 하나의 계획을 지킨다. 사용자 정지, 외부 입력 대기, 공급자 한도 대기, 연속 계획 실패 정지 중에는 새 세션을 띄우지 않는다. 종료한 세션을 그대로 재기동하지 않는다. 각 정지의 해제 조건, 프로세스 관리·재기동과 상태 저장은 [RUNTIME.md](RUNTIME.md)가 정한다.
