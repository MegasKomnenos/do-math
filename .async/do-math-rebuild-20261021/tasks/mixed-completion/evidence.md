# 실제 혼합 연구 완주 결과

수정 후 새 인스턴스가 사람의 개입 없이 **계획 → 연구 → 독립 연구 검토 → 다음 계획 → 목표 검토 achieved**를 완주했다. 5개 세션이 모두 종료 코드 0으로 끝나 공식 재검사·공개 반영을 마쳤고 실행기도 완료 상태로 종료했다. 개발 task는 목표·설정만 제공했으며 이 인스턴스에 추가 입력·수동 산출 편집·재기동을 하지 않았다. 첫 실행에서 발견한 Windows 상태 교체 결함과 수정은 아래 실행 경위에 구분했다.

최종 인스턴스 절대 경로: `C:/math/.async/do-math-rebuild-20261021/tasks/mixed-completion/evidence/instance-add-zero-fixed-20261021/`.

## 후속 검토자의 읽기 경로

1. [목표](evidence/preparation/goal.md)와 [설정](evidence/preparation/settings.json)을 읽는다.
2. [공개 연구 output.json](evidence/instance-add-zero-fixed-20261021/knowledge/k3812dd40113a4425b0b901de60dfd0bc/output.json)에서 [해설](evidence/instance-add-zero-fixed-20261021/knowledge/k3812dd40113a4425b0b901de60dfd0bc/exposition.md), [Lean 원문](evidence/instance-add-zero-fixed-20261021/knowledge/k3812dd40113a4425b0b901de60dfd0bc/Proof.lean), [컴파일 기록](evidence/instance-add-zero-fixed-20261021/knowledge/k3812dd40113a4425b0b901de60dfd0bc/lean-verification.json)으로 간다.
3. [독립 연구 검토](evidence/instance-add-zero-fixed-20261021/knowledge/kf5af23be4e1b4e0588de16f547142351/output.json)와 [검토 근거](evidence/instance-add-zero-fixed-20261021/knowledge/kf5af23be4e1b4e0588de16f547142351/review-notes.md)를 읽는다. target.record는 위 연구 ID이며 결과 add_zero_all은 supported / accepted / matches다.
4. [다음 계획](evidence/instance-add-zero-fixed-20261021/knowledge/k886da92b6d4f49a8a83840b838feff00/output.json)이 그 검토를 읽고 목표 검토를 요청한 이유를 읽는다.
5. [목표 검토](evidence/instance-add-zero-fixed-20261021/knowledge/kc7325f0829e84ab5ab14fdfd5938ca33/output.json)의 achieved와 [공개 상세 근거](evidence/instance-add-zero-fixed-20261021/knowledge/kc7325f0829e84ab5ab14fdfd5938ca33/goal-review-notes.md), [재컴파일 기록](evidence/instance-add-zero-fixed-20261021/knowledge/kc7325f0829e84ab5ab14fdfd5938ca33/lean-recheck.json)을 읽는다.
6. [최종 status](evidence/final-status.json), [세션별 실행·공식 검사 발췌](evidence/session-evidence.json), [Git 기록](evidence/git-evidence.txt)으로 실제 프로세스 흐름을 확인한다. 수학 판단의 근거는 2~5의 공개 자료이며 작성자 CLI 로그로 대체하지 않는다.

## 세션과 공개 기록

| 세션 ID | 범주 | 공급자/설정 모델 | 노력 | 공개 기록 | 자기 공식 검사 로그 행 |
|---|---|---|---|---|---|
| `s742ec928bdcf45ca9de8dc319f48eb2f` | plan | `codex/gpt-6.1-sol` | high | `kb6b5f6071b954b05979968472814f8e9` | 16 |
| `s64441e372131443796865caff9e7b1ef` | research | `codex/gpt-6.1-sol` | high | `k3812dd40113a4425b0b901de60dfd0bc` | 28 |
| `sdd6fb4ae8326435b91e5c0d4047f91de` | review | `claude/sonnet` | high | `kf5af23be4e1b4e0588de16f547142351` | 45 |
| `sd268523d1f2344cf8cee2a3dac5de1e5` | plan | `codex/gpt-6.1-sol` | high | `k886da92b6d4f49a8a83840b838feff00` | 24 |
| `s44423f00d3434963b5caf6bcb823ea70` | review | `claude/sonnet` | high | `kc7325f0829e84ab5ab14fdfd5938ca33` | 63 |

