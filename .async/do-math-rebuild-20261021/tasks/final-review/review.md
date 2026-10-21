# 새 do-math 최종 독립 개발 검토

판정: **합격. 현재 배정의 완료 기준을 충족하며, 개발 완료를 막는 결함을 발견하지 않았다.** 검토 작업은 complete다. 제품 변경은 없다. 최종 완료 게시와 이 검토의 수용은 manager가 담당한다.

사용자가 승인한 기준은 새 구현·가짜 세션 흐름·실제 Codex와 Claude가 함께 참여하는 작은 목표의 무인 완주다. 이 기준을 어려운 연구의 장기 안정성이나 모든 운영 환경의 보증으로 확대하지 않았다. 파일 존재나 형식 통과만으로 합격한 것이 아니라, 사용자와 후속 세션의 실제 진입점에서 필요한 의미를 회수하고 코드 및 공개 연구 본문과 대조했다.

## 검토 대상과 읽기 경로

제품 기준 경로는 이 task의 [workspace/.claude/skills/do-math/](workspace/.claude/skills/do-math/)다. 아래 제품 파일명은 모두 이 경로 기준이다. 확정 요구는 [사용자 원문](../../user-messages.md)과 이 배정의 [context](inputs/context.md), [plan](inputs/plan.md), [seams](inputs/seams.md)를 읽었다. [objective.md](objective.md), [task.json](task.json), `C:/math/services/async-development/protocol.md`의 review·보고 절차도 적용했다. 기존 do-math 코드나 Git 이력을 설계 기준으로 사용하지 않았다.

직접 따라 읽은 소비자 경로는 다음과 같다.

1. 사용자 대화: `SKILL.md` → `RUNTIME.md`의 준비·기동·상태·운영 → `protocol.md`의 설정·산출 계약 및 `CLI.md` → `runner.py`, `cli_adapter.py`, `check.py`의 실제 정의.
2. 실행 세션: 최종 실제 인스턴스의 다섯 `sessions/<ID>/input.json`과 `prompt.txt` → common/protocol/goal → 해당 범주의 plan/research/review 문서 → task의 사건·지시·대상. 이때 연결된 문서 내용은 현재 검토 workspace의 제품으로 읽었다.
3. 수학 결과: 최종 인스턴스의 goal/settings → 공개 연구 output → 해설·Lean·컴파일 기록 → 독립 연구 검토 → 다음 계획 → 목표 검토와 공개 보조 근거. 작성자 비공개 로그로 수학적 근거를 보충하지 않았다.
4. 실행 근거: [mixed-completion/evidence.md](../mixed-completion/evidence.md) → final-status/session-evidence/git-evidence → 실제 input/prompt 및 새 기동 로그. [runner/report.json](../runner/report.json), [CLI 조사](../cli-discovery/cli-evidence.md), [mixed-completion/report.json](../mixed-completion/report.json), [manager 0008 판단](../../managers/0008/decision.md)을 읽고 관련 코드·시험·diff와 대조했다.

## 목적과 확정 조건별 판정

