# review_fixtures

| 항목 | 값 |
|---|---|
| 원문 | `.claude/skills/do-math/scripts/tests/review_fixtures.py` (542행) |
| 정의 수 | 함수 8, 클래스 4(`ReviewFakeEngine`, `ReassessmentHarness`, `KnowledgeRoundtripHarness`, `ImpactReviewHarness`), 상수 0 |
| 이 모듈을 쓰는 시험 모듈 | 13개(`consumers.json` 기준). 다른 픽스처 모듈은 이 모듈을 import하지 않는다 |
| 이 모듈이 부르는 다른 픽스처 | `research_fixtures`(`governance_start`, `start_scoped_review`, `trust_environment`, `trust_fixture`, `scope_assessment`, `current_state`, `git_init`, `bare_engine`), `engine_fixtures.FakeEngine`, `knowledge_fixtures`(`formal_evidence`, `knowledge_candidate`, `verified_knowledge`), `record_fixtures`(`execution_state`, `observation_knowledge`, `research_work_context`, `two_observation_output`) |

## 목적

모듈 docstring(행 1–23)은 이 모듈을 "동일성 검토(identity review) 픽스처: 검토 엔진 대역, 범위가 정해진 검토 주기, 검토자 출력, 검토 하네스"라고 소개한다. 핵심 원칙은 docstring 둘째 문단에 있다. 검토자, 연구자, 컴파일러의 답은 합성이지만, 그 답이 지나가는 검토 주기(review cycle), 입장(admission), 적용 코드는 제품의 것이다. 그래서 이 모듈의 대역은 답을 만드는 쪽만 바꾸고, 답을 받는 쪽은 모두 제품 함수(`review_cycle.start_review`·`accept_result`·`next_actions`, 엔진의 `_admit_review_execution`·`_apply_identity_review`·`_defer_review_for_research`, `knowledge_records`의 기록 함수)를 거친다.

이 모듈이 맡는 영역은 동일성 검토의 세 층이다.

- 순수 주기: `scoped_start`, `review_stage_output`, `deferred_research_cycle`, `research_answer`.
- 메모리 엔진: `ReviewFakeEngine`, `grant_replacement`, `defer_review_for_research`, 그리고 `ReassessmentHarness`.
- 저장된 형태의 기록: `reviewed_candidate`와 `KnowledgeRoundtripHarness`. 뒤의 것은 실제 Git 저장소를 쓴다.

여기에 연구 산출의 영향 검토(impact review)를 위한 `ImpactReviewHarness`가 더해진다.

## 구성

| 무리 | 정의 | 부르는 것 |
|---|---|---|
| 메모리 검토 엔진 | `_no_artifacts`, `ReviewFakeEngine`, `grant_replacement` | `ReviewFakeEngine.__init__` → `research_fixtures.governance_start`·`trust_fixture`·`trust_environment`, `knowledge_io.ensure_ontology`, `kr.create_candidate`·`record_formal_result`, `build_profiles`, `_no_artifacts`; `start` → `research_fixtures.start_scoped_review`; `execute` → 엔진의 `_prepare_review_context`·`_admit_review_execution`·`_record_review_input`·`_apply_identity_review`; `grant_replacement` → `governance.preserve_source`·`apply_decision` |
| 순수 검토 주기 | `scoped_start`, `review_stage_output`, `deferred_research_cycle`, `research_answer` | `review_cycle.start_review`·`context_for`·`next_actions`·`defer_for_research`·`inline_source_row` |
| 연구 유예 | `defer_review_for_research` | 엔진의 `_start_identity_review`·`_prepare_review_context`·`_defer_review_for_research`, `ReviewFakeEngine.execute`·`pending` |
| 저장된 형태의 후보 | `reviewed_candidate` | `record_fixtures.execution_state`, `engine_fixtures.FakeEngine.environment`, `knowledge_fixtures.knowledge_candidate`·`formal_evidence`, `research_fixtures.scope_assessment`, `review_cycle`의 `start_review`·`next_actions`·`accept_result`·`identity_assessment`, `kr.record_identity_assessment` |
| 하네스 | `ReassessmentHarness`, `KnowledgeRoundtripHarness`, `ImpactReviewHarness` | 각각 `ReviewFakeEngine`; `scoped_start`·`review_stage_output`·`knowledge_fixtures.verified_knowledge`·`ResearchRepository`; `do_math.integration`·`submission.seal_submission`·`research_fixtures.bare_engine` |

