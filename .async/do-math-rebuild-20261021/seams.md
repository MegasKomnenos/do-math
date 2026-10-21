# do-math 재구축: 인터페이스

이 문서는 새 do-math의 구성 요소가 서로 주고받는 것을 정리한다. 흐름과 불변식, 그 이유는 `context.md` 3·4절에 있다. 구성 요소는 실행기, 세 범주의 세션, 공식 검사 스크립트, 사용자 대화, CLI다. 수용된 산출 계약의 진입점은 REPO 기준 `.claude/skills/do-math/protocol.md`이며 제품 문서의 절을 참조할 때 그 파일명을 함께 적었다. 실제 검사는 같은 폴더의 `check.py`에 있다. 운영 인터페이스는 `runner.py`와 `RUNTIME.md`, CLI 인터페이스는 `cli_adapter.py`와 `CLI.md`에 정의되어 있다.

## 1. 연구 인스턴스 폴더

현재 계약 상태: 프로토콜·검사기, CLI 어댑터, 작업맥락 네 문서, 실행기와 운영 문서, SKILL 진입 안내, 실제 혼합 모델 완주와 최종 독립 개발 review를 수용해 개발을 완료했다. runner에서 공급자 접두 모델 표기를 맞췄고 mixed-completion에서 Windows의 일시적 파일 교체 거부 처리를 보완했다. 1~8절의 계약은 사용 가능한 최종 구현을 설명한다. final-review는 제품·인터페이스를 변경하지 않았으며 요구별 대조와 확인 한계는 RECORDS의 `tasks/final-review/review.md`, 수용 판단은 `managers/0009/decision.md`에서 찾는다.

실행기, 세션, 사용자 대화가 함께 쓰는 공간이다. 연구 인스턴스 하나에 폴더 하나다. 다음이 들어가야 한다.

- 목표와 사용자 조건
- 설정: 동시 세션 상한, 범주별 기본 모델·노력 수준, 공급자 한도 대기 간격, CLI 경로, Lean 명령
- 축적 지식
- 세션마다의 세션 폴더
- 실행기의 상태 기록
- 사용자의 정지 표시와 입력이 놓이는 자리

이 폴더의 Git 기록은 저장소 본체의 Git 기록과 섞이지 않게 둔다.

구체 형식: `protocol.md` 1절. 인스턴스는 `goal.md`, `settings.json`, `knowledge/<record>/`, `sessions/<session>/`, `runner/`, `control/STOP`, `control/inputs/`를 갖고 자체 `.git/`을 둔다. `.skill-workspace/` 등 상위 Git에서 제외된 곳이나 저장소 밖에 만든다. 기록 ID와 세션 ID는 실행기가 각각 중복 없이 부여한다. 사용자는 고유 이름의 UTF-8 텍스트를 inputs에 추가하며 원문은 보존한다. STOP의 존재는 새 파견만 막는다. runner 내부 상태의 읽기 계약은 이 문서 7절과 RUNTIME.md에 있다.

설정은 `max_sessions` 양의 정수, `defaults.plan/research/review`의 `{model, effort}`, `cli.codex/claude` 경로, `limit_wait_seconds` 양수, `lean`의 `{command, version_command, cwd, env}`다. 모델은 `codex/<model>` 또는 `claude/<model>`이며 `/` 뒤 전체를 CLI에 전달한다. Lean command는 배열 뒤에 원문 절대 경로를 붙여 호출한다. cwd는 절대 경로 또는 null(세션 폴더), env는 상속 환경에 덮어쓰는 문자열 매핑이다. 세션이 이 설정으로 컴파일하며 version_command의 실제 문자열을 정보로 남긴다. 공식 산출 검사는 settings를 검사하지 않는다.

## 2. 실행기 → 세션: 기동

실행기는 세션을 새 CLI 프로세스로 띄운다. 세션이 시작할 때 다음을 알 수 있어야 한다.

- 자기 범주
- 작업맥락 3층의 위치
  - 공통요소: 스킬 폴더의 문서, 그리고 인스턴스 폴더의 목표·조건
  - 작업공통요소: 자기 범주의 문서
  - 작업특정요소: 이번 세션의 파일
- 축적 지식을 읽을 위치
- 자기가 쓸 세션 폴더
- 공식 검사 스크립트를 실행하는 방법
- 검토 세션이면 검토 대상: 연구 산출의 검토라면 축적 지식에서 그 산출을 식별하는 정보, 목표 검토라면 목표 검토라는 사실

