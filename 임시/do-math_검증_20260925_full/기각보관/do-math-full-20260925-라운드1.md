---
유형: 기각보관
출처: do-math-full-20260925
라운드: 1
항목: 4
---

# 기각 보관 — do-math-full-20260925 라운드1

## R1-27

### 원문
제목: 중앙 관측이 자기 점검과 무관한 제어 호출까지 응답 의무에서 면제한다

### 위치
`.claude/skills/do-math/scripts/do_math/engine.py` 2923~2934행. 제어 서버·도구 이름만 보고 `control_submit`과 `control_receipt`를 자기 점검 호출로 등록한다. 정밀한 인자·의무 대조는 `observations.py` 649~692행에 이미 있다.

### 기준
`임시/do-math_검증_20260925_full/동결.md` 267행:

```
- 연구 책임자의 목표·필수조건·허가와 AI 역할의 판단 권한을 보존한다. 검증된 지식·부분 결과·실패·근거와 실행 이력을 왜곡하지 않는다.
```

`.claude/skills/do-math/GLOSSARY.md` 「실질 행동」:

```
모델 요청의 외부 전송, 프로그램 실행, 연구 파일 쓰기, 허용 도구 호출과 외부 행동 요청처럼 실제 효과를 만들 수 있는 행위다. 계획, 대기열 등록과 문서상의 제안만으로 실질 행동이 시작된 것은 아니다.
```

`.claude/skills/do-math/SKILL.md` 「변경될 전제와 이미 유효한 판단을 구별한다」:

```
각 역할의 구체적인 선언·처분·질문·복구 형식은 「공통 실행」과 실행별 스키마를 따른다.
```

위 인용은 해당 문단의 마지막 문장이다. 「공통 실행」 126행은 정확한 자기 점검 조회 완료 뒤의 명령 위치를 응답 전 행동의 판단 근거로 정한다.

### 영향
실제 의무를 전달하고 정확한 payload를 반환한 poll 완료를 관측한 뒤, 다음 바이트 구간에 `control_submit(kind=submission_preview)` 시작 사건을 넣어 실제 `_observe_running`을 호출했다. 파일 쓰기·중앙 저장은 대역으로 처리했다. 결과는 `acknowledged_call_id=POLL`, `PREVIEW in self_check_call_ids=True`, `missed_reason=None`이었다. 자기 점검을 아직 답하지 않았는데 새 후보 적용 preview가 응답 행동으로 잘못 분류된다.

정밀 판별기의 `control_submit` 분기는 `kind=self_check_response`만 다룬다(`observations.py` 670~675행). 그러나 중앙의 선등록 때문에 `_start_call` 623행과 `_complete_call` 646행의 일반 행동 집계에서 제외된다. 같은 집합은 `engine.py` 2935~2939행의 자기 점검 전용 체크포인트 판별에도 사용된다. 기존 `test_observation_audit1.py` 71~78행은 관측기를 직접 호출해 다른 제어 제출을 일반 행동으로 판정하지만 중앙의 선등록을 거치지 않는다. `graphify affected/path` 뒤 중앙과 관측기 원문을 함께 추적했다. 넓은 선등록을 제거하고 기존 인자·의무 식별을 사용한다. 전달 전 사건·인지 미확인 사건·종료 뒤 재생의 경계는 기존 관측기가 유지한다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/engine.py 2923~2934행
원래:
```
        # These are provider-observed MCP identities, not IDs claimed in a draft.
        calls = []
        for event in events:
            item = event.get("item", {})
            if (event.get("type") in {"item.started", "item.completed"} and item.get("type") == "mcp_tool_call"
                    and item.get("server") == "execution_control" and item.get("tool") in {"control_self_check", "control_submit", "control_receipt"}):
                calls.append(item)
            if event.get("type") == "assistant":
                calls.extend(block for block in event.get("message", {}).get("content", [])
                    if isinstance(block, dict) and block.get("type") == "tool_use"
                    and block.get("name") in {"mcp__execution_control__control_self_check", "mcp__execution_control__control_submit", "mcp__execution_control__control_receipt"})
        candidate.register_self_check_calls([call["id"] for call in calls if isinstance(call.get("id"), str)])
```
대체:
```

```

### 조각 2 — .claude/skills/do-math/scripts/tests/test_research_reliability.py 186~186행
원래:
```
    def test_one_native_chunk_is_one_owner_transaction(self):
```
대체:
```
    def test_owner_does_not_exempt_preview_as_a_self_check_response(self):
        from unittest.mock import Mock
        from test_redesign_ENGINE import routing_engine
        from test_redesign_OBSERVATION import rule, ObservationRedesignTests
        from do_math.observations import self_check_feedback
        for preview in (False, True):
            with self.subTest(preview=preview), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                tracker = ObservationTracker('EX-one', root, {'observation_rules': [rule()],
                    'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5}, clock=Clock())
                obligation = next(row for row in tracker.observe({'type': 'tick', 'counters': {'attempts': 2}})
                                  if row['kind'] == 'self_check_due')
                tracker.record_delivery(obligation['id'], source_offset=0)
                envelope = {'self_check_id': obligation['id'], 'execution_id': 'EX-one',
                            'payload': self_check_feedback(tracker.obligations[obligation['id']])}
                source = {'stream': 'stdout.jsonl', 'start_offset': 0, 'end_offset': 100,
                          'received_at': '2026-09-25T00:00:00Z', 'received_monotonic': 0}
                tracker.observe({'type': 'item.completed', 'item': {'id': 'POLL', 'type': 'mcp_tool_call',
                    'server': 'execution_control', 'tool': 'control_self_check',
                    'arguments': {'self_check_id': obligation['id']}, 'result': envelope}},
                    source=source, evaluate=False)
                arguments = ({'request_id': 'PREVIEW', 'kind': 'submission_preview', 'payload': {}} if preview else
                    {'self_check_id': obligation['id'], 'response': ObservationRedesignTests.response(obligation)})
                event = {'type': 'item.started', 'item': {'id': 'NEXT', 'type': 'mcp_tool_call',
                    'server': 'execution_control', 'tool': 'control_submit' if preview else 'control_self_check',
                    'arguments': arguments}}
                engine = routing_engine()
                engine._controls = Mock(); engine._check_conversations = Mock(return_value=False)
                engine._save = Mock(); engine._enqueue = Mock(); engine._inline_reviewing = False
                engine.runtime['executions']['EX-one'] = {'id': 'EX-one', 'status': 'running',
                    'role': 'research_work', 'action': {'role': 'research_work'}}
                batch = ObservationBatch([event], [(100, 200)], '2026-09-25T00:00:01Z',
                    1, 100, 200, root / 'stdout.jsonl', lambda: False)
                with patch.object(ObservationBatch, 'caught_up', return_value=False):
                    engine._observe_running('EX-one', tracker, batch)
                missed = tracker.obligations[obligation['id']].get('missed_reason')
                self.assertEqual(missed, 'research_action_before_response' if preview else None)
                self.assertEqual(engine._enqueue.called, preview)

    def test_one_native_chunk_is_one_owner_transaction(self):
```


### 판정
확정: 기각 · 승인기 [2, 3] · 기각기 [1] · 처분: 없음
최종 판정: 기각

### 근거
- 기 1: 관문 4의 개선이 성립하지 않는다. 원래 선등록은 정상 safety_boundary 제출 호출도 제외하므로, 그 호출의 native 시작이 중앙 요청보다 먼저 관측돼도 경계를 접수할 수 있다. 조각 1로 선등록만 지우면 그 호출 자체가 pending_research에 남는다. 실제 연구 도구가 모두 끝난 뒤 inflight_calls=false·call_ids=[]를 제출해도 중앙은 자기 경계 제출 호출을 미신고 연구 호출로 보고 거절한다. 대체는 preview의 과도한 면제를 없애지만 정상 안전 경계 접수에 새로운 도착 순서 의존성을 만든다. 추가 시험은 preview와 자기 점검 응답만 비교하여 이 경계를 다루지 않는다.

## R1-M1

### 원문
구성: R1-02 · R1-03 · R1-22 · R1-23

### 위치
`.claude/skills/do-math/scripts/do_math/cli.py` 264~268행, 294행, 328행과 `.claude/skills/do-math/scripts/tests/test_operator.py` 행 224 뒤 및 225~228행. 저장 또는 적용 뒤 예약 재조정이 실패했을 때의 실패 봉투, 재조정 명령, 그 경계의 시험이다.

### 기준
`.claude/skills/do-math/README.md` 「인스턴스 생성」 141행:

```
독립 운영을 등록했으면 응답의 `result.operator_schedule`에서 실제 두 작업을 확인한다. 저장은 성공했지만 예약 등록이 실패하면 생성된 인스턴스 ID·snapshot과 실패·재조정 명령을 반환한다. 같은 연구를 다시 `init`하지 말고 해당 인스턴스의 설치 문제를 해결한다.
```

`.claude/skills/do-math/README.md` 「오류와 반환 코드」 492행:

```
| `5` | Git 저장·저장소 작업, OS 또는 subprocess 도구 오류이면 응답 `kind`는 `tool_error`다. `run`이 다른 실행기가 보유한 writer lock을 얻지 못한 경우도 여기에 속하며, 이때는 그 실행기가 끝난 뒤 다시 실행한다. 제어 명령의 lock 경합은 오류가 아니라 exit 0과 `lock="busy"`로 반환한다. 구현이 요청을 처리하지 못한 내부 계약 오류이면 `kind`는 `contract_error`이고 `next_owner`는 `maintenance`다. `init`·`configure`가 상태를 저장했으나 예약 등록에 실패한 경우에도 exit 5이며, 이때는 `result.operator_schedule`에 `status="failed"`와 그대로 실행할 재조정 명령이 들어 있다 |
```

`.claude/skills/do-math/README.md` 「독립 운영의 설정과 정지」 456행:

```
`operator status`는 실제 예약 작업을 조회한다. `operator install`은 현재 인스턴스 설정으로 정상 감독·연구 엔진 작업을 다시 맞추고 `operator uninstall`은 그 인스턴스의 연구·정기 감독·일회성 wake 예약을 제거한다.
```

### 영향
예약 도구의 OS·subprocess 시작 오류가 저장 또는 적용 뒤 `init`·`configure`의 실패 봉투를 벗어나면, 이미 생긴 인스턴스·snapshot 또는 적용 영수증과 `operator_schedule`이 일반 오류 응답에서 사라진다. 또한 반환한 `operator install`은 공개 Python 진입점이 아니어서 그대로 실행할 수 없고, 비활성화 뒤 제거 실패에도 설치를 지시해 승인된 설정과 반대가 된다. 오류 범위를 보존하고 현 Python·설치본·인스턴스를 PowerShell 인용으로 넣은 install 또는 uninstall 명령을 반환하면, 사용자는 재초기화나 경로 추측 없이 해당 설치를 재조정할 수 있다.

### 근거
R1-02와 R1-22는 같은 두 재조정 호출에서 `RuntimeError` 밖의 `OSError`·`subprocess.SubprocessError`가 저장된 결과를 잃게 한다는 지적과 대역 시험을 제시한다. R1-03과 R1-23은 같은 `_schedule_failure` 구간에서 실행파일 없는 install 문자열을 반환한다는 지적을 합쳤고, R1-03의 비활성화 방향과 PowerShell 작은따옴표 인용을 취했다. R1-22의 `Exception` 형식 확장은 두 호출부가 포착하는 구체 오류 범위를 바꾸지 않고 그 실패 봉투의 입력 형식을 맞추므로 취했다. 구성 항목 사이의 조각 교차는 정규화된 다섯 키로 녹였으며, 서로 어긋나는 근거나 대체 문면은 없었다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/cli.py 264~268행
원래:
```
def _schedule_failure(result: dict[str, Any], error: RuntimeError, repository: Path,
                      instance: str) -> tuple[dict[str, Any], int]:
    reconcile = subprocess.list2cmdline(["operator", "install", "--repository", str(repository), "--instance", instance])
    result["operator_schedule"] = {"status": "failed", "error": str(error), "reconcile": reconcile}
    return result, 5
```
대체:
```
def _schedule_failure(result: dict[str, Any], error: Exception, repository: Path,
                      instance: str) -> tuple[dict[str, Any], int]:
    mode = "install" if result.get("config", {}).get("operator_enabled", True) else "uninstall"
    def quote(value):
        return "'" + str(value).replace("'", "''") + "'"
    entrypoint = Path(__file__).resolve().parents[1] / "do_math.py"
    reconcile = ("& " + quote(sys.executable) + " " + quote(entrypoint)
                 + " operator " + mode + " --repository " + quote(repository.resolve())
                 + " --instance " + quote(instance))
    result["operator_schedule"] = {"status": "failed", "error": str(error), "reconcile": reconcile}
    return result, 5
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/cli.py 294~294행
원래:
```
            except RuntimeError as error:
```
대체:
```
            except (RuntimeError, OSError, subprocess.SubprocessError) as error:
```

### 조각 3 — .claude/skills/do-math/scripts/do_math/cli.py 328~328행
원래:
```
            except RuntimeError as error:
```
대체:
```
            except (RuntimeError, OSError, subprocess.SubprocessError) as error:
```

### 조각 4 — .claude/skills/do-math/scripts/tests/test_operator.py 행 224 뒤
대체:
```
    def test_saved_results_survive_schedule_process_start_errors(self):
        configuration = {'operator_enabled': True}
        for command in ('init', 'configure'):
            for error in (OSError('scheduler executable unavailable'),
                          subprocess.SubprocessError('scheduler process failed')):
                with self.subTest(command=command, error=type(error).__name__):
                    argv = [command, '--repository', str(self.repository)]
                    if command == 'init':
                        argv += ['--workspace', str(self.workspace), '--goal', 'Keep the saved instance']
                        saved = {'instance_id': self.instance, 'snapshot': 'saved-head',
                                 'status': 'initializing'}
                    else:
                        argv += ['--instance', self.instance, '--config-file', 'unused.json']
                        saved = {'effect': 'applied', 'request_id': 'UC-saved',
                                 'snapshot': 'saved-head', 'config': configuration}
                    args = cli.build_parser().parse_args(argv)
                    with patch.object(cli, '_require_git'), \
                         patch.object(cli, 'initialize', return_value=dict(saved)), \
                         patch.object(cli, '_control', return_value=dict(saved)), \
                         patch.object(cli, '_json_file', return_value=configuration), \
                         patch.object(cli, 'ResearchRepository') as repository, \
                         patch.object(cli, '_reconcile_operator', side_effect=error):
                        repository.return_value.load.return_value = ('saved-head', {'config': configuration}, {})
                        result, code = cli.execute(args)
                    self.assertEqual(code, 5)
                    self.assertEqual({key: result[key] for key in saved}, saved)
                    self.assertEqual(result['operator_schedule']['status'], 'failed')
                    self.assertEqual(result['operator_schedule']['error'], str(error))

```

### 조각 5 — .claude/skills/do-math/scripts/tests/test_operator.py 225~228행
원래:
```
    def _config(self, value: dict) -> Path:
        path = self.root / "config.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path
```
대체:
```
    def test_schedule_reconcile_preserves_entrypoint_paths_and_disable_direction(self):
        repository = self.root / "research owner's repository"
        for enabled in (True, False):
            with self.subTest(enabled=enabled):
                result, code = cli._schedule_failure(
                    {'config': {'operator_enabled': enabled}}, RuntimeError('failed'),
                    repository, self.instance)
                command = result['operator_schedule']['reconcile']
                quote = lambda value: "'" + str(value).replace("'", "''") + "'"
                self.assertTrue(command.startswith('& ' + quote(sys.executable) + ' '))
                self.assertIn(quote(Path(cli.__file__).resolve().parents[1] / 'do_math.py'), command)
                self.assertIn(' operator ' + ('install' if enabled else 'uninstall') + ' ', command)
                self.assertIn('--repository ' + quote(repository.resolve()), command)
                self.assertTrue(command.endswith('--instance ' + quote(self.instance)))
                self.assertEqual(code, 5)

    def _config(self, value: dict) -> Path:
        path = self.root / "config.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path
