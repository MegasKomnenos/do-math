# 라운드 2 — 「사용자에게 올린다」로 확정된 항목

항목의 원문(심사 대상에 실린 그대로)과 심사자 셋의 판정 절이다. 이 파일은 런의 중간물이며 수리자, 병합자, 심사자에게 주지 않는다. 종료 보고의 상신문은 이것을 재료로 쓴다.

## R2-54
제목: 논문에 인쇄되는 참고문헌 목록의 문면은 어느 세션도 고칠 수 없는데, 독해 세션은 매번 그것을 지적한다

### 위치
`.claude/skills/do-math/runtime/paper.py` 3795행(논문의 `references.bib`는 정본의 참고문헌 그대로다), 1673행(그 항목들을 `amsplain`이 인쇄한다), 1750행(기계 검사가 읽는 글은 제목·초록·절뿐이다), 2419~2420행과 2832~2846행(수리 세션과 해소 세션이 낼 수 있는 것은 part와 `plan.json`이다), 4005행과 4078행(두 독해 세션은 `references.bib`를 받는다). 그 문면이 어겨서는 안 되는 규칙은 `.claude/skills/do-math/reference/paper-method.md` 174행이다.

### 기준
`.claude/skills/do-math/reference/paper-method.md` 172행과 174행:

```
The canon is the means by which the result was obtained and verified. The user decided that it does not appear in the paper: the paper states the mathematics, and a reader who has never heard of the canon misses nothing.
```

```
The paper does not speak of sessions, records, reviews, weights, units, steps, or of the way the paper itself was produced.
```

`임시/do-math_검증_20261125-2/동결.md` 122행:

```
가이드가 약속하지만 코드가 하지 않는 동작, 코드가 하지만 가이드가 말하지 않아 작업 세션이나 운영자의 행동이 어긋나는 동작도 여기에 든다.
```

같은 문서 152행:

```
첫째는 실제 파일로 입증되는 결함인데 사용자 결정을 그대로 두고는 닫을 수 없는 것이다. 두 결정이 한 자리에서 부딪치는 경우와 결정이 내다보지 않은 경우가 그렇다.
```

### 영향
방법 문서 174행은 연구의 장부에 관한 말(세션, 기록, 검토 따위)이 논문에 나오지 않는다고 하고, 그 범위를 「the text, comments in the LaTeX source, and labels」로 적는다. 참고문헌 목록은 그 셋에 들지 않지만 논문에 인쇄된다. 프로그램은 정본의 `bibliography.bib`를 그대로 `references.bib`로 쓰고(3795행), 그 파일은 어느 검사도 읽지 않으며 어느 세션도 돌려줄 수 없다. 그래서 정본의 서지 항목에 연구의 장부에 관한 말이 들어 있으면 그 말은 그대로 논문에 인쇄되고, 명령 안에서 그것을 없앨 길이 없다.

실제로 일어난 일이다. `.skill-workspace/parking-staircase/paper-out-2/references.bib` 50행의 `note` 필드는 「Preprint, arXiv:2507.07243, version 2 of 19 September 2026; the records cite it by the numbers of this version.」으로 시작하고, 원고는 그 항목을 일곱 군데에서 인용한다(`parts/intro.tex` 여섯 군데, `parts/tables.tex` 한 군데). 같은 폴더의 `log.json`에서 원고만 읽는 독해 여섯 번(이벤트 54, 73, 94, 218, 230, 248)과 실제 논문 옆 독해 여덟 번(이벤트 114, 124, 139, 155, 165, 175, 191, 201)이 한 번도 빠짐없이 그 문면을 지적했다. 여덟째 실제 논문 옆 독해의 지적은 「"The records" refers to nothing the reader has.」라고 적는다. 실제 논문 옆 독해 뒤의 수리 여덟 번 가운데 여섯 번은 그 지적에 글을 그대로 두었고, 첫 수리가 적은 사유는 「it is not a part, and this session can write only parts」다. 나머지 두 번의 지적은 본문의 문장도 함께 가리킨 것이었다. 손으로 꾸린 `solved/parking-unimodality/`에서는 `records/bibliography.bib` 50행에 같은 문면이 있고, 논문 쪽 `paper/references.bib` 37~43행의 같은 항목에는 그 말이 없다. 손으로 꾸리는 과정에서 논문 쪽 항목만 고쳐진 것이다.

