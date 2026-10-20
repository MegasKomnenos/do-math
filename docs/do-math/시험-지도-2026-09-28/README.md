# do-math 시험 지도

이 지도는 `.claude/skills/do-math/scripts/tests/`에 있는 do-math 시험 전체가 어떻게 구성되어 있는지 기술한다. 다루는 것은 시험 모듈 122개와 그 안의 테스트 1,931개 전부, 공유 픽스처 모듈 9개, 시험 실행기다. 기준 판본은 커밋 `3552607`(2026-09-28)다. 이 지도를 만드는 동안 시험과 제품 코드는 이 커밋에서 바뀌지 않았으므로, 모든 행 좌표는 이 커밋의 원문을 가리킨다.

시험을 언제 어떻게 돌리고 새 시험을 어떻게 쓰는지의 정본은 `scripts/tests/시험-지침.md`다. 이 지도는 그 규칙이 실제 코드에서 어떤 모습으로 구현되어 있는지를 보이는 참조 자료다. 지도와 원문이 다르면 원문이 옳다. 이 지도는 시험을 실행해서 만든 것이 아니다. 따라서 현재 판본에서 시험이 통과하는지는 말하지 않는다.

## 1. 요약

do-math의 시험은 표준 라이브러리 `unittest` 위에 서 있다. 시험 모듈은 검사하는 제품 모듈이나 성질의 이름을 달고 있다. 모듈 122개는 여섯 조각(shard)으로 나뉘고, 자체 실행기 `scripts/run_tests.py`가 조각 순서대로 돌린다. 실행기는 결과가 실제로 확인되지 않았는데도 통과로 읽히는 경우를 막는 규칙을 여럿 갖고 있다. 예를 들어 조각에 등록되지 않은 모듈이나 오타 난 시험 ID가 있으면 실행하지 않고, 실행 도중 코드가 바뀌면 통과로 세지 않는다.

시험마다 출발하는 **시작 상태**가 다르다. `시험-지침.md`는 네 단을 정하고, 검사할 성질이 성립하는 가장 싼 단에서 출발하라고 한다.
1. 순수 함수 호출
2. 합성 활성 상태 템플릿
3. 공개 활성화 템플릿
4. 공개 경로 직접 구동. 공개 경로란 사용자와 운영자가 쓰는 진입점(엔진의 `initialize`·`activate`·`control`, CLI `do_math.py`)만 거쳐 상태를 만드는 길이다

2단과 3단의 무거운 상태는 `restore_template`가 프로세스마다 한 번 만들어 두고, 시험마다 같은 절대 경로에 바이트 그대로 복원한다. 다만 네 단은 새 시험을 쓸 때 고르는 순서이지, 기존 시험을 빠짐없이 나누는 분류가 아니다. 기존 시험은 순수 호출이 절반 가까이이고, 나머지 상당수는 네 단 어디에도 들지 않는 상태에서 출발한다. 메모리 위에서만 도는 엔진 대역, 실제 Git 저장소에 직접 조립한 상태, 실제 프로세스와 Windows Job을 다루는 구성이 그런 상태다(3.4절). 네 단의 상태와 그 밖의 출발 상태, 그리고 시험이 쓰는 대역은 모두 픽스처 모듈 9개가 층을 이루어 제공한다. 뿌리는 `research_fixtures`이고, 모든 대역은 답을 만드는 쪽(모델 역할의 답, 컴파일러 결과, 신뢰·승인 증거)만 합성하며, 그 답을 받아 검사·저장·수송하는 쪽은 제품 코드를 그대로 쓴다(4.3절).

실제 Lean이나 실제 프로세스 자원을 다루는 29개 시험(`lean` 20, `resource` 9)만 격리 표지를 달고, 실행기가 이들을 Windows Job 안의 별도 프로세스에서 제한 시간과 함께 돌린다. 그러나 실제 외부 자원을 쓰는 시험은 이보다 훨씬 많다. 스크립트 러너로 엔진을 모는 시험은 모델 호출마다 실제 Windows Job 자식 프로세스를 띄운다. 저장소에 닿는 시험은 실제 `git` 자식 프로세스를 띄운다. 반대로 모델의 답, 대부분의 컴파일러 결과, 신뢰 환경 증거는 합성된 것이다. 그러므로 시험 통과는 제품의 결정 규칙, 저장, 경로가 합성 입력 위에서 맞게 돈다는 뜻이다. 실제 모델 연구나 실제 수학 성과가 검증되었다는 뜻은 아니다.

지도는 다섯 부분으로 되어 있다.
- 이 총론
- 실행기 문서 [기반/실행기.md](기반/실행기.md)
- 픽스처 문서 9개 [기반/픽스처/](기반/픽스처/)
- 시험 모듈 문서 122개 [모듈/](모듈/)
- 색인(10절)

모듈 문서는 테스트마다 원문 행 범위와 함께 다섯 가지를 적는다. 성질, 준비, 실행, 단언, 대역이다.

## 2. 스위트의 형태

### 2.1 파일 구성

```text
.claude/skills/do-math/scripts/
├── run_tests.py          시험 실행기 (356행)
├── test_categories.py    조각 목록 SHARDS와 격리 표지 test_group (83행)
├── do_math/              시험 대상 제품 패키지 (하위 패키지 record_schemas 포함 약 3.5만 행)
└── tests/
    ├── 시험-지침.md       시험 실행·작성 규칙의 정본
    ├── test_*.py         시험 모듈 122개 (테스트 1,931개)
    └── *_fixtures.py     공유 픽스처 모듈 9개
```

시험 코드는 픽스처를 포함해 약 4.4만 행이다. 시험 모듈 안의 클래스는 346개다. 그 가운데 338개가 테스트를 담고, 나머지 8개는 시험이 쓰는 보조 클래스다. 모델 역할에 답하는 대역 러너가 넷(`RejectingRunner`, `QuotaRunner`, `InvestigationRunner`, `ConcurrentRunner`), `FakeEngine`을 상속한 엔진 대역이 하나(`Host`), 다른 시험 클래스가 상속하는 하네스 기반 클래스가 셋(`RecoveryHarness`, `StopFlagHarness`, `BoundaryFixture`)이다.

`.agents/skills/do-math/`에는 Codex용 생성 사본이 있다. 이 사본은 `.claude/skills/writing-skills/scripts/build_skill_mirrors.py`가 정본에서 만드는 산출물이며 손으로 고치지 않는다. 시험을 고칠 때는 정본만 고치고 사본은 생성기로 다시 만든다. 2026-09-28에 확인한 바로는 시험 파일의 내용이 정본과 같다. 두 파일(`test_role_input.py`, `test_review_research.py`)만 줄 끝 문자(CRLF)가 다르다.

### 2.2 조각

| 조각 | 모듈 | 테스트 | 격리 시험 | 성격 |
|---|---:|---:|---:|---|
| `foundation` | 69 | 1,039 | 10 | 순수 규칙과 저장 계층. 대부분 순수 호출이나 대역 위에서 돈다 |
| `host` | 18 | 173 | 18 | 실제 프로세스, Windows Job, Lean, 운영자 예약, 호스트 자원 |
| `lifecycle` | 20 | 378 | 1 | 엔진 수명, 제어, CLI, 역할 입력 |
| `research` | 4 | 121 | 0 | 목적 시나리오로 엔진을 끝까지 모는 연구 흐름, 스케줄러, 복구 |
| `review` | 8 | 179 | 0 | 동일성 검토와 제출 흐름 |
| `academic` | 3 | 41 | 0 | 학술 요건과 모델 평가 |

표의 **동일성 검토**는 이 지도 전체에서 자주 나오는 제품 개념이다. Lean 정본이 가진 정확한 형식 문면이 원래의 자연어 수학 진술과 같은 뜻인지를 독립 검토자가 판정하는 절차를 말한다(`GLOSSARY.md` 97행). 형식 검증(Lean이 증명을 받아들이는지)과는 다른 판정이다.

조각 목록의 정본은 `test_categories.SHARDS`다. 조각의 시간 목표는 두 가지다. 조각 하나를 단독으로 돌려 120초 안에, 전체를 300초 안에 끝내는 것이다. 이 목표가 현재 판본에서 충족되는지는 이 지도가 확인하지 않았다. 실행기, 조각, 격리의 세부는 [기반/실행기.md](기반/실행기.md)에 있다.

### 2.3 이름과 배치의 규칙

`시험-지침.md` 4절이 정하고, 원문에서 지켜지고 있는 규칙은 다음과 같다.

- 시험 모듈은 검사하는 제품 모듈이나 성질의 이름을 단다. 예: `do_math/scheduler.py`는 `test_session_scheduler`, 역할 입력 포장은 `test_role_input`. 수리 회차 같은 계기로 이름을 짓지 않는다. 다만 `test_observations.test_three_reported_counterexamples`처럼 계기로 이름을 지은 시험이 하나 남아 있다.
- 테스트 이름은 검사하는 성질을 문장으로 말한다. 이 이름이 실제 단언보다 넓은 경우가 적지 않다(8절).
- 시험 모듈은 다른 시험 모듈을 import하지 않는다. 원문 전체에서 시험 모듈 사이의 import는 0건이다. 두 모듈 이상이 쓰는 도우미는 픽스처 모듈로 옮기고, 한 모듈만 쓰는 도우미는 그 모듈의 모듈 함수로 둔다.
- 제품이 정의한 이름(역할, 스키마, 상수, 오류 문구)은 import해서 쓰고, 계산 결과처럼 시험이 검사하려는 값은 시험에 직접 적는다.

시험 모듈 118개는 스스로 `scripts/`를 `sys.path`에 넣는다. 나머지 4개는 스스로 경로를 넣지 않는다. `run_tests.py`로 돌리면 파이썬이 실행기가 있는 `scripts/`를 경로에 넣으므로 이 4개도 안전하게 import된다. 반면 `unittest discover`로 돌리면 앞서 import된 다른 시험 모듈이 넣어 둔 경로에 기대므로 수집 순서에 의존한다([기반/실행기.md](기반/실행기.md) 3절). `__main__` 블록은 119개 모듈에 있다. 블록이 없는 3개(`test_initialization_probe_batch`, `test_launch_recovery`, `test_schedule_pythonw`)는 파일을 직접 실행해도 시험이 시작되지 않는다. 경로를 스스로 넣지 않는 4개 가운데 `test_design_walkthroughs`, `test_knowledge_import_engine`, `test_knowledge_io` 3개는 블록이 있지만, 파일을 직접 실행하면 픽스처 모듈이 `do_math`를 import하는 단계에서 `ModuleNotFoundError`로 멈춘다. 나머지 하나인 `test_schedule_pythonw`는 `do_math`를 import하지 않으며, 앞의 블록 없는 3개에 속한다.

## 3. 시작 상태 체계

### 3.1 네 단과 판별 질문

`시험-지침.md` 4절 규칙 3은 새 시험이 출발할 상태를 아래 순서로 보고, 처음 성립하는 단을 쓰라고 정한다.

| 단 | 시작 상태 | 준비 비용 | 쓰는 경우 |
|---|---|---|---|
| 1 | 순수 함수나 검증기를 직접 호출한다 | 없음 | 저장소도 엔진도 필요 없는 규칙 |
| 2 | `restore_template(state_fixtures.active_instance, config=...)`: 합성 활성 상태 | 약 1초 | 활성화 뒤의 검증된 상태만 필요할 때 |
| 3 | `restore_template(research_fixtures.activated_instance, ...)`: 공개 활성화의 결과 | 첫 빌드 수십 초, 이후 복원 | 실제 해석 실행과 봉인 제출이 남긴 기록이 필요할 때 |
| 4 | 공개 초기화·활성화 경로를 처음부터 돈다 | 수십 초 | 그 경로 자체가 검사 대상일 때 |

