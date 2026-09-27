# 결과 — IO 그룹 병합

- worktree: `C:/math-worktrees/c-int`, 브랜치 `c-int`
- 병합 커밋: `d32271ab71e33e5b9ee05528db1cbf85fc60d165`
  - 부모: `7b66a07`(c-int, 통합자의 `_reviewed_candidate` 수리 뒤)와 `e3c5ac1`(c-io)
  - 공통 기준점: `d380cd3`(REV 병합)
- 메시지: "IO 그룹 병합". 트레일러는 없다(4절 끝 참고).
- push와 다른 브랜치 조작은 하지 않았다.

아래 경로는 따로 적지 않으면 `.claude/skills/do-math/scripts/` 기준이다.

HEAD 쪽 변경은 기준점 이후의 RUN 병합(`640e9e3`), RES 병합(`c22cb98`), 통합자의 시험 수리(`7b66a07`)를 모두 담는다. 두 쪽이 모두 바꾼 파일은 10개다.
- 제품: `cli.py`, `engine.py`, `model_runner.py`, `scheduled_operator.py`
- 시험: `research_fixtures.py`, `test_redesign_ACTIVITIES.py`, `test_redesign_ENGINE.py`, `test_redesign_EVIDENCE_walkthroughs.py`, `test_redesign_PROFILES.py`
- 문서: `이음새-정본.md`

텍스트 충돌은 `engine.py` 한 곳뿐이었다.

## 1. 충돌마다 두 쪽의 의도와 푼 방법

### 1.1 `do_math/engine.py` `_observe_running`의 자기 점검 발급 끝부분

- **HEAD 쪽 의도(RUN-01).** 자기 점검 요청을 발급한 뒤의 게시를 `self._save()`에서 `self._publish_observation()`으로 바꿨다. 관찰 게시가 게시 head를 옮겨도 소유 루프의 재판정을 일으키지 않게 하려는 것이다. RUN은 기준점의 `batch is not None` 조건은 그대로 두었다.
- **IO 쪽 의도(HIS-13).** `_observe_running`이 `ObservationBatch`만 받으므로 `batch is not None` 분기를 모두 지웠다. 게시 호출은 기준점의 `self._save()`를 문맥으로 남겼다.
- **해소.** IO의 무조건 구조에 HEAD의 게시 함수를 쓴다.

```python
            tracker.record_delivery(obligation['id'], source_offset=batch.stream_size())
            self.runtime['self_check_obligations'][obligation['id']] = deepcopy(tracker.obligations[obligation['id']])
        if self_checks:
            self._publish_observation()
```

- **자동 병합 구간 확인.** 같은 함수의 앞부분도 자동 병합되었다. 그 구간에서 두 가지를 확인했다.
  - 옛 분기(`batch is None`, `isinstance(event, ObservationBatch)`, `self_check_request(obligation)`)가 남지 않았다.
  - HEAD의 HIS-20 되돌림(`original_runtime = None if self._unchanged() else deepcopy(self.runtime)`)과 본문의 `self._publish_observation(artifacts or None)`이 살아 있다.

## 2. 충돌 표지 밖에서 발견해 고친 것

### 2.1 `tests/test_redesign_ENGINE.py` — RUN이 더한 시험의 dict 사건

- RUN은 HIS-20의 재현 시험 `ObservationTransactions.test_failed_observation_rolls_back_to_the_published_state_without_copying_it_first`를 새로 쓰면서 `engine._observe_running("EX-one", tracker, {"type": "tick"})`를 썼다.
- IO는 기준점에 있던 같은 모듈의 dict 호출 네 곳을 모두 `observation_batch`로 옮겼지만, 기준점 뒤에 생긴 이 시험은 알 수 없었다.
- HIS-13 뒤에 이 호출은 `batch.events`에서 `AttributeError`가 된다. 텍스트 충돌 없이 깨진 의미적 충돌이다.
- 이웃 시험들이 IO 뒤에 쓰는 형태로 고쳤다: `observation_batch(received_monotonic=tracker.clock(), stream_path=Path(temporary) / "stdout.jsonl")`. 빈 묶음은 옛 `tick`에 해당한다(결과-IO HIS-13 행).
- 시험이 보는 성질("게시가 실패하면 런타임을 먼저 복사하지 않고 게시 상태로 되돌린다")은 그대로다. 빈 묶음도 첫 틱에서 `observation_stream`을 새로 만들어 게시 경로를 지나고, 거기서 가짜 `_save`가 실패한다.
- 대상 시험에서 통과했다.