| 요구 | 실제 내용과 판단 |
|---|---|
| 대화 없이 지속 연구 | `SKILL.md`가 목표·조건과 설정 준비, 자체 Git 인스턴스 init, 독립 start, 새 token/PID/로그·status 확인, 위치 반환까지 설명한다. `runner.py:initialize/start/Runner.run`과 일치한다. 시작 명령 반환 뒤 계획→연구→검토→계획→목표 검토로 진행한 실제 근거가 있다. |
| 지식 축적·환류 | `common.md`, `research.md`, `protocol.md`는 결과뿐 아니라 failed_attempts와 open_questions, 확인 범위와 한계를 공개하게 한다. `plan.md`는 실패한 접근과 부분 결과를 다음 과제에 사용하고 같은 시도를 반복할 때 달라지는 점을 설명하게 한다. `Runner.finish/apply_output`이 실패와 끝난 검토를 계획 사건으로 연결한다. |
| 사람이 읽는 해설이 주 산출물 | `research.md`는 정의·가정·주장·논증·목표와의 관계·실제 확인을 본문에 쓰게 하며 계산/문헌/Lean의 근거 전달을 각각 설명한다. 실제 exposition.md는 Nat의 0 포함, 전칭 명제, 덧셈 정의, 정의적 계산과 반사성, 실행 방법과 한계를 전달한다. |
| 독립 검토와 세 판단의 분리 | `review.md`는 공개 원문 사본의 Lean 재컴파일, 해설과 Lean의 대응, 별도의 목표 판정을 구분한다. `check.py:Checker.review`는 연구 결과마다 assessment/lean/alignment와 이유를 요구하고 목표에는 goal 판정을 요구한다. 실행기는 목표 achieved만 완료 신호로 쓴다. 실제 두 검토는 별도 Claude 세션이며 공개 원문을 바탕으로 근거를 남겼다. |
| 사용자 권한과 세션 재량 | `SKILL.md/common.md/plan.md`는 사용자 목표·필수조건·허가와 AI의 연구 방법·과제 분해를 구분한다. 방법 선택마다 새 승인을 요구하지 않으며 필요한 외부 입력만 wait로 보낸다. 학술 후속은 범위 밖으로 유지한다. |
| 세 층 작업맥락 | `Runner.dispatch`와 실제 input/prompt에 common.md·protocol.md·goal.md, 범주 문서, task가 구분돼 전달된다. 모든 세션에 자기 폴더·공개 지식·설정·공식 검사 argv가 있다. 계획에만 RUNTIME/state의 미완료 요청 읽기 안내가 추가된다. |
| 세션이 검사하고 실행기도 같은 검사 | `common.md`가 직접 `check.py <session-dir>` 실행, 오류 수정, 자기 판단 후 종료를 지시한다. 실제 다섯 세션에 호출·성공 근거가 있다. `check.py:main`과 `Runner.finish`의 `check_session`은 동일한 `Checker.run`을 사용한다. 실행기의 재검사는 별도 로그 존재가 아니라 이 코드 경로와 integrated·공개 기록·커밋을 함께 대조해 판단했다. |
| 검사 범위는 구조·참조 실재 | `check.py` 전체를 읽었다. 필수 구조, category/target, 실제 파일·기록·결과, 연구 검토 항목 완결성을 검사한다. Lean 실행, 수학 판정, 현재성·대체 충돌 판정, Markdown 의미 판단은 없다. output 링크 거부는 복사 가능한 공개 자료를 위한 전달 조건이다. |
| 현재 환경과 평범한 파일·Git | 코드에 설치 해시 봉인·판본 불일치 차단·감시 예약 작업은 없다. Lean 명령과 version 문자열은 세션이 사용·기록한다. PID 생성 식별값은 프로세스 재사용 구분용이고 단일 실행기 잠금은 필수 불변식용이다. 목표 검토가 사본 동일성을 설명하려고 기록한 SHA-256은 일회성 세션 판단이며 실행기 봉인 조건이 아니다. |
| 두 CLI와 모델 지정 | `cli_adapter.py:provider_for_model/build_command`는 명시적 codex/claude 접두로 공급자를 고르고 뒤 전체를 모델에 전달한다. `Runner.dispatch`는 범주 기본값에 요청의 model/effort만 덮어쓴다. 자동 검토·계획은 기본값이다. 실제 Codex gpt-6.1-sol/high와 Claude sonnet/high 실행이 있다. |
| 한도에서는 전체 파견 대기 | `detect_usage_limit`은 공급자 거절 표식만 읽고 명확한 미래 reset 또는 설정 간격을 반환한다. 중복 키·모르는 출력·정상 인용으로 산출을 거부하지 않는다. `Runner.finish/blocked/tick`이 한도를 다른 파견 조건과 분리하고 종료 산출은 계속 검사한다. 실측 한도 발생은 완료 근거에 포함하지 않았다. |

