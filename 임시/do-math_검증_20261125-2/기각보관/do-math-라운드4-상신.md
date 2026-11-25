# 라운드 4 — 「사용자에게 올린다」로 확정된 항목

항목의 원문(심사 대상에 실린 그대로)과 심사자 셋의 판정 절이다. 이 파일은 런의 중간물이며 수리자, 병합자, 심사자에게 주지 않는다. 종료 보고의 상신문은 이것을 재료로 쓴다.

## R4-44
제목: 꾸러미 설정의 저자 필드 `orcid`와 `github`는 받기만 하고 어디에도 쓰이지 않는다

### 위치
산출물에 구현된 내용의 문제다.

- `.claude/skills/do-math/reference/operations.md` 472행. 설정 표의 `authors` 줄이 저자 객체의 선택 필드로 `address`, `email`, `orcid`, `github`를 든다.
- `.claude/skills/do-math/runtime/finalize.py` 93~97행. `load_config`가 그 다섯 키를 허용하고, 거절 문장도 다섯을 든다.
- 값이 쓰이는 자리 전부: `.claude/skills/do-math/runtime/finalize.py` 1742~1743행(논문의 저자 줄에 `name`, `address`, `email`만 넘긴다), `.claude/skills/do-math/runtime/package.py` 946행과 976~977행(`formalization.yaml`의 `project.authors`와 `project.responsible_maintainers`에 `name`만 싣는다), 같은 파일 1415~1416행(README에 `name`만 싣는다). `orcid`와 `github`를 읽는 코드는 없다.
- `.claude/skills/do-math/runtime/tests/test_finalize.py` 1104행. 끝까지 가는 운전의 시험이 `orcid`가 든 저자를 설정에 넣지만, 그 값에 관한 단언은 없다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 134행:

```
넷째는 세 갈래를 가로지르는 손상이다. 이번 주에 걷어 낸 기능의 잔재, 쓰이지 않는 코드와 인자, 코드나 시험이 한 규칙을 두 군데에 따로 구현한 것과 그 둘 사이의 어긋남, 앞 상태를 서술하는 주석과 문서, 이 기계에만 맞는 경로와 수치가 여기에 든다.
```

`임시/do-math_검증_20261125-2/동결.md` 128행:

```
그 독자에게 맞지 않는 내용, 같은 사항에 대해 가이드끼리 어긋나는 서술, 코드의 실제 동작과 어긋나는 서술, 더는 없는 것을 말하는 서술, 의도를 정확히 전하지 못하는 서술이 결함이다.
```

`임시/do-math_검증_20261125-2/동결.md` 177행(상신 제안으로 내라고 지정한 수리):

```
(나) 인스턴스의 `settings.json`의 설정 키를 없애거나 이름을 바꾸거나 그 기본값을 바꾸는 수리. 꾸러미 파이프라인의 설정 파일의 키와 명령줄 옵션은 (라)로 본다.
```

```
(라) 명령의 인자, 출력의 키와 출력이 나가는 자리(표준 출력인가 표준 오류인가), 종료 코드 가운데 프로그램의 다른 프로세스가 쓰거나 읽는 것, 또는 가이드가 작업 세션이나 운영자에게 쓰라고 한 것을 없애거나 그 뜻을 바꾸는 수리.
```

`임시/do-math_검증_20261125-2/맥락.md` 228행:

```
**Delete what is not used.** "delete what is not used" (session `20538f79`, 24 November 11:53:14Z); "delete leftovers." (the same session, 10:40:29Z).
```

`.skill-workspace/finalize-pipeline/agreement.md` 83행:

```
3. The author fields of the configuration feed `formalization.yaml`. With the default empty name those fields are left empty and the final report lists them as what the user fills in before submitting.
```

`.claude/skills/do-math/reference/operations.md` 478행:

```
The authors and the human review are facts about the user, so ask for them before the first start and write nothing the user did not say.
```