```


### 판정
확정: 기각 · 승인기 [2, 3] · 기각기 [1] · 처분: 없음
최종 판정: 기각

### 근거
- 기 1: 관문 6의 조각 규약에 어긋난다. 조각 4는 기존 클래스 본문을 이어야 성립하는 의존 삽입인데 틈 좌표만 주고 이웃 행을 구간에 포함하지 않았다. 계약/조각.md 5절은 이런 삽입을 이웃 행과 새 내용을 포함한 구간으로 쓰도록 요구한다. 오류 포착 범위와 재조정 명령의 개선은 인정되지만, 항목의 조각 전건이 규약을 충족하지 않는다.

## R1-M5

### 원문
구성: R1-10 · R1-30

### 위치
`.claude/skills/do-math/scripts/do_math/repair_execution.py` 1~26행·217~481행, `operational_dispositions.py` 10행·48~49행·96~102행·109~200행, `engine.py` 747행·4346행·4385~4399행·4479~4480행, `submission.py` 688~689행과 그 전용 시험·계약 문면이다.

### 기준
`.claude/skills/do-math/AGENTS.md` 「개발 원칙」:

```
- 설계를 바꾸면 구현·호출부·스키마·테스트·예시·문서를 같은 변경에서 새 계약으로 교체한다. 구판 호환을 위한 이전 구현·이름 별칭·래퍼·구형 인자·무시되는 설정·버전별 분기·마이그레이션 경로를 남기지 않는다.
- 과거 실험 인스턴스·저장 기록·산출물은 호환성 요구가 아니다. 새 계약으로 다시 초기화해 검증한다. 예전 자료를 읽기 위한 기본값 보충이나 자동 변환을 추가하지 않는다.
```

### 영향
현행 생산자는 설치 대상만 `repair`로 수락하고, 실행 입력 손상은 봉인 원문을 확인해 새 작업 공간을 여는 `retry`로 처리한다. 그러나 구형 입력 복원 실행기와 느슨한 검사, 그 상태 분기·직접 구성 시험·문서 허용이 남아 저장된 옛 처분을 재실행할 수 있다. 설치 수리의 진단·게시 경로는 유지하고, 입력 복원 전용 실행·후속·시험을 제거해 생산자·소비자·문서를 하나의 현행 계약으로 맞춘다.

### 근거
R1-10과 R1-30은 모두 현행 생산자가 만들지 않는 입력 복원 `repair`의 제거를 요구한다. R1-30의 중앙 경로 단순화는 설치 수리만 남기는 목적에 더 직접 맞으므로 취했다. R1-10의 현행 `retry` 시험으로의 교체 제안은 유지했고, 옛 복원 이력을 계속 마무리한다는 문면과 복원 성공을 전제한 시험은 버렸다. 지급 키 밖의 변경은 하지 않는다.

### 조각 1 — .claude/skills/do-math/references/CLI-실행-계약.md 811~811행
원래:
```
새 `repair`는 `installation:<스킬 상대 파일 경로>`의 설치 결함에 사용하며, 아래 실행 수명·복구 절과 「운영 점검」의 진단·검증 절차를 따른다. 저장된 입력 복원 이력의 `repair_deferred`·`repair_verification_failed`는 당시의 실패 상태로 읽고 성공으로 바꾸지 않는다. 작업자의 수리 산문을 셸 코드로 실행하지 않는다. 설치 기동 실패와 수락된 설치 결함 진단에서 사용하는 외부 복구 launcher는 `operator`의 별도 승인·잠금·설치 검사 계약을 따른다.
```
대체:
```
`repair`는 `installation:<스킬 상대 파일 경로>`의 설치 결함에 사용하며, 아래 실행 수명·복구 절과 「운영 점검」의 진단·검증 절차를 따른다. 작업자의 수리 산문을 셸 코드로 실행하지 않는다. 설치 기동 실패와 수락된 설치 결함 진단에서 사용하는 외부 복구 launcher는 `operator`의 별도 승인·잠금·설치 검사 계약을 따른다.
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/engine.py 747~747행
원래:
```
            and row.get("status") not in {"applied", "repair_deferred", "repair_verification_failed"}]
```
대체:
```
            and row.get("status") != "applied"]
```

### 조각 3 — .claude/skills/do-math/scripts/do_math/engine.py 4346~4346행
원래:
```
        disposition = operational_dispositions.validate_new_disposition(proposal)
```
대체:
```
        disposition = operational_dispositions.validate_disposition(proposal)
```

### 조각 4 — .claude/skills/do-math/scripts/do_math/engine.py 4385~4399행
원래:
```
            result = repair_execution.complete_repair(self, record)
            target = self.runtime["executions"][record["target_execution_id"]]
            if result["status"] in {"applied", "repair_verification_failed", "repair_deferred"}:
                if target.get("pending_operational_disposition") == record["id"]:
                    target.pop("pending_operational_disposition")
                followup = result.get("result", {}).get("followup")
                if followup:
                    owner = followup["next_owner"]
                    if owner in {"operational_review", "research_preparation"}:
                        self._enqueue(owner, target["id"] if owner == "operational_review" else previous.get("target"),
                            reason=followup["reason"], operational_disposition_id=record["id"])
                    else:
                        questions.link(self.runtime, execution_id=record["execution_id"], field="repair/" + record["id"],
                            owner=owner, targets=[target["id"]], reason=followup["reason"])
            return result
```
대체:
```
            return repair_execution.complete_repair(self, record)
```

### 조각 5 — .claude/skills/do-math/scripts/do_math/engine.py 4479~4480행
원래:
```
                if record['status'] in {'applied', 'repair_deferred', 'repair_verification_failed',
                        'installation_repair_pending', 'installation_repair_waiting', 'installation_repair_resolved'}:
```
대체:
```
                if record['status'] in {'applied', 'installation_repair_pending',
                        'installation_repair_waiting', 'installation_repair_resolved'}:
```

### 조각 6 — .claude/skills/do-math/scripts/do_math/operational_dispositions.py 10~10행
원래:
```
from collections.abc import Callable
```
대체:
```

```

### 조각 7 — .claude/skills/do-math/scripts/do_math/operational_dispositions.py 48~49행
원래:
```
        if not isinstance(disposition["repair_target"], str) or not disposition["repair_target"]:
            raise ValueError("repair needs repair_target")
```
대체:
```
        if not isinstance(disposition["repair_target"], str) or not disposition["repair_target"]:
            raise ValueError("repair needs repair_target")
        if not disposition["repair_target"].startswith("installation:"):
            raise ValueError("local input damage requires retry with replay_safety; repair is for installation: targets")
```

### 조각 8 — .claude/skills/do-math/scripts/do_math/operational_dispositions.py 96~102행
원래:
```
def validate_new_disposition(disposition):
    """New repairs change installation files; old input repairs remain readable."""
    checked = validate_disposition(disposition)
    if checked['kind'] == 'repair' and not checked['repair_target'].startswith('installation:'):
        raise ValueError('local input damage requires retry with replay_safety; repair is for installation: targets')
    return checked

```
대체:
```

```

### 조각 9 — .claude/skills/do-math/scripts/do_math/operational_dispositions.py 109~200행
원래:
```

def execute_repair(record: dict, *, target_execution: dict, current_basis_refs,
                   repair: Callable, verify: Callable, resume: Callable, publish: Callable) -> dict:
    """Execute an authorized repair, verify its exact effects, then request resume.

    ENGINE owns the callbacks: repair runs the admitted maintenance operation;
    verify reads its resulting artifacts; resume enqueues the continuation.
    publish must CAS this disposition record and its referenced evidence into
    the same authoritative runtime. Callback effect keys are stable per OD ID.
    No successful return from repair alone means that the disposition applied.

    In-flight states require reconciliation, not blind replay after a crash.
    Completed phases can be resumed without repeating their effects. An owner
    must reconcile an interrupted callback using its stable effect key before
    calling again with its recorded result.
    """
    value = deepcopy(record)
    disposition = validate_disposition(value["disposition"])
    if disposition["kind"] != "repair" or not disposition["meaning_preserving"]:
        raise ValueError("execute_repair requires an admitted meaning-preserving repair")
    if not isinstance(value.get("id"), str) or not value["id"]:
        raise ValueError("repair requires an authoritative disposition ID")
    if target_execution.get("id") != value.get("target_execution_id") or target_execution.get("status") != "ended":
        raise ValueError("repair requires its ended predecessor")

    def check_current():
        refs = current_basis_refs() if callable(current_basis_refs) else current_basis_refs
        if not disposition_is_current(disposition, refs):
            raise ValueError("repair disposition basis is no longer current")

    def save(status):
        from .repository import canonical_json
        value["status"] = status
        canonical_json(value)
        publish(deepcopy(value))

    def refs(result, field):
        items = result.get(field)
        if (not isinstance(items, list) or not items or any(not isinstance(x, str) or not x for x in items)
                or len(set(items)) != len(items)):
            raise ValueError("repair result needs distinct " + field)
        return items

    check_current()
    status = value.get("status", "pending")
    if status in {"repair_running", "repair_verifying", "repair_resuming"}:
        raise ValueError("interrupted repair phase requires effect reconciliation before retry")
    if status == "applied":
        if not all(value.get(key) for key in ("repair_effect", "repair_verification", "repair_resume")):
            raise ValueError("applied repair lacks execution, verification or resume evidence")
        return value
    if status not in {"pending", "awaiting_termination", "repair_required", "repair_verification_required", "repair_resume_required"}:
        raise ValueError("repair requires an explicit retry disposition after failure")
    plan = {"disposition_id": value["id"], "target_execution_id": value["target_execution_id"],
            "owner": disposition["next_owner"], "repair_target": disposition["repair_target"],
            "verification": disposition["verification"], "basis_refs": disposition["basis_refs"]}
    if status in {"pending", "awaiting_termination", "repair_required"}:
        save("repair_running")
        # If execution raises, the last published status explicitly requires
        # reconciliation. It does not silently re-run a possibly partial effect.
        effect = repair({**plan, "effect_key": value["id"] + ":repair"})
        if (not isinstance(effect, dict) or not isinstance(effect.get("execution_id"), str)
                or not effect["execution_id"] or effect.get("target") != plan["repair_target"]):
            raise ValueError("repair execution result does not identify the requested target")
        refs(effect, "effect_refs")
        value["repair_effect"] = deepcopy(effect)
        save("repair_verification_required")
    if value["status"] == "repair_verification_required":
        check_current()
        save("repair_verifying")
        verification = verify({**plan, "effect_key": value["id"] + ":verify"}, deepcopy(value["repair_effect"]))
        if (not isinstance(verification, dict) or not isinstance(verification.get("execution_id"), str)
                or not verification["execution_id"] or type(verification.get("passed")) is not bool
                or type(verification.get("meaning_preserved")) is not bool):
            raise ValueError("repair verification requires an execution and explicit verdicts")
        refs(verification, "evidence_refs")
        if set(refs(verification, "effect_refs")) != set(value["repair_effect"]["effect_refs"]):
            raise ValueError("repair verification did not inspect the exact repaired effects")
        value["repair_verification"] = deepcopy(verification)
        if not verification["passed"] or not verification["meaning_preserved"]:
            save("repair_verification_failed")
            return value
        save("repair_resume_required")
    check_current()
    save("repair_resuming")
    resumed = resume({**plan, "effect_key": value["id"] + ":resume"}, deepcopy(value["repair_verification"]))
    if (not isinstance(resumed, dict) or not isinstance(resumed.get("request_id"), str) or not resumed["request_id"]
            or resumed.get("continuation_of") != value["target_execution_id"]):
        raise ValueError("repair resume must identify a continuation of the repaired predecessor")
    value["repair_resume"] = deepcopy(resumed)
    save("applied")
    return value
```
대체:
```

```