2단과 3단의 차이는 상태를 만드는 방법에 있다. 2단 상태에서 합성된 것은 증거뿐이고, 그 증거를 검증하고 게시하는 경로는 제품 코드다. `engine_fixtures.FakeEngine`이 합성 증거 셋을 조립하고, 제품의 저장소 검증을 거쳐 Git에 게시한다. 세 증거는 모델 CLI 어댑터를 쓸 수 있다는 관찰, 승인된 Lean 도구 모음을 뜻하는 신뢰 환경, 사용자의 초기 입력을 해석한 실행의 결과다. 그래서 공개 초기화 절차가 동작한다는 것은 입증하지 않는다. 3단 상태는 실제 공개 `initialize`와 `activate`를 한 번 돌린 결과다.

4단을 유지할지는 다음 판별 질문으로 정한다. "활성화 과정에 결함이 있어도 활성화가 끝난 상태가 정상과 같다면, 이 시험은 실패해야 하는가?" 그렇다면 공개 경로를 유지한다. 템플릿에서 출발한 시험에는 최종 상태를 바꾸지 않는 활성화 결함이 드러나지 않기 때문이다. `research_fixtures` docstring은 공개 경로를 지키는 전용 시험으로 둘을 지목한다.

- `test_engine.EngineTests.test_public_initialization_reaches_active_with_distinct_interpretation`: 공개 `initialize`에서 시작한다. 공개 `control`로 헌장 승인, 권한, 프로브, 신뢰 환경 등록과 전환, 채택 결정을 채운다. 그다음 실제 해석 실행 둘(작성자와 검사자)을 거쳐 `active`에 이른다. 단언은 네 가지다. 상태가 `active`이고, 두 실행 ID가 서로 다르며, `capability_evidence`가 있고, `missing`이 빈 목록이다.
- `test_engine.PublicGitFlow.test_public_activation_work_receipt_assessment_and_next_plan`: 공개 활성화에서 시작해 연구 준비, 계약 검토, 계획, 연구 작업을 거친다. 모든 역할 출력은 실제 `submit_intent`로 보내지고, 시험은 그 수신증이 `accepted`인지 확인한다. 다음 계획의 평가가 과제를 완료하고 지식을 게시하며, 흐름은 Git 재적재로 끝난다.

여기에 3단 위의 빌드 `purpose_fixtures.solved_instance`가 더해진다. 이 빌드는 공개 활성화에서 출발해 목적 시나리오를 수학적 해결까지 몬다. `test_purpose_engine.SolvedPurposeTests`가 이 빌드를 읽는다.

### 3.2 템플릿 기계 `restore_template`

`research_fixtures.restore_template(build, **parameters)`는 `(root, value)`를 돌려준다. 동작 규칙은 다음과 같다. 세부는 [기반/픽스처/research_fixtures.md](기반/픽스처/research_fixtures.md)에 있다.

- **빌드 시점**: 한 프로세스 안에서 같은 빌드와 같은 매개변수로 처음 요청이 오면 `build(root, shared, **parameters)`를 한 번 돌린다. 이 빌드는 그 요청을 한 시험 안에서 돈다. 매개변수는 JSON 값이고 기본값까지 키에 들어간다.
- **복원**: 빌드가 끝나면 `research_fixtures`의 `_Template` 클래스가 빌드가 `root`(`live` 폴더)에 남긴 내용을 `pristine` 폴더로 복사해 둔다(`research_fixtures.py` 1023행). 같은 템플릿의 첫 요청은 사본이 아니라 이 `live` 폴더 자체를 받는다. 두 번째 요청부터는 `live`를 지우고 `pristine`에서 다시 복사한 것을 받는다(1028–1029행). 그래서 첫 시험이 폴더를 바꾸어도 다음 사본은 빌드 직후의 바이트로 돌아간다. 복사 대상에는 Git 객체와 참조, `runs/` 출력을 담은 작업 공간, 제어 수신함이 들어간다. `value`는 빌드가 돌려준 값의 깊은 사본이다.
- **같은 절대 경로**: 한 템플릿의 사본은 늘 같은 `root` 경로에 놓인다. 상태 안의 절대 경로와 그 경로에 걸린 해시가 참으로 남게 하기 위해서다. 그래서 새 사본을 요청하면 이전 사본이 대체된다. 시험은 한 엔진을 다 쓴 뒤에 다음 사본을 요청해야 한다.
- **`shared` 폴더**: 상태가 파일 지문을 기록하는 파일은 `shared` 아래에 둔다. 신뢰 도구 모음이 그 예다. 복사하면 생성 시각이 바뀌기 때문이다. `shared`는 복사하지도 지우지도 않으며, 빌드 뒤에는 읽기만 해야 한다. 이 규칙을 어기는 시험이 하나 있다(8절).
- **실패 전파**: 빌드가 실패하면 그 템플릿을 요청하는 이후의 모든 시험이 실패한다. 첫 시험은 원래 예외를 받고, 이후 시험은 템플릿 키만 담은 `AssertionError`를 받는다.
- **프로세스 한정**: 템플릿은 디스크에서 재사용하지 않는다. 설치 판본, 권한 만료, 시계 최고 기록을 담고 있기 때문이다. 빌드 뒤 경과 시간에 좌우되는 규칙은 공개 경로로 시험한다.
- **프로세스 안의 엔진 상태는 사본에 없다**: `_task_readiness` 같은 값은 새 엔진에서 다시 설정해야 한다.

### 3.3 공유 빌드와 더 깊은 빌드

| 빌드 | 정의 위치 | 출발 상태 | 결과 |
|---|---|---|---|
| `active_instance` | `state_fixtures` | 합성 조립 | 2단: 검증된 합성 활성 상태 |
| `activated_instance` | `research_fixtures` | 공개 `initialize`+`activate` | 3단: 첫 연구 단계 직전의 게시 상태 |
| `initialized_instance` | `engine_fixtures` | 공개 `initialize`만 | 초기화 직후 상태 |
| `solved_instance` | `purpose_fixtures` | `activated_instance` | 목적 시나리오를 수학적 해결까지 몬 상태(`AcademicRunner`) |
| `purpose_state` | `purpose_fixtures` | `active_instance` | 과제 `A`의 작업이 대기열에 오르거나(`until='prepared'`) 동일성 검토가 열린 상태(`'review'`) |
| `assessment_preparation_instance` | `purpose_fixtures` | `active_instance` | 학술 과제 둘이 모델 평가를 기다리는 상태 |
| 모듈 전용 빌드 13개 | 각 시험 모듈 | 아래 목록 밑의 설명 참조 | 모듈마다 docstring에 적힌 상태 |

여기서 어떤 빌드가 "2단 위에 쌓인다"는 것은 2단 빌드의 결과를 출발점으로 재사용한다는 뜻이며, 공개 경로를 다시 돌지는 않는다.

`purpose_state`를 예로 들면 다음과 같다. `restore_template`가 `purpose_state`를 빌드할 때 `root` 폴더를 넘긴다. `purpose_state`는 그 `root` 아래에서 `active_instance`를 `restore_template` 없이 직접 불러 2단 상태를 만든다. 그다음 `purpose_state`는 만들어진 2단 상태의 엔진을 목적 시나리오 러너(`PurposeRunner`)로 더 몰아, 과제 `A`의 작업이 대기열에 오르거나(`until='prepared'`) 동일성 검토가 열리는(`until='review'`) 지점에서 멈춘다. 이렇게 완성된 `root`의 내용 전체가 `purpose_state` 템플릿으로 보관된다.

더 깊은 빌드의 대부분은 3단이 아니라 2단 위에 쌓인다. 3단 위에 쌓이는 경우는 둘뿐이다. 하나는 공유 빌드 `solved_instance`다. 다른 하나는 모듈 전용 빌드 `ready_work`를 `public=True`로 부른 경우다(`test_session_scheduler.ParallelEngineTests`). `ready_work`를 기본값으로 부르면 2단 위에 쌓인다. 모듈 전용 빌드는 다음 13개다.
- `requirement_change_instance`(`test_academic_engine`)
- `cli_instance`(`test_cli`)
- `created_instance`(`test_cli_advanced`)
- `plan_ready_instance`(`test_currentness`)
- `efficiency_instance`(`test_engine`)
- `overflowed_maintenance`(`test_input_recovery`)
- `rejected_assessment_instance`(`test_model_assessment_flow`)
- `reviewed_task`, `parked_failed_plan`, `paused_limited_recovery`(`test_research_recovery`)
- `ready_work`(`test_session_scheduler`)
- `waiting_action`(`test_stop_flags`)
- `prepared_tasks`(`test_submission_boundaries`)

13개가 출발하는 상태는 세 갈래다.
- `active_instance`(2단)에서 출발: 10개. 이 가운데 `rejected_assessment_instance`는 2단에서 바로 출발하지 않고, 2단 위의 빌드인 `assessment_preparation_instance`를 먼저 만든 뒤 그 상태를 더 몬다.
- 부르는 인자에 따라 달라짐: `ready_work` 1개. 기본은 `active_instance`에서, `public=True`로 부르면 `activated_instance`(3단)에서 출발한다.
- 공개 CLI 초기화에서 출발: `cli_instance`, `created_instance` 2개.

### 3.4 실제 분포

네 단은 새 시험을 쓸 때의 선택 순서다. 기존 시험의 출발 상태는 이보다 다양하다. 아래 수치는 모듈 문서를 쓰고 대조하는 과정에서 모듈 무리별로 어림한 값을 합친 것이다. 기계로 센 값이 아니므로 크기의 감각으로만 읽는다. 범주는 시험의 주된 출발 상태로 나눈 것이다. 메모리 엔진 대역이 실제 Git에 게시하는 시험처럼 두 범주에 걸치는 시험이 있어 범주가 서로 배타적이지 않고, 합계도 1,931과 정확히 맞지 않는다.

| 출발 상태 | 대략의 테스트 수 | 주로 있는 곳 |
|---|---:|---|
| 1단: 순수 함수·검증기·사전 상태 | 약 900 | `foundation` 전반. 거버넌스, 과제 계약, 제출 검사, 지식 도메인 |
| 메모리 엔진 대역(`FakeEngine`, `routing_engine`, `bare_engine`, `ReviewFakeEngine` 등) | 약 400 | 엔진의 상태 전이 규칙(`lifecycle`, `review`) |
| 실제 Git 저장소에 직접 조립·게시한 상태 | 약 250 | 저장 계층, 기록 가족, 지식 저장 |
| 2단·3단 템플릿과 그 위의 빌드 | 약 200 | `research`, `review`, `lifecycle`, `academic` |
| 실제 프로세스·Job·Lean을 직접 다루는 구성 | 약 150 | `host` |
| 4단 공개 경로 | 수십 | 초기화·활성화 전용 시험, CLI 초기화 |

같은 성질을 층을 바꾸어 두 번 검사하는 짝이 많다. 순수 함수나 메모리 엔진 층에서 규칙을 보고, 공개 제어나 Git 재적재 층에서 연결을 다시 보는 식이다. 예:
- `test_formal_engine`의 `FormalContinuationTests`(메모리 엔진) ↔ `FormalAttemptLineageTests`(공개 제어와 재적재)
- `test_governance_engine`의 `CentralGovernanceTests`(메모리 엔진) ↔ `PublicGitGovernanceTests`(실제 Git과 공개 제어)
- `test_input_recovery`의 `OverflowConnections` ↔ `OverflowGitConnection`(실제 Git)

모듈 문서의 머리 표는 모듈마다 이 분포를 적고, 클래스 절은 클래스마다 출발 상태를 적는다.

## 4. 픽스처 층

### 4.1 아홉 모듈

