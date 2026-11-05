---
유형: 기각보관
출처: do-math
라운드: 1
항목: 2
---

# 기각 보관 — do-math 라운드1

## R1-03

### 원문
제목: 루트가 형식 해결된 뒤에도 실행기가 형식화 파이프라인을 상한 없이 다시 만들어 형식화가 막힌 노드가 하나라도 있으면 실행기가 끝나지 않는다

### 위치
- `.claude/skills/do-math/runtime/runner.py` 462~470행(`populate`의 형식화 생성 고리): `informal_proved`·`informal_refuted`인 노드에 진행 중인 형식화 파이프라인이 없고 `formal_ready`인 증명이 있으면, `state['complete']`와 관계없이 새 형식화 파이프라인을 만듭니다.
- 같은 파일 539~542행(`schedule`): `populate()`를 루트 완료 검사보다 먼저 부릅니다.
- 같은 파일 637~638행(`tick`): `finished`는 대기·실행 중인 작업이 하나도 없어야 참이 됩니다.
- 이 동작을 설명하는 문서는 `.claude/skills/do-math/reference/operations.md` 75행, `.claude/skills/do-math/reference/common.md` 133행, `.claude/skills/do-math/SKILL.md` 38행입니다.

### 기준
.claude/skills/do-math/reference/common.md 133행:

```
Once review validates a formal solution of the root, the runner stops launching attempts and explorations. Existing sessions retain their normal scope, and peer, review, formalizer and organizer work continues as its inputs become ready. The runner finishes after this remaining processing ends.
```

.claude/skills/do-math/reference/operations.md 75행:

```
A formal root and a finished runner are different states: after formal completion, new attempts and explorations stop, while existing sessions continue and the runner still prepares their peer and review stages, ready formalizations and due organization batches.
```

.claude/skills/do-math/SKILL.md 38행·46행:

```
The runner stops launching attempts and explorations when the root has an accepted formal solution, and continues remaining sessions and eligible follow-ups until finished. Existing sessions retain their normal scope.
```

```
When reporting completion, distinguish formal settlement of the root from the runner finishing its remaining work.
```

.claude/skills/do-math/reference/lean.md 211행:

```
The broker exits on its own when the instance has finished its sessions and follow-ups, no session is active, and no compile job is queued or running. A formal root alone does not end its service while follow-ups remain.
```

### 영향
#### 재현 경로

1. 루트가 `formal_proved`가 되어 `state['complete']`가 참이 됩니다.
2. 이와 별개로 노드 X가 `informal_proved`이고, 그 증명의 `formal_dependencies`가 비어 있거나 모두 형식 해결되어 있어 `formal_ready`가 참입니다.
3. X의 형식화 파이프라인(formalizer → peer → review)이 형식 해결 없이 끝납니다. 부분 기록으로 게시되거나 배제 판정으로 끝나는 경우입니다.
4. 다음 `tick`의 `schedule` → `populate`가 X에 진행 중인 형식화가 없음을 보고 곧바로 새 형식화 파이프라인을 만듭니다(runner.py 465~470행). `dispatch_pending`은 완료 뒤에 attempt·explore만 취소하므로(497~502행) 이 형식화는 파견됩니다.
5. 같은 일이 X가 형식 해결되거나 비형식 해결 상태를 잃을 때까지 반복됩니다. 그동안 `remaining`이 참이라 `finished`는 거짓으로 남습니다. 브로커도 lean.md 211행의 규칙대로 종료하지 않습니다.

#### 달라지는 것

운영자와 사용자는 common.md 133행의 "The runner finishes after this remaining processing ends"를 읽고 남은 처리가 유한하다고 기대합니다. 실제로는 사용 중인 Lean 환경에서 형식화가 막힌 노드가 하나만 있어도, 루트가 이미 해결된 뒤에 설정 기본값인 xhigh 세션이 형식화·peer·review 세 단계로 상한 없이 소비됩니다.