### 조각 10 — .claude/skills/do-math/scripts/do_math/repair_execution.py 1~26행
원래:
```
"""Consume an admitted repair as an evidenced, deterministic ENGINE file effect.

This is not another provider attempt, permission ledger or execution registry.
The existing OD record owns progress; immutable Git artifacts own byte evidence.
Execution IDs on local effects identify the affected execution, not a claim
that its former worker performed the repair. No prose is executable here.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import secrets

from . import activities, execution_profiles, operational_dispositions
from .git_store import GitStateStoreError, PhysicalBoundary
from .repository import canonical_json


class RepairNeedsDecision(ValueError):
    """The observed effect no longer permits deterministic continuation."""


```
대체:
```
"""Route preserved failures and hand accepted installation repairs to recovery."""
from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path, PurePosixPath

from . import activities, operational_dispositions
from .git_store import GitStateStoreError
from .repository import canonical_json
```

### 조각 11 — .claude/skills/do-math/scripts/do_math/repair_execution.py 217~481행
원래:
```
def _now():
    return datetime.now(timezone.utc).isoformat()


def _input_path(workspace, relative):
    path = PurePosixPath(relative)
    if (not isinstance(relative, str) or path.as_posix() != relative or path.is_absolute()
            or len(path.parts) < 2 or path.parts[0] != "input"
            or any(p in {".", ".."} or ":" in p or "\\" in p for p in path.parts)):
        raise ValueError("repair target must be an exact sealed input path")
    destination = workspace.joinpath(*path.parts)
    boundary = PhysicalBoundary(workspace)
    # Check every existing parent, including Windows junctions, before writes.
    PhysicalBoundary(destination.parent)
    if not destination.parent.resolve().is_relative_to(workspace.absolute()):
        raise ValueError("repair parent escapes execution workspace")
    if destination.exists() or destination.is_symlink():
        with boundary.open(destination, "rb"):
            pass
    return destination, boundary


def _read_input(boundary, path):
    try:
        with boundary.open(path, "rb") as stream:
            return stream.read()
    except FileNotFoundError:
        return None


def _replace_input(boundary, path, raw):
    """Atomic same-directory replacement; no mutation of linked-file contents.

    This protects ordinary accidental path escape, not a hostile process with
    the same OS identity racing directory renames. The adopted boundary remains
    instructional, not OS isolation.
    """
    temporary = path.with_name(".repair-" + secrets.token_hex(12))
    try:
        with boundary.open(temporary, "xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        _input_path(boundary.root, path.relative_to(boundary.root).as_posix())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _verify_input(boundary, path, binding):
    raw = _read_input(boundary, path)
    return {"sha256": None if raw is None else _digest(raw),
            "bytes": None if raw is None else len(raw),
            "passed": raw is not None and _digest(raw) == binding["sha256"] and len(raw) == binding["bytes"]}


def complete_repair(engine, record):
    """One hook for ENGINE._complete_operational_disposition, before its fallback.

    The caller holds the existing instance writer lock and has admitted this
    operational judgment. ``engine`` supplies instance/runtime/head/store and
    its ordinary ``_save(artifacts=None)`` CAS. Reacquire records after saves:
    ENGINE replaces its assembled views. Never fall through to a research retry.

    Supported request: repair_target is an exact manifest catalog/detail path;
    verification is exactly ``sha256:<that entry's hash>``. Other requests are
    returned with reason/next owner, not evaluated as programs. Only an ended
    execution's private input is restored from its immutable Git input bundle.
    The former provider is not restarted here. A verified repair opens its
    existing activity's explicit continuation, for ordinary fresh admission.
    """
    identifier = record["id"]
    current = engine.runtime.get("operational_dispositions", {}).get(identifier)
    if current is None or current != record:
        raise ValueError("repair must consume the current authoritative OD record")
    record = deepcopy(current)
    disposition = operational_dispositions.validate_disposition(record["disposition"])
    if disposition["kind"] != "repair":
        raise ValueError("complete_repair only consumes repair dispositions")
    if disposition['repair_target'].startswith('installation:'):
        if record['status'] in {'installation_repair_pending', 'installation_repair_waiting', 'applied'}:
            return record
        return request_installation_repair(engine, record)
    state = deepcopy(record.get("result", {}).get("repair", {}))
    if record["status"] == "applied" and state:
        if (not state.get("repair_effect") or not state.get("repair_resume")
                or state.get("repair_verification", {}).get("passed") is not True
                or state.get("repair_verification", {}).get("meaning_preserved") is not True):
            raise ValueError("applied repair lacks verified effects and explicit continuation")
        return record
    if record["status"] in {"repair_verification_failed", "repair_deferred"}:
        return record

    def defer(reason, owner="operational_review"):
        latest = deepcopy(engine.runtime["operational_dispositions"][identifier])
        latest["status"] = "repair_deferred"
        latest.setdefault("result", {})["followup"] = {"kind": "repair_requires_decision",
            "reason": reason, "next_owner": owner, "target_execution_id": record["target_execution_id"]}
        engine.runtime["operational_dispositions"][identifier] = latest
        engine._save()
        return deepcopy(engine.runtime["operational_dispositions"][identifier])

    target = engine.runtime["executions"][record["target_execution_id"]]
    reviewer = engine.runtime["executions"].get(record["execution_id"])
    if target["status"] != "ended":
        raise ValueError("input repair requires an ended predecessor")
    if not disposition["meaning_preserving"]:
        return defer("A semantic change needs a new research preparation judgment", "research_preparation")
    if not reviewer or reviewer.get("role") != "operational_review" or reviewer.get("action", {}).get("target") != target["id"]:
        return defer("Repair lacks the matching operational review execution")
    activity = engine.runtime["activities"][target["owner_activity_id"]]
    if activity["status"] == "finished" or any(engine.runtime["executions"][eid]["status"] != "ended"
            for eid in activity["assigned_execution_ids"]):
        return defer("Original activity is finished or has a live successor; do not overwrite its input")
    if not target.get("action", {}).get("id"):
        return defer("Original activity has no identified continuation action")

    def basis_refs():
        live_target = engine.runtime["executions"][target["id"]]
        action = engine.runtime["executions"][reviewer["id"]].get("action", {})
        refs = {live_target["id"], *action.get("observation_refs", []), *action.get("obligation_ids", [])}
        refs.update(ref for ref in (live_target.get("result_ref"),
            engine.runtime.get("checkpoints", {}).get(target["id"], {}).get("artifact_ref")) if ref)
        return refs

    if not operational_dispositions.disposition_is_current(disposition, basis_refs()):
        return defer("Operational judgment cites a basis outside its current input")
    try:
        profile = execution_profiles.resolve_profile(engine.instance["execution_profiles"], target["execution_profile_ref"])
        review_profile = execution_profiles.resolve_profile(engine.instance["execution_profiles"], reviewer["execution_profile_ref"])
        if review_profile["role"] != "operational_review" or review_profile["actor_kind"] != reviewer["actor_kind"]:
            raise ValueError("authorizing reviewer differs from its fixed execution profile")
        manifest = target["input_manifest"]
        if manifest.get("execution_profile_ref") != target["execution_profile_ref"] or profile["role"] != target["role"]:
            raise ValueError("sealed input and selected profile differ")
        bundle = target["input_bundle"]
        if not isinstance(bundle, str) or not bundle or any(c in bundle for c in "/\\:") or bundle in {".", ".."}:
            raise ValueError("input bundle is not one immutable artifact identity")
        base = "runtime/artifacts/" + bundle
        sealed_manifest = engine.store.read(base + "/manifest.json", engine.head)
        if json.loads(sealed_manifest) != manifest:
            raise ValueError("current execution manifest differs from sealed input manifest")
        relative = disposition["repair_target"]
        matches = [row for row in [*manifest.get("catalog", []), *manifest.get("detail_sources", [])]
                   if row.get("path") == relative]
        if len(matches) != 1:
            raise ValueError("repair target is not one exact sealed catalog/detail entry")
        entry = matches[0]
        if (not isinstance(entry.get("sha256"), str) or len(entry["sha256"]) != 64
                or type(entry.get("bytes")) is not int or entry["bytes"] < 0):
            raise ValueError("sealed entry needs a SHA-256 hash and integer byte length")
        if disposition["verification"] != "sha256:" + entry["sha256"]:
            raise ValueError("verification needs the exact supported sha256:<sealed hash> contract; prose is not executed")
        source_ref = base + "/" + relative
        if entry.get("artifact_ref", source_ref) != source_ref:
            raise ValueError("input entry names a different artifact bundle")
        raw = engine.store.read(source_ref, engine.head)
        if _digest(raw) != entry["sha256"] or len(raw) != entry["bytes"]:
            raise ValueError("sealed source bytes fail their manifest hash/length")
        workspace = Path(engine.instance["workspace"]).absolute() / "runs" / target["id"] / "workspace"
        destination, boundary = _input_path(workspace, relative)
        binding = {"kind": "restore_sealed_input", "executor": "engine_local_file_effect",
            "execution_id": target["id"], "authorizing_execution_id": reviewer["id"],
            "disposition_sha256": _digest(canonical_json(disposition)),
            "execution_profile_ref": target["execution_profile_ref"],
            "review_profile_ref": reviewer["execution_profile_ref"], "manifest_sha256": _digest(sealed_manifest),
            "source_ref": source_ref, "target": relative, "sha256": entry["sha256"], "bytes": entry["bytes"],
            "workspace": str(workspace)}
        if state and state.get("binding") != binding:
            raise ValueError("repair binding changed after its first effect intent")
    except (ValueError, KeyError, OSError, GitStateStoreError) as error:
        return defer(str(error))

    # Git seals the whole bundle on its first publication, not just each file.
    artifact_base = "runtime/artifacts/" + identifier + "-repair-"
    pending = {}
    if not state:
        before = _read_input(boundary, destination)
        state = {"binding": binding, "before_sha256": None if before is None else _digest(before),
                 "intent_ref": artifact_base + "intent/receipt.json"}
        pending[state["intent_ref"]] = canonical_json({**binding, "before_sha256": state["before_sha256"],
                                                     "effect_key": identifier + ":repair"})
    else:
        intent = json.loads(engine.store.read(state["intent_ref"], engine.head))
        if intent != {**binding, "before_sha256": state["before_sha256"], "effect_key": identifier + ":repair"}:
            return defer("Persisted repair intent differs from immutable evidence")

    def publish(value):
        nonlocal state
        saved = deepcopy(value)
        for field in ("repair_effect", "repair_verification", "repair_resume"):
            if field in saved:
                state[field] = saved.pop(field)
        saved.setdefault("result", {})["repair"] = deepcopy(state)
        if saved["status"] == "repair_verification_failed":
            saved["result"]["followup"] = {"kind": "repair_verification_failed", "next_owner": "operational_review",
                "reason": "Restored bytes did not match the same sealed input; no continuation opened"}
        engine.runtime["operational_dispositions"][identifier] = saved
        engine._save(artifacts=dict(pending) or None)
        pending.clear()

    def repair(plan):
        observed = _read_input(boundary, destination)
        digest = None if observed is None else _digest(observed)
        if digest != binding["sha256"]:
            if digest != state["before_sha256"]:
                raise RepairNeedsDecision("repair target changed after intent; independent reconciliation required")
            _replace_input(boundary, destination, raw)
        effect_ref = artifact_base + "effect/receipt.json"
        effect = {"execution_id": target["id"], "executor": "engine_local_file_effect",
            "authorizing_execution_id": reviewer["id"], "target": relative,
            "effect_key": plan["effect_key"], "effect_refs": [effect_ref]}
        pending[effect_ref] = canonical_json({**binding, "effect_key": plan["effect_key"],
                                            "intent_ref": state["intent_ref"]})
        return effect

    def verify(plan, effect):
        expected_ref = artifact_base + "effect/receipt.json"
        expected_receipt = {**binding, "effect_key": identifier + ":repair", "intent_ref": state["intent_ref"]}
        if (effect.get("execution_id") != target["id"] or effect.get("effect_refs") != [expected_ref]
                or json.loads(engine.store.read(expected_ref, engine.head)) != expected_receipt):
            raise RepairNeedsDecision("repair verification references a different effect or immutable receipt")
        facts = _verify_input(boundary, destination, binding)
        ref = artifact_base + "verification/receipt.json"
        proof = {"execution_id": target["id"], "executor": "engine_local_file_effect",
            "effect_key": plan["effect_key"], "passed": facts["passed"], "meaning_preserved": facts["passed"],
            "effect_refs": effect["effect_refs"], "evidence_refs": [ref]}
        pending[ref] = canonical_json({**proof, "observed": facts, "source_ref": source_ref,
                                     "expected_sha256": binding["sha256"], "expected_bytes": binding["bytes"]})
        return proof

    def resume(plan, verification):
        expected_ref = artifact_base + "verification/receipt.json"
        receipt = json.loads(engine.store.read(expected_ref, engine.head))
        if (verification.get("evidence_refs") != [expected_ref]
                or any(receipt.get(key) != value for key, value in verification.items())
                or receipt.get("expected_sha256") != binding["sha256"]
                or receipt.get("source_ref") != source_ref):
            raise RepairNeedsDecision("continuation lacks the exact immutable verification receipt")
        if not _verify_input(boundary, destination, binding)["passed"]:
            raise RepairNeedsDecision("verified input changed before continuation; no research was resumed")
        # The queue and OD applied receipt are saved together by publish below.
        action = activities.continue_activity(engine.runtime, target["id"], at=_now(),
            reason="verified_input_repair:" + identifier, next_owner="engine")
        return {"request_id": action["id"], "continuation_of": target["id"], "effect_key": plan["effect_key"],
                "owner_activity_id": target["owner_activity_id"], "verification_refs": verification["evidence_refs"]}

    value = deepcopy(record)
    value.update({k: deepcopy(state[k]) for k in ("repair_effect", "repair_verification", "repair_resume") if k in state})
    # Safe reconciliation is specific to this idempotent byte restoration and
    # read-only verifier. It is not permission to replay arbitrary repairs.
    reconciled = {"repair_running": "repair_required", "repair_verifying": "repair_verification_required",
                  "repair_resuming": "repair_resume_required"}
    value["status"] = reconciled.get(value["status"], value["status"])
    if value["status"] == "applied" and not state.get("repair_effect"):
        # The current ENGINE producer prelabels new ODs applied. No effect has
        # actually been accepted until this consumer publishes all three phases.
        value["status"] = "repair_required"
    try:
        operational_dispositions.execute_repair(value, target_execution=target, current_basis_refs=basis_refs,
            repair=repair, verify=verify, resume=resume, publish=publish)
    except RepairNeedsDecision as error:
        return defer(str(error))
    return deepcopy(engine.runtime["operational_dispositions"][identifier])
```
대체:
```

```