값을 치르는 이는 셋이다. 사용자는 「the records」를 말하는 참고문헌 목록이 인쇄된 논문을 받는다. 운전은 독해마다 답할 수 없는 지적 하나를 더 받는다. 실제 논문 옆 독해는 지적이 없는 독해가 두 번 이어져야 끝나므로(방법 문서 265행), 위의 운전에서처럼 독해마다 그 지적이 나오면 그 조건은 채워지지 않고 독해는 상한 여덟 번까지 간다. 그리고 그 지적은 마지막에 `kept` 목록에 사유와 함께 남아 운영자와 사용자가 읽어야 한다. 꾸러미 파이프라인의 논문도 같다. 그 논문은 파이프라인이 고친 참고문헌에서 쓰이지만, 고치는 세션이 손대는 것은 저자·제목·게재처·연도·쪽과 식별자뿐이다(`finalize/sources.md` 39행).

논문 명령에 대해 사용자에게 올라가 있는 물음 가운데 이웃한 것이 있다. 맥락.md 338행의 「what to do with findings about citations when the canon has no bibliography」다. 여기의 결함은 참고문헌이 있고 그 문면이 문제인 경우여서 그 물음의 답으로 닫히지 않는다.

### 상신
#### 읽은 범위

이 결함이 거론하는 개체는 셋이고, 각각 정의·정본 문서·결정을 열었다.

정본의 참고문헌(`canon/bibliography.bib`). 정의는 `.claude/skills/do-math/runtime/canon.py` 62행과 1228~1250행(`merge_bibliography`: 이미 있는 키의 항목은 그대로 남는다)이다. 정본 문서는 `.claude/skills/do-math/reference/literature.md` 73~91행(서지 항목에 무엇을 적는가)과 `.claude/skills/do-math/reference/change-format.md` 118행이다. 결정은 `임시/do-math-lean-설계/합의.md` 49행(「서지는 정본의 참고문헌 파일 하나에 모은다」)과 `docs/do-math/lean-canon-design.md` 109행이다. 두 결정은 항목이 무엇을 담는지는 정하지 않는다.

논문의 `references.bib`. 정의는 위치 칸의 `paper.py` 행들이다. 정본 문서는 `reference/paper-method.md` 154행, 174행, 229행과 `reference/operations.md` 399행, 407행이다. 결정은 맥락.md 252행과 258~260행(4.10절)의 사용자 말, 그리고 338행(4.13절)의 답하지 않은 물음이다.

꾸러미 파이프라인의 `sources` 세션. 정의는 `.claude/skills/do-math/runtime/finalize.py` 1096~1152행(세션이 돌려준 `bibliography.bib`가 라이브러리의 참고문헌을 갈음한다)이다. 정본 문서는 `.claude/skills/do-math/finalize/sources.md` 전문이다. 결정은 `.skill-workspace/finalize-pipeline/agreement.md` 59행이다.

실제 운전의 자료로 `.skill-workspace/parking-staircase/paper-out-2/`의 `references.bib`, `log.json`, `parts/intro.tex`, `.skill-workspace/parking-root-paper/paper-out3/log.json`, `solved/parking-unimodality/records/bibliography.bib`를 열었다. 열지 않은 것은 주차함수 정본에서 그 `note`를 쓴 세션의 기록이다. 그 항목이 어떤 지침 아래에서 쓰였는지는 확인하지 못했다. 그런 문면이 든 것으로 확인한 정본은 주차함수 연구에서 나온 것들뿐이다.

#### 세계 물음

독해 세션이 참고문헌 목록의 문면을 지적했을 때 이 명령이 그리는 행위자들은 다음과 같이 한다. 수리 세션은 글을 그대로 두고 사유를 적는다. 해소 세션도 part와 계획만 낼 수 있으므로 같다. 운영자는 `kept` 목록을 사용자와 읽는다(`reference/operations.md` 399행). 지적에 답하는 데 필요한 개체는 「서지 항목의 문면을 고쳐 돌려주는 세션」인데, 논문 명령에는 없다. 연구에도 없다. 연구의 후보는 항목을 더할 뿐이고 이미 있는 키의 항목은 바꾸지 못한다. 그 개체가 있는 곳은 꾸러미 파이프라인의 `sources` 세션 하나다. 그 세션은 참고문헌 전체를 고쳐 돌려주지만, 지침이 고치라고 하는 것에 연구의 장부에 관한 말은 들어 있지 않다.