### 2.2 대조했으나 고칠 것이 없던 것

- **두 쪽이 모두 바꾼 파일 10개.** 파일마다 "병합 결과와 HEAD의 차이"를 "IO가 기준점에서 바꾼 것"과 줄 단위로 대조했다. 10개 모두 정확히 같다. `engine.py`는 IO가 문맥으로만 둔 `self._save()` 자리가 HEAD의 `self._publish_observation()`으로 남아 있어 대조와 맞는다.
- **IO가 지운 이름.** 제품·시험·`probe_cli.py`에서 grep했다. 대상은 `CodexModelRunner`, `ClaudeModelRunner`, `CodexExecution`, `describe_timeout=` 인자, `bytes_received`, `rejected_rule_reasons`, `allowed_subjects`, `last_checkpoint`, `.responses`, 러너의 `.codex`·`.claude`, `ControlTransport.receipt`·`records`, `codex_worker`에서 `cli_worker`로 옮긴 여덟 이름이다. 남은 참조는 0건이다.
  - `codex_adapter.py:135`의 `describe_timeout = 10.0`은 IO가 남긴 클래스 속성이다.
  - `observations.self_check_request`는 IO가 엔진의 import에서만 지웠고 모듈 안에서는 계속 쓰는 함수다.
  - `transport_bytes_received`는 사건 종류 이름으로, 지운 필드와 이름만 겹친다.
- **`observe`의 필수 `source`(IO-13).** AST로 제품·시험·`probe_cli.py`의 모든 속성 호출 `X.observe(...)`를 찾았다. `source` 키워드가 없는 호출은 0건이다. 시험 도우미 `research_fixtures.observe(tracker, event)`는 맨 이름 호출이라 대상이 아니다.
- **`_observe_running`의 dict 인자.** 제품·시험의 호출 14곳 가운데 dict를 넘기던 것은 2.1의 한 곳뿐이었다. `engine.py:3271`은 러너의 `on_observation`이 주는 묶음을 넘긴다.
- **옛 경로의 `patch`.** 시험에서 `do_math.codex_worker.*`, `do_math.claude_worker.*`, `do_math.model_runner.*`를 가리키는 `patch`는 `test_research_reliability.py:254`의 `do_math.model_runner.time.sleep` 하나다. `model_runner.py:10`이 `time`을 import하므로 유효하다. 옛 러너 생성(`ModelRunner(codex=...)`, `.codex.run(`)은 0건이다.
- **정적 해석.** 제품 모듈 84개(새 `cli_worker` 포함)를 import하고 AST로 확인했다.
  - 모든 상대 import와 `모듈.속성` 참조가 해석된다.
  - 엔진 믹스인의 `self` 호출이 모두 `ResearchEngine`의 속성이다. `self.lifecycle_monotonic(`만 예외이며, 이것은 `engine.py:447`이 초기화하는 인스턴스 속성이다.
  - `ResearchEngine`의 MRO에서 같은 메서드가 두 번 정의된 경우는 0건이다.

## 3. 실행한 확인과 결과

| 확인 | 대상 | 결과 |
|---|---|---|
| 구문 컴파일 | `do_math/**/*.py`, `operator_bootstrap.py`, `probe_cli.py`, `tests/*.py`(223개 파일) | 통과. 내장 `compile()`을 써서 바이트코드를 남기지 않았다 |
| 제품 import | `do_math` 모듈 84개 | 통과 |
| 시험 import | `tests/test_*.py` 135개 | 135개 모두 통과, 실패 0 |
| 정적 해석·옛 이름·필수 인자 | 2.2의 항목 | 남은 참조 0, 중복 정의 0, `source` 없는 `observe` 0 |
| 대상 시험(프로세스 1개, 백그라운드) | IO가 고친 시험 모듈 22개 | 통과 347, 오류 2, 실패 0(140초). 오류 2건은 병합과 무관하다(아래) |