모델과 노력 수준은 계획이 그 세션에 따로 지정한 값이 있으면 그 값을, 없으면 범주의 기본값을 쓴다. 계획 세션이 따로 지정할 수 있는 세션은 계획 세션이 게시한 과제를 수행하는 연구 세션과, 계획 세션이 요청한 검토 세션이다. 자동으로 붙는 검토와 계획 세션 자신은 범주의 기본값을 쓴다. 검토 세션에는 대상 결과를 쓴 세션의 세션 폴더 위치를 주지 않는다.

구체 형식: `protocol.md` 2절 및 `check.py:Checker.check_input`. 세션 폴더의 `input.json`에 `instance` 절대 경로, `category`(`plan|research|review`), `context.common` 절대 파일 목록, `context.category` 절대 파일, `task` 객체를 둔다. 작업특정요소는 `task` 자체이며 공통으로 `instructions`와 `references`를 가진다. 연구는 `supersedes`, 검토는 `target`, 계획은 `events`를 추가한다. 목표·조건과 맥락 파일들은 존재해야 한다. 기동 프롬프트는 자기 세션 폴더·input.json·공식 검사 명령을 알려 준다.

수용된 작업맥락의 경로는 `<skill>/common.md`, `<skill>/plan.md`, `<skill>/research.md`, `<skill>/review.md`다. 실행기는 common 목록에 common.md, protocol.md, 인스턴스 goal.md를 넣고 category에 해당 범주 문서를 연결한다. 이 경로 선택은 구현 배정이며 사용자가 정한 파일명은 아니다. 세션은 input.json에서 시작해 공통요소·자기 범주·task를 읽고 공개 knowledge를 따라 판단하며 자기 output/에 산출을 남긴다.

- `common.md`의 ‘자기 작업을 찾기’, ‘공개 지식을 읽는 판단’, ‘기록하고 제출하기’: 세 층의 의미, 현재 대체 본문·상충 검토, 자기 폴더 쓰기, 공개 자료의 완결성과 공식 검사·반영을 연결한다.
- `plan.md`의 ‘이번 사건과 현재 연구를 읽기’, ‘다음 과제를 정하기’, ‘판단과 요청을 게시하기’: 네 사건을 해석하고 실패·부분 결과를 다음 요청에 사용하며, 동시 대체와 중복 배정을 피한다. 기존 과제 결과를 기다리는 것과 사용자 입력이 필요한 wait를 구분한다.
- `research.md`의 ‘사람이 읽는 해설과 근거 만들기’, ‘다음 세션에 결과 전달하기’: 정의·조건·논증·확인 범위를 공개하고 설정의 Lean 명령·판본을 실제 사용하며, 실패·질문과 전체 대체 산출을 남긴다.
- `review.md`의 ‘대상을 정하고 공개 기록 읽기’부터 ‘검토 기록 제출하기’: 연구 전체의 모든 결과, 실패·질문을 공개 자료에서 읽고 자기 사본에서 Lean을 재컴파일한다. 주장 근거·Lean 수용·해설 일치와 목표 판정을 구분하고 원문 중요 내용의 누락과 산출의 정확성을 양방향으로 판단한다.

계획의 미완료 요청 읽기는 `Runner.dispatch`의 계획 전용 프롬프트가 `RUNTIME.md`와 `<instance>/runner/state.json`을 연결한다. requests의 `pending`·`assigned`가 미완료 요청이며 category/task/origin/selection/status/session/record로 지시·대체 의도·진행 상태를 읽는다. 요청 키는 `<공개계획ID>:research:<인덱스>`, `:reviews:<인덱스>`, `:goal_review`이고 자동 검토는 `<연구ID>:automatic_review`다. 선택 이유는 origin의 공개 계획에서 읽으며 자동 검토의 origin은 연구 기록이다. 실패 사건의 session을 sessions에서 찾아 request→requests.task/origin으로 원 요청을 읽는다. request가 null인 실패 계획은 해당 session의 input.json.task.events에서 원 사건을 회수한다. `skill-entry`에서 plan.md와 RUNTIME.md에 이 경로를 명시했다. 검토 입력에는 이 실행 상태 경로나 작성자 폴더·로그를 넣지 않는다. 정적 연결과 가짜 입력 전달에 더해 mixed-completion의 정상 계획·연구·검토 수행을 확인했다. 실제 실패 사건의 환류까지 실행한 근거는 아니다.

