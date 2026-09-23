---
name: graphify
description: do-math 내부 문서·스크립트의 관계, 계약과 절차의 근거를 찾는 지식 그래프다. 에이전트가 do-math 작업 중 구조 탐색이 필요하다고 판단하거나 사용자가 graphify 조회·업데이트를 요청할 때 사용한다.
---

# do-math graphify

작업에 필요한 문서·스크립트·계약을 찾아 현재 원문으로 돌아가기 위한 지도다. 분석 범위는 저장소의 `.claude/skills/do-math/` 내부 파일이다. 테스트와 예제도 포함한다. 그래프에서 찾은 연결은 버그 여부나 계약 준수의 판정이 아니며, 연결이 없다는 사실만으로 불필요한 코드라고 판단하지 않는다.

Claude Code와 Codex는 모두 `.claude/skills/graphify/`의 지침·도구와 `.claude/graphify/do-math/`의 단일 상태를 사용한다. `.agents/skills/graphify/`는 생성 사본이다. 아래 명령은 저장소 루트에서 실행하며, 작업 디렉터리를 바꿔 호출할 때는 스크립트의 절대경로를 사용한다. 도구는 실행 위치와 무관하게 정본 do-math 경로를 선택한다.

## 필요할 때 조회

에이전트가 구조 탐색의 필요를 판단하여 조회한다. 모든 do-math 작업의 선행 단계로 강제하지 않는다. 사용자의 `/graphify` 호출에 조회 목적이 불명확하면 상태와 사용 가능한 명령을 안내한다. 경로만 주거나 인자가 없다는 이유로 새 그래프를 만들지 않는다.

```powershell
python .claude/skills/graphify/scripts/graph.py status
python .claude/skills/graphify/scripts/graph.py query "작업 계약 완료 의무"
python .claude/skills/graphify/scripts/graph.py query "contracts.py" --budget 4000
python .claude/skills/graphify/scripts/graph.py query "scripts_do_math_engine_researchengine_controls" --exact --relation calls
python .claude/skills/graphify/scripts/graph.py explain "계약/연구-수행.md"
python .claude/skills/graphify/scripts/graph.py path "SKILL.md" "계약/연구-수행.md"
python .claude/skills/graphify/scripts/graph.py affected "scripts/do_math/contracts.py"
```

조회 명령은 먼저 원본 파일의 내용 해시를 비교하고 `current`, `stale`, `missing` 상태와 추가·변경·삭제 목록을 표시한다. 그래프·캐시·답변을 저장하지 않으며 모델을 호출하지 않는다. `stale`이어도 위치를 찾는 데 사용할 수 있지만, 찾은 `source_file`과 `source_location`은 갱신 당시 좌표다. `.claude/skills/do-math/` 아래 현재 원문에서 해당 개념을 다시 찾아 판단 근거를 확인한다. 삭제된 파일은 현행 근거로 사용하지 않는다.

검색은 graphify의 문자열 매칭을 사용하므로 긴 자연어 질문보다 실제 파일명·함수명·문서 용어를 고른다. `query --exact`는 정확한 노드 ID 또는 파일 경로의 직접 관계만 반환하며, `--relation calls`처럼 관계 종류를 반복 지정해 좁힐 수 있다. 한국어와 영어 사이의 자동 의미 검색은 보장되지 않는다. 결과가 없거나 관계가 충분하지 않으면 원문을 직접 조사한다. 그래프가 없으면 원문으로 작업을 계속할 수 있으며, 명시적 업데이트 요청 없이 생성하지 않는다.

## 명시적인 업데이트

사용자가 graphify 업데이트·초기 구축을 명시적으로 요청했을 때 다음 명령을 실행한다. `/graphify update`와 `/graphify --update`는 이 명령으로 연결한다. 코드 수정, 커밋, 조회 자체는 갱신 권한이 아니다.

```powershell
python .claude/skills/graphify/scripts/graph.py update
```

동시 추출 수는 기본 3개이며 `--workers N`, 문서당 제한 시간은 기본 900초이며 `--timeout 초`로 바꾼다. 의미 추출은 **`codex exec`와 `gpt-6-sol`**을 사용한다. Claude Code에서 업데이트해도 동일하다. Codex CLI 로그인과 해당 모델 접근 권한이 필요하다. Python의 graphify 라이브러리도 필요하며, 이 구성의 검증 환경은 `graphifyy==0.9.48`이다. 누락되면 `python -m pip install graphifyy==0.9.48`으로 준비한다.