표의 행 번호는 각 `sessions/<ID>/cli.stdout.jsonl`에서 1부터 센 것이다. 모든 세션이 실제 `check.py <자기 세션>`를 호출해 `{"ok": true, "errors": []}`를 받았다. Claude 결과 행은 각각 46과 64이며 호출/응답을 tool_use_id로 연결한 발췌를 session-evidence.json에 남겼다. launch.json의 실제 argv에서 공급자 접두 없이 Codex `gpt-6.1-sol`/high, Claude `sonnet`/high가 전달됐다. 두 Claude CLI의 init 이벤트는 실제 모델을 `claude-sonnet-5-5`로 보고했다. 원 launch.json·process.json·exit.json·CLI 로그는 각 세션 폴더에 보존된다.

실행기의 재검사는 `runner.py:Runner.finish`가 `check_session(session)` 통과 뒤에만 publishing·knowledge 복사·Git 커밋·integrated로 진행하는 코드와 실제 상태·공개 기록·커밋을 대조했다. 별도 재검사 로그 필드를 새로 만들거나 사후 검사 실행을 당시 재검사처럼 기록하지 않았다. `apply_output`은 연구 뒤 자동 검토 요청, 검토 뒤 review_finished 사건, 목표 achieved의 complete 기록을 만들었다. 다음 계획의 input.json에는 공개 독립 검토 ID를 가리키는 review_finished가 있으며, 두 검토의 input/prompt에는 작성자 세션 경로가 전달되지 않았다.

최종 상태는 `complete=kc7325f0829e84ab5ab14fdfd5938ca33`, `runner_alive=false`, 다섯 세션 모두 integrated다. 호스트·CLI도 모두 종료했다. 추가 사용자 입력은 `seen_inputs=[]`이고 외부 입력/한도 대기가 없었다. 수정 후 실행기의 stderr는 0바이트다. Git은 초기화 1커밋 + 공개 5커밋으로 총 6커밋이며 `git status --porcelain`은 비어 있다. 각 공개 기록은 하나의 Publish 커밋과 연결된다.

## 공개 수학 결과를 대조한 내용과 한계

직접 읽은 정리는 `theorem add_zero_all (n : Nat) : n + 0 = n := by rfl`이다. 추가 가정·sorry·공리가 없고 임의의 Nat, 따라서 0을 포함한다. 해설은 Nat의 범위, Nat.add의 오른쪽 인자 0 계산, 정의적 동등성에서 등호 반사성으로 이어지는 이유를 설명한다. 연구와 검토의 공개 기록에는 같은 원문 컴파일 종료 코드 0과 빈 진단이 기록돼 있다. 독립 연구 검토와 목표 검토는 각각 공개 원문을 자기 작업 사본으로 재컴파일했으며, 해설·타입·논증 대응을 별도로 판단했다. 목표 검토가 공개한 Audit.lean/Control.lean 및 lean-recheck.json도 읽었다. 음성 대조 Control.lean의 종료 코드 1은 의도된 실패이고 목표 정리의 실패가 아니다.

실제 판본은 `Lean (version 4.32.0, x86_64-w64-windows-gnu, commit 8c9756b28d64dab099da31a4c09229a9e6a2ef35, Release)`다. 연구·독립 검토·목표 검토에 모두 기록돼 있다. 수학 확인을 개발 세션이 다시 수행하지 않았으며 공개 원문과 두 독립 검토의 구체적 확인 범위로 판단했다. 한 판본만 사용했다는 한계와 OfNat 표기 해석의 설명 생략은 목표 검토가 목표 조건에 대조해 달성을 막지 않는다고 판단했고, 해당 설명을 읽어 확인했다.

