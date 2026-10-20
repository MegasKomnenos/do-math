# test_reading_map

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_reading_map.py` (97행) |
| 클래스 / 테스트 | 2 / 7 |
| 시험 대상 제품 코드 | `do_math/contracts.py`의 `reading_map`, `prompt_documents`, `render_prompt`; `do_math/engine.py`의 `ResearchEngine._context`, `ResearchEngine._documents`, `_installation_manifest` |
| 사용하는 픽스처 모듈 | `purpose_fixtures`: `ActivatedPurposeHarness`(그 `make_active`가 `research_fixtures.restore_template`과 `state_fixtures.active_instance`를 쓴다) |
| 격리 표지 | 없음 |
| 시작 상태 | `ReadingMapTests`: 1단(임시 스킬 루트를 만들어 문서 적재 함수를 직접 호출). `DocumentContextTests`: 2단(`make_active`로 `state_fixtures.active_instance` 템플릿 복원) |

## 목적

모듈 docstring은 "선언된 읽기 순서가 실제 모델 입력에 바뀌지 않고 도달해야 한다"라고 밝힌다. 역할마다 읽을 문서의 유일한 정본은 `SKILL.md`의 `<!-- role-reading-map:start -->`와 `<!-- role-reading-map:end -->` 사이 표다. `reading_map`은 이 표를 읽고 `common` 행과 역할 행을 이어 역할별 경로 목록을 만든다(docstring "Read the sole document assignment table authored in SKILL.md."). `prompt_documents`는 그 순서대로 각 문서의 바이트를 읽고 `path`, `sha256`, `content`를 돌려준다. `render_prompt`는 그 문서들을 프롬프트에 싣는다. 이 모듈은 네 가지를 확인한다. 순서가 선언과 같다. 바이트가 그대로 실린다. 선언이 바뀌면 실리는 문서도 바뀐다. 누락되거나 모호한 선언은 오류다. 엔진 층에서는 문서가 작업 공간에 복구 가능한 사본으로 놓이고, 참조 문서가 설치 판본 확인에 포함되는지 본다.

## 모듈 수준 요소

- 행 9: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리다.
- 행 10–11: `contracts`의 `prompt_documents`, `render_prompt`와 `purpose_fixtures`의 `ActivatedPurposeHarness`를 import한다.
- 행 97: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

## ReadingMapTests (행 14–73)

`unittest.TestCase`를 그대로 상속하고 표지와 도우미 메서드는 없다.

`setUp` (행 15–28)은 임시 스킬 루트 `self.root`를 만들고, `addCleanup`으로 정리를 등록한다. 실제 설치본(`Path(__file__).resolve().parents[2]`, 곧 스킬 폴더)에서 `SKILL.md`를 `copy2`로, `계약/` 폴더 전체를 `copytree`로 복사한다. 그래서 읽기 표와 역할 계약 문서는 실제 판본이다. 나머지 문서는 짧은 대역 문장으로 새로 쓴다.
- `GLOSSARY.md`: "The common definition is supplied here."
- `references/공통-실행.md`: 바이트 `b'Common procedure.\r\nKeep this exact edition.\r\n'`. 줄 끝이 CRLF여서 바이트 보존 확인에 쓰인다.
- `references/모델과-실행예산.md`: "Select a model from difficulty and importance, then wait for its slot."
- `references/지식-저작과-재사용.md`: "Apply the existing result only within its actual assumptions."
- `references/학술자료-활용.md`: "Read the original rendered equation before criticizing its transcription."
- `references/자기-점검.md`: "Answer each due self-check rule with its evidence."

`references/과제-착수조건.md`와 `references/입력-소비자.md`는 `setUp`에서 만들지 않는다. 필요한 테스트가 직접 만든다.

### `test_declared_shared_procedures_are_supplied_in_reading_order` (행 30–41)
- 성질: `research_work` 역할은 공통 문서와 제 역할 문서를 선언된 순서대로 원 바이트 그대로 받고, 다른 역할에만 배정된 문서는 받지 않는다.
- 준비: `setUp`의 임시 스킬 루트.
- 실행: `prompt_documents('research_work', skill_root=self.root)`와 `render_prompt('research_work', {'question': 'Use the documented assumption'}, skill_root=self.root)`.
- 단언: 경로 목록이 정확히 일곱 개의 순서다: `SKILL.md`, `GLOSSARY.md`, `references/공통-실행.md`, `references/지식-저작과-재사용.md`, `references/학술자료-활용.md`, `references/자기-점검.md`, `계약/연구-수행.md`. 문서마다 `content.encode('utf-8')`가 디스크 바이트와 같고(CRLF 보존 포함), `sha256`이 그 바이트의 SHA-256과 같다. 렌더된 프롬프트는 "Apply the existing result only within its actual assumptions."를 포함한다. 프롬프트는 `'For research_plan:'`을 포함하지 않는다(실패 메시지: 다른 역할이 따로 관리되는 계획 규칙 사본을 받으면 안 된다). 또 `'Select a model from difficulty and importance'`를 포함하지 않는다(실패 메시지: 모델 선택 규칙은 모델을 평가하는 역할에만 간다).
- 대역: 없음. 임시 스킬 루트의 참조 문서가 대역 텍스트다.
- 비고: `'For research_plan:'` 문구는 현재 저장소에서 이 테스트와 그 생성 사본(`.agents/skills/do-math/scripts/tests/test_reading_map.py` 40행) 밖의 어떤 `.md`나 `.py`에도 나오지 않는다. 그래서 이 음성 단언은 계획 규칙 사본이 다시 들어오는 퇴행을 막는 감시로만 작동한다. 그런데 이 임시 루트에서 실제 판본으로 실리는 문서는 `SKILL.md`와 `계약/연구-수행.md`뿐이고, `GLOSSARY.md`와 `references/` 문서는 `setUp`의 대역 문장이다. 따라서 이 감시는 그 두 실제 문서에 사본이 들어오는 경우만 잡고, 실제 공통 참조 문서(`references/`)에 들어오는 경우는 잡지 못한다.

### `test_role_rows_add_their_references_after_the_common_documents` (행 43–55)
- 성질: 각 역할 행의 문서는 공통 문서 다섯 개 뒤에 그 행의 순서대로 붙는다.
- 준비: `setUp`의 루트에 `references/과제-착수조건.md`와 `references/입력-소비자.md`를 "Role reference."로 추가한다. 공통 목록은 `SKILL.md`, `GLOSSARY.md`, `references/공통-실행.md`, `references/지식-저작과-재사용.md`, `references/학술자료-활용.md`다.
- 실행: 역할 여섯 개에 대해 `prompt_documents(role, skill_root=self.root)`.
- 단언: 각 역할의 경로 목록이 공통 목록 뒤에 다음을 붙인 것과 정확히 같다.
  - `research_preparation`: `references/모델과-실행예산.md`, `references/과제-착수조건.md`, `계약/후보-준비.md`
  - `research_plan`: `references/모델과-실행예산.md`, `계약/연구-계획.md`
  - `task_contract_review`: `references/모델과-실행예산.md`, `references/과제-착수조건.md`, `계약/작업-계약-검토.md`
  - `operational_review`: `references/자기-점검.md`, `계약/운영-점검.md`
  - `intent_interpretation`: `references/입력-소비자.md`, `계약/의도-해석.md`
  - `goal_audit`: `계약/목표-감사.md`
- 대역: 없음.
- 비고: `subTest(role=...)`의 여섯 케이스는 위의 역할이다. `SKILL.md` 표의 나머지 역할(`research_work`, `identity_review`, `supplemental_research`, `maintenance`)은 여기서 보지 않는다. `research_work`는 앞 테스트가 본다. 기대 목록은 현재 `SKILL.md` 표와 일치한다.

### `test_changing_the_declared_role_path_changes_the_supplied_document` (행 57–62)
- 성질: 읽기 표에서 역할 문서의 경로를 바꾸면 실제로 실리는 문서도 바뀐다. 곧 경로는 코드에 고정되어 있지 않다.
- 준비: 임시 `SKILL.md`의 `` `계약/연구-수행.md` ``를 `` `계약/특정-수행.md` ``로 바꾸고, `계약/특정-수행.md`를 "The replacement is the declared role contract."로 만든다.
- 실행: `prompt_documents('research_work', skill_root=self.root)`.
- 단언: 마지막 문서의 `path`가 `'계약/특정-수행.md'`다.
- 대역: 없음.

### `test_missing_required_reference_is_not_silently_omitted` (행 64–66)
- 성질: 선언된 문서가 없으면 조용히 건너뛰지 않고 오류가 난다.
- 준비: 임시 루트에서 `references/공통-실행.md`를 지운다.
- 실행: `prompt_documents('research_work', skill_root=self.root)`.
- 단언: `FileNotFoundError`가 난다. 예외 유형만 본다. 제품의 `_document`가 `read_bytes`로 파일을 읽을 때 난 예외가 그대로 올라온다.
- 대역: 없음.

### `test_missing_or_ambiguous_reading_map_is_an_error` (행 68–73)
- 성질: 읽기 표가 없거나 같은 경로를 두 번 선언하면 오류다.
- 준비: 두 가지 `SKILL.md` 내용. (1) `'No reading map'` 한 줄. (2) 원본에서 `` `SKILL.md`, `GLOSSARY.md` ``를 `` `SKILL.md`, `SKILL.md`, `GLOSSARY.md` ``로 바꾼 것.
- 실행: 각 내용을 `SKILL.md`에 쓰고 `prompt_documents('research_work', skill_root=self.root)`를 부른다.
- 단언: 두 경우 모두 `ValueError`가 난다. 예외 유형만 본다. 제품에서 (1)은 표지 쌍이 정확히 하나가 아니라는 오류("SKILL.md requires exactly one role reading map")에, (2)는 `common` 행의 경로 중복 오류("reading map requires distinct roles and document paths")에 걸린다.
- 대역: 없음.
- 비고: `subTest(text=malformed[:40])`의 두 케이스는 위 (1)과 (2)다.

## DocumentContextTests (행 76–94)

기반 클래스는 `purpose_fixtures.ActivatedPurposeHarness`다. 그 `setUp`은 `install_adapter_fixture`로 `do_math.initialization.adapter_for`를 패치해 외부 관찰만 대역으로 바꾼다. `make_active()`는 `restore_template(state_fixtures.active_instance, config={})`로 합성 활성 상태를 복원하고, `self.root`를 그 템플릿의 루트로 둔다. 그리고 `ResearchEngine(self.root/'repository', instance_id, runner=PurposeRunner(), formal_verifier=formal_fixture)`를 만든다. 클래스 자체에는 속성, 훅, 도우미가 없다.

### `test_declared_documents_have_recoverable_input_copies` (행 77–87)
- 성질: 엔진이 역할 입력을 준비하면 선언된 문서가 작업 공간의 입력 사본으로 놓이고, 그 사본은 엔진이 적재한 문서와 바이트가 같다.
- 준비: 2단. `make_active()`로 합성 활성 상태를 복원하고, 템플릿 루트 아래에 `preview` 작업 공간 폴더를 만든다.
- 실행: `engine._context({'role': 'research_preparation'}, workspace)`.
- 단언: 맥락에 `implementation_documents` 키가 있다. 그 행들의 `path` 목록이 `engine._documents['research_preparation']`의 경로 목록과 같다. 행마다 작업 공간의 `local_path`(제품은 `input/implementation/<path>`로 쓴다) 파일 바이트가 원 문서 `content`의 UTF-8 인코딩과 같고, 그 SHA-256이 행의 `sha256`과 같다.
- 대역: `ActivatedPurposeHarness`의 어댑터 패치, `PurposeRunner`(호출되지 않음), `formal_fixture` 형식 검증기 대역(호출되지 않음).

### `test_installed_reference_changes_are_part_of_the_version_check` (행 89–94)
- 성질: 설치 판본을 확인하는 매니페스트에는 공통 참조 문서가 포함되므로, 참조 문서가 바뀌면 설치 판본도 바뀐 것으로 판정된다.
- 준비: 2단. `make_active()`.
- 실행: `engine._installation_manifest()['files']`.
- 단언: `files`의 키에 `references/공통-실행.md`, `references/지식-저작과-재사용.md`, `references/학술자료-활용.md`가 있다.
- 대역: `ActivatedPurposeHarness`의 어댑터 패치.
- 비고: 이 테스트는 이름과 달리 변경을 일으키지 않는다. 세 경로가 매니페스트에 들어 있다는 사실만 단언한다. `_installation_manifest`는 실제 설치 스킬 루트(`_SKILL_ROOT`)를 해시하므로 임시 루트가 아니라 실제 설치본을 읽는다.

## 관계

- 같은 제품 기능의 다른 층: `test_contracts`의 `test_role_document_missing_fails`, `test_prompt_contains_actual_documents_context_and_schema`, `test_declared_role_documents_are_complete`도 `prompt_documents`와 `render_prompt`를 검사한다. 그 모듈은 계약 전반을 보고, 이 모듈은 읽기 순서와 바이트 보존에 집중한다.
- 픽스처 의존: `purpose_fixtures.ActivatedPurposeHarness`. 그 안에서 `research_fixtures.restore_template`, `state_fixtures.active_instance`, `research_fixtures.install_adapter_fixture`를 쓴다.
- 이 모듈에만 있는 도우미: 없다. `setUp`의 임시 스킬 루트 구성이 이 모듈 고유의 준비다.
- 겹치거나 보완하는 시험: 첫 클래스는 제품 함수에 임시 스킬 루트를 넘겨 선언 변경과 누락을 실험한다. 둘째 클래스는 실제 설치본으로 엔진이 같은 문서를 작업 공간과 판본 확인에 싣는지 본다.