## 메모리 검토 엔진

### `grant_replacement(engine, *, reuse='reusable')` (행 39–45)
- 종류: 함수.
- 하는 일과 반환값: `engine`에 `K1` 검토의 기록 기반 교체를 허가하는 grant를 적용한다. 먼저 사용자 출처 `SOURCE-review`("Authorize record-based replacement of K1 review.")를 `governance_sources`에 보존한다. 이어 `governance.apply_decision`으로 결정 `DEC-review`를 적용한다. 이 결정의 grant `GR-review`는 `kind='local'`, `roles=['identity_review']`, `reuse`, `included_targets=['K1']`, `purposes=['record_replacement']`이다. 반환값은 없고, `engine.instance`와 `engine.runtime`을 바꾼다.
- 부작용: 엔진 상태를 바꾼다. 저장은 하지 않는다.
- 의존: `governance.preserve_source`, `governance.apply_decision`.
- 소비자: `test_delegations`, `test_reassessment`, `test_review_cycle`, `test_review_engine`, `test_review_policy`.

### `_no_artifacts(path, snapshot)` (행 48–49)
- 종류: 함수(저장소 읽기 대역).
- 하는 일과 반환값: 언제나 `FileNotFoundError(path)`를 던진다.
- 부작용: 없음.
- 의존: 없음.
- 소비자: 모듈 안에서만 사용. `ReviewFakeEngine.__init__`(행 112)가 `self.store.read`로 건다. 봉인된 산출물을 읽으려는 검토 경로는 이 오류로 드러난다.

