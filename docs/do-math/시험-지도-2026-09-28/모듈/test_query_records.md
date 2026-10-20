# test_query_records

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_query_records.py` (85행) |
| 클래스 / 테스트 | 2 / 4 |
| 시험 대상 제품 코드 | `do_math/engine.py`의 `query_records`, `read_record`, `_query_record`(`_QUERY_FAMILIES`); `do_math/planning.py`의 `RECORD_FAMILIES`; `do_math/repository.py`의 `ResearchRepository.query`, `save_with_state`, `load`, `read`, `RepositoryCursorError`; `do_math/knowledge_io.py`의 `import_candidate` |
| 사용하는 픽스처 모듈 | `engine_fixtures`: `QUERY_INSTANCE_ID`, `start_query_repository` |
| 격리 표지 | 없음 |
| 시작 상태 | `QueryFamilyNameTests`는 1단. `QueryRecordTests`는 `start_query_repository`로 공개 `initialize`를 실제로 돌린 뒤 저장소 계층에서 지식 레코드와 산출 파일을 발행한 상태(4단의 공개 초기화 + 저장소 직접 쓰기, 활성화는 없음) |

## 목적

모듈 docstring은 "모델 실행 없이 고정 스냅숏에서 하는 레코드·파일 질의 검사"라고 밝힌다. 검사하는 계약은 셋이다. 질의 결과의 `family` 이름은 조건 문법이 쓰는 이름이다. 레코드 질의 커서와 파일 질의 커서는 자기가 만들어진 스냅숏에 묶이므로 머리(head)가 전진한 뒤에도 옛 스냅숏을 이어 읽는다. 관계 질의는 방향을 가리고, 레코드 읽기는 저장된 바이트의 해시를 낸다. 제품 좌표는 `engine.py`의 `_query_record`(행 371–376), `query_records`(행 379), `read_record`(행 429–432)와 `repository.py`의 `ResearchRepository.query`(커서 복호화와 스냅숏 대조)다.

## 모듈 수준 요소

- `SCRIPTS` (행 11): 스킬의 `scripts/` 폴더. 행 12–13에서 `sys.path`에 없으면 맨 앞에 넣는다.
- 행 84–85: 직접 실행하면 `unittest.main(verbosity=2)`로 이 모듈의 시험을 돈다.

## QueryFamilyNameTests (행 22–33)

`unittest.TestCase`를 그대로 상속하고 표지, 속성, 훅, 도우미가 없다.

### `test_query_family_names_are_the_condition_grammar_names` (행 23–33)
- 성질: 질의가 돌려주는 레코드의 `family`는 저장 가족 이름이 아니라 조건 문법의 가족 이름이다.
- 준비: `planning.RECORD_FAMILIES`의 모든 항목 가운데 저장 가족(`stored`)이 `None`이 아닌 것. 항목마다 `{"family": stored, "record": {"id": "X", "family": "relation"}}` 행을 만든다.
- 실행: `_query_record(row)`.
- 단언: 결과의 `family`가 문법 이름 `name`(예: 저장 가족 `goal_judgments`면 `goal-judgment`)과 같다. 저장 가족 `question_links`는 `question`으로 바뀐다. 문법이 이름 짓지 않은 저장 가족 `capability_evidence`는 이름이 그대로 남는다.
- 대역: 없음.
- 비고: `subTest(stored=stored)`로 가족마다 나눈다. `instance` 항목은 저장 가족이 `None`이라 빠진다. 행 27의 주석대로, 레코드 안에 원래 있던 `family` 필드는 `kind_definitions`에서만 `definition_family`로 옮겨진다. 이 테스트는 그 이동 결과를 단언하지 않고, 모든 가족에서 바깥 `family`가 덮어써지는 것만 본다.

## QueryRecordTests (행 36–81)

`unittest.TestCase`를 그대로 상속하고 표지와 클래스 속성이 없다.

- `setUp` (행 37–38): `engine_fixtures.start_query_repository(self)`를 부른다. 이 도우미는 테스트 객체에 다음을 둔다. `root`(`enterContext`로 연 임시 폴더), `git`(`git_init`으로 만든 저장소), `workspace`. 그 위에 공개 `engine.initialize(git, goal="A goal", workspace=..., instance_id=QUERY_INSTANCE_ID, config={"operator_enabled": False, "scholarly_enabled": False})`를 실제로 돌려 `initial_head`를 얻는다. 적재한 상태에 `import_candidate`로 지식 레코드 둘을 넣는다. "One"은 definition, 요약 `alpha`이고 "Two"는 theorem, 요약 `beta`다. 그 ID가 `kids`다. `import_relation`으로 One이 Two를 지지(`supports`)하는 관계를 더하고 그 ID를 `relation_id`로 둔다. `save_with_state`로 발행한 커밋이 `old_head`다. 같은 상태에 산출 파일 두 개(`runtime/artifacts/query-fixture/a.txt`=`b"needle alpha"`, `b.txt`=`b"needle beta"`)를 더해 한 번 더 발행한 커밋이 `file_head`다. 공개 초기화까지만 하고 활성화와 엔진 실행은 하지 않으므로 모델 실행이 없다.

### `test_record_cursor_reuses_its_old_snapshot_after_head_advances` (행 40–54)
- 성질: 레코드 질의의 커서는 머리가 전진한 뒤에도 자기가 만들어진 옛 스냅숏을 계속 읽으며, 새 레코드를 섞지 않는다.
- 준비: 클래스 절의 `setUp`. 추가로 `file_head` 상태에 `import_candidate`로 question 레코드 "Three"를 넣고 `save_with_state`로 발행해 머리를 전진시킨다.
- 실행: `query_records(git, QUERY_INSTANCE_ID, snapshot=old_head, limit=1)`로 첫 쪽을 읽는다. 머리를 전진시킨 뒤 `query_records(..., cursor=first["next_cursor"], limit=10)`로 이어 읽는다.
- 단언: 첫 쪽의 `snapshot`이 `old_head`이고 `truncated`가 참이다. 이어 읽은 쪽의 `snapshot`도 `old_head`다. 이어 읽은 항목의 레코드 ID에 새 question의 ID가 없다.
- 대역: 없음.

### `test_relations_direction_hash_and_absent_record` (행 56–67)
- 성질: 관계 질의는 나가는 방향과 들어오는 방향을 가리고, 레코드 읽기는 저장 바이트의 해시를 내며 요약을 해설 레코드로 분리하고, 없는 레코드는 오류다.
- 준비: 클래스 절의 `setUp`. `old_head`를 쓴다.
- 실행: `query_records(..., related_to=kids[0], direction="outgoing")`와 `query_records(..., related_to=kids[1], direction="incoming")`. `read_record(git, QUERY_INSTANCE_ID, kids[0], snapshot=old_head)`. 그 레코드의 `exposition_id`로 `read_record`. `read_record(..., "K-absent", ...)`.
- 단언: 나가는 방향의 ID 집합은 `{kids[1], relation_id}`, 들어오는 방향은 `{kids[0], relation_id}`다. 곧 관계 레코드와 반대편 끝이 함께 나온다. 읽은 레코드의 `sha256`이 `repository.read(record["path"], old_head)` 바이트의 SHA-256과 같다. 지식 레코드에는 `summary` 키가 없다. 해설 레코드의 `items` 가운데 `text == "alpha"`인 항목이 있다. 없는 ID는 `KeyError`를 던진다(예외 유형만 본다).
- 대역: 없음.

### `test_file_cursor_reuses_old_snapshot_and_malformed_cursor_is_error` (행 69–81)
- 성질: 파일 질의의 커서도 옛 스냅숏에 묶이고, 형식이 깨진 커서는 오류이며, 결과가 없는 질의는 빈 쪽 하나를 낸다.
- 준비: 클래스 절의 `setUp`. 추가로 `file_head`의 상태를 그대로 다시 `save_with_state`해 머리를 전진시킨다.
- 실행: `repository.query(snapshot=file_head, prefix="runtime/artifacts/query-fixture/", text="needle", limit=1)`로 첫 쪽을 읽는다. 머리를 전진시킨 뒤, 스냅숏을 주지 않고 커서만 주어 `limit=10`으로 이어 읽는다. 깨진 커서 `"%%%"`로 질의한다. `text="missing"`으로 질의한다.
- 단언: 이어 읽은 쪽의 `snapshot`이 `file_head`이고, 항목 경로가 `["runtime/artifacts/query-fixture/b.txt"]` 하나다. 깨진 커서는 `RepositoryCursorError`를 던진다(유형만 본다). `missing` 질의는 `total=0`, `items=[]`, `truncated=False`다.
- 대역: 없음.
- 비고: 이 테스트는 `file_head`를 적재한 상태를 바꾸지 않고 그대로 `save_with_state`한다. `test_repository`의 `SaveWithStateTests.test_unchanged_state_is_noop_and_returns_normalized_reload_views`가 고정하듯, 바뀌지 않은 상태의 저장은 새 커밋을 만들지 않고 같은 머리를 돌려준다. 그래서 이름이 말하는 "옛 스냅숏 재사용"의 전제인 머리 전진이 이 테스트에서는 일어나지 않는다. 이어 읽은 쪽의 `snapshot == file_head` 단언은 현재 머리와도 같으므로, 커서의 스냅숏이 현재 머리 대신 쓰였는지를 가려내지 못한다. 레코드 커서 쪽 테스트(`test_record_cursor_reuses_its_old_snapshot_after_head_advances`)는 새 레코드를 더해 머리를 실제로 전진시킨다.

## 관계

- 같은 커서 계약을 저장소 계층에서 검사하는 테스트는 `test_repository`의 `test_query_cursor_is_bound_to_snapshot_and_query_and_has_no_empty_page`다. 이 모듈은 엔진의 `query_records`·`read_record` 층과, 관계·가족 이름 투영을 더한다.
- CLI 층의 질의 출처는 `test_cli_surface`의 `test_file_query_and_read_include_resolved_snapshot_provenance`가 검사한다.
- 픽스처 의존: `engine_fixtures.start_query_repository`와 `QUERY_INSTANCE_ID`. 이 도우미는 안에서 `research_fixtures.git_init`과 공개 `engine.initialize`를 쓴다.
- 이 모듈에만 있는 도우미는 없다.