### 영향
운영자는 첫 기동 전에 설정 표를 보고 사용자에게 저자 정보를 묻는다. 표가 `orcid`와 `github`를 저자의 필드로 들므로, 운영자는 그 둘도 묻거나 사용자가 준 값을 설정에 넣는다. 프로그램은 그 값을 받아들이고(`finalize.py` 95행), 운전의 어느 단계도 그것을 읽지 않는다. 꾸러미의 논문, `formalization.yaml`, README 어디에도 두 값은 나타나지 않고, 종료 보고도 그 사실을 말하지 않는다. 사용자는 준 정보가 꾸러미에 실렸다고 여기게 되고, 운영자는 그것을 바로잡을 근거를 가이드에서 얻지 못한다. 프로그램 쪽에는 읽는 곳이 없는 입력 두 개가 남아, 코드를 고치는 다음 사람이 그 쓰임을 찾아보는 값을 치른다.

이 결함을 닫는 길은 동등하지 않은 것이 둘 이상이고, 그 가운데 키를 걷는 수리는 동결문 불변식의 (라)가 상신 제안으로 지정한 것이어서 조각으로 내지 않는다.

### 상신
#### 읽은 범위

개체는 꾸러미 설정의 `authors` 항목이 갖는 키 `orcid`와 `github`다.

- 정의: `runtime/finalize.py` 72~111행(`default_config`, `load_config`), 1739~1745행(`write_paper`의 저자 줄), `runtime/package.py` 925~990행(`formalization`), 1404~1416행(`readme_text`), `runtime/paper.py` 1629~1641행(`read_title_page`). 스킬 전체에서 두 낱말이 나오는 자리는 `finalize.py` 95·97행, `operations.md` 472행, 시험 두 곳(`test_finalize.py` 1104행, `test_paper.py` 2838행)뿐임을 검색으로 확인했다.
- 정본 문서: `reference/operations.md` 「The command and its configuration」(460~480행)과 「What the run leaves, and what to tell the user」(530~548행).
- 결정: 꾸러미 합의 `.skill-workspace/finalize-pipeline/agreement.md` 19행(사용자의 말 "have a configurable name and others, …"과 그 풀이)과 83행, 설계 `.skill-workspace/finalize-pipeline/design.md` 58행(같은 표 줄), 맥락 문서 4.11절 표의 「Author and licence」 줄. 등록소의 현행 요건은 `.skill-workspace/finalize-pipeline/registry/clones/PalomarRegistry_PalomarPolicy/CONTRIBUTING.md` 447~451행과 507~510행에서 읽었다. 그 문서는 `project.responsible_maintainers`가 이름 문자열의 목록이고, 예전의 사상(mapping) 꼴은 호환을 위해서만 읽는다고 적는다.
- 열지 않은 것: 두 키를 들인 커밋의 세션 전사(열람 금지). 등록소의 `formalization.yaml` 형식 저장소에서는 두 낱말을 검색만 했고 결과가 없었다.

#### 세계 물음

운영자는 사용자에게 저자 정보를 묻고 설정 파일에 적는다. 사용자는 이름과 함께 ORCID와 GitHub 계정을 줄 수 있고, 표가 그 필드를 들기 때문에 운영자는 그것을 적는다. 그 값을 담을 개체, 곧 꾸러미의 어느 파일의 어느 칸이 정의 파일에 있는가를 보면 없다. 논문의 저자 줄은 이름·주소·전자우편만 받고, 등록소 파일의 두 목록은 이름 문자열만 받으며, README는 이름만 적는다.

#### 선택지