`task.target`은 연구 전체에 대한 `{"kind":"research","record":"<ID>"}` 또는 인스턴스 전체에 대한 `{"kind":"goal"}`다. 자동 검토는 대상과 기본 지시, 추가 검토는 계획의 지시와 참조도 받는다. 검토 기동·입력에는 작성자 세션 폴더를 넣지 않는다. 계획 요청의 model/effort는 지정된 필드만 범주 기본값을 덮어쓰고 하나라도 지정하면 selection_reason이 필요하다. 계획 자신과 자동 검토는 범주 기본값을 쓴다.

## 3. 세션 → 실행기: 산출과 종료

세션은 자기 세션 폴더에만 쓴다. 산출은 범주별로 정해진 분류 형식을 따른다. 세션이 끝났는지는 프로세스가 끝났는지로 판정한다. 세션이 따로 "끝났음"을 알리는 신호는 필요하지 않다.

범주마다 산출이 담아야 할 의미는 다음과 같다.

- **연구**: 결과(해설, 실제 확인 범위, 해당하면 Lean 원문과 `lean --version` 문자열), 실패한 시도와 그 범위, 남은 질문, 사용한 축적 지식의 참조.
- **검토**: 대상 산출 안의 결과마다의 판단과 그 근거. 목표 검토라면 목표 달성 여부의 판정과 그 근거. 실행기가 "달성"을 기계적으로 읽을 수 있는 판정 값이 있어야 한다.
- **계획**: 아래 5절의 게시 내용과, 판단의 이유.

구체 형식: `protocol.md` 3~6절. 세션은 `output/output.json`과 거기에 연결된 공개 파일을 작성한다. 모든 산출은 `category`, `references`, `supersedes`를 가진다. JSON은 UTF-8(BOM 허용), 모르는 추가 필드는 무시한다. 전달 ID는 영문·숫자로 시작하며 영문·숫자·`_`·`-`로 구성한다. 공개 파일 경로는 output 기준 `/` 구분 상대 경로이며 절대 경로·`..`·파일시스템 링크를 쓰지 않는다. Markdown과 웹 인용의 실제 사용 가능성은 세션이 확인한다.

- 연구(`Checker.research`): `results[{id, exposition, verification, lean}]`, `failed_attempts[{description, verification}]`, `open_questions` 문자열 목록. 결과가 없어도 된다. exposition은 공개 해설 파일이며 lean은 null 또는 `{sources:[공개 원문 경로],version:실제 판본 문자열}`다. verification에는 직접 확인한 범위와 한계를 적는다.
- 연구 검토(`Checker.review`): 입력과 일치하는 `target`, 원 연구의 각 결과 ID를 정확히 한 번 다루는 `results`, `summary`. 각 결과는 result ID와 assessment/lean/alignment를 갖고 판단마다 verdict와 reason을 둔다. assessment는 supported/not_supported/undetermined, lean은 accepted/rejected/not_checked/not_applicable, alignment는 matches/differs/not_checked/not_applicable이다. 결과가 없는 연구도 빈 results와 summary로 검토한다.
- 목표 검토(`Checker.review`): goal target, `goal:{verdict,reason}`을 둔다. verdict는 achieved/not_achieved/undetermined다. **재검사·반영된 목표 검토의 achieved만** 실행기의 완료 신호다.
- 계획은 다음 5절의 게시 필드와 reason을 갖는다. 별도 승인·종료 신호는 없다.

## 4. 공식 검사 스크립트

세션과 실행기가 같은 스크립트를 같은 방식으로 실행한다. 입력은 세션 폴더 하나다. 출력은 통과 여부이고, 통과하지 못하면 그 이유를 세션이 고칠 수 있게 알려 준다. 검사 범위는 두 가지다. 범주별 형식의 필수 파일과 항목이 갖춰졌는지, 그리고 산출이 가리키는 축적 지식의 기록과 파일이 실제로 있는지다. Lean 컴파일과 내용의 정확성은 검사하지 않는다.

구체 형식: `python <skill>/check.py <session-dir>`. `check.py:main`이 성공 종료 0, 형식·참조 실패 1, 명령 인자 오류 2를 반환한다. 정상 호출 stdout은 `{"ok":bool,"errors":[첫 오류 위치와 이유]}`이며 통과 시 errors는 빈 목록이다. 파일을 쓰지 않는다. Python `check_session(str|Path) -> list[str]`도 같은 `Checker.run`을 사용하며 통과 시 [], 실패 시 첫 진단 하나를 돌려준다. 예상 파일·JSON·인코딩 오류는 진단으로 돌아오고 프로그래밍 오류는 전파된다.

