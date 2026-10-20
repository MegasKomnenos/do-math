# test_reporting

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_reporting.py` (239행) |
| 클래스 / 테스트 | 2 / 8 |
| 시험 대상 제품 코드 | `do_math/reporting.py`의 `timeline`, `timeline_csv`, `snapshot_report`(안에서 `status_report`, `state_checks.inspect_state`, `retention.pending_cleanup_failures`), `render_human_report`, `dispatch_waits`, `render_dispatch_waits`, `task_status`, `ASSURANCE`; `do_math/cli.py`의 `build_parser`, `execute`(`timeline --format csv`); `do_math/engine.py`의 `ResearchEngine._maintenance_cleanup`; `do_math/retention.py`의 `_inventory`; 준비용 `claude_stream.parse_stream`, `payloads.json_safe`, `execution_profiles.execution_observation` |
| 사용하는 픽스처 모듈 | `record_fixtures`: `surface_state`, `stored_surface_state`, `approved_task`; `research_fixtures`: `git_init`, `bare_engine`, `dispatched_launch` |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(투영 함수에 사전 상태 직접 전달) 3개. `ResearchRepository` 대역(`create_autospec`)으로 `snapshot_report`·`timeline`을 부르는 것 3개. `git_init` 저장소에 `stored_surface_state`를 직접 `initialize`한 실제 Git 스냅숏 3개(네 단 밖: 저장소 계층 직접 초기화). 표에서 한 테스트(`test_engine_cleanup_failure_reaches_snapshot_reporting`)는 `bare_engine`과 저장소 대역을 함께 쓰므로 두 무리에 겹쳐 셌다 |

## 목적

모듈 docstring은 없다. 제품 `reporting.py`의 docstring은 "연구 스냅숏과 따로 관찰한 로컬 증거의 투영"이다. 이 모듈은 상태 보고(`snapshot_report`와 사람용 렌더링), 실행 타임라인(`timeline`, CSV 내보내기), 대기와 과제 상태 투영(`dispatch_waits`, `task_status`)이 고정된 스냅숏 하나에서 계산되고 저장 값을 잃지 않는다는 것을 검사한다. 세부 계약은 여섯이다. 공급자 사용량 투영이 Git 왕복을 견딘다. 상태 보고는 산출물 바이트를 읽지 않고 크기만 한 번에 묻는다. 타임라인은 명시적 이어받기(continuation)와 대기 후속을 보존한다. 모르는 시각은 비워 두고 KST 날짜 경계를 넘는다. 투영은 원 상태에서 분리된 사본이다. 정리(cleanup) 실패는 보고까지 전달된다.

## 모듈 수준 요소

- 행 10: 스킬의 `scripts/` 폴더를 확인 없이 `sys.path` 맨 앞에 넣는다.
- 행 11–17: `do_math.reporting`을 이름으로도 가져오고(`reporting.dispatch_waits` 등), 모듈로도 import한다.
- 행 238–239: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

## ReportingTests (행 20–176)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_claude_usage_projection_survives_git_and_timeline` (행 21–60)
- 성질: Claude 스트림에서 해석한 사용량 투영은 Git 저장·적재와 타임라인 투영을 거쳐도 그대로 남고, 보고된 비용은 소수 문자열로 보존된다.
- 준비: Claude 스트림 두 줄을 JSONL 바이트로 만든다. `system/init` 줄과 `result/success` 줄이다. 뒤의 줄은 `usage`(입력 10, 출력 5)와 `modelUsage`(`claude-opus-5`의 `inputTokens=10`, `costUSD=0.01`)를 담는다. `parse_stream`으로 해석한 뒤 네 키(`usage_segments`, `model_usage_reported`, `usage_scope`, `reported_models`)를 골라 `json_safe`로 투영한다. 저장소는 `git_init`과 `new_id("RI")`로 만든다. 상태는 `stored_surface_state()`에 인스턴스 `id`·`workspace`를 채우고 활동 `AC-1`의 `owner_ref`를 인스턴스로 바꾼 것이다. 실행 `EX-1`을 `status="ended"`, `outcome="cancelled"`, `ended_at`, `usage=parsed["usage_total"]`과 네 투영 키로 갱신한다. `provider_observation`은 `execution_observation`으로 만든다. 이 상태로 `initialize`한다.
- 실행: `store.load(head)`로 적재한 실행과 `timeline(root, identifier, snapshot=head)`의 첫 행.
- 단언: 해석 결과의 `turn_completed`가 참이다. 네 키 각각이 저장된 실행과 타임라인 행 양쪽에서 투영 값과 같다. 타임라인 행의 `usage`가 `{"input_tokens": 10, "output_tokens": 5}`다. `provider_observation.reported_fields_json`을 풀어 낸 `model_usage_reported`가 해석 결과와 같다. 저장된 `model_usage_reported["claude-opus-5"]["costUSD"]`가 `{"reported_decimal": "0.01"}`다. 곧 부동소수 비용은 `json_safe`에서 소수 문자열 표기로 바뀌어 저장된다.
- 대역: 없음. 실제 Git 저장소를 쓴다.