`stop`으로 새 파견을 막아도 이 상태는 끝나지 않습니다. `stop` 직전에 만들어진 형식화 작업이 `pending`으로 남아 `finished`가 계속 거짓이고, 실행기는 할 일 없이 살아 있습니다.

루트 완료 전에 상한 없이 반복하는 것은 기존 결정입니다. `test_formalization_has_no_round_cap`(tests/test_research.py 1036~1042행)이 그 결정을 고정합니다. 문제가 되는 것은 그 결정이 완료 뒤 기간에도 그대로 적용되는 결과입니다.

### 상신
#### 읽은 범위

지급 밖에서 연 파일은 두 개입니다. `기억/layer3/L-0020.md`(do-math 구현과 운영의 현행 노드)에서는 형식화·종료 관련 줄을 검색했고, 루트 완료 뒤 형식화를 계속할지 정한 결정은 없었습니다. `기억/layer1/M-0609.md`는 연구 지속 원칙을 담은 노드이고, 형식화 반복 횟수나 완료 뒤 범위에 관한 결정은 없었습니다.

추적한 개체는 세 가지입니다.

- 형식화 파이프라인 생성: 정의는 runner.py `populate`, 정본 문서는 operations.md 99행·common.md 45행, 결정은 시험 `test_formalization_has_no_round_cap`.
- 실행기 종료 상태 `finished`: 정의는 runner.py `tick`, 정본 문서는 operations.md 75행·common.md 133행.
- 루트 완료 상태 `complete`: 정의는 runner.py `tick`·`publish`, 정본 문서는 SKILL.md 38행·46행.

완료 뒤 형식화 범위를 정한 별도 결정 파일은 찾지 못했습니다.

#### 세계 물음

루트가 형식 해결되면 사용자는 결과 보고를 받습니다. 운영자는 `status`의 `finished`를 보고 실행이 끝났는지 판단합니다. 남은 형식화를 언제 그칠지는 이 행위자들이 결정하거나 조회할 수 있어야 합니다. 그런데 정의 파일에는 그런 개체가 없습니다. 설정(settings.py `defaults`)에는 완료 뒤 형식화 범위를 정하는 키가 없고, 실행기 상태(runner.py `initialize`)에는 `complete`·`finished`만 있습니다.

#### 선택지

- 갑. 현행 동작을 유지하고 문서만 바로잡습니다. operations.md 75행, common.md 133행, SKILL.md 38행에 다음을 적습니다. 완료 뒤에도 형식화 준비가 된 모든 비형식 노드에서 횟수 상한 없이 형식화가 계속되고, 그 노드들이 모두 형식 해결되거나 준비 상태를 잃기 전에는 실행기가 끝나지 않을 수 있다는 것입니다. 하류 영향: 코드와 시험은 바뀌지 않습니다. 완료 뒤 비용은 여전히 상한이 없고, 이를 끊는 운영 수단(`stop`)도 실행기를 끝내지 못합니다.
- 을. 루트가 형식 해결된 뒤에는 새 형식화 파이프라인을 만들지 않습니다. 이미 실행 중인 형식화와 그 peer·review는 끝까지 처리합니다. 고칠 곳은 넷입니다. runner.py `populate`의 형식화 생성 고리는 `state['complete']`일 때 건너뜁니다. `dispatch_pending`은 완료 뒤 아직 파견되지 않은 `pending` 형식화를 attempt·explore처럼 취소합니다. 세 문서의 "ready formalizations"·"formalizer ... work continues"를 이 범위로 고칩니다. 완료 뒤 실행기가 끝나는 시험을 하나 더합니다. 하류 영향: 완료 뒤 처리가 유한해지고 `finished`가 확실히 참이 됩니다. 그 대신 다른 노드의 비형식 해결은 형식 보증 없이 남습니다. 그 기록과 리뷰는 계속 공개되어 있습니다. 완료 전의 상한 없는 반복(`test_formalization_has_no_round_cap`)은 그대로입니다.
- 병. 완료 뒤 형식화를 계속할지를 새 설정 키로 운영자가 고르게 합니다. 하류 영향: settings.py의 키·검증·기본값, 문서 세 곳, 시험이 늘어납니다. 기본값을 갑과 을 중 무엇으로 둘지는 여전히 정해야 합니다.