공개 지식 읽기 규칙도 소비자 본문에 충분히 남아 있다. `common.md/protocol.md`는 공개됐다는 사실과 수학적 인정을 구분하고, 전체 기록 대체의 끝에서 본문을 읽되 가지가 갈라지면 양쪽을 읽게 한다. 기존 검토를 새 연구에 승계하지 않고 상충 검토가 있는 결과는 인정된 전제로 쓰지 않는다. `research.md`는 부분 수정이어도 유지할 내용을 포함한 전체 대체 산출을 내게 한다. 이 해석과 동시 대체 회피는 계획의 책임이며 실행기가 새 충돌 판정 체계를 만들지 않았다.

계획의 후속 판단 경로도 링크만 있는 상태가 아니다. `plan.md`와 `RUNTIME.md`에 pending/assigned의 의미, requests.task/origin/selection/status/session/record, 실패 사건의 sessions[ID].request→requests.task/origin 경로가 본문으로 설명된다. 실패 계획의 request가 null이면 원 input.json.task.events를 회수한다. `Runner.dispatch`가 이 문서와 상태 경로를 실제 계획 프롬프트에 넣는다. 사용자는 SKILL의 상태 표와 운영 명령으로 STOP·입력·한도·완료를 구분하고, 꺼진 실행기에 start가 필요한 경우 및 CLI 하나를 종료하는 방법을 알 수 있다.

## 열 가지 불변식과 코드 대조

| 번호 | 관련 정의와 확인 |
|---|---|
| 1. 정해진 흐름 | `initialize`의 start 사건, `Runner.apply_output`의 계획 게시·연구 자동 검토·review_finished·goal achieved, `tick`의 파견 순서가 확정 흐름과 일치한다. |
| 2. 새 세션·검토 입력 | `dispatch/session_host/build_command`가 매번 새 디렉터리와 프로세스를 쓰며 resume/continue를 쓰지 않는다. 실제 두 검토 input/prompt에는 작성자 세션 위치나 로그가 없고 자기 세션과 공개 대상만 있다. 이는 전달·지시 규칙이며 OS 읽기 격리 주장은 없다. |
| 3. 자기 폴더·새 공개 기록·Git | common과 prompt의 쓰기 범위 지시, `finish`의 output 전체 copytree→새 knowledge 디렉터리 rename→Publish 커밋을 확인했다. input/work/log는 복사 대상이 아니다. 기존 공개 기록을 덮어쓰지 않는다. |
| 4. 반영 전 공식 재검사 | `finish`는 check_session의 오류가 있으면 failed 및 session_failed로 저장하고 복사하지 않는다. 통과 뒤 publishing으로 들어간다. |
| 5. 전체 동시 상한 | `active`가 starting/running/publishing을 세고 `tick`이 max_sessions에서 뺀 슬롯만 파견한다. 계획은 active plan이 없을 때 하나만 파견한다. |
| 6. 단일 실행기 | `Runner.run`의 InstanceLock 안에서 상태를 다시 읽고 실행한다. Windows byte lock/Linux flock은 프로세스 종료 시 해제되며 파일 삭제를 요구하지 않는다. |
| 7. 프로세스 종료·같은 검사·재파견 없음 | `session_host`는 CLI 핸들을 기다리고 `collect`는 기록된 host/CLI 생존을 확인한다. 종료 방식·코드와 관계없이 finish로 간다. assigned/finished/failed 요청은 pending으로 되돌리지 않는다. 재시도는 새 계획의 새 요청이다. |
| 8. STOP과 사용자 입력 | `tick`은 collect/ingest_inputs를 먼저 하고 blocked를 확인한다. STOP 동안 기존 산출 처리를 계속하며 사용자 원문을 events로 보존한다. input 파일은 고유 이름으로 보존한다. |
| 9. 완료·외부 입력 대기 | complete/wait는 별도 차단이다. 사용자 입력이 wait를 풀고 complete는 풀지 않는다. 완료 후에도 collect를 계속하며 active가 없어질 때 run이 끝난다. 계획 도중 들어온 미전달 입력을 오래된 wait가 막지 않도록 apply_output이 처리한다. |
| 10. 공급자 한도 | `finish`가 종료 로그의 한도만 읽어 limit_until을 설정한다. `blocked`는 모든 새 파견을 막는다. 한도 만료는 STOP/wait/complete에 영향을 주지 않는다. 로그 읽기 OSError는 log_error로 남겨도 공식 재검사로 진행한다. |

