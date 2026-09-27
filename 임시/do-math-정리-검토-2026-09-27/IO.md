# do-math 정리 검토: IO 영역 (외부 프로세스·제어·관찰)

이 문서는 `기준.md` 8절 형식에 따른 IO 영역 검토 결과다. 검토 기준 시점은 main `9b434f4`의 작업 트리이고, 작업 트리에 변경은 없다. 경로는 `C:/math/.claude/skills/do-math/` 기준의 상대 경로로 적는다. `scripts/do_math/`는 `do_math/`로, `scripts/tests/`는 `tests/`로 줄인다.

## 1. 읽은 범위

전문을 읽은 파일은 다음과 같다.

| 파일 | 행 수 |
|---|---|
| `do_math/claude_adapter.py` | 55 |
| `do_math/claude_stream.py` | 177 |
| `do_math/claude_worker.py` | 86 |
| `do_math/codex_adapter.py` | 352 |
| `do_math/codex_worker.py` | 188 |
| `do_math/model_runner.py` | 373 |
| `do_math/cli.py` | 687 |
| `do_math/control_transport.py` | 594 |
| `do_math/control_contracts.py` | 202 |
| `do_math/observation_transport.py` | 42 |
| `do_math/observations.py` | 1160 |
| `do_math/operation_trace.py` | 289 |
| `C:/math/임시/do-math-정리-검토-2026-09-27/기준.md` | 238 |
| `AGENTS.md` | 11 |
| `C:/math/docs/do-math/검사-경량화-이음새-계약.md` | 245 |
| `C:/math/임시/경량화-조사-2026-09-26/IO.md` | 453 |
| `C:/math/임시/경량화-조사-2026-09-26/결과-E.md` | 132 |
| `C:/math/기억/layer1/M-0349.md`, `M-0350.md` | 64, 101 |

세 커밋의 영역 변경은 다음 범위를 읽었다.

- `9b434f4`: 영역에서 바뀐 파일은 `operation_trace.py` 하나이며, 그 diff 전문을 읽었다.
- `8d2ffd0`: `claude_adapter.py`, `cli.py`, `control_transport.py`, `model_runner.py`의 diff를 읽었다. 나머지 영역 파일은 `--stat`으로 변경 규모만 확인했다.
- `379a171`: `cli.py`, `claude_adapter.py`, `control_contracts.py`의 변경 행을 읽었다. 나머지 영역 파일은 현재 원문 전문과 `결과-E.md`의 ID별 처분으로 대신했다.

이음새를 따라 일부만 읽은 파일은 다음과 같다.

| 파일 | 읽은 행 |
|---|---|
| `do_math/engine.py` | 60-82, 505-520, 880-892, 1081-1125, 1229-1245, 1650-1670, 2570-2595, 2776-2900, 3170-3183, 3395-3420 |
| `do_math/submission.py` | 237-240, 1122-1142 |
| `do_math/scheduled_operator.py` | 575-595 |
| `do_math/parallel.py` | 70-100 |
| `do_math/file_io.py` | 212-217 |
| `scripts/probe_cli.py` | 55-70 |
| `tests/test_codex_adapter.py` | 120-135, 172-208 |
| `tests/test_redesign_PROFILES.py` | 168-185, 250-262, 560-583, 848-870, 985-1010 |
| `tests/test_claude_adapter.py` | 100-112 |
| `기억/layer1/M-0348.md` | 영역 관련 행만 grep |
| `references/CLI-실행-계약.md` | 48, 954, 956 |
| `references/공통-실행.md` | 128, 169, 172 |

검토하지 못한 종류는 없다.

## 2. 영역 판정

IO 영역은 2라운드를 거친 뒤 방향성에 대체로 맞는다. 제어 어휘, 바인딩 모양, 자기 점검 응답 스키마, worker 공통 요청 검사, 공급자→어댑터 표가 각각 정본 하나로 모였고, 생산자와 수신자가 그 이름을 참조한다. 가장 큰 개선 여지는 두 가지다. 첫째, 공급자 중립 골격이 여전히 Codex 이름과 러너 하위 클래스 계층에 묶여 있다. 2라운드가 어댑터 층에서 푼 문제(IO-17)를 러너·worker·실행 기록 층에 적용하면, 러너 세 클래스를 어댑터 표 기반 하나로 줄일 수 있다(IO-01). 둘째, 제어 전송이 인스턴스 이력 전체에 비례하는 조회를 한다. 새 요청마다 모든 전송 디렉터리를 glob하고, 엔진을 만들 때마다 모든 전송의 `state.json`을 읽는다(IO-02, IO-03). M-0349가 남긴 스키마 키워드 공백은 범위가 좁혀진다. 엔진 실행은 늘 제어 바인딩을 받으므로 역할 응답 스키마는 공급자 CLI에 가지 않는다. 제품 운영에서 CLI에 닿는 경로는 MCP 도구 `inputSchema`와 수리 보고 스키마 둘이며, 둘 다 아직 실측되지 않았다(IO-12). 진단 스크립트 `probe_cli.py`의 스키마도 CLI에 가지만 운영 경로는 아니다.

검토했고 없음: 불일관, 파생상태, 문서, 결함, 임시방편, 잔재, 비대, 낡음

## 3. 후보

후보는 무게 순서로 배열했다. IO-01~IO-03과 IO-12가 이 영역의 중심이다.

#### IO-01 공급자 중립 골격이 Codex 이름의 클래스·모듈에 남아 있다

- 검토: 1
- 종류: 경계
- 좌표: `do_math/model_runner.py:23-33`, `do_math/model_runner.py:276-302`, `do_math/codex_worker.py:1-5`, `do_math/codex_worker.py:27-32`, `do_math/claude_worker.py:14`, `do_math/claude_worker.py:26`, `do_math/codex_adapter.py:1-6`, `do_math/codex_adapter.py:31-48`, `do_math/claude_adapter.py:28-29`
- 현상: 두 공급자가 함께 쓰는 골격이 세 층에서 Codex 이름을 달고 있다.
  - 러너 층: `ClaudeModelRunner`가 `CodexModelRunner`를 상속한다. 두 클래스의 차이는 생성자의 공급자 이름과 `worker_options`의 반환값뿐이다(`model_runner.py:24-33`, `model_runner.py:279-285`). 여기에 `ModelRunner`가 모델 이름으로 공급자를 골라 두 러너 중 하나에 넘긴다(`model_runner.py:288-302`). 공급자 이름에서 어댑터를 얻는 정본 `ADAPTERS`·`provider_adapter`(`claude_adapter.py:40-47`)가 이미 있는데도, 러너 층은 공급자마다 하위 클래스를 따로 둔다.
  - worker 층: 두 worker가 공유하는 요청 검사와 실행 골격(`check_common_request`, `run_cli`, `STATUS_BINDING_KEYS`)이 `codex_worker.py`에 있다. 그래서 Claude worker가 `codex_worker`를 import하고(`claude_worker.py:14`), 환경 허용 목록도 Codex 목록에서 `CODEX_HOME`을 빼는 식으로 만든다(`claude_worker.py:26`). Claude 어댑터의 식별 모듈에도 `codex_worker`가 들어간다(`claude_adapter.py:28`). 공통 골격을 고치는 변경과 Codex 인자를 고치는 변경이 같은 파일에 모인다.
  - 실행 기록 층: 두 공급자가 모두 쓰는 실행 기록의 이름이 `CodexExecution`이고(`codex_adapter.py:31`), 공유 기반 `LocalCLIAdapter`가 있는 모듈의 docstring은 "`codex exec`용 어댑터"라고 적는다(`codex_adapter.py:1-6`).
