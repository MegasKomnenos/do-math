# 라운드 3 — 「사용자에게 올린다」로 확정된 항목

항목의 원문(심사 대상에 실린 그대로)과 심사자 셋의 판정 절이다. 이 파일은 런의 중간물이며 수리자, 병합자, 심사자에게 주지 않는다. 종료 보고의 상신문은 이것을 재료로 쓴다.

## R3-44
제목: 저자의 `orcid`·`github` 칸은 설정이 받아들이고 운영자 문서가 적어 두었으나 어디에도 쓰이지 않는다

### 위치
`.claude/skills/do-math/runtime/finalize.py` 93행과 95행(`load_config`가 두 키를 받아들임), `.claude/skills/do-math/reference/operations.md` 472행(설정 표의 `authors` 행이 두 키를 든다). 두 키를 읽는 코드는 없다. `finalize.py` 1617~1618행은 표제 쪽에 `name`, `address`, `email`만 넘기고, `.claude/skills/do-math/runtime/package.py` 946행은 `formalization.yaml`에 이름만 쓰며, `package.py` 1415~1416행은 README에 이름만 쓴다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 134행:

```
넷째는 세 갈래를 가로지르는 손상이다. 이번 주에 걷어 낸 기능의 잔재, 쓰이지 않는 코드와 인자, 코드나 시험이 한 규칙을 두 군데에 따로 구현한 것과 그 둘 사이의 어긋남, 앞 상태를 서술하는 주석과 문서, 이 기계에만 맞는 경로와 수치가 여기에 든다. 가이드 안의 되풀이는 여기에 들지 않고 둘째 갈래가 정한다.
```

`.claude/skills/do-math/reference/operations.md` 472행:

```
| `authors` | `[]` | A list of objects with `name` and optionally `address`, `email`, `orcid`, `github`. An empty list means that no author is named anywhere: the paper has no author line and no file of the package names an author. |
```

`.skill-workspace/finalize-pipeline/agreement.md` 28행:

```
- What is not used is deleted.
```

`임시/do-math_검증_20261125-2/동결.md` 177행(이 수리를 상신 제안으로 내게 하는 지정):

```
(라) 명령의 인자, 출력의 키와 출력이 나가는 자리(표준 출력인가 표준 오류인가), 종료 코드 가운데 프로그램의 다른 프로세스가 쓰거나 읽는 것, 또는 가이드가 작업 세션이나 운영자에게 쓰라고 한 것을 없애거나 그 뜻을 바꾸는 수리.
```

### 영향
운영자가 운영자 문서의 표를 보고 저자마다 ORCID나 GitHub 계정을 설정에 적는다. 운전은 그것을 받아들이고, 꾸러미의 어느 파일에도 그 값이 나오지 않는다. 운영자는 값이 버려졌다는 말을 어디에서도 듣지 못한다. 코드를 읽는 다음 사람은 두 키가 쓰이는 자리를 찾다가 없다는 것을 확인하는 값을 치른다. 운전이 깨지는 것은 없다. 두 키를 없애는 수리는 가이드가 운영자에게 쓰라고 한 설정 키를 없애는 것이어서 동결문이 상신 제안으로 내게 한다.

### 상신
#### 읽은 범위

- 정의: `.claude/skills/do-math/runtime/finalize.py` 75~109행(`load_config`), 1614~1620행(`write_paper`), `.claude/skills/do-math/runtime/paper.py` 1629~1650행(`read_title_page`, `author_lines`), `.claude/skills/do-math/runtime/package.py` 925~990행(`formalization`), 1402~1416행(`readme_text`).
- 정본 문서: `.claude/skills/do-math/reference/operations.md` 472행.
- 결정: `.skill-workspace/finalize-pipeline/agreement.md` 19행(결정 7, 저자와 라이선스)과 28행, `임시/do-math_검증_20261125-2/맥락.md` 289행(4.11절 표의 「Author and licence」 행).
- 등록소의 양식: `.skill-workspace/finalize-pipeline/registry/clones/mathlib-initiative_formalization.yaml/schema/v0.4.schema.json` 23~33행(`project.authors`와 `responsible_maintainers`의 원소는 글자열).
- 기억 노드: `기억/layer1/M-0774.md`부터 `M-0779.md`까지에서 두 키의 이름을 검색했고, 어느 노드에도 나오지 않았다. 두 키가 어느 출력을 위해 들어왔는지를 적은 기록은 찾지 못했다.