#### 선택지

선택지 1. 그 문면이 생기는 자리와 이미 항목을 고치는 자리에서 닫는다. `reference/literature.md`의 서지 항목 문단에, 항목은 논문의 참고문헌 목록에 그대로 인쇄되므로 연구가 그 문헌을 어떻게 읽고 인용했는지는 기록의 `## Literature` 부분에 둔다는 것을 그 까닭과 함께 적는다. `finalize/sources.md`의 「Correct the entry」 단계에는 서지 사실이 아닌 문면을 항목에서 걷어 내는 일을 더한다. 하류: 앞으로 쓰이는 정본에는 그런 문면이 들어오지 않고, 꾸러미의 논문은 걷어 낸 참고문헌에서 쓰인다. 논문 명령의 코드는 바뀌지 않는다. 파이프라인 밖에서 이미 있는 정본으로 도는 논문 운전은 지금과 같아서, 독해가 지적하고 `kept`에 사유와 함께 남는다.

선택지 2. 논문 명령 안에서 닫는다. 모든 part를 고칠 수 있는 수리 세션과 해소 세션이 `references.bib`도 돌려줄 수 있게 하고, 프로그램은 돌려받은 파일의 키와 항목 종류가 그대로인지를 본다. 하류: 어느 정본으로 도는 운전이든 그 지적에 답할 수 있다. 대가는 셋이다. 연구가 읽고 적은 서지 사실을 논문 세션이 바꿀 수 있게 되고, 그 뜻은 스크립트가 검사하지 못한다. 세션이 내는 파일의 계약과 그 검사와 시험이 새로 든다. 꾸러미에서는 `records/bibliography.bib`와 논문의 `references.bib`가 서로 달라질 수 있다.

선택지 3. 그대로 둔다. 지적은 독해마다 나오고 `kept`에 남아 사용자에게 전해진다. 사용자가 정본의 참고문헌을 손으로 고치지 않는 한 논문은 그 문면을 인쇄한다.

선택지 4. 두 독해 세션에게 참고문헌 목록은 연구의 것이니 지적하지 말라고 알린다. 하류: 지적은 사라지고 독해가 상한 전에 끝날 수 있게 되지만, 그 문면은 아무에게도 알려지지 않은 채 인쇄된다.

#### 변형 물음

선택지 2의 첫째 대가를 줄이는 변형이 있다. 세션이 고칠 수 있는 것을 `note` 필드로 좁히고, 프로그램이 나머지 필드가 글자 그대로인지를 본다. 서지 사실이 바뀔 위험은 없어지지만 새 계약과 검사와 시험은 그대로 든다. 선택지 1이 남기는 자리(이미 있는 정본, 파이프라인 밖의 운전)를 없애는 변형은 찾지 못했다. 정본의 항목은 후보로 바꿀 수 없기 때문이다.

#### 추천 하나

선택지 1을 추천한다. 각 선택지를 승인한 뒤의 상태를 견주면 이렇다. 선택지 3과 4는 논문에 그 문면이 남는다. 선택지 2와 그 변형은 모든 운전에서 결함을 없애지만, 논문을 쓰는 세션에게 연구의 서지를 고치는 권한과 그것을 받치는 장치를 새로 들인다. 선택지 1은 장치를 더하지 않고 원인을 막는다. 항목을 쓰는 연구 세션은 그 항목이 논문에 인쇄된다는 것을 지금 어느 가이드에서도 듣지 못하고, 항목을 고치는 `sources` 세션은 이미 참고문헌 전체를 돌려주고 있다. 사용자가 발표할 논문을 얻는 길은 꾸러미 파이프라인이므로, 그 길의 논문이 깨끗해지면 남는 것은 파이프라인 밖에서 옛 정본으로 도는 운전뿐이고, 거기서는 지금처럼 `kept`의 사유가 사용자에게 그 사실을 알린다.