1. 두 키를 걷는다. `finalize.py` 95행의 허용 집합과 97행의 문장에서 `orcid`와 `github`를 빼고, `operations.md` 472행에서 두 낱말을 빼며, `test_finalize.py` 1104행의 설정에서 `orcid`를 뺀다. 하류 영향: 두 키를 가진 설정 파일은 기동 때 이름으로 거절된다(종료 코드 1). 꾸러미의 내용은 달라지지 않는다. 지금도 두 값은 어디에도 실리지 않기 때문이다. 두 키를 넣고 시작한 운전이 있다면 설정이 달라져 이어 갈 수 없는데, 맥락 문서 6.2절은 이 런이 시작될 때 설치본으로 도는 꾸러미 운전이 없었다고 적는다.
2. 키는 두고 가이드만 고친다. `operations.md` 472행에, 두 필드는 받아들여지지만 꾸러미의 어느 파일에도 쓰이지 않는다고 적는다. 하류 영향: 운영자가 그 둘을 묻지 않게 되고, 사용자가 준 값이 실렸다고 오해할 일이 없어진다. 프로그램에는 읽는 곳 없는 입력 두 개가 그대로 남는다.
3. 두 값을 꾸러미에 싣는다. 실을 자리는 README의 저자 줄뿐이다. 등록소의 현행 형식은 이름 문자열만 받기 때문이다. 하류 영향: 사용자가 요청한 적 없는 출력이 꾸러미에 생기고, 그 문장의 형식과 검사를 새로 정해야 한다.

#### 변형 물음

선택지 1의 대가는 두 키를 쓴 설정 파일이 거절되는 것이다. 거절하지 않고 조용히 버리게 하는 변형은 선택지 2와 같은 최종 상태(읽는 곳 없는 입력)를 남긴다. `lean.judge`처럼 「받아들이되 효과 없음」으로 남기는 변형은 그 키를 가진 인스턴스가 실제로 있어서 둔 것인데, 두 키를 가진 꾸러미 설정 파일이 있다는 근거는 찾지 못했다. 선택지 3의 대가(새 출력)를 줄이는 변형은 찾지 못했다.

#### 추천 하나

선택지 1을 추천한다. 세 선택지의 최종 상태를 견주면, 1은 가이드와 프로그램이 같은 세 필드(`name`, `address`, `email`)를 말하고 쓰이지 않는 입력이 없는 상태다. 2는 결함의 절반(쓰이지 않는 입력)을 남긴 채 그것을 설명하는 문장을 가이드에 더한다. 그 입력을 유지해야 할 독립 소비자나 호환 계약, 이행 제약은 위 읽은 범위에서 찾지 못했다. 3은 사용자가 정하지 않은 출력을 새로 들인다. 사용자는 쓰이지 않는 것을 지우라고 말해 왔고(맥락 문서 4.7절), 꾸러미 합의는 저자 필드가 등록소 파일을 채운다고만 적는데 그 파일이 받는 것은 이름이다.


### 심사 산출 심사_1.md의 판정

> 판정: 승인
> 처분: 사용자에게 올린다
> ### 실측
> `finalize.py` 95·97행이 저자 객체의 `orcid`와 `github`를 허용하고, `operations.md` 472행이 그 둘을 필드로 든다. 저자 값을 쓰는 자리(`finalize.py`의 논문 저자 줄, `package.py`의 `formalization`과 `readme_text`)는 `name`, `address`, `email`만 읽는다. 맥락 문서 4.11절 표의 사용자 말은 「a configurable name and others」로 두 필드를 따로 정하지 않았고, 맥락 문서 9.8절도 두 키를 읽는 곳 없는 입력으로 적는다. 키를 걷는 수리는 동결문 불변식 (라)가 상신 제안으로 지정한 꾸러미 설정 키의 변경이다.
> ### 원인
> 설정이 받아들이는 저자 필드와 꾸러미가 싣는 필드가 어긋난 채 두 필드가 들어왔다.
> ### 크기
> 운영자가 사용자에게 묻고 적는 두 값이 꾸러미 어디에도 실리지 않고, 사용자는 실렸다고 여긴다.
> ### 클래스
> 없음
> ### 상신안
> 선택지 1(두 키를 걷는다)은 확인된 결함, 곧 읽는 곳 없는 입력과 그것을 약속하는 가이드 줄을 함께 없앤다. 선택지 2는 결함의 절반을 남기고 설명을 더하며, 선택지 3은 사용자가 정하지 않은 출력을 들인다. 추천은 셋의 최종 상태를 견주어 1을 고르고, 편집 권한이나 승인 절차를 이점으로 세우지 않는다. 결함을 남기는 선택지를 추천하지 않으므로 보존 근거는 필요하지 않다. 관문 8을 통과한다.
>