세션 실행 시간 상한은 없다. start의 10초 확인과 write_json의 1초 재시도는 각각 기동 확인·상태 저장의 동작이며 연구 세션 시간 제한이 아니다. `kill-session`은 최신 process.json의 PID와 생성 식별값을 같은 OS 핸들로 확인해 CLI 하나를 종료한다. 자손 전체 종료를 보장한다고 쓰지 않는다. 재기동의 미완료 배정·공개 복구는 저장된 요청 및 기록 ID와 단일 실행기 조건으로 처리하며 자동 재기동 서비스는 없다.

## 실제 혼합 완주의 내용 판단

최종 인스턴스는 [instance-add-zero-fixed-20261021](../mixed-completion/evidence/instance-add-zero-fixed-20261021/)이다. 아래 경로는 이 인스턴스 기준이다. 실패한 첫 인스턴스는 완료 근거로 세지 않았다.

`goal.md`는 “모든 자연수 n의 n + 0 = n을 Lean으로 증명하고 충실한 사람이 읽을 해설을 작성”, “자연수에 0 포함”을 요구한다. `settings.json`은 max_sessions=2, 계획/연구 Codex gpt-6.1-sol/high, 검토 Claude sonnet/high, 설치된 core Lean 직접 호출이다. 해당 목표에 Mathlib이나 여러 Lean 판본을 추가로 요구하지 않는다.

| 공개 기록 | 직접 읽은 내용과 결론 |
|---|---|
| `knowledge/k3812dd40113a4425b0b901de60dfd0bc/` | output.json, exposition.md, Proof.lean, lean-verification.json. 정리는 `theorem add_zero_all (n : Nat) : n + 0 = n := by rfl` 한 줄이다. 임의의 n이며 0을 포함하고 추가 가정·sorry·공리 선언이 없다. 해설은 Nat.add의 오른쪽 인자 재귀식에서 n+0이 n으로 계산되고 반사성으로 닫히는 이유를 설명한다. 유한 표본 계산을 전칭 증명으로 확대하지 않는다. 실제 version/compile argv·cwd·env·종료 코드 0·빈 진단이 공개돼 있다. |
| `knowledge/kf5af23be4e1b4e0588de16f547142351/` | output.json과 review-notes.md. target이 위 연구 전체를 가리키고 유일한 add_zero_all을 supported/accepted/matches로 각각 판단한다. 공개 원문의 자기 작업 사본 재컴파일, 타입·증명항·공리 의존 확인, Prelude의 인용 정의 대조와 한계를 기술한다. 작성자 폴더의 자료를 근거로 채우지 않는다. 보조 Audit 작업 파일 자체는 비공개지만 동일 정리에 붙인 명령과 결과가 본문에 있어 필수 근거를 회수할 수 있다. |
| `knowledge/k886da92b6d4f49a8a83840b838feff00/output.json` | 검토 결과와 목표를 대조하고 미완료 요청이 없음을 확인한 뒤 goal_review 하나를 요청한다. OfNat 설명 생략·한 판본 확인을 목표 미달성으로 확대하지 않고 별도 목표 검토에 판단하도록 전달한다. 계획 자체가 완료를 선언하지 않는다. |
| `knowledge/kc7325f0829e84ab5ab14fdfd5938ca33/` | output.json, goal-review-notes.md, lean-recheck.json, lean/Audit.lean, lean/Control.lean. 공개 원문 사본의 재컴파일 성공과 목표의 각 조건을 연결해 achieved를 내린다. Audit의 타입·증명항·공리 확인 출력과 원문이 대응한다. Control의 0+n=rfl 실패는 의도한 음성 대조이며 목표 정리 실패가 아니다. 대체·상충 검토·결론에 영향을 주는 열린 질문이 없다는 판단은 공개 목록과 일치한다. |