`Checker.check_input/plan/research/review`가 필수 구조·입출력 범주와 검토 대상·결과 항목을 검사하고 `references/supersedes/target/local_file`이 실제 기록·파일·결과 참조를 확인한다. 기존 기록 전체의 재귀 검사나 현재성·Lean·수학적 타당성 판단은 하지 않는다. 공개 output 전체의 파일시스템 링크도 거부해 작성자 작업 폴더에 대한 의존이 그대로 복사되지 않게 한다. Markdown/웹 인용의 의미와 참조 누락 여부는 검사 대상이 아니다. 작은 확인 코드는 `tests/test_check.py:HandoffTests`다.

## 5. 계획 → 실행기: 게시

계획 세션의 산출에서 실행기가 읽는 것은 다음과 같다.

- **연구 과제의 게시**: 과제마다 연구 세션의 작업특정요소가 될 지시. 필요하면 그 과제의 모델·노력 수준과 지정 이유가 붙는다.
- **추가 검토 요청**: 이미 반영된 연구 산출에 검토를 더 붙이는 요청. 요청 내용이 그 검토 세션의 작업특정요소에 더해진다. 필요하면 그 검토의 모델·노력 수준과 지정 이유가 붙는다.
- **목표 검토 요청**: 필요하면 모델·노력 수준과 지정 이유가 붙는다.
- **외부 입력 대기 선언**: 사용자에게 필요한 것과 그 이유.

계획 세션이 받는 작업특정요소는 아직 어느 계획 세션에도 넘기지 않은 사건 전부다. 계획 세션이 도는 동안 생긴 사건은 다음 계획 세션에 넘긴다. 사건은 네 종류다. 끝난 검토(재검사를 통과해 반영된 검토 산출), 실패한 세션(검토 세션을 포함해 산출 없이 끝났거나 실행기의 재검사를 통과하지 못한 세션), 들어온 사용자 입력, 그리고 첫 계획이라면 시작 사건이다. 연구 세션이 정상으로 끝난 것은 계획의 사건이 아니다. 그 산출이 반영되면 실행기가 먼저 검토를 띄우고, 그 검토가 끝나면 끝난 검토로서 계획에 넘어간다.

구체 형식: `protocol.md` 6절, `check.py:Checker.plan/request`. output의 `reason`, `research`, `reviews`, `goal_review`, `wait`가 필수다. research와 reviews는 배열, goal_review와 wait는 부재 시 null이다. 연구 요청은 instructions/references/supersedes, 추가 검토 요청은 instructions/references/research target, 목표 검토 요청은 instructions/references를 갖고 실행기가 goal target을 붙인다. 각 요청의 선택 model/effort와 selection_reason은 2절의 의미를 따른다. 요청은 계획 기록 ID+배열명+인덱스로 식별해 한 번 파견할 수 있다. 후속 계획의 빈 목록은 앞선 게시를 취소하지 않는다. 실패한 요청을 재시도하려면 새 계획이 새 요청을 낸다.

wait는 `{needed,reason}`이다. 요청과 함께 있으면 요청은 게시되지만 사용자 입력이 올 때까지 새 파견은 대기한다. 기존 세션은 계속 종료·반영 처리한다.

계획 input의 `task.events`는 start, review_finished(record: 반영된 검토 ID), session_failed(session: 세션 ID, reason: 실패 설명), user_input(text: 입력 원문)의 목록이다(`Checker.check_input`). 아직 전달하지 않은 사건 전부를 시작 시 한 계획에 주고 실행 중 도착분은 다음 계획에 준다. 정상 연구 반영은 계획 사건으로 만들지 않고 자동 검토로 연결한다.

## 6. 실행기 → 축적 지식: 반영

세션은 끝나기 전에 4절의 스크립트로 자기 산출을 검사한다. 세션이 끝나면 실행기가 같은 스크립트를 그 세션 폴더에 다시 돌린다. 이것이 재검사다. 실행기는 재검사를 통과한 세션 산출을 축적 지식에 새 파일로 복사해 두고 Git 커밋을 남긴다. 세션 폴더는 그 세션의 기록으로 그대로 남는다. 기존 파일은 덮어쓰지 않는다. 연구 산출의 검토는 대상인 연구 산출과 연결해 둔다. 목표 검토의 산출은 특정 연구 산출이 아니라 연구 인스턴스 전체에 대한 판정으로 둔다. 기존 기록을 대신하는 새 기록은 무엇을 대신하는지 밝히고 아래 대체 규칙으로 현재 본문과 이력을 읽는다.