### 심사 산출 심사_1_배치2.md의 판정

> 판정: 승인
> 처분: 사용자에게 올린다
>
> ### 실측
> paper.py 3794행은 정본의 참고문헌을 `capitals_kept`만 거쳐 `references.bib`로 쓰고, 1750행의 기계 검사 `texts`에는 그 파일이 없다. 수리 프롬프트(2419~2420행)가 내게 하는 것은 part 파일이다. 방법 문서 174행의 배제 범위는 본문, LaTeX 주석, 라벨이다. `.skill-workspace/parking-staircase/paper-out-2/references.bib` 50행의 `note`가 「the records cite it by the numbers of this version」을 담는 것을 확인했고, 같은 폴더 `log.json`에서 「the records」가 46번 나온다. `finalize/sources.md` 39행의 「Correct the entry」는 저자·제목·게재처·연도·쪽과 식별자만 고치게 한다. `reference/literature.md` 73~91행은 그 항목이 논문에 인쇄된다는 것을 말하지 않는다.
>
> ### 원인
> 정본의 서지 항목이 논문의 참고문헌으로 그대로 인쇄되는데, 항목을 쓰는 연구 세션도, 논문 명령의 세션도, 꾸러미의 `sources` 세션도 연구의 장부에 관한 말을 걷어 낼 책임이나 수단을 갖지 않는다.
>
> ### 크기
> 실제 운전에서 「the records」를 말하는 참고문헌이 인쇄되었고, 독해마다 답할 수 없는 지적이 나와 실제 논문 옆 독해가 상한까지 갔다.
>
> ### 클래스
> `note` 밖의 서지 필드에 같은 말이 들어간 정본이 있는지는 확인하지 않았다.
>
> ### 상신안
> 선택지 넷 가운데 1과 2는 결함을 고치거나 원인을 막는다. 추천인 선택지 1은 승인 뒤의 상태(새 정본에는 그 말이 들어오지 않고 꾸러미의 논문은 걷어 낸 참고문헌에서 쓰인다, 파이프라인 밖의 옛 정본 운전만 지금처럼 `kept`로 알린다)를 다른 선택지의 최종 상태와 견주어 세웠다. 편집 권한의 부족이나 승인 절차 자체를 이점으로 세우지 않았다. 남는 자리는 파이프라인 밖의 옛 정본인데, 이것은 대체 구조를 더하며 결함을 보존하는 추천이 아니라 정본의 항목을 후보로 바꿀 수 없다는 이행 제약에서 오는 잔여로 적혀 있다. 비동등한 결과가 둘 이상 남으므로 상신이 맞다.
>

### 심사 산출 심사_2_배치2.md의 판정

> 판정: 승인
> 처분: 사용자에게 올린다
>
> ### 실측
> 사본 `paper.py` 3794행은 materials의 bibliography를 그대로 `references.bib`로 쓴다. `.skill-workspace/parking-staircase/paper-out-2/references.bib` 50행의 `note`는 「the records cite it by the numbers of this version」을 담고, 그 키 `celano2025`는 `parts/intro.tex`에 여섯 번, `parts/tables.tex`에 한 번 나온다. 같은 폴더 `log.json`에 「"The records" refers to nothing the reader has.」(1건)와 「it is not a part, and this session can write only parts」가 있다. `solved/parking-unimodality/records/bibliography.bib` 50행에는 같은 문면이 있고 `paper/references.bib` 37~43행에는 없다. 방법 문서 174행과 `finalize/sources.md` 39행(고치는 필드가 서지 사실과 식별자뿐)도 항목의 인용과 같다.
>
> ### 원인
> 연구 세션은 서지 항목이 논문에 인쇄된다는 것을 듣지 못하고, 논문 명령 안에는 항목의 문면을 돌려줄 수 있는 세션이 없다.
>
> ### 크기
> 연구의 장부를 말하는 문장이 인쇄된 논문에 남고, 실제 논문 옆 독해는 답할 수 없는 지적 때문에 상한 여덟 번까지 간다.
>
> ### 클래스
> `finalize/sources.md`의 「Correct the entry」 단계가 같은 문면을 걷지 않는 자리.
>
> ### 상신안
> 선택지 넷 가운데 1과 2(및 그 변형)가 확인된 결함을 고친다. 1은 문면이 생기는 자리(`reference/literature.md`)와 항목을 고치는 자리(`finalize/sources.md`)를 고치고, 2는 논문 세션에 참고문헌을 돌려줄 권한과 그 검사를 새로 준다. 두 결과는 비동등하고, 어느 쪽인지는 논문 세션의 권한과 서지 사실의 보전 가운데 무엇을 앞세울지에 대한 사용자의 판단에 달린다. 추천(1)은 각 선택지를 승인한 뒤의 상태를 견주어 세웠고, 편집 권한 부족이나 승인 절차를 이점으로 세우지 않았다. 1이 남기는 것(파이프라인 밖에서 옛 정본으로 도는 운전의 `kept` 사유)은 알려진 결함을 남긴 채 대체 구조를 더하는 경우가 아니다. 관문 8은 통과한다.
>