- 근거: 2라운드 IO-17은 같은 문제를 어댑터 층에서만 풀었다(`결과-E.md` 1절 IO-17). 2라운드 IO-06은 공통 모듈의 이름을 통합자 결정으로 남겼고, 결과 파일은 "공통 모듈의 이름은 바꾸지 않았다"고 적는다(`결과-E.md` IO-06 행). 러너 클래스를 참조하는 곳은 grep `CodexModelRunner|ClaudeModelRunner`로 찾았다. 제품에서는 `model_runner.py` 밖에 0건이고, 시험에서는 6개 파일 42건이다.
- 제안: 가장 큰 실익은 러너 층에 있다.
  1. 공급자별 worker 요청 필드를 어댑터 속성으로 옮긴다. 대상은 Codex의 `sandbox`·`approval_policy`·`windows_sandbox`·`final_path`와 Claude의 실행 파일 키다(`LocalCLIAdapter.worker_options(evidence_dir)`).
  2. 러너를 한 클래스로 둔다. 이 클래스는 `run(model=...)`에서 `provider_adapter(provider_for(model))`로 어댑터를 고른다. `claude:` 접두 제거도 이 한 곳에서 한다. 지금은 `model_runner.py:60`과 `model_runner.py:297`, 두 곳에 있다.
  3. worker 공통 골격은 중립 이름의 새 모듈로 옮기거나, `codex_worker.py` 모듈 자체를 중립 이름으로 바꾸고 Codex 전용 부분(`load_request`, `build_argv`)을 떼어 낸다. 어느 쪽이든 `identity_modules`의 모듈 이름이 바뀐다.
  4. `CodexExecution`의 이름을 중립 이름으로 바꾼다.
- 실익: 러너 층에서 약 20행과 클래스 둘이 사라진다. 공급자를 하나 더할 때 고칠 곳이 어댑터와 worker 둘로 준다. 지금은 러너 하위 클래스와 `ModelRunner` 분기도 고쳐야 한다. worker 층은 공통 골격을 고치는 변경과 Codex 인자를 고치는 변경이 서로 다른 파일로 갈린다.
- 비용과 위험: 새 상태·수명·복구 규칙은 없다. 시험 6개 파일 42곳이 러너 클래스를 직접 만들거나 `_adapter`를 바꿔 끼운다(예: `tests/test_redesign_PROFILES.py:855-856`). worker 모듈 이름을 바꾸면 `identity_modules`가 바뀌므로, 적용 뒤 첫 확인에서 기존 능력 증거가 한 번 무효가 된다(2라운드 IO-08과 같은 성질). Job 안 직접 적재의 import 경로도 함께 바뀐다.
- 기능·커버리지 영향: 없음(동작 보존). 시험의 생성 방식만 바뀐다.
- 사용자 결정 관련: 없음
- 확신도: 추정. 구조와 중복은 원문으로 확인했다. 시험 42곳을 어댑터 교체 방식 하나로 옮길 수 있는지는 확인하지 않았다. 시험마다 러너 생성 방식을 대조하면 확정된다.

#### IO-02 새 제어 요청마다 인스턴스의 모든 전송 디렉터리를 훑는다

- 검토: 1
- 종류: 비용
- 좌표: `do_math/control_transport.py:221`, `do_math/control_transport.py:439`, `do_math/control_transport.py:480-488`, `do_math/engine.py:516`, `do_math/engine.py:1233-1234`
- 현상: `receive`는 요청을 받을 때마다 `_receipt(request_id)`로 이전 영수증을 찾는다(`control_transport.py:221`). `_receipt`는 메모리 dict `_receipts`에 없으면 `self.root.glob("*/outbox/" + request_id + ".json")`로 인스턴스의 모든 전송 디렉터리를 훑는다(`control_transport.py:487`). 새 요청의 ID는 정의상 아직 메모리에 없다. 따라서 새 요청은 하나도 빠짐없이 이 전수 조회를 거친다. 전송 디렉터리는 실행마다 하나씩 생기고 지워지지 않는다. grep `execution-control`의 제품 일치는 생성 지점 `engine.py:516` 1건뿐이며, 삭제하는 코드는 없다. 2라운드 IO-19는 `pump`의 전수 조회만 열린 전송으로 좁혔고, 이 glob은 바꾸지 않았다고 적었다(`결과-E.md` IO-19 행).
- 근거: 영수증의 키는 `request_id` 하나이고(`control_transport.py:439`), 전송 ID가 들어가지 않는다. 엔진 발행자도 같은 요청 ID를 인스턴스 전체의 `control_receipts`에서 선형으로 찾는다(`engine.py:1233-1234`). 요청 ID의 이름공간이 두 층 모두 인스턴스 전역이다.
- 제안: 이 후보의 범위는 transport의 조회 비용이다. 다른 실행 사이의 ID 충돌을 없애는 일은 엔진 조회도 바꿔야 하므로 별도의 엔진 영역 후보로 5절에 적었다. transport 영수증의 키를 `(transport_id, request_id)`로 바꾼다. 조회는 `root / transport_id / "outbox" / (request_id + ".json")` 하나를 직접 읽는다. 전송 ID는 요청의 필수 필드이며, `_validate_request`가 이미 파일 이름 규칙으로 검사한다(`control_transport.py:412-413`).
- 실익: 새 요청 하나의 조회 비용이 "인스턴스가 지금까지 연 전송 수에 비례하는 stat"에서 파일 하나의 읽기로 준다. 측정값은 없다. 추정 근거는 실행 수이며, 수백 실행 인스턴스라면 요청마다 수백 번의 stat이다.
- 비용과 위험: 새 상태·수명 규칙은 없고, 키 모양만 바뀐다. 다른 전송에서 같은 요청 ID를 다시 쓰는 경우의 처리 단계가 바뀐다. 지금은 transport가 `ValueError`("reused with different content")를 내고, 그 전달을 `delivery_validation` 거부 영수증으로 기록한다. 바꾼 뒤에는 엔진의 전역 조회가 `rejected`를 돌려준다(`engine.py:1235-1237`). 두 경우 모두 거부이므로 작업자가 보는 결과는 같고 거부 단계만 다르다. `tests/test_redesign_ENGINE.py:1329`는 `transport._receipts`를 직접 읽으므로 함께 고쳐야 한다.
- 기능·커버리지 영향: 있음. 전송 간 ID 재사용의 거부 단계와 사유 문구가 바뀐다.
- 사용자 결정 관련: 없음
- 확신도: 확인. 조회 경로와 키 모양은 원문으로 확인했다. 비용의 크기는 측정하지 않았다.
- 덧붙임(영역 밖과 이어짐): 안전 경계 요청의 ID는 작업자가 짓는다(`references/공통-실행.md:169-172`, 예시 `boundary-실제-고유-ID`). 이름공간이 인스턴스 전역이므로, 다른 실행이 우연히 같은 ID를 쓰면 뒤의 실행의 경계 보고가 거부된다. 문서는 "고유 ID"의 범위를 적지 않는다. 이 충돌을 없애려면 엔진 발행자의 조회(`engine.py:1233-1234`)도 전송 범위로 좁혀야 하므로, 5절에 엔진 영역 관찰로 적는다.

#### IO-03 엔진을 만들 때마다 모든 전송의 state.json을 읽는다