| 모듈 | 행 | 정의 | 쓰는 시험 모듈 | 맡는 것 |
|---|---:|---:|---:|---|
| [`research_fixtures`](기반/픽스처/research_fixtures.md) | 1,129 | 58 | 85 | 모든 영역이 쓰는 입력(과제 후보, 검토 출력, 헌장과 승인, 신뢰 환경, 관찰 규칙, 시계), 자식 프로세스를 대신하는 도우미 `git_init`·`run_cli`, 스크립트 러너 호출마다 실제 Windows Job 자식을 띄우는 `local_job_runner`, 공개 활성화 `activate`, `restore_template`와 3단 빌드 |
| [`state_fixtures`](기반/픽스처/state_fixtures.md) | 147 | 6 | 20 | 2단 빌드 `active_instance`, 그 사본을 주는 `active_repository`·`start_active_copy`, 소유자 루프 도우미 `owner_calls`·`start_model_call` |
| [`engine_fixtures`](기반/픽스처/engine_fixtures.md) | 813 | 32 | 33 | 메모리 엔진 대역 `FakeEngine`, 응답 경로용 `routing_engine`, 역할 문맥용 `context_engine`, Git 기반 시작 상태 `start_submission_history`·`start_query_repository`·`start_repair_host` |
| [`runner_fixtures`](기반/픽스처/runner_fixtures.md) | 180 | 6 | 14 | 모든 역할에 가장 작은 유효 출력으로 답하는 `ScriptedRunner`, 컴파일러 대역 `formal_ok` |
| [`purpose_fixtures`](기반/픽스처/purpose_fixtures.md) | 609 | 18 | 16 | 목적 시나리오 `PurposeRunner`(자연수 항등식 하나의 증명), 하네스 `PurposeHarness`·`ActivatedPurposeHarness`, 더 깊은 빌드 셋 |
| [`record_fixtures`](기반/픽스처/record_fixtures.md) | 393 | 25 | 39 | 순수 도메인 함수용 사전 기록(거버넌스, 과제 계약, 제출, 표면 상태) |
| [`knowledge_fixtures`](기반/픽스처/knowledge_fixtures.md) | 189 | 10 | 10 | 지식 후보와 합성 형식 증거, 작은 지식 그래프, 형식 경계 엔진 |
| [`review_fixtures`](기반/픽스처/review_fixtures.md) | 542 | 12 | 13 | 동일성 검토 엔진 대역 `ReviewFakeEngine`, 순수 검토 주기, 검토 하네스 셋 |
| [`provider_fixtures`](기반/픽스처/provider_fixtures.md) | 236 | 16 | 22 | 공급자·호스트·외부 서비스 경계의 대역(`Adapter`, `FakeJob`, `PROFILE_CONFIG`, `provider_repository`, `actual_command`, `HTTPFixtureHandler`) |

"정의"는 모듈 수준의 함수와 클래스 수다. "쓰는 시험 모듈"은 원문의 import와 속성 접근을 AST로 센 값이다.

### 4.2 의존 구조

`research_fixtures`가 뿌리다. 나머지 여덟 모듈이 모두 이것을 import한다. 거꾸로 `research_fixtures`가 다른 픽스처 모듈을 import하는 곳은, `activated_instance` 안에서 `runner_fixtures.ScriptedRunner`를 늦게 import하는 한 곳뿐이다. 이 import는 함수 안에서 일어나므로 import 순환이 생기지 않는다. 그 위에 다음 관계가 쌓인다.

- `engine_fixtures`는 `record_fixtures`와 `knowledge_fixtures`를 쓴다.
- `state_fixtures.active_instance`는 `engine_fixtures.FakeEngine.activate`로 합성 활성 상태를 조립한다. 따라서 2단 체계 전체가 `engine_fixtures` 위에 서 있다.
- `purpose_fixtures`는 `state_fixtures`와 `runner_fixtures.formal_ok`를 쓴다.
- `review_fixtures`는 `engine_fixtures`, `knowledge_fixtures`, `record_fixtures`를 쓴다.
- `knowledge_fixtures.formal_result`는 합성 형식 증거를 만드는 주된 원천이다. `runner_fixtures.formal_ok`, `engine_fixtures`, `review_fixtures`가 이것을 쓴다. 다만 `review_fixtures`는 의존 폐포와 증거 필드 일부를 직접 만든다.
- `provider_fixtures`는 `research_fixtures.current_state` 하나에만 기댄다.

### 4.3 대역의 원칙

아홉 모듈의 대역은 한 원칙을 따른다. **답을 만드는 쪽만 합성하고, 답을 받는 쪽은 제품 코드를 그대로 쓴다.**

- **엔진 대역도 제품 `ResearchEngine`이다.** 엔진 대역 넷은 모두 제품 엔진 클래스의 객체이고, 만드는 방법만 다르다.
  - `FakeEngine`, `ReviewFakeEngine`: `ResearchEngine`의 하위 클래스다. 자기 `__init__`에서 제품의 `__init__` 대신 `_init_process_state()`만 부르고 저장소 대역을 붙인다.
  - `bare_engine`: `object.__new__(ResearchEngine)`로 제품의 `__init__` 없이 객체를 만든 뒤 `_init_process_state()`를 부른다.
  - `routing_engine`: `bare_engine`에 `NoRepository` 저장소를 붙이고 메서드 몇 개를 autospec으로 바꾼 것이다.

  `_init_process_state()`(`engine.py` 454행)는 엔진을 돌리는 프로세스 하나가 메모리에만 들고 있고 저장소에는 쓰지 않는 값들을 초기화한다. 과제 준비성 계산 결과, 지금 실행 중인 실행의 ID, 작업자와 엔진이 제어 요청을 주고받는 통로의 연결 정보, 수명 시계와 그 기준점 등이 여기에 든다. 네 대역 모두 이 초기화를 거친다.

  제품과 달라지는 것은 대개 저장소와 저장(`_save`)이다. 저장소 대역은 다섯이다: 메모리 `StateStore`, 쓰기를 거부하는 `NoRepository`, 입력 스냅숏 저장소, `ResearchRepository`의 autospec, `ReviewFakeEngine`이 쓰는 아티팩트를 하나도 읽지 못하는 최소 저장소(`SimpleNamespace`).
- **스크립트 러너의 출력은 실제 생산자 경로를 지난다.** `ScriptedRunner`와 `PurposeRunner`는 역할의 실제 입력에서 답을 만든다. 그 답은 실제 작업자가 거치는 네 단계를 똑같이 거친다.
  - 후보 결속(`research_fixtures.bind_candidates`): 과제 후보에 작성자에게 실제로 제공된 작업 프로필과 현재 유효한 권한 부여만 참조로 붙인다.
  - 응답 봉인(`research_fixtures.seal_response`): 함께 제출되는 조각들의 목록을 선언한다. 목록에는 출력 전체, 연구 작업이면 출력의 지식·관계 행 각각, 작업 공간의 `activity-extensions.json`에 적힌 행 각각이 들어간다. 이 목록이 한 묶음으로 제출된다는 선언이 봉인이고, 행동·출력·확장의 내용 해시로 `IN-` 식별자를 만든다.
  - JSON 스키마 검증: 역할의 출력 스키마로 답을 검사한다.
  - 제어 수송(`research_fixtures.submit_intent`): 출력을 파일로 쓰고, 제품의 `submission.request_control`로 제출 의향을 보낸다. 그다음 `ControlTransport.wait_receipt`로 엔진의 수신증을 60초까지 기다리고, 수신증이 `accepted`가 아니면 실패한다.

  앞의 두 단계는 작업자의 동작을 재현한 픽스처 도우미이고, 수송 단계는 제품 코드를 그대로 쓴다. 그래서 엔진이 받는 것은 실제 제출과 같은 모양이다.
- **대역 안에 검사가 있다.** 러너와 픽스처는 엔진이 넘긴 입력이 계약에 맞지 않으면 `AssertionError`를 낸다. 예를 들어 `PurposeRunner`의 목표 감사 응답은 효력 있는 최종 판정만 받았는지 검사한다. 이런 검사는 엔진을 끝까지 몰아야만 도는 경우가 있다. 그래서 `시험-지침.md` 4절 규칙 4는 그런 시험을 조기에 멈추지 말라고 한다.
- **합성 증거는 합성임을 숨기지 않는다.** 어댑터 관찰, Lean 결과, 사용자 승인에 해당하는 픽스처 값은 합성 시험 증거다. 호스트 능력, 실제 컴파일 결과, 실제 사용자의 승인을 입증하지 않는다(`research_fixtures` docstring).

## 5. 실행, 격리, 외부 자원

### 5.1 실행기

`run_tests.py`는 `tests/test_*.py`를 `unittest` discovery로 모은다. 그다음 조각, 시험 ID(모듈·클래스·메서드 접두), glob 조건으로 고르고, `SHARDS` 순서대로 돌린다. 결과는 매번 새 출력 폴더의 `report.json`에 쓴다. 이 파일에는 시험별 결과와 시간, 조각 시간, 실행 전 판본의 파일별 해시, 실행 중 변경 목록이 들어간다. 시험 하나가 실패하면, 다음 시험이 시작되기 전에 그 실패가 해당 조각의 결과 폴더(`<출력 폴더>/<조각>/`, 격리 실행이면 `<출력 폴더>/<조각>-isolated-<번호>/`)의 `failures/` 아래에 즉시 게시된다. 실행이 중간에 끊겨도 실패 증거가 남게 하려는 것이다. 결과를 재사용하는 캐시는 없다.

실행기가 통과를 세우지 않는 경우는 다음과 같다.
- 조각 등록 누락이나 유령 등록
- 수집 중 import 오류
- 어떤 시험에도 맞지 않는 ID
- 빈 선택
- 비어 있지 않은 출력 폴더
- 준비 단계 실패로 시작하지 않은 시험
- 격리 작업자의 시간 초과나 미완료
- 실행 중 `.py` 파일 변경

같은 모듈이 두 조각에 적히면 `SHARDS`에 뒤에 적힌 조각에 조용히 배정되고 검출되지 않는다. 판정 규칙 전부와 행 좌표는 [기반/실행기.md](기반/실행기.md)에 있다.

### 5.2 격리 표지와 실제 자원 사용의 차이

격리 표지 `test_group('lean')`과 `test_group('resource')`가 붙은 시험 29개는 실행기가 따로 처리한다. 클래스 단위로 Windows Job이 소유한 별도 프로세스에서 돌고, 시험 하나와 준비·종료 단계마다 기본 300초의 제한 시간이 걸린다. 표지는 대개 `category`라는 별칭으로 붙는다(`from test_categories import test_group as category`).

| 모듈 | lean | resource |
|---|---:|---:|
| `test_formal` | 6 | |
| `test_formal_runtime` | 4 | 1 |
| `test_knowledge_import_engine` | 6 | |
| `test_knowledge_storage` | 2 | |
| `test_knowledge` | 1 | |
| `test_lean_preview` | 1 | |
| `test_machine_parallel` | | 3 |
| `test_host_resources` | | 2 |
| `test_live_observation` | | 1 |
| `test_owned_job_children` | | 1 |
| `test_schedule_lifetime` | | 1 |

**격리 표지는 실제 외부 자원을 쓰는 시험 전부를 가리키지 않는다.** 표지는 실행기가 외부에서 수명과 시간을 관리해야 하는 시험만 가리킨다. 표지 없이 실제 자원을 쓰는 시험도 실행기 프로세스 안에서 돌며, 프로세스 수준의 시간 상한 없이 돈다. 다음이 그런 경우다.

- **Windows Job 자식 프로세스**
  - `research_fixtures.local_job_runner`는 러너 메서드를 감싼다. 러너가 시작을 알리면 실제 Windows Job 안에 잠자는 Python 자식(`time.sleep(600)`)을 하나 띄운다. 답 자체는 시험 프로세스 안에서 만들어진다. `ScriptedRunner`, `PurposeRunner`, `CheckedRunner`와 여러 지역 러너가 이 데코레이터를 쓴다. 따라서 이 러너로 엔진을 모는 시험과 `activated_instance`, `solved_instance`, `purpose_state` 빌드는 모두 호출마다 실제 Job을 만든다.
  - `test_stop_flags`의 16개, `test_windows_job` 전체, `test_launch_recovery`, `test_owned_job_children`의 표지 없는 3개도 실제 Job을 쓴다.
- **Git 자식 프로세스**
  - 제품 `GitStateStore`는 생성할 때 `git rev-parse`를 부르고, 읽을 때 `cat-file`을, 모르는 부모 트리가 있으면 `ls-tree`를, 게시할 때 참조를 옮기는 `update-ref`를 자식 프로세스로 부른다. 게시할 때 블롭·트리·커밋 객체는 프로세스 안에서 쓴다.
  - 그래서 실제 저장소에 닿는 모든 시험이 `git` 자식 프로세스를 띄운다. `research_fixtures.git_init`는 프로세스당 한 번만 `git init`을 돌리고, 이후에는 `.git`을 복사한다.