### 심사 산출 심사_2.md의 판정

> 판정: 승인
> 처분: 사용자에게 올린다
> ### 실측
> `orcid`·`github`는 `finalize.py` 95·97행과 `operations.md` 472행에서만 나오고, 읽는 코드가 없다(검색으로 확인). 꾸러미 합의 19행은 사용자의 말 「have a configurable name and others」를 싣는다. 그래서 저자 설정의 필드가 사용자 결정에 들 수 있다. 설정 키와 그 허용을 바꾸는 수리는 동결문 177행 (라)가 상신을 지정한 것이다. 관문 8도 대조했다. 선택지 1과 2는 확인된 결함의 제거나 수정을 포함한다. 추천은 세 선택지의 최종 상태를 견주며, 편집 권한이나 승인 절차를 이점으로 세우지 않는다. 결함을 남기는 선택지 2를 추천하지도 않는다.
> ### 원인
> 받아들이는 설정 필드가 쓰는 곳보다 넓다.
> ### 크기
> 사용자가 준 ORCID·GitHub가 꾸러미에 실렸다고 오해하게 하고, 쓰이지 않는 입력 둘이 남는다.
> ### 클래스
> 없음
> ### 상신안
> 선택지 1(두 키를 걷고 문서와 시험 설정에서 뺀다), 2(키를 두고 쓰이지 않음을 문서에 적는다), 3(README에 싣는다)은 서로 다른 최종 상태를 낳는다. 그리고 「configurable name and others」가 두 필드를 뜻했는지는 사용자만 정할 수 있다. 추천인 선택지 1은 가이드와 프로그램이 같은 세 필드를 말하게 하고, 쓰이지 않는 입력을 남기지 않는다. 그 대가로 두 키를 가진 설정 파일은 거절된다.
>

### 심사 산출 심사_3.md의 판정

> 판정: 승인
> 처분: 사용자에게 올린다
> ### 실측
> `orcid`와 `github`는 `finalize.py` 95·97행, `operations.md` 472행, 시험 두 곳에만 나온다(`grep`으로 확인). 저자 줄(1742~1743행), `formalization.yaml`, README는 `name`, `address`, `email` 가운데 일부만 싣는다. 꾸러미 합의 19행과 맥락 문서 289행에서 사용자의 말은 「configurable name and others」이고, 합의의 풀이는 그것을 「the other title-page fields」라고 적는다.
> ### 원인
> 설정이 받아들이는 필드가 꾸러미의 어떤 출력과도 이어지지 않는다.
> ### 크기
> 운영자가 사용자에게 쓰이지 않는 정보를 묻고, 사용자는 그것이 실렸다고 여긴다.
> ### 클래스
> 없음
> ### 상신안
> 선택지 셋은 모두 확인된 결함(받기만 하고 쓰이지 않는 입력과 그것을 약속하는 표)을 다룬다. 1은 입력을 없애고, 2는 그 사실을 문서에 적고, 3은 출력을 더한다. 키를 걷는 수리는 동결문 불변식 (라)가 상신 제안으로 지정한 것이어서 조각으로 낼 수 없다. 2와 1의 최종 상태가 비동등하므로 상신이 선다. 추천 1은 승인 뒤의 최종 상태를 견주어 고른 것이다. 편집 권한이나 승인 절차를 이점으로 세우지 않았고, 결함을 남기는 선택지를 추천하지 않았다. 「the other title-page fields」의 풀이로 보면 추천은 사용자의 말을 좁히지 않는다. 다만 「others」의 범위는 사용자만 정할 수 있으므로 올리는 것이 맞다.
>