- 검토: 1
- 종류: 비용
- 좌표: `do_math/control_transport.py:129-134`, `do_math/control_transport.py:156-160`, `do_math/engine.py:510-516`, `do_math/cli.py:231`, `do_math/cli.py:331`, `do_math/cli.py:433`
- 현상: `ControlTransport.__init__`는 `root.glob("*/binding.json")`으로 모든 전송을 찾고, 전송마다 `_is_open`으로 `state.json`을 읽어 열린 전송 집합 `_open`을 채운다(`control_transport.py:159-160`). 엔진 생성자는 이 객체를 언제나 만든다(`engine.py:516`). 그래서 `pump`가 필요 없는 명령도 인스턴스의 전송 수만큼 파일을 읽는다. `status`(`cli.py:331`), `check`(`cli.py:433`), 제어 명령 뒤의 엔진 생성(`cli.py:231`)이 그런 명령이다. 이 스캔은 2라운드 IO-19가 들였다(`결과-E.md` IO-19 행). IO-19 이전에는 이 비용이 run 루프의 `pump`에만 있었다.
- 근거: grep `_open\b`는 제품에서 `control_transport.py`의 6건(129, 158, 160, 177, 259, 303)만 찾는다. 그중 129는 함수 `_is_open`이다. 집합 `_open`을 쓰는 곳은 생성자(158, 160), `issue`(177), `close`(303)이고, 읽는 곳은 `pump`(259) 하나다.
- 제안: 디스크 스캔을 첫 `pump` 때로 미룬다. `_open`을 `None`으로 시작하고, `pump`가 `None`을 만나면 그때 스캔한다. `issue`와 `close`는 집합이 이미 있을 때만 갱신한다. 스캔하지 않은 상태에서도, 뒤의 첫 `pump` 스캔이 디스크의 `binding.json`과 `state.json`으로 같은 집합을 얻는다.
- 실익: `status`·`check`처럼 펌프하지 않는 명령에서 전송 수만큼의 파일 읽기가 사라진다. 측정값은 없다. M-0350이 `status` 비용을 초 단위로 다룬 명령이라 실익이 드러나는 자리다.
- 비용과 위험: 기존 집합에 "아직 스캔하지 않음" 상태 하나가 더해진다. 무효화 규칙은 그대로다. 동작은 보존된다. 엔진 생성과 첫 `pump` 사이에 전송이 열리거나 닫히는 경우를 보자. 지금은 생성 때의 집합을 `issue`·`close`가 고쳐 반영한다. 미룬 뒤에는 첫 `pump`의 스캔이 그 시점의 디스크 상태로 반영한다. 어느 쪽이든 첫 `pump`가 읽는 전송은 같다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인. 호출 경로는 원문으로 확인했다. 비용의 크기는 측정하지 않았다.

#### IO-04 바인딩된 실행도 쓰이지 않는 출력 스키마 파일을 쓰고 Git에 보존한다

- 검토: 1
- 종류: 비용
- 좌표: `do_math/model_runner.py:86-88`, `do_math/model_runner.py:93-97`, `do_math/engine.py:3179-3181`, `do_math/engine.py:3413-3417`, `do_math/engine.py:1107-1113`
- 현상: 러너는 실행마다 `output.schema.json`을 증거 디렉터리에 쓴다(`model_runner.py:86-88`). 그러나 요청에 그 경로를 넣는 것은 제어 바인딩이 없을 때뿐이다(`model_runner.py:93-97`). 엔진은 모든 실행에 바인딩을 발급한다(`engine.py:3179-3181`, `engine.py:3417`). 따라서 엔진 실행에서는 이 파일을 공급자가 받지 않는다. 그런데 엔진은 증거 디렉터리 전체를 `provider-evidence/` 산출로 봉인해 Git에 넣는다(`engine.py:1107-1113`).
- 근거: 역할 응답 스키마의 직렬 크기를 `contracts.schema_for`로 쟀다(명령: `python -c "... contracts.schema_for(r) ..."`, 저장소 무변경). 10개 역할이 2,531~7,212바이트였다. grep `output.schema.json`의 일치는 `model_runner.py:86` 1건이다.
- 제안: 스키마 파일 쓰기를 `if control_binding is None:` 분기 안으로 옮긴다.
- 실익: 엔진 실행마다 파일 쓰기 하나와 봉인 산출 하나가 준다(스키마 2.5~7KB). 더 중요한 실익도 있다. 지금은 보존된 공급자 증거에 공급자가 받지 않은 스키마가 들어 있어, 증거를 읽는 사람이 CLI가 이 스키마를 강제했다고 오해할 수 있다. 제안 뒤에는 그 파일이 사라진다.
- 비용과 위험: 새 상태·수명 규칙은 없다. 보존 산출 목록에서 파일 하나가 빠진다. 스키마는 프롬프트에 이미 렌더링되어 있어(`context_store.py:638`) 입력 증거로 남는다.
- 기능·커버리지 영향: 있음. 엔진 실행의 `provider-evidence/`에서 `output.schema.json`이 빠진다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### IO-05 관찰 추적기의 생산자 없는 설정·필드와 쓰기만 하는 상태

- 검토: 1
- 종류: 미사용
- 좌표: `do_math/observations.py:79`, `do_math/observations.py:86`, `do_math/observations.py:251-252`, `do_math/observations.py:272-273`, `do_math/observations.py:451-452`, `do_math/observations.py:792`, `do_math/observations.py:807`, `do_math/observations.py:40`, `do_math/observations.py:1069`, `do_math/observations.py:1079`, `do_math/observations.py:465`, `do_math/observations.py:893`, `do_math/observations.py:927`, `do_math/observations.py:468`, `do_math/observations.py:957`
- 현상: 네 가지가 있다.
  1. 추적기는 설정 키 `observation_subjects`를 `allowed_subjects`로 읽어 규칙 검사에 넘긴다(`observations.py:451-452`, `observations.py:792`, `observations.py:807`). 이 키를 설정하는 코드는 없다. `tracker_config`(`observations.py:199-218`)도 넣지 않는다. 그래서 `validate_rules`와 `validate_rule_proposal`의 `allowed_subjects` 인자와 그 분기(`observations.py:272-273`)는 늘 `None`을 받는다.
  2. `self_check_feedback`의 인자 `rejected_rule_reasons`(`observations.py:1069`)를 넘기는 호출이 없다. 그래서 작업자에게 전달되는 자기 점검 요청은 언제나 `"rejected_rule_reasons": []`를 싣는다(`observations.py:1079`). 공개 필드 목록에도 이 이름이 있다(`observations.py:40`).
  3. `self.responses`(`observations.py:465`)는 응답 기록 전체를 쌓는다. 그러나 읽는 곳은 다음 ID의 번호를 세는 `len(self.responses)` 하나뿐이다(`observations.py:893`).
  4. `self.last_checkpoint`는 쓰기만 하고 읽지 않는다(`observations.py:468`, `observations.py:957`).
- 근거: 검색식과 결과는 다음과 같다.
  - `observation_subjects`: 저장소 `.py` 전체 1건(`observations.py:451`).
  - `allowed_subjects`: 8건, 모두 `observations.py` 안.
  - `rejected_rule_reasons`: `.py`·`.md` 전체에서 `observations.py`의 3건뿐. 호출 `self_check_feedback(`은 `engine.py:1341`, `engine.py:1365`, `state_checks.py:348`, `observations.py:1085`이며, 모두 인자 하나로 부른다.
  - `\.responses\b`: 3건, 모두 `observations.py`.
  - `\.last_checkpoint\b`: 2건.
  - 엔진이 추적기 속성에 접근하는 목록(grep `(tracker|candidate)\.[a-z_]+`, `engine.py`·`lifecycle_engine.py`·`scheduler.py`)에도 넷 중 어느 이름도 없다.