- **그 밖의 자식 프로세스와 자원**
  - `do_math.py` CLI의 자식 실행: 종료 코드와 인코딩이 검사 대상인 곳
  - `probe_cli.py`와 스킬 복사
  - MCP 서버와의 JSON-RPC 왕복
  - `read_input.py` 도구(`role_reach`)
  - `pythonw`와 PowerShell(`test_schedule_*`)
  - `multiprocessing`(`test_provider_wait`)
  - 루프백 HTTP 서버(`HTTPFixtureHandler`)
  - `cmd.exe mklink /J` 접합점

### 5.3 환경 전제

- **Windows**: 시험 체계는 Windows를 전제한다. 격리는 Windows Job으로 이루어진다. 모델 실행 슬롯을 잡는 `SessionSlots.acquire`와 `dispatched_launch`는 `launch.ticket`에서 `windows_job.owner_identity()`로 Windows API를 부른다. 비Windows에서 `unittest.skipUnless(os.name == 'nt')`로 명시적으로 건너뛰는 시험은 일부뿐이다. 그런 시험은 대부분 `host` 조각에 있고, 그 밖에는 `test_owned_job_children`(클래스 전체), `test_retention`의 1개, `test_session_scheduler`의 1개다. Windows 기능에 닿는 나머지 시험(모델 슬롯을 잡는 시험, 실제 Job을 띄우는 시험 등)은 비Windows 환경에서 건너뛰지 않고 오류가 난다.
- **Lean 도구 모음**: 실제 Lean 시험은 대부분 `provider_fixtures.actual_command()`로 컴파일러를 찾는다. `test_knowledge`의 Lean 시험은 같은 규칙을 모듈 안에서 직접 계산한다. 이 규칙은 환경변수 `DO_MATH_KNOWLEDGE_TEST_LEAN`이 있으면 그 경로를, 없으면 저장소 루트의 `.skill-workspace/do-math-toolchains`를 쓴다. 이 폴더는 Git이 추적하지 않으므로 git worktree에는 없다. 도구 모음이 없을 때의 동작은 시험마다 다르다.
  - 건너뛰는 시험: `test_knowledge`의 1개, `test_knowledge_import_engine`의 6개.
  - 실패하는 시험: `test_knowledge_storage`의 2개와 `host` 조각의 Lean 시험 다수.
  - `test_formal.ToolchainContractTests.test_inspection_matches_actual_formal_verifier`: 환경변수를 보지 않고 `toolchain_root()`를 직접 쓰므로 worktree에서는 늘 건너뛴다.
- **시계와 대기**: 대부분의 시간 의존 동작은 시계를 주입하고, 조건을 폴링하되 상한을 둔다. 고정 대기 `time.sleep(1.05)`는 두 곳에 남아 있다. `purpose_fixtures` 157행의 관찰 분기와 `test_submission_tools`의 호출 시간 초과 시험이다.

### 5.4 시험 통과가 입증하는 범위

- **모델의 답**: 모든 역할의 답은 `ScriptedRunner`, `PurposeRunner`, 또는 시험 안의 지역 러너가 만든 대본이다. 실제 모델을 부르는 시험은 없다.
- **컴파일러 결과**: 실제 Lean을 부르는 시험은 `lean` 표지가 붙은 20개가 중심이다. 테스트마다 실제 도구 모음을 부르는지는 각 모듈 문서의 대역·비고 항목에 적혀 있다. 나머지 형식 검증은 합성 결과(`formal_ok`, `formal_result`)나, Lean 명령을 흉내 내는 Python 스크립트를 쓴다.
- **신뢰와 승인**: 신뢰 환경, 어댑터 관찰, 사용자 승인은 픽스처가 만든 합성 증거다.

따라서 전체 통과가 입증하는 것은 제품의 상태 규칙, 계약 검사, 저장, 게시, 제어 수송, 복구 경로가 합성 입력 위에서 명세대로 도는 것이다. 실제 모델 연구의 품질이나 실제 수학 성과는 이 시험들의 범위 밖이다. 이 판본을 커밋한 작업의 기록(저장소의 작업 기억 노드 `기억/layer1/M-0357.md` 47행)에 따르면, 그 작업의 마지막 통합 확인은 발견 1,931, 통과 1,930, 건너뜀 1, 실패 0이었다. 이 지도는 그 결과를 다시 확인하지 않았다.

## 6. 제품 영역별 대응

아래 표는 시험 모듈을 주로 검사하는 제품 영역에 한 번씩 배정한 것이다. 배정은 모듈 문서의 목적 절에 따른 이 지도의 분류다. 한 모듈이 여러 영역에 걸치는 경우가 많으므로, 경계의 세부는 각 모듈 문서의 머리 표("시험 대상 제품 코드")와 관계 절을 본다. 괄호 안은 조각과 테스트 수다.

| 영역 | 주요 제품 모듈 | 시험 모듈(조각, 테스트 수) | 테스트 |
|---|---|---|---:|
| 저장소와 상태 계약 | `git_store`, `repository`, `state_contract`, `state_checks`, `file_io`, `payloads` | [`git_store`](모듈/test_git_store.md) (foundation 31), [`repository`](모듈/test_repository.md) (foundation 30), [`state_contract`](모듈/test_state_contract.md) (foundation 7), [`state_checks`](모듈/test_state_checks.md) (foundation 23), [`family_records`](모듈/test_family_records.md) (foundation 75), [`file_io`](모듈/test_file_io.md) (foundation 8), [`json_digests`](모듈/test_json_digests.md) (foundation 6), [`unicode_flow`](모듈/test_unicode_flow.md) (foundation 5), [`payloads`](모듈/test_payloads.md) (foundation 6), [`query_records`](모듈/test_query_records.md) (foundation 4), [`retention`](모듈/test_retention.md) (foundation 13), [`reporting`](모듈/test_reporting.md) (foundation 8), [`context_store`](모듈/test_context_store.md) (foundation 35), [`cli_surface`](모듈/test_cli_surface.md) (foundation 2) | 253 |
| 계약과 제출 | `contracts`, `submission`, `integration`, `formal_preview` | [`contracts`](모듈/test_contracts.md) (foundation 16), [`contract_checks`](모듈/test_contract_checks.md) (foundation 11), [`submission_checks`](모듈/test_submission_checks.md) (foundation 36), [`submission_flow`](모듈/test_submission_flow.md) (review 34), [`submission_tools`](모듈/test_submission_tools.md) (review 34), [`submission_boundaries`](모듈/test_submission_boundaries.md) (review 11), [`native_final_submission`](모듈/test_native_final_submission.md) (review 11), [`reference_catalog`](모듈/test_reference_catalog.md) (foundation 4), [`preparation_cache`](모듈/test_preparation_cache.md) (foundation 3), [`integration_bundles`](모듈/test_integration_bundles.md) (foundation 18), [`completion_settlement`](모듈/test_completion_settlement.md) (foundation 6), [`lean_preview`](모듈/test_lean_preview.md) (host 6) | 190 |
| 거버넌스, 목표 감사, 질문 | `governance`, `governance_engine`, `questions`, `question_engine`, `delegations`, `input_basis` | [`governance`](모듈/test_governance.md) (foundation 41), [`governance_engine`](모듈/test_governance_engine.md) (lifecycle 31), [`goal_audit`](모듈/test_goal_audit.md) (foundation 12), [`questions`](모듈/test_questions.md) (foundation 14), [`question_flow`](모듈/test_question_flow.md) (review 4), [`delegations`](모듈/test_delegations.md) (foundation 11), [`decision_basis`](모듈/test_decision_basis.md) (foundation 13), [`initial_intent_connection`](모듈/test_initial_intent_connection.md) (lifecycle 6) | 132 |
| 계획과 과제 | `planning`, `planning_engine`, `task_contracts`, `task_scope`, `revisions`, `relation_refs` | [`planning`](모듈/test_planning.md) (foundation 21), [`planning_engine`](모듈/test_planning_engine.md) (lifecycle 10), [`task_contracts`](모듈/test_task_contracts.md) (foundation 61), [`task_scope`](모듈/test_task_scope.md) (foundation 8), [`task_completion`](모듈/test_task_completion.md) (lifecycle 10), [`revision_obligations`](모듈/test_revision_obligations.md) (foundation 7), [`relation_dependencies`](모듈/test_relation_dependencies.md) (foundation 5), [`repetition`](모듈/test_repetition.md) (review 10), [`reading_map`](모듈/test_reading_map.md) (foundation 7) | 139 |
| 지식과 형식 검증 | `knowledge`, `knowledge_io`, `knowledge_engine`, `knowledge_records`, `formal`, `formal_engine` | [`knowledge`](모듈/test_knowledge.md) (foundation 57), [`knowledge_io`](모듈/test_knowledge_io.md) (foundation 12), [`knowledge_storage`](모듈/test_knowledge_storage.md) (foundation 12), [`knowledge_import_engine`](모듈/test_knowledge_import_engine.md) (foundation 15), [`reassessment`](모듈/test_reassessment.md) (foundation 21), [`impact_review`](모듈/test_impact_review.md) (foundation 13), [`currentness`](모듈/test_currentness.md) (research 13), [`formal`](모듈/test_formal.md) (host 32), [`formal_runtime`](모듈/test_formal_runtime.md) (host 8), [`formal_engine`](모듈/test_formal_engine.md) (lifecycle 11), [`formal_input_manifest`](모듈/test_formal_input_manifest.md) (foundation 1) | 195 |
| 동일성 검토 | `review_cycle`, `review_policy`, `review_engine` | [`review_cycle`](모듈/test_review_cycle.md) (foundation 24), [`review_policy`](모듈/test_review_policy.md) (foundation 12), [`review_scope_wire`](모듈/test_review_scope_wire.md) (foundation 6), [`review_engine`](모듈/test_review_engine.md) (review 58), [`review_research`](모듈/test_review_research.md) (review 17) | 117 |
| 엔진 수명, 제어, CLI | `engine`, `lifecycle_engine`, `control_contracts`, `control_transport`, `cli`, `operation_trace` | [`engine`](모듈/test_engine.md) (lifecycle 32), [`lifecycle_engine`](모듈/test_lifecycle_engine.md) (lifecycle 73), [`lifecycle_gates`](모듈/test_lifecycle_gates.md) (foundation 15), [`controls`](모듈/test_controls.md) (lifecycle 24), [`control_shapes`](모듈/test_control_shapes.md) (lifecycle 13), [`control_transport`](모듈/test_control_transport.md) (foundation 18), [`stop_flags`](모듈/test_stop_flags.md) (lifecycle 16), [`checkpoint_persistence`](모듈/test_checkpoint_persistence.md) (lifecycle 5), [`input_recovery`](모듈/test_input_recovery.md) (lifecycle 10), [`cli`](모듈/test_cli.md) (lifecycle 27), [`cli_advanced`](모듈/test_cli_advanced.md) (lifecycle 6), [`role_input`](모듈/test_role_input.md) (lifecycle 58), [`operation_trace`](모듈/test_operation_trace.md) (lifecycle 5), [`purpose_engine`](모듈/test_purpose_engine.md) (research 19), [`design_walkthroughs`](모듈/test_design_walkthroughs.md) (foundation 15) | 336 |
| 초기화, 신뢰 환경, 설치 수리 | `initialization`, `trust_validation`, `trust_inventory`, `preflight`, `repair_execution`, `configuration` | [`environment_validation`](모듈/test_environment_validation.md) (foundation 23), [`trust_continuation`](모듈/test_trust_continuation.md) (foundation 2), [`installation_discovery`](모듈/test_installation_discovery.md) (foundation 4), [`initialization_probe_batch`](모듈/test_initialization_probe_batch.md) (lifecycle 8), [`observation_admission`](모듈/test_observation_admission.md) (lifecycle 8), [`diagnosed_installation_recovery`](모듈/test_diagnosed_installation_recovery.md) (host 8), [`repair_execution`](모듈/test_repair_execution.md) (foundation 11), [`preflight`](모듈/test_preflight.md) (host 10), [`configuration`](모듈/test_configuration.md) (foundation 3) | 77 |
| 실행 프로필, 모델 공급자, 관찰 | `execution_profiles`, `execution_lifecycle`, `execution_window`, `model_runner`, `claude_adapter`, `codex_adapter`, `observations` | [`execution_profiles`](모듈/test_execution_profiles.md) (foundation 34), [`execution_lifecycle`](모듈/test_execution_lifecycle.md) (foundation 15), [`execution_window`](모듈/test_execution_window.md) (foundation 3), [`model_runner`](모듈/test_model_runner.md) (foundation 10), [`claude_adapter`](모듈/test_claude_adapter.md) (foundation 12), [`claude_stream`](모듈/test_claude_stream.md) (foundation 8), [`codex_adapter`](모듈/test_codex_adapter.md) (foundation 15), [`provider_final_contract`](모듈/test_provider_final_contract.md) (foundation 3), [`model_metadata_boundary`](모듈/test_model_metadata_boundary.md) (foundation 6), [`provider_wait`](모듈/test_provider_wait.md) (host 6), [`provider_recovery`](모듈/test_provider_recovery.md) (lifecycle 4), [`observations`](모듈/test_observations.md) (foundation 61), [`live_observation`](모듈/test_live_observation.md) (lifecycle 21), [`worker_temporary_outputs`](모듈/test_worker_temporary_outputs.md) (host 1) | 199 |
| 스케줄링, 호스트 자원, 복구 | `scheduler`, `session_slots`, `parallel`, `budget`, `windows_job`, `launch` | [`session_scheduler`](모듈/test_session_scheduler.md) (research 41), [`machine_scheduling`](모듈/test_machine_scheduling.md) (foundation 4), [`machine_parallel`](모듈/test_machine_parallel.md) (host 22), [`budget`](모듈/test_budget.md) (foundation 5), [`host_resources`](모듈/test_host_resources.md) (host 23), [`windows_job`](모듈/test_windows_job.md) (host 8), [`owned_job_children`](모듈/test_owned_job_children.md) (foundation 4), [`background_processes`](모듈/test_background_processes.md) (host 3), [`launch_recovery`](모듈/test_launch_recovery.md) (host 4), [`supervisor_recovery`](모듈/test_supervisor_recovery.md) (foundation 6), [`research_recovery`](모듈/test_research_recovery.md) (research 48) | 168 |
| 운영자 예약과 스킬 배포 | `scheduled_operator`, `operator_bootstrap.py`, `operator_schedule.ps1`, `probe_cli.py` | [`operator`](모듈/test_operator.md) (host 22), [`operator_bootstrap`](모듈/test_operator_bootstrap.md) (host 4), [`schedule_lifetime`](모듈/test_schedule_lifetime.md) (host 1), [`schedule_pythonw`](모듈/test_schedule_pythonw.md) (host 2), [`probe_cli`](모듈/test_probe_cli.md) (host 3), [`standalone`](모듈/test_standalone.md) (foundation 3) | 35 |
| 학술 요건과 외부 작업 | `academic`, `academic_engine`, `external`, `external_engine`, `scholarly`, `model_policy` | [`academic`](모듈/test_academic.md) (foundation 17), [`academic_engine`](모듈/test_academic_engine.md) (academic 11), [`academic_preparation`](모듈/test_academic_preparation.md) (academic 8), [`model_assessment_flow`](모듈/test_model_assessment_flow.md) (academic 22), [`external`](모듈/test_external.md) (host 10), [`external_operations`](모듈/test_external_operations.md) (foundation 6), [`scholarly`](모듈/test_scholarly.md) (foundation 5) | 79 |
| 시험 실행기 | `run_tests.py`, `test_categories.py` | [`test_runner`](모듈/test_test_runner.md) (foundation 11) | 11 |