#### 세계 물음

저자를 가진 운영자는 설정에 이름과 소속, 전자우편을 적고, 가지고 있으면 ORCID와 GitHub 계정도 적는다. 이름은 논문의 저자란, README, `formalization.yaml`에 나온다. 소속과 전자우편은 논문의 표제 쪽에 나온다. ORCID와 GitHub 계정을 실을 자리는 정의 파일에 없다. 논문의 표제 쪽(amsart의 `\author`, `\address`, `\email`)과 등록소의 양식(저자는 이름의 목록) 모두 그 칸을 갖지 않는다.

#### 선택지

- 가. 두 키를 받아들이는 집합과 거절문, 운영자 문서의 표에서 지운다. 두 키를 적은 설정은 시작에서 `"authors" is a list of objects ...`로 거절되고, 운영자는 그 값이 쓰이지 않는다는 것을 일을 시작하기 전에 안다. 시험 `test_a_run_comes_to_its_end_with_the_package_in_place`의 설정(1102행)이 `orcid`를 주므로 그 줄을 함께 고친다.
- 나. 두 키를 그대로 받아들이고, 운영자 문서의 표에 그 값이 꾸러미의 어느 파일에도 적히지 않는다고 적는다. 설정은 그대로 통과하고, 쓰이지 않는 키가 코드에 남는다.
- 다. 두 값을 실을 자리를 만든다. 예컨대 README의 저자 줄에 적는다. 사용자가 승인한 요약은 설정할 수 있는 것으로 「name and others」를 들었을 뿐 그 값들을 어디에 싣는지는 정하지 않았으므로, 이것은 새 출력을 더하는 일이다.

#### 변형 물음

가의 대가는 이미 두 키를 적어 둔 설정이 거절되는 것이다. 거절문이 받아들이는 키를 모두 들고 있으므로 운영자는 그 자리에서 두 키를 지우면 된다. 그 대가를 줄이는 변형(두 키를 받아들이되 경고를 내는 것)은 쓰이지 않는 키를 남기므로 나와 같아진다.

#### 추천 하나

가. 사용자의 상시 결정이 「What is not used is deleted」이고, 두 키를 실을 자리가 논문의 표제 쪽에도 등록소의 양식에도 없다. 나는 쓰이지 않는 키를 남기고, 다는 사용자가 정하지 않은 출력을 더한다.


### 심사 산출 심사_1.md의 판정

> 판정: 승인
> 처분: 사용자에게 올린다
> ### 실측
> 사본 finalize.py 93·95행만 `orcid`·`github`를 받아들이고, 읽는 코드는 runtime/ 어디에도 없다. operations.md 472행이 두 키를 운영자에게 적는다. test_finalize.py 1102행이 `orcid`를 준다. agreement.md 28행이 「What is not used is deleted.」다.
> ### 원인
> 설정이 받아들이는 저자 칸 둘이 어느 출력에도 쓰이지 않는다.
> ### 크기
> 운영자가 적은 값이 말없이 버려지고, 코드를 읽는 사람이 쓰임을 찾게 된다. 운전은 깨지지 않는다.
> ### 클래스
> 없음
> ### 상신안
> 두 키를 없애는 수리는 가이드가 운영자에게 쓰라고 한 꾸러미 설정 키를 없애는 것이어서 동결문 177행 (나)·(라)가 상신으로 지정한다(심사 계약의 넷째 경우). 선택지 가는 결함을 제거하고, 나는 문서로 알리며, 다는 자리를 만든다. 추천 가는 세 선택지의 승인 뒤 최종 상태를 견주며 근거로 사용자의 상시 결정과 실을 자리의 부재를 든다. 편집 권한이나 절차를 품질상 이점으로 세우지 않았고, 결함을 남기는 선택지를 추천하지 않았다.
>