#### 변형 물음

갑의 대가는 완료 뒤 비용에 상한이 없다는 점입니다. 이를 줄이려고 노드마다 완료 뒤 형식화를 한 번으로 제한하는 변형을 검토했습니다. 그러나 이 변형은 기존 결정인 "형식화에는 횟수 상한이 없다"(`test_formalization_has_no_round_cap`)와 같은 축에 새 상한을 들이므로 넣지 않았습니다. 을의 대가는 남은 노드의 형식 보증을 잃는다는 점입니다. 이를 줄이려면 형식화를 요청하는 운영자 명령이 필요한데, 현행 명령 목록(operations.md 81~93행)에 그런 명령이 없어 새 인터페이스를 만들어야 합니다. 그래서 선택지에 넣지 않았습니다. 병은 갑과 을 사이의 선택을 설정으로 미루는 변형이고, 그 자체로 위에 선택지로 적었습니다.

#### 추천

을을 추천합니다.

- 루트 완료 뒤 attempt·explore를 멈추는 현행 규칙(SKILL.md 38행)과 같은 근거, 곧 연구 질문이 해결됐다는 사실을 형식화의 새 출발에도 적용하는 것입니다.
- "The runner finishes after this remaining processing ends"라는 약속이 실제로 성립합니다.
- 완료 전의 상한 없는 형식화라는 기존 결정을 건드리지 않습니다.

지배 관계도 검사했습니다. 병은 결함을 해소하지 않은 채 설정 구조를 더합니다. 그 설정을 따로 소비할 곳이나 호환 계약은 찾지 못했으므로 병은 추천하지 않습니다.


### 판정
확정: 기각 · 승인기 [2, 3] · 기각기 [1] · 처분: 없음
최종 판정: 기각

### 근거
- 기 1: 관문 1에서 주장한 종료 약속 위반이 성립하지 않는다. 현재 원문은 남은 처리가 끝난 뒤 종료한다고 조건을 두며, 그 처리가 유한 시간 안에 끝난다고 보장하지 않는다. 완료 뒤 준비된 형식화의 지속은 문서에 이미 포함되어 있어 코드와도 일치한다. 형식화가 계속 실패할 때 비용이 상한 없이 들 수 있다는 관찰은 확인되지만, 이것만으로 현행 정본을 위반하는 결함이나 완료 뒤 새 형식화를 끊어야 할 미확정 요구가 확인되지는 않는다. 새 종료 정책에 대한 선호를 추정해 상신을 승인할 수 없다.

## R1-06

### 원문
제목: mcp_probe.py는 작업자 도구 배선을 확인하는 대역이라고 적혀 있지만 어느 시험이나 문서도 그것을 쓰지 않는다

### 위치
.claude/skills/do-math/runtime/tests/mcp_probe.py 1행(`"""A local, side-effect-free MCP tool for verifying explicit worker tool wiring."""`)과 파일 전체(1~20행).

`.claude/skills/do-math`, `.agents/skills/do-math`, `기억/`을 검색했다. 검색어는 `mcp_probe`, `do_math_probe`, `MCP_PROBE_OK`다. 결과에는 이 파일 자신과 그 생성 사본만 나왔다. git 이력에서 `MCP_PROBE_OK`를 담은 커밋은 기준선 커밋 0f46f493 하나뿐이다.

배선을 다루는 현행 시험은 .claude/skills/do-math/runtime/tests/test_context.py 139~172행과 174~188행이다. 이 시험들은 argv와 `worker-mcp.json`, `-c mcp_servers=` 재정의의 문면만 확인한다. 설정된 서버의 도구가 실제 작업자 세션에 닿는지는 확인하지 않는다.

### 기준
.claude/skills/do-math/reference/operations.md 48행:

```
Only explicitly configured external tools enter worker sessions. `mcp_servers` maps server names to configuration objects. A local server uses `command`, `args`, and optional `env`; an HTTP server uses `url` and the provider's supported transport configuration.
```