구체 형식: `protocol.md` 3·7절. 종료 방식·코드와 관계없이 공식 재검사를 하고 통과한 `sessions/<ID>/output/`의 **전체 내용**을 새 `knowledge/<record>/`로 복사한다. output.json과 상대 경로를 그대로 보존하고 input/work/log는 복사하지 않는다. 인스턴스 Git에 반영마다 커밋하며 기존 기록을 덮어쓰지 않는다. 세션 폴더는 기록으로 남는다. `Runner.finish`가 공식 `check_session` 재검사, 새 기록 ID 저장, runner/stage-<ID>에 전체 복사 후 공개 위치로 rename, 인스턴스 Git 커밋을 처리한다. 이미 공개·커밋된 기록은 재기동 시 이어 처리한다. `apply_output`의 후속 요청·사건과 세션 완료를 함께 원자 저장한다. 가짜 프로세스와 임시 Git으로 반영·복구를 확인했고, mixed-completion에서 실제 모델 산출 다섯 건의 공개·Git 반영까지 확인했다.

`runner.py:write_json(path, value)`는 임시 파일을 쓰고 flush/fsync한 뒤 os.replace로 완전한 JSON을 교체한다. mixed-completion 수정은 Windows OSError의 winerror 5/32/33에만 같은 교체를 50ms 간격으로 최대 1초 재시도한다. 기존 상태는 교체 성공까지 유지하며 지속 거부와 다른 오류는 전파한다. 호출 계약·상태 형식·세션 시간 제한은 바뀌지 않는다. 운영 설명은 RUNTIME.md의 반영·복구 부분, 실제 열린 파일과 지속 거부 확인은 tests/test_state_write.py다.

지식 참조는 `{record, file?, result?}`다. record는 해당 knowledge 폴더의 output.json, file은 그 기록 안의 실제 파일, result는 연구 results[].id를 가리킨다. 공개 해설에서 사용한 기존 지식도 references에 적는다. 검토는 target으로 원 연구 전체와 연결된다.

`supersedes`는 기존 기록 전체를 대신할 ID 목록이다. A를 B가 대신하면 본문은 B에서, 이력·근거는 A에서 읽고 대체 사슬의 끝을 현재 본문으로 삼는다. 부분 수정도 유지할 내용까지 담은 전체 산출을 낸다. 가지가 갈라지면 어느 쪽도 자동 선택하지 않고 다음 계획이 판단한다. 과제의 대체 의도와 실제 산출의 대체 선언이 같아야 한다고 검사하지 않는다. 구 검토는 새 연구로 자동 승계되지 않으며 검토 자체가 대체되면 그 이력을 따라 읽는다. 새 연구는 검토 전에는 주장이고 현재 검토가 상충하면 인정된 결과로 쓰지 않는다. 동시 대체 과제를 피하는 책임은 계획에 있고 실행기에 충돌 판정을 추가하지 않는다.

## 7. 사용자 ↔ 실행기

사용자 대화가 할 수 있어야 하는 일은 다음과 같다. 각 일은 인스턴스 폴더나 명령을 통해 이루어진다.

- 새 인스턴스를 만들고 실행기를 독립 프로세스로 띄운다.
- 진행 상황을 읽는다.
- 정지 표시를 놓거나 거둔다.
- 입력을 넣는다.
- 끝나지 않고 멈춰 버린 세션 하나의 프로세스를 끝낸다. 정지 표시와는 별개다.
- 실행기를 다시 띄운다.

사용자 대화의 진입점은 `.claude/skills/do-math/SKILL.md`다. 목표·설정 준비→자체 Git 인스턴스 init→독립 start→새 시작 로그와 status 확인→위치 반환 순서를 제공한다. 공개 결과는 knowledge/<기록>/output.json에서 해설과 연구 검토를 읽고, state.complete가 가리키는 목표 검토에서 달성 근거를 읽는다. STOP·입력·한도·완료의 각 조건 및 꺼진 실행기에 start가 필요한 경우도 본문에 있다. 구체 명령 정의는 같은 폴더의 `runner.py`와 `RUNTIME.md`가 제공한다. 명령은 `python <skill>/runner.py <명령> <instance>`이며 성공은 종료 0/stdout JSON, 실행 오류는 1/stderr `{"error":"설명"}`, 인자 오류는 2다. `run`은 시작 JSON 뒤 실행을 계속한다.