### 심사 산출 심사_3_배치2.md의 판정

> 판정: 승인
> 처분: 사용자에게 올린다
>
> ### 실측
> `Paper.assemble`은 정본의 참고문헌을 `references.bib`로 그대로 쓴다(3794행). `paper-method.md` 174행의 배제 범위는 본문, 주석, 라벨이다. `.skill-workspace/parking-staircase/paper-out-2/references.bib` 50행의 `note`가 「the records cite it by the numbers of this version」을 담고, 같은 폴더 `log.json`에 그 문면이 23번 나온다. 손으로 꾸린 꾸러미의 논문 쪽 항목(`solved/parking-unimodality/paper/references.bib` 37~43행)에는 그 말이 없다. `finalize/sources.md` 39행이 고치게 하는 것은 저자, 제목, 게재처, 연도, 쪽과 식별자다.
>
> ### 원인
> 연구 세션은 서지 항목이 논문에 그대로 인쇄된다는 것을 듣지 못하고, 논문 명령에는 그 문면을 고칠 수 있는 세션이 없다.
>
> ### 크기
> 「the records」를 말하는 참고문헌 목록이 논문에 인쇄되고, 독해마다 답할 수 없는 지적이 나와 실제 논문 옆 독해가 상한까지 간다.
>
> ### 클래스
> 꾸러미 파이프라인의 논문도 같은 참고문헌에서 쓰인다(항목이 적었다).
>
> ### 상신안
> 선택지 넷 가운데 1과 2와 그 변형은 결함을 고치고, 3은 그대로 두며, 4는 지적을 없앤다. 추천(1)은 승인 뒤의 최종 상태를 넷 모두와 견주어 세웠다. 편집 권한의 부족이나 승인 절차를 이점으로 세우지 않았다. 추천 1은 대체 구조를 더하는 선택지가 아니고, 남는 자리(옛 정본으로 파이프라인 밖에서 도는 운전)는 정본 항목을 후보로 바꿀 수 없다는 이행 제약으로 설명된다. 수리 방향이 둘 이상의 비동등한 결과로 갈리고, 이웃한 미답 물음(맥락 문서 338행)이 있으므로 사용자에게 올린다.
>

## R2-91
제목: 꾸러미 설정의 저자 필드 `orcid`와 `github`를 프로그램이 받기만 하고 어디에도 쓰지 않는다

### 위치
`.claude/skills/do-math/reference/operations.md` 466행(설정 표의 `authors` 행)과 472행(저자를 첫 시작 전에 사용자에게 물으라는 문단), `.claude/skills/do-math/runtime/finalize.py` 92~95행(`load_config`이 저자 객체에 허용하는 키).

### 기준
동결문 `임시/do-math_검증_20261125-2/동결.md` 134행이 이 결함의 갈래를 정한다.

```
넷째는 세 갈래를 가로지르는 손상이다. 이번 주에 걷어 낸 기능의 잔재, 쓰이지 않는 코드와 인자, 코드나 시험이 한 규칙을 두 군데에 따로 구현한 것과 그 둘 사이의 어긋남, 앞 상태를 서술하는 주석과 문서, 이 기계에만 맞는 경로와 수치가 여기에 든다.
```