대상 시험은 `.claude/skills/do-math`에서 실행했고, `DO_MATH_KNOWLEDGE_TEST_LEAN`에 계약 6절의 경로를 주었다.

```
python -B scripts/run_tests.py --output C:/Users/wogud/AppData/Local/Temp/merge-io-check-1 \
  test_background_processes test_checkpoint_persistence test_claude_adapter test_cli test_codex_adapter \
  test_control_preview test_control_transport_io test_currentness_recovery test_execution_observation_profile \
  test_host_resources test_model_runner test_native_final_submission test_observation_audit1 test_observations \
  test_provider_final_contract test_redesign_ACTIVITIES test_redesign_ENGINE test_redesign_EVIDENCE_walkthroughs \
  test_redesign_OBSERVATION test_redesign_PROFILES test_research_reliability test_worker_temporary_outputs
```

- 통합자가 지정한 다섯 모듈(`test_codex_adapter`, `test_model_runner`, `test_control_transport_io`, `test_observations`, `test_redesign_OBSERVATION`)은 모두 이 22개에 들어 있다.
- 2.1에서 고친 시험은 보고서에서 통과로 확인했다.
- 보고서: `C:/Users/wogud/AppData/Local/Temp/merge-io-check-1/report.json`

### 오류 1: `test_control_transport_io.ControlTransportIoTests.test_request_id_rejected_without_engine_record_stays_taken_in_every_transport`

IO가 IO-02용으로 새로 쓴 시험이다. 이 오류는 순서에 따라 결과가 갈리는 불안정한 시험 때문이며, 병합과 무관하다.

- **병합과 무관한 근거.** 병합 결과의 `do_math/control_transport.py`는 c-io와 바이트 단위로 같다(`git diff c-io`가 비어 있다). 시험도 IO가 쓴 그대로다.
- **원인.**
  - 전송 ID는 `token_urlsafe(18)`, 곧 완전한 난수다(`control_transport.py:165`).
  - `pump`는 전송 ID를 정렬한 순서로 inbox를 처리하고(`:264`), `_receipt`는 `os.scandir` 순서로 모든 outbox에서 처음 찾은 영수증을 돌려준다(`:489-498`).
  - 둘째 전송의 ID가 첫 전송보다 앞서면 다음 순서로 실패한다. 둘째 전송의 재사용 요청이 먼저 거부되어 그 outbox에 거부 영수증이 생긴다. 이어 첫 전송의 정당한 재전달을 처리할 때 `_receipt`가 둘째 전송의 영수증을 먼저 찾아 "내용이 다르다"고 판정한다. 첫 전송의 outbox에 거부 영수증을 쓰려다 이미 있는 엔진 영수증과 부딪혀, `_reject_delivery_file`이 `ValueError("request_id was already received with different content")`를 `pump` 밖으로 던진다.
- **재현.** 전송 ID를 두 방향으로 강제한 스크립트로 확인했다. 스크립트는 저장소 밖 `C:/Users/wogud/AppData/Local/Temp/merge-io-repro/order.py`에 있고, 병합 결과의 제품 코드를 쓴다.
  - 첫 전송 ID가 앞설 때: `ok: rejected/delivery_validation`
  - 둘째 전송 ID가 앞설 때: 시험과 같은 `ValueError`
  - 따라서 이 시험은 실행마다 대략 절반의 확률로 실패한다. IO의 인계 확인(`io-r3`)은 운 좋게 통과했다.
- **제품 결함이다.** 시험만의 문제가 아니다. 다른 전송이 같은 요청 ID를 재사용해 거부된 뒤에는, 원래 전송의 정당한 재전달이 `pump`에서 예외를 낸다. `_receipt`가 요청을 보낸 전송 자신의 outbox를 먼저 보지 않기 때문이다.
  - IO-02는 조회 방식만 glob에서 존재 검사로 바꿨다. 이 "처음 찾은 것" 규칙은 그 전에도 있었을 것으로 보이나 확인하지 않았다.
  - 수리 방향은 IO-02 설계의 영역이라 고치지 않았다. 예를 들면 `receive`가 요청의 전송 자신의 outbox를 먼저 조회하는 것이다(4절).

### 오류 2: `test_observations.Tests.test_engine_answers_reminder_without_opening_model_review`

병합 전 HEAD부터 있던 결함이다.