- 제안: 설정 키 읽기, `allowed_subjects` 인자와 분기, `rejected_rule_reasons` 인자·필드·공개 필드 항목, `last_checkpoint`를 지운다. `responses` 목록은 정수 계수기 하나로 바꾼다.
- 실익: 약 12행이 사라진다. 작업자 요청에서 늘 비어 있는 필드 하나가 빠진다. 엔진은 관찰 묶음마다 추적기 전체를 깊은 복사한다(`engine.py:2789`). 여기서 응답 원문(`response_json`)을 담은 목록이 빠지므로 복사 비용이 응답 수에 따라 늘지 않는다.
- 비용과 위험: 새 상태는 없다. 자기 점검 요청의 payload 모양이 바뀐다. 이 payload의 해시가 인지 확인에 쓰이지만, 생성과 대조가 같은 함수를 거치므로(`observations.py:575-576`, `observations.py:686`) 일관성은 유지된다.
- 기능·커버리지 영향: 있음. 작업자에게 가는 자기 점검 요청에서 늘 `[]`이던 `rejected_rule_reasons` 필드가 빠진다. 그 밖의 기능 변화는 없다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### IO-06 소비자 없는 구조 필드·메서드와 도달하지 않는 방어 분기

- 검토: 1
- 종류: 미사용
- 좌표: `do_math/codex_adapter.py:33-34`, `do_math/codex_adapter.py:43`, `do_math/codex_adapter.py:47`, `do_math/codex_adapter.py:136-138`, `do_math/codex_adapter.py:220`, `do_math/codex_adapter.py:242-247`, `do_math/observation_transport.py:29`, `do_math/control_transport.py:308-313`, `do_math/model_runner.py:126-127`
- 현상: 다음은 제품 안에 소비자가 없다.
  - `CodexExecution`의 필드: `prompt_path`, `snapshot_dir`, `stop_requested`는 제품과 시험 어디에서도 읽지 않는다. `stop_requested`는 쓰기만 한다(`codex_adapter.py:220`). `request_path`는 시험 한 곳만 읽는다(`tests/test_redesign_PROFILES.py:291`, `295`).
  - 생성자 인자 `describe_timeout`(`codex_adapter.py:136`)을 넘기는 호출이 없다. 늘 기본값 10초다.
  - `ObservationBatch.bytes_received`(`observation_transport.py:29`)는 시험 한 곳만 읽는다(`tests/test_model_runner.py:124`).
  - `ControlTransport.receipt`와 `records`(`control_transport.py:308-313`)는 제품 호출이 없고 시험 3곳만 부른다.
  - `collect`는 요청 바이트의 JSON 해석이 실패하면 빈 dict로 대체한다(`codex_adapter.py:242-247`). 그러나 `request_raw`는 언제나 `start`가 같은 프로세스에서 `compact_json_bytes(dict)`로 만든 바이트다(`codex_adapter.py:206`, `codex_adapter.py:212-214`). 이 대체 분기를 타는 것은 잘못된 바이트 `b"old"`를 넣는 시험 하나뿐이다(`tests/test_codex_adapter.py:204`).
  - 러너의 `hasattr(self._adapter, "capability_identity")`와 `isinstance(identity, dict) and identity`(`model_runner.py:126-127`)는 늘 참이다. 모든 어댑터가 기반 클래스의 `capability_identity`를 가지고, 이 메서드는 네 키짜리 dict를 돌려준다(`codex_adapter.py:140-149`). 이 경로를 타는 시험은 둘이다. `tests/test_redesign_PROFILES.py:985-1003`은 `Mock`의 `capability_identity`가 dict를 돌려주게 하므로 두 조건을 모두 통과한다. `tests/test_redesign_PROFILES.py:850-864`는 프로필 없이 부르므로 `profile is not None`에서 식별 계산 자체를 건너뛴다. 따라서 두 조건을 지워도 두 시험의 결과는 같다.
- 근거: 검색식과 결과는 다음과 같다. 필드마다 `\.<이름>\b`로 제품과 시험을 검색했다.
  - `prompt_path`·`snapshot_dir`·`stop_requested`: `CodexExecution` 소비 0건(`lifecycle_engine.py:517`의 `stop_requested`는 runtime 키로, 다른 개념이다).
  - `describe_timeout`: `codex_adapter.py` 밖 0건.
  - `bytes_received`: 제품 0건, 시험 1건.
  - `\.receipt\(`와 `\.records\(\)` 두 검색: 제품 0건(`repository.records`는 다른 메서드), 시험 3건.
  - `capability_identity`: 제품의 정의는 `codex_adapter.py:140` 하나.
- 제안: 위 필드·인자·메서드를 지우고, 해당 시험을 현행 계약으로 고친다. 두 방어 분기도 지운다. 시험은 `request_path` 대신 `start`가 돌려준 `request_raw`를 읽고, `receipt` 대신 `worker_receipt(binding, id)`나 outbox 파일을 읽고, `b"old"` 대신 유효한 요청 바이트를 넣는다.
- 실익: 약 20행이 사라진다. 제품 표면에서 시험 전용 메서드 둘과 소비자 없는 필드 넷이 빠진다.
- 비용과 위험: 새 상태는 없다. 시험 5개 파일을 고쳐야 한다.
- 기능·커버리지 영향: 없음(제품 동작 보존)
- 사용자 결정 관련: 없음
- 확신도: 확인

#### IO-07 엄격 JSON 해석을 호출처마다 손으로 조립하고, 같은 파일을 두 규칙으로 읽는다

- 검토: 1
- 종류: 이음새
- 좌표: `do_math/file_io.py:212-217`, `do_math/observations.py:398-399`, `do_math/observations.py:785-792`, `do_math/model_runner.py:260`, `do_math/model_runner.py:336`, `do_math/codex_worker.py:100`, `do_math/claude_worker.py:31`, `do_math/claude_worker.py:70`, `do_math/cli.py:40`, `do_math/submission.py:237-240`, `do_math/submission.py:1125-1138`
- 현상: 이음새 계약 11절은 엄격 JSON 해석의 정본으로 `file_io.strict_json_loads`를 등록한다. 이 함수는 세 가지를 거부한다. 중복 키, `NaN`·`Infinity` 같은 이름 붙은 상수, `1e999`처럼 무한대로 넘치는 지수다(`file_io.py:212-217`). 그런데 IO 영역의 호출처는 이 함수를 부르지 않고 훅을 손으로 조립한다. 조립 방식은 세 가지다.
  - 두 훅(`unique_pairs`, `reject_constant`)을 조립한다. 지수 넘침 검사는 빠진다. `model_runner.py:260`(최종 응답), `model_runner.py:336`(저장 요청), `observations.py:398-399`(checkpoint)가 여기에 든다.
  - 중복 키 훅 하나만 쓴다. `codex_worker.py:100`과 `claude_worker.py:31`(worker 요청), `claude_worker.py:70`(출력 스키마), `cli.py:40`(사용자 JSON 파일)이 여기에 든다.
  - 훅을 하나도 쓰지 않는다. `observations.py:791`(교체 제안 파일 `observation-rules.json`)이다.

  이 불일관이 한 파일에서 드러나는 곳이 있다. 작업자가 쓴 `observation-rules.json`을 제출 검사는 `load_json`으로 읽는다(`submission.py:1132`, `237-240`). 이 함수는 두 훅과 저장 값 영역 검사를 쓴다. 추적기는 같은 파일을 훅 없이 읽는다(`observations.py:791`). 그래서 중복 키가 있는 파일에 대해 제출 검사는 "duplicate" 오류를 내고, 추적기는 마지막 값을 조용히 받아들인 뒤 다른 사유로 반려한다.