이 수리를 조각으로 내지 못하는 까닭은 같은 문서 177행의 (나)와 (라)다.

```
꾸러미 파이프라인의 설정 파일의 키와 명령줄 옵션은 (라)로 본다.
```

```
(라) 명령의 인자, 출력의 키와 출력이 나가는 자리(표준 출력인가 표준 오류인가), 종료 코드 가운데 프로그램의 다른 프로세스가 쓰거나 읽는 것, 또는 가이드가 작업 세션이나 운영자에게 쓰라고 한 것을 없애거나 그 뜻을 바꾸는 수리.
```

저자 필드가 어디로 가야 하는지는 꾸러미 합의 `.skill-workspace/finalize-pipeline/agreement.md` 19행과 83행이 적는다.

```
The name and the other title-page fields are configuration.
```

```
3. The author fields of the configuration feed `formalization.yaml`. With the default empty name those fields are left empty and the final report lists them as what the user fills in before submitting.
```

### 영향
`load_config`은 저자 객체의 키로 `name`, `address`, `email`, `orcid`, `github`를 받는다(`runtime/finalize.py` 92~95행). 그 뒤 설정의 저자를 읽는 자리는 다섯이다. 논문의 저자란으로 가는 `title-page.json`은 `name`, `address`, `email`만 옮긴다(`runtime/finalize.py` 1617~1618행). 등록소 파일 `formalization.yaml`의 `authors`와 `responsible_maintainers`는 이름의 목록이다(`runtime/package.py` 939행, 969~970행). README의 저자 줄도 이름만 쓴다(같은 파일 1408~1409행). 나머지 두 자리는 저자가 없는지만 본다(같은 파일 1481행, `runtime/finalize.py` 1784행). `orcid`와 `github`를 읽는 코드는 `runtime/finalize.py`, `runtime/package.py`, `runtime/paper.py` 어디에도 없다.

운영자는 operations.md 472행에 따라 첫 시작 전에 사용자에게 저자 정보를 묻고, 466행이 든 다섯 필드를 그대로 물을 수 있다. 사용자가 ORCID와 GitHub 계정을 주면 설정은 통과하고 운전은 끝까지 가지만, 꾸러미의 어느 파일에도 그 값은 없고 `report.md`의 「What you fill in before a submission to the registry」도 그것을 말하지 않는다. 사용자는 자기 식별자가 꾸러미에 실렸다고 믿고 제출을 준비하게 된다.

### 상신
#### 읽은 범위

추적한 개체는 설정의 저자 필드 `orcid`와 `github` 하나다.

- 정의: `.claude/skills/do-math/runtime/finalize.py` 70~109행(`default_config`, `load_config`). 지급 안의 사본에서 읽었다.
- 정본 문서: `.claude/skills/do-math/reference/operations.md` 462~472행. 지급 안의 사본에서 읽었다.
- 결정: `.skill-workspace/finalize-pipeline/agreement.md` 19행과 83행(기준 원문), `임시/do-math_검증_20261125-2/맥락.md` 289행(4.11절 표의 「Author and licence」 행)과 4.12절.
- 지급 밖에서 연 것: `.skill-workspace/finalize-pipeline/design.md` 58행(설정 표의 `authors` 행으로 operations.md 466행과 같은 문장이다), 301행과 566행(논문 명령의 저자란 파일은 `name`, `address`, `email`만 가진다), 363행(`formalization.yaml`의 `authors`는 설정에서 온다); `.skill-workspace/finalize-pipeline/registry/clones/kim-em_erdos-unit-distance-comparator/formalization.yaml` 1~40행(등록소에 실제로 제출된 파일의 `authors`와 `responsible_maintainers`는 이름의 목록이다).

셋 가운데 열지 않은 것은 없다. 등록소의 `formalization.yaml` 스키마 원문은 네트워크 밖에 있어 열지 않았고, 위 실제 제출 파일 하나로 갈음했다.

#### 세계 물음