### `ReviewFakeEngine` (행 52–188)
- 종류: 대역(메모리 엔진). 제품 `ResearchEngine`을 상속한다.
- 하는 일과 반환값: docstring은 "검증된 형식 증거와 검토 정책을 가진 후보 정리 `K1` 하나 위의 제품 엔진"이다. 제품 그대로인 부분은 검토 주기를 여는 코드, 맥락 준비, 실행 입장, 결과 적용, 지식 기록이다. 바뀌는 부분은 세 가지다. 저장소가 없다(`store`는 `SimpleNamespace(git_dir=None, read=_no_artifacts)`). `_save`는 호출만 기록하는 autospec 대역이다. 검토자의 답은 `execute`가 합성한다.
- 메서드:
  - `__init__` (행 62–115): `ResearchEngine.__init__`을 부르지 않고 `_init_process_state()`로 프로세스 지역 상태만 만든다. 상태는 다음 순서로 조립한다.
    1. 검토 정책(`fixture-review-policy-v5`)을 만든다. 필수 관점 없음, 최소 초기 슬롯 2, 판정 슬롯 `judge-0`~`judge-2`, `round_limit=rounds`(기본 2), 활동 실행 한도 24, 초과 처분 `unresolved`.
    2. 고정 범위(scope)를 만든다. 초기 슬롯은 둘이다: `initial-0`(관점 `formal`)과 `initial-1`(관점 `semantic`).
    3. `governance_start`로 인스턴스를 만든다. 설정은 `reviewers=2`와 `DEFAULT_CONFIG`의 `review_research_limit`이다.
    4. 옛 형태의 `K1`을 꺼내 `ensure_ontology`로 온톨로지를 채운다. `K1`의 원문은 `theorem sample : 1 = 1 := rfl`이다.
    5. `DEFAULT_CONFIG` 프로필을 설치한다. `identity_review`와 `supplemental_research` 프로필 참조를 `self.profile`과 `self.research_profile`에 둔다.
    6. `root` 아래에 합성 신뢰 환경 `TE-review`를 만들어 활성화하고, 그 바인딩을 런타임에 둔다.
    7. `theorem` 종류 정의로 후보를 만들고(`kr.create_candidate`), 검증된 형식 결과를 기록한다(`kr.record_formal_result`). 형식 결과에는 의존 폐포와 선언 증거가 채워져 있다.
    8. `head='snapshot-one'`, `sequence=0`으로 둔다.
    소비 시험이 `start`에서 쓰도록 범위를 `self.scope`에 보관한다. 주석(행 74)은 "엔진이 연 검토는 scope 단계에서 시작한다"고 밝힌다.
  - `start` (행 117–119): `kid`(기본 `K1`)의 검토를 연다. 시작점은 scope 단계가 아니라 초기 슬롯이다. 인자로 받은 `scope`가 있으면 그것을, 없으면 고정 범위를 `research_fixtures.start_scoped_review`에 넘기고 주기 ID를 돌려준다.
  - `pending` (행 121–122): 큐에서 첫 `identity_review` 행동을 돌려준다. 없으면 `StopIteration`이 난다.
  - `assessment` (행 124–126): `kid`의 `review_cycle_id`로 주기를 찾고, 그 주기의 `assessment_id`로 `identity_assessments`의 행을 돌려준다.
  - `usable` (행 128–129): `kr.usable_links(instance, kid)`가 비어 있지 않은지 돌려준다.
  - `revise` (행 131–138): `previous_id`의 제안 보기(`kr.proposal_view`)에서 형식·상태·검토 필드를 뺀 후속 후보 `new_id`(기본 `K2`)를 만든다. 후보는 `supersedes=previous_id`, `revision+1`, 새 `explanation`('Expanded proof by reflexivity'), `formal_result_ref`를 가진다. `kr.create_candidate`로 기록하고 `new_id`를 돌려준다.
  - `execute` (행 140–188): 다음 검토 행동 하나를 검토자처럼 답하고 적용한다. 차례는 다음과 같다.
    1. 실행 ID `ex-<순번>`과 작업 공간 `root/ex-<순번>/workspace`를 정한다.
    2. 제품의 `_prepare_review_context`로 맥락을 만든다.
    3. 단계별 기본 답을 만든다. scope 단계는 두 슬롯의 `generated-scope` 범위를 낸다. initial 단계는 `match`, 발견 없음이다. organize 단계는 대기 중인 발견(`pending_findings`)마다 쟁점 `issue-<n>`을 만든다. 답할 슬롯은 발견이 초기 단계의 것이면 그 슬롯, 아니면 `initial-0`이다. judge 단계는 `match`이며 모든 쟁점을 `rejected`로 판정한다. answer 단계는 모든 답변 요청을 `withdraw`한다.
    4. `changes`로 필드를 덮어쓴다.
    5. 실행 기록을 `running` 상태로 넣는다. 기록에는 입력 스냅숏, 프롬프트 해시 `actual-prompt-hash`, 검토 프로필 참조가 담긴다.
    6. 제품의 `_admit_review_execution`을 부른다.
    7. `record_first`가 참이면 `_record_review_input`을 두 번 부른다.
    8. 행동을 큐에서 빼고 `_apply_identity_review`를 부른다.
    9. 실행을 `ended`/`output_accepted`로 마감하고 `(context, output, execution_id)`를 돌려준다.
    대역 안의 검사는 두 가지다. 입장 결과의 `disposition`이 `'admitted'`가 아니면 그 값을 담은 `ValueError`를 던진다. 대기 중인 검토 행동이 없으면 `pending`에서 `StopIteration`이 난다.
- 부작용: 파일을 쓰지 않는다. 신뢰 환경 합성 설치 파일만 `root` 아래에 생긴다(`trust_fixture`). 저장소도 프로세스도 없다.
- 의존: `research_fixtures.governance_start`·`trust_fixture`·`trust_environment`·`start_scoped_review`, `knowledge_io.ensure_ontology`, `kr.create_candidate`·`record_formal_result`·`usable_links`·`proposal_view`, `build_profiles`, `profile_ref`, `_no_artifacts`.
- 시작 상태의 단: 네 단 밖(메모리 엔진 대역).
- 소비자: `test_context_store`, `test_delegations`, `test_reassessment`, `test_review_cycle`, `test_review_engine`, `test_review_policy`, `test_review_research`, `test_role_input`.