### 조각 12 — .claude/skills/do-math/scripts/do_math/submission.py 688~689행
원래:
```
        from .operational_dispositions import validate_new_disposition, require_basis_refs
        check("output/disposition", lambda: validate_new_disposition(output["disposition"]))
```
대체:
```
        from .operational_dispositions import validate_disposition, require_basis_refs
        check("output/disposition", lambda: validate_disposition(output["disposition"]))
```

### 조각 13 — .claude/skills/do-math/scripts/tests/test_observation_audit1.py 1~1행
원래:
```
"""RV_CONTEXT 03/04/08 regression cases, using real local repair effects."""
```
대체:
```
"""Observation profile and exact control-response binding regression cases."""
```

### 조각 14 — .claude/skills/do-math/scripts/tests/test_observation_audit1.py 111~167행
원래:
```
    def test_repair_performs_restoration_then_verifies_before_resume_and_publication(self):
        target = self.ws / "input.txt"
        target.write_bytes(b"broken")
        wanted = hashlib.sha256(b"restored").hexdigest()
        record = {"id": "OD-1", "target_execution_id": "EX-1", "status": "pending", "disposition": {
            "kind": "repair", "basis_refs": ["EX-1"], "next_owner": "maintenance", "reason": "restore missing input",
            "repair_target": str(target), "meaning_preserving": True, "verification": "SHA-256=" + wanted}}
        published, order = [], []
        def repair(plan):
            order.append("repair")
            target.write_bytes(b"restored")
            return {"execution_id": "FIX-1", "target": plan["repair_target"], "effect_refs": ["ART-restored"]}
        def verify(plan, effect):
            order.append("verify")
            return {"execution_id": "VERIFY-1", "passed": hashlib.sha256(target.read_bytes()).hexdigest() == wanted,
                    "effect_refs": effect["effect_refs"], "evidence_refs": ["ART-hash"], "meaning_preserved": True}
        def resume(plan, verification):
            order.append("resume")
            self.assertTrue(verification["passed"])
            return {"request_id": "AC-resume", "continuation_of": "EX-1"}
        result = od.execute_repair(record, target_execution={"id": "EX-1", "status": "ended"},
            current_basis_refs={"EX-1"}, repair=repair, verify=verify, resume=resume, publish=lambda r: published.append(deepcopy(r)))
        self.assertEqual(order, ["repair", "verify", "resume"])
        self.assertEqual(result["status"], "applied")
        self.assertEqual(result["repair_effect"]["execution_id"], "FIX-1")
        self.assertEqual(result["repair_verification"]["evidence_refs"], ["ART-hash"])
        self.assertEqual(published[-1], result)

    def test_failed_verification_and_stale_basis_never_resume(self):
        record = {"id": "OD-1", "target_execution_id": "EX-1", "status": "pending", "disposition": {
            "kind": "repair", "basis_refs": ["EX-1"], "next_owner": "maintenance", "reason": "fix",
            "repair_target": "input", "meaning_preserving": True, "verification": "hash"}}
        calls = []
        args = dict(target_execution={"id": "EX-1", "status": "ended"}, repair=lambda p: {"execution_id": "F", "target": "input", "effect_refs": ["A"]},
            verify=lambda p,e: {"execution_id": "V", "passed": False, "effect_refs": ["A"], "evidence_refs": ["V-log"], "meaning_preserved": True},
            resume=lambda *a: calls.append("resume"), publish=lambda r: None)
        with self.assertRaises(ValueError): od.execute_repair(record, current_basis_refs=set(), **args)
        result = od.execute_repair(record, current_basis_refs={"EX-1"}, **args)
        self.assertEqual(result["status"], "repair_verification_failed")
        self.assertEqual(calls, [])

    def test_interrupted_repair_requires_reconciliation_and_never_replays_blindly(self):
        record = {"id": "OD-1", "target_execution_id": "EX-1", "status": "pending", "disposition": {
            "kind": "repair", "basis_refs": ["EX-1"], "next_owner": "maintenance", "reason": "fix",
            "repair_target": "input", "meaning_preserving": True, "verification": "hash"}}
        published, effects = [], []
        def repair(plan):
            effects.append(plan["effect_key"])
            raise OSError("lost after partial effect")
        args = dict(target_execution={"id": "EX-1", "status": "ended"}, current_basis_refs={"EX-1"},
            repair=repair, verify=lambda *a: self.fail("verification must wait"), resume=lambda *a: self.fail("no resume"),
            publish=lambda r: published.append(deepcopy(r)))
        with self.assertRaises(OSError): od.execute_repair(record, **args)
        self.assertEqual(published[-1]["status"], "repair_running")
        with self.assertRaisesRegex(ValueError, "reconciliation"): od.execute_repair(published[-1], **args)
        self.assertEqual(effects, ["OD-1:repair"])

```
대체:
```

```