같은 제품 기능이 여러 층의 모듈에 나뉘어 있는 경우가 많다. 층의 조합은 영역마다 다르다.

| 영역 | 1단이나 대역 층 | 엔진·Git·공개 층 |
|---|---|---|
| 거버넌스 | `test_governance`, `test_goal_audit`(`foundation`, 사전 기록과 믹스인 직접 호출) | `test_governance_engine`(`lifecycle`) |
| 계획 | `test_planning`, `test_task_contracts`, `test_task_completion` | `test_planning_engine`(메모리 엔진 대역) |
| 지식 | `test_knowledge`, `test_knowledge_io`(순수 도메인) | `test_knowledge_storage`(Git 왕복), `test_knowledge_import_engine`(엔진 제어와 중앙 형식 소비자), `lean` 표지 시험(실제 Lean) |
| 검토 | `test_review_cycle`, `test_review_policy`(순수 주기) | `test_review_engine`, `test_review_research` |
| 기록 가족 | `test_family_records` | 여러 도메인 생산자의 결과를 저장 계약 쪽에서 본다. 도메인 규칙 자체는 각 도메인 모듈이 본다 |

## 7. 반복되는 시험 기법

- **호출 수 관측**: `patch.object(대상, 이름, wraps=원래 함수)`로 제품 함수를 감싸 호출 횟수를 센다. "한 번만 읽는다·해시한다·검증한다" 같은 비용 성질을 단언하는 방법이다(`test_repository`, `test_git_store`, `test_payloads`, `test_submission_checks`). 이 기법은 패치 대상이 실제 호출 경로와 같은 모듈일 때만 유효하다. 다른 모듈을 패치한 예가 하나 있다(8절).
- **autospec 대역**: `create_autospec`으로 엔진 메서드나 `ResearchRepository`를 대체한다. 호출 여부와 순서를 기록하거나, 불리면 실패하게 해서 "하지 않음"을 단언한다.
- **사본 대조**: 입력이나 상태의 `deepcopy`나 `canonical_json`을 떠 두고, 거부나 미리보기 뒤에 바뀌지 않았는지 비교한다. 원자성과 읽기 전용을 보이는 방법이다.
- **CAS 실패 흉내**: `_save`에 `side_effect=ValueError("CAS")`를 걸어 게시 원자성을 본다.
- **비밀 문자열 누출 검사**: 입력에 `PRIVATE-...` 문자열을 심는다. 그다음 `role_reach`가 역할이 그 문자열에 실제로 닿은 곳(`reached`: 프롬프트, 작업 공간 파일, 읽기 도구 요청)과, 입력 스냅숏에서 그 문자열을 담은 파일(`held`)을 보고한다. `held`가 비어 있으면 스냅숏에 비밀이 없었던 것이므로 `reached`가 비어도 아무것도 입증하지 않는다.
- **변조 뒤 거부**: 생산자 왕복으로 만든 기록의 필드 하나를 바꾼 뒤, 검증기가 그 영역의 사유로 거부하는지 본다(`test_family_records`). 검증을 우회하려고 `_store.publish`로 손상된 커밋을 직접 게시하는 시험도 있다(`test_family_records`, `test_repository`, `test_unicode_flow` 등).
- **유니코드 정규형 쌍**: 분해형 `e`+U+0301과 완성형 U+00E9, 켈빈 기호 U+212A와 라틴 `K`, CRLF. 원 바이트가 정규화 없이 보존되는지를 본다. 편집기에서는 두 키가 같아 보이므로 원문을 읽을 때 주의한다.
- **시계 주입과 한정 폴링**: `Clock`, `lifecycle_clock`, `ObservationTracker(clock=)`, `session_slots.time.time` 패치 등으로 시계를 주입한다. 다른 스레드나 프로세스의 결과는 상한(5–60초)을 둔 폴링으로 기다린다.
- **`subTest` 표**: 거부 원인이나 변형을 표로 나열한다. `test_control_shapes`의 공개 행동 70 사례가 그 예다.
- **조기 정지**: `PurposeHarness.drive(engine, predicate, limit=45)`는 조건이 참이 되면 멈춘다. 그 전에 흐름이 `paused`, `closed`, `waiting`이 되면 시험을 실패시킨다. 목표 판정이 단언 대상이거나 러너 안의 검사가 뒤에서 도는 경우에만 끝까지 몬다.

## 8. 원문에서 확인된 주의점

지도를 쓰고 대조하는 과정에서 원문 시험의 한계가 여럿 확인되었다. 이 절은 제품 결함이 아니라 **시험이 무엇을 입증하지 못하는지**를 모은 것이다. 모든 항목은 독립 대조에서 원문 좌표로 확인되었다. 개별 사항은 해당 모듈 문서의 비고에 있다.

### 8.1 넓게 나타나는 경향

- **이름이 단언보다 넓다.** 이름이 말하는 성질의 일부만 단언하는 시험이 여러 모듈에 있다. 예를 들어 이름은 "여섯 처분"을 말하는데 키가 있는지만 보는 경우, 이름은 거부 쪽도 말하는데 받아들이는 경로만 보는 경우가 있다. 모듈 문서는 이런 시험의 비고에 "이름은 X를 말하지만 단언은 Y만 확인한다"고 적는다.
- **음성 시험이 거부 사유를 고정하지 않는다.** 많은 거부 시험, 특히 `foundation`의 거버넌스와 과제 계약 시험은 `assertRaises(ValueError)`로 예외 유형만 본다. 정규식 조각을 보더라도 그 조각이 여러 제품 문구에 공통으로 들어 있는 경우가 있다. 이때 입력이 의도한 규칙이 아니라 앞선 다른 검사에서 거부되어도 시험은 통과한다. 모듈 문서는 입력을 실제로 거부하는 제품 분기를 따라가 비고에 적었다.

### 8.2 개별 사항