| 명령 | 입력과 동작 |
|---|---|
| `init INSTANCE --goal FILE --settings FILE` | 아직 없는 인스턴스에 목표·설정 원문, 폴더와 자체 Git을 만든다. `initialize/load_settings`가 담당한다. 설정은 실행기 기동 시 읽으며 Lean은 세션이 사용한다. |
| `start INSTANCE` | 독립 기동·재기동. 새 token의 시작 로그와 PID+생성 식별값을 확인해 pid/stdout/stderr/instance를 반환한다. Windows는 무창 detached 프로세스다. 10초 확인 실패는 자식 종료를 뜻하지 않으므로 로그·status를 먼저 읽는다. |
| `status INSTANCE` | `runner_alive`, `knowledge`, `dispatch_blocks`, 전체 `state`를 읽기 전용으로 반환한다. 죽은 실행기의 세션 상태는 마지막 저장 시점이며 재기동 때 생존을 확인한다. |
| `stop INSTANCE` / `resume INSTANCE` | STOP 생성/제거. 새 파견만 막으며 이미 시작한 세션의 종료·반영을 막지 않는다. resume은 실행기를 기동하지 않는다. |
| `input INSTANCE --file FILE` | 비어 있지 않은 UTF-8 원문 바이트를 고유 이름으로 control/inputs에 복사한다. 실행기가 다음 계획 사건으로 소비하고 외부 입력 대기를 푼다. 실행기가 꺼져 있으면 start가 필요하다. |
| `kill-session INSTANCE SESSION_ID` | 최신 process.json의 PID+OS 생성 식별값을 같은 OS 핸들로 확인해 해당 CLI 하나를 종료한다. 별도 자손 전체 종료가 아니다. 남은 산출은 일반 종료와 같은 재검사로 판단한다. |

`Runner.run/InstanceLock`이 단일 실행기를 유지한다. 세션 호스트 `session_host`는 한 번 기동한 CLI의 핸들을 보유하고 process.json/exit.json을 남긴다. AI 역할·자동 재기동 서비스가 아니다. 배정·사건 소비를 저장하고 호스트 식별값 저장 뒤 GO로 시작을 허용한다. 재기동의 `collect`는 호스트와 CLI가 살아 있으면 기다리고 죽었으면 `finish`로 검사한다. 이미 배정된 요청은 재파견하지 않는다. 생존 조회 권한 오류는 죽음으로 오인하지 않고 오류로 드러난다.

상태는 `<instance>/runner/state.json`이다. `requests`의 읽기 의미는 2절, 자세한 필드는 RUNTIME의 ‘계획이 읽을 미완료 요청과 사건’을 따른다. `sessions`는 category/request/model/effort/status와 프로세스·검사 결과를 담는다. 세션 상태는 starting/running/publishing/integrated/failed다. `events`는 아직 계획에 전달하지 않은 사건, `seen_inputs`는 소비한 사용자 파일명, `input_errors`는 소비 전 진단이다. 원문은 보존하고 파일 이름으로 소비를 추적한다. `wait`는 외부 입력 요구 또는 null, `limit_until`은 전체 파견 재개 UTC Unix 초, `complete`는 달성을 판정한 공개 목표 검토 ID 또는 null이다.

`Runner.tick`은 종료 처리와 입력 수집을 먼저 하고, STOP·wait·limit·complete 중 하나라도 있으면 파견하지 않는다. 한도·외부 입력 대기 중 실행기는 살아 있다. 빈 슬롯이 있으면 사건을 받을 단일 계획을 먼저 띄우고 남은 슬롯에 게시 순서대로 pending 요청을 보낸다. 계획 중 발생한 사건은 다음 계획에 남긴다. 오래된 계획의 wait는 아직 전달하지 않은 새 사용자 입력을 막지 않는다. 완료 후 기존 세션은 검사·반영하고 모두 끝나면 실행기가 종료한다.

manager는 이 명령·상태·기동 경로를 코드와 운영 본문에 대조했다. task의 가짜 흐름 6개 시험에는 Windows 독립 기동과 실제 Git 반영·복구가 포함된다. `skill-entry`의 사용자 진입 안내에 이어 mixed-completion은 init/start/status로 실제 두 CLI의 작은 Lean 목표를 무인 완주했다. RECORDS의 `tasks/mixed-completion/evidence.md`에서 공개 연구→연구 검토→목표 검토와 최종 상태·세션별 실행·Git 근거로 이어진다. complete는 `kc7325f0829e84ab5ab14fdfd5938ca33`이며 다섯 세션 모두 integrated·종료, runner_alive=false다. Linux·호스트 재부팅·실제 한도·장기 어려운 연구는 확인하지 않았다.