## 순수 검토 주기

### `scoped_start(proposal, reviewers, judges=3, max_rounds=3, previous=None)` (행 190–201)
- 종류: 함수.
- 하는 일과 반환값: scope 단계가 이미 정해진 순수 검토 주기를 돌려준다. `reviewers`가 정수면 슬롯 `initial-0`…을 만들고, 목록이면 그대로 쓴다. `judges`도 같다. 정책 `test-policy-v5`는 최소 초기 슬롯을 슬롯 수로, 활동 실행 한도를 `슬롯 수 + max_rounds × (슬롯 수 + 4)`로 둔다. 범위(`test-scope`)의 초기 슬롯은 관점 이름이 슬롯 이름과 같다. 이 정책과 범위로 `review_cycle.start_review(proposal, reviewers, judges, max_rounds, previous, policy=..., scope_assessment=...)`를 부른 결과를 돌려준다.
- 부작용: 없음.
- 의존: `do_math.review_cycle.start_review`.
- 시작 상태의 단: 1단.
- 소비자: `test_knowledge`, `test_reassessment`, `test_review_cycle`. 모듈 안에서는 `KnowledgeRoundtripHarness.cycle`이 쓴다.

### `review_stage_output(cycle, stage, **changes)` (행 203–222)
- 종류: 함수.
- 하는 일과 반환값: 순수 주기 `cycle`의 다음 단계 `stage`에 대한 검토자 출력을 돌려준다. 기본 필드는 `proposal_digest`, 요약, `used_sources=['proposal:1']`, 빈 질문이다. 단계별 답은 docstring대로다. initial은 `match`, 발견 없음이다. organize는 `context_for(cycle, next_actions(cycle)[0])`의 대기 발견마다 쟁점 `i<j>`를 만든다. 번호는 기존 쟁점 수부터 이어 가고, 답할 슬롯은 발견이 initial·answer 단계의 것이면 그 슬롯, 아니면 `initial-0`이다. answer는 모든 답변 요청을 `maintain`한다. judge는 `mismatch`이며 모든 쟁점을 `approved`로 판정한다. 마지막으로 `changes`가 필드를 덮어쓴다.
- 부작용: 없음.
- 의존: `review_cycle.context_for`, `next_actions`.
- 비고: `ReviewFakeEngine.execute`와 답의 방향이 반대다. 그쪽은 쟁점을 철회하고 기각해 `match`로 끝나고, 이쪽은 이의를 유지하고 승인해 `mismatch`로 끝난다. scope 단계에 대한 분기는 없으므로, scope 단계 출력은 호출자가 채운다(`KnowledgeRoundtripHarness.cycle` 행 431–432).
- 소비자: `test_reassessment`, `test_review_cycle`. 모듈 안에서는 `KnowledgeRoundtripHarness.cycle`이 쓴다.

### `defer_review_for_research(engine)` (행 225–249)
- 종류: 함수.
- 하는 일과 반환값: `ReviewFakeEngine`에서 `K1`의 검토를 열고, 첫 초기 검토를 고정 출처 연구 때문에 유예시킨 뒤 주기 ID를 돌려준다. 차례는 다음과 같다.
  1. `_start_identity_review('K1')`로 검토를 연다. 제품 경로이므로 scope 단계부터 시작한다.
  2. `engine.execute()`로 scope 단계를 답한다.
  3. 다음 행동을 복사해 `root/deferred`에서 맥락을 준비한다.
  4. 연구 요청 `domain`을 가진 실행 `INV-request`를 `running`으로 등록한다. 요청의 질문은 "Which axioms does this exact declaration use?", 출처는 `proposal:formal.axioms`와 `proposal:lean_code`다. 실행에는 프롬프트 해시 `deferred-prompt-hash`가 붙는다.
  5. `unresolved`·범위 미완결 출력으로 제품의 `_defer_review_for_research`를 부른다.
  6. 실행을 `ended`/`output_accepted`로 마감한다.