이 결과는 Windows의 작은 core Lean 목표에 대한 실제 혼합 완주다. Linux, 호스트 재부팅, 실제 공급자 한도, 장기 어려운 연구와 다른 Lean 판본을 확인한 근거는 아니다. 실제 한도는 발생하지 않았고 유도하지 않았다. 제품 환경 고정·해시 봉인·수학 검사 확장은 추가하지 않았다. 최종 독립 개발 review와 공용 소스 통합은 manager의 후속 작업이다.

# 실행 경위: 첫 시도와 수정 후 기동

## 실행 위치와 입력

이 배정은 workspace의 새 do-math 사용자 진입점 `SKILL.md`를 따라 목표·설정을 준비하고 실제 Codex·Claude 세션의 무인 완료를 확인한다. 개발 세션은 목표·설정 준비와 운영 조회만 수행하며 연구 계획·지시·산출·검토를 대신 작성하지 않는다.

- 스킬: `C:/math/.async/do-math-rebuild-20261021/tasks/mixed-completion/workspace/.claude/skills/do-math/`
- 인스턴스: `C:/math/.async/do-math-rebuild-20261021/tasks/mixed-completion/evidence/instance-add-zero-20261021/`
- 목표 원문: [goal.md](evidence/preparation/goal.md)
- 설정 원문: [settings.json](evidence/preparation/settings.json)
- 도구 판본 확인: [versions.json](evidence/preparation/versions.json)
- 기동 반환: [launch.json](evidence/launch.json)
- 기동 후 조회: [status-after-start.json](evidence/status-after-start.json)

목표는 0을 포함한 모든 자연수 n의 n + 0 = n을 Lean으로 증명하고 충실한 사람이 읽을 해설을 작성하는 것이다. `max_sessions=2`, 계획·연구 기본값은 `codex/gpt-6.1-sol`/`high`, 검토는 `claude/sonnet`/`high`로 선택했다. core Lean 직접 호출이며 Mathlib을 요구하지 않았다. 이는 실행 선택이고 사용자 수학 목표에 덧붙인 연구 전략이 아니다.

`git -C C:/math check-ignore .async/do-math-rebuild-20261021/tasks/mixed-completion/evidence/instance-add-zero-20261021`이 해당 경로를 반환했다. 인스턴스 자체 `.git/`은 init이 생성한다.

## 실제 명령과 기동 확인

다음 명령의 작업 폴더는 위 workspace다.

```powershell
python -B .claude/skills/do-math/runner.py init C:/math/.async/do-math-rebuild-20261021/tasks/mixed-completion/evidence/instance-add-zero-20261021 --goal C:/math/.async/do-math-rebuild-20261021/tasks/mixed-completion/evidence/preparation/goal.md --settings C:/math/.async/do-math-rebuild-20261021/tasks/mixed-completion/evidence/preparation/settings.json
python -B .claude/skills/do-math/runner.py start C:/math/.async/do-math-rebuild-20261021/tasks/mixed-completion/evidence/instance-add-zero-20261021
python -B .claude/skills/do-math/runner.py status C:/math/.async/do-math-rebuild-20261021/tasks/mixed-completion/evidence/instance-add-zero-20261021
```

`init`과 `start`는 각각 종료 코드 0이었다. 반환 PID는 11444, 이번 기동 토큰은 `62d416f687b54afa94c78aa73b41a7a7`다. `runner/start-62d416f687b54afa94c78aa73b41a7a7.stdout.log`의 started 기록과 토큰·PID가 일치했고 status의 runner_alive=true를 확인했다. 새 stderr 경로는 같은 접두의 `.stderr.log`다. start 호출이 반환한 뒤 별도 status 호출에서도 계획 CLI가 살아 실행되고 있음을 확인했다.