운영자는 사용자에게 저자의 이름, 주소, 전자우편, ORCID, GitHub 계정을 묻고 설정 파일에 적는다. 운전은 그 설정을 받아 끝까지 간다. 이 행위에 필요한 개체는 「저자의 ORCID나 GitHub 계정이 적히는 꾸러미 안의 자리」인데, 정의 파일에 그런 자리가 없다. 논문의 저자란은 세 필드만 받고, 등록소 파일과 README는 이름만 받는다. 합의 83행이 말한 「author fields … feed `formalization.yaml`」도 등록소 형식이 이름만 받으므로 이 두 필드에는 갈 곳이 없다.

#### 선택지

1. 두 필드를 없앤다. `load_config`의 허용 키와 거절 문장에서 `orcid`, `github`를 빼고 operations.md 466행에서도 뺀다. 그 뒤로 두 필드를 가진 설정은 다른 모르는 키처럼 이름을 들어 거절된다. 하류 영향은 하나다. 두 필드를 넣어 시작했다가 멈춘 운전이 있으면, 설정을 고치는 순간 「configuration」이 달라져 이어 갈 수 없으므로 작업 폴더를 지우고 새로 시작해야 한다. 맥락 문서 6.2절은 이 런이 시작할 때 설치본으로 도는 꾸러미 운전이 없었다고 적고, 시험 운전은 기본 설정으로 돌았다.
2. 두 필드를 그대로 받고, operations.md 466행에 두 필드는 받기만 하고 꾸러미 어디에도 쓰이지 않는다고 적는다. 운영자는 더 묻지 않게 되지만, 쓰이지 않는 인자가 프로그램과 문서에 남는다.
3. 두 필드를 꾸러미에 쓴다. 쓸 자리(README의 저자 줄, 논문의 저자란, 꾸러미의 다른 파일)를 사용자가 정해야 하고, 논문의 저자란이라면 논문 명령의 `--title-page` 형식과 방법 문서까지 바뀐다.

#### 변형 물음

선택지 1의 대가는 두 필드를 가진 기존 설정이 거절된다는 것이다. 그 대가를 없애는 변형은 `settings.py`가 `lean.judge`에 하듯 두 키를 받되 무시하고 문서에서만 빼는 것이다. 그러면 거절은 없지만 운영자가 모르는 채 버려지는 입력이 남아 지금의 결함과 같은 꼴이 되므로 선택지로 넣지 않았다. 선택지 3의 대가는 쓸 자리를 정하고 형식을 넓히는 일인데, 그 대가를 줄이는 변형은 README의 저자 줄에만 괄호로 덧붙이는 것이다. 그 경우에도 등록소 파일에는 실리지 않으므로 사용자가 그 정도를 원하는지가 먼저 정해져야 한다.

#### 추천 하나

선택지 1을 추천한다. 승인 뒤의 최종 상태를 견주면, 1은 설정이 받는 것과 꾸러미에 실리는 것이 같아지고 운영자가 사용자에게 묻는 것이 모두 쓰인다. 2는 결함을 문서로 설명할 뿐 쓰이지 않는 인자를 남긴다. 2가 그 인자를 남겨야 할 독립된 소비자나 호환 계약은 찾지 못했다. 두 필드를 읽는 코드가 없고, 등록소 형식에도 받을 자리가 없으며, 두 필드를 넣어 돈 운전의 기록도 없다. 3은 사용자가 말한 「a configurable name and others」를 넓히는 새 능력이어서, 사용자가 그 자리를 원한다고 답할 때에만 선다.


### 심사 산출 심사_1_배치2.md의 판정

> 판정: 승인
> 처분: 사용자에게 올린다
>
> ### 실측
> finalize.py 92~95행은 저자 객체에 orcid와 github를 허용한다. runtime의 .py 전체에서 두 이름은 그 두 행에만 나온다. operations.md 466행은 다섯 필드를 들고, 472행은 저자를 사용자에게 물으라고 한다. 꾸러미 합의 19행과 83행을 확인했다. 두 키를 없애는 수리는 동결문 177행 (나)의 끝 문장과 (라)에 따라 상신으로 지정된다.
>
> ### 원인
> 설정이 받는 저자 필드 둘이 꾸러미 어디에도 쓰이지 않는다.
>
> ### 크기
> 사용자가 ORCID와 GitHub를 주면 운전은 통과하지만 그 값이 꾸러미에 없고, 보고도 그것을 말하지 않는다.
>
> ### 클래스
> 없음
>
> ### 상신안
> 선택지 1(두 필드를 없앰)과 3(쓸 자리를 정해 씀)은 결함을 없애고, 2는 문서로 설명만 한다. 추천 1은 승인 뒤의 최종 상태를 견주어 세웠다. 1은 받는 것과 실리는 것이 같아지고, 2는 쓰이지 않는 인자를 남기며, 3은 새 자리를 정하는 사용자 결정이 필요하다. 결함을 남기는 2를 추천하지 않았고, 그 보존 근거(독립 소비자·호환 계약)가 없다는 것도 적었다. 편집 권한의 부족이나 승인 절차를 이점으로 세우지 않았다.
>