도구는 다음 순서로 갱신한다.

1. 내부 파일의 스냅샷과 해시를 확보한다. 생성 캐시와 외부로 이어지는 링크는 제외한다.
2. 새로 생기거나 바뀐 Markdown을 `codex exec -m gpt-6-sol`에 전달한다. 원문 해시·추출 지침·모델이 같은 유효한 추출은 재사용한다. [의미 추출 규격](references/semantic.md)에 따라 계약·절차의 개념과 관계를 추출한다.
3. Python과 Markdown의 구조를 graphify로 추출한다. 문서 의미와 함께 방향 및 복수 관계를 보존한 그래프를 구성한다. 그 밖의 파일은 목록 노드로 포함되며 내부 구조까지 분석한 것은 아니다.
4. 인용 행, 내부 경로, 관계 끝점과 실행 중 원본 변경 여부를 검사한다. 성공하면 현재 전체 파일 기준으로 그래프를 교체하므로 삭제된 파일의 노드도 사라진다. 커뮤니티 보고서와 탐색용 HTML을 생성한다.

중단: 문서 추출·검증이 실패하거나 원본이 실행 중 바뀌면 기존 그래프를 유지한다. 오류에 나온 실행 기록을 확인하고 문제를 해결한 뒤 업데이트를 명시적으로 다시 호출한다. 성공한 문서 추출은 캐시에 남는다. HTML 생성만 실패하면 이미 갱신된 JSON 그래프는 사용할 수 있으며 시각화 실패를 함께 보고한다.

중단: `update.lock`이 있으면 동시 갱신을 거절한다. 해당 PID의 작업이 종료됐는지 확인한 뒤에만 남은 잠금 파일을 제거한다. 실행 중인 갱신의 잠금을 제거하지 않는다.

## 산출물과 해석

산출물은 `.claude/graphify/do-math/` 아래에 있으며 Git에는 포함하지 않는 로컬 생성물이다.

| 경로 | 용도 |
|---|---|
| `graphify-out/graph.json` | 관계·방향·출처·추출 당시 파일 해시를 담은 그래프 |
| `graphify-out/GRAPH_REPORT.md` | 규모, 분석 범위와 커뮤니티 목록 |
| `graphify-out/graph.html` | 관계도. 5,000개 노드를 넘으면 커뮤니티 사이 연결로 집계 |
| `graphify-out/tree.html` | 파일과 기호를 펼쳐 보는 구조도 |
| `semantic/` | 문서별 의미 추출 캐시와 실제 사용량 |
| `runs/` | Codex 입력·응답·실행 인자·이벤트·오류 기록 |

`EXTRACTED`는 원문에 명시되거나 정적 구조에서 추출한 관계, `INFERRED`는 추론, `AMBIGUOUS`는 불확실한 관계다. 문서가 요구한 동작과 구현이 실제로 수행하는 동작은 원문·코드·필요한 실행 검증으로 대조한다. 내부 모듈명이 유일한 import, 명시적 import 별칭으로 찾은 내부 심볼, 선언된 상속 관계를 따라 찾은 `self`·`super()` 호출은 `INFERRED`로 표시한다. 외부 의존성의 내용은 분석하지 않는다. 내부 노드에 연결되지 않은 import 중 내부 모듈명이 없는 것은 JSON의 `graph.out_of_scope_imports`에, 외부에서 가져온 심볼과 내장 심볼은 `graph.out_of_scope_symbols`에, 나머지 연결되지 않은 구조 참조는 `graph.unresolved_references`에 남는다. 어느 쪽도 곧바로 결함 목록으로 해석하지 않는다.

완료 보고에는 파일·노드·관계 수와 의미 추출 성공 여부를 포함한다. 사용량은 실제 Codex 이벤트에서 읽으며, 확인하지 못한 값은 0으로 추정하지 않는다. graphify 일반 명령으로 루트 그래프를 만들거나 자동 훅·watch·답변 재수집을 설치하지 않는다.