이후 상태와 공개 지식을 읽기 전용으로 관찰했다. 첫 시도에서 발견한 결함과 수정 후 결과를 구분해 기록한다.

## 첫 실행에서 발견한 저장 결함과 수정

첫 인스턴스는 계획·연구 두 기록을 공개하고 Claude 검토까지 수행했지만 실행기가 상태 교체에서 종료했다. 원 오류는 `instance-add-zero-20261021/runner/start-62d416f687b54afa94c78aa73b41a7a7.stderr.log`에 있다. `state.json.<uuid>.tmp -> state.json`의 `os.replace`가 `[WinError 5] 액세스가 거부되었습니다`를 냈다. status의 `running`은 마지막 저장 상태였으며 이후 조회에서 runner_alive=false, Claude 세션 exit.json의 종료 코드 0을 확인했다. 이 실행은 무인 완료 근거로 세지 않는다.

Windows에서 대상 파일을 `open('rb')`로 열어 둔 작은 재현에서도 os.replace가 접근/공유 거부를 냈다. 실제 실행에서 파일을 잡고 있던 독자까지 특정한 것은 아니며, 이 오류 형태를 재현한 것이다. 주기적 상태 저장은 status나 계획의 읽기와 겹칠 수 있다. reader를 배제하거나 구조를 바꾸는 대신 `runner.py:write_json`에서 Windows 오류 5/32/33만 같은 원자 교체를 50ms 간격으로 최대 1초 재시도한다. 이전 상태는 완전한 파일로 유지한다. 계속된 거부나 다른 오류는 호출자에 그대로 전파한다. 세션 시간 상한, 수학 검사, 새 감독 프로세스는 추가하지 않았다.

검증 명령: `python -B -m unittest discover -s .claude/skills/do-math/tests -p test_state_write.py -v`. 2개 시험이 0.187초에 통과했다. 실제 Windows 열린 파일의 교체 실패와 해제 뒤 새 상태 저장, 계속된 거부의 오류 전파·이전 상태 보존을 확인했다. 기존 가짜 흐름 시험 전체는 반복하지 않았다.

첫 인스턴스에는 운영 명령 `runner.py stop <첫 인스턴스>`를 적용했다. [failed-instance-status.json](evidence/failed-instance-status.json)에 STOP과 꺼진 실행기를 보존했다. 세 세션의 호스트/CLI 모두 종료한 것을 OS 식별 조회로 확인했다. 상태와 산출은 수동 편집하지 않았고 해당 인스턴스를 재시작하지 않았다.

## 수정 후 새 인스턴스

최종 완주 대상은 `C:/math/.async/do-math-rebuild-20261021/tasks/mixed-completion/evidence/instance-add-zero-fixed-20261021/`이다. 위와 동일한 준비 goal.md/settings.json을 사용해 새 init 및 start를 수행했다. 명령은 앞 절의 인스턴스 인자만 `instance-add-zero-fixed-20261021`로 바꾼 것이다. 실제 기동 반환은 [launch-fixed.json](evidence/launch-fixed.json), 기동 후 조회는 [status-fixed-after-start.json](evidence/status-fixed-after-start.json)이다.

PID 18568, 토큰 `7b764091fefa4b3486b0b6d5da51d1dc`의 새 stdout started 기록과 runner_alive=true를 확인했다. stdout/stderr는 이 인스턴스의 `runner/start-7b764091fefa4b3486b0b6d5da51d1dc.stdout.log` 및 `.stderr.log`다. 새 연구에는 입력 추가, 수동 산출 편집, 세션 재실행을 하지 않는다.

## 제출 형식 확인

`python C:/math/services/async-development/check.py report C:/math/.async/do-math-rebuild-20261021 mixed-completion`을 직접 실행해 `PASS report`를 확인했다. 이는 보고 필드·실제 변경 경로의 검사이며 수학적 달성 근거는 앞의 공개 결과와 검토다.