- **오류.** 가짜 엔진이 `types.SimpleNamespace`인데 `_unchanged`가 없어 `AttributeError`가 난다(`engine.py:2671`).
- **병합 전부터 있던 결함이라는 근거.**
  - HEAD(`7b66a07`)의 이 시험(388행)은 dict `{"type": "tick"}`를 넘기면서 `tracker.observe`를 가로채 늘 관찰 한 건을 돌려주게 한다. 그래서 관찰이 비지 않아 이른 반환을 지나고, RUN의 HIS-20이 더한 `self._unchanged()` 호출에 닿는다.
  - 가짜 엔진에는 그 메서드가 없고, 그 뒤 RUN-01의 `self._publish_observation(...)`도 없다.
  - IO의 변경(dict를 `observation_batch`로)은 이 경로를 바꾸지 않았다.
  - RUN은 이 가짜 엔진을 고치지 않았고, 인계 확인에서 `test_observations`를 돌리지 않았다. 앞 RUN 병합의 대상 시험에도 이 모듈은 없었다.
- 병합 범위 밖이라 고치지 않았다(4절).

## 4. 남은 위험

- **오류 2의 수리(병합 전 결함, RUN × `test_observations`).** `test_observations.py`의 이 시험의 `SimpleNamespace(...)`에 `_unchanged=lambda: False, _publish_observation=lambda artifacts=None: None`을 더한다.
  - `_unchanged`가 거짓이면 제품은 되돌림용 사본을 만들어 기존 흐름대로 진행한다.
  - `_publish_observation`은 RUN-01에서 `_save`를 대신하는 관찰 게시다. 가짜 엔진의 `_save`와 같은 무동작이면 된다.
  - 고친 뒤 이 시험 ID만 다시 돌리면 된다.
- **오류 1의 결함(IO-02 제품·시험, 순서 의존).**
  - 제품: `ControlTransport._receipt`가 요청을 보낸 전송 자신의 outbox를 먼저 보지 않는다. 그래서 다른 전송이 재사용으로 거부된 뒤 원래 전송의 재전달이 `pump`에서 `ValueError`를 낸다.
  - 시험: 전송 ID가 무작위라 대략 절반의 확률로 실패한다.
  - 수리안의 예: `receive`가 영수증을 찾을 때 요청의 `transport_id` outbox를 먼저 보고, 없을 때만 전역으로 훑는다. 그러면 전역 유일성(다른 전송의 재사용 거부)은 유지되고 순서 의존이 사라진다. 이 수리는 IO-02의 설계 판단이므로 IO 담당이나 통합자가 정해야 한다.
  - 시험은 `order.py`처럼 두 순서를 모두 강제하면 결정적이 된다.
- **통합 확인 전이다.** 돌린 모듈 밖의 상호작용은 통합 확인에서 드러난다. 특히 RUN-01의 `_publish_observation`, HIS-20의 되돌림, IO의 묶음 전용 관찰 경로가 만나는 소유 루프 전 구간 시험(`test_purpose_engine` 등)과, `ModelRunner` 통합의 소비자(`test_probe_cli`, `test_submission_tools`, `test_machine_parallel`)는 이번에 돌리지 않았다.
- **문서.** 결과-IO 4절의 문서 변경(`references/공통-실행.md` 165행, `references/초기화-운전.md` 215행)은 이 병합의 범위가 아니어서 반영하지 않았다.
- **앞 두 병합 커밋의 트레일러.** `C:/math/.claude/skills/commit-harness/SKILL.md:27`은 커밋 메시지에 "`Co-Authored-By` 등 트레일러는 붙이지 않는다"고 정한다. 프로젝트 CLAUDE.md가 커밋 절차의 정본으로 지정한 사용자 수준 지침이다.
  - 앞선 RUN 병합(`640e9e3`)과 RES 병합(`c22cb98`)에서 나는 이 규칙을 확인하지 않고 세션 시스템 지시만 근거로 트레일러를 붙였다. 잘못된 판단이었다.
  - 이번 커밋에는 붙이지 않았다.
  - 두 커밋의 메시지는 고치지 않았다. 공유 통합 브랜치의 이력을 다시 쓰는 일은 이 파견의 범위 밖이므로 통합자의 판단에 맡긴다.