### `test_status_reports_artifact_presence_and_length_in_one_batch_without_bytes` (행 62–97)
- 성질: 상태 보고는 산출물 바이트를 읽지 않고, 산출물 12개의 존재와 길이를 한 번의 배치 크기 조회로 확인하며, 길이가 바뀌거나 사라진 산출물을 막힘(blocked)으로 보고한다.
- 준비: `surface_state()`의 실행 `EX-1`에 출력 파일 12개를 단다. 각각 `runtime/artifacts/BA-1/<번호>`를 가리키고 `b'preserved result'`의 해시와 길이를 적는다. 머리는 `'a'*40`이다. 저장소 대역이 쓸 `stored` 사전은 경로마다 같은 길이를 준다.
- 실행: `do_math.reporting.ResearchRepository`를 대역으로 바꾸고 `snapshot_report(Path('.'), 'RI-test', requested_areas=['record_storage'])`를 부른다. `stored`에서 첫 경로의 길이를 1 늘리고 둘째 경로를 지운 뒤 한 번 더 부른다.
- 단언: 첫 보고의 `inspection.status`가 `healthy`다. `blob_sizes`는 정확히 한 번, `(paths, head, missing='omit')`로 불렸다. 둘째 보고의 상태는 `blocked`이고, 발견(findings)들의 `evidence`와 산출물 경로 집합의 교집합이 바뀐 두 경로 `{paths[0], paths[1]}`다.
- 대역: `create_autospec(ResearchRepository, instance=True)`. `load`는 `(head, instance, runtime)`을 돌려준다. `read`와 `read_many`는 호출되면 `AssertionError('status reads no artifact bytes')`를 던진다. `blob_sizes`는 `sizes` 함수다. `sizes`는 받은 스냅숏이 `head`인지 단언하고, `missing='omit'`이 아니면서 없는 경로가 있으면 `GitStateStoreError('batch size did not return a blob')`를 던지며, 있는 경로의 크기만 돌려준다. `patch('do_math.reporting.ResearchRepository', return_value=store)`로 제품이 여는 저장소를 이 대역으로 바꾼다.
- 비고: 행 91의 주석은 "길이 변화나 없는 산출물은 막고, 길이가 같은 바이트 변화는 check의 몫"이라고 밝힌다. 곧 상태 보고는 바이트 비교를 하지 않는다. 바이트 비교는 `test_state_checks`의 `test_engine_entry_checks_presence_and_length_while_check_compares_bytes`가 검사한다.

### `test_timeline_preserves_explicit_continuation_and_pending_successor` (행 98–120)
- 성질: 타임라인은 실행이 명시한 이어받기만 싣고, 그 실행을 이어받는 대기 행동을 후속으로 붙이며, CSV 내보내기에도 같은 값을 싣고, 입력 상태를 바꾸지 않는다.
- 준비: 사전 runtime. `EX-first`(ended, 행동 `AC-work`)와 `EX-second`(ended, `continuation_of="EX-first"`, 행동도 같은 이어받기를 가짐). 대기열에는 `EX-second`를 이어받는 `pending`(`AC-work`, `research_work`)과, 관련 없는 실행을 이어받는 `AC-other`가 있다. 비교용 `deepcopy`를 떠 둔다.
- 실행: 저장소 대역을 넣고 `timeline(Path('.'), 'RI-test', snapshot='a'*40)`, 이어서 `timeline_csv(value)`를 `csv.DictReader`로 읽는다.
- 단언: `EX-first`의 `continuation_of`는 `None`이고 `next_actions`는 `[]`다. `EX-second`의 `continuation_of`는 `EX-first`이고 `next_actions`는 `[pending]`이다. `AC-other`는 어느 행에도 붙지 않는다. CSV의 `EX-second` 행에서 `continuation_of`는 `EX-first`이고, `next_actions` 칸을 JSON으로 풀면 `[pending]`이다. 호출 뒤 runtime이 사본과 같다.
- 대역: `create_autospec(ResearchRepository, instance=True)`. `load`는 스냅숏 인자와 상관없이 `('a'*40, {}, runtime)`을 돌려준다. `patch('do_math.reporting.ResearchRepository', ...)`로 주입한다.
- 비고: 이름의 "명시적 이어받기"는 `EX-first`처럼 `continuation_of`를 적지 않은 실행에 추론 값을 넣지 않는다는 뜻이다. 단언은 그것을 `None` 비교로 확인한다.