해설의 `OfNat` 리터럴 해석 생략은 Nat과 0의 의미 및 Nat.add 계산 논증을 왜곡하지 않는다. 사람이 읽을 증명 해설을 충족하며 해당 구현 표기까지 더 풀어 쓰는 것은 선택적 보완이다. 연구·검토가 사용한 판본은 `Lean (version 4.32.0, x86_64-w64-windows-gnu, commit 8c9756b28d64dab099da31a4c09229a9e6a2ef35, Release)`로 일치한다. 다른 판본 미확인은 기록돼 있고 사용자 목표가 요구한 추가 조건이 아니다. 그러므로 achieved의 근거가 충분하다.

실제 실행의 확인은 [session-evidence.json](../mixed-completion/evidence/session-evidence.json), [final-status.json](../mixed-completion/evidence/final-status.json), [git-evidence.txt](../mixed-completion/evidence/git-evidence.txt)을 사용했다.

| 세션 | 역할·공급자 | 공식 검사 성공 발췌 행 | 공개 기록 |
|---|---|---|---|
| s742ec928bdcf45ca9de8dc319f48eb2f | 첫 계획·Codex | 16 | kb6b5f6071b954b05979968472814f8e9 |
| s64441e372131443796865caff9e7b1ef | 연구·Codex | 28 | k3812dd40113a4425b0b901de60dfd0bc |
| sdd6fb4ae8326435b91e5c0d4047f91de | 연구 검토·Claude | 45→46 | kf5af23be4e1b4e0588de16f547142351 |
| sd268523d1f2344cf8cee2a3dac5de1e5 | 다음 계획·Codex | 24 | k886da92b6d4f49a8a83840b838feff00 |
| s44423f00d3434963b5caf6bcb823ea70 | 목표 검토·Claude | 63→64 | kc7325f0829e84ab5ab14fdfd5938ca33 |

행 번호는 원 CLI stdout의 위치로, 이번 review가 새로 모델을 실행한 기록이 아니다. 발췌에 실제 공식 검사 명령과 `ok:true/errors:[]`, Codex 종료 코드 0 또는 Claude tool 응답의 exit=0가 있다. launch argv는 공급자 접두를 제거한 모델을 사용하며 두 Claude의 init 모델은 claude-sonnet-5-5로 기록돼 있다. 다섯 input/prompt 원문도 직접 읽어 사건과 공개 대상의 연결을 확인했다.

final-status는 complete가 위 목표 검토 ID, 다섯 세션 모두 integrated, runner_alive=false, wait=null, limit_until=0, seen_inputs=[]다. session-evidence에는 각 CLI·host 생존 false가 있다. 완료 뒤 목표 검토의 review_finished 사건이 남아 있는 것은 새 계획을 띄우지 않는 완료 의미와 일치한다. Git 발췌는 초기화 1건과 공개 5건의 6커밋, 깨끗한 작업 트리이며 HEAD 48d393477ea673e563abe868487425421d11a9ac가 목표 검토 반영이다.

launch-fixed.json의 PID 18568과 실제 새 stdout의 started PID/birth/token `7b764091fefa4b3486b0b6d5da51d1dc`가 일치하고 정상 명령 종료 JSON도 있다. 해당 stderr는 비어 있다. 추가 입력·수동 산출 편집·재기동 없이 완주했다는 사실은 task의 명시적 보고와 이 일관된 실행 근거 범위에서 수용했다. seen_inputs=[]만으로 모든 사람의 행동을 입증했다고 해석하지 않았다.

## 가짜 흐름 및 Windows 수정의 근거