- 근거: grep `object_pairs_hook=unique_pairs`로 영역 안 일치 7건을 찾았다(위 좌표. `claude_worker.py`는 2건). 영역 밖 일치는 `payloads.py:175`, `repository.py:731`, `submission.py:238`이다. `strict_json_loads`를 부르는 곳은 영역 안에 `claude_stream.py:79`, `codex_adapter.py:76` 두 곳뿐이다.
- 제안: 위 7곳의 손 조립 해석을 `strict_json_loads` 호출로 바꾼다. 저장 값 영역 검사가 필요한 곳(`submission.load_json`, checkpoint)은 그 뒤에 영역 검사를 한 번 더 한다. 추적기의 규칙 파일 해석은 `strict_json_loads(raw.decode("utf-8-sig"))`로 바꾼다. `observations`가 `submission`을 import하면 의존 방향이 뒤집히므로, 공용 조합이 필요하면 `file_io`에 둔다.
- 실익: 해석 규칙의 손 조립 사본 7곳이 정본 호출로 바뀐다. 한 파일에 대한 두 경로의 반려 사유가 같아진다. 지수 넘침 거부가 빠진 네 곳도 정본 규칙을 얻는다. 다만 그중 최종 응답과 checkpoint는 뒤이은 저장 값 검사(`model_runner.py:261`, `observations.py:400`)가 넘침으로 생긴 무한대를 이미 거부한다. 따라서 여기서 얻는 것은 동작 차이보다 규칙의 단일화다.
- 비용과 위험: 새 상태는 없다. 추적기 반려 사유와 일부 오류 문구가 바뀐다. worker 요청과 출력 스키마는 같은 프로세스가 `compact_json_bytes`로 만든 바이트이므로 판정은 바뀌지 않는다.
- 기능·커버리지 영향: 있음(중복 키·넘침 입력의 반려 사유 문구)
- 사용자 결정 관련: 없음
- 확신도: 확인. 호출처는 전수 grep으로 확인했다. 뒤이은 저장 값 검사가 무한대를 거부하는지는 6절의 넷째 명령으로 확인했다.

#### IO-08 자기 점검 응답의 수신 검사가 공유 검사 함수를 거치지 않는다

- 검토: 1
- 종류: 이음새
- 좌표: `do_math/control_transport.py:65-67`, `do_math/control_transport.py:350-353`, `do_math/observations.py:852-857`
- 현상: 이음새 계약 11절은 `SELF_CHECK_RESPONSE_SCHEMA`와 `self_check_response_errors`를 "생산자·수신자 공용"으로 등록한다. 생산자(`worker_submit`)는 `self_check_response_errors`를 쓴다(`control_transport.py:351`). 그러나 수신자 `record_self_check_response`는 `jsonschema.validate(response, SELF_CHECK_RESPONSE_SCHEMA)`를 직접 부른다(`observations.py:852-854`). 같은 스키마를 서로 다른 진입점으로 검사하는 셈이다. 게다가 `jsonschema.validate`는 호출마다 메타스키마 검사를 한다.
- 근거: grep `self_check_response_errors`의 제품 일치는 정의와 `control_transport.py:351` 2건이다.
- 제안: 수신자도 `self_check_response_errors(response)`가 비었는지로 판정한다. 함수 안의 `import jsonschema`는 지운다.
- 실익: 검사 진입점이 하나가 되고, 등록된 이음새 계약과 실제 코드가 일치한다. 응답마다 하던 메타스키마 검사가 사라진다. 코드는 약 3행 준다.
- 비용과 위험: 새 상태는 없다. 두 경로 모두 draft 2020-12로 검사하므로 판정은 같다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### IO-09 같은 프로세스 안에서 같은 값을 다시 검사하는 두 곳

- 검토: 1
- 종류: 비용
- 좌표: `do_math/observations.py:347`, `do_math/observations.py:452-456`, `do_math/observations.py:807-813`, `do_math/observations.py:988`, `do_math/codex_worker.py:89`, `do_math/codex_worker.py:114`, `do_math/claude_worker.py:46`
- 현상: 두 곳이 같은 값을 같은 프로세스에서 다시 검사한다.
  1. `evaluate_rules`는 들어온 규칙을 매번 `validate_rules`로 다시 검사한다(`observations.py:347`). 규칙에는 깊은 복사와 시각 해석도 포함된다. 운영에서 이 함수를 부르는 곳은 추적기 한 곳이다(`observations.py:988`). 추적기는 관찰 묶음이 따라잡을 때마다 이 함수를 부른다. 그런데 추적기의 규칙은 생성 때(`observations.py:452-456`)와 교체 때(`observations.py:807-813`) 이미 같은 함수로 검사됐다.
  2. worker는 `load_request` 안의 `check_common_request`에서 바인딩을 검사한다(`codex_worker.py:89`). 곧이어 `build_argv`에서 같은 요청을 다시 검사한다(`codex_worker.py:114`, `claude_worker.py:46`). 제품에서 `build_argv`는 `run`이 `load_request` 직후에만 부른다(`codex_worker.py:176-177`, `claude_worker.py:79-80`).
- 근거: 검사된 규칙과 요청은 같은 프로세스 안에서 전달되며, 그사이에 디스크 왕복·다른 스레드·재시작이 없다. 기준 2절 2항의 세 조건과 2절 6항의 "같은 사실의 반복 확인"에 해당한다.
  - grep `evaluate_rules`: 제품 1건. 시험은 모두 유효한 규칙을 넘긴다(`tests/test_redesign_OBSERVATION.py:56`, `61`, `115`, `171`, `174`, `204`). 204행의 `ValueError`는 값 검사(`observations.py:366-367`)에서 난다.
  - grep `build_argv`: 제품 2건. 시험은 `build_argv`의 바인딩 거부를 기대하지 않는다. 바인딩 거부 시험은 `load_request`와 `validate_execution_binding`을 직접 부른다(`tests/test_redesign_PROFILES.py:258-259`, `579-580`).
- 제안: `evaluate_rules`에서 `validate_rules` 호출을 지운다. 규칙 검사는 생산자인 추적기의 생성·교체 경로에 남긴다. `build_argv` 두 곳의 `validate_execution_binding`도 지운다. 이 경우 `claude_worker`의 해당 import가 필요 없어진다.
- 실익: 관찰 평가마다 규칙 검사와 깊은 복사 한 번이 사라지고, 코드는 약 4행 준다.
- 비용과 위험: `evaluate_rules`를 직접 부르는 호출자는 규칙을 먼저 검사해야 한다. 유일한 제품 호출자인 추적기는 이미 그렇게 한다. 시험 호출은 유효한 규칙을 넘기며, 그중 하나는 `validate_rules`를 먼저 부른다(`tests/test_redesign_OBSERVATION.py:115`).
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### IO-10 CLI 발견 계약의 일부가 실제 정의의 수기 사본이다

- 검토: 1
- 종류: 이음새
- 좌표: `do_math/cli.py:533-538`, `do_math/cli.py:577-583`, `do_math/cli.py:635`, `do_math/cli.py:668-683`
- 현상: `--describe`는 몇 가지 값을 손으로 다시 적는다.
  - `request_fields`(`cli.py:578`)는 같은 파일의 요청 스키마 `properties` 키(`cli.py:534-538`)를 다시 적은 것이다.
  - `error_exit_codes`(`cli.py:582`)는 `main`의 예외 처리가 쓰는 종료 코드 2와 5(`cli.py:669-683`)를 다시 적은 것이다.
  - CLI wire 판본 5는 요청 스키마(`cli.py:534`), 발견 결과(`cli.py:577`), 봉투(`cli.py:635`)에 따로 적혀 있다.

  2라운드 IO-18은 이 발견 계약이 실제 봉투와 이미 어긋난 것을 발견해, 봉투 필드만 `RESPONSE_FIELDS`로 통일했다. 나머지 사본은 남았다.