### 조각 15 — .claude/skills/do-math/scripts/tests/test_observation_audit1.py 193~193행
원래:
```
            "scope": "Actual local file restoration/hash verification; provider events and central publication are test fixtures."},
```
대체:
```
            "scope": "Observation profiles and control-response binding; provider events and central publication are test fixtures."},
```

### 조각 16 — .claude/skills/do-math/scripts/tests/test_redesign_ENGINE.py 1451~1468행
원래:
```
    def test_central_repair_restores_actual_sealed_bytes_before_one_continuation(self):
        from test_repair_execution import RepairExecutionTests
        fixture = RepairExecutionTests("test_actual_restore_verify_and_explicit_activity_followup")
        fixture.setUp(); self.addCleanup(fixture.doCleanups)
        host = fixture.host
        host.runtime["executions"]["EX-target"]["pending_operational_disposition"] = "OD-repair"
        host._save()
        result = ResearchEngine._complete_operational_disposition(host, host.runtime["operational_dispositions"]["OD-repair"])
        host._save()
        self.assertEqual(result["status"], "applied")
        self.assertEqual(fixture.destination.read_bytes(), fixture.raw)
        self.assertEqual(len(host.runtime["queue"]), 1)
        self.assertEqual(host.runtime["queue"][0]["continuation_of"], "EX-target")
        self.assertNotIn("pending_operational_disposition", host.runtime["executions"]["EX-target"])
        ResearchEngine._complete_operational_disposition(host, host.runtime["operational_dispositions"]["OD-repair"])
        self.assertEqual(len(host.runtime["queue"]), 1)
        proof = host.runtime["operational_dispositions"]["OD-repair"]["result"]["repair"]
        self.assertEqual(proof["repair_effect"]["effect_refs"], proof["repair_verification"]["effect_refs"])
```
대체:
```

```