### 심사 산출 심사_2_배치2.md의 판정

> 판정: 승인
> 처분: 사용자에게 올린다
>
> ### 실측
> 사본 `finalize.load_config`(92~95행)는 저자 객체에 `orcid`와 `github`를 허용한다. `runtime/*.py`, `reference/`, `finalize/` 전체에서 두 이름은 그 두 줄과 `operations.md` 466행에만 나온다. 꾸러미 합의 19행은 「The name and the other title-page fields are configuration」, 83행은 저자 필드가 `formalization.yaml`로 간다고 적는다. 동결문 177행은 꾸러미 설정 파일의 키를 (라)로 보아 그 수리를 상신 제안으로 지정한다.
>
> ### 원인
> 설정이 받는 저자 필드 가운데 둘이 꾸러미의 어느 파일에도 쓰이지 않는다.
>
> ### 크기
> 운영자가 문서대로 물어 받은 사용자의 ORCID·GitHub 계정이 말없이 버려지고, 사용자는 식별자가 꾸러미에 실렸다고 믿는다.
>
> ### 클래스
> 없음
>
> ### 상신안
> 선택지 1(두 필드를 없앤다)과 3(두 필드를 쓴다)이 결함을 고친다. 2는 결함을 문서로 설명할 뿐이고 추천되지 않았다. 추천(1)은 승인 뒤의 최종 상태를 견주어 세웠다. 1에서는 설정이 받는 것과 꾸러미가 싣는 것이 같아진다. 2에 대해서는 보존 근거(독립 소비자·호환 계약·이행 제약)를 찾지 못했다고 밝힌다. 3은 새 능력이라는 이유로 사용자의 답에 맡긴다. 편집 권한이나 승인 절차를 이점으로 세우지 않았다. 동결문 177행 (라)가 상신을 지정한 수리이므로 처분은 사용자에게 올린다. 관문 8은 통과한다.
>

### 심사 산출 심사_3_배치2.md의 판정

> 판정: 승인
> 처분: 사용자에게 올린다
>
> ### 실측
> `load_config`는 저자 객체의 키로 `orcid`와 `github`를 받는다(`finalize.py` 93·95행). 런타임 전체에서 두 이름은 그 두 줄에만 나온다. 저자란 파일은 `name`, `address`, `email`만 옮긴다(1617행). `operations.md` 466행은 다섯 필드를 들고, 472행은 저자를 첫 시작 전에 사용자에게 물으라고 한다. 꾸러미 합의 19행과 83행을 확인했다. 설정 파일의 키를 없애는 수리는 동결문 177행 (나)·(라)에 따라 상신 제안이다.
>
> ### 원인
> 설정이 받는 저자 필드 가운데 둘이 꾸러미 어디에도 쓰이지 않는다.
>
> ### 크기
> 사용자가 준 식별자가 꾸러미에 실렸다고 믿고 제출을 준비하게 된다.
>
> ### 클래스
> 없음
>
> ### 상신안
> 선택지 셋 가운데 1(없앤다)과 3(쓴다)은 결함을 고친다. 2(문서에만 적는다)는 결함을 남기는데, 항목은 그 보존 근거(독립 소비자·호환 계약)를 찾지 못했다고 적고 2를 추천하지 않는다. 추천 1은 승인 뒤의 최종 상태를 견주어 세웠다. 편집 권한이나 승인 절차를 이점으로 세우지 않았다. 동결문의 불변식이 이 처분을 지정한다.
>