## 8. 실행기 ↔ CLI

실행기는 Codex CLI와 Claude CLI로 세션을 띄운다. 모델 이름에서 어느 CLI를 쓸지 정하는 규칙이 필요하다. 끝난 세션의 CLI 출력에서 실행기가 읽는 것은 공급자 사용 한도 신호 하나뿐이다. 신호가 있으면 해제 시각도 함께 읽는다. 각 CLI의 실제 기동 인자와 한도 신호의 모양은 실제 CLI로 확인해 여기에 기록한다.

제품 진입점은 `.claude/skills/do-math/CLI.md`, 실제 정의는 같은 폴더의 `cli_adapter.py`다. 현재 통합된 함수 계약은 다음과 같다.

- `provider_for_model(model) -> "codex"|"claude"`: 첫 `/` 앞의 명시적 공급자를 반환한다. `codex/<model>` 또는 `claude/<model>`만 받으며 뒤가 빈 문자열·공백뿐이면 ValueError다. bare 이름 추정·모델 allowlist는 없다. 모델 존재·접근 권한은 CLI가 판단한다.
- `build_command(cli_path, model, effort, cwd) -> Command(provider, argv, cwd)`: 호출자는 기본값과 요청 지정을 합친 최종 모델·노력, 공급자의 CLI 경로, 세션 작업 폴더를 준다. 첫 `/` 뒤 전체를 CLI 모델에 전달한다. 반환 cwd는 resolve된 Path이며 argv는 shell=False Popen에 그대로 준다. Codex 노력은 TOML 문자열로 전달하고 Claude는 low/medium/high/xhigh/max를 받는다. 빈 값·잘못된 모델 표기/Claude 노력은 ValueError다. 파일 존재·인증·모델 접근은 기동 때 드러난다.
- `detect_usage_limit(provider, stdout_path, stderr_path, *, now, fallback_seconds, session_started_at=None, local_timezone=None) -> UsageLimit|None`: 끝난 두 로그를 읽으며 now/시작 시각/반환 retry_at은 UTC Unix 초다. None은 지원하는 표식을 못 찾았다는 뜻이다. UsageLimit은 provider, retry_at, source(provider 또는 fallback)를 가진다. 미래 reset을 확정하지 못하면 now+양의 fallback_seconds를 쓴다. Codex 시간만 있는 메시지는 시작과 현재가 같은 호스트 로컬 날짜일 때만 해석하고 시작 미확인·자정 경계·DST 모호성에는 fallback을 쓴다. 표시된 분의 시작을 쓰므로 실제 reset의 초보다 최대 59초 빠를 수 있다. local_timezone=None은 호스트 로컬 시간대다.
- Claude는 최상위 type=assistant/is_api_error_message=true/api_error=usage_limit_reached만 계정 거절로 읽는다. 일반 창의 resetsAt, 의미가 확인된 일반 overage 거절의 두 reset 중 최솟값을 사용한다. scope/disabled reason 등 특수 분기나 잘못된 시간은 fallback이다. rate_limit_event 보조 탐지는 채택하지 않았다. 여러 실제 거절의 최종 만료는 각각의 만료 중 최댓값이다.
- 잘못된 호출 설정은 ValueError이며 파일 부재/읽기 오류는 OSError로 전파한다. 실행기는 로그 읽기 오류를 기록하고 공식 산출 재검사를 계속한다. 잘못된 UTF-8은 대체하고 불완전 JSON·일반 출력·모르는 값은 건너뛴다. 중복 키는 json.loads의 마지막 값을 사용한다. 로그 형식이나 CLI 종료 코드는 산출 승인 조건이 아니다.

실행기는 Command.argv/cwd와 UTF-8 stdin·stdout/stderr 파일, CLI 프로세스 핸들·PID·시작 시각을 연결한다. 어댑터는 대기·산출 승인·세션 재시작을 수행하지 않는다. 한도 반환은 모든 새 파견의 대기 만료에만 적용하며 정지·외부 입력 대기·완료 상태는 별도로 유지한다. 사용 예와 세부 오류 의미는 CLI.md 본문에 있다. cli-adapter task의 합성 로그 8개 시험에 더해 runner가 공급자 접두 argv 확인을 같은 시험에 반영하고 8개 통과를 보고했다. manager는 변경 코드·시험·조사 근거를 정적으로 대조했다. 실제 모델·실측 한도는 이 수용으로 확인된 것이 아니다.