- 대역 안의 검사: `_defer_review_for_research`가 거짓을 돌려주면 `AssertionError('The review was not deferred for research')`를 던진다.
- 부작용: 엔진 상태만 바꾼다.
- 의존: `ReviewFakeEngine.execute`·`pending`, 엔진의 `_start_identity_review`·`_prepare_review_context`·`_defer_review_for_research`.
- 소비자: `test_review_research`, `test_role_input`.

### `deferred_research_cycle()` (행 252–267)
- 종류: 함수.
- 하는 일과 반환값: `(cycle, action)`을 돌려준다. 두 검토자(`initial-0` 관점 `first`, `initial-1` 관점 `second`) 범위와 정책 ID `review-policy-v5-default`로 `start_review({'revision': 1}, reviewers=2, scope_assessment=scope)`를 연다. 첫 행동에 대해 `unresolved` 출력과 연구 요청 `r`("What is the exact domain?", 출처 `proposal`)을 만든다. 출처 행은 `inline_source_row('proposal', cycle['proposal'])`이고, 요청자는 `'requester'`, `limit=3`이다. 이것으로 `defer_for_research`를 부른 결과 주기와, 유예된 행동을 짝으로 돌려준다.
- 부작용: 없음.
- 의존: `review_cycle.start_review`, `next_actions`, `defer_for_research`, `inline_source_row`.
- 시작 상태의 단: 1단.
- 소비자: `test_family_records`, `test_review_cycle`, `test_review_research`.

### `research_answer(cycle)` (행 270–275)
- 종류: 함수.
- 하는 일과 반환값: `cycle['research']`의 첫(유일한) 요청에 대한 조사자 답을 돌려준다. 답은 요청의 `id`와 `request_digest`를 그대로 싣고, `outcome='answered'`, `answer='The domain is Nat.'`, `scope_complete=True`, `evidence_refs=['proposal']`이다.
- 부작용: 없음.
- 의존: 없음.
- 소비자: `test_review_cycle`, `test_review_research`.

## 저장된 형태의 후보

### `reviewed_candidate(root, *, verified=False)` (행 278–335)
- 종류: 함수.
- 하는 일과 반환값: `(instance, runtime, kid, assessment ID)`를 돌려준다. 저장된 형태의 정리 후보가 봉인된 동일성 검토 한 번을 거친 상태다. 차례는 다음과 같다.
  1. `record_fixtures.execution_state("identity_review")`에서 시작한다.
  2. `verified`가 참이면 `engine_fixtures.FakeEngine(root)`로 합성 신뢰 환경 `synthetic-base`를 활성화한다. 그 신뢰 환경, 전이, 바인딩을 복사해 온다.
  3. `ensure_ontology`를 적용하고 후보 `theorem t : True := True.intro`(선언 `t`)를 가져온다(`import_candidate`).
  4. `verified`면 `formal_evidence`로 검증된 형식 결과를 기록한다.
  5. 검토자 하나, 한 라운드짜리 순수 주기를 연다(`start_review`). ID `RC-1`, 활동 `AT-1`, 입력 스냅숏 `'a'*40`, 정책 `policy-test`를 붙인다.
  6. 두 행동을 차례로 받아들인다(`accept_result`). scope 단계는 `research_fixtures.scope_assessment`로 `initial-0` 한 슬롯을 준다. initial 단계는 `verified`면 `match`, 아니면 `unresolved`다. 두 행동의 실행 `EX-review-0`과 `EX-review-1`은 활동 `AT-1`에 배정된다.
  7. `identity_assessment`로 평가를 만들어 `record_identity_assessment`로 기록한다.