| 위치 | 확인된 사실 | 영향 |
|---|---|---|
| `test_submission_flow.py` 939–978 (`test_sealed_response_waits_for_a_record_change_after_a_failed_identity_check`) | 이 시험은 템플릿의 `shared` 폴더를 두 번 고친다. (1) 합성 `lake.exe`를 덮어쓰고, 시험이 끝까지 성공한 경우에만 원래 바이트로 되돌린다(`try`/`finally`가 없다). (2) `setup_lean.rerecord`로 도구 모음 기록에 기준선을 더하고 `records/.lock`을 남기는데, 이 둘은 어떤 경우에도 되돌리지 않는다. | `shared`는 빌드 뒤 읽기만 한다는 규칙을 어긴다. (2) 때문에 같은 템플릿을 쓰는 뒤 시험은 늘 바뀐 기록을 본다. (1) 때문에 이 시험이 중간에 실패하면 바뀐 `lake.exe`가 남아, 뒤 시험의 게시 관문이 "approved toolchain file changed"로 실패할 수 있다. |
| `test_submission_flow.py` 131–132 | `patch.object(submission, 'hashlib', ...)`로 재해시를 막으려 하지만, 봉인 행의 해시는 `repository.verify_artifact`가 `repository` 모듈의 `hashlib`로 계산한다. | 주석(127행)이 말하는 "봉인 행은 프로세스당 한 번 해시한다"는 성질이 깨져도 시험은 통과한다. |
| `test_research_recovery.py` 310–330, 396–401 | 진단 러너의 repair 처분이 `repair_target`에 실행 ID를 넣는데, 처분 스키마(`contracts.py` 191행)는 `^installation:` 패턴을 요구한다. 제출은 스키마 이슈로 거부되고 호출은 실패로 끝난다. | 시험은 실패한 진단 뒤의 `ready` 상태만 확인하므로 다른 이유로 통과한다. 패턴(커밋 `379a171`)이 시험(`d03f7d9`)보다 뒤에 생겼다. |
| `test_engine.py` 529, 666–678 | `initial_preparation_wait`라는 키와 기제는 제품에 없다. 커밋 `b134089`에서 도입되고 `8694693`에서 폐기되었으며 `9e5e120`에서 스키마 키가 삭제되었다. | 529행의 `assertNotIn`은 늘 참이다. 666–678행의 두 시험은 `_dispatchable`에 달려 있어 공허하지 않지만, 이름은 사라진 기제를 가리킨다. |
| `test_knowledge_storage.py` 244–249 | `lean` 표지 시험 둘에 도구 모음이 없을 때 건너뛰는 장치가 없다. 같은 조건의 `test_knowledge`(343–344행), `test_knowledge_import_engine`(218–219행)은 건너뛴다. | Lean이 없는 환경(git worktree 포함)에서 `verify_lean`이 `unavailable`을 돌려 실패한다. `host` 조각의 `test_formal`, `test_formal_runtime`, `test_lean_preview`에 있는 `lean` 표지 시험 가운데 건너뛰는 장치가 없는 것도 같은 이유로 실패한다(시험마다의 동작은 각 모듈 문서의 비고에 있다). |
| `test_lean_preview.py` 125 | `assertIsNotNone(command)`는 `actual_command()`가 늘 목록을 돌려주므로 항상 참이다. | 도구 모음의 존재를 확인하지 못한다. |
| `test_formal.py` 241, 246, 276 | 241행: 합성 컴파일러는 원천을 읽지 않는다. 246행: 실제 실패 사유는 공리 출력 누락이 아니라 `signature output missing`이고 사유를 단언하지 않는다. 276행: 첫 정지 확인에서 끝나 합성 컴파일러가 돌지 않는다. | 세 시험의 이름이 말하는 경로가 실제로는 실행되지 않는다. |
| `test_task_scope.py`의 `test_rejects_changed_snapshot_user_or_academic_task_and_live_or_terminal_task` 안의 셋째 사례(과제의 `academic_requirement_id`를 바꾼 경우), `test_task_contracts.py` 374–386, `test_governance.py` 63–75·148, `test_goal_audit.py` 190–194, `test_execution_lifecycle.py` 133–135, `test_execution_profiles.py` 98–100·351–352 | 입력이 이름이 가리키는 규칙보다 앞선 다른 검사(스냅숏 계약 해시, 증거 참조 요구, 독립 실행 확인, 판정 묶음 소비, 의향 모양, 내용 해시, 역할 일치)에서 거부된다. 예외 유형만 단언하거나 여러 문구에 공통인 조각만 본다. | 이름이 가리키는 거부 규칙이 사라져도 시험은 통과한다. `task_scope`의 보호 의무 분기는 이 모듈의 어느 시험도 고정하지 않는다. |
| `test_model_assessment_flow`의 exact coverage·`test_missing_candidate_...`·`test_missing_family_...` | 거부 입력에 `contract_checks`가 없어 `contract_check.coverage` 이슈가 늘 함께 난다. | 이슈 유무 단언이 평가 누락을 사유로 고정하지 못한다. |
| `test_stop_flags.py` 331 | 단언이 `len(calls) <= 1`이다. | 기반 계산이 0회여도 통과한다. |
| `test_query_records.py` 69–81 | 바꾸지 않은 상태를 저장하므로 머리가 전진하지 않는다. | 이름이 말하는 "옛 스냅숏 재사용"을 가려내지 못한다. |
| `test_file_io.py` 97 | 전역 `VERIFIED_ARTIFACTS` 정리가 `finally` 밖에 있다. | 시험이 중간에 실패하면 같은 프로세스의 뒤 시험에 전역 기억이 남는다. |
| `purpose_fixtures.py` 157, `test_submission_tools.py` 253 | `time.sleep(1.05)` 고정 대기. | `시험-지침.md` 4절 규칙 5(고정 대기 금지) 위반. 사유 주석이 없다. |
| `test_observations.py` 675–687 (`test_three_reported_counterexamples`) | 계기로 지은 이름 아래 독립 성질 셋을 담았다. | `시험-지침.md` 4절 규칙 2·9 위반. |
| `test_design_walkthroughs.py` 1–5 | docstring은 워크스루 열두 개를 말하지만 `docs/do-math/통합-설계.md` 17.3절은 13항목이고, 13번(단일 제출과 같은-S0 편입)에 대응하는 `test_w13`이 없다. | 설계 워크스루 하나가 시험으로 대응되지 않는다. |
| `research_fixtures.py` 모듈 docstring(48–53행) | 두 가지가 실제와 다르다. (1) docstring은 첫 호출을 포함해 매번 새 사본을 준다고 쓰지만, 첫 `restore`는 사본이 아니라 빌드 폴더 자체를 준다. (2) docstring은 모든 빌드가 저장소를 `root/'repository'`에, 작업 공간을 `root/'work-0'`에 둔다고 쓰지만, `cli_instance`는 작업 공간을 `root/'workspace'`에 두고, `created_instance`는 저장소를 `root/'repo'`에, 작업 공간을 `root/'workspace'`에 둔다. | docstring을 규칙으로 믿고 경로를 가정하면 이 두 빌드에서 어긋난다. |
| `record_fixtures.py` 모듈 docstring(60–61행) | `surface_state`의 실행 `EX-1`을 docstring은 "running"이라 부르지만, 실제로는 `create_execution`이 만든 `queued` 상태 그대로다. | docstring을 믿고 실행 중 상태를 전제한 시험을 쓰면 어긋난다. |
| `test_model_metadata_boundary.py` 28–33, 51–54 | 정규식 `'missing'`과 `'unexpected'`로 거부를 가리는데, 제품 메시지(`model_policy.py` 79–83행)는 두 키를 늘 함께 싣는다. | 빠뜨림과 초과를 구별하지 못한다. |
| 모델 슬롯을 잡는 시험들(`test_claude_adapter`, `test_machine_scheduling`, `test_execution_profiles`, `test_execution_lifecycle`, `test_supervisor_recovery`, `test_provider_final_contract`가 확인된 예다) | `launch.ticket`이 `windows_job.owner_identity()`를 부르고, 이 함수는 비Windows에서 `WindowsJobUnsupportedError`를 던진다. 해제도 실제 `owner_ended`를 부른다. 이 모듈들에는 `skipUnless`가 없다. | 비Windows 환경에서는 건너뛰지 않고 오류가 난다. 이 전제를 가진 시험의 완전한 목록은 이 지도가 따로 세지 않았고, 확인된 시험은 각 모듈 문서의 비고에 Windows 전제로 적혀 있다. |
| `engine.py` 3250–3251(시험 없음) | 작업 역할에는 호출 마감이 없다는 엔진 분기를 어느 시험도 단언하지 않는다. 러너 규칙(`test_model_runner`, `test_execution_profiles`)과 창 공개(`test_execution_window`)만 시험된다. | 엔진 쪽 분기가 바뀌어도 시험이 실패하지 않는다. |

## 9. 문서 구성과 사용법

### 9.1 문서 구성

| 경로 | 내용 |
|---|---|
| `README.md` | 이 총론 |
| `기반/실행기.md` | `run_tests.py`, `test_categories.py`의 구조와 판정 규칙 |
| `기반/픽스처/<모듈>.md` | 픽스처 모듈 9개. 정의마다 행 범위, 종류, 하는 일, 부작용, 의존, 시작 상태의 단, 소비 시험 모듈 |
| `모듈/<모듈>.md` | 시험 모듈 122개. 머리 표, 목적, 모듈 수준 요소, 클래스별 절, 테스트별 항목, 관계 |

모듈 문서의 구성은 다음과 같다.
- **머리 표**: 조각, 원문 경로와 행 수, 클래스와 테스트 수, 시험 대상 제품 코드, 사용하는 픽스처, 격리 표지, 시작 상태 요약.
- **클래스 절**(`## 클래스 (행 a–b)`): 기반 클래스, 표지, 설정 훅이 만드는 시작 상태, 클래스 도우미.
- **테스트 항목**(`### \`test_이름\` (행 a–b)`): 다섯 항목(성질, 준비, 실행, 단언, 대역)과, 필요할 때 비고.
  - 성질: 시험이 보증하는 성질. 이름이 아니라 실제 단언에 맞춰 적는다.
  - 비고: `subTest` 사례, 건너뛰기 조건, 실제 외부 자원, 이름과 단언의 차이.
- **관계 절**: 같은 기능을 다른 층에서 보는 모듈, 픽스처 의존.

### 9.2 찾는 방법

- 제품 코드를 고치기 전에 영향 시험을 찾을 때: 6절 표에서 영역의 모듈을 찾는다. 그다음 각 모듈 문서 머리 표의 "시험 대상 제품 코드"와 관계 절에서 대상 함수를 확인한다. 픽스처가 흉내 내는 제품 속성을 바꿀 때는 해당 픽스처 문서의 "소비자"까지 따라간다.
- 실패한 시험을 해석할 때: 시험 ID의 모듈 문서에서 그 테스트 항목을 찾는다. 준비 항목으로 출발 상태를, 대역 항목으로 무엇이 합성인지를, 비고로 알려진 한계를 확인한다. 실패가 환경 전제(5.3) 때문인지도 먼저 본다.
- 새 시험을 쓸 때: `시험-지침.md` 4절을 따른다. 쓸 수 있는 시작 상태는 3.3절과 [research_fixtures.md](기반/픽스처/research_fixtures.md)의 `restore_template` 항목에서 고른다. 같은 성질의 기존 시험이 있는지는 해당 모듈 문서의 테스트 항목에서 확인한다.

행 좌표는 커밋 `3552607`의 원문 기준이다. 원문이 바뀌면 좌표가 어긋나므로 테스트 이름으로 찾는다. 테스트 목록 전체는 `python scripts/run_tests.py --list`로 다시 얻을 수 있다.

## 10. 색인

### 10.1 시험 모듈

행, 클래스, 테스트는 원문에서 기계로 센 값이다. 격리 수는 실행기의 `isolation_for` 판정으로 센 값이다. "제품 모듈(import)"은 시험 모듈이 직접 import한 `do_math` 모듈이며, 실제 시험 대상의 전부가 아닐 수 있다.