임시/do-math_검증_2026-11-05/동결.md 「불변식 목록」:

```
- 새 인스턴스를 위한 현재 여섯 역할과 운영 인터페이스를 유지하고, 결함 수리에 필요한 연결된 코드·문서·시험을 함께 고친다. 실제 실행 중인 연구 인스턴스는 이 검증의 편집 대상이 아니다.
```

임시/do-math_검증_2026-11-05/동결.md 「목적 진술」:

```
문서와 코드의 불일치, 데이터 보존·복구·동시 실행의 실제 실패, 시험이 놓친 동작을 검토한다.
```

### 영향
시험 디렉토리를 읽는 유지보수자는 설명문만 보고 작업자 도구 배선을 이 대역으로 검증한다고 믿게 된다. 그러나 실제로는 어떤 검사도 이 대역을 실행하지 않는다. 운영 문서 48행이 약속하는 "명시 설정한 도구만 작업자에 들어간다"는 동작에서 확인되는 것은 명령 문면까지다. 도구가 세션에 실제로 닿는지는 확인되지 않은 채 남는다. 이 파일은 `.agents` 생성 사본에도 그대로 복제되어 배포된다.

### 상신
#### 읽은 범위

추적 대상 개체는 `mcp_probe.py` 대역과 그것이 확인한다고 적은 "작업자 도구 배선"이다. 지급 밖에서 연 것은 다음과 같다.

- 정의: .claude/skills/do-math/runtime/launch.py 28~38행(`mcp_servers` 재정의와 `worker-mcp.json` 작성). 지급된 사본과 같은 원본에서 읽었다.
- 정본 문서: .claude/skills/do-math/reference/operations.md 48행, .claude/skills/do-math/SKILL.md 28행, .claude/skills/do-math/reference/tools.md 53행.
- 결정: 기억/layer3/L-0020.md(`probe`, `MCP` 검색 결과 84·194행)와 git 이력(`git log --all -S MCP_PROBE_OK`).

이 대역을 두기로 한 결정 문서나 그 사용 절차를 정한 결정은 찾지 못했다.

#### 세계 물음

이 세계에서 행위자는 scholarly-mcp 같은 도구를 `mcp_servers`에 설정하는 운영자다. 운영자는 그 도구가 새 인스턴스의 작업자에게 실제로 닿는지 알고 싶어 한다. 그 행위에 필요한 개체 가운데 설정의 정의(launch.py, operations.md 48행)는 있다. 반면 "배선 확인 절차"는 정의 파일에도 정본 문서에도 없다. tools.md 53행은 작업자가 도구를 쓸 수 없을 때 그 한계를 기록하라고만 정한다.

#### 선택지

- A. `mcp_probe.py`를 지운다(원본과 생성 사본 동기화 포함). 하류 영향: 잘못된 검증 약속이 사라진다. 배선 확인 수단은 지금과 마찬가지로 없다. 다른 시험과 문서에는 변경이 없다.
- B. 대역을 남기고 operations.md에 수동 실측 절차를 더한다. 이 절차는 `mcp_servers`에 이 프로브를 넣은 인스턴스에서 작업자가 `do_math_probe`를 불러 `MCP_PROBE_OK`를 받는지 확인한다. 하류 영향: 운영자에게 실제 배선 확인 수단이 생긴다. 대신 인증된 실제 CLI와 모델 비용이 드는 새 운영 절차가 생기고, 그 절차를 유지할 책임도 생긴다.
- C. 대역을 남기고 단위 시험을 더한다. 이 시험은 `worker_command`가 쓴 `worker-mcp.json`의 `command`·`args`로 프로브를 띄워 `initialize`, `tools/list`, `tools/call` 왕복을 확인한다. 하류 영향: 설정이 실행 가능한 서버를 가리킨다는 것까지는 확인된다. 그러나 CLI가 그 서버를 세션에 붙이는지는 여전히 확인되지 않는다. 결과적으로 대역 자신을 시험하는 순환 검사에 가깝다.