- 대역 안의 검사: 주기의 끝 상태가 `verified`일 때 `completed`, 아닐 때 `unresolved`가 아니면 `AssertionError("The synthetic review ended as ...")`를 던진다.
- 부작용: `verified`일 때 `root` 아래에 합성 신뢰 환경 파일이 생긴다.
- 의존: `record_fixtures.execution_state`, `engine_fixtures.FakeEngine`, `knowledge_fixtures.formal_evidence`·`knowledge_candidate`, `research_fixtures.scope_assessment`, `knowledge_io`, `kr`, `review_cycle`, `create_execution`, `assign_execution`.
- 시작 상태의 단: 1단(순수 도메인 함수로 만든 사전).
- 비고: `rc.identity_assessment`에 넘기는 `reason`은 `verified`와 관계없이 "Scope remains incomplete"로 고정되어 있다(행 332). 이 값은 평가의 `summary` 필드가 된다(`do_math/review_cycle.py` 행 426–436). 그래서 `verified=True`로 `match`가 된 평가에도 이 요약이 남는다.
- 소비자: `test_design_walkthroughs`, `test_family_records`.

## 하네스

### `ReassessmentHarness` (행 338–384)
- 종류: 하네스(`unittest.TestCase`, 시험 없음).
- 하는 일과 반환값: docstring은 "`K1` 검토가 끝나 그 평가의 재평가(reassessment)를 받을 준비가 된 `ReviewFakeEngine`"이다. 상속하거나, 인스턴스에서 `setUp`을 직접 부르고 끝나면 `doCleanups`를 부르라고 적혀 있다.
- 메서드:
  - `setUp` (행 349–356): 임시 디렉터리를 만들어 정리를 등록한다. 그 위에 `ReviewFakeEngine`을 만들고 `_start_identity_review('K1')`로 검토를 연다(scope 단계부터). 큐에 `identity_review`가 남아 있는 동안 `execute()`를 반복한다. 기본 답을 따르므로 `match`로 끝난다. 속성 `directory`, `engine`, `original`(첫 주기 ID), `assessment`를 둔다.
  - `request` (행 358–360): 공개 재평가 요청 모양을 돌려준다: `assessment_id`, `assessment_sha256`(`exact_content_hash(assessment)`), `evidence`.
  - `defect` (행 362–367): 첫 주기의 `initial:1:initial-0` 결과를 낸 실행에 `context_origin=['author']`를 적고, 실행 `author`를 `ended`로 등록한다. 그리고 `{'kind': 'author_context', 'execution_id': ...}` 증거를 돌려준다. 곧 초기 검토자 하나의 맥락에 작성자의 것이 섞였다는 결함을 심는다.
  - `use` (행 369–371): `assessment_uses`에서 이 평가의 사용 기록을 찾아 돌려준다. 없으면 `StopIteration`이 난다.
  - `complete` (행 373–384): 큐의 검토 행동을 모두 `decision` 쪽으로 답한다. `unresolved`면 모든 initial 답을 `unresolved`·범위 미완결로 바꾼다. `mismatch`면 두 곳을 바꾼다. `initial-0`의 initial 답은 발견 `defect`("The stated domain differs")를 가진 `mismatch`가 되고, judge 답은 모든 쟁점을 `approved`로 판정하는 `mismatch`가 된다. `match`면 기본 답을 그대로 쓴다.
- 부작용: 임시 디렉터리(정리 등록됨)와 그 아래의 합성 신뢰 환경 파일.
- 의존: `ReviewFakeEngine`, `exact_content_hash`.
- 시작 상태의 단: 네 단 밖(메모리 엔진 대역).
- 소비자: `test_reassessment`, `test_review_engine`.