### `test_fixed_snapshot_preserves_unknown_times_and_crosses_the_kst_date` (행 122–151)
- 성질: 타임라인은 요청한 고정 스냅숏을 읽고, 모르는 시각은 채우지 않으며, UTC 시각을 KST로 옮길 때 날짜 경계를 넘긴다. CLI의 CSV 출력은 함수 결과와 같다.
- 준비: `git_init` 저장소에 `stored_surface_state()`를 앞 테스트처럼 채워 `initialize`한다. 실행 `EX-1`은 `status='ended'`이고, 행동은 `{'id': 'A', 'role': 'research_work', 'lineage_id': 'L'}`, 모델은 `claude-opus-5`, `created_at='2026-09-18T15:01:02+00:00'`, `ended_at='2026-09-18T15:02:03+00:00'`, 결과는 `cancelled`다. 시작 시각은 적지 않는다. 그 뒤 인스턴스 `title`을 바꿔 `save_with_state`로 머리를 전진시킨다.
- 실행: `timeline(root, identifier, snapshot=head)`와 `timeline_csv`. CLI 파서로 `timeline --repository ... --instance ... --snapshot <head> --format csv`를 해석해 `execute`에 넘긴다.
- 단언: `counts_by_unit`이 `{'internal_execution': 1}`이다. 첫 행의 `created_at_local`이 `'2026-09-19T00:01:02+09:00'`이다(15시 UTC가 KST 다음 날 0시). `started_at_utc`와 `started_at_local`은 `None`이다. `lineage_id`는 `'L'`이다. CSV의 `started_at_utc` 칸은 빈 문자열이다. CLI는 종료 코드 0이고, 출력이 `timeline_csv(value)`와 같다.
- 대역: 없음. 실제 Git 저장소를 쓴다.
- 비고: 이름의 "고정 스냅숏"은 머리를 전진시킨 뒤 옛 `head`를 지정해 읽는 준비로 표현된다. 단언은 스냅숏 필드를 직접 비교하지 않는다. 대신 CLI 출력이 같은 스냅숏의 함수 결과와 같음을 확인한다.

### `test_non_task_wait_projection_is_detached_and_printable` (행 153–164)
- 성질: 과제에 속하지 않은 행동의 배정 대기도 투영되어 출력되고, 투영은 원 상태와 분리된 사본이며, 그 행동이 실행 중이면 대기가 투영되지 않는다.
- 준비: 대기열에 `research_preparation` 행동 `AC-prep` 하나. `dispatch_wait`는 `{kind: 'capacity', constraint_id: 'BC-old', next_owner: 'user'}`다.
- 실행: `reporting.dispatch_waits(runtime)`, `reporting.render_dispatch_waits({'tasks': [], 'dispatch_waits': rows})`.
- 단언: 렌더링된 글에 `AC-prep`, `capacity`, `BC-old`가 있다. 투영 행의 `wait.kind`를 바꿔도 원 대기열의 값은 `capacity`로 남는다. `AC-prep`을 행동으로 가진 `running` 실행 `EX-live`를 더하면 `dispatch_waits`가 `[]`를 돌려준다.
- 대역: 없음.
- 비고: 이 테스트 뒤 원문 행 165–166은 빈 줄 둘이다.

### `test_task_rows_of_an_ended_instance_carry_no_readiness` (행 167–176)
- 성질: 종료된 인스턴스의 과제 행에는 준비도(readiness)와 대기가 없다.
- 준비: `record_fixtures.approved_task()`의 과제를 `status='active'`로 바꾼다.
- 실행: `reporting.task_status(instance, runtime)`. 이어서 runtime의 `status`를 `closed`와 `completed`로 바꾼 사본 각각으로 다시 부른다.
- 단언: 활성 상태에서는 첫 행의 `readiness.state`가 `ready`다(대조군). 종료 상태에서는 행이 정확히 하나이고(`row, =` 풀기), `readiness`가 `None`, `waits`가 `[]`다.
- 대역: 없음.
- 비고: `subTest(status=ended)`로 `closed`와 `completed`를 나눈다.