### 조각 17 — .claude/skills/do-math/scripts/tests/test_repair_execution.py 1~219행
원래:
```
"""Real Git/file-effect tests for the central deterministic repair consumer."""
from copy import deepcopy
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import activities, execution_lifecycle, execution_profiles
from do_math.engine import DEFAULT_CONFIG
from do_math.repository import ResearchRepository, canonical_json
from do_math import repair_execution

AT = "2026-09-20T00:00:00Z"


class RepositoryHost:
    """Only the ENGINE save facade; all persistence/validation uses the real store."""
    def _save(self, artifacts=None):
        self.head = self.store.save_with_state(self.head, self.instance, self.runtime, artifacts=artifacts)[0]
        self.head, self.instance, self.runtime = self.store.load(self.head)


class RepairExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        repo = root / "repo"
        repo.mkdir()
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
        self.host = host = RepositoryHost()
        host.store = ResearchRepository(repo, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV")
        configured = execution_profiles.build_profiles(DEFAULT_CONFIG)
        profiles = configured["execution_profiles"]
        host.instance = {"feature_version": 5, "workspace": str(root / "private"),
            "capacity_constraints": configured["capacity_constraints"],
            "execution_profiles": {key: p for key, p in profiles.items()
                                   if p["role"] in {"research_work", "operational_review"}}}
        host.runtime = {"feature_version": 5, "executions": {}, "queue": [], "operational_dispositions": {}}
        for eid, role, aid in [("EX-target", "research_work", "AY-target"),
                                ("EX-review", "operational_review", "AY-review")]:
            profile = next(p for p in host.instance["execution_profiles"].values() if p["role"] == role)
            activities.open_activity(host.runtime, activity_id=aid, activity_kind=role,
                owner_ref="engine", input_refs=[], opened_at=AT)
            execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=aid,
                actor_kind="ai", input_manifest={}, profile_ref=execution_profiles.profile_ref(profile), created_at=AT)
            execution.update(role=role, action={"id": "AC-" + eid, "role": role, "owner_activity_id": aid})
            activities.assign_execution(host.runtime, aid, execution)
            execution_lifecycle.transition_execution(execution, "ended", at=AT, outcome="cancelled")
        self.raw = b"sealed mathematical input\n"
        self.digest = hashlib.sha256(self.raw).hexdigest()
        self.relative = "input/catalog/tasks.json"
        target = host.runtime["executions"]["EX-target"]
        target["input_bundle"] = "BA-target"
        target["input_manifest"] = {"catalog": [{"path": self.relative, "sha256": self.digest, "bytes": len(self.raw)}],
                                    "execution_profile_ref": target["execution_profile_ref"]}
        self.source = "runtime/artifacts/BA-target/" + self.relative
        self.destination = root / "private/runs/EX-target/workspace" / self.relative
        self.destination.parent.mkdir(parents=True)
        self.destination.write_bytes(b"damaged")
        self.record = {"id": "OD-repair", "execution_id": "EX-review", "target_execution_id": "EX-target",
            "created_at": AT, "status": "repair_required", "disposition": {
                "kind": "repair", "basis_refs": ["EX-target"], "next_owner": "engine",
                "reason": "Restore the sealed input", "repair_target": self.relative,
                "meaning_preserving": True, "verification": "sha256:" + self.digest}}
        host.runtime["operational_dispositions"][self.record["id"]] = deepcopy(self.record)
        host.runtime["executions"]["EX-review"]["action"]["target"] = "EX-target"
        host.head = host.store.initialize(host.instance, host.runtime)
        host._save({self.source: self.raw,
                    "runtime/artifacts/BA-target/manifest.json": canonical_json(target["input_manifest"])})

    def run_repair(self):
        return repair_execution.complete_repair(self.host, self.host.runtime["operational_dispositions"]["OD-repair"])

    def test_actual_restore_verify_and_explicit_activity_followup(self):
        result = self.run_repair()
        self.assertEqual(result["status"], "applied")
        self.assertEqual(self.destination.read_bytes(), self.raw)
        proof = result["result"]["repair"]
        self.assertTrue(proof["repair_verification"]["passed"])
        self.assertEqual(proof["repair_effect"]["effect_refs"], proof["repair_verification"]["effect_refs"])
        action = self.host.runtime["queue"][0]
        self.assertEqual(action["continuation_of"], "EX-target")
        self.assertEqual(action["owner_activity_id"], "AY-target")
        self.assertEqual(len(self.host.runtime["executions"]), 2)  # no fictitious provider run
        self.assertEqual(self.host.store.load()[2]["operational_dispositions"]["OD-repair"], result)

    def reload(self):
        self.host.head, self.host.instance, self.host.runtime = self.host.store.load()

    def test_actual_corruption_after_effect_fails_verification_without_followup(self):
        replace = repair_execution._replace_input
        def corrupt(*args):
            replace(*args)
            self.destination.write_bytes(b"corrupted after restoration")
        with patch.object(repair_execution, "_replace_input", side_effect=corrupt):
            result = self.run_repair()
        self.assertEqual(result["status"], "repair_verification_failed")
        self.assertFalse(result["result"]["repair"]["repair_verification"]["passed"])
        self.assertEqual(self.host.runtime["queue"], [])
        self.assertEqual(result["result"]["followup"]["next_owner"], "operational_review")

    def test_interruption_after_file_effect_reconciles_without_replacing_twice(self):
        replace = repair_execution._replace_input
        def interrupt(*args):
            replace(*args)
            raise RuntimeError("simulated loss after actual os.replace")
        with patch.object(repair_execution, "_replace_input", side_effect=interrupt):
            with self.assertRaisesRegex(RuntimeError, "simulated loss"):
                self.run_repair()
        self.reload()
        self.assertEqual(self.host.runtime["operational_dispositions"]["OD-repair"]["status"], "repair_running")
        with patch.object(repair_execution, "_replace_input", side_effect=AssertionError("duplicate effect")):
            result = self.run_repair()
        self.assertEqual(result["status"], "applied")
        head = self.host.head
        self.assertEqual(self.run_repair(), result)
        self.assertEqual(head, self.host.head)
        self.assertEqual(len(self.host.runtime["queue"]), 1)

    def test_interruption_after_verification_retains_proof_and_only_opens_followup(self):
        save = self.host._save
        def interrupt(artifacts=None):
            save(artifacts)
            if self.host.runtime["operational_dispositions"]["OD-repair"]["status"] == "repair_resume_required":
                raise RuntimeError("simulated loss after verification CAS")
        with patch.object(self.host, "_save", side_effect=interrupt):
            with self.assertRaisesRegex(RuntimeError, "simulated loss"):
                self.run_repair()
        self.reload()
        with patch.object(repair_execution, "_replace_input", side_effect=AssertionError("duplicate effect")):
            result = self.run_repair()
        self.assertEqual(result["status"], "applied")
        self.assertEqual(len(self.host.runtime["queue"]), 1)

    def test_interrupted_resume_queue_and_receipt_are_one_git_cas(self):
        save = self.host._save
        def interrupt(artifacts=None):
            if self.host.runtime["operational_dispositions"]["OD-repair"]["status"] == "applied":
                raise RuntimeError("simulated loss before final CAS")
            save(artifacts)
        with patch.object(self.host, "_save", side_effect=interrupt):
            with self.assertRaisesRegex(RuntimeError, "simulated loss"):
                self.run_repair()
        self.reload()
        self.assertEqual(self.host.runtime["queue"], [])
        self.assertEqual(self.host.runtime["operational_dispositions"]["OD-repair"]["status"], "repair_resuming")
        self.assertEqual(self.run_repair()["status"], "applied")
        self.assertEqual(len(self.host.runtime["queue"]), 1)

    def test_prose_is_returned_to_owner_and_never_executed(self):
        record = self.host.runtime["operational_dispositions"]["OD-repair"]
        record["disposition"]["verification"] = "Write-Output hacked; remove everything"
        self.host._save()
        result = self.run_repair()
        self.assertEqual(result["status"], "repair_deferred")
        self.assertIn("prose is not executed", result["result"]["followup"]["reason"])
        self.assertEqual(self.destination.read_bytes(), b"damaged")
        self.assertEqual(self.host.runtime["queue"], [])

    def test_source_hash_is_checked_before_file_mutation(self):
        target = self.host.runtime["executions"]["EX-target"]
        target["input_bundle"] = "BA-bad-source"
        self.host._save({"runtime/artifacts/BA-bad-source/" + self.relative: b"incorrect source",
            "runtime/artifacts/BA-bad-source/manifest.json": canonical_json(target["input_manifest"])})
        result = self.run_repair()
        self.assertEqual(result["status"], "repair_deferred")
        self.assertIn("manifest hash/length", result["result"]["followup"]["reason"])
        self.assertEqual(self.destination.read_bytes(), b"damaged")

    def test_missing_sealed_source_returns_reason_and_next_owner(self):
        target = self.host.runtime["executions"]["EX-target"]
        target["input_bundle"] = "BA-missing-source"
        self.host._save({"runtime/artifacts/BA-missing-source/manifest.json": canonical_json(target["input_manifest"])})
        result = self.run_repair()
        self.assertEqual(result["status"], "repair_deferred")
        self.assertEqual(result["result"]["followup"]["next_owner"], "operational_review")
        self.assertIn("failed", result["result"]["followup"]["reason"])
        self.assertEqual(self.destination.read_bytes(), b"damaged")

    def test_different_post_intent_target_is_not_overwritten_on_recovery(self):
        with patch.object(repair_execution, "_replace_input", side_effect=RuntimeError("lost before effect")):
            with self.assertRaises(RuntimeError):
                self.run_repair()
        self.reload()
        self.destination.write_bytes(b"new information not in original intent")
        result = self.run_repair()
        self.assertEqual(result["status"], "repair_deferred")
        self.assertIn("changed after intent", result["result"]["followup"]["reason"])
        self.assertEqual(self.destination.read_bytes(), b"new information not in original intent")
        self.assertEqual(self.host.runtime["queue"], [])

    def test_profile_binding_is_checked_against_sealed_manifest(self):
        self.host.runtime["executions"]["EX-target"]["input_manifest"]["execution_profile_ref"] = {}
        result = self.run_repair()
        self.assertEqual(result["status"], "repair_deferred")
        self.assertEqual(self.destination.read_bytes(), b"damaged")


if __name__ == "__main__":
    if "--evidence" in sys.argv:
        import json
        position = sys.argv.index("--evidence")
        evidence = Path(sys.argv[position + 1])
        del sys.argv[position:position + 2]
        program = unittest.main(exit=False)
        evidence.write_text(json.dumps({"tests_run": program.result.testsRun,
            "passed": program.result.wasSuccessful(), "failures": [str(x) for x in program.result.failures],
            "errors": [str(x) for x in program.result.errors],
            "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "source_sha256": hashlib.sha256(Path(repair_execution.__file__).read_bytes()).hexdigest(),
            "actual": "Real isolated Git CAS/schema repository, sealed artifacts and filesystem replacements",
            "doubles": "ENGINE facade (real store), injected crash/corruption boundaries; no live provider"}, indent=2), encoding="utf-8")
        sys.exit(0 if program.result.wasSuccessful() else 1)
    unittest.main()
```
대체:
```
"""Central handoff of an accepted installation repair; no model is called."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import repair_execution
from do_math.engine import ResearchEngine


class RepairExecutionTests(unittest.TestCase):
    def fixture(self):
        record = {"id": "OD-repair", "execution_id": "EX-review", "target_execution_id": "EX-target", "status": "repair_required", "disposition": {"kind": "repair", "basis_refs": ["EX-target"], "next_owner": "installation_recovery", "reason": "The installed receiver rejects valid output.", "repair_target": "installation:scripts/do_math/engine.py", "meaning_preserving": True, "verification": "Reproduce the rejected output and run the receiver regression."}}
        runtime = {"executions": {"EX-target": {"id": "EX-target", "status": "ended", "error": "receiver failure", "result_ref": "runtime/artifacts/BA-failure/result.json", "action": {}}, "EX-review": {"id": "EX-review", "status": "ended"}}, "operational_dispositions": {record["id"]: deepcopy(record)}, "queue": []}
        return SimpleNamespace(runtime=runtime, _save=Mock()), record

    def test_central_handoff_preserves_failure_and_does_not_open_a_retry(self):
        host, record = self.fixture()
        with patch.object(repair_execution, "installation_fingerprint", return_value="a" * 64):
            result = ResearchEngine._complete_operational_disposition(host, record)
        self.assertEqual(result["status"], "installation_repair_pending")
        self.assertEqual(result["disposition"], record["disposition"])
        self.assertEqual(host.runtime["queue"], [])
        self.assertEqual(ResearchEngine._complete_operational_disposition(host, result), result)


if __name__ == "__main__":
    unittest.main()
```

### 조각 18 — .claude/skills/do-math/scripts/tests/test_static_review_repairs.py 576~576행
원래:
```
        fixture = RepairExecutionTests('test_actual_restore_verify_and_explicit_activity_followup')
```
대체:
```
        fixture = RepairExecutionTests('test_central_handoff_preserves_failure_and_does_not_open_a_retry')
```

### 조각 19 — .claude/skills/do-math/scripts/tests/test_static_review_repairs.py 628~628행
원래:
```
        fixture = RepairExecutionTests('test_actual_restore_verify_and_explicit_activity_followup')
```
대체:
```
        fixture = RepairExecutionTests('test_central_handoff_preserves_failure_and_does_not_open_a_retry')
```

### 조각 20 — .claude/skills/do-math/계약/운영-점검.md 65~65행
원래:
```
새 후속 요청과 운영 처분의 적용 기록은 같은 Git 갱신으로 보존되며, 같은 처분의 재처리는 후속을 중복 생성하지 않는다. 이미 저장된 옛 입력 복원 요청은 기존 복원·검증·후속 계약으로 마무리할 수 있다. 그 이력의 `repair_deferred`나 `repair_verification_failed`를 성공으로 쓰거나, 새 입력 복원 요청을 `repair`로 제출하지 않는다.
```
대체:
```
새 후속 요청과 운영 처분의 적용 기록은 같은 Git 갱신으로 보존되며, 같은 처분의 재처리는 후속을 중복 생성하지 않는다. 입력 손상은 위의 `retry` 계약으로 처리하고, `repair`는 설치 결함에 사용한다.
```