- 근거: 사본들은 원문으로 대조했다. 지금은 모두 실제 정의와 일치한다.
- 제안: `request_fields`는 `list(_request_schema(parser)['properties'])`로 만든다. 종료 코드는 모듈 상수 `ERROR_EXIT_CODES` 하나를 두고, `main`과 `describe_commands`가 함께 쓴다. 판본 번호도 상수 하나로 둔다.
- 실익: 발견 계약이 실제와 다시 어긋날 여지가 사라진다. 이 위험은 2라운드 IO-18이 발견한 불일치로 한 번 실현되었다. 행 수는 거의 같다.
- 비용과 위험: 없음
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### IO-11 같은 뜻을 두 번 적은 작은 사본 세 곳

- 검토: 1
- 종류: 기타(한 파일 안에서 같은 효과를 두 번 적은 사본. 4.1의 이음새는 모듈 사이 정의를 말하므로 따로 분류함)
- 좌표: `do_math/cli.py:668-673`, `do_math/cli.py:21`, `do_math/cli.py:319`, `do_math/control_contracts.py:112-114`
- 현상: 세 곳이 있다.
  1. `CliInputError`는 `ValueError`의 하위 클래스인데(`cli.py:28`), `main`이 두 예외를 본문이 같은 두 절로 따로 처리한다(`cli.py:668-673`).
  2. `prepare-import-approval` 분기가 모듈 머리에서 이미 가져온 `canonical_json`을 다시 import한다(`cli.py:21`, `cli.py:319`).
  3. `CANDIDATE`의 `formal_result_ref`는 텍스트 필드 목록에 들어간 뒤, 같은 dict 리터럴의 뒤 키 `'formal_result_ref': TIME`에 덮어써진다(`control_contracts.py:112-114`). 앞의 선언은 효과가 없다.
- 근거: 원문. 셋 모두 세 경량화 이전의 커밋에서 왔다(`git blame`: 08eecbf1, 7d2597ec, a299fd8c, c4d78382).
- 제안: 첫째는 `ValueError` 절 하나로 합친다. 둘째는 중복 import를 지운다. 셋째는 텍스트 목록에서 `formal_result_ref`를 뺀다.
- 실익: 약 5행이 준다. 셋째는 필드의 실제 형(문자열 또는 null)을 한 곳에만 적게 한다.
- 비용과 위험: 없음
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### IO-12 새 스키마 키워드가 공급자 CLI에 닿는 경로는 MCP 도구 스키마와 수리 보고 스키마이며, 실측되지 않았다

- 검토: 2
- 종류: 공백
- 좌표: `do_math/control_transport.py:39-57`, `do_math/control_transport.py:530-531`, `do_math/engine.py:3179-3181`, `do_math/engine.py:3413-3417`, `do_math/model_runner.py:93-97`, `do_math/claude_worker.py:69-74`, `do_math/codex_worker.py:121-122`, `do_math/scheduled_operator.py:588`, `scripts/probe_cli.py:68`
- 현상: M-0349 「남은 위험과 진입점」은 "모델에 전달하는 스키마의 새 키워드(`pattern`, `enum`, `anyOf`+null, `minItems`/`maxItems`)를 공급자 CLI가 받아들이는지"를 미확인으로 남겼다. 원문을 따라가면 이 위험의 범위와 경로가 다음과 같이 좁혀진다.
  - 역할 응답 스키마는 CLI에 가지 않는다. 엔진은 모든 실행에 제어 바인딩을 발급하고(`engine.py:3179-3181`) 러너에 넘긴다(`engine.py:3417`). 러너는 바인딩이 없을 때만 요청에 출력 스키마 경로를 넣는다(`model_runner.py:93-97`). 러너를 부르는 곳은 셋이다. 엔진 실행(인자는 `engine.py:3413`이 만들고 호출은 `scheduler.py:598`이 한다), 수리 실행(`scheduled_operator.py:588`), 진단 스크립트 `probe_cli.py:68`. 역할 응답 스키마는 프롬프트 본문에만 렌더링된다.
  - CLI 출력 스키마로 가는 것은 수리 보고 스키마와 probe 스키마 둘이다. 수리 보고 스키마의 키워드를 읽기 전용 명령으로 모았다. 진단이 없는 판은 `required`, `additionalProperties`, `items`, `type`만 쓰고, 진단이 있는 판은 여기에 `enum`과 `minLength`를 더한다. 두 판 모두 `pattern`, `anyOf`, `minItems`/`maxItems`는 없다. Codex는 파일 경로로(`codex_worker.py:121-122`), Claude는 `$schema`·`x-contract-id`를 뺀 JSON으로(`claude_worker.py:69-74`) 받는다.
  - 새 키워드가 실제로 공급자에게 가는 경로는 MCP 도구 스키마다. 2라운드 IO-04가 `control_self_check`의 `inputSchema.properties.response`에 `SELF_CHECK_RESPONSE_SCHEMA`를 실었다(`control_transport.py:530-531`). 두 CLI는 `tools/list`로 이 스키마를 받는다. 이 스키마에는 `minItems`, `uniqueItems`, `minLength`, `additionalProperties: false`가 있다. 또 `type` 없는 `enum` 노드(`progress`, `status`)와 아무 제약 없는 빈 스키마 `"rule_proposal": {}`가 있다(`control_transport.py:39-57`). 이전 판에서 이 자리는 `{"type": "object"}`였다(`C:/math/임시/경량화-조사-2026-09-26/IO.md`의 IO-04 현상).
- 근거: 위 호출 경로는 전수 grep으로 확인했다. 러너 호출은 grep `runner\.run(|ModelRunner()\.run|self\.runner\.run`으로 찾았다. `do_math/` 안의 일치는 2건이다. 하나는 `scheduler.py:598`로, 엔진이 `engine.py:3413`에서 만든 인자로 러너를 부른다. 다른 하나는 `scheduled_operator.py:588`이다. 여기에 `do_math/` 밖의 진단 스크립트 `probe_cli.py:68`을 더한 셋이 앞의 "러너를 부르는 곳 셋"이다. 시험은 MCP 서버를 실제로 띄워 도구 호출을 검사한다(`test_control_preview`, `test_redesign_ACTIVITIES`, `test_submission_tools`). 그러나 실제 Codex·Claude CLI가 이 `inputSchema`를 받아 모델에게 어떤 도구 정의로 넘기는지는 어느 시험도 확인하지 않는다. 연구 인스턴스는 결정 1로 모두 삭제되었고, 2라운드 이후의 실제 연구 실행 기록은 찾지 못했다.
- 제안: 실제 확인이 먼저다. 연구 실행 하나를 Codex와 Claude로 각각 돌려 두 가지를 확인한다. 하나는 MCP 서버가 도구 목록 단계에서 거부되지 않는지다. 다른 하나는 `control_self_check`에 정상 응답을 보낼 수 있는지다. 확인할 지점은 세 곳이다. CLI가 `type` 없는 노드(`enum`만 있는 노드, `{}`)를 어떤 형으로 번역하는가. `uniqueItems`·`minItems`를 거부하거나 버리는가. 모델이 `rule_proposal`을 객체로 보내는가. 확인 전에도 할 수 있고 수신 판정을 바꾸지 않는 조치가 하나 있다. `enum` 노드에 `"type": "string"`을, `rule_proposal`에 `"type": "object"`를 명시하면 번역의 모호성이 사라진다. 수신 쪽은 `rule_proposal`을 어차피 객체로만 받아들이므로(`observations.py:80-81`), 이 조치는 수신 판정을 바꾸지 않는다. 오히려 객체가 아닌 제안을 더 일찍 도구 오류로 돌려준다. 수리 보고 스키마의 `minLength`·`enum`은 Codex의 출력 스키마 처리에서 같은 방식으로 확인한다(OPS 영역, 5절).
- 실익: MCP 서버가 CLI에서 거부되면 모든 연구 실행이 제어 도구를 잃는다. 그 경우 제출 경로가 막히므로, 확인의 가치가 가장 큰 공백이다. 반대로 역할 응답 스키마가 CLI에 가지 않는다는 사실은 M-0349 위험의 대부분을 닫는다.
- 비용과 위험: 실제 CLI 실행 두 번이 든다. 명시 형 추가는 스키마 두 노드를 바꾸며, 새 상태는 없다.
- 기능·커버리지 영향: 명시 형을 추가하면 객체가 아닌 `rule_proposal`이 규칙 반려 대신 도구 오류가 된다.
- 사용자 결정 관련: 없음
- 확신도: 추정. 경로는 전수 확인했다. CLI의 수용 여부는 실행해야 확정된다.