### 심사 산출 심사_2.md의 판정

> 판정: 승인
> 처분: 사용자에게 올린다
> ### 실측
> 사본 finalize.py 92~97행이 `orcid`와 `github`를 받아들이고 거절문에 들며, operations.md 472행이 두 키를 운영자에게 적는다. 저장소의 `.claude/skills/do-math`에서 두 낱말은 그 둘과 시험 두 곳(test_finalize.py 1104행, test_paper.py 2819행의 입력)에만 나오고 읽는 코드가 없다. agreement.md 19행(결정 7)은 「a configurable name and others」를 정했을 뿐 두 칸을 정하지 않았고, 28행이 「What is not used is deleted」다. 동결문 177행 (라)와 그 머리가 꾸러미 파이프라인의 설정 키를 (라)로 보므로, 운영자에게 쓰라고 한 키를 없애는 수리는 상신 제안이다.
> ### 원인
> 쓰이지 않는 설정 칸이 받아들여지고 운영자 문서에 적혀 있다.
> ### 크기
> 운영자가 적은 값이 말없이 버려지고, 코드를 읽는 사람이 쓰이는 자리를 찾는 값을 치른다. 운전은 깨지지 않는다.
> ### 클래스
> 없음
> ### 상신안
> 선택지 셋(가: 두 키 삭제, 나: 그대로 두고 문서에 버려진다고 적음, 다: 실을 자리를 만듦)이 모두 지금의 어긋남(받아들이나 쓰이지 않음)을 닫는다. 추천 가는 각 선택지 승인 뒤의 최종 상태를 사용자 결정(agreement.md 28행)과 출력 양식(표제 쪽, 등록소의 이름 목록)에 견주어 정했고, 편집 권한이나 절차를 이점으로 세우지 않았다. 알려진 결함을 남기는 나를 추천하지 않았다. R3-M3이 같은 행(operations.md 472행, finalize.py 92~95행)의 문면을 바꾸므로, 가가 승인되면 그 뒤의 문면에서 두 키를 지우게 된다.
>

### 심사 산출 심사_3.md의 판정

> 판정: 승인
> 처분: 사용자에게 올린다
>
> ### 실측
> 사본 do-math 트리에서 `orcid`와 `github`는 finalize.py 93·95행, operations.md 472행, test_finalize.py 1102행에만 나온다. 저자를 쓰는 자리는 이름이나 `name`·`address`·`email`만 읽는다. agreement.md 19행의 결정 7은 「configurable name and others」를 정했고, 28행에 「What is not used is deleted.」가 있다. 두 키는 운영자 문서가 운영자에게 쓰라고 한 설정 키이므로 없애는 수리는 동결문 177행 (라)에 든다.
>
> ### 원인
> 설정이 두 키를 받아들이고 문서가 그것을 적었으나 그 값을 쓰는 출력이 없다.
>
> ### 크기
> 운영자가 적은 값이 말없이 버려지고, 코드를 읽는 사람이 쓰이는 자리를 찾느라 비용을 치른다. 운전이 깨지지는 않는다.
>
> ### 클래스
> 없음.
>
> ### 상신안
> 선택지 가는 결함(쓰이지 않는 키)을 제거하고, 나는 문서로 알리며 키를 남기고, 다는 새 출력을 더한다. 추천 가는 승인 뒤의 최종 상태(쓰이지 않는 키가 없음, 설정이 시작에서 거절되어 운영자가 미리 앎)를 다른 선택지의 최종 상태와 견주어 근거를 대며, 편집 권한이나 절차를 이점으로 세우지 않는다. 나는 알려진 결함을 남기는 선택지이지만 추천되지 않았다. 동결문 불변식이 이 수리를 상신 제안으로 지정하므로 처분은 사용자에게 올린다.
>