#### 변형 물음

B의 대가는 실제 CLI 비용과 새 절차의 유지다. 이 대가를 줄이는 변형이 있다. 절차를 상시 운영 단계로 두지 않고, 새 도구를 처음 설정할 때 한 번만 하는 선택 확인으로 operations.md의 `mcp_servers` 설명 옆에 한 문장으로 둔다. 이 변형을 B′로 선택지에 넣는다. C의 순환성을 없애는 변형은 단위 시험 범위 안에서 찾지 못했다. 실제 CLI 없이는 세션 부착을 관찰할 수 없기 때문이다.

#### 추천

A를 추천한다.

각 선택지를 승인한 뒤의 최종 상태를 비교하면 다음과 같다.

- A: 산출물에 거짓 약속이 남지 않는다. 시험 디렉토리의 모든 파일에 소비자가 있다.
- B′: 운영자에게 확인 수단을 주는 대신, 사용자가 정한 적 없는 실측 절차를 운영 인터페이스에 더한다.
- C: 결함(배선 미검증)을 남긴 채 대역을 위한 시험만 더한다.

지배 관계를 검사했다. C는 결함을 남기고 구조만 추가하는 선택지인데, C를 유지해야 할 독립 소비자나 호환 계약을 찾지 못했다. 그래서 C는 추천하지 않는다.

다만 사용자가 실제 CLI로 도구 배선을 확인하는 수단을 원한다면 B′가 그 목적을 가장 적은 비용으로 충족한다. 이 선호는 산출물과 기록에서 확인되지 않으므로 사용자의 결정으로 남긴다.


### 판정
확정: 기각 · 승인기 [] · 기각기 [1, 2, 3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 1: 관문 1에서 거짓 검증 약속이라는 지적이 확인되지 않는다. 프로브의 용도 설명은 현재 자동 시험이 그 프로브를 실행한다는 주장이 아니다. 사용 참조가 없다는 사실도 도구의 용도 설명을 거짓으로 만들지는 않는다. 실제 CLI 배선의 통합 검증 범위가 좁다는 관찰과 이 파일의 설명이 유지보수자를 속인다는 주장은 구별해야 한다. 항목이 추천한 삭제를 승인하려면 해당 설명 자체의 결함이나 프로브 보유 금지 기준이 확인되어야 하나 지급 원문에서는 확인되지 않는다.
- 기 2: 관문 1에서 지적이 읽은 대로 성립하지 않는다. 첫 줄은 프로브의 용도와 능력을 설명하며, 현행 자동 시험이 이 도구로 실제 세션 배선을 검증한다고 약속하지 않는다. 사용자가 없다는 사실로 그 설명을 거짓 검증 약속이라고 단정할 수 없다. 운영 계약의 실제 위반도 이 항목의 근거에서 확인되지 않는다.

또한 영향 칸은 도구가 실제 세션에 닿는지 확인되지 않는 상태를 손상으로 삼는다. 관문 8에서 추천 A는 프로브를 삭제할 뿐 그 미검증 상태를 없애지 않는다. 삭제와 실제 CLI 실측 중 무엇을 선호하는지를 묻기 전에, 주장한 결함과 그 수정·제거의 대응이 성립해야 한다. 이 항목의 상신 근거로는 부족하다.
- 기 3: 관문 1에서 지적의 핵심인 거짓 검증 약속이 성립하지 않는다. 어떤 시험도 이 도구를 사용하지 않는다는 사실과, 도구의 용도를 설명한 첫 문장이 실제 검증 수행을 약속한다는 주장은 다르다. 설명문에는 스위트가 이 도구를 실행한다거나 CLI 부착을 검증했다는 진술이 없다. 실제 세션 부착의 미검증을 별도 손상으로 읽더라도 추천 A의 파일 삭제는 그 미검증을 없애지 않는다. 확인된 잘못된 약속의 제거라는 전제가 서지 않아 관문 8의 추천 비교도 승인할 수 없다. 이 판정은 다른 결함이나 지급 밖 이력에 기대지 않았다.