| 조각 | 모듈 | 행 | 클래스 | 테스트 | 격리 | 픽스처 모듈 | 제품 모듈(import) |
|---|---|---:|---:|---:|---:|---|---|
| foundation | [test_academic](모듈/test_academic.md) | 309 | 3 | 17 |  | record, research | academic, configuration, engine, execution_profiles, external, governance, knowledge, planning, repository, task_contracts, task_scope |
| foundation | [test_budget](모듈/test_budget.md) | 97 | 1 | 5 |  |  | budget, session_slots |
| foundation | [test_claude_adapter](모듈/test_claude_adapter.md) | 240 | 1 | 12 |  | provider, research | claude_adapter, claude_worker, cli, codex_worker, configuration, contracts, execution_profiles, model_policy, model_runner, observations, session_slots |
| foundation | [test_claude_stream](모듈/test_claude_stream.md) | 135 | 1 | 8 |  | provider, record | claude_adapter, claude_stream, payloads, record_schemas |
| foundation | [test_cli_surface](모듈/test_cli_surface.md) | 57 | 1 | 2 |  | research | cli, repository |
| foundation | [test_codex_adapter](모듈/test_codex_adapter.md) | 226 | 1 | 15 |  | provider | claude_worker, cli_worker, codex_adapter, codex_worker, windows_job |
| foundation | [test_completion_settlement](모듈/test_completion_settlement.md) | 147 | 2 | 6 |  | research | activities, repository, retention |
| foundation | [test_configuration](모듈/test_configuration.md) | 55 | 1 | 3 |  |  | configuration, engine, execution_profiles |
| foundation | [test_context_store](모듈/test_context_store.md) | 599 | 3 | 35 |  | engine, knowledge, record, research, review | context_store, contracts, engine, execution_lifecycle, execution_profiles, knowledge_records, planning, repository, review_cycle, submission |
| foundation | [test_contract_checks](모듈/test_contract_checks.md) | 141 | 1 | 11 |  | record, research |  |
| foundation | [test_contracts](모듈/test_contracts.md) | 200 | 1 | 16 |  | record, research | contracts, governance, integration, record_schemas, review_cycle, scheduled_operator, submission |
| foundation | [test_control_transport](모듈/test_control_transport.md) | 433 | 3 | 18 |  |  | control_transport, file_io |
| foundation | [test_decision_basis](모듈/test_decision_basis.md) | 211 | 1 | 13 |  | research | input_basis, integration, knowledge_records, planning, revisions |
| foundation | [test_delegations](모듈/test_delegations.md) | 311 | 3 | 11 |  | record, research, review | activities, delegations, engine, execution_lifecycle, execution_profiles, governance, repository |
| foundation | [test_design_walkthroughs](모듈/test_design_walkthroughs.md) | 473 | 2 | 15 |  | engine, research, review | context_store, contracts, engine, execution_profiles, initialization, knowledge, knowledge_io, knowledge_records, observations, planning, questions, repository, review_cycle, task_contracts, task_scope |
| foundation | [test_environment_validation](모듈/test_environment_validation.md) | 412 | 4 | 23 |  | research | configuration, execution_profiles, formal, initialization, repository, trust_inventory, trust_validation |
| foundation | [test_execution_lifecycle](모듈/test_execution_lifecycle.md) | 371 | 4 | 15 |  | research | activities, configuration, control_transport, execution_lifecycle, execution_profiles, provider_wait, repository, session_slots |
| foundation | [test_execution_profiles](모듈/test_execution_profiles.md) | 903 | 3 | 34 |  | engine, provider, record, research | claude_adapter, claude_worker, cli_worker, codex_adapter, codex_worker, configuration, context_store, contracts, control_transport, execution_profiles, file_io, formal, initialization, model_policy, observations, repository, session_slots, state_contract, windows_job |
| foundation | [test_execution_window](모듈/test_execution_window.md) | 56 | 1 | 3 |  |  | execution_window, repository |
| foundation | [test_external_operations](모듈/test_external_operations.md) | 105 | 2 | 6 |  | research | external, governance |
| foundation | [test_family_records](모듈/test_family_records.md) | 1260 | 2 | 75 |  | engine, knowledge, record, research, review | academic, activities, configuration, context_store, contracts, engine, events, execution_lifecycle, execution_profiles, execution_window, external, git_store, governance, initialization, knowledge, knowledge_io, knowledge_records, model_policy, observations, planning, questions, record_schemas, repository, review_policy, revisions, session_slots, state_contract, submission, trust_validation |
| foundation | [test_file_io](모듈/test_file_io.md) | 100 | 2 | 8 |  |  | file_io, repository |
| foundation | [test_formal_input_manifest](모듈/test_formal_input_manifest.md) | 72 | 1 | 1 |  | record, research | context_store, execution_profiles, formal |
| foundation | [test_git_store](모듈/test_git_store.md) | 575 | 4 | 31 |  | research | git_store |
| foundation | [test_goal_audit](모듈/test_goal_audit.md) | 233 | 2 | 12 |  | engine, record, research | academic, activities, contracts, governance, repository, session_slots |
| foundation | [test_governance](모듈/test_governance.md) | 564 | 5 | 41 |  | engine, record, research | configuration, control_contracts, governance, initialization, initialization_engine, questions, repository, review_cycle, submission |
| foundation | [test_impact_review](모듈/test_impact_review.md) | 678 | 3 | 13 |  | record, research, review | activities, contracts, engine, execution_lifecycle, execution_profiles, git_store, integration, knowledge, knowledge_io, model_policy, repository, submission |
| foundation | [test_installation_discovery](모듈/test_installation_discovery.md) | 85 | 1 | 4 |  | research | engine, file_io |
| foundation | [test_integration_bundles](모듈/test_integration_bundles.md) | 279 | 2 | 18 |  | record, research | activities, contracts, execution_profiles, integration, knowledge_io, model_policy, repository, submission |
| foundation | [test_json_digests](모듈/test_json_digests.md) | 90 | 1 | 6 |  |  | academic, external, file_io, observations, repository |
| foundation | [test_knowledge](모듈/test_knowledge.md) | 721 | 2 | 57 | 1 | knowledge, research, review | (test_categories), activities, configuration, execution_lifecycle, execution_profiles, formal, knowledge, knowledge_io, knowledge_records, record_schemas, repository, review_cycle, state_contract, trust_validation |
| foundation | [test_knowledge_import_engine](모듈/test_knowledge_import_engine.md) | 341 | 3 | 15 | 6 | knowledge, provider, record, research, state | (test_categories), activities, engine, execution_lifecycle, execution_profiles, formal, knowledge, knowledge_records, repository, review_policy, state_contract, trust_validation |
| foundation | [test_knowledge_io](모듈/test_knowledge_io.md) | 201 | 1 | 12 |  | knowledge, research | knowledge, knowledge_io, knowledge_records, repository, state_contract |
| foundation | [test_knowledge_storage](모듈/test_knowledge_storage.md) | 312 | 2 | 12 | 2 | knowledge, provider, research, review | (test_categories), activities, configuration, context_store, execution_lifecycle, execution_profiles, formal, knowledge, knowledge_io, knowledge_records, repository |
| foundation | [test_lifecycle_gates](모듈/test_lifecycle_gates.md) | 201 | 4 | 15 |  | engine, research | configuration, execution_profiles, initialization, record_schemas |
| foundation | [test_machine_scheduling](모듈/test_machine_scheduling.md) | 99 | 2 | 4 |  | provider, research | execution_profiles, parallel, record_schemas, repository, session_slots |
| foundation | [test_model_metadata_boundary](모듈/test_model_metadata_boundary.md) | 141 | 1 | 6 |  | engine, record, research, runner | configuration, contracts, execution_profiles, model_policy |
| foundation | [test_model_runner](모듈/test_model_runner.md) | 127 | 2 | 10 |  | provider | model_runner |
| foundation | [test_observations](모듈/test_observations.md) | 863 | 4 | 61 |  | provider, record, research | configuration, context_store, execution_profiles, file_io, observations, operational_dispositions, repository, state_contract, submission |
| foundation | [test_owned_job_children](모듈/test_owned_job_children.md) | 93 | 1 | 4 | 1 |  | (test_categories), control_transport, windows_job |
| foundation | [test_payloads](모듈/test_payloads.md) | 125 | 4 | 6 |  | research | payloads, repository |
| foundation | [test_planning](모듈/test_planning.md) | 367 | 6 | 21 |  | knowledge, record | activities, git_store, initialization, knowledge, knowledge_io, knowledge_records, model_policy, planning, task_scope |
| foundation | [test_preparation_cache](모듈/test_preparation_cache.md) | 70 | 1 | 3 |  |  | file_io, preflight, submission |
| foundation | [test_provider_final_contract](모듈/test_provider_final_contract.md) | 92 | 1 | 3 |  | provider, research | claude_adapter, claude_stream, claude_worker, codex_worker, control_transport, execution_profiles |
| foundation | [test_query_records](모듈/test_query_records.md) | 85 | 2 | 4 |  | engine | engine, knowledge_io, planning, repository |
| foundation | [test_questions](모듈/test_questions.md) | 240 | 4 | 14 |  | record, research | git_store, governance, questions, record_schemas, repository, revisions, submission |
| foundation | [test_reading_map](모듈/test_reading_map.md) | 97 | 2 | 7 |  | purpose | contracts |
| foundation | [test_reassessment](모듈/test_reassessment.md) | 391 | 4 | 21 |  | review | activities, configuration, engine, execution_lifecycle, execution_profiles, knowledge, knowledge_records, repository, review_cycle |
| foundation | [test_reference_catalog](모듈/test_reference_catalog.md) | 86 | 1 | 4 |  |  | contracts, submission |
| foundation | [test_relation_dependencies](모듈/test_relation_dependencies.md) | 94 | 2 | 5 |  | engine, record | knowledge, planning, questions, revisions, submission, task_scope |
| foundation | [test_repair_execution](모듈/test_repair_execution.md) | 212 | 3 | 11 |  | engine, record, research | activities, engine, execution_lifecycle, parallel, repair_execution, scheduled_operator |
| foundation | [test_reporting](모듈/test_reporting.md) | 239 | 2 | 8 |  | record, research | claude_stream, cli, execution_profiles, git_store, payloads, reporting, repository |
| foundation | [test_repository](모듈/test_repository.md) | 515 | 6 | 30 |  | research | git_store, governance, initialization, repository, state_checks, state_contract |
| foundation | [test_retention](모듈/test_retention.md) | 259 | 1 | 13 |  | research | file_io, record_schemas, repository, retention |
| foundation | [test_review_cycle](모듈/test_review_cycle.md) | 381 | 2 | 24 |  | review | configuration, execution_profiles, review_cycle |
| foundation | [test_review_policy](모듈/test_review_policy.md) | 232 | 1 | 12 |  | review | input_basis, review_cycle, review_policy |
| foundation | [test_review_scope_wire](모듈/test_review_scope_wire.md) | 165 | 2 | 6 |  | research | configuration, contracts, execution_profiles, record_schemas, review_cycle, review_policy, submission |
| foundation | [test_revision_obligations](모듈/test_revision_obligations.md) | 139 | 1 | 7 |  | record, research | engine, governance, planning, revisions |
| foundation | [test_scholarly](모듈/test_scholarly.md) | 92 | 1 | 5 |  |  | scholarly |
| foundation | [test_standalone](모듈/test_standalone.md) | 62 | 1 | 3 |  |  | formal |
| foundation | [test_state_checks](모듈/test_state_checks.md) | 432 | 3 | 23 |  | knowledge, record, research | configuration, context_store, execution_profiles, external, git_store, knowledge, knowledge_records, record_schemas, repository, state_checks, state_contract |
| foundation | [test_state_contract](모듈/test_state_contract.md) | 135 | 4 | 7 |  | research | activities, execution_profiles, knowledge_io, model_policy, repository, state_contract |
| foundation | [test_submission_checks](모듈/test_submission_checks.md) | 530 | 3 | 36 |  | record, research | contracts, git_store, governance, integration, repository, submission |
| foundation | [test_supervisor_recovery](모듈/test_supervisor_recovery.md) | 224 | 1 | 6 |  | provider, research | execution_profiles, file_io, git_store, repository, scheduled_operator, session_slots |
| foundation | [test_task_contracts](모듈/test_task_contracts.md) | 899 | 9 | 61 |  | record, research | activities, configuration, contracts, engine, execution_lifecycle, execution_profiles, governance, input_basis, knowledge, planning, repository, revisions, state_contract, submission, task_contracts, task_scope |
| foundation | [test_task_scope](모듈/test_task_scope.md) | 190 | 3 | 8 |  | record, research, runner | contracts, knowledge, knowledge_io, knowledge_records, planning, repository, submission, task_scope |
| foundation | [test_test_runner](모듈/test_test_runner.md) | 193 | 1 | 11 |  |  | (test_categories) |
| foundation | [test_trust_continuation](모듈/test_trust_continuation.md) | 107 | 2 | 2 |  | research, state | engine, maintenance_gate, trust_validation |
| foundation | [test_unicode_flow](모듈/test_unicode_flow.md) | 99 | 1 | 5 |  | research | context_store, repository |
| host | [test_background_processes](모듈/test_background_processes.md) | 151 | 1 | 3 |  |  |  |
| host | [test_diagnosed_installation_recovery](모듈/test_diagnosed_installation_recovery.md) | 181 | 1 | 8 |  | record | configuration, execution_lifecycle, execution_profiles, launch, repair_execution, scheduled_operator |
| host | [test_external](모듈/test_external.md) | 107 | 1 | 10 |  | provider | external, repository |
| host | [test_formal](모듈/test_formal.md) | 341 | 2 | 32 | 6 | provider, research | (test_categories), formal, repository, trust_validation |
| host | [test_formal_runtime](모듈/test_formal_runtime.md) | 134 | 1 | 8 | 5 | provider | (test_categories), execution_profiles, formal, session_slots |
| host | [test_host_resources](모듈/test_host_resources.md) | 560 | 4 | 23 | 2 | provider, research | (test_categories), activities, configuration, contracts, engine, execution_lifecycle, execution_profiles, git_store, initialization, model_runner, repository, session_slots, windows_job |
| host | [test_launch_recovery](모듈/test_launch_recovery.md) | 78 | 1 | 4 |  |  | launch, windows_job |
| host | [test_lean_preview](모듈/test_lean_preview.md) | 165 | 1 | 6 | 1 | provider | (test_categories), contracts, file_io, formal, formal_preview, submission |
| host | [test_machine_parallel](모듈/test_machine_parallel.md) | 611 | 3 | 22 | 3 | engine, research, state | (test_categories), configuration, engine, execution_lifecycle, execution_profiles, formal, git_store, knowledge_records, parallel, repository, session_slots, windows_job |
| host | [test_operator](모듈/test_operator.md) | 393 | 2 | 22 |  | research | cli, planning, scheduled_operator |
| host | [test_operator_bootstrap](모듈/test_operator_bootstrap.md) | 84 | 1 | 4 |  |  | file_io |
| host | [test_preflight](모듈/test_preflight.md) | 108 | 2 | 10 |  | research | contracts, initialization, lifecycle_engine, preflight, record_schemas, repository |
| host | [test_probe_cli](모듈/test_probe_cli.md) | 56 | 1 | 3 |  |  |  |
| host | [test_provider_wait](모듈/test_provider_wait.md) | 189 | 1 | 6 |  | provider, research | git_store, provider_wait, repository, session_slots |
| host | [test_schedule_lifetime](모듈/test_schedule_lifetime.md) | 56 | 1 | 1 | 1 |  | (test_categories) |
| host | [test_schedule_pythonw](모듈/test_schedule_pythonw.md) | 61 | 1 | 2 |  |  |  |
| host | [test_windows_job](모듈/test_windows_job.md) | 281 | 1 | 8 |  |  | windows_job |
| host | [test_worker_temporary_outputs](모듈/test_worker_temporary_outputs.md) | 59 | 1 | 1 |  |  | claude_worker, cli_worker, codex_worker, context_store |
| lifecycle | [test_checkpoint_persistence](모듈/test_checkpoint_persistence.md) | 162 | 3 | 5 |  | purpose, research | observation_transport, observations, repository |
| lifecycle | [test_cli](모듈/test_cli.md) | 587 | 2 | 27 |  | research | cli, control_contracts, engine, reporting, repository |
| lifecycle | [test_cli_advanced](모듈/test_cli_advanced.md) | 151 | 2 | 6 |  | record, research | cli, governance, knowledge, knowledge_records, repository |
| lifecycle | [test_control_shapes](모듈/test_control_shapes.md) | 188 | 2 | 13 |  | engine, record, research | control_contracts, engine, file_io, governance, knowledge_engine, repository, trust_validation |
| lifecycle | [test_controls](모듈/test_controls.md) | 571 | 8 | 24 |  | engine, research, runner, state | configuration, control_contracts, engine, maintenance_gate, observations, planning, repository, scheduled_operator, submission |
| lifecycle | [test_engine](모듈/test_engine.md) | 766 | 7 | 32 |  | engine, research, runner, state | activities, codex_adapter, configuration, context_store, control_transport, engine, execution_lifecycle, execution_profiles, file_io, governance, knowledge_records, launch, record_schemas, repository, state_contract, submission, task_contracts, windows_job |
| lifecycle | [test_formal_engine](모듈/test_formal_engine.md) | 256 | 4 | 11 |  | engine, research, state | configuration, engine, execution_profiles, knowledge_io, knowledge_records, repository |
| lifecycle | [test_governance_engine](모듈/test_governance_engine.md) | 633 | 5 | 31 |  | engine, record, research | academic, cli, configuration, contracts, engine, execution_lifecycle, governance, integration, planning, record_schemas, repository, submission |
| lifecycle | [test_initial_intent_connection](모듈/test_initial_intent_connection.md) | 165 | 2 | 6 |  | engine, record, research | engine, execution_profiles, governance, initialization, model_policy, repository |
| lifecycle | [test_initialization_probe_batch](모듈/test_initialization_probe_batch.md) | 139 | 2 | 8 |  | research, state | configuration, engine, execution_profiles, initialization, repository |
| lifecycle | [test_input_recovery](모듈/test_input_recovery.md) | 448 | 4 | 10 |  | engine, record, research, runner, state | activities, contracts, engine, execution_profiles, integration, planning, repository, submission |
| lifecycle | [test_lifecycle_engine](모듈/test_lifecycle_engine.md) | 1103 | 5 | 73 |  | engine, provider, research, state | academic, activities, configuration, engine, execution_profiles, governance, initialization, knowledge, questions, record_schemas, repository |
| lifecycle | [test_live_observation](모듈/test_live_observation.md) | 588 | 6 | 21 | 1 | engine, provider, record, research | (test_categories), codex_adapter, configuration, control_transport, execution_profiles, observation_transport, observations, parallel, record_schemas, windows_job |
| lifecycle | [test_observation_admission](모듈/test_observation_admission.md) | 146 | 2 | 8 |  | engine, research | configuration, engine, execution_profiles, initialization, observations, repository |
| lifecycle | [test_operation_trace](모듈/test_operation_trace.md) | 101 | 1 | 5 |  |  | operation_trace |
| lifecycle | [test_planning_engine](모듈/test_planning_engine.md) | 232 | 5 | 10 |  | engine, record, research | configuration, execution_lifecycle, execution_profiles, initialization, model_policy, planning, repository, revisions, session_slots, task_contracts |
| lifecycle | [test_provider_recovery](모듈/test_provider_recovery.md) | 184 | 3 | 4 |  | provider, research, runner, state | engine, provider_wait, scheduled_operator, session_slots |
| lifecycle | [test_role_input](모듈/test_role_input.md) | 1399 | 10 | 58 |  | engine, knowledge, provider, purpose, record, research, review, runner | configuration, context_store, contracts, delegations, execution_lifecycle, execution_profiles, git_store, input_basis, integration, knowledge, knowledge_io, knowledge_records, operational_dispositions, planning, repository, review_cycle, state_contract, submission |
| lifecycle | [test_stop_flags](모듈/test_stop_flags.md) | 367 | 5 | 16 |  | engine, research, runner, state | engine, execution_lifecycle, knowledge, parallel, windows_job |
| lifecycle | [test_task_completion](모듈/test_task_completion.md) | 166 | 3 | 10 |  | record | planning, repository, task_scope |
| research | [test_currentness](모듈/test_currentness.md) | 474 | 4 | 13 |  | engine, purpose, research, state | engine, file_io, git_store, integration, knowledge, knowledge_io, observations, operational_dispositions, planning, repository, state_contract, submission |
| research | [test_purpose_engine](모듈/test_purpose_engine.md) | 377 | 3 | 19 |  | purpose, record, research, state | configuration, context_store, contracts, engine, execution_profiles, knowledge, knowledge_records, model_policy, repository, submission |
| research | [test_research_recovery](모듈/test_research_recovery.md) | 973 | 12 | 48 |  | engine, purpose, record, research, state | activities, configuration, contracts, engine, execution_lifecycle, execution_profiles, file_io, operational_dispositions, planning, record_schemas, repair_execution, repository |
| research | [test_session_scheduler](모듈/test_session_scheduler.md) | 953 | 13 | 41 |  | engine, provider, purpose, research, runner, state | activities, configuration, engine, execution_lifecycle, execution_profiles, file_io, model_policy, planning, repository, scheduled_operator, scheduler, session_slots, windows_job |
| review | [test_native_final_submission](모듈/test_native_final_submission.md) | 245 | 3 | 11 |  | engine | codex_adapter, engine, execution_lifecycle, model_runner, payloads, repository, windows_job |
| review | [test_question_flow](모듈/test_question_flow.md) | 134 | 2 | 4 |  | engine, purpose, research, runner | engine, integration, question_engine, repository |
| review | [test_repetition](모듈/test_repetition.md) | 321 | 2 | 10 |  | engine, purpose, research, runner | activities, contracts, engine, execution_lifecycle, file_io, governance, input_basis, integration, planning, repository, revisions, submission, task_contracts |
| review | [test_review_engine](모듈/test_review_engine.md) | 1405 | 9 | 58 |  | engine, purpose, research, review, state | activities, cli, configuration, context_store, delegations, engine, execution_lifecycle, execution_profiles, file_io, governance, knowledge, knowledge_io, knowledge_records, repository, review_cycle, review_policy |
| review | [test_review_research](모듈/test_review_research.md) | 436 | 4 | 17 |  | purpose, research, review, state | execution_profiles, knowledge, knowledge_records, repository, review_cycle, review_policy, submission |
| review | [test_submission_boundaries](모듈/test_submission_boundaries.md) | 445 | 3 | 11 |  | purpose, research, runner, state | context_store, engine, knowledge, knowledge_records, planning, repository |
| review | [test_submission_flow](모듈/test_submission_flow.md) | 982 | 14 | 34 |  | engine, knowledge, record, research | context_store, contracts, control_transport, engine, execution_lifecycle, git_store, input_basis, integration, knowledge, knowledge_io, planning, repository, submission, trust_validation |
| review | [test_submission_tools](모듈/test_submission_tools.md) | 703 | 4 | 34 |  | purpose, research, state | context_store, contracts, control_transport, engine, git_store, governance, knowledge, knowledge_io, repository, review_cycle, scheduled_operator, submission |
| academic | [test_academic_engine](모듈/test_academic_engine.md) | 416 | 2 | 11 |  | purpose, research, state | academic, engine, external, governance, task_scope |
| academic | [test_academic_preparation](모듈/test_academic_preparation.md) | 173 | 2 | 8 |  | purpose, research, runner | activities, contracts, model_policy, planning, repository, revision_engine, submission |
| academic | [test_model_assessment_flow](모듈/test_model_assessment_flow.md) | 448 | 4 | 22 |  | purpose, research, runner | contracts, engine, model_policy, planning, repository, submission |