수용된 조사 진입점은 RECORDS의 `tasks/cli-discovery/cli-evidence.md`다. 같은 디렉터리의 아래 근거까지 따라 읽을 수 있다. 이는 기동 옵션과 구현상의 출력 경로를 확인한 것이며 실제 모델 요청이나 실측 한도 로그가 아니다.

- Codex `exec`는 stdin(`-`), `--cd`, `--model`, `-c model_reasoning_effort=...`, `-c approval_policy=...`, `--sandbox`, `--ephemeral`, `--json`을 지원한다. Claude `--print`는 stdin, 프로세스 cwd, `--model`, `--effort`, `--dangerously-skip-permissions`, `--permission-prompts none`, `--no-session-persistence`, `--output-format stream-json --verbose`로 기동할 수 있다. 근거는 `codex-exec-help.txt`, `claude-help.txt`와 `cli-evidence.md` 1절이다. resume/continue 없이 매번 새 프로세스를 사용한다. Claude `--bare`는 OAuth를 읽지 않아 현재 구독 로그인 예에 쓰지 않았다.
- Codex 오류 이벤트는 `type=error`의 `message`, 또는 `type=turn.failed`의 `error.message`다. `upstream-exec_events.rs:ThreadErrorEvent`는 메시지만 가진다. `upstream-error.rs:UsageLimitReachedError`의 Display 구현에 usage limit, workspace credits, spend cap 문구가 있고 `format_retry_timestamp`는 로컬 시각을 출력한다. 같은 날은 시간만, 다른 날은 영문 월·서수 일자·연도까지 나온다. exec 출력에 숫자 resetsAt이 있다고 가정하지 않는다. 날짜를 확정할 수 없거나 유효한 미래 시각이 없으면 설정된 대기 간격으로 처리한다.
- Claude assistant 레코드의 최상위 `is_api_error_message=true`, `api_error=usage_limit_reached`는 계정 한도 거절 표식이다. `api_error_params.rate_limit_info`의 `resetsAt`·`overageResetsAt`은 Unix 초다. `claude-semantic-excerpts.txt`, `claude-assistant-shape.txt`, `claude-limit-details.txt`의 schema·출력 생성 코드가 근거다. `rate_limit_event`는 정상·경고도 포함하므로 이벤트 존재 자체를 차단으로 읽지 않는다. 일반 `error=rate_limit`이나 429만으로도 부족하다. overage 이용 가능성과 복수 reset의 의미는 `cli-evidence.md` 3절 및 `claude-overage-rendering.txt`를 따른다. 보조 신호의 채택 범위는 어댑터 구현에서 근거에 맞게 정한다.
- 로그는 한도 신호만 읽는다. JSON이 아닌 줄, 모르는 필드, 중복 키를 이유로 산출을 거부하지 않는다. 정상 답변이나 도구가 인용한 한도 문구도 공급자 거절로 취급하지 않는다. 종료 상태와 산출 재검사는 별개이며 CLI 종료 코드와 관계없이 공식 검사로 산출을 판단한다.
- argv 목록, `shell=False`, UTF-8 stdin 파일, stdout/stderr 파일을 사용하면 셸 재인용과 출력 PIPE 대기를 피할 수 있다. 세션 종료는 CLI 프로세스 핸들로 판단한다. 실행기 독립 기동의 Windows 예와 작은 확인은 `cli-evidence.md` 5절 및 `detach-probe*`에 있다. 호출 Python이 끝난 뒤 자식이 완료 파일을 남긴 사실만 확인했으며 외부 job-object 종료·재부팅 뒤 생존을 보장하는 근거는 아니다.

무인 권한 옵션은 OS 수준의 쓰기 격리가 아니다. 자기 세션 폴더만 쓴다는 지시를 작업맥락에 담는다. 실제 모델 접근·파일 산출은 mixed-completion에서 Codex gpt-6.1-sol/high 세 세션과 Claude sonnet/high 두 세션으로 확인했다. Claude init이 보고한 실제 모델은 claude-sonnet-5-5다. 기본값 선택과 접두를 제거한 실제 argv가 기록돼 있으며 모든 가능한 설정 조합의 검증은 아니다. 한도 탐지는 근거 기반 합성 입력의 확인 범위이며 실제 한도는 발생하지 않았다. Claude typed 필드가 internal인 점, Codex 날짜 생략과 다중 overage 시각의 불확실성은 구현·운영 안내에도 유지한다. 이 조사로 환경 고정이나 출력 전체의 형식 검사를 추가하지 않는다.