`tests/test_runner.py`와 `tests/test_cli_adapter.py`를 읽고 runner 보고의 확인 범위와 대조했다. 보고된 runner 6개 시험은 실제 가짜 CLI 프로세스·공식 검사기·임시 Git으로 5세션 완주, 종료 코드 7 연구의 정상 산출 반영, 추가 output 파일 공개, 모델/노력 부분 덮어쓰기, STOP·합성 한도·실패·wait·입력, 살아 있는 CLI 복구 및 완료 뒤 기존 산출 반영, 중복 커밋 방지, 잠금, 독립 기동을 확인한다. Adapter 8개 시험은 양 CLI 명령과 근거 기반 합성 한도·정상 인용·잘린 로그·중복 키를 다룬다. 제품 맥락 문서 대신 임시 문서를 사용한 시험이라는 한계를 유지한다. 이번 review가 이 시험들을 반복 실행하지 않았다.

한도 신호의 근거는 CLI 조사에 있는 설치 help·동일 버전 Codex 공식 소스·Claude 설치 구현의 출력 경로다. 제품의 Codex 오류 이벤트/Claude 최상위 usage_limit_reached 표식, 명확한 시각만 채택하고 나머지는 fallback으로 처리하는 선택이 그 근거와 맞는다. Claude typed 필드의 internal 성격, 특수 overage·Codex 날짜 생략의 불확실성은 CLI.md에도 남아 있다. 합성 검사를 실제 계정 한도 관측으로 기술하지 않았다.

mixed-completion의 base/workspace에서 runner.py와 RUNTIME.md의 diff를 직접 산출해 읽었고 현재 review workspace와 해당 결과의 바이트 일치도 확인했다. 새 tests/test_state_write.py 전체를 읽었다. 변경은 `runner.py:write_json`의 flush/fsync 후 os.replace에 Windows 오류 5/32/33만 최대 약 1초, 50ms 간격으로 재시도하는 부분과 운영 설명·두 시험이다. 교체 성공 전 이전의 완전한 JSON을 유지하고 지속 거부 및 다른 오류는 전파한다. 세션 시간 상한이나 감독 장치를 추가하지 않았다.

첫 인스턴스의 실제 stderr는 state.json 임시 파일 교체의 WinError 5다. 당시 어느 독자가 파일을 잡았는지는 특정되지 않았다. `test_reader_releases_old_state`는 Windows에서 실제 파일을 열어 교체 거부를 재현하고 해제 뒤 저장을, `test_persistent_denial_remains_an_error`는 지속 거부와 이전 상태 보존을 확인한다. 두 시험 통과는 mixed-completion 보고의 근거로 수용했다. 이 수정은 관찰된 사용 결함에 맞는 작은 변경이며 수정 후 별도 새 인스턴스의 무인 완주까지 있다.

## 남은 문제와 확인 한계

완료를 막는 결함: **없음**. 추가 수정 task를 필수로 배정할 근거를 발견하지 않았다.

선택적 보완: 실제 연구 exposition.md에 `OfNat`의 표기 해석을 한 문장 덧붙이면 Lean 구현을 더 자세히 알고 싶은 독자에게 도움이 될 수 있다. 공개 검토가 이미 그 의미와 영향을 설명하고 있으며 현재 목표 달성이나 제품 사용을 막지 않는다. 공개 기록을 수정하라는 요청은 아니다.

이번 검토는 제품 코드·문서·시험 코드·수용된 실행 근거의 정적 대조다. 새로운 모델 연구, Lean 재컴파일, 제품 단위시험, 실제 한도 유도는 수행하지 않았다. Linux, 호스트 재부팅, 실제 공급자 한도, 어려운 문제의 장기 연구, 다른 Lean 판본 및 모든 설정 조합은 미확인이다. 이는 승인된 완료 기준을 충족하지 못한 항목이 아니라 해당 기준 밖의 한계다.

보고서 검사는 `python C:/math/services/async-development/check.py report C:/math/.async/do-math-rebuild-20261021 final-review`로 직접 수행해 종료 코드 0과 `PASS report`를 확인했고 report.json의 verification에 기록했다. 이 형식 검사는 위 내용 판단을 대신하지 않는다. 제품, canonical source_repo, 다른 task 파일, 그래프, .agents 사본은 변경하지 않았다.
