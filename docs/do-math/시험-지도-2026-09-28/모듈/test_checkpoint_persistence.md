# test_checkpoint_persistence

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_checkpoint_persistence.py` (162행) |
| 클래스 / 테스트 | 3 / 5 |
| 시험 대상 제품 코드 | `do_math/observations.py`의 `preserve_checkpoint`, `ObservationTracker`; `do_math/observation_transport.py`의 `ObservationBatch`; `do_math/engine.py`의 `ResearchEngine`(`run`, `_register_execution`, `_observe_running`, `_recover_disappeared`, `_context`, `_save`); `do_math/repository.py`의 `canonical_json` |
| 사용하는 픽스처 모듈 | `purpose_fixtures`(`ActivatedPurposeHarness`, `CURRENTNESS_CONFIG`); `research_fixtures`(`dispatched_launch`, `local_job_runner`) |
| 격리 표지 | 없음 |
| 시작 상태 | `FinalCheckpointCaptureTests`와 `CheckpointPreservationTests`는 1단(`preserve_checkpoint`에 임시 작업공간). `CheckpointPersistenceTests`는 2단(`ActivatedPurposeHarness.make_active`가 `state_fixtures.active_instance`를 `CURRENTNESS_CONFIG`로 복원) |

## 목적

모듈 docstring은 "체크포인트와 그것이 이름 붙인 증거는 실행이 끝난 뒤에도 접근 가능하다"는 성질을 밝힌다. 작업자는 작업공간의 `checkpoint.json`에 현재 주장, 증거 경로, 시도, 남은 일, 다음 단계, 진행 상태를 쓴다. 제품은 관찰할 때마다 `preserve_checkpoint`로 그 파일과 `evidence_paths`가 가리키는 파일을 산출물로 떠 둔다. 이 모듈은 다음을 검사한다.

- 떠 둔 증거는 작업공간 파일이 나중에 바뀌어도 원래 바이트를 유지한다.
- 크기 예산을 넘는 증거는 지어내지 않고 생략 목록에 적는다.
- 마지막 체크포인트가 없어지거나 깨져도 마지막 유효 체크포인트를 보존하고 최종 관찰 상태를 기록한다.
- 끝난 실행을 검토하는 운영 검토는 원래 체크포인트 증거와 최종 출력 파일을 구별해 받는다.

## 모듈 수준 요소

- 행 12: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는다.
- 행 19–21 `CHECKPOINT`: 유효한 작업자 체크포인트 값. 주장 `'original evidence'`, 증거 경로 `['proof.txt']`, 시도 `['original checked']`, 남은 일 `['continue']`, 다음 단계 `'continue'`, 진행 상태 `'working'`이다. `FinalCheckpointCaptureTests`와 `CheckpointPersistenceTests`가 이 값이나 그 변형을 쓴다. `CheckpointPreservationTests`는 이 상수를 쓰지 않고 자체 값을 쓴다.
- 행 161–162: 직접 실행하면 `unittest.main()`.

## FinalCheckpointCaptureTests (행 24–68)

`unittest.TestCase`를 상속한다. 설정 훅과 도우미가 없다. 두 시험 모두 임시 디렉터리를 작업공간으로 삼아 `preserve_checkpoint`를 직접 부른다(1단).

### `test_final_capture_owns_exact_raw_and_input_evidence_independently_of_submission_outputs` (행 25–46)
- 성질: 체크포인트 포획은 체크포인트 원 바이트와 증거 파일의 그 시점 바이트를 자기 산출물로 소유하고, 체크포인트가 그대로이면 증거 파일이 바뀌어도 새로 포획하지 않으며, 체크포인트가 바뀌면 그 시점의 증거를 새로 뜬다.
- 준비: `input/source.txt`에 `b'fixed input'`. 증거 경로를 `['input/source.txt']`로 바꾼 `CHECKPOINT`의 정규 JSON을 `checkpoint.json`에 쓴다.
- 실행: `preserve_checkpoint(workspace, artifact_prefix='runtime/artifacts/BA-1/checkpoint', max_bytes=4096)`. 원천 파일을 `b'changed later'`로 바꾸고 `previous=first`, 접두 `BA-2`로 다시 부른다. 체크포인트 주장을 `'new claim'`으로 바꾸고 `previous=first`, 접두 `BA-3`로 부른다.
- 단언: 첫 포획의 산출물에서 `artifact_ref` 바이트가 원 체크포인트 바이트이고, 첫 증거 파일의 산출물이 `b'fixed input'`이다. 두 번째 호출은 첫 기록과 같은 기록을 돌려주고 새 산출물이 `{}`다. 세 번째 기록의 `sha256`은 첫 것과 다르고, 그 증거 파일 산출물이 `b'changed later'`다.
- 대역: 없음.
- 비고: 이름의 "제출 출력과 독립"이라는 부분에 대응하는 제출 출력은 이 시험에 없다. 단언은 포획이 원천 파일을 자기 산출물로 떠 두는 것만 본다. 제출 출력과의 구별은 `CheckpointPersistenceTests.test_ended_review_receives_the_original_checkpoint_evidence`가 본다.

### `test_capture_budget_omissions_and_invalid_final_do_not_invent_evidence` (행 48–68)
- 성질: 예산을 넘는 증거는 생략으로 기록되고, 체크포인트가 사라지면 앞 기록을 유지한 채 최종 상태 `missing`을 남기며, 체크포인트 자체가 예산을 넘으면 부분 관찰 상태로만 기록하고 산출물을 만들지 않는다.
- 준비: 100바이트 `proof.txt`와 `CHECKPOINT` 원 바이트.
- 실행: `max_bytes=len(raw)`로 포획. `checkpoint.json`을 지우고 `previous=first`, `max_bytes=4096`으로 포획. 체크포인트를 되살리고 `max_bytes=1`로 포획.
- 단언: 첫 포획의 `evidence_files`가 `[]`이고 `evidence_omitted[0].path`가 `proof.txt`이며, 산출물 바이트 합이 체크포인트 길이와 같다. 두 번째는 `artifact_ref`가 첫 것과 같고 `final_observation.checkpoint_status`가 `missing`이며 새 산출물이 `{}`다. 세 번째는 `kind`가 `observed_partial_state`이고 산출물이 `{}`다.
- 대역: 없음.

## CheckpointPersistenceTests (행 71–141)

`purpose_fixtures.ActivatedPurposeHarness`를 상속한다. 그 `setUp`이 `install_adapter_fixture`로 능력 관측을 `FixtureAdapter`로 바꾼다.

- `setUp` (행 72–74): 부모 `setUp` 뒤 `make_active(**CURRENTNESS_CONFIG)`를 부른다. `make_active`는 `restore_template(active_instance, config=CURRENTNESS_CONFIG)` 사본 위에 `PurposeRunner`와 형식 대역 `formal_fixture`를 단 엔진을 만든다. `CURRENTNESS_CONFIG`는 입력 한도 2,000,000바이트, 도구 검토 창 60초, 자기 점검 응답 창 5초, 학술 검색·운전자 끔이다. 결과는 `self.engine`이고 `self.root`는 사본의 루트다.

시작 상태는 2단이다.

### `test_ended_review_receives_the_original_checkpoint_evidence` (행 76–107)
- 성질: 실패로 끝난 실행을 검토하는 운영 검토는 체크포인트 당시의 증거 바이트를 체크포인트 증거로, 끝날 때의 작업공간 파일을 복구 자료로 따로 받는다.
- 준비: 클래스 절. 지역 러너 `Worker`의 `run`은 `local_job_runner`로 감싸 실제 로컬 Job 안에서 돈다. 그 안에서 `on_started`를 부르고, `proof.txt`에 `b'original evidence'`, `checkpoint.json`에 `CHECKPOINT`를 쓴다. 이어서 `on_observation`에 빈 `ObservationBatch`를 보내고, 소유자가 관찰을 적용해 `runtime['checkpoints']`에 그 실행이 나타날 때까지 폴링한다(10밀리초 간격, 상한 60초). 그 체크포인트 사본을 `captured`에 담은 뒤 `proof.txt`를 `b'changed after checkpoint'`로 바꾸고 `status='failed'`, `error='fixture interruption'`을 돌려준다.
- 실행: `engine.run(max_steps=1)`, 이어서 큐의 `operational_review` 행동으로 `engine._context(review, root/'review')`.
- 단언: 준비 실행의 최종 체크포인트 `sha256`과 `evidence_files`가 포획 당시 값과 같다. 문맥의 `operational_evidence.checkpoint_files`가 1개이고 그 로컬 파일 바이트가 `b'original evidence'`다. `recovery_materials.output_files` 가운데 `proof.txt` 행의 로컬 파일 바이트는 `b'changed after checkpoint'`다.
- 대역: 지역 `Worker` 러너(`PurposeRunner`를 대체).
- 비고: 주석은 관찰이 큐에 들어가고 소유자가 다음 차례에 적용한다고 적는다. 그래서 러너 스레드가 폴링으로 기다린다. 실제 외부 자원: `local_job_runner`가 띄우는 Windows Job 자식 프로세스.

### `test_restart_preserves_last_valid_checkpoint_and_records_invalid_final_observation` (행 109–141)
- 성질: 실행이 사라진 뒤의 복구는 깨진 마지막 체크포인트 대신 마지막 유효 체크포인트를 보존하고 최종 관찰을 `invalid`로 기록하며, 그 결과가 게시되어 운영 검토 문맥에서 `preserved`로 보인다.
- 준비: 클래스 절 위에서 행동 `AC-fixture`로 `running` 실행 `EX-fixture`를 등록한다. `dispatched_launch`로 `dispatched` 단계의 발사 표를 붙이고, Job 이름을 담은 용량 기록(`local_termination='unknown'`)을 넣는다(주석: 입장한 발사). 작업공간 `runs/EX-fixture/workspace`에 `proof.txt`와 `CHECKPOINT`를 쓰고, 상태를 `running`, 큐를 그 행동으로 두고 `_save()`한다. `deadline_only` 추적기로 빈 배치를 `_observe_running`에 넘겨 체크포인트를 기록시키고 그 사본을 `previous`로 둔다. 그런 다음 `checkpoint.json`을 `b'{interrupted write'`로 덮는다.
- 실행: `do_math.windows_job.named_job_empty`와 `owner_ended`를 참으로 패치하고, 작성자 잠금 안에서 `_recover_disappeared()`. 이어서 `store.load()`와 `_context({'role': 'operational_review', 'target': 'EX-fixture'}, root/'review')`.
- 단언: 최종 체크포인트의 `kind`가 `worker_checkpoint`이고, `artifact_ref`와 `evidence_files`가 `previous`와 같으며, `final_observation.checkpoint_status`가 `invalid`다. 저장소에서 다시 읽은 체크포인트가 메모리 값과 같다. 문맥의 `operational_evidence.checkpoint_status`가 `preserved`다.
- 대역: `named_job_empty`, `owner_ended` 패치(프로세스 종료 확인을 대신한다), `dispatched_launch`의 합성 발사 표.
- 비고: 실제 Git 게시(`_save`, `store.load`)를 쓴다. 이름의 "재시작"은 새 엔진을 여는 것이 아니다. 같은 엔진에서 `_recover_disappeared`를 부르고 저장소에서 다시 읽는 것으로 재현한다.

## CheckpointPreservationTests (행 144–158)

`unittest.TestCase`를 상속한다. 설정 훅과 도우미가 없다.

### `test_collected_checkpoint_keeps_exact_resume_reference` (행 145–158)
- 성질: 수집된 체크포인트는 원 바이트를 그대로 산출물로 두고, 그 해시를 기록한다.
- 준비: 1단. `counters: {}`를 포함한 자체 체크포인트 값을 `json.dumps`로 인코딩한 바이트(정규 JSON이 아님)를 `checkpoint.json`에 쓴다.
- 실행: `preserve_checkpoint(workspace, artifact_prefix='runtime/artifacts/BA/checkpoint', max_bytes=4096)`.
- 단언: `kind`가 `worker_checkpoint`이고, `artifact_ref`의 산출물이 쓴 원 바이트와 같으며, `sha256`이 그 바이트의 SHA-256이다.
- 대역: 없음.
- 비고: 원 바이트가 정규 JSON이 아니어도 다시 직렬화하지 않고 그대로 보존됨을 본다. 이 점은 원문이 명시하지 않고, `json.dumps`를 쓴 준비와 바이트 동일성 단언에서 읽은 것이다.

## 관계

- **다른 층의 같은 기능.** `preserve_checkpoint`는 `test_observations`와 `test_family_records`도 부른다. 실시간 관찰에서 체크포인트를 포획하는 소유자 경로(`_observe_running`)는 `test_live_observation.ObservationCollectionTests.test_checkpoint_capture_preserves_its_evidence_before_live_file_changes`가 메모리 엔진(`routing_engine`)으로 검사한다. 이 모듈의 `CheckpointPersistenceTests`는 그 경로를 실제 Git 게시와 운영 검토 문맥까지 잇는다.
- **픽스처 의존.** `purpose_fixtures.ActivatedPurposeHarness`(2단 템플릿과 `FixtureAdapter`), `CURRENTNESS_CONFIG`, `research_fixtures.local_job_runner`(실제 로컬 Job 수명), `dispatched_launch`(발사 표).
- **이 모듈에만 있는 도우미.** 모듈 상수 `CHECKPOINT`와 지역 러너 `Worker`.
- **겹치거나 보완하는 시험.** `test_final_capture_owns_exact_raw_and_input_evidence_independently_of_submission_outputs`와 `test_ended_review_receives_the_original_checkpoint_evidence`는 같은 성질("포획 뒤 파일이 바뀌어도 포획한 바이트가 남는다")을 순수 함수 층과 엔진·검토 문맥 층에서 본다. 최종 체크포인트가 없는 경우(`missing`)는 1단에서, 깨진 경우(`invalid`)는 2단 복구 경로에서 본다.