#### IO-13 관찰 입력의 dict 경로가 제품에서 도달하지 않는 두 번째 의미를 유지한다

- 검토: 2
- 종류: 공백
- 좌표: `do_math/observations.py:556-564`, `do_math/observations.py:668-670`, `do_math/observations.py:930-931`, `do_math/engine.py:2786-2791`, `do_math/engine.py:2810`, `do_math/engine.py:2874`
- 현상: 추적기의 `observe(event, source=None)`는 `source`가 없을 때 다른 의미로 동작한다.
  - 시각은 수신 시각 대신 `clock()`을 쓴다(`observations.py:931`).
  - "응답 전 연구 행동" 판정에서 모든 의무를 이미 전달·인지된 것으로 본다(`observations.py:559-562`).
  - 폴 인지를 건너뛴다(`observations.py:669`).

  제품에서 추적기에 관찰을 넣는 경로는 러너의 `on_observation` 하나이고, 러너는 언제나 `ObservationBatch`를 넘긴다(`model_runner.py:178`). 엔진의 틱도 `source`를 넘긴다(`engine.py:2815-2816`). 그래서 `source=None` 경로를 타는 것은 엔진의 dict 사건 분기(`engine.py:2790-2791`, `2810`, `2874`)와 시험뿐이다. `결과-E.md` 4절은 이 경로를 "운영 코드는 없다. 대역을 모두 묶음으로 바꾸면 이 경로를 지울 수 있다"며 남겼다.
- 근거: grep `\.observe(`의 제품 일치는 `engine.py:2810`, `2815` 2건이다. grep `on_observation`으로 러너만 호출함을 확인했다(`parallel.py:79-80`은 콜백을 그대로 감싼다). 시험은 `tracker.observe`를 9개 파일에서 89회 부르고, `_observe_running`에 dict를 넘기는 곳이 3곳이다(`tests/test_observations.py:388`, `tests/test_redesign_ENGINE.py:1387`, `1392`).
- 제안: 추적기가 `source`를 필수로 받게 하고, 시험은 묶음 대역을 만드는 도우미 하나로 `source`를 채운다. 엔진의 dict 분기는 엔진 영역에서 함께 지운다(5절).
- 실익: 제품이 쓰지 않는 두 번째 판정 의미(전달·인지 가정)가 사라진다. 그 결과 시험이 운영과 같은 판정을 검사하게 된다.
- 비용과 위험: 새 상태는 없다. 시험 약 90곳을 고쳐야 하는데, 이는 기준 2절 11항(가장 싼 시작 상태)과 부딪힐 수 있다. 추적기 단위 시험이 매번 묶음을 만들어야 하기 때문이다. 도우미 하나로 이 비용을 흡수할 수 있는지가 채택의 관건이다.
- 기능·커버리지 영향: 있음. 시험이 `source=None` 의미 대신 운영 의미를 검사하게 된다.
- 사용자 결정 관련: 없음
- 확신도: 추정. 제품 도달 불가는 확인했다. 시험 이전 비용은 파일별로 대조하면 확정된다.

## 4. 보존 판정

- **`do_math/operation_trace.py:22-116`의 live 스냅숏 제한(타이머 하나, `pending`, `closed`).** 파견문은 이 구조가 기준 2절 8항(새 상태·수명 규칙의 비용)에 비추어 가장 단순한 형태인지 판정하라고 요청했다. 이 구조는 사용자가 받아들인 "진행 표시 최대 1초 지연"(사용자 결정)을 지키는 가장 단순한 형태라고 판정한다.
  - 타이머가 필요한 이유: 이 스냅숏을 읽는 곳은 `status`의 `operation_progress`(`engine.py:1514`)다. 한 `run` 연산 전체가 하나의 추적이다(`engine_operation`). 따라서 시간 비교만 하는 스로틀은 1초 한계를 지키지 못한다. 짧은 사이에 연 스팬 뒤로 긴 조용한 구간이 오면, 그 스팬은 다음 행이 올 때까지 스냅숏에 나타나지 않는다.
  - 대안 1은 스냅숏 없이 읽는 쪽이 `.jsonl`을 다시 읽는 것이다. 이 방식은 몇 시간짜리 `run` 추적 전체를 `status`마다 읽는다. 활성 스팬은 오래전에 시작됐을 수 있어 꼬리만 읽을 수 없기 때문이다.
  - 대안 2는 엔진의 주기 활동에 기대어 뒤늦은 쓰기를 하는 것이다. 이 방식은 추적 정확성을 무관한 호출 빈도에 묶는다.
  - `closed` 표지가 필요한 이유: `parallel`의 작업 스레드는 문맥을 복사해 추적 뒤에도 행을 낼 수 있다(`parallel.py:93-94`). 그래서 닫힌 뒤에도 행을 추적 파일에 덧붙이는 경로가 필요하다(`operation_trace.py:54-60`). `closed`는 그 경로에서 스냅숏을 다시 쓰지 않게 하는 표지다.
  - 흠: `_write_pending`의 `not self.closed` 조건(`operation_trace.py:95`)은 `close`가 `pending`을 비우므로 없어도 된다. 다만 1행이고 의도를 드러내므로 후보로 올리지 않는다. 또 클래스 docstring은 `close`가 "flushes and stops both"라고 적는다(`operation_trace.py:28`). 그러나 실제 `close`는 스트림을 닫고 타이머를 취소할 뿐, 대기 중인 스냅숏은 쓰지 않고 버린다(`operation_trace.py:83-89`). 곧바로 `tracing`이 live 파일을 지우므로(`operation_trace.py:156-160`) 동작 문제는 없다. docstring의 한 낱말이 부정확한 정도라 후보로 올리지 않는다.