### 조각 21 — .claude/skills/do-math/계약/유지보수.md 72~72행
원래:
```
종료된 실행의 로컬 입력만 손상됐고 Git에 봉인된 원문은 온전하면 「운영 점검」의 `retry` 경로로 남은 의무를 잇는다. 실행기는 선행 실행의 종료·봉인 자료·현재 권한을 확인한 뒤 새 작업 공간과 입력을 지급한다. 유지보수 AI가 옛 사본을 복원하거나 별도 복원·검증 단계를 만드는 일은 필요하지 않다. 이미 보존된 복원·검증 영수증은 실제 성공·실패 범위의 이력으로 읽는다. 봉인 원문 자체의 손상, 지원하지 않는 환경 수리나 남은 의미 판단은 이유와 실제 다음 소유자에게 돌린다. 설치 파일 결함의 새 `repair`와 외부 복구는 「운영 점검」과 「독립 운영」 계약을 따른다.
```
대체:
```
종료된 실행의 로컬 입력만 손상됐고 Git에 봉인된 원문은 온전하면 「운영 점검」의 `retry` 경로로 남은 의무를 잇는다. 실행기는 선행 실행의 종료·봉인 자료·현재 권한을 확인한 뒤 새 작업 공간과 입력을 지급한다. 유지보수 AI가 옛 사본을 복원하거나 별도 복원·검증 단계를 만드는 일은 필요하지 않다. 봉인 원문 자체의 손상, 지원하지 않는 환경 수리나 남은 의미 판단은 이유와 실제 다음 소유자에게 돌린다. 설치 파일 결함의 `repair`와 외부 복구는 「운영 점검」과 「독립 운영」 계약을 따른다.
```


### 판정
확정: 기각 · 승인기 [] · 기각기 [1, 2, 3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 1: 관문 3·4·5가 성립하지 않는다. complete_repair 정의를 통째로 삭제하면서 중앙이 여전히 이를 호출하므로, 보존한다고 한 설치 수리 경로가 AttributeError로 깨진다. 또한 조각 18·19는 시험 메서드 이름만 바꾸어 기존 fixture 소비자의 host·store·head 요구를 충족하지 못한다. 입력 복원 제거 뒤 설치 수리와 현행 retry 시험을 유지한다는 영향 칸의 결과를 대체 문면이 달성하지 못하며, 구현·호출부·시험을 같은 계약으로 정렬한다는 불변식에도 어긋난다.
- 기 2: 관문 3·4에 미달한다. 영향 칸은 설치 수리의 진단·게시 경로를 유지한다고 하지만, 제안대로면 설치 repair가 삭제된 함수를 호출해 AttributeError로 중단한다. 새 설치 수리 시험도 같은 호출을 통과해야 하므로 이를 해소하지 못한다. 기존 retry 회귀 두 개는 fixture.host를 얻지 못해 유지해야 할 후속·게시 검사를 잃는다. 구형 입력 복원 제거라는 지적은 실재하지만 이 조각 전건으로는 주장한 손상을 없애면서 현행 설치 수리와 retry 검사를 보존할 수 없다.
- 기 3: 관문 3·4 미충족. 영향 칸은 설치 수리의 현행 진단·게시 경로를 유지한다고 하지만, 제안대로면 그 경로가 삭제된 complete_repair를 호출하여 AttributeError를 낸다. 기존 retry 경계 시험 두 곳도 fixture.host가 없어 실패한다. 구형 입력 복원 제거 자체의 타당성과 별개로, 지급된 대체 문면은 현행 소비자와 시험을 보존하지 못한다.

## R1-M3

### 원문
구성: R1-06 · R1-21

### 위치
`.claude/skills/do-math/scripts/do_math/engine.py` 594행, 2995행, 3029~3034행과 `.claude/skills/do-math/scripts/tests/test_observations.py` 308~311행, `test_redesign_ENGINE.py` 1287행·1424행, `test_research_reliability.py` 96행·167행·493행이다.

### 기준
`.claude/skills/do-math/AGENTS.md` 「개발 원칙」:

```
- 설계를 바꾸면 구현·호출부·스키마·테스트·예시·문서를 같은 변경에서 새 계약으로 교체한다. 구판 호환을 위한 이전 구현·이름 별칭·래퍼·구형 인자·무시되는 설정·버전별 분기·마이그레이션 경로를 남기지 않는다.
```

```
- 테스트도 현행 계약을 직접 구성한다. 구형 fixture나 인터페이스를 살리려고 제품 코드에 예외를 넣지 않는다. 폐기한 기능만 검사하는 테스트는 제거하고, 유지하는 기능의 검사는 새 계약에 맞춘다.
```

### 영향
운영 점검 요청은 2995~3000행에서 직접 `_enqueue`로 공통 배정 경로에 넣는다. 생성 뒤 바뀌지 않는 `_inline_reviewing`과 호출되지 않는 `_run_inline_review`는 이 경로의 선택에 기여하지 않지만, 시험 fixture는 이를 계속 구성하거나 관측한다. 이를 남기면 현행 계약 밖의 래퍼와 무시되는 설정을 유지하고 실제 요청 생산 지점의 시험 관측도 흐린다. 플래그·래퍼와 그 fixture 설정을 없애되, 기한·현재성·살아 있는 실행 확인, 운영 슬롯 배정, 나머지 관찰·저장 대역은 유지한다.

### 근거
R1-06과 R1-21은 같은 원인, 기준, 9개 정규화 조각을 제안한다. 사본에서 594행의 거짓 대입, 2995행의 부정 조건, 3029~3034행의 `_enqueue` 래퍼, 그리고 다섯 시험 자리의 `_inline_reviewing` 설정을 확인했다. `test_observations.py`의 가짜 객체는 실제 요청 지점인 `_enqueue`를 관측하도록 바꾼다. R1-06의 `**kw`와 R1-21의 `**k`는 동등하므로 전자를 취했다. 두 항목의 graphify 언급은 함수 호출 부재의 독립 근거가 아니므로 병합 근거에서 버리고, 사본의 정의·대입·호출 위치와 기준 원문만 남겼다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/engine.py 594~594행
원래:
```
        self._inline_reviewing = False
```
대체:
```

```

### 조각 2 — .claude/skills/do-math/scripts/do_math/engine.py 2995~2995행
원래:
```
                    if trigger and live and not self._inline_reviewing and self.runtime["status"] not in {"paused", "closed"}:
```
대체:
```
                    if trigger and live and self.runtime["status"] not in {"paused", "closed"}:
```

### 조각 3 — .claude/skills/do-math/scripts/do_math/engine.py 3029~3034행
원래:
```
    def _run_inline_review(self, parent_id: str, observation: dict) -> None:
        # All operational reviews use the same fixed-profile execution and receipt path.
        self._enqueue("operational_review", parent_id, live=True, observation=json_safe(observation),
                      obligation_ids=observation.get("obligation_ids", []),
                      observation_refs=observation.get("observation_refs", []))
        self._save()
```
대체:
```

```

### 조각 4 — .claude/skills/do-math/scripts/tests/test_observations.py 308~311행
원래:
```
        fake = SimpleNamespace(_controls=lambda: None, _check_conversations=lambda: False, _save=lambda *a: None,
            _inline_reviewing=False, instance={"workspace": str(self.ws)}, runtime={"status": "running"}, _trackers={},
            _review_observation_source=lambda execution_id, event: None,
            _run_inline_review=lambda *a: queued.append(a))
```
대체:
```
        fake = SimpleNamespace(_controls=lambda: None, _check_conversations=lambda: False, _save=lambda *a: None,
            instance={"workspace": str(self.ws)}, runtime={"status": "running"}, _trackers={},
            _review_observation_source=lambda execution_id, event: None,
            _enqueue=lambda *a, **kw: queued.append((a, kw)))
```

### 조각 5 — .claude/skills/do-math/scripts/tests/test_redesign_ENGINE.py 1287~1287행
원래:
```
        engine._inline_reviewing = False; engine._transport = Mock(); engine._transport_bindings = {"EX-one": {}}
```
대체:
```
        engine._transport = Mock(); engine._transport_bindings = {"EX-one": {}}
```

### 조각 6 — .claude/skills/do-math/scripts/tests/test_redesign_ENGINE.py 1424~1424행
원래:
```
        engine._inline_reviewing = False; engine._record_review_observation = Mock()
```
대체:
```
        engine._record_review_observation = Mock()
```

### 조각 7 — .claude/skills/do-math/scripts/tests/test_research_reliability.py 96~96행
원래:
```
        engine._save = Mock(); engine._inline_reviewing = False
```
대체:
```
        engine._save = Mock()
```

### 조각 8 — .claude/skills/do-math/scripts/tests/test_research_reliability.py 167~167행
원래:
```
        engine._save = Mock(); engine._inline_reviewing = False
```
대체:
```
        engine._save = Mock()
```

### 조각 9 — .claude/skills/do-math/scripts/tests/test_research_reliability.py 493~493행
원래:
```
            engine._save = Mock(); engine._inline_reviewing = False
```
대체:
```
            engine._save = Mock()
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 승인하되 고치지 않는다