## StatusSnapshotTests (행 179–235)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_engine_cleanup_failure_reaches_snapshot_reporting` (행 180–209)
- 성질: 엔진의 유지보수 정리가 파일 검사 실패로 저하(degraded)되면, 그 실패가 기록되어 상태 보고의 발견·정리 실패·사람용 렌더링에 모두 나타나고, 실행 폴더는 지워지지 않는다.
- 준비: `surface_state()`의 실행 `EX-1`을 `status='ended'`, `outcome='execution_incomplete'`로 바꾼다. `dispatched_launch`로 만든 발사표에 `phase='finished'`를 덧씌우고, `capacity={'local_termination': 'confirmed'}`를 둔다. 인스턴스 `workspace`를 임시 폴더로 두고 그 아래에 `runs/EX-1` 폴더를 만든다. 엔진은 `bare_engine(instance, runtime, head='a'*40, store=create_autospec(Repository, instance=True))`다.
- 실행: 엔진의 `_cleanup_scope`가 `['EX-1']`을, `_retention_state`가 준비한 `state`를 돌려주도록 패치한다. `state`는 `approved_execution_ids=['EX-1']`, 빈 보호 참조를 담는다. `_save`도 패치하고, `do_math.retention._inventory`가 `PermissionError('cannot inspect files')`를 던지게 한다. 그 상태로 `engine._maintenance_cleanup({}, 'EX-maint')`를 부른다. 이어서 `engine.store.load`가 `('a'*40, instance, runtime)`을 돌려주게 하고, 보고용 저장소도 그 대역으로 바꿔 `snapshot_report(Path(directory), 'IN-1', requested_areas=['record_storage'])`를 부른다.
- 단언: 정리 결과의 `status`가 `degraded`다. runtime `history`의 마지막 항목 `kind`가 `maintenance_cleanup`이다. 보고의 `inspection.findings` 가운데 `status='degraded'`이고 메시지에 `cannot inspect files`가 든 행이 있다. `cleanup_failures[0].next_owner`가 `maintenance`다. `render_human_report(report)`에 `degraded`가 들어 있다. `runs/EX-1` 폴더가 그대로 있다.
- 대역: `create_autospec(ResearchRepository, instance=True)` 저장소. `patch.object`로 바꾼 `engine._cleanup_scope`, `engine._retention_state`, `engine._save`. `patch('do_math.retention._inventory', side_effect=PermissionError(...))`. `patch('do_math.reporting.ResearchRepository', return_value=engine.store)`.
- 비고: 엔진 경로는 `bare_engine`으로 저장소 적재 없이 만든다. 실제 파일 시스템에는 임시 폴더와 `runs/EX-1`만 있다.

### `test_json_and_human_status_share_one_snapshot` (행 211–235)
- 성질: JSON 상태 보고와 사람용 렌더링은 같은 스냅숏에서 나오며, 관찰되지 않은 호스트 필드는 비어 있고, 알 수 없는 호스트 관찰 필드는 거부된다.
- 준비: `git_init` 저장소에 `stored_surface_state()`를 앞 테스트들처럼 채워 `initialize`한다. 호스트 관찰은 예산 `{"work-model": {"limit": 1, "used": 0, "execution_ids": []}}`과 `research_observed_at="2026-09-20T00:00:00Z"`다.
- 실행: `snapshot_report(root, identifier, snapshot=head, host_observation=...)`, `render_human_report(report)`. 이어서 알 수 없는 필드 `observed_at`만 담은 관찰로 `snapshot_report`를 부른다.
- 단언: 보고의 `snapshot`이 `head`다. `goal`이 `"Prove P"`이고 `assurance`가 제품 상수 `ASSURANCE`다. `research_observed_at`과 `budget`이 준 값과 같다. `pending_controls`는 `None`이다(단언 메시지: "관찰되지 않은 호스트 필드는 관찰되지 않은 채로 남는다"). 사람용 글에 `head`, `"inspection:"`, `"work-model 0/1"`이 들어 있다. 알 수 없는 필드는 `ValueError`를 정규식 `"unknown fields: observed_at"`로 던진다. 거부 사유는 필드 이름까지 고정된다.
- 대역: 없음. 실제 Git 저장소를 쓴다.

## 관계

- 정리와 보존 규칙 자체는 `test_retention`이 검사한다. 이 모듈의 `test_engine_cleanup_failure_reaches_snapshot_reporting`은 정리 실패가 `retention.pending_cleanup_failures`를 거쳐 보고에 닿는지만 본다.
- 상태 점검의 영역별 결과와 산출물 바이트 비교는 `test_state_checks`가 검사한다. 이 모듈의 두 보고 테스트는 `requested_areas=['record_storage']`로 그 점검을 보고 경로에서 부른다.
- Claude 스트림 해석 자체는 `test_claude_stream`이 검사한다. 이 모듈은 해석 결과가 저장과 타임라인을 거쳐 보존되는지만 본다.
- 과제 준비도의 계산 규칙은 준비도를 다루는 다른 모듈(예: `test_session_scheduler`, `test_planning`, `test_currentness`)이 맡는다. 이 모듈은 종료된 인스턴스에서 그 값을 싣지 않는 투영 규칙만 본다.
- 픽스처 의존: `record_fixtures.surface_state`, `stored_surface_state`, `approved_task`; `research_fixtures.git_init`, `bare_engine`, `dispatched_launch`.
- 이 모듈에만 있는 도우미는 `test_status_reports_artifact_presence_and_length_in_one_batch_without_bytes` 안의 지역 함수 `sizes`(배치 크기 조회 대역)뿐이다.