- **`do_math/control_transport.py:156`, `do_math/control_transport.py:272-288`의 `_pump_cache`.** 키는 경로다. 값은 정착된 지문과 최종 영수증이다. 무효화는 지문 불일치와 `close`에서 일어난다(`control_transport.py:304-305`). 최종 영수증은 다시 바뀌지 않으므로 결과를 정하는 입력이 모두 키에 들어 있다. 시험은 이 캐시를 비우지 않는다(grep `_pump_cache` 시험 0건).
- **`do_math/observations.py:759-774`, `do_math/observations.py:776-789`의 checkpoint·규칙 파일 지문 메모.** 정착된 지문만 기억하고, 유효한 판독만 기억하며, 지문이 다르면 다시 읽는다. 이음새 계약 1절의 `fingerprint_settled` 규칙을 따른다.
- **`do_math/control_contracts.py:128-139`의 `@cache` `_configure_validator`.** 입력이 제품 상수 `config_schema()`뿐이라 키가 필요 없다.
- **`do_math/model_runner.py:305-373`의 `verified_native_final` 재검사.** 입력이 Git에서 읽은 저장 결과일 수 있다(`engine.py:2586`). 따라서 기준 2절 12항의 "신뢰 경계 밖 입력의 수신 검사"에 해당한다.
- **`do_math/codex_adapter.py:61-114`과 `do_math/claude_stream.py:52-177`의 두 스트림 해석기, `do_math/codex_worker.py:112-137`과 `do_math/claude_worker.py:45-75`의 두 argv 구성.** 공급자 CLI의 실제 차이다(기준 4.3). IO-01은 이 둘을 합치자는 제안이 아니다.
- **`do_math/observation_transport.py:8-13`의 관대한 행 해석.** 관찰은 행 하나의 실패로 멈추면 안 되고, 권위 판정은 `collect`의 엄격 해석이 맡는다(2라운드 보존 판정 유지).
- **`do_math/control_contracts.py:21-32`의 내용 기반 제어 요청 ID.** M-0348은 `pause → resume → 같은 사유의 pause`가 이전 영수증을 재생해 정지하지 않은 일을 관찰로 남겼다. 이것은 문서화된 멱등 계약이다(`references/CLI-실행-계약.md:48`). 재생은 `replayed=true`로 드러나고, 의도적인 새 적용에는 `--idempotency-key`를 쓴다. 공백으로 올리지 않는다.
- **`do_math/control_contracts.py:65-70`의 `TEXT`(`{'type':'string'}`)와 `contracts.TEXT`(비지 않은 텍스트).** 이름이 같지만 제어 모양의 형 표시와 wire의 비지 않은 텍스트는 서로 다른 개념이다(기준 2절 3항).
- **`do_math/control_transport.py:298-302`의 `close` 안 `ValueError` 무시.** `결과-E.md` 5절이 원인(이미 영수증을 받은 요청 ID의 바뀐 재전달)과 결과(먼저 쓴 영수증 유지)를 밝혔다. 원인을 아는 처분이므로 임시방편이 아니다.

## 5. 영역 밖 관찰

- ENG `do_math/engine.py:1233-1234`: 제어 요청 ID를 인스턴스 전체의 `control_receipts`에서 선형으로 찾는다. 이름공간이 전역이라, 작업자가 지은 안전 경계 ID(`references/공통-실행.md:169-172`)가 다른 실행과 겹치면 거부된다. 조회도 이력에 비례한다. IO-02와 함께 전송 범위로 좁힐 후보다.
- ENG `do_math/engine.py:2786-2791`, `2810`, `2874`: `_observe_running`의 dict 사건 분기는 제품에서 도달하지 않는다(IO-13).
- STO `do_math/payloads.py:175`, `do_math/repository.py:731`, REV `do_math/submission.py:238`: 정본 `strict_json_loads` 대신 `unique_pairs`·`reject_constant` 두 훅을 손으로 조립한다(IO-07과 같은 불일관).
- OPS `do_math/scheduled_operator.py:588`: 수리 실행은 CLI 출력 스키마로 `repair_report_schema`를 넘긴다(`enum`, `minLength` 포함). 이 스키마의 Codex 수용 여부는 실측되지 않았다(IO-12).
- HIS `C:/math/docs/do-math/검사-경량화-이음새-계약.md:69`: "worker 능력 식별의 파일 범위가 `control_transport`와 `file_io`"라는 문장이 현재 코드와 다르다. 현재 범위는 어댑터별 `identity_modules`다(`codex_adapter.py:332`, `claude_adapter.py:28-29`). `결과-E.md` 3절이 이 수정을 통합자 몫으로 넘겼는데, 반영되지 않았다.
- HIS `C:/math/docs/do-math/검사-경량화-이음새-계약.md:230`: `self_check_response_errors`를 "생산자·수신자 공용"으로 적었지만 수신자는 쓰지 않는다(IO-08).
- TSB/TSA `tests/test_codex_adapter.py:120-124`: Job 안 직접 적재의 회귀 시험은 `codex_worker.py`만 실행한다. `claude_worker.py`의 직접 적재는 시험이 없다. 이번 검토에서 직접 실행해 보니 사용법 오류로 정상 종료했고, import 오류는 없었다(6절).

## 6. 작업 기록

- 동작 확인 명령은 네 번 실행했다. 모두 추적 파일을 바꾸지 않는다. 다만 둘째 명령은 추적되지 않는 `do_math/__pycache__`에 바이트코드를 남겼을 수 있다.
  1. `python -c "... contracts.schema_for(r) ..."`: 역할 응답 스키마 10개의 직렬 크기. 결과는 2,531~7,212바이트였다.
  2. `python -c "... subprocess.run([sys.executable,'claude_worker.py']) ..."`: `do_math/`에서 실행했다. 결과는 종료 코드 1과 `usage: claude_worker.py REQUEST.json`이었고, import 오류는 없었다. 같은 명령으로 `claude_stream`의 직접 import도 `ok`였다.
  3. `python -c "... repair_report_schema(diagnosed=...) ..."`: 키워드 목록. 결과는 IO-12에 적었다.
  4. `python -c "... canonical_json({'x': float('inf')}) ... validate_storage_value(...) ..."`: 두 함수 모두 `ValueError`("JSON floating-point numbers are not permitted")를 냈다(IO-07).
- 예상과 달랐던 결과가 둘이다.
  - M-0349의 스키마 키워드 공백은 역할 응답 스키마가 CLI에 간다는 전제에서 나왔다. 원문에서는 엔진 실행이 늘 바인딩되어 역할 스키마가 CLI에 가지 않았다. 새 키워드는 오히려 MCP 도구 스키마를 통해 공급자에게 간다.
  - IO-19가 `pump` 비용을 줄이면서, 같은 비용이 모든 엔진 생성으로 옮겨 갔다(IO-03).
- `결과-E.md` 4절의 미확인 위험은 다음과 같이 처분했다.
  - Codex final 대조: M-0349가 실제 실행 5건으로 일치를 확인했다. 원문에서 새로 찾은 사실이 없어 후보로 올리지 않았다.
  - 직접 적재: Codex worker와 MCP 서버는 시험이 덮는다. Claude worker는 위 확인으로 동작을 봤고, 시험 공백은 5절에 적었다.
  - 종료 뒤 마지막 행: 설계대로 동작하며 저장량 증가는 실행당 한 행이라 후보로 올리지 않았다.
  - pump 범위: IO-03에 반영했다.
  - dict 사건 경로: IO-13으로 올렸다.
- `379a171`의 영역 diff는 세 파일만 줄 단위로 읽었다. 나머지는 현재 원문 전문과 `결과-E.md`의 ID별 처분으로 대신했다(1절). 흔적을 놓치지 않도록 영역 12개 파일 전체에 두 검색을 더 했다. 하나는 AST 기반 미사용 import 검사로, 0건이었다. 다른 하나는 경위 주석 검색(`R\d+|IO-|no longer|legacy|removed` 등)으로, `codex_adapter.py:144`의 설계 항목 표지 `(R22)` 1건이었다. 이 주석의 내용(지문이 바뀔 때만 다시 해시)은 현재 동작과 맞으므로 잔재로 올리지 않았다. 이어서 `결과-E.md`가 지웠다고 적은 이름(`_runner_tools`, `_drain_review_observations`, `_review_event_cursors`, `parse_output`, `OBSERVATION_OPERATORS`, `OBSERVATION_SOURCES`, `_OPERATOR_SUBJECTS`, `_REMOVED_ENV`, `_write_status`, `final_text_mismatch`, `structured_output_*`, `reported_evidence`, `control_server_name`)을 스킬의 `.py`·`.md` 전체에서 검색했다. 남은 참조는 0건이었다. 이 검색 중에 IO-07의 손 조립 해석을 찾았다.