### `KnowledgeRoundtripHarness` (행 387–469)
- 종류: 하네스(`unittest.TestCase`, 시험 없음).
- 하는 일과 반환값: docstring은 "실제 Git 저장소 안의, 검증되었지만 아직 검토되지 않은 정리와, 도메인이 만든 봉인된 검토"이다.
- 메서드:
  - `setUp` (행 398–415): 임시 디렉터리에 `git_init`으로 저장소를 만들고 새 `RI` ID의 `ResearchRepository`를 둔다. 합성 신뢰 환경 `TE-test`를 만들고(`synthetic-lean`), `verified_knowledge(environment, binding=binding, identity=False)`로 검증된 정리 하나를 얻는다. 주석(행 411)대로 `current_state`로 생명주기 게이트를 통과하는 상태를 만든다. `lean_command=['synthetic-lean']`로 만든 프로필 가운데 `identity_review` 프로필 하나와 용량 제약을 상태에 둔다. 속성 `root`, `repo`, `state`, `runtime`, `kid`, `profile`을 둔다.
  - `cycle` (행 417–454): `kid`에 대한 완결된 합성 검토 하나를 순수 주기로 돌리고 실행을 기록한다. `scoped_start(proposal, reviewers=2, max_rounds=1)`에서 정책과 범위를 얻고, 그 정책으로 scope 단계부터 시작하는 주기를 새로 연다(`start_review`). 활동 하나를 연다. `next_actions`가 남는 동안 `review_stage_output`으로 답을 만든다. scope 단계에는 준비한 범위를 넣는다. `mismatch`면 `initial-0`에 이의 `objection`을 넣고, `unresolved`면 모든 initial을 미해결로 만든다. 답은 `accept_result`로 받아들인다. 행동마다 실행을 만들어 활동에 배정하고, 다음 순서로 전이한다: `starting` → `running` → 제출 영수증 `accepted` → `stopping` → `ended`/`output_accepted`. 끝에 `self.assertEqual(cycle['decision'], decision)`로 주기의 결정이 요청한 것과 같은지 단언한다. 이것이 대역 안의 검사다. 주기에 ID, `knowledge_id`, `identity_basis`, `policy_ref='policy:fixture'`를 붙여 `runtime['review_cycles']`에 넣고 돌려준다.
  - `assessment` (행 456–462): `cycle(decision)`으로 주기를 만들고 `identity_assessment`를 기록한 뒤(`kr.record_identity_assessment`) 평가 ID를 돌려준다.
  - `roundtrip` (행 464–469): 처음에는 `repo.initialize`로, 이후에는 `save_with_state`로 상태를 게시한다. 그다음 `repo.load()`로 다시 읽어 `head`, `state`, `runtime`을 바꾼다.
- 부작용: 실제 Git 저장소(임시 디렉터리, 정리 등록됨)와 커밋. `git_init`은 프로세스당 한 번 `git init` 자식 프로세스를 돌린 모형을 복사한다.
- 의존: `research_fixtures.current_state`·`git_init`·`trust_environment`·`trust_fixture`, `knowledge_fixtures.verified_knowledge`, `scoped_start`, `review_stage_output`, `ResearchRepository`, `build_profiles`, `review_cycle`, `activities`, `execution_lifecycle`, `kr`.
- 시작 상태의 단: 네 단 밖(합성 상태를 실제 Git 저장소에 직접 게시).
- 소비자: `test_knowledge_storage`, `test_reassessment`.