### 10.2 기반 문서

- [기반/실행기.md](기반/실행기.md)
- 픽스처: [research_fixtures](기반/픽스처/research_fixtures.md), [state_fixtures](기반/픽스처/state_fixtures.md), [engine_fixtures](기반/픽스처/engine_fixtures.md), [runner_fixtures](기반/픽스처/runner_fixtures.md), [purpose_fixtures](기반/픽스처/purpose_fixtures.md), [record_fixtures](기반/픽스처/record_fixtures.md), [knowledge_fixtures](기반/픽스처/knowledge_fixtures.md), [review_fixtures](기반/픽스처/review_fixtures.md), [provider_fixtures](기반/픽스처/provider_fixtures.md)

## 11. 이 지도의 완전성과 정확성

- **완전성**: 원문 AST에서 모든 모듈, 클래스, 테스트, 도우미, 모듈 수준 이름과 행 범위를 뽑은 목록을 정답지로 삼았다. 이 목록의 테스트 1,931개는 실행기 `--list`의 수집 결과와 정확히 일치한다. 모든 문서가 정답지의 모든 항목을 지정된 제목 서식과 행 범위로 담고 있음을 기계 검사로 확인했다. 정답지에 없는 테스트 제목도 없다. 테스트 항목 1,931개는 모두 다섯 필수 항목을 갖추었다.
- **정확성**: 모든 문서를 작성자와 다른 검증자가 원문과 제품 코드에 전수 대조했다. 검증자가 원문 좌표로 입증한 지도 문서의 결함은 총론과 실행기 문서를 포함해 232건이고, 모두 문서에서 고쳤다. 이 수는 원문 시험의 결함이 아니라 지도 문서가 원문과 어긋난 곳의 수다. 결함은 주로 네 종류였다. 제품·픽스처 행 좌표의 어긋남, 다른 모듈이 어떤 함수를 패치할 뿐인데 "부른다"고 쓴 관계 진술, 개수와 단계 수의 오기, 성질을 실제 단언보다 넓게 쓴 문장이다. 작성 단계에서 보고된 원문 결함 주장 가운데 일부는 대조에서 기각되었다. 예를 들어 켈빈 기호 키를 중복 키로 본 주장이 그렇다. 기각된 주장은 문서에서 사실대로 바로잡았다. 8절의 개별 사항은 모두 이 대조에서 원문 좌표로 확인된 것이다.
- **남은 한계**
  - 3.4절의 분포 수치는 어림값이다.
  - 모듈 문서가 적은 "의도"는 원천(docstring, 주석, 계약 문서, 커밋)에 근거가 있는 것만 담았다. 근거가 없는 곳은 코드가 검사하는 성질만 적었다.
  - 이 지도는 시험을 실행하지 않았다.