### `ImpactReviewHarness` (행 472–542)
- 종류: 하네스(`unittest.TestCase`, 시험 없음).
- 하는 일과 반환값: docstring은 "영향 검토를 위해 보류된 research_work 묶음(bundle)"이다. 이 묶음은 `A`와 `C`를 고치고 영향 집합에 `B`를 선언한다.
- 메서드:
  - `seal_review_fixture` (행 484–504): docstring은 "소비자를 시험하기 전에 실제 중앙 포착(central capture) 형식을 쓴다"이다. 차례는 다음과 같다.
    1. `fixed['action']`의 스키마로 제출 도구를 설치한다(`submission.install_tools`).
    2. `output`을 `draft.json`으로 쓰고 `submission.seal_submission`으로 봉인한다.
    3. `self.assertTrue(sealed['passed'], ...)`로 봉인 통과를 단언한다. 이것이 대역 안의 검사다.
    4. 생명주기 사건만 autospec으로 막은 `bare_engine()`의 `_stage_submission_capture`로 포착 산출물을 만든다. 영수증 모양은 `submit_intent`, `accepted`, `origin='explicit_tool'`이다.
    5. 실행을 `ended`/`output_accepted`로 전이하고 `submitted_output_ref`를 적는다.
    6. 게시할 산출물을 돌려준다.
  - `setUp` (행 506–527): `self.api = do_math.integration`으로 둔다. 빈 온톨로지 인스턴스에 관찰(observation) 후보 `A`, `B`, `C`를 가져오고, 생산 실행 `EX-producer`를 `running`(입력 스냅숏 `fixed-input`)으로 둔다. 생산자 출력은 `two_observation_output()`에서 지식을 비운 것이다. 여기에 통합 묶음 `IN-held` 하나를 둔다. 묶음의 구성원은 `output`과 두 `knowledge_changes`이고, 영향 집합은 `[B]`, `previous_hashes`는 `A`와 `C`의 내용 해시다. 확장은 `A`와 `C`의 요약을 바꾸는 `knowledge_changes` 둘이다. 각 변경은 영향 집합 `[B]`를 가진다. 이것을 `api.split_bundles(output, extensions, research_work_context())`로 나눈 첫 묶음을 `self.bundle`에 둔다.
  - `request` (행 529–531): `api.bundle_impact_request(instance, runtime, bundle, producer_execution_id="EX-producer", input_snapshot=...)`의 결과를 돌려준다.
  - `review_output` (행 533–542): 독립 영향 검토의 출력을 돌려준다. `impact_review`는 요청의 `integration_id`, `payload_sha256`, `producer_execution_id`, `input_snapshot`을 복사한다. 요청의 모든 계획에 대해 `approve` 결정을 싣고, `affected_ids`는 계산된 영향과 선언된 영향의 합집합이다. 자신의 통합 묶음은 `IN-review` 하나다.
- 부작용: `seal_review_fixture`는 호출자가 준 `workspace`에 제출 도구와 `draft.json`을 쓴다.
- 의존: `do_math.integration`, `do_math.knowledge.content_hash`, `knowledge_io`, `record_fixtures.observation_knowledge`·`research_work_context`·`two_observation_output`, `contracts.action_schema`, `submission.install_tools`·`seal_submission`, `research_fixtures.bare_engine`, `transition_execution`.
- 시작 상태의 단: 1단(순수 도메인 함수). `seal_review_fixture`만 파일 시스템을 쓴다.
- 소비자: `test_family_records`, `test_impact_review`, `test_review_engine`.

## 관계

- 다른 픽스처 모듈과의 의존: `research_fixtures`에서 거버넌스 시작, 신뢰 환경, 범위 확정 검토(`start_scoped_review`), `bare_engine`, `git_init`, `current_state`를 가져온다. `engine_fixtures.FakeEngine`은 `reviewed_candidate`의 신뢰 환경 활성화에만 쓴다. `knowledge_fixtures`는 검증된 지식과 형식 증거를, `record_fixtures`는 실행 상태와 관찰 출력을 준다. 반대 방향의 의존은 없다. `consumers.json`에서 이 모듈의 소비자는 모두 시험 모듈이다.
- 시작 상태 체계에서의 자리: 이 모듈의 정의는 `restore_template` 템플릿(2·3단)을 쓰지 않는다. 순수 주기 함수와 `ImpactReviewHarness`는 1단에 속한다. `ReviewFakeEngine`과 `ReassessmentHarness`는 메모리 엔진 대역이고, `KnowledgeRoundtripHarness`는 실제 Git 저장소 위의 합성 상태다. 검토 흐름을 공개 경로에서 보는 시험은 이 모듈이 아니라 `purpose_fixtures`의 `purpose_state(until='review')`나 `ActivatedPurposeHarness`에서 시작한다.
- 답의 방향: `ReviewFakeEngine.execute`는 `match` 쪽 기본 답을, `review_stage_output`은 `mismatch` 쪽 기본 답을 낸다. `ReassessmentHarness.complete`와 `KnowledgeRoundtripHarness.cycle`은 이 기본 답에 `decision`별 변경을 얹어 `match`, `mismatch`, `unresolved` 세 결말을 만든다.
