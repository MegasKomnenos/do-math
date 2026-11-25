# 라운드 1 — 승인되었으나 적용하지 않은 항목

라운드 1의 심사에서 승인이 확정되었으나 적용에서 뺀 항목 41건의 원문이다. 라운드 사본을 뜬 뒤 런 밖의 커밋이 산출물 원본을 바꾸었고, 이 항목들은 바뀐 파일에 조각을 두고 있다. 좌표와 축자는 그 라운드의 사본 기준이어서 지금의 원본과 맞지 않을 수 있다. 처리의 경위는 장부의 신호 처리 절에 있다. 이 파일은 런의 중간물이며 수리자, 병합자, 심사자에게 주지 않는다. 종료 보고가 이 항목들의 결함이 마지막 트리에 남았는지를 맞대어 적는다.

## R1-08
제목: 운영자 문서가 review와 organizer의 재개를 적으면서 재개하지 않는 한 경우를 빠뜨린다

### 위치
`.claude/skills/do-math/reference/operations.md` 600행. 「출력이 전송 검사를 통과하지 못하면 호스트가 같은 대화를 재개한다」와 「`output_checked`는 검사가 통과했을 때의 근거다」의 두 서술.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 128행.

```
그 독자에게 맞지 않는 내용, 같은 사항에 대해 가이드끼리 어긋나는 서술, 코드의 실제 동작과 어긋나는 서술, 더는 없는 것을 말하는 서술, 의도를 정확히 전하지 못하는 서술이 결함이다.
```

코드의 실제 동작. `.claude/skills/do-math/runtime/ending.py` 219~226행.

```
        if output_role:
            # The session is done when its output passes the check the runner makes of it. What the check
            # finds is what the next turn is told; a candidate that changed is the runner's to restore.
            problems = output_problems(session)
            if not problems or problems == [CANDIDATE_CHANGED]:
                authorize(session, state, 'runner', 'output_checked',
                          'The transport check of the output passed.' if not problems else problems[0])
                return result
```

### 영향
`status`는 세션마다 호스트의 `end_check` 기록을 보여 준다. 후보가 배정 뒤에 바뀐 review는 재개 없이 `output_checked`로 끝나고 설명에 `candidate changed after review assignment`가 적힌다. 600행만 읽은 운영자는 `output_checked`를 검사 통과로 읽으므로, 바로 뒤에 그 작업이 다시 대기로 돌아가고 후보가 복원되거나 peer가 바뀌는 것을 보면 통과한 review가 버려졌다고 진단하게 된다. 그 경우에 실행기가 하는 일은 같은 문서의 「Refusals, failed outputs and damaged candidates」 절(642행)에 이미 있으므로, 600행 끝에 그 경우와 그 절을 가리키는 두 문장을 더한다. 기존 문장은 그대로 둔다.

### 조각 1 — .claude/skills/do-math/reference/operations.md 600~600행
원래:
```
The host of a review or an organizer keeps its session alive in the same way, for a different reason. Such a session ends with its output, an assessment or an organization, and writes no end decision. When one of its turns ends and the output does not pass the transport check, the host resumes the same conversation and tells it what the check found, at most `max_end_resumptions` times. A reviewer's turn can end while the sub-reviewers it delegated to are still at work, and without this the whole review would be made again by a new session. The authorization in the session's `end_check` record then has the basis `output_checked` when the check passed, and `resumption_limit` when it still failed at the limit; in the second case the runner starts a new session for the stage, as it does after an interruption.
```
대체:
```
The host of a review or an organizer keeps its session alive in the same way, for a different reason. Such a session ends with its output, an assessment or an organization, and writes no end decision. When one of its turns ends and the output does not pass the transport check, the host resumes the same conversation and tells it what the check found, at most `max_end_resumptions` times. A reviewer's turn can end while the sub-reviewers it delegated to are still at work, and without this the whole review would be made again by a new session. The authorization in the session's `end_check` record then has the basis `output_checked` when the check passed, and `resumption_limit` when it still failed at the limit; in the second case the runner starts a new session for the stage, as it does after an interruption. One finding of the check is not put to the session, because no further turn can remove it: that the candidate under review changed after the review was assigned. The host then resumes nothing and records `output_checked` with that finding as the explanation, and the runner deals with the candidate as "Refusals, failed outputs and damaged candidates" below describes.
```


## R1-11
제목: 운영자 문서가 컴파일의 비중을 앞 설계와 견주어 적는다

### 위치
`.claude/skills/do-math/reference/operations.md` 225행의 구절 `in this design compiles carry more of the work than before`.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 134행.

```
넷째는 세 갈래를 가로지르는 손상이다. 이번 주에 걷어 낸 기능의 잔재, 쓰이지 않는 코드와 인자, 코드나 시험이 한 규칙을 두 군데에 따로 구현한 것과 그 둘 사이의 어긋남, 앞 상태를 서술하는 주석과 문서, 이 기계에만 맞는 경로와 수치가 여기에 든다.
```

### 영향
「than before」가 가리키는 것은 넷째 세대 이전의 설계다. 이 문서를 읽는 운영자는 그 설계를 받지 않았으므로 무엇보다 많다는 것인지 알 수 없고, 견줌에서 얻는 것이 없다. 문단이 운영자에게 주는 것은 그 뒤의 내용, 곧 어떤 일들이 컴파일인지와 그래서 동시에 도는 컴파일의 수가 연구의 속도에 걸린다는 것이다. 수리는 견줌의 구절만 「compiles carry much of the work」로 바꾸고 나머지 문장과 열거를 그대로 둔다. 지우는 글이 주던 것은 없다. 값을 치르는 것은 Windows에서 컴파일이 메모리를 기다리는 까닭을 찾아 이 절을 여는 모든 운영자다.

### 조각 1 — .claude/skills/do-math/reference/operations.md 225~225행
원래:
```
All Lean compilation of an instance goes through its broker, and in this design compiles carry more of the work than before: sessions compile what they state, a peer's candidate is built before it is frozen, review builds it again, and every publication that changes a Lean file is a build of the library. How many compiles can run at once therefore bears on how fast the research moves.
```
대체:
```
All Lean compilation of an instance goes through its broker, and compiles carry much of the work: sessions compile what they state, a peer's candidate is built before it is frozen, review builds it again, and every publication that changes a Lean file is a build of the library. How many compiles can run at once therefore bears on how fast the research moves.
```


## R1-12
제목: 지도와 논문의 절이 두 명령을 「전에는 손으로 만들던 것」으로 소개한다

### 위치
`.claude/skills/do-math/reference/operations.md` 373행.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 134행.

```
넷째는 세 갈래를 가로지르는 손상이다. 이번 주에 걷어 낸 기능의 잔재, 쓰이지 않는 코드와 인자, 코드나 시험이 한 규칙을 두 군데에 따로 구현한 것과 그 둘 사이의 어긋남, 앞 상태를 서술하는 주석과 문서, 이 기계에만 맞는 경로와 수치가 여기에 든다.
```

### 영향
373행은 두 명령이 무엇을 만드는지를 이름으로 말하지 않고 「연구가 끝난 뒤 전에는 손으로 만들던 것」이라고 적는다. 운영자는 전에 무엇을 손으로 만들었는지 받은 적이 없으므로 이 문장에서 두 명령의 산출을 알 수 없다. 또 「after a research had ended」는 지도 명령에 맞지 않는다. 같은 절 377행은 지도 명령이 인스턴스가 도는 동안을 포함해 언제든 돌 수 있다고 적는다. 수리는 두 명령의 산출을 이름으로 적는다. 지우는 구절이 주던 것은 없고, 두 산출의 이름은 절 제목과 `SKILL.md` 66행에 같은 말로 있다.

### 조각 1 — .claude/skills/do-math/reference/operations.md 373~373행
원래:
```
Two further commands produce, from the canon, what was formerly made by hand after a research had ended.
```
대체:
```
Two further commands produce the dependency map and the paper from the canon.
```


## R1-13
제목: 색인 보기의 설명이 넷째 세대에 없는 survey를 든다

### 위치
`.claude/skills/do-math/reference/operations.md` 321행의 구절 `and it has no surveys`.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 128행.

```
그 독자에게 맞지 않는 내용, 같은 사항에 대해 가이드끼리 어긋나는 서술, 코드의 실제 동작과 어긋나는 서술, 더는 없는 것을 말하는 서술, 의도를 정확히 전하지 못하는 서술이 결함이다.
```

### 영향
survey는 앞 세대에서 organizer가 색인의 모듈마다 써 붙이던 글이다(`docs/do-math/lean-canon-design.md` 47행의 표가 그것을 「each module with a written survey」로 적는다). 넷째 세대의 운영자 문서 둘은 이 낱말을 이 자리에서만 쓰고 뜻을 주지 않는다. 운영자는 색인 보기에 없다는 survey가 무엇인지 알 수 없다. 운영자가 이 자리에서 얻어야 할 것, 곧 이 보기를 아무도 손으로 쓰지 않는다는 것은 같은 문장의 앞 절이 말한다. 수리는 뒤 절만 지운다. 지우는 글이 주던 것은 없다.

### 조각 1 — .claude/skills/do-math/reference/operations.md 321~321행
원래:
```
`knowledge/index.md` is the derived index: every element of the canon, grouped by module, with modules and elements in the order of their names, each with its weight, its standing and its self-description. A definition has no standing and is shown with its kind. Nobody writes this view, and it has no surveys. Use it to see everything the canon holds, including the elements the root does not rest on, which the frontier does not show.
```
대체:
```
`knowledge/index.md` is the derived index: every element of the canon, grouped by module, with modules and elements in the order of their names, each with its weight, its standing and its self-description. A definition has no standing and is shown with its kind. Nobody writes this view. Use it to see everything the canon holds, including the elements the root does not rest on, which the frontier does not show.
```


## R1-36
제목: wide_lines가 참고문헌 파일 paper.bbl의 줄 번호를 paper.tex의 줄로 보고한다

### 위치
`.claude/skills/do-math/runtime/paper.py` 1890~1903행의 `wide_lines`다. 이 함수의 반환을 원고의 절로 돌리는 자리는 같은 파일 3765~3766행(`settle`)과 1949~1951행(`part_at`)이다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 122행이 이 갈래를 정한다.

```
첫째는 코드의 결함이다. 실제 입력, 상태, 동시 실행, 실패 경로, Windows와 Linux의 프로세스·파일 동작에서 의도한 동작이 깨지는 것이 여기에 든다.
```

의도한 동작은 방법 문서가 적는다. `.claude/skills/do-math/reference/paper-method.md` 259행과 261행이다.

```
A line that TeX set more than a few points wider than the text block, so that it stands out into the margin, goes to repair in the same way.
```

```
What a check or a reader found in one section goes to a session that repairs that section and no other.
```

### 영향
TeX은 로그에 넘친 줄을 「지금 읽고 있는 파일」의 줄 번호로 적는다. 원고의 마지막 명령 `\bibliography{references}`에서 TeX은 `paper.bbl`을 읽기 시작하고, 그 뒤에 적히는 줄 번호는 `paper.bbl`의 것이다. 실제 운전의 로그 두 편이 이 꼴을 보인다. `.skill-workspace/parking-staircase/paper-out-2/typeset/paper.log` 192~193행은 아래와 같고, `.skill-workspace/parking-root-paper/paper-out3/typeset/paper.log` 179~180행도 같은 꼴이다.

```
[196] [197] [198] [199] [200] [201] [202] [203] [204] [205] [206] (paper.bbl
Underfull \hbox (badness 2012) in paragraph at lines 76--78
```

이 두 로그에서 `paper.bbl` 안의 줄은 `Underfull`이어서 `OVERFULL`(286~287행)에 걸리지 않았다. 참고문헌 항목 하나가 5pt 넘게 넘치면 TeX은 같은 자리에 `Overfull \hbox (…pt too wide) in paragraph at lines 76--78`을 적고, `wide_lines`는 로그 전체에서 이 꼴을 찾으므로 `paper.tex, lines 76 to 78: TeX set a line …pt wider than the text block`을 돌려준다. `settle`은 그 번호를 `part_at`으로 `paper.tex`의 76행이 든 절에 돌리고, 그 절의 수리 세션은 넘치지 않은 줄을 넘쳤다고 듣는다. 세션이 그 줄을 고치면 멀쩡한 글이 바뀐다. 세션이 아무 part도 바꾸지 않으면 3852~3854행이 그 산출을 쓸 수 없는 것으로 치고, 두 번째 세션도 그러면 운전이 종료 코드 1로 끝난다. `--resume`은 다시 `settle`부터 하므로 같은 자리에서 다시 끝난다. 참고문헌은 어느 세션도 바꿀 수 없다. `references.bib`는 정본의 서지를 옮긴 것이고(3715행), part는 서지 명령을 쓸 수 없다(278~280행).

실제 운전에서 참고문헌의 `Overfull`은 관찰되지 않았다. 확인한 것은 로그의 꼴과 코드의 경로다.

수리는 로그를 `paper.bbl`을 읽기 시작하는 자리까지만 읽게 한다. part의 문단과 수식은 `\bibliography` 명령보다 앞에서 조판되므로, 그 자리 앞에 적힌 줄만이 `paper.tex`의 줄이다. TeX은 꽉 찬 로그 줄을 아무 글자에서나 끊으므로 파일 이름 안의 줄바꿈도 받는다. 이 수리 뒤에 참고문헌 안의 넘친 줄은 보고되지 않는다. 지금도 그 줄은 제 이름으로 보고된 적이 없고, 그것을 따로 보고하게 하는 것은 이 항목이 다루지 않는다. 시험 조각은 `paper.bbl` 뒤의 줄이 빠지는 것을 두 꼴(이름이 한 줄에 있는 로그, 이름 안에서 줄이 끊긴 로그)로 단언한다. 수리 전의 함수는 두 단언에서 실패한다.

### 조각 1 — .claude/skills/do-math/runtime/paper.py 1890~1899행
원래:
```
def wide_lines(log):
    """The lines that TeX set wider than the text block by more than WIDE_PT, as its log reports them.

    TeX reports such a line as a warning and typesets the paper all the same, with the line standing
    out into the margin."""
    log = Path(log)
    if not log.is_file():
        return []
    found = []
    for width, single, first, last in OVERFULL.findall(log.read_text(encoding='utf-8', errors='replace')):
```
대체:
```
# TeX names a file that it begins to read after an opening parenthesis, and the lines it reports from there on are
# lines of that file. Its log breaks a line that is full at any character, also inside such a name.
BIBLIOGRAPHY_READ = re.compile(r'\(\n?(?:\.\n?/\n?)?' + r'\n?'.join(re.escape(char) for char in 'paper.bbl'))


def wide_lines(log):
    """The lines of paper.tex that TeX set wider than the text block by more than WIDE_PT, as its log reports them.

    TeX reports such a line as a warning and typesets the paper all the same, with the line standing
    out into the margin. After the parts TeX reads the bibliography, paper.bbl, and a line that it
    reports from there on is a line of that file: no part holds it and no session can change it. So
    the log is read up to the place where TeX begins to read paper.bbl."""
    log = Path(log)
    if not log.is_file():
        return []
    found = []
    text = BIBLIOGRAPHY_READ.split(log.read_text(encoding='utf-8', errors='replace'), maxsplit=1)[0]
    for width, single, first, last in OVERFULL.findall(text):
```

### 조각 2 — .claude/skills/do-math/runtime/tests/test_paper.py 882~886행
원래:
```
                           'Overfull \\hbox (69.23543pt too wide) detected at line 31\n', encoding='utf-8')
            self.assertEqual(paper.wide_lines(log),
                             ['paper.tex, line 31: TeX set a line 69pt wider than the text block',
                              'paper.tex, lines 40 to 44: TeX set a line 12pt wider than the text block',
                              'paper.tex, lines 50 to 53: TeX set a line 7pt wider than the text block'])
```
대체:
```
                           'Overfull \\hbox (69.23543pt too wide) detected at line 31\n'
                           # After the parts TeX reads paper.bbl; the lines it reports there are lines of that file.
                           '[12] [13] (paper.bbl\n'
                           'Overfull \\hbox (30.5pt too wide) in paragraph at lines 7--9\n'
                           '[14]) (paper.aux) )\n', encoding='utf-8')
            self.assertEqual(paper.wide_lines(log),
                             ['paper.tex, line 31: TeX set a line 69pt wider than the text block',
                              'paper.tex, lines 40 to 44: TeX set a line 12pt wider than the text block',
                              'paper.tex, lines 50 to 53: TeX set a line 7pt wider than the text block'])
            # The log breaks a full line at any character, also inside the name of the file TeX begins to read.
            log.write_text('Overfull \\hbox (12.4pt too wide) in paragraph at lines 40--44\n'
                           '[12] [13] (./pap\ner.bbl\n'
                           'Overfull \\hbox (30.5pt too wide) in paragraph at lines 7--9\n', encoding='utf-8')
            self.assertEqual(paper.wide_lines(log),
                             ['paper.tex, lines 40 to 44: TeX set a line 12pt wider than the text block'])
```


## R1-40
제목: PLAN_PROMPT와 DRAFT_PLAN_PROMPT는 어느 프롬프트도 만들지 않는 상수이고, 시험 하나가 실제 프롬프트 대신 그 상수를 단언한다

### 위치
`.claude/skills/do-math/runtime/paper.py` 2090~2091행의 두 상수와 그것을 이름으로 드는 3407행의 주석, 그리고 `.claude/skills/do-math/runtime/tests/test_paper.py` 2837행의 단언이다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 134행과 132행이 이 갈래를 정한다.

```
넷째는 세 갈래를 가로지르는 손상이다. 이번 주에 걷어 낸 기능의 잔재, 쓰이지 않는 코드와 인자, 코드나 시험이 한 규칙을 두 군데에 따로 구현한 것과 그 둘 사이의 어긋남, 앞 상태를 서술하는 주석과 문서, 이 기계에만 맞는 경로와 수치가 여기에 든다.
```

```
셋째는 시험의 결함이다. 사용자의 요구는 넷이다. 실제 생산 경로로 의도한 동작을 검증하는가. 대상이 벗어나면 실패할 수 있는가.
```

### 영향
계획 세션의 프롬프트는 `make_plan`이 3408~3409행에서 조각들을 직접 이어 만든다. `PLAN_PROMPT`와 `DRAFT_PLAN_PROMPT`를 읽는 코드는 스킬 어디에도 없다. `runtime/`과 `reference/`를 두 이름으로 검색한 결과는 정의 두 줄, 3407행의 주석, `test_paper.py` 2837행뿐이다. 프롬프트를 고치려고 이 파일을 읽는 다음 사람은 같은 프롬프트의 조립을 두 군데에서 만나고, 상수를 고쳐도 세션이 받는 글은 바뀌지 않는다.

2837행은 「초안이 아닌 운전의 계획 프롬프트는 인용할 결과의 목록을 묻지 않는다」를 그 상수에 대고 단언한다. `make_plan`이 초안이 아닌 운전에도 `PLAN_CITATIONS`를 넣게 바뀌어도 상수는 그대로이므로 이 단언은 통과한다. 단언이 지키려는 동작을 실제로 지나가는 자리는 `RunTests.test_one_command_leaves_the_paper_and_what_stands_beside_it`의 `calls[0]`이다. 이 호출은 초안이 아닌 운전의 첫 계획 세션이고(973행, 982~984행), 그 프롬프트는 1006~1007행에서 이미 읽힌다. 그 프롬프트를 이루는 조각(`PLAN_OPENING`, `PLAN_KEYS`, `PLAN_NOTATION`, `PLAN_ACCEPTS`, `PLAN_CLOSING`, 빈 `main_note`)에는 `"citations"`라는 글자가 없고, `PLAN_CITATIONS`에만 있다.

수리는 두 상수를 지우고, 주석을 상수의 이름 없이 같은 사실을 말하게 고치며, 단언을 실제 프롬프트로 옮긴다. 옮긴 단언은 `make_plan`이 초안이 아닌 운전에 그 목록을 묻게 되면 실패한다. 2836행과 2838행의 단언(초안의 계획은 목록을 묻고, 목록 없는 계획은 받지 않는다)은 그대로 둔다.

### 조각 1 — .claude/skills/do-math/runtime/paper.py 2090~2091행
원래:
```
PLAN_PROMPT = PLAN_OPENING + PLAN_KEYS + PLAN_NOTATION + PLAN_ACCEPTS + PLAN_CLOSING
DRAFT_PLAN_PROMPT = PLAN_OPENING + PLAN_KEYS + PLAN_CITATIONS + PLAN_NOTATION + PLAN_ACCEPTS + PLAN_CLOSING
```
대체:
```

```

### 조각 2 — .claude/skills/do-math/runtime/paper.py 3407~3407행
원래:
```
        # The same text as PLAN_PROMPT or DRAFT_PLAN_PROMPT when the declaration that settles the root is the main result.
```
대체:
```
        # main_note adds its paragraph only when the main result is another element than the one that settles the root.
```

### 조각 3 — .claude/skills/do-math/runtime/tests/test_paper.py 1007~1007행
원래:
```
        self.assertIn('output/study.md', calls[0]['prompt'])
```
대체:
```
        self.assertIn('output/study.md', calls[0]['prompt'])
        # Only the plan of a draft is asked for the results that the paper would cite.
        self.assertNotIn('"citations"', calls[0]['prompt'])
```

### 조각 4 — .claude/skills/do-math/runtime/tests/test_paper.py 2835~2837행
원래:
```
        # Only the plan of a draft is asked for the results to cite, and it is not accepted without the list.
        self.assertIn('"citations"', calls[0]['prompt'])
        self.assertNotIn('"citations"', paper.PLAN_PROMPT)
```
대체:
```
        # The plan of a draft is asked for the results to cite, and it is not accepted without the list.
        self.assertIn('"citations"', calls[0]['prompt'])
```


## R1-41
제목: machine_checks는 시험만 부르는 함수다

### 위치
`.claude/skills/do-math/runtime/paper.py` 1830~1832행의 `machine_checks`와, 그것을 부르는 `.claude/skills/do-math/runtime/tests/test_paper.py` 709행, 759행, 804행이다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 134행이 이 갈래를 정한다.

```
넷째는 세 갈래를 가로지르는 손상이다. 이번 주에 걷어 낸 기능의 잔재, 쓰이지 않는 코드와 인자, 코드나 시험이 한 규칙을 두 군데에 따로 구현한 것과 그 둘 사이의 어긋남, 앞 상태를 서술하는 주석과 문서, 이 기계에만 맞는 경로와 수치가 여기에 든다.
```

### 영향
프로그램이 원고의 기계 검사에 쓰는 함수는 `machine_findings`다. `settle`이 3750~3751행에서 그것을 불러 문제의 문장과 part를 함께 받는다. `machine_checks`는 그 결과에서 문장만 뽑는 한 줄이고, `runtime/` 전체에서 이것을 부르는 자리는 `test_paper.py`의 세 줄뿐이다. 프로그램을 읽는 다음 사람은 기계 검사의 입구를 둘 만나고, 어느 쪽이 운전에서 쓰이는지를 호출처를 찾아 가려야 한다.

수리는 그 함수를 지우고, 시험의 도우미 `ManuscriptTests.problems`가 `machine_findings`를 직접 부르게 한다. 도우미가 계획을 인자로 받게 하면 759행과 804행도 같은 도우미를 지나가므로, 시험이 프로그램의 함수를 부르는 자리는 하나가 된다. 세 자리의 단언과 그것이 받는 문자열은 그대로다. 문제의 문장을 ` | `로 이은 문자열은 바뀌기 전과 같은 값이다. `ManuscriptTests`의 다른 메서드는 `problems`를 인자 없이, 또는 part 이름을 키워드로만 부르므로(712행, 733~793행) 첫 자리에 계획을 받게 해도 호출이 달라지지 않는다. `PLAN`은 275행에서 정의되어 클래스 본문이 읽힐 때 이미 있다.

### 조각 1 — .claude/skills/do-math/runtime/paper.py 1827~1832행
원래:
```
    return found_problems


def machine_checks(materials, plan, parts):
    """What a machine can check in the manuscript, as sentences for a repair session; empty when all hold."""
    return [finding['problem'] for finding in machine_findings(materials, plan, parts)]
```
대체:
```
    return found_problems
```

### 조각 2 — .claude/skills/do-math/runtime/tests/test_paper.py 708~709행
원래:
```
    def problems(self, **changed):
        return ' | '.join(paper.machine_checks(self.materials(), PLAN, {**PARTS, **changed}))
```
대체:
```
    def problems(self, plan=PLAN, **changed):
        return ' | '.join(finding['problem'] for finding in
                          paper.machine_findings(self.materials(), plan, {**PARTS, **changed}))
```

### 조각 3 — .claude/skills/do-math/runtime/tests/test_paper.py 759~759행
원래:
```
        self.assertIn('the title: ' + said + 'Lean', ' | '.join(paper.machine_checks(self.materials(), plan, PARTS)))
```
대체:
```
        self.assertIn('the title: ' + said + 'Lean', self.problems(plan))
```

### 조각 4 — .claude/skills/do-math/runtime/tests/test_paper.py 804~804행
원래:
```
        check = lambda text: ' | '.join(paper.machine_checks(self.materials(), plan, {**PARTS, 'tools': text}))
```
대체:
```
        check = lambda text: self.problems(plan, tools=text)
```


## R1-42
제목: fetch.py는 중간에 끊긴 내려받기를 만나면 그 논문을 FAILED로 적지 못하고 스크립트 전체가 예외로 끝난다

### 위치
`.claude/skills/do-math/exemplars/fetch.py` 108~110행(`unpack`의 gzip 풀기)이다. 그 예외를 받지 못하는 자리는 같은 파일 382~387행(`main`)이다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 122행이 이 갈래를 정한다.

```
첫째는 코드의 결함이다. 실제 입력, 상태, 동시 실행, 실패 경로, Windows와 Linux의 프로세스·파일 동작에서 의도한 동작이 깨지는 것이 여기에 든다.
```

의도한 동작은 스크립트 자신의 설명(`exemplars/fetch.py` 30~31행)과 `exemplars/README.md` 13행이 적는다.

```
An archive is untrusted data.  It is unpacked in memory only, member names
with an absolute path or a ".." are refused, and nothing from it is executed.
```

```
The script downloads the source of every paper that is missing or differs from the manifest, joins it into a single file and checks its SHA-256.
```

### 영향
`main`은 논문마다 `build(download(...))`를 부르고 `BuildError`만 받아 「FAILED」 한 줄을 적은 뒤 다음 논문으로 간다(382~387행). 내려받기가 중간에 끊기면 이 경로를 벗어난다. `_request`는 `resp.read(MAX_BYTES + 1)`로 읽는데(71행), 이 기계의 Python 3.12.10에서 `http.client`의 `read(amt)`는 Content-Length에 못 미친 채 연결이 끝나도 예외 없이 받은 만큼을 돌려준다(`Lib/http/client.py` 475~488행, 「Ideally, we would raise IncompleteRead if the content-length wasn't satisfied, but it might break compatibility.」). 잘린 바이트는 gzip의 머리 두 바이트를 가졌으므로 109~110행으로 가고, `GzipFile.read`는 `EOFError`를 낸다(`Lib/gzip.py` 563~565행, 「Compressed file ended before the end-of-stream marker was reached」). 손상된 스트림이면 `gzip.BadGzipFile`이나 `zlib.error`가 난다. 셋 다 `BuildError`가 아니므로 `main`을 뚫고 나가 스크립트가 역추적과 함께 끝나고, 매니페스트에서 그 뒤에 오는 논문은 받지 않는다.

이 값은 논문 명령을 처음 돌리는 기계가 치른다. `runtime/paper.py`의 `load_collection`은 빠진 논문이 있으면 `fetch.py`를 한 번 돌리고(419~421행), 그 뒤에도 빠진 것이 있으면 멈춘다(430~435행). 논문 서른두 편 가운데 하나의 내려받기가 끊기면, 끊긴 논문 하나만 다시 받으면 될 일이 그 뒤의 논문 전부를 다시 받는 일이 되고, 운영자가 받는 것은 「FAILED」 줄이 아니라 역추적의 끝 열 줄이다.

수리는 gzip을 푸는 자리에서 그 세 예외를 `BuildError`로 바꾼다. 그러면 `main`의 기존 경로가 그 논문을 FAILED로 적고 다음으로 간다. 파일에 쓰는 바이트를 만드는 경로(`flatten`, `drop_comments`, `cut_after_end`)는 건드리지 않으므로 `manifest.json`의 해시와 맞는 결과는 달라지지 않는다. 시험은 이 스크립트를 지나가는 것이 없었으므로 하나를 더한다. 시험은 실제 `fetch.py`의 `main`을 부르고, 네트워크 경계인 `download`만 대역으로 바꾼다. 첫 논문의 원문은 끝이 잘린 gzip이고 둘째 논문의 원문은 온전하다. 수리 전에는 `main`이 `EOFError`로 끝나 시험이 실패한다. 수리 뒤에는 종료 코드가 1이고, 첫 논문은 쓰이지 않으며, 둘째 논문이 쓰인다.

### 조각 1 — .claude/skills/do-math/exemplars/fetch.py 행 46 뒤
대체:
```
import zlib
```

### 조각 2 — .claude/skills/do-math/exemplars/fetch.py 109~110행
원래:
```
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as gz:
            data = gz.read(MAX_BYTES + 1)
```
대체:
```
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as gz:
                data = gz.read(MAX_BYTES + 1)
        except (OSError, EOFError, zlib.error) as exc:
            raise BuildError("the e-print cannot be unpacked: %s" % exc)
```

### 조각 3 — .claude/skills/do-math/runtime/tests/test_paper.py 110~111행
원래:
```
import copy
import hashlib
```
대체:
```
import copy
import gzip
import hashlib
import importlib.util
```

### 조각 4 — .claude/skills/do-math/runtime/tests/test_paper.py 930~930행
원래:
```
        self.assertEqual(paper.likeness_papers(manifest, CHOSEN), FIRST_FOUR + NEXT_FOUR)
```
대체:
```
        self.assertEqual(paper.likeness_papers(manifest, CHOSEN), FIRST_FOUR + NEXT_FOUR)


class FetchScriptTests(unittest.TestCase):
    """The collection's own fetch.py. Only the download is stood in for, since it is the network."""

    def test_a_source_that_cannot_be_unpacked_fails_its_paper_and_the_next_paper_is_still_fetched(self):
        spec = importlib.util.spec_from_file_location('exemplars_fetch', paper.EXEMPLARS / 'fetch.py')
        fetch = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fetch)
        source = exemplar('beta').encode('utf-8')
        built = fetch.build(source)
        # The first download ended early, so its compressed stream lacks its end; the second is whole.
        sources = {'1001.0001v1': gzip.compress(source)[:-12], '1001.0002v1': source}
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            write_json(folder / 'manifest.json', [
                {'key': 'alpha', 'arxiv': '1001.0001v1', 'sha256': hashlib.sha256(built).hexdigest()},
                {'key': 'beta', 'arxiv': '1001.0002v1', 'sha256': hashlib.sha256(built).hexdigest()}])
            with patch.object(fetch, 'HERE', str(folder)), patch.object(fetch, 'download', side_effect=sources.get), \
                    patch('builtins.print') as shown:
                self.assertEqual(fetch.main([]), 1)
            said = [call.args[0] for call in shown.call_args_list]
            self.assertTrue(any(line.startswith('alpha: FAILED, the e-print cannot be unpacked') for line in said), said)
            self.assertFalse((folder / 'alpha.tex').exists())
            self.assertEqual((folder / 'beta.tex').read_bytes(), built)
```


## R1-50
제목: 논문 명령의 --model과 --effort를 지나가는 시험이 없다

### 위치
`.claude/skills/do-math/runtime/tests/test_paper.py` 전체에서 `--model`은 1780행에 한 번, `--tex` 뒤에 놓여 거절되는 인자로만 나오고 `--effort`는 나오지 않는다. 시험되지 않는 동작은 `.claude/skills/do-math/runtime/paper.py` 5222~5228행(`choice`를 세 진입점에 넘김)과 3301~3305행(`Paper.__init__`이 `choice`로 쓰는 쪽과 읽는 쪽의 모델을 정함)이다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 132행:

```
넷 가운데 하나를 어긴 시험, 어떤 시험도 알아채지 못할 동작, 확인하는 것에 견주어 지나치게 오래 걸리는 시험, 한 번의 실행 뒤에 남는 찌꺼기가 결함이다.
```

`.claude/skills/do-math/reference/operations.md` 407행:

```
`--model <provider/model>`, for example `claude/opus`, puts every session on that one model, the reading and the comparison included. `--effort <level>` sets the effort of planning, writing and repair, and of every session when `--model` is given with it.
```

### 영향
운영자 문서가 약속하는 두 옵션의 동작을 어떤 시험도 지나가지 않는다. `paper.py` 5227행이 `choice` 자리에 `None`을 넘겨도, 3304~3305행을 지워 `--model`을 준 운전에서 독해와 대조가 `review` 역할의 모델로 남아도, 3304행의 조건이 `--effort`만 준 운전에서도 참이 되게 바뀌어도 102건이 모두 통과한다. 운영자는 `--model`로 한 모델에 모았다고 믿는 운전에서 독해가 다른 모델로 돌거나, `--effort`만 주었는데 독해 모델이 바뀌는 것을 운전 뒤 `session.json`을 열어 보아야 안다. 조각 1은 이미 `paper.main`으로 도는 초안 시험에 두 옵션을 주고 모든 세션의 `session.json`을 단언한다. 그 시험은 모델을 단언하지 않았고, 기본 모델로 도는 초안은 같은 클래스의 둘째 시험(2893~2909행)이 `produce`로 지나가며, 기본 모델의 선택은 1070~1075행이 단언한다. 새 운전을 더하지 않으므로 세션 수와 시간은 그대로다. 조각 2는 `--effort`만 준 경우를 세션을 띄우지 않고 `Paper`에서 단언한다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_paper.py 2829~2831행
원래:
```
        with patch('paper.worker_command', side_effect=self.command), patch('builtins.print'):
            self.assertEqual(paper.main([str(self.instance), '--out', str(self.out), '--parallel', '1', '--draft', '--tex', *TEX]), 0)
        calls = self.calls()
```
대체:
```
        with patch('paper.worker_command', side_effect=self.command), patch('builtins.print'):
            self.assertEqual(paper.main([str(self.instance), '--out', str(self.out), '--parallel', '1', '--draft',
                                         '--model', 'claude/sonnet', '--effort', 'low', '--tex', *TEX]), 0)
        calls = self.calls()
        # --model puts every session on that model, the comparison included, and --effort with it is their effort.
        self.assertEqual({tuple(read_json(self.folder(call) / 'session.json')[key] for key in ('model', 'effort'))
                          for call in calls}, {('claude/sonnet', 'low')})
```

### 조각 2 — .claude/skills/do-math/runtime/tests/test_paper.py 2694~2694행
원래:
```
        self.assertTrue(issubclass(paper.Paper, paper.Sessions))
```
대체:
```
        self.assertTrue(issubclass(paper.Paper, paper.Sessions))
        # --effort without --model is the effort of the writer alone; the assessor stays as the review role has it.
        alone = paper.Paper(self.instance, out, TEX, {'model': None, 'effort': 'low'})
        self.assertEqual((alone.writer, alone.assessor),
                         ({'model': first['model'], 'effort': 'low'}, {'model': 'claude/opus', 'effort': 'high'}))
```


## R1-54
제목: TeX 명령이 없을 때의 시험이 세 거절의 사유를 고정하지 않는다

### 위치
`.claude/skills/do-math/runtime/tests/test_paper.py` 1326~1327행, 1338~1339행, 1350~1351행(`RunTests.test_without_a_tex_command_everything_else_is_done_and_the_manuscript_is_typeset_later`).

### 기준
`임시/do-math_검증_20261125-2/맥락.md` 866행:

```
- **A test of a refusal fixes the reason for the refusal**, not only that something was refused. Its input starts from what the real producer makes and changes the one thing the test is about, so that the failure can be attributed.
```

### 영향
`paper.Stop`은 이 명령의 모든 거절과 모든 실패한 단계가 올리는 예외다. 세 자리의 `assertRaises(paper.Stop)`은 어떤 거절이든 통과시킨다. 1327행은 TeX 명령이 없다는 거절(`.claude/skills/do-math/runtime/paper.py` 5123행)을 뜻하지만 원고를 찾지 못한다는 거절(5119행)이 나도 통과한다. 1339행은 폴더가 비어 있지 않다는 거절(4917행)을, 1351행은 명령을 찾지 못했다는 거절(1844행)을 뜻하지만 두 자리 모두 `produce`나 `tex_recipe`가 다른 문구의 `Stop`을 내도 통과한다. 조각은 세 자리에 `paper.py`의 그 문구를 고정한다. 입력과 순서는 그대로다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_paper.py 1326~1327행
원래:
```
            with self.assertRaises(paper.Stop):
                self.run_paper(good(), tex=None, only=True)
```
대체:
```
            with self.assertRaisesRegex(paper.Stop, 'no TeX command is available'):
                self.run_paper(good(), tex=None, only=True)
```

### 조각 2 — .claude/skills/do-math/runtime/tests/test_paper.py 1338~1339행
원래:
```
        with self.assertRaises(paper.Stop):
            self.run_paper(good())
```
대체:
```
        with self.assertRaisesRegex(paper.Stop, 'is not empty; give a new folder to --out'):
            self.run_paper(good())
```

### 조각 3 — .claude/skills/do-math/runtime/tests/test_paper.py 1350~1351행
원래:
```
        with self.assertRaises(paper.Stop):
            paper.tex_recipe(['no-such-tex-command'])
```
대체:
```
        with self.assertRaisesRegex(paper.Stop, 'the TeX command no-such-tex-command was not found'):
            paper.tex_recipe(['no-such-tex-command'])
```


## R1-55
제목: 읽히지 않은 원고의 조판 거절을 시험이 사유 없이 단언한다

### 위치
`.claude/skills/do-math/runtime/tests/test_paper.py` 1380~1381행(`RunTests.test_typesetting_later_keeps_what_stayed_open_and_needs_a_run_that_finished_its_checks`).

### 기준
`임시/do-math_검증_20261125-2/맥락.md` 866행:

```
- **A test of a refusal fixes the reason for the refusal**, not only that something was refused. Its input starts from what the real producer makes and changes the one thing the test is about, so that the failure can be attributed.
```

### 영향
이 자리는 기계 검사가 열린 채 끝난 운전의 원고를 `--typeset-only`가 조판하지 않는다는 것(`.claude/skills/do-math/runtime/paper.py` 5129~5132행)을 보려는 것이다. `assertRaises(paper.Stop)`은 `typeset_only`가 올리는 다른 거절, 곧 원고가 없다는 거절(5119행)이나 좁은 수리가 중단되었다는 거절(5152행)로도 통과한다. 세 거절은 운영자에게 서로 다른 조치를 가리키는데(원고가 없다, 앞선 운전이 읽기와 대조를 마치지 않았다, `--resume`으로 먼저 이어라), 시험은 그 가운데 어느 것이 났는지를 가리지 않는다. 조각은 5131행의 문구를 고정한다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_paper.py 1380~1381행
원래:
```
        with self.assertRaises(paper.Stop):
            self.run_paper(script, only=True)
```
대체:
```
        with self.assertRaisesRegex(paper.Stop, 'holds a manuscript whose reading and comparison did not run to their end'):
            self.run_paper(script, only=True)
```


## R1-56
제목: 찾을 수 없는 TeX 엔진의 거절을 시험이 사유 없이 단언한다

### 위치
`.claude/skills/do-math/runtime/tests/test_paper.py` 1775~1776행(`RunTests.test_the_known_engines_are_run_in_the_way_each_needs`).

### 기준
`임시/do-math_검증_20261125-2/맥락.md` 866행:

```
- **A test of a refusal fixes the reason for the refusal**, not only that something was refused. Its input starts from what the real producer makes and changes the one thing the test is about, so that the failure can be attributed.
```

### 영향
이 자리의 `shutil.which` 대역은 `tectonic`을 찾지 못하게 되어 있고, 시험은 `tex_recipe(['tectonic'])`이 `.claude/skills/do-math/runtime/paper.py` 1843~1844행의 거절을 낸다는 것을 보려 한다. `assertRaises(paper.Stop)`만으로는 `tex_recipe`가 다른 까닭으로 멈춰도 통과한다. 조각은 그 문구를 고정한다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_paper.py 1775~1776행
원래:
```
            with self.assertRaises(paper.Stop):
                paper.tex_recipe(['tectonic'])
```
대체:
```
            with self.assertRaisesRegex(paper.Stop, 'the TeX command tectonic was not found'):
                paper.tex_recipe(['tectonic'])
```


## R1-57
제목: 고른 지적 번호의 시험이 두 가지 거절을 가리지 않는다

### 위치
`.claude/skills/do-math/runtime/tests/test_paper.py` 1951~1953행(`PassageTests.test_the_numbers_of_the_chosen_findings`).

### 기준
`임시/do-math_검증_20261125-2/맥락.md` 866행:

```
- **A test of a refusal fixes the reason for the refusal**, not only that something was refused. Its input starts from what the real producer makes and changes the one thing the test is about, so that the failure can be attributed.
```

### 영향
`paper.chosen_numbers`는 두 가지로 거절한다. 번호의 꼴이 아닌 글은 `.claude/skills/do-math/runtime/paper.py` 2976~2977행으로, 목록 밖의 번호는 2980행으로 거절한다. 시험은 여섯 입력이 `Stop`을 낸다는 것만 본다. 2974행의 정규식이 좁아져 두 자리 번호가 꼴에서 거절되면 `'10'`은 목록 밖이라는 문구 대신 꼴이 틀렸다는 문구로 거절되고, 목록이 열 건을 넘는 운전에서는 옳은 번호까지 거절되는데, 이 시험은 통과한다. 조각은 입력마다 어느 거절인지를 문구로 고정한다. `''`, `'two'`, `'1,,2'`는 2974~2977행을, `'0'`, `'4-2'`, `'10'`은 2979~2980행을 지난다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_paper.py 1951~1953행
원래:
```
        for wrong in ('', 'two', '0', '4-2', '10', '1,,2'):
            with self.assertRaises(paper.Stop, msg=wrong):
                paper.chosen_numbers(wrong, 9)
```
대체:
```
        # A text that does not have the form of the numbers is refused as that, and a number outside the list as that.
        for wrong, reason in (('', 'it was given ""'), ('two', 'it was given "two"'), ('1,,2', 'it was given "1,,2"'),
                              ('0', 'the run has 9 open findings'), ('4-2', 'the run has 9 open findings'),
                              ('10', 'the run has 9 open findings')):
            with self.assertRaisesRegex(paper.Stop, reason, msg=wrong):
                paper.chosen_numbers(wrong, 9)
```


## R1-58
제목: 멈춘 운전의 폴더에 새 운전을 거절하는 것을 시험이 사유 없이 단언한다

### 위치
`.claude/skills/do-math/runtime/tests/test_paper.py` 2057~2058행(`SideBySideTests.test_a_run_stopped_between_sections_keeps_what_was_written_and_is_continued`).

### 기준
`임시/do-math_검증_20261125-2/맥락.md` 866행:

```
- **A test of a refusal fixes the reason for the refusal**, not only that something was refused. Its input starts from what the real producer makes and changes the one thing the test is about, so that the failure can be attributed.
```

### 영향
주석은 「A new run does not write over the folder」라고 적는다. 그 거절은 `.claude/skills/do-math/runtime/paper.py` 4916~4918행이다. `assertRaises(paper.Stop)`은 `produce`가 세션을 띄우기 전에 내는 다른 거절(4920~4923행의 것들)로도 통과하므로, 이 자리가 보려는 「폴더가 비어 있지 않아서 거절했다」는 사실은 고정되지 않는다. 조각은 4917행의 문구를 고정한다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_paper.py 2057~2058행
원래:
```
        with self.assertRaises(paper.Stop):
            self.run_paper(good())
```
대체:
```
        with self.assertRaisesRegex(paper.Stop, 'is not empty; give a new folder to --out'):
            self.run_paper(good())
```


## R1-59
제목: 목록에 없는 번호의 시험이 세 입력의 거절 사유를 고정하지 않는다

### 위치
`.claude/skills/do-math/runtime/tests/test_paper.py` 2645~2647행(`OpenFindingsTests.test_the_numbers_given_are_those_of_the_list`).

### 기준
`임시/do-math_검증_20261125-2/맥락.md` 866행:

```
- **A test of a refusal fixes the reason for the refusal**, not only that something was refused. Its input starts from what the real producer makes and changes the one thing the test is about, so that the failure can be attributed.
```

### 영향
`act_on_open`은 번호를 읽기 전에 여섯 가지로 거절할 수 있다(`.claude/skills/do-math/runtime/paper.py` 5046, 5050, 5055, 5059, 5076, 5081행). 이 시험의 세 입력은 그 뒤 5091행의 `chosen_numbers`에서 거절되어야 하는데, `assertRaises(paper.Stop)`은 앞의 여섯 가운데 어느 것이 나도 통과한다. 예컨대 정본 대조(5073~5078행)가 잘못되어 모든 `--open-findings`가 거절되는 회귀에서도 이 시험은 통과한다. 이 시험의 운전은 독해의 지적 둘만 열어 두므로 목록은 2건이다. 조각은 `'3'`과 `'0'`에 2980행의 문구를, `'tools'`에 2976~2977행의 문구를 고정한다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_paper.py 2645~2647행
원래:
```
        for wrong in ('3', '0', 'tools'):
            with self.assertRaises(paper.Stop):
                self.run_paper(good(), open_findings=wrong)
```
대체:
```
        outside = 'the run has 2 open findings, numbered from 1 to 2'
        for wrong, reason in (('3', outside), ('0', outside), ('tools', 'it was given "tools"')):
            with self.assertRaisesRegex(paper.Stop, reason):
                self.run_paper(good(), open_findings=wrong)
```


## R1-60
제목: 표제지 파일의 시험이 꼴이 틀린 파일과 읽히지 않는 파일의 거절을 가리지 않는다

### 위치
`.claude/skills/do-math/runtime/tests/test_paper.py` 2769~2775행(`TitlePageTests.test_the_title_page_file_names_the_authors`).

### 기준
`임시/do-math_검증_20261125-2/맥락.md` 866행:

```
- **A test of a refusal fixes the reason for the refusal**, not only that something was refused. Its input starts from what the real producer makes and changes the one thing the test is about, so that the failure can be attributed.
```

### 영향
`paper.read_title_page`는 JSON으로 읽히지 않는 파일을 `.claude/skills/do-math/runtime/paper.py` 1617행으로, 저자 목록의 꼴이 틀린 파일을 1622~1623행으로 거절한다. 시험의 다섯 입력은 `Stop`만 단언한다. 그래서 꼴이 틀린 네 파일이 1617행의 「cannot be read as JSON」으로 거절되거나, 읽히지 않는 파일이 1622행의 문구로 거절되는 회귀가 나도 통과한다. 그때 운영자는 고칠 자리를 가리키지 않는 문구를 받는다. 조각은 두 거절의 문구를 고정한다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_paper.py 2769~2775행
원래:
```
        for wrong in ({'authors': [{'name': ''}]}, {'authors': 'Ada'}, {'authors': [{'name': 'Ada', 'email': 3}]}, ['Ada']):
            write_json(page, wrong)
            with self.assertRaises(paper.Stop):
                paper.read_title_page(page)
        page.write_text('{', encoding='utf-8')
        with self.assertRaises(paper.Stop):
            paper.read_title_page(page)
```
대체:
```
        for wrong in ({'authors': [{'name': ''}]}, {'authors': 'Ada'}, {'authors': [{'name': 'Ada', 'email': 3}]}, ['Ada']):
            write_json(page, wrong)
            with self.assertRaisesRegex(paper.Stop, 'each author has a "name" that is not empty'):
                paper.read_title_page(page)
        page.write_text('{', encoding='utf-8')
        with self.assertRaisesRegex(paper.Stop, 'cannot be read as JSON'):
            paper.read_title_page(page)
```


## R1-61
제목: 초안 폴더의 조판 거절을 시험이 사유 없이 단언한다

### 위치
`.claude/skills/do-math/runtime/tests/test_paper.py` 2890~2891행(`DraftTests.test_a_draft_holds_the_statements_the_formulas_the_gaps_and_the_results_to_cite`).

### 기준
`임시/do-math_검증_20261125-2/맥락.md` 866행:

```
- **A test of a refusal fixes the reason for the refusal**, not only that something was refused. Its input starts from what the real producer makes and changes the one thing the test is about, so that the failure can be attributed.
```

### 영향
주석은 초안이 「no manuscript to typeset」이라고 적는다. 그 거절은 `.claude/skills/do-math/runtime/paper.py` 5117~5119행이다. 바로 앞 2888~2889행은 같은 폴더의 `--resume` 거절을 문구로 고정하는데 이 자리는 `Stop`만 본다. 5118행의 검사가 초안 폴더를 받아들이게 바뀌면 `typeset_only`는 더 나아가 5131행에서 「읽기와 대조가 끝나지 않은 원고」라는 다른 문구로 거절하고, 그때에도 이 시험은 통과한다. 조각은 5119행의 문구를 고정한다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_paper.py 2890~2891행
원래:
```
        with self.assertRaises(paper.Stop):
            self.run_paper(drafting(), only=True)
```
대체:
```
        with self.assertRaisesRegex(paper.Stop, 'does not hold a manuscript of this command'):
            self.run_paper(drafting(), only=True)
```


## R1-62
제목: 인스턴스를 쓰지 않는 조립과 조판의 시험 다섯이 시험마다 인스턴스를 두 번 복사한다

### 위치
`.claude/skills/do-math/runtime/tests/test_paper.py` 810~886행. `ManuscriptTests(PaperCase)`의 뒤쪽 여섯 시험 가운데 820~831행을 뺀 다섯(810~818, 833~834, 836~846, 848~871, 873~886행)은 `setUp`이 준비한 것을 하나도 쓰지 않는다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 132행:

```
넷 가운데 하나를 어긴 시험, 어떤 시험도 알아채지 못할 동작, 확인하는 것에 견주어 지나치게 오래 걸리는 시험, 한 번의 실행 뒤에 남는 찌꺼기가 결함이다.
```

`임시/do-math_검증_20261125-2/맥락.md` 870행:

```
When cutting a test's cost, keep its starting state and the real path it goes down, not only its assertions; a method without an assertion of its own may still check through a helper or through the absence of an exception.
```

### 영향
`PaperCase.setUp`은 시험마다 `InstanceCase.setUp`으로 인스턴스 틀과 스킬의 `reference/`, `roles/`, `resume/`, `SKILL.md`를 임시 폴더에 복사하고(`tests/support.py` 173~179행), 게시된 인스턴스를 한 번 더 복사하고, 논문 열네 편의 모음을 쓴다(`test_paper.py` 425~438행). 다섯 시험은 `paper.assemble(PLAN, PARTS)`, `paper.capitals_kept`, `paper.typeset`, `paper.tight_displays`, `paper.wide_lines`를 모듈 상수와 자기 임시 폴더로만 부른다. 준비한 인스턴스, 모음, `paper.EXEMPLARS`의 패치 가운데 어느 것도 읽지 않는다. 이 값은 `tests.test_paper`를 돌릴 때마다 치른다. 조각은 `self.materials()`를 쓰는 820~831행의 시험을 앞으로 옮겨 `ManuscriptTests`에 남기고, 그 뒤에 `unittest.TestCase` 클래스의 머리를 넣어 다섯 시험이 그 클래스에 들게 한다. 시험의 본문과 단언은 한 글자도 바뀌지 않고, 수집되는 시험 수는 102건 그대로다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_paper.py 810~831행
원래:
```
    def test_the_running_head_is_the_title_with_its_formulas_left_as_they_are(self):
        # amsart capitalizes the title for the head, and with no author it does so twice, formulas included.
        tex = paper.assemble(PLAN, PARTS)[0]
        title = PLAN['title'].strip()
        self.assertIn('\\newcommand{\\RunningHead}{' + title + '}\n\\uppercasenonmath\\RunningHead\n\\begin{document}\n'
                      '\\title{' + title + '}\n', tex)
        # The head is printed when it has room beside the page number, and left out when it has not.
        self.assertIn('\\maketitle\n\\sbox0{\\normalfont\\scriptsize\\RunningHead}\\ifdim\\wd0>.85\\textwidth\\markboth{}{}'
                      '\\else\\markboth{\\RunningHead}{\\RunningHead}\\fi\n', tex)

    def test_the_running_head_is_the_short_title_when_the_plan_gives_one(self):
        title = PLAN['title'].strip()
        tex = paper.assemble({**PLAN, 'short_title': ' A short title of $x^2$ '}, PARTS)[0]
        self.assertIn('\\newcommand{\\RunningHead}{A short title of $x^2$}\n\\uppercasenonmath\\RunningHead\n'
                      '\\begin{document}\n\\title{' + title + '}\n', tex)
        # A plan without the key is carried out as before; with the key, it is a text, and it names no Lean name.
        materials = self.materials()
        self.assertEqual(paper.check_plan(materials, {**PLAN, 'short_title': 'A short title'}, KEYS), [])
        self.assertIn('"short_title", when the plan has it, is a nonempty text',
                      paper.check_plan(materials, {**PLAN, 'short_title': ''}, KEYS))
        self.assertTrue(any(problem.startswith('the short title has Lean')
                            for problem in paper.check_plan(materials, {**PLAN, 'short_title': 'Squares in Lean'}, KEYS)))
```
대체:
```
    def test_the_running_head_is_the_short_title_when_the_plan_gives_one(self):
        title = PLAN['title'].strip()
        tex = paper.assemble({**PLAN, 'short_title': ' A short title of $x^2$ '}, PARTS)[0]
        self.assertIn('\\newcommand{\\RunningHead}{A short title of $x^2$}\n\\uppercasenonmath\\RunningHead\n'
                      '\\begin{document}\n\\title{' + title + '}\n', tex)
        # A plan without the key is carried out as before; with the key, it is a text, and it names no Lean name.
        materials = self.materials()
        self.assertEqual(paper.check_plan(materials, {**PLAN, 'short_title': 'A short title'}, KEYS), [])
        self.assertIn('"short_title", when the plan has it, is a nonempty text',
                      paper.check_plan(materials, {**PLAN, 'short_title': ''}, KEYS))
        self.assertTrue(any(problem.startswith('the short title has Lean')
                            for problem in paper.check_plan(materials, {**PLAN, 'short_title': 'Squares in Lean'}, KEYS)))


class TypesetTests(unittest.TestCase):
    """What the script writes around the parts and reads from a run of TeX; none of it needs an instance."""

    def test_the_running_head_is_the_title_with_its_formulas_left_as_they_are(self):
        # amsart capitalizes the title for the head, and with no author it does so twice, formulas included.
        tex = paper.assemble(PLAN, PARTS)[0]
        title = PLAN['title'].strip()
        self.assertIn('\\newcommand{\\RunningHead}{' + title + '}\n\\uppercasenonmath\\RunningHead\n\\begin{document}\n'
                      '\\title{' + title + '}\n', tex)
        # The head is printed when it has room beside the page number, and left out when it has not.
        self.assertIn('\\maketitle\n\\sbox0{\\normalfont\\scriptsize\\RunningHead}\\ifdim\\wd0>.85\\textwidth\\markboth{}{}'
                      '\\else\\markboth{\\RunningHead}{\\RunningHead}\\fi\n', tex)
```


## R1-63
제목: 독자가 이름으로 든 절을 읽는 순수 함수의 시험이 인스턴스와 자료 추출을 치른다

### 위치
`.claude/skills/do-math/runtime/tests/test_paper.py` 1922~1927행(`BriefTests.test_the_section_that_a_reader_names_is_understood_in_the_forms_a_reader_gives_it`).

### 기준
`임시/do-math_검증_20261125-2/동결.md` 132행:

```
넷 가운데 하나를 어긴 시험, 어떤 시험도 알아채지 못할 동작, 확인하는 것에 견주어 지나치게 오래 걸리는 시험, 한 번의 실행 뒤에 남는 찌꺼기가 결함이다.
```

`임시/do-math_검증_20261125-2/맥락.md` 870행:

```
When cutting a test's cost, keep its starting state and the real path it goes down, not only its assertions; a method without an assertion of its own may still check through a helper or through the absence of an exception.
```

### 영향
이 시험은 `paper.named_part(PLAN, value)`를 열여덟 값으로 부를 뿐이고 `setUp`이 준비한 것을 쓰지 않는다. 그런데 `BriefTests(PaperCase)`에 들어 있어서, 돌 때마다 `PaperCase.setUp`의 인스턴스 복사 두 번과 지침·모음의 복사에 더해 `BriefTests.setUp`(1787~1790행)의 정본 재생, 자료 추출, `paper.Layout` 계산을 치른다. 조각은 이 시험 앞에 `unittest.TestCase` 클래스의 머리를 넣는다. 이 시험은 `BriefTests`의 마지막 메서드이고 바로 뒤가 다음 클래스(1930행)이므로 다른 시험의 소속은 바뀌지 않는다. 본문과 단언은 그대로다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_paper.py 1920~1922행
원래:
```
        self.assertIn('Passing from n to n + 1 adds the odd number 2n + 1.', text)

    def test_the_section_that_a_reader_names_is_understood_in_the_forms_a_reader_gives_it(self):
```
대체:
```
        self.assertIn('Passing from n to n + 1 adds the odd number 2n + 1.', text)


class NamedPartTests(unittest.TestCase):
    def test_the_section_that_a_reader_names_is_understood_in_the_forms_a_reader_gives_it(self):
```


## R1-64
제목: 본문 줄글을 가르는 순수 함수의 시험이 시험마다 인스턴스를 두 번 복사한다

### 위치
`.claude/skills/do-math/runtime/tests/test_paper.py` 3613~3641행(`CoverageTests.test_the_running_text_is_what_stands_outside_the_statements_and_the_proofs`).

### 기준
`임시/do-math_검증_20261125-2/동결.md` 132행:

```
넷 가운데 하나를 어긴 시험, 어떤 시험도 알아채지 못할 동작, 확인하는 것에 견주어 지나치게 오래 걸리는 시험, 한 번의 실행 뒤에 남는 찌꺼기가 결함이다.
```

`임시/do-math_검증_20261125-2/맥락.md` 870행:

```
When cutting a test's cost, keep its starting state and the real path it goes down, not only its assertions; a method without an assertion of its own may still check through a helper or through the absence of an exception.
```

### 영향
이 시험은 `paper.assemble(PLAN, parts)`와 `paper.running_text(PLAN, parts, spans)`를 모듈 상수로만 부르고 `setUp`이 준비한 것을 쓰지 않는다. `CoverageTests(PaperCase)`의 첫 시험이어서 돌 때마다 인스턴스 복사 두 번과 지침·모음의 복사를 치른다(`tests/support.py` 173~179행, `test_paper.py` 425~438행). 조각은 이 시험을 `CoverageTests` 앞의 `unittest.TestCase` 클래스로 옮긴다. 옮기는 본문은 3613~3641행 그대로이고, `CoverageTests`의 머리와 `kinds`는 그 뒤에 그대로 선다. 수집되는 시험 수는 같다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_paper.py 3607~3643행
원래:
```
class CoverageTests(PaperCase):
    """The running text of the manuscript compared with the elements, after everything else."""

    def kinds(self, since=0):
        return [(c['kind'], c['section']) for c in self.calls()][since:]

    def test_the_running_text_is_what_stands_outside_the_statements_and_the_proofs(self):
        tools = TOOLS.replace('The sum $S_{n+1}$ exceeds $S_n$ by $2n + 1$.', '\n'.join([
            'We have', '\\begin{equation}\\label{eq:tools-gain}', 'S_{n+1} - S_n = 2n + 1.', '\\end{equation}',
            'A second display is used here alone:', '\\begin{equation}\\label{eq:tools-local}', '2n + 1 > 0.', '\\end{equation}',
            'By \\eqref{eq:tools-local} the claim follows.'])) + '\n% A comment alone asserts nothing.\n'
        proof = PROOF.replace('The sums increase by', 'The sums increase by \\eqref{eq:tools-gain} and')
        parts = {**PARTS, 'tools': tools, 'proof': proof}
        tex, spans = paper.assemble(PLAN, parts)
        found = paper.running_text(PLAN, parts, spans)
        # The abstract goes with the first section. A numbered statement and a proof are left out, and what stands
        # before and after them is given paragraph by paragraph.
        self.assertEqual([(e['entry'], e['kind'], e['part'], e['text']) for e in found['intro']], [
            (1, 'running text', 'abstract', ABSTRACT.strip()),
            (2, 'running text', 'intro', INTRO.split('\n')[0]),
            (3, 'running text', 'intro', 'The proof, in Section~\\ref{sec:proof}, is an induction whose step is Lemma~\\ref{lem:square}.')])
        # Of a proof, a displayed formula is given when text outside that proof refers to it, and no other.
        self.assertEqual([(e['entry'], e['kind'], e.get('labels')) for e in found['tools']],
                         [(1, 'formula of a proof, referred to from outside that proof', ['eq:tools-gain']),
                          (2, 'running text', None)])
        self.assertIn('S_{n+1} - S_n = 2n + 1.', found['tools'][0]['text'])
        self.assertTrue(found['tools'][1]['text'].startswith('The next lemma is the expansion of a square'))
        # A section that consists of a proof has no running text.
        self.assertEqual(found['proof'], [])
        # Each entry names the lines of the manuscript at which it stands.
        lines = tex.split('\n')
        for entry in found['intro'] + found['tools'][1:]:
            self.assertEqual(lines[int(entry['lines']) - 1], entry['text'])
        first, last = map(int, found['tools'][0]['lines'].split(' to '))
        self.assertEqual((lines[first - 1], lines[last - 1]), ('\\begin{equation}\\label{eq:tools-gain}', '\\end{equation}'))

    def test_a_sentence_that_no_element_covers_is_cut_and_the_section_is_compared_once_more(self):
```
대체:
```
class RunningTextTests(unittest.TestCase):
    def test_the_running_text_is_what_stands_outside_the_statements_and_the_proofs(self):
        tools = TOOLS.replace('The sum $S_{n+1}$ exceeds $S_n$ by $2n + 1$.', '\n'.join([
            'We have', '\\begin{equation}\\label{eq:tools-gain}', 'S_{n+1} - S_n = 2n + 1.', '\\end{equation}',
            'A second display is used here alone:', '\\begin{equation}\\label{eq:tools-local}', '2n + 1 > 0.', '\\end{equation}',
            'By \\eqref{eq:tools-local} the claim follows.'])) + '\n% A comment alone asserts nothing.\n'
        proof = PROOF.replace('The sums increase by', 'The sums increase by \\eqref{eq:tools-gain} and')
        parts = {**PARTS, 'tools': tools, 'proof': proof}
        tex, spans = paper.assemble(PLAN, parts)
        found = paper.running_text(PLAN, parts, spans)
        # The abstract goes with the first section. A numbered statement and a proof are left out, and what stands
        # before and after them is given paragraph by paragraph.
        self.assertEqual([(e['entry'], e['kind'], e['part'], e['text']) for e in found['intro']], [
            (1, 'running text', 'abstract', ABSTRACT.strip()),
            (2, 'running text', 'intro', INTRO.split('\n')[0]),
            (3, 'running text', 'intro', 'The proof, in Section~\\ref{sec:proof}, is an induction whose step is Lemma~\\ref{lem:square}.')])
        # Of a proof, a displayed formula is given when text outside that proof refers to it, and no other.
        self.assertEqual([(e['entry'], e['kind'], e.get('labels')) for e in found['tools']],
                         [(1, 'formula of a proof, referred to from outside that proof', ['eq:tools-gain']),
                          (2, 'running text', None)])
        self.assertIn('S_{n+1} - S_n = 2n + 1.', found['tools'][0]['text'])
        self.assertTrue(found['tools'][1]['text'].startswith('The next lemma is the expansion of a square'))
        # A section that consists of a proof has no running text.
        self.assertEqual(found['proof'], [])
        # Each entry names the lines of the manuscript at which it stands.
        lines = tex.split('\n')
        for entry in found['intro'] + found['tools'][1:]:
            self.assertEqual(lines[int(entry['lines']) - 1], entry['text'])
        first, last = map(int, found['tools'][0]['lines'].split(' to '))
        self.assertEqual((lines[first - 1], lines[last - 1]), ('\\begin{equation}\\label{eq:tools-gain}', '\\end{equation}'))


class CoverageTests(PaperCase):
    """The running text of the manuscript compared with the elements, after everything else."""

    def kinds(self, since=0):
        return [(c['kind'], c['section']) for c in self.calls()][since:]

    def test_a_sentence_that_no_element_covers_is_cut_and_the_section_is_compared_once_more(self):
```


## R1-65
제목: 모듈의 answers와 같은 함수를 한 시험이 지역 이름으로 다시 정의한다

### 위치
`.claude/skills/do-math/runtime/tests/test_paper.py` 2292~2293행. 모듈 수준의 `answers`는 같은 파일 362~365행이다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 134행:

```
이번 주에 걷어 낸 기능의 잔재, 쓰이지 않는 코드와 인자, 코드나 시험이 한 규칙을 두 군데에 따로 구현한 것과 그 둘 사이의 어긋남, 앞 상태를 서술하는 주석과 문서, 이 기계에만 맞는 경로와 수치가 여기에 든다.
```

### 영향
2292~2293행의 `lambda`는 362~365행의 함수와 식이 같다. 둘 다 `json.dumps([{'finding': number, 'action': action, 'note': f'{action} {number}'} for number, action in enumerate(actions, 1)])`를 돌려준다. 이 시험만 지역 이름으로 모듈의 함수를 가린다. 수리 세션의 답의 꼴이 바뀌어 362~365행을 고치는 사람은 이 사본을 놓치고, 그러면 이 시험 하나만 옛 꼴의 답으로 돈다. 조각은 지역 정의를 지운다. 2295, 2298, 2300, 2301행의 호출은 모듈의 함수로 가고 같은 값을 받는다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_paper.py 2292~2293행
원래:
```
        answers = lambda *actions: json.dumps([{'finding': number, 'action': action, 'note': f'{action} {number}'}
                                              for number, action in enumerate(actions, 1)])
```
대체:
```

```


## R1-66
제목: 모듈이 이미 들여온 threading을 한 시험이 다시 들여온다

### 위치
`.claude/skills/do-math/runtime/tests/test_paper.py` 1959행. 모듈은 114행에서 `threading`을 들여오고 2733행에서 쓴다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 134행:

```
이번 주에 걷어 낸 기능의 잔재, 쓰이지 않는 코드와 인자, 코드나 시험이 한 규칙을 두 군데에 따로 구현한 것과 그 둘 사이의 어긋남, 앞 상태를 서술하는 주석과 문서, 이 기계에만 맞는 경로와 수치가 여기에 든다.
```

### 영향
1959행의 `import threading`은 하는 일이 없다. 같은 이름이 114행에서 모듈에 이미 묶여 있고 1970행은 어느 쪽으로든 같은 모듈을 받는다. 이 줄은 모듈 수준의 들여오기가 생기기 전의 흔적이며, 읽는 사람에게 이 시험만 따로 들여와야 할 까닭이 있는 것처럼 보인다. 조각은 그 줄을 지운다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_paper.py 1959~1959행
원래:
```
        import threading
```
대체:
```

```


## R1-68
제목: 선택이 유도를 골랐을 때 루트의 기록이 옛 증명을 말하는 채로 남을 수 있다

### 위치
`.claude/skills/do-math/runtime/finalize.py` 1158~1162행(`Run.records`)과 1846행(`2.5-records` 단계의 입력 목록). 관련 자리는 같은 파일 604행(선택이 고른 색인을 `lib/0-selected/index.json`에 쓴다)과 `.claude/skills/do-math/runtime/package.py` 489~493행(`record_todo`가 `changed`를 정하는 비교)이다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 122행:

```
첫째는 코드의 결함이다. 실제 입력, 상태, 동시 실행, 실패 경로, Windows와 Linux의 프로세스·파일 동작에서 의도한 동작이 깨지는 것이 여기에 든다. 가이드가 약속하지만 코드가 하지 않는 동작, 코드가 하지만 가이드가 말하지 않아 작업 세션이나 운영자의 행동이 어긋나는 동작도 여기에 든다.
```

`.claude/skills/do-math/finalize/records-write.md` 33행:

```
`changed` (its Lean text differs from the one its record was written for)
```

`.claude/skills/do-math/finalize/common.md` 84행:

```
Every text of the package that presents mathematics presents the chosen proof and nothing beside it.
```

### 영향
재현 경로는 선택 세션이 `route`가 `derivation`인 선택지를 고른 운전이다. `read_decision`은 유도 파일을 루트의 모듈 자리에 놓고 컴파일해 얻은 색인을 돌려주고, `selection`은 그 색인을 `lib/0-selected/index.json`에 쓴다(604행). 이 색인에서 루트의 `source_sha`는 이미 유도의 본문에서 나온 값이다. `records`는 이 색인을 `record_todo`의 기준 색인으로 넘긴다. `record_todo`는 기준 색인과 지금 색인의 `source_sha`가 다를 때에만 `changed`로 올리므로, 루트의 Lean 본문이 4단계까지 유도 그대로이면 루트는 `changed`가 아니다. 루트의 기록은 `lib/0-selected/records`에 연구가 쓴 그대로 복사된 것이어서, 연구가 준 증명을 말로 적고 있다.

그 결과는 옛 기록의 문면에 달린다. 옛 기록이 이제 라이브러리에 없는 선언을 백틱으로 들면 루트는 `names a declaration that is gone`이라는 다른 사유로 목록에 오른다. 들지 않으면 목록에 오르지 않는다. 뒤의 경우 루트의 기록은 꾸러미에 없는 증명을 말하는 채로 `records/`에 실리고, 대조 세션의 목록에도 오르지 않으며, 논문 명령은 그 기록에서 루트의 증명을 쓴다. 유도는 기존 둘째 증명을 한 줄로 적용하는 것일 수도 있어, 옛 증명이 든 선언이 모두 남는 경우가 실제로 생긴다.

기록은 연구의 색인에 대해 쓰였으므로, 목록을 연구의 색인(`source/canon/index.json`)에 견주어 만들면 유도가 바꾼 루트가 `changed`로 오른다. 유도가 없는 운전에서는 두 색인이 같은 객체에서 나온 같은 내용이어서 동작이 달라지지 않는다. `2.5-records` 단계는 이제 `lib/0-selected`를 읽지 않고 `source`를 읽으므로 단계의 입력 목록을 함께 고친다. `state.json`의 `read` 칸은 프로그램이 다시 읽지 않는다.

지금의 시험은 유도를 고른 운전을 `2.1-take` 앞에서 세우므로 이 경로를 지나가지 않는다. 더한 시험은 같은 유도로 `2.6-draft` 앞까지 가서, 기록 작성 세션이 받은 `todo.json`이 루트를 `changed`로 싣는지를 본다. 고치기 전의 코드에서는 루트가 `names a declaration that is gone`으로 실려 이 단언이 실패한다.

### 조각 1 — .claude/skills/do-math/runtime/finalize.py 1158~1162행
원래:
```
    def records(self):
        arranged = self.work / 'lib' / '4-arranged'
        self.bring_records('5', arranged / 'lean', read_json(arranged / 'index.json'),
                           read_json(self.work / 'lib' / '0-selected' / 'index.json'), arranged / 'records',
                           arranged / 'bibliography.bib', [], self.work / 'lib' / '5-records')
```
대체:
```
    def records(self):
        arranged = self.work / 'lib' / '4-arranged'
        # The records that stand were written by the research, so the list is made against the research's index.
        # The index of step 1 already holds the root as a derivation of the selection proves it; against that
        # index the root's record, which tells the proof the research gave, would count as written for this proof.
        self.bring_records('5', arranged / 'lean', read_json(arranged / 'index.json'),
                           canon.read_index(self.work / 'source' / 'canon' / 'index.json'), arranged / 'records',
                           arranged / 'bibliography.bib', [], self.work / 'lib' / '5-records')
```

### 조각 2 — .claude/skills/do-math/runtime/finalize.py 1846~1846행
원래:
```
                self.step('2.5-records', [lib + '0-selected', lib + '4-arranged'], [lib + '5-records'], self.records)
```
대체:
```
                self.step('2.5-records', ['source', lib + '4-arranged'], [lib + '5-records'], self.records)
```

### 조각 3 — .claude/skills/do-math/runtime/tests/test_finalize.py 행 1390 뒤
대체:
```

    def test_the_record_of_a_root_that_a_derivation_proves_is_listed_as_changed(self):
        derived = module_text(theorem('root', ROOT_STATEMENT, uses=['named_four'], proof='rfl',
                                      doc='The sum of the first `n` odd numbers is the square of `n`.'),
                              imports=('Small.Defs', 'Small.Helper'))
        option = {'id': 'a', 'main': 'Small.named_four', 'route': 'derivation', 'proves': 'p', 'rests_on': 'r', 'size': 's',
                  'for': 'f', 'against': 'a'}
        plan = script(selection=[{'output/decision.json': decision(options=[option]), 'output/derivations/a.lean': derived}],
                      review=[{'output/review.json': json.dumps({
                          'parts': [{'id': 'core', 'modules': ['Small.Root', 'Small.Helper']}], 'cross': []})}])
        plan['simplify:core'] = [{'output/report.json': json.dumps({'deleted': [], 'cross': [], 'notes': ''})}]
        plan['records-write:5-01'] = [{
            'output/records/Small/root.md': record_text('The sum of the first n odd numbers equals n times n.', weight='unit',
                                                        proof='From `Small.named_four`.'),
            'output/records/Small/named_four.md': record_text('The first four odd numbers sum to sixteen.'),
            'output/findings.json': '[]'}]
        plan['records-compare:5-01'] = [{'output/verdicts.json': json.dumps([
            {'declaration': name, 'verdict': 'agrees', 'difference': ''} for name in ('Small.root', 'Small.named_four')])}]
        with patch('finalize.Run.draft', side_effect=paper.Stop('halted for the test')):
            self.assertEqual(self.run_command(plan, config=self.config()), 2, self.said)
        self.assertIn('The run stopped at the step `2.6-draft`', (self.work / 'report.md').read_text(encoding='utf-8'))
        # The research wrote the root's record for the proof it gave. The root now has the proof of the derivation,
        # so its record is listed as written for another Lean text, whatever the old record names.
        written = self.calls('records-write')[0]
        todo = read_json(self.work / 'sessions' / written['folder'] / 'todo.json')
        self.assertEqual({item['declaration']: item['why'] for item in todo},
                         {'Small.named_four': 'names a declaration that is gone', 'Small.root': 'changed'})
```


## R1-69
제목: 마지막 검사가 TeX의 `f:\mathbb{N}` 꼴을 드라이브 경로로 읽어 운전을 세운다

### 위치
`.claude/skills/do-math/runtime/package.py` 43행(`DRIVE_PATH`), 1456~1465행(`standalone_problems`의 설명), 1496~1504행(쓴 문서마다 드라이브 경로를 찾는 자리). `.claude/skills/do-math/runtime/finalize.py` 1786~1789행은 종료 보고가 이 검사를 서술하는 문장이다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 122행:

```
첫째는 코드의 결함이다. 실제 입력, 상태, 동시 실행, 실패 경로, Windows와 Linux의 프로세스·파일 동작에서 의도한 동작이 깨지는 것이 여기에 든다.
```

`임시/do-math_검증_20261125-2/맥락.md` 283행:

```
The folder stands alone: nothing in it points outside itself or says that something exists only on this machine, and its build instructions work from the unpacked archive.
```

### 영향
`DRIVE_PATH`는 글자 하나, 쌍점, 역슬래시나 슬래시의 순서를 찾는다. TeX에서 사상을 적는 `f:\mathbb{N}`과 집합을 적는 `\{x:\ ...\}`가 같은 꼴이다. 검사는 `WRITTEN`의 문서 전부에 이 식을 적용하고, 그 안에 논문의 원문 `paper/paper.tex`와, 세션이 수식을 달러 기호 사이에 쓰는 `README.md`가 있다. 저장소에 있는 실제 논문 `solved/parking-unimodality/paper/paper.tex`의 38행과 74행이 `\mathrm{PF}_n:\ M(\alpha)`를 담고 있고, 이 식은 두 자리 모두에 맞는다.

이런 논문을 가진 운전은 모든 단계를 지난 뒤 `6-check`에서 `paper/paper.tex holds a drive path`로 서고 종료 코드 2를 낸다. 같은 명령을 다시 주어도 같은 자리에서 선다. 고칠 원인이 운영자에게 없고, 논문을 손으로 고치면 `4-paper`가 적어 둔 해시와 달라져 다시 선다.

이 식만으로는 TeX와 경로를 가를 수 없으므로 찾는 범위를 고친다. 논문의 원문은 드라이브 경로를 찾지 않고, 다른 문서는 한 줄 안의 달러 기호 사이를 빼고 찾는다. 작업 폴더의 경로와 계정 이름을 찾는 검사는 모든 문서에 그대로 남는다. 잃는 것은 논문 원문에 적힌, 작업 폴더도 계정 이름도 담지 않은 드라이브 경로와, 한 줄에서 두 달러 기호 사이에 놓인 경로를 알아채는 일이다. 종료 보고의 문장은 검사가 실제로 확인한 범위를 말하도록 함께 고친다.

시험은 논문 원문과 README에 위의 꼴을 넣어 검사가 통과하는지와, 수식 옆의 실제 경로는 여전히 잡히는지를 본다. 고치기 전의 코드에서는 첫 단언이 실패한다.

### 조각 1 — .claude/skills/do-math/runtime/package.py 행 43 뒤
대체:
```
FORMULA = re.compile(r'\$[^$\n]+\$')  # a formula between dollar signs on one line, as a Markdown document writes it
```

### 조각 2 — .claude/skills/do-math/runtime/package.py 1460~1461행
원래:
```
    archive holds the account name; no document the pipeline wrote holds a drive path or the work
    folder's path; every text file ends its lines with LF; `lean/` and `records/` have the hashes of
```
대체:
```
    archive holds the account name; no document the pipeline wrote holds the work folder's path, or a
    drive path outside TeX, where a letter, a colon and a command have the form of one, so that the
    source of the paper and the formulas of the other documents are not searched for it; every text
    file ends its lines with LF; `lean/` and `records/` have the hashes of
```

### 조각 3 — .claude/skills/do-math/runtime/package.py 1499~1502행
원래:
```
        text = files[relative].read_text(encoding='utf-8', errors='replace')
        found = DRIVE_PATH.search(text)
        if found:
            problems.append(f'{relative} holds a drive path: {text[found.start():found.start() + 40]!r}')
```
대체:
```
        text = files[relative].read_text(encoding='utf-8', errors='replace')
        # In TeX a letter, a colon and a command, as in `f:\mathbb{N}`, have the form of a drive path. The source of
        # the paper is not searched for one, and another document is searched without its formulas.
        searched = '' if relative.endswith('.tex') else FORMULA.sub(' ', text)
        found = DRIVE_PATH.search(searched)
        if found:
            problems.append(f'{relative} holds a drive path: {searched[found.start():found.start() + 40]!r}')
```

### 조각 4 — .claude/skills/do-math/runtime/finalize.py 1787~1787행
원래:
```
            'holds the account name; no document the pipeline wrote holds a drive path; every text file ends its '
```
대체:
```
            "holds the account name; no document the pipeline wrote holds a drive path outside the paper's source and "
            'the formulas of the other documents; every text file ends its '
```

### 조각 5 — .claude/skills/do-math/runtime/tests/test_finalize.py 행 886 뒤
대체:
```
        # In TeX a letter, a colon and a command have the form of a drive path. The source of the paper is not searched
        # for one, and a Markdown document is searched without its formulas; a path beside a formula is still found.
        (folder / 'paper' / 'paper.tex').write_text('$\\{\\alpha\\in\\mathrm{PF}_n:\\ M(\\alpha)\\le k\\}$\n',
                                                    encoding='utf-8', newline='\n')
        (folder / 'README.md').write_text('# Title\n\nA map $f:\\mathbb{N}\\to\\mathbb{N}$.\n', encoding='utf-8', newline='\n')
        (folder / 'MANIFEST.sha256').write_text(package.manifest_text(folder), encoding='utf-8', newline='\n')
        self.assertEqual(package.standalone_problems(folder, work, 'no-such-account', freeze), [])
        (folder / 'README.md').write_text('# Title\n\nA map $f:\\mathbb{N}\\to\\mathbb{N}$, built in C:\\Users\\someone.\n',
                                          encoding='utf-8', newline='\n')
        (folder / 'MANIFEST.sha256').write_text(package.manifest_text(folder), encoding='utf-8', newline='\n')
        problems = package.standalone_problems(folder, work, 'no-such-account', freeze)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn('README.md holds a drive path', problems[0])
```


## R1-70
제목: 꾸러미 독해 지침은 읽지 못한 문서를 빈 `quote`로 알리게 하고 프로그램은 빈 `quote`를 거절한다

### 위치
`.claude/skills/do-math/runtime/finalize.py` 1678~1683행(`read_findings`)과 1689행(산문 두 절의 지적을 가르는 식). 맞은편은 `.claude/skills/do-math/finalize/package-read.md` 60행이다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 122행:

```
가이드가 약속하지만 코드가 하지 않는 동작, 코드가 하지만 가이드가 말하지 않아 작업 세션이나 운영자의 행동이 어긋나는 동작도 여기에 든다.
```

`.claude/skills/do-math/finalize/package-read.md` 60행:

```
If you could not read one of them, that is itself a finding: name the file, leave `quote` empty, and say under `problem` that it was not read and why.
```

`.claude/skills/do-math/finalize/common.md` 30행:

```
What you could not do is said in the output, in the field the form has for it. An empty list means that you looked at everything and found nothing, so it must not stand for work you did not reach.
```

### 영향
재현 경로는 꾸러미 독해 세션이 문서 하나를 끝까지 읽지 못하고 지침대로 `quote`를 비운 지적을 낸 경우다. `read_findings`는 `is_text(f.get('quote'))`로 그 산출을 거절한다. 둘째 세션은 「every finding has "file", "quote" and "problem"」이라는 사유를 받는다. 이 사유는 지침이 시킨 것을 하지 말라는 말이어서, 둘째 세션이 같은 지적을 내면 운전은 「no package-read session left output the script can use」로 서고, 지적을 거두면 읽지 않은 문서가 읽은 것으로 지나간다.

어느 쪽이 틀렸는지는 장치의 목적으로 가른다. 공통 지침은 하지 못한 일을 산출에 적게 하고, 독해 지침은 그 자리를 빈 `quote`로 정했다. 프로그램의 검사는 지적을 본문에서 찾을 수 있게 하려는 것이므로, 찾을 본문이 없는 이 한 경우를 받아야 한다. 그러면 1689행의 식도 고쳐야 한다. 빈 문자열은 어느 글에나 들어 있으므로, 지금의 식은 `README.md`에 관한 빈 `quote` 지적을 산문 절의 지적으로 세어 교정 세션에 넘긴다. 읽지 못한 문서는 산문을 고쳐서 답할 수 없으므로 운전을 세우는 쪽에 넣는다.

시험은 대본의 지적 목록에 빈 `quote` 지적을 하나 더해, 독해 세션이 한 번만 뜨고 보고가 그 지적을 싣는지를 본다. 고치기 전의 코드에서는 독해 세션이 두 번 뜨고 보고에 두 지적이 모두 없다.

### 조각 1 — .claude/skills/do-math/runtime/finalize.py 1678~1683행
원래:
```
        def read_findings(output):
            findings = Sessions.load(output / 'findings.json', list)
            if not all(isinstance(f, dict) and is_text(f.get('file')) and is_text(f.get('quote')) and is_text(f.get('problem'))
                       for f in findings):
                raise Unusable(['every finding has "file", "quote" and "problem"'])
            return findings
```
대체:
```
        def read_findings(output):
            findings = Sessions.load(output / 'findings.json', list)
            # The quote is empty in one case, which the instruction gives: a document that the reader could not read.
            if not all(isinstance(f, dict) and is_text(f.get('file')) and isinstance(f.get('quote'), str)
                       and is_text(f.get('problem')) for f in findings):
                raise Unusable(['every finding has "file", "quote" and "problem"'])
            return findings
```

### 조각 2 — .claude/skills/do-math/runtime/finalize.py 1689~1689행
원래:
```
            ours = [f for f in findings if not (f['file'].endswith('README.md') and collapsed(f['quote']) in whole)]
```
대체:
```
            # A finding without a quote names a document that was not read, which no correction of the prose answers.
            ours = [f for f in findings if not (f['file'].endswith('README.md') and collapsed(f['quote'])
                                                and collapsed(f['quote']) in whole)]
```

### 조각 3 — .claude/skills/do-math/runtime/tests/test_finalize.py 1341~1342행
원래:
```
        plan = script(package_read=[{'output/findings.json': json.dumps([
            {'file': 'README.md', 'quote': 'Everything in this folder is under', 'problem': 'The licence is not named.'}])}])
```
대체:
```
        # The second finding has no quote, as the instruction asks for a document that the reader could not read.
        plan = script(package_read=[{'output/findings.json': json.dumps([
            {'file': 'README.md', 'quote': 'Everything in this folder is under', 'problem': 'The licence is not named.'},
            {'file': 'README.md', 'quote': '', 'problem': 'The file was not read to its end.'}])}])
```

### 조각 4 — .claude/skills/do-math/runtime/tests/test_finalize.py 행 1346 뒤
대체:
```
        self.assertIn('The file was not read to its end.', report)
        self.assertEqual(len(self.calls('package-read')), 1)  # a finding without a quote is a finding, and is not refused
```


## R1-71
제목: 간결화·되접기 세션이 남긴 `report.json`이 JSON이 아니면 그 부분을 버리지 않고 운전이 선다

### 위치
`.claude/skills/do-math/runtime/finalize.py` 845~846행(간결화 산출의 판독)과 1212~1213행(되접기 산출의 판독). 원인이 되는 자리는 `.claude/skills/do-math/runtime/package.py` 622행으로, `part_output`이 세션의 `report.json`을 `read_json`으로 읽는다.

### 기준
`임시/do-math_검증_20261125-2/맥락.md` 302행:

```
- **Only simplifications may be discarded.** A part of the simplifying, arranging or fold-back steps that fails its check is dropped and keeps its previous form. Every other failed exit check stops the run with exit code 2, and the same command continues it.
```

`.claude/skills/do-math/finalize/common.md` 31행:

```
When the program cannot use what a session left, it launches one more session for the same task and tells it why.
```

### 영향
재현 경로는 간결화나 되접기 세션이 `output/report.json`을 JSON으로 읽히지 않는 글로 남긴 경우다. 두 판독 함수는 `part_output`을 먼저 부르고, `part_output`은 그 파일을 `read_json`으로 읽어 `ValueError`를 낸다. `Sessions.session`이 다음 세션을 띄우는 예외는 `Unusable`, `TypeError`, `KeyError`, `AttributeError`, `UnicodeDecodeError`뿐이고(`runtime/paper.py` 3234~3237행), `discardable`은 `Stop`만 받으므로(`finalize.py` 284행), 이 예외는 `step`까지 올라가 `Halt`가 된다(206~208행). 운전은 종료 코드 2로 서고, 사람이 같은 명령을 다시 주어야 그 부분의 세션이 다시 뜬다. 지침과 설계는 이 경우를 둘째 세션과 그 부분의 버림으로 사람 없이 넘기게 했다.

같은 파일을 바로 다음 줄에서 `Sessions.load`가 읽고, 이 함수는 읽히지 않는 JSON을 `Unusable`로 낸다. 두 줄의 순서를 바꾸면 깨진 보고는 다른 흠과 같이 둘째 세션에 사유로 전해지고, 둘째도 쓸 수 없으면 그 부분이 버려진다. 보고가 없는 경우의 동작은 순서와 무관하게 같다.

시험은 이미 버려지는 부분인 `aux`의 첫 산출을 깨진 보고로 두어, 둘째 세션이 「output/report.json is not JSON」을 받는지를 본다. 고치기 전의 코드에서는 운전이 `2.3-simplify`에서 서서 그 시험의 첫 단언(종료 코드 0)이 실패한다.

### 조각 1 — .claude/skills/do-math/runtime/finalize.py 845~846행
원래:
```
                files, deleted, problems = package.part_output(output, taken, lambda m: m in part['modules'], self.definitions)
                report = Sessions.load(output / 'report.json')
```
대체:
```
                # The report is read first: `part_output` reads the same file, and a report that is no JSON object
                # is for the next session to repair, like every other fault of an output.
                report = Sessions.load(output / 'report.json')
                files, deleted, problems = package.part_output(output, taken, lambda m: m in part['modules'], self.definitions)
```

### 조각 2 — .claude/skills/do-math/runtime/finalize.py 1212~1213행
원래:
```
                files, deleted, problems = package.part_output(output, arranged / 'lean', inside, self.definitions, inside)
                report = Sessions.load(output / 'report.json')
```
대체:
```
                report = Sessions.load(output / 'report.json')  # first, as in the simplification: `part_output` reads it too
                files, deleted, problems = package.part_output(output, arranged / 'lean', inside, self.definitions, inside)
```

### 조각 3 — .claude/skills/do-math/runtime/tests/test_finalize.py 행 1279 뒤
대체:
```
            'simplify:aux': {'output/report.json': '{"deleted": ['},
```

### 조각 4 — .claude/skills/do-math/runtime/tests/test_finalize.py 행 1312 뒤
대체:
```
                ('simplify:aux', 'output/report.json is not JSON'),
```


## R1-73
제목: `rests-on.md`가 검토 지침이 말하는 「무엇이 그것에 기대는가」를 싣지 않는다

### 위치
`.claude/skills/do-math/runtime/package.py` 694~703행(`rests_on_text`). 맞은편은 `.claude/skills/do-math/finalize/review.md` 25행이다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 122행:

```
가이드가 약속하지만 코드가 하지 않는 동작, 코드가 하지만 가이드가 말하지 않아 작업 세션이나 운영자의 행동이 어긋나는 동작도 여기에 든다.
```

`.claude/skills/do-math/finalize/review.md` 25행:

```
- `rests-on.md`: for the elements of the library, what each rests on and what rests on it, from the research's index. Read it in full; it shows which declarations are used once, which are used only inside their own module, and what crosses from one group of modules to another.
```

### 영향
프로그램이 쓰는 `rests-on.md`의 한 줄은 요소마다 진술이 드는 이름과 증명이 드는 이름뿐이다. 그 요소를 드는 요소의 목록은 없다. 검토 세션은 지침에서 이 파일이 한 번만 쓰이는 선언, 자기 모듈 안에서만 쓰이는 선언, 모듈 무리를 건너는 것을 보여 준다는 말을 듣는다. 이 셋은 모두 「무엇이 그것을 쓰는가」에서 나오는데 파일에는 반대 방향만 있어서, 세션은 요소 전부의 목록을 스스로 뒤집어야 그것을 얻는다. 검토 세션은 이 판단으로 라이브러리를 부분으로 가르고, 가른 자리를 건너는 선언은 간결화 내내 이름과 진술이 묶인다.

어느 쪽이 틀렸는지는 이 파일의 쓰임으로 가른다. 지침이 파일에 맡긴 세 가지 쓰임이 모두 쓰는 쪽의 목록을 요구하므로 프로그램이 모자란 쪽이다. 줄마다 그 요소를 드는 요소를 덧붙인다. 지침의 문장은 그대로 맞게 된다.

시험은 검토에서 선 운전의 작업 폴더에서 검토 세션이 받은 파일을 읽어, 루트만이 쓰는 `Small.sq_step`의 줄이 루트를 드는지를 본다. 고치기 전의 코드에서는 그 줄에 `named by`가 없어 단언이 실패한다.

### 조각 1 — .claude/skills/do-math/runtime/package.py 694~703행
원래:
```
def rests_on_text(index, kept=None):
    """`rests-on.md`: for each element, what its statement names and what its proof names."""
    lines = ['# What rests on what', '']
    for name, entry in sorted(index['entries'].items()):
        if kept is not None and name not in kept:
            continue
        lines.append(f"- `{name}` ({entry['kind']}, `{entry['module']}`): statement names "
                     + (', '.join(f'`{used}`' for used in entry['statement_uses']) or 'nothing') + '; proof names '
                     + (', '.join(f'`{used}`' for used in entry['uses']) or 'nothing'))
    return '\n'.join(lines) + '\n'
```
대체:
```
def rests_on_text(index, kept=None):
    """`rests-on.md`: for each element, what its statement names, what its proof names, and which elements name it."""
    entries = {name: entry for name, entry in index['entries'].items() if kept is None or name in kept}
    users = {}
    for name, entry in entries.items():
        for used in set(entry['statement_uses'] + entry['uses']):
            users.setdefault(used, []).append(name)
    lines = ['# What rests on what', '']
    for name, entry in sorted(entries.items()):
        lines.append(f"- `{name}` ({entry['kind']}, `{entry['module']}`): statement names "
                     + (', '.join(f'`{used}`' for used in entry['statement_uses']) or 'nothing') + '; proof names '
                     + (', '.join(f'`{used}`' for used in entry['uses']) or 'nothing') + '; named by '
                     + (', '.join(f'`{user}`' for user in sorted(users.get(name, []))) or 'nothing'))
    return '\n'.join(lines) + '\n'
```

### 조각 2 — .claude/skills/do-math/runtime/tests/test_finalize.py 행 1225 뒤
대체:
```
        # What the reviewing session is given says of each element which elements name it, and not only what it names.
        rests = (self.work / 'sessions' / self.calls('review')[0]['folder'] / 'rests-on.md').read_text(encoding='utf-8')
        step = next(line for line in rests.split('\n') if line.startswith('- `Small.sq_step` '))
        self.assertTrue(step.endswith('; named by `Small.root`'), step)
```


## R1-75
제목: `library_ok`의 인자 `due`를 넘기는 호출이 없다

### 위치
`.claude/skills/do-math/runtime/finalize.py` 349~350행(서명), 358행(설명), 379~381행(쓰이는 자리).

### 기준
`임시/do-math_검증_20261125-2/동결.md` 134행:

```
이번 주에 걷어 낸 기능의 잔재, 쓰이지 않는 코드와 인자, 코드나 시험이 한 규칙을 두 군데에 따로 구현한 것과 그 둘 사이의 어긋남, 앞 상태를 서술하는 주석과 문서, 이 기계에만 맞는 경로와 수치가 여기에 든다.
```

### 영향
`library_ok`를 부르는 자리는 `finalize.py`의 699, 739, 757, 851, 887, 894, 904, 945, 1224행 아홉이고 모두 이름 붙인 인자만 쓰며 어느 것도 `due`를 넘기지 않는다. 시험에도 넘기는 자리가 없다. 그래서 381행의 `records if due else None`은 늘 `None`이고, 358행의 설명 「with the records when they are `due`」는 돌지 않는 경로를 말한다. 기록이 요소마다 있는지는 기록을 쓰는 자리인 `bring_records`가 1142행에서 `index_problems`를 직접 불러 확인한다.

이 값을 치르는 이는 이 함수를 읽고 고치는 다음 사람이다. 설명을 믿으면 합치기와 배열 단계에서도 기록 검사가 켜질 수 있다고 읽게 된다. 동작은 달라지지 않으므로 시험의 수리는 없다.

### 조각 1 — .claude/skills/do-math/runtime/finalize.py 349~350행
원래:
```
    def library_ok(self, label, base=None, files=None, replace=None, delete=(), extract=False, records=None,
                   due=False, keep=None, modules=None, onto=None, whole=True):
```
대체:
```
    def library_ok(self, label, base=None, files=None, replace=None, delete=(), extract=False, records=None,
                   keep=None, modules=None, onto=None, whole=True):
```

### 조각 2 — .claude/skills/do-math/runtime/finalize.py 358~358행
원래:
```
        `canon.check_applied`, with the records when they are `due`. `records` are the records whose
```
대체:
```
        `canon.check_applied` without the records, which `bring_records` checks. `records` are the records whose
```

### 조각 3 — .claude/skills/do-math/runtime/finalize.py 379~381행
원래:
```
            if not problems and extract and whole:
                problems = package.index_problems(index, self.root, self.statement_hash, self.allowed,
                                                  records if due else None)
```
대체:
```
            if not problems and extract and whole:
                problems = package.index_problems(index, self.root, self.statement_hash, self.allowed)
```


## R1-76
제목: `Run`이 받는 `config_path`를 아무것도 읽지 않는다

### 위치
`.claude/skills/do-math/runtime/finalize.py` 146~148행(`Run.__init__`)과 1894행(`main`이 넘기는 자리).

### 기준
`임시/do-math_검증_20261125-2/동결.md` 134행:

```
이번 주에 걷어 낸 기능의 잔재, 쓰이지 않는 코드와 인자, 코드나 시험이 한 규칙을 두 군데에 따로 구현한 것과 그 둘 사이의 어긋남, 앞 상태를 서술하는 주석과 문서, 이 기계에만 맞는 경로와 수치가 여기에 든다.
```

### 영향
`config_path`는 `runtime/` 전체에서 `finalize.py` 146행과 148행에만 나온다. `main`이 설정 파일의 경로를 넘기고 `Run`이 속성에 담지만 읽는 자리가 없다. 설정의 내용은 `load_config`가 읽어 셋째 인자로 이미 넘긴다. 이어 가는 운전이 같은 설정인지는 설정 내용의 해시로 가린다(446행). 시험의 `finalize.Run(...)` 호출 셋은 모두 인자 셋만 준다.

이 값을 치르는 이는 코드를 읽는 다음 사람이다. 속성이 있으면 운전이 설정 파일을 다시 읽는 자리가 있다고 읽게 된다. 명령줄의 `--config`는 그대로이고 동작은 달라지지 않는다.

### 조각 1 — .claude/skills/do-math/runtime/finalize.py 146~148행
원래:
```
    def __init__(self, instance, name, config, config_path=None):
        self.instance, self.name, self.config = Path(instance).resolve(), name, config
        self.config_path = config_path
```
대체:
```
    def __init__(self, instance, name, config):
        self.instance, self.name, self.config = Path(instance).resolve(), name, config
```

### 조각 2 — .claude/skills/do-math/runtime/finalize.py 1894~1894행
원래:
```
        code = Run(args.instance, args.name, load_config(args.config), args.config).run()
```
대체:
```
        code = Run(args.instance, args.name, load_config(args.config)).run()
```


## R1-79
제목: 설정이 받는 저자의 `orcid`와 `github`가 등록소 파일에 실리지 않는다

### 위치
`.claude/skills/do-math/runtime/package.py` 930행(`formalization`이 저자를 이름만으로 만든다). 받는 자리는 `.claude/skills/do-math/runtime/finalize.py` 93행이고, 운영자에게 알리는 자리는 `.claude/skills/do-math/reference/operations.md` 466행이다.

### 기준
`임시/do-math_검증_20261125-2/맥락.md` 291행:

```
its four files are made at the freeze; the author fields feed them
```

`임시/do-math_검증_20261125-2/동결.md` 143행:

```
반대로 사용자가 요구했으나 산출물에 실리지 않은 것과 가이드가 약속했으나 코드가 하지 않는 것은 능력의 추가가 아니고 누락이며, 결함이다.
```

`.claude/skills/do-math/reference/operations.md` 466행:

```
A list of objects with `name` and optionally `address`, `email`, `orcid`, `github`.
```

### 영향
`load_config`는 저자마다 `name`, `address`, `email`, `orcid`, `github`를 받는다. `address`와 `email`은 논문의 표제면으로 간다(`finalize.py` 1600행). `orcid`와 `github`는 받기만 하고 읽는 자리가 없다. `formalization`은 `project.authors`와 `project.responsible_maintainers`를 이름의 목록으로 쓴다.

운영자가 ORCID를 설정에 넣으면 거절도 경고도 없이 운전이 끝나고, 등록소 파일에는 이름만 실린다. 운영자는 제출 뒤에야 그것을 안다. 사용자가 승인한 요약은 저자 칸이 등록소의 네 파일로 들어간다고 적었다. 이 두 칸이 갈 자리는 그 파일뿐이다. 등록소가 읽는 형식은 구축 세션이 받아 둔 사본 `.skill-workspace/finalize-pipeline/registry/clones/PalomarRegistry_PalomarSubmission/README.md` 282~285행에 있다. 저자는 이름이거나, `name`에 선택 칸 `github`와 `orcid`를 가진 매핑이다. 같은 사본의 `scripts/submission_contract.py`는 책임 관리자도 같은 함수로 읽는다.

그래서 두 칸 가운데 하나라도 준 저자는 매핑으로, 주지 않은 저자는 지금처럼 이름으로 쓴다. 두 칸을 주지 않은 설정에서 파일은 한 바이트도 달라지지 않는다. `yaml_text`는 사전의 목록을 이미 쓴다. 기존 시험의 한 단언이 ORCID를 준 저자를 이름만으로 기대하고 있어 함께 고친다.

### 조각 1 — .claude/skills/do-math/runtime/package.py 930~930행
원래:
```
    names = [author['name'] for author in config['authors']]
```
대체:
```
    # A person is a name, or a mapping with the name where the configuration gives a GitHub login or an ORCID iD:
    # the two forms in which the registry reads an author and a responsible maintainer.
    names = [{'name': author['name'], **{key: author[key] for key in ('github', 'orcid') if author.get(key)}}
             if author.get('github') or author.get('orcid') else author['name'] for author in config['authors']]
```

### 조각 2 — .claude/skills/do-math/runtime/tests/test_finalize.py 1150~1150행
원래:
```
        self.assertEqual((meta['project']['name'], meta['project']['authors']), ('Odd numbers sum to squares', ['A. Author']))
```
대체:
```
        # The ORCID iD of an author goes with the name into the registry's file, for the author and for the maintainer.
        person = [{'name': 'A. Author', 'orcid': '0000'}]
        self.assertEqual((meta['project']['name'], meta['project']['authors'], meta['project']['responsible_maintainers']),
                         ('Odd numbers sum to squares', person, person))
```


## R1-80
제목: 세 거절 시험이 거절의 사유를 고정하지 않는다

### 위치
`.claude/skills/do-math/runtime/tests/test_finalize.py` 404행, 996행, 1202행.

### 기준
`기억/layer3/L-0023.md` 34행:

```
음성 시험은 거부된 사실만이 아니라 거부 사유를 고정한다.
```

`임시/do-math_검증_20261125-2/동결.md` 181행:

```
단언은 대상이 벗어나면 실패한다.
```

### 영향
404행의 시험은 색인의 한 구간을 한 줄 밀고 `package.take`가 `CanonError`를 내는지만 본다. `take`는 `CanonError`를 세 자리에서 낸다(`package.py` 295행, 304행, 307행). 루트가 색인에 없을 때, 색인이 든 파일이 라이브러리에 없을 때, 선언의 원문이 색인의 해시와 다를 때다. 이 시험이 겨누는 것은 셋째인데, 셋째 검사가 빠지고 앞의 둘 가운데 하나가 걸려도 시험은 통과한다.

996행과 1202행은 꾸러미 폴더가 이미 있을 때의 거절을 낱말 `exists` 하나로 확인한다. 프로그램이 내는 문면은 `<폴더> exists`다(`finalize.py` 460행, 466행). 지금의 프로그램에서 다른 거절이 이 낱말을 담는 경우는 확인하지 못했다. 확인한 것은 단언이 문면 전체가 아닌 한 낱말에 걸려 있어, 어느 폴더가 있다고 거절했는지를 고정하지 않는다는 사실이다. 세 자리 모두 프로그램이 내는 문면을 그대로 단언하게 고친다. 값을 치르는 것은 이 거절들을 고치는 다음 수리다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_finalize.py 404~404행
원래:
```
        with self.assertRaises(canon.CanonError):
```
대체:
```
        with self.assertRaisesRegex(canon.CanonError, 'the source of Small.unused_two is not the text the index'):
```

### 조각 2 — .claude/skills/do-math/runtime/tests/test_finalize.py 996~996행
원래:
```
        self.refused('exists', config=self.config())
```
대체:
```
        self.refused(f'{self.solved} exists', config=self.config())
```

### 조각 3 — .claude/skills/do-math/runtime/tests/test_finalize.py 1202~1202행
원래:
```
        self.assertIn('exists', self.said)
```
대체:
```
        self.assertIn(f'{self.solved} exists', self.said)
```


## R1-81
제목: operations.md가 게시 빌드의 컴파일이 실행 사정으로 끝난 경우를 적지 않고, 재부팅 뒤에도 같은 게시가 끝까지 간다고 적는다

### 위치
`.claude/skills/do-math/reference/operations.md` 594행(「Publication of a candidate」 절의 셋째 문단)과 646행(「Restarts, runner failures and installation updates」 절의 첫 문단)이다. 594행은 후보가 게시되지 못하는 까닭을 넷으로 든다.

```
It can nevertheless fail to apply or to build, through no defect of its mathematics: another publication replaced the proof it replaces, a new module's path is now taken, two candidates introduced the same name, or a machine check fails on the canon as it now is.
```

646행은 실행기를 다시 띄운 뒤의 게시를 이렇게 적는다.

```
Publication uses a saved identity, staging directory and Git commit; restarting continues the same publication, with the build it had started, and completes it and its follow-ups without publishing anything twice.
```

맞댄 코드는 `.claude/skills/do-math/runtime/runner.py` 775~782행(`advance_build`의 `build` 단계)과 700~719행(`publication_failed`), `.claude/skills/do-math/runtime/lean_broker.py` 1248~1254행(`collect`), 1296~1300행(`finish`), 1070~1078행(`settle_build`), `.claude/skills/do-math/runtime/canon.py` 968~979행(`build_outcome`)이다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 122행(목적 진술, 결함의 첫째 갈래)이다.

```
가이드가 약속하지만 코드가 하지 않는 동작, 코드가 하지만 가이드가 말하지 않아 작업 세션이나 운영자의 행동이 어긋나는 동작도 여기에 든다.
```

같은 문서 124행이다.

```
가이드와 코드가 어긋나면 어느 쪽도 그 자체로 기준이 아니다. 기준은 차례로 사용자 결정, 합의와 설계 기록 가운데 뒤의 사용자 결정이 바꾸지 않은 부분, 그리고 그 장치의 목적이다.
```

이 동작에 대한 사용자 결정은 `임시/do-math_검증_20261125-2/맥락.md` 208행(4.6절 「A publication build that fails for a reason of execution」)이 싣는다.

```
Asked how to dispose of six defects, the user answered for this one "4) pass" (session `3750b5d4`, 22 November 18:29:45Z), beside "apply" for the others.
```

```
Whether the sentence of the document still disagrees with it was not checked; making a document say what the program does is a separate matter and does not decide the behaviour.
```

### 영향
게시가 `build` 단계에 있고 그 빌드의 컴파일 하나가 돌고 있을 때 기계가 다시 켜진 경우를 코드로 따라갔다. 운영자가 `start`를 주면 새 실행기가 브로커를 띄운다. 새 브로커의 `collect`는 돌고 있던 컴파일의 호스트와 Lean이 모두 없고 `exit.json`도 없는 것을 보고 그 컴파일을 `the job host ended without recording an exit`라는 까닭으로 끝낸다(`lean_broker.py` 1248~1254행). 종료 코드가 없는 컴파일은 `failed`가 되고(1298~1300행), 그 모듈을 가진 빌드도 `failed`로 닫힌다(1070~1078행). 실행기의 `advance_build`는 닫힌 빌드가 성공이 아니면 까닭을 가리지 않고 `publication_failed`를 부른다(`runner.py` 775~782행). 그러면 후보는 대체 peer에게 가서 다시 만들어지고 새 검토를 받으며, organizer의 변경은 대체 organizer가 다시 만든다(700~719행). 시스템이 Lean 프로세스를 끝낸 경우와 빌드의 컴파일이 취소된 경우에도 `build_outcome`이 성공이 아니라고 답하므로(`canon.py` 968~979행) 같은 길로 간다. 프로그램을 실행해 재현하지는 않았다.

646행을 읽은 운영자는 재부팅 뒤에 같은 게시가 끝까지 간다고 기대한다. 실제로는 게시가 사라지고 `status`에 `the candidate could not be published on the current canon`으로 시작하는 오류를 가진 peer 작업이 생긴다. 594행은 게시 실패의 까닭을 정본이나 후보의 사정 넷으로만 들므로, 운영자는 이 오류를 후보나 정본의 결함으로 읽어 사용자에게 그렇게 보고하거나, 가이드와 다른 동작을 실행기의 고장으로 보고 복구를 시도할 수 있다.

어느 쪽을 고칠지는 사용자 결정이 정한다. 사용자는 이 동작을 보고받고 「4) pass」라고 답했고, 그 동작을 바꾸는 일은 사용자가 정할 일로 남았다. 그래서 동작은 그대로 두고 가이드가 그 동작을 말하게 한다. 조각 1은 594행의 까닭 목록에 실행 사정으로 끝난 빌드를 더하고, 조각 2는 646행에 재부팅으로 컴파일이 끝난 경우를 더한다. 두 조각은 문장을 더할 뿐이고 지우는 글이 없다. 두 문장을 그대로 단언하는 시험은 `runtime/tests/`에 없다.

### 조각 1 — .claude/skills/do-math/reference/operations.md 594~594행
원래:
```
A candidate was frozen when its peer's session ended, and other publications have changed the canon since. Statements never change in place, so what the candidate rests on is still there. It can nevertheless fail to apply or to build, through no defect of its mathematics: another publication replaced the proof it replaces, a new module's path is now taken, two candidates introduced the same name, or a machine check fails on the canon as it now is. A candidate that would not build would break the canon for every session, so the runner does not publish it. The work goes to a replacement peer, which receives the producer's work, the earlier peer's work and the reason, makes a new candidate, and that candidate receives a new review. An organizer's change that fails in the same way is made again by a replacement organizer. The pending job's error in `status` names the reason.
```
대체:
```
A candidate was frozen when its peer's session ended, and other publications have changed the canon since. Statements never change in place, so what the candidate rests on is still there. It can nevertheless fail to apply or to build, through no defect of its mathematics: another publication replaced the proof it replaces, a new module's path is now taken, two candidates introduced the same name, or a machine check fails on the canon as it now is. The build can also end without compiling for a reason that lies in neither the candidate nor the canon: a Lean process that the system ended, a compile that was cancelled, or a restart of the machine while a compile of the build was running. The runner does not tell that case from the others, and it does not build the same candidate again. A candidate that would not build would break the canon for every session, so the runner does not publish it. The work goes to a replacement peer, which receives the producer's work, the earlier peer's work and the reason, makes a new candidate, and that candidate receives a new review. An organizer's change that fails in the same way is made again by a replacement organizer. The pending job's error in `status` names the reason.
```

### 조각 2 — .claude/skills/do-math/reference/operations.md 646~646행
원래:
```
After a runner crash or machine reboot, use `start` on the same instance. The runner identifies existing processes by PID and creation identity, follows those still alive, and collects ended work. Publication uses a saved identity, staging directory and Git commit; restarting continues the same publication, with the build it had started, and completes it and its follow-ups without publishing anything twice. Do not delete locks or edit runner state to force recovery. Use shells at the same privilege level on Windows, because process-query access is part of liveness detection.
```
대체:
```
After a runner crash or machine reboot, use `start` on the same instance. The runner identifies existing processes by PID and creation identity, follows those still alive, and collects ended work. Publication uses a saved identity, staging directory and Git commit; restarting continues the same publication, with the build it had started, and completes it and its follow-ups without publishing anything twice. One case ends differently. The build goes on only where its compiles are still running, as they are after a runner crash, which leaves the broker alive. A reboot ends a compile that was running; the broker that the new runner starts records that compile as failed, and the publication then takes the path of a candidate that does not build, described under Publication of a candidate above. Do not delete locks or edit runner state to force recovery. Use shells at the same privilege level on Windows, because process-query access is part of liveness detection.
```


## R1-83
제목: 바뀐 산출물에서 멈춘 꾸러미 운전에 finalize.py가 내는 문장이 operations.md에 없는 처치를 권한다

### 위치
`.claude/skills/do-math/runtime/finalize.py` 191~193행(`Run.step`이 읽을 산출물의 해시가 기록과 다를 때 내는 `Stop`의 문장)이다. 이 문장은 `stopped`가 `report.md`의 「What the check found」 밑에 그대로 싣는다(같은 파일 1801~1810행). 같은 사정을 운영자에게 말하는 가이드의 자리는 `.claude/skills/do-math/reference/operations.md` 508행이다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 124행(목적 진술)이다.

```
가이드와 코드가 어긋나면 어느 쪽도 그 자체로 기준이 아니다. 기준은 차례로 사용자 결정, 합의와 설계 기록 가운데 뒤의 사용자 결정이 바꾸지 않은 부분, 그리고 그 장치의 목적이다.
```

사용자의 말은 `임시/do-math_검증_20261125-2/맥락.md` 277행(4.11절)에 있다.

```
I don't want a pipeline that would repeat back into its previous stages like we often did;
```

같은 문서 301행(4.11절)이 그 말에서 나온 장치를 적는다.

```
**A product is written once.** A later step compares a product's hash with the run's state before reading it; a difference stops the run and names the product, and nothing is silently made again.
```

가이드가 운영자에게 주는 처치는 `.claude/skills/do-math/reference/operations.md` 508행이다.

```
If a product was changed, put it back as it was. A run that cannot be continued is abandoned by removing its work folder, after which the command starts anew.
```

### 영향
두 운전 사이에 작업 폴더의 산출물 하나가 바뀌면 명령은 종료 코드 2로 멈추고, 운영자는 가이드가 시킨 대로 `report.md`를 읽는다. 거기에 실린 프로그램의 문장은 처치를 둘 든다. 하나는 산출물을 되돌리는 것이고, 다른 하나는 `state.json`에서 그 단계와 뒤 단계의 항목을 손으로 지워 그 단계들을 다시 만들게 하는 것이다. 가이드는 둘째 처치를 주지 않는다. 가이드의 처치는 산출물을 되돌리는 것과, 되돌릴 수 없으면 작업 폴더를 지우고 새로 시작하는 것이다. 운영자는 한 사정에 대해 서로 다른 지시 둘을 받는다.

틀린 쪽은 프로그램의 문장이다. 사용자는 끝난 단계로 되돌아가지 않는 파이프라인을 요구했고, 그 요구에서 나온 장치가 「산출물은 한 번 쓰고, 소리 없이 다시 만들지 않는다」이다. `state.json`의 항목을 손으로 지우는 처치는 끝난 단계를 다시 만드는 일이며, 그 결과가 맞는지를 프로그램이 보지 않는다. `Run.step`은 항목이 있는 단계에서 곧바로 돌아오고 그 단계가 읽은 것을 다시 대조하지 않는다(`finalize.py` 181~183행). 그래서 운영자가 지워야 할 항목 가운데 하나라도 남기면, 남은 단계의 산출물은 앞 단계를 다시 만들기 전의 입력에서 만든 그대로 꾸러미에 들어가고 운전은 멈추지 않는다. 다시 만든 앞 단계의 산출물이 전과 다르면, 해시 대조가 막으려던 상태(서로 맞지 않는 산출물로 꾸러미가 만들어지는 것)가 이 처치로 생긴다. 프로그램을 실행해 재현하지는 않았다.

조각 1은 문장의 처치를 가이드의 것으로 맞춘다. 문장의 앞부분(어느 산출물이 달라졌는가)은 그대로다. 조각 2는 이 경로를 지나는 시험이 보고에서 그 처치를 확인하게 한다. 그 시험은 지금 문장의 앞부분만 단언한다(`runtime/tests/test_finalize.py` 1234행).

### 조각 1 — .claude/skills/do-math/runtime/finalize.py 191~193행
원래:
```
                    raise Stop(f'the product {relative} is not what the step that wrote it left: its hash differs from '
                               'the one in state.json. A product is written once; restore it, or delete the entries of '
                               'that step and of the steps after it from state.json so that they are made again')
```
대체:
```
                    raise Stop(f'the product {relative} is not what the step that wrote it left: its hash differs from '
                               'the one in state.json. A product is written once: put it back as it was. A run whose '
                               'product cannot be put back is abandoned by removing its work folder, after which the '
                               'command starts anew')
```

### 조각 2 — .claude/skills/do-math/runtime/tests/test_finalize.py 1234~1234행
원래:
```
        self.assertIn('the product lib/1-taken is not what the step that wrote it left', report)
```
대체:
```
        self.assertIn('the product lib/1-taken is not what the step that wrote it left', report)
        self.assertIn('put it back as it was', report)
```


## R1-91
제목: 꾸러미 파이프라인 시험의 Lake 대역이 라이브러리에 없는 이름에도 공리 줄을 내 준다

### 위치
`.claude/skills/do-math/runtime/tests/test_finalize.py` 87~92행. `stand_in_lake`의 `env lean Check.lean` 분기가 `Check.lean`이 묻는 이름마다, 그 이름이 라이브러리에 있는지 보지 않고 `propext, Quot.sound` 공리 줄을 출력한다. 12~13행의 모듈 설명이 그 동작을 적는다.

### 기준
`기억/layer3/L-0023.md` 22행:

```
대역은 모르는 것을 성공으로 답하지 않고, 실제 생산자가 계산할 사실을 스스로 추론하거나 빠진 값을 채우지 않는다.
```

`임시/do-math_검증_20261125-2/맥락.md` 865행:

```
A stand-in does not answer the unknown with success, does not infer what the real producer would compute, and does not fill in what is missing.
```

### 영향
동결 단계는 `Check.lean`을 Lake로 돌려 근과 주정리의 공리 줄을 읽고, 줄이 없거나 허용 밖의 공리가 있으면 운전을 멈춘다(`runtime/finalize.py` 1476~1482행). 이 검사는 동결된 라이브러리가 허용 공리만으로 근을 증명한다는 것을 꾸러미가 내세우는 근거다. 프로그램이 `Check.lean`에 틀린 이름을 쓰게 되면(예: 정리를 옮기거나 이름을 바꾼 뒤 옛 이름을 묻는 결함) 실제 Lean은 그 이름을 모른다고 실패하지만, 지금의 대역은 그 이름에도 통과하는 공리 줄을 낸다. 그래서 동결까지 가는 시험 전부가 그런 결함을 통과시킨다.

수리는 대역이 `Check.lean`이 직접 또는 다른 모듈을 거쳐 들여오는 모듈들이 선언한 이름에만 공리 줄을 내고, 그 밖의 이름에서는 실패하게 한다. 선언과 들여온 모듈은 같은 대역이 `DoMathExtract.lean`에 이미 쓰는 `canon_lean.library`와 `canon_lean.imported`로 읽는다. 두 호출은 같은 작업 폴더에서 돈다. 동결 단계가 두 명령을 모두 `stage` 폴더에서 실행하기 때문이다(`runtime/finalize.py` 1433~1434행, 1476행).

지금의 시험이 그대로 통과한다는 것은 독해로 확인했다. `Check.lean`은 근의 모듈 하나를 들여오고 근과 주정리를 묻는다(`runtime/package.py` 855~861행, `runtime/finalize.py` 1415행). 픽스처에서 근의 모듈은 `Small.Step`과 `Small.Helper`를 들여오고(254행), 시험이 주정리로 고르는 `Small.sq_step`, `Small.twice_zero`, `Small.named_four`는 그 두 모듈에 있다(125~135행, 1360행, 1400~1405행). 대역이 출력하는 실패 문구는 Lean의 문구를 흉내 내지 않고 대역의 것임을 밝힌다. 실행해 보지는 않았다.

이 수리가 닫지 않는 것이 둘 있다. `build`는 여전히 어떤 프로젝트에도 성공하고, 공리 줄의 내용은 여전히 대역이 정한 기본값이다. 둘 다 Lean을 흉내 내는 더 큰 대역을 요구하므로 이 항목에 넣지 않았다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_finalize.py 12~13행
원래:
```
runs the stand-in compiler's extraction; `env lean Check.lean` prints an axioms line for every name
that Check.lean asks about. Run as `test_finalize.py version` it is Lean's version command.
```
대체:
```
runs the stand-in compiler's extraction; `env lean Check.lean` prints an axioms line for every name
that Check.lean asks about, and fails at a name that no module Check.lean imports declares. Run as
`test_finalize.py version` it is Lean's version command.
```

### 조각 2 — .claude/skills/do-math/runtime/tests/test_finalize.py 87~92행
원래:
```
    if arguments[:2] == ['env', 'lean'] and arguments[2] == 'Check.lean':
        for name in re.findall(r'^#print axioms (\S+)$', Path('Check.lean').read_text(encoding='utf-8'), re.M):
            axioms = settings.get('axioms', {}).get(name, ['propext', 'Quot.sound'])
            print(f"{name} : a statement\n'{name}' depends on axioms: [{', '.join(axioms)}]" if axioms
                  else f"'{name}' does not depend on any axioms")
        return 0
```
대체:
```
    if arguments[:2] == ['env', 'lean'] and arguments[2] == 'Check.lean':
        sys.path.insert(0, str(THIS.parent))
        import canon_lean
        text = Path('Check.lean').read_text(encoding='utf-8')
        # As in Lean, a name is known when a module that the file imports, directly or through others, declares it.
        visible = canon_lean.imported('.', re.findall(r'^import (\S+)$', text, re.M))
        declared = {declaration['user'] for declaration in canon_lean.library('.')
                    if declaration['module'] in visible and not declaration['private']}
        for name in re.findall(r'^#print axioms (\S+)$', text, re.M):
            if name not in declared:
                print(f'Check.lean: the stand-in finds no declaration {name} in the modules the file imports')
                return 1
            axioms = settings.get('axioms', {}).get(name, ['propext', 'Quot.sound'])
            print(f"{name} : a statement\n'{name}' depends on axioms: [{', '.join(axioms)}]" if axioms
                  else f"'{name}' does not depend on any axioms")
        return 0
```


## R1-M2
구성: R1-06 · R1-07 · R1-82

### 위치
`.claude/skills/do-math/reference/operations.md`의 두 종료 코드 표다. 하나는 429~434행에 있는 논문 명령의 표이고, 다른 하나는 500~504행에 있는 꾸러미 명령의 표다. 두 표는 종료 코드 2에 뜻을 하나씩만 준다. 433행은 「원고가 만들어졌고 지적이 열린 채 남았다」이고, 504행은 「단계가 검사를 통과하지 못했다」이다. 이 표들과 맞대는 코드는 `.claude/skills/do-math/runtime/paper.py` 5203행과 `.claude/skills/do-math/runtime/finalize.py` 1892행의 `args = parser.parse_args(argv)`다. 두 줄 모두 거절을 종료 코드 1로 바꾸는 `try` 블록보다 앞에 있다. 그래서 `argparse`가 읽지 못한 명령줄은 종료 코드 2로 끝난다. `paper.py`에서는 5167행이 `--out`을 `required=True`로, `finalize.py`에서는 1890행이 `--name`을 `required=True`로 둔다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 122행(목적 진술, 결함의 첫째 갈래)이다.

```
가이드가 약속하지만 코드가 하지 않는 동작, 코드가 하지만 가이드가 말하지 않아 작업 세션이나 운영자의 행동이 어긋나는 동작도 여기에 든다.
```

운영자가 종료 코드 2를 어떻게 읽을지는 `.claude/skills/do-math/reference/operations.md` 433행의 첫 두 칸과 504행이 정한다.

```
| 2 | The manuscript was produced, and findings stayed open after the bounded repairs. |
```

```
| 2 | A stage could not meet its check. | Read `report.md`, which names the step, the check and what the check found. Remove the cause and give the same command again. |
```

### 영향
`argparse`는 모르는 옵션이나 빠진 필수 인자를 만나면 사용법과 오류를 표준 오류에 쓰고 종료 코드 2로 끝난다. 이때 두 명령은 세션을 띄우지 않고 파일도 쓰지 않는다.

논문 명령에서 운영자가 이미 끝난 운전의 폴더에 `--open-findings`를 주면서 옵션 이름 하나를 잘못 적었다고 하자. 표는 종료 코드 2를 「원고가 만들어졌고 지적이 남았다」로 읽게 하고, `log.json`의 마지막 `end` 이벤트를 읽으라고 한다. 그 이벤트는 앞 운전이 남긴 것이다. 그래서 운영자는 돌지 않은 처리의 결과라고 여기며 앞 운전의 남은 지적을 사용자에게 보고하게 된다. 꾸러미 명령에서도 같은 일이 생긴다. 멈춘 운전은 같은 명령을 같은 인자로 다시 주어 잇는데, 이때 `--name`을 빠뜨리면 종료 코드 2가 나온다. 표는 `report.md`를 읽으라고 하지만, 작업 폴더의 `report.md`는 앞서 멈췄을 때 쓰인 것이다. 운영자는 같은 단계가 다시 실패했다고 읽고, 이미 없앤 원인을 다시 찾거나 같은 정지를 사용자에게 한 번 더 보고한다.

고칠 쪽은 가이드다. 스킬 밖의 `docs/do-math/running.md` 312행이 논문 명령에 대해 이 동작을 이미 적고 있다. 코드의 종료 코드를 바꾸면, 조각으로 고칠 수 없는 그 문서가 틀리게 된다. 그래서 두 표의 행은 그대로 두고, 표마다 뒤에 문단 하나를 더해 읽지 못한 명령줄의 2와 그때 폴더에 남은 것의 출처를 적는다. 지우는 글은 없다.

### 근거
세 구성 항목은 결함과 수리 방향이 같다. R1-06은 논문 표를, R1-07은 꾸러미 표를 다루고, R1-82는 두 표를 함께 다룬다. 사본에서 다음을 확인했다. `paper.py` 5203행과 `finalize.py` 1892행의 `parse_args`는 `try` 앞에 있다. `paper.py` 5167행의 `--out`과 `finalize.py` 1890행의 `--name`은 필수 인자다. `operations.md` 433행과 504행은 기준에 인용한 그대로다. 435행과 505행은 표 바로 뒤의 빈 행이므로, 두 틈에 「문단 + 빈 행」을 넣으면 뒤따르는 문단과의 간격이 유지된다. `docs/do-math/running.md` 312행이 「A command line that `paper.py` cannot parse also exits with 2, with a usage message in place of a result.」임을 원문에서 확인했다.

취한 것은 다음과 같다. 두 표를 하나의 지적으로 묶는 R1-82의 구성을 취했다. 논문 쪽 사례는 R1-82의 `--open-findings` 오타 사례를 취했다. 이 사례에서 운영자가 앞 운전의 결과를 이번 결과로 보고하는 경로가 가장 구체적이기 때문이다. 꾸러미 쪽에는 R1-07이 짚은 「`Run`이 만들어지기 전이라 `report.md`가 쓰이지 않는다」는 사실을 취했다. 대체 문면에는 R1-07의 「no run was started or continued」를 취했다. R1-82의 「does nothing else」보다 운영자가 무엇이 일어나지 않았는지를 더 정확히 알 수 있다. 「earlier stop of the same run」을 「earlier start」보다 앞세운 이유도 같다.

버린 것은 다음과 같다. R1-82가 근거로 든 `depmap.py`와 `operations.md` 391행의 선례, 그리고 「이 표를 단언하는 시험이 `runtime/tests/`에 없다」는 주장은 이번에 확인하지 않았으므로 옮기지 않았다. 수리 방향은 `running.md` 312행만으로도 선다. 운영자가 실제로 읽는 문서가 `operations.md`뿐이라는 R1-06의 주장도 확인하지 않았으므로 옮기지 않았다.

구성 항목 사이에 사실의 어긋남은 없다. 문구만 갈렸고, 두 조각은 같은 틀(무엇이 2를 내는가, 그때 무엇이 일어나지 않는가, 폴더에 남은 것은 누구의 것인가)로 하나로 녹여 썼다. 지급 키 밖에서 새 결함은 보지 못했다.

### 조각 1 — .claude/skills/do-math/reference/operations.md 행 435 뒤
대체:
```
A command line that the command cannot read, for example one without `--out` or with an option it does not have, also ends with exit code 2. The usage and the error are then on standard error, no session was launched and nothing was written, so the row for 2 does not apply. What the folder given to `--out` holds, the last `end` event of its `log.json` included, was then left by an earlier run and is not a result of this command.

```

### 조각 2 — .claude/skills/do-math/reference/operations.md 행 505 뒤
대체:
```
A command line that the command cannot read, for example one without `--name` or with an option it does not have, also ends with exit code 2. The usage and the error are then on standard error, no run was started or continued, and no `report.md` was written, so the row for 2 does not apply. A `report.md` in the work folder then belongs to an earlier stop of the same run and is not an account of this command.

```


## R1-M5
구성: R1-24 · R1-89

### 위치
`.claude/skills/do-math/runtime/tests/support.py` 168~179행의 `InstanceCase.setUp`, `.claude/skills/do-math/runtime/tests/test_paper.py` 404~428행의 `PaperCase`, `.claude/skills/do-math/runtime/tests/test_finalize.py` 245~266행의 `FinalizeCase`.

`InstanceCase.setUp`은 시험마다 두 가지를 복사한다. 하나는 `init`이 만든 인스턴스를 `self.root / 'instance'`로 뜨는 복사(173행)이고, 다른 하나는 설치된 스킬의 `reference/`, `roles/`, `resume/`와 `SKILL.md`를 `self.skill`로 뜨는 복사(175~179행)다. `PaperCase.setUp`은 프로세스의 첫 시험이 아니면, `FinalizeCase.setUp`은 첫 시험에서도, 그 뒤에 근이 증명된 인스턴스를 `self.root / 'settled'`로 다시 복사해 `self.instance`를 그쪽으로 바꾼다. 그래서 방금 뜬 `self.root / 'instance'`는 어느 시험도 읽지 않는다. 가이드 사본도 실행기나 팩 조립, 재개 글, 꾸러미 지침을 다루는 시험만 읽고 나머지 시험은 만들기만 한다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 132행:

```
넷 가운데 하나를 어긴 시험, 어떤 시험도 알아채지 못할 동작, 확인하는 것에 견주어 지나치게 오래 걸리는 시험, 한 번의 실행 뒤에 남는 찌꺼기가 결함이다.
```

`임시/do-math_검증_20261125-2/동결.md` 351행:

```
시험의 비용을 줄이는 수리는 그 시험의 시작 상태, 실제 경로, 단언을 잃지 않는다.
```

`임시/do-math_검증_20261105/동결.md` 56행(사용자의 요구):

```
(d) tests of the actual intended runtime behavior rather than a divergent imitation, assertions capable of failing when behavior deviates, and simple, cost-effective tests without unnecessary machinery;
```

`기억/layer3/L-0023.md` 73행:

```
시험 비용을 줄일 때에는 단언뿐 아니라 시작 상태와 실제 경로를 보존한다.
```

### 영향
두 복사는 모두 시험이 쓰지 않는 것을 시험마다 만든다. 가이드 사본은 파일 36개, 738,006바이트이고, `support.py`를 들이는 열네 모듈의 `InstanceCase` 계열 시험이 전부 이 값을 치른다. 그 가운데 `test_paper.py`에는 `self.skill`을 읽는 자리가 없고, `test_canon.py`의 `CandidateToolTests` 열아홉 시험 가운데 게시를 거치는 것은 하나다. 버려지는 인스턴스 사본은 `PaperCase`의 93개 시험과 `FinalizeCase`의 47개 시험 가운데 139개가 치른다. 그 사본은 Git 저장소와 컴파일 캐시를 담고, 맥락 문서 7.4절의 기록으로 두 모듈은 합쳐 742초, 스위트 전체 시간의 삼분의 일쯤을 쓴다. 두 복사를 덜어 줄어드는 시간은 재지 않았다. 이 런은 시험을 돌리지 않는다.

수리는 두 복사를 각각 쓰는 자리로 옮긴다. 가이드 사본은 `self.skill`을 처음 읽는 순간에 같은 경로로 만든다. 인스턴스 사본은 `setUp`이 복사할 원본을 `starting_instance` 메서드에서 얻게 하고, 두 픽스처가 근이 증명된 인스턴스를 이미 가졌으면 그것을 돌려주게 한다. 그러면 `setUp`의 한 번의 복사가 곧 시험이 쓸 인스턴스가 된다. 시험이 받는 시작 상태와 실제 경로와 단언은 그대로다.

### 근거
두 구성 항목은 같은 `setUp`의 서로 다른 복사를 겨누고, 두 수리는 서로 독립이어서 둘 다 취했다. 어긋나는 주장은 없다. 겹친 자리는 `support.py` 168~181행 하나이고, 조각 2가 두 항목의 변경을 한 문면으로 담는다: `setUp`은 `starting_instance()`를 복사하고, `skill`은 `cached_property`가 되며, `starting_instance`의 기본 구현이 `configure` 앞에 선다.

기준 인용 넷은 원문에서 확인했다. 동결문 132행 인용은 그 행의 부분 문장이고, `임시/do-math_검증_20261105/동결.md` 56행 인용도 그 행 안의 (d) 구절이다. R1-24가 인용한 132행 앞부분(사용자의 요구 넷)은 같은 행이므로 짧은 쪽 하나로 모았다.

사본에서 확인한 것: `self.skill`에 값을 대입하는 자리는 `support.py` 175행 하나여서 `cached_property`와 부딪치는 대입이 없다. `FinalizeCase.setUp`은 `self.skill / 'finalize'`에 파일을 쓰므로 그 시험들은 지금처럼 사본을 갖는다. `PaperCase`의 첫 시험은 `_SETTLED`가 아직 없어 `template(...)`의 사본 위에서 게시하고, 뒤의 시험은 지금 `settled`에 받던 것과 같은 `_SETTLED`의 사본을 `instance`에 받는다. 지우는 `stop_broker` 정리는 `InstanceCase.setUp`이 `self.instance`에 이미 등록한다. `FinalizeCase`의 첫 시험은 이제 방금 게시하고 브로커를 멈춘 원본 위에서 도는데, `_SETTLED`는 그 직후에 뜬 사본이므로 내용이 같다. 지금의 `FinalizeCase`는 `settled`에 `stop_broker` 정리를 등록하지 않는데, 수리 뒤에는 `instance`에 등록된 정리가 그 몫을 한다. 폴더 이름 `settled`에 기대는 시험은 없다고 R1-89가 적었고, 이 병합은 그 주장을 다시 세지 않았다.

R1-89가 지적한 `InstanceCase.scenario`(199~213행)의 같은 꼴 낭비는 시험 본문이 시나리오를 고르는 구조여서 이 수리로 닫히지 않는다. 지급 키 밖이므로 바꾸지 않고, 회수는 다음 라운드의 수리에 둔다.

### 조각 1 — .claude/skills/do-math/runtime/tests/support.py 9~9행
원래:
```
import atexit
```
대체:
```
import atexit
from functools import cached_property
```

### 조각 2 — .claude/skills/do-math/runtime/tests/support.py 168~181행
원래:
```
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.instance = self.root / 'instance'
        shutil.copytree(template(self.root_variant), self.instance)
        self.addCleanup(stop_broker, self.instance)
        self.skill = self.root / 'skill'
        installed = Path(__file__).resolve().parents[2]
        for name in ('reference', 'roles', 'resume'):
            shutil.copytree(installed / name, self.skill / name)
        shutil.copyfile(installed / 'SKILL.md', self.skill / 'SKILL.md')

    def configure(self, **changes):
```
대체:
```
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.instance = self.root / 'instance'
        shutil.copytree(self.starting_instance(), self.instance)
        self.addCleanup(stop_broker, self.instance)

    @cached_property
    def skill(self):
        """A copy of the installed guides, made when a test first asks for it; a test that asks for none makes none."""
        skill = self.root / 'skill'
        installed = Path(__file__).resolve().parents[2]
        for name in ('reference', 'roles', 'resume'):
            shutil.copytree(installed / name, skill / name)
        shutil.copyfile(installed / 'SKILL.md', skill / 'SKILL.md')
        return skill

    def starting_instance(self):
        """The instance that setUp copies for the test: the instance as `init` created it.

        A fixture whose tests all begin on research that it publishes once per test process returns
        that instance instead, so that no test copies an instance it then puts aside."""
        return template(self.root_variant)

    def configure(self, **changes):
```

### 조각 3 — .claude/skills/do-math/runtime/tests/test_finalize.py 245~248행
원래:
```
class FinalizeCase(InstanceCase):
    """An instance whose root is proved in Lean through a step, made once through the real publication path."""

    def setUp(self):
```
대체:
```
class FinalizeCase(InstanceCase):
    """An instance whose root is proved in Lean through a step, made once through the real publication path."""

    def starting_instance(self):
        return _SETTLED or super().starting_instance()

    def setUp(self):
```

### 조각 4 — .claude/skills/do-math/runtime/tests/test_finalize.py 265~266행
원래:
```
        self.instance = self.root / 'settled'
        shutil.copytree(_SETTLED, self.instance)
```
대체:
```

```

### 조각 5 — .claude/skills/do-math/runtime/tests/test_paper.py 404~407행
원래:
```
class PaperCase(InstanceCase):
    """An instance whose root is proved in Lean, made once through the real publication path."""

    def setUp(self):
```
대체:
```
class PaperCase(InstanceCase):
    """An instance whose root is proved in Lean, made once through the real publication path."""

    def starting_instance(self):
        return _SETTLED or super().starting_instance()

    def setUp(self):
```

### 조각 6 — .claude/skills/do-math/runtime/tests/test_paper.py 425~428행
원래:
```
        else:
            self.instance = self.root / 'settled'
            shutil.copytree(_SETTLED, self.instance)
            self.addCleanup(stop_broker, self.instance)
```
대체:
```

```


## R1-M9
구성: R1-39 · R1-86

### 위치
`.claude/skills/do-math/reference/operations.md` 413행(「The paper」 절의 `--from-draft` 문단)에 있는 다음 문장이다.

```
The command keeps a copy of the draft as `draft.json` when the run begins, and `--resume` and `--open-findings` take the declarations from that copy when they compare the canon with `materials.json`, so the folder of the draft is not needed again.
```

이 문장과 맞대는 코드는 `.claude/skills/do-math/runtime/paper.py`에 있다. 4985~4986행은 운전을 시작할 때 `draft.json`만 운전 폴더에 쓴다. 4965행과 4993행은 처음에 받은 초안 폴더의 경로를 운전 기록에 남기고, 이어 가는 운전은 그 경로를 다시 쓴다. 5014~5016행은 계획이 없을 때 `plan_from_draft`를 부르고, 3429행의 `plan_from_draft`는 `read_draft(folder)`로 초안 폴더를 읽는다. 2990~2995행의 `read_draft`는 그 폴더에 `plan.json`, `study.md`, `draft.json` 가운데 하나라도 없으면 멈춘다. 운전 폴더의 `plan.json`과 `study.md`는 3455~3459행에서 계획이 검사를 통과하거나 계획 세션이 고친 뒤에 `keep_plan`(3414~3417행)이 쓴다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 128행(목적 진술, 결함의 갈래)이다.

```
그 독자에게 맞지 않는 내용, 같은 사항에 대해 가이드끼리 어긋나는 서술, 코드의 실제 동작과 어긋나는 서술, 더는 없는 것을 말하는 서술, 의도를 정확히 전하지 못하는 서술이 결함이다.
```

프로그램이 무엇을 옮겨 두고 왜 옮기는지는 `runtime/paper.py` 4934~4936행의 주석이 적는다. 옮겨 두는 것은 재료를 정하는 데 쓰이는 초안이고, 목적은 재료를 `materials.json`의 것과 같게 하는 것이다.

```
    # A paper that is written from a draft has among its materials the declarations that closed a gap of the
    # draft. A run that is continued takes them from the draft it recorded when it began, so that the materials
    # are those of materials.json whatever has become of the folder the draft came from.
```

### 영향
413행이 드는 까닭은 선언을 `draft.json`의 사본에서 취한다는 것이다. 그 까닭은 초안의 `plan.json`과 `study.md`에는 미치지 않는다. 그래서 「다시 필요하지 않다」는 옮긴 계획이 운전 폴더에 `plan.json`으로 놓인 뒤에만 성립한다.

그 전에 운전이 멈추는 일은 실제로 있을 수 있다. 옮긴 계획이 검사에 걸리면 계획을 고치는 세션이 세 번까지 뜨고(3455행), 그 동안 운전 폴더에는 `materials.json`과 `draft.json`만 있다. 이 상태에서 `--resume`으로 이으면 `produce`가 `plan_from_draft`를 다시 부르고, 이 함수가 기록된 초안 폴더에서 세 파일을 다시 읽는다. `runtime/tests/test_paper.py` 3103~3146행의 시험이 이 경로(계획을 고치는 세션들이 쓸 것을 남기지 않아 멈춘 운전을 `--resume`으로 잇는다)를 지나며, 그 시험에서는 초안 폴더가 그대로 남아 있다.

413행을 믿고 운전을 시작한 뒤 초안 폴더를 지우거나 옮긴 운영자는, 운전이 계획 단계에서 멈췄을 때 그것을 이을 수 없다. `read_draft`가 `holds no draft of this command to write the paper from`으로 멈추고 명령은 종료 코드 1로 끝난다. 꾸러미 파이프라인은 초안 폴더를 작업 폴더 안에 그대로 두므로 이 경우에 들지 않는다.

### 근거
두 구성 항목은 같은 문장, 같은 기준(동결문 128행), 같은 코드 경로를 들고 같은 결론에 이른다. 어긋나는 사실 주장은 없다. 병합자는 사본의 `paper.py`에서 2990~2995행, 3414~3417행, 3429행, 3455~3459행, 4934~4936행, 4965행, 4985~4986행, 4993행, 5014~5016행을 읽어 두 항목의 서술이 코드와 맞음을 확인했다. 동결문 128행의 인용은 두 항목이 같은 문면을 들었으므로 그 문면을 옮겼다. `test_paper.py` 3103~3146행에 관한 R1-39의 서술은 병합자가 직접 읽지 않았고, R1-39의 서술을 그대로 옮겼다. 프로그램을 실행해 재현하지는 않았다(R1-86도 같은 사실을 적는다).

위치 칸은 R1-86의 코드 대조 목록을 바탕으로 하고, R1-39가 든 4985~4986행(`draft.json`만 옮김)과 4993행을 더했다. 기준 칸에는 R1-39가 든 4934~4936행의 주석을 함께 실었다. 이 주석이 옮겨 두는 범위를 재료로 한정하므로, 프로그램이 아니라 문서를 고쳐야 한다는 판단의 근거가 된다.

대체 문면은 두 항목의 안을 하나로 녹였다. R1-86의 안은 「다시 필요하지 않다」가 성립하는 때를 정확히 좁히지만, 운영자가 무엇을 해야 하는지는 말하지 않는다. R1-39의 안은 계획과 독해 기록이 옮겨지지 않는다는 사실과, 폴더를 언제까지 두어야 하는지를 운영자에게 지시한다. 병합 문면은 두 항목 모두 남긴 원래 문장의 앞부분과 까닭(`draft.json` 사본으로 비교한다)을 그대로 둔다. 그 뒤에 R1-86처럼 「다시 필요하지 않다」를 운전 폴더에 `plan.json`이 놓인 뒤로 한정하고, R1-39처럼 `plan.json`과 `study.md`는 옮겨지지 않는다는 사실과 폴더를 그때까지 두라는 지시를 붙인다. 멈출 수 있는 계기로는 R1-86이 든 계획 세션의 수리를 예로 남겼다. 문단의 나머지 문장, 특히 마지막 문장 「`--resume` continues such a run without the folder being named again」은 코드(4965행이 기록된 경로를 다시 씀)와 맞으므로 바꾸지 않았다. 지우는 글은 없고, `runtime/tests/`에 이 문장을 단언하는 시험은 없다(두 항목의 서술).

지급 키 밖에서 새로 본 결함은 없다.

### 조각 1 — .claude/skills/do-math/reference/operations.md 413~413행
원래:
```
`--from-draft <folder>` writes the paper from a draft, on the instance as it is after the library was changed. The folder holds `plan.json`, `study.md` and `draft.json`, and in `draft.json` each gap that a declaration has closed names that declaration under `closed_by`, each statement and formula names under `element` the element that states it now, and one that had to go carries `"cut": true`. The materials of such a run are what the formal proof of the root rests on together with every declaration that `closed_by` names and the instance has, and everything those rest on, also where the proof of the root does not use them; `materials.md` and the files given to the sessions mark such an element as added for the draft of the paper, and `materials.json` names the declarations under `further`. A statement among them is taken only when its own proof is settled and formal. The command keeps a copy of the draft as `draft.json` when the run begins, and `--resume` and `--open-findings` take the declarations from that copy when they compare the canon with `materials.json`, so the folder of the draft is not needed again. No session plans the paper again and none reads the collection for a plan. The command brings the plan of the draft to the materials by script: an element that is no longer among the materials leaves the plan; a declaration that closed the gap of a numbered statement becomes the element of that statement, under its kind and its label; a declaration that closed the gap of a formula or an assertion is absorbed into the statement in whose proof the gap stood when that statement rests on it, and otherwise into the running text of the gap's section; a statement whose element now has a source is cited and not proved. The check of the plan then decides. Only when it finds problems does a planning session repair the plan, from the plan, the problems, the account of the papers and the draft, at most three times. The brief of each section carries the statements and formulas of that section as they were drafted, and the writer is told that they stand as drafted. Everything after the writing runs as in any run. `--resume` continues such a run without the folder being named again.
```
대체:
```
`--from-draft <folder>` writes the paper from a draft, on the instance as it is after the library was changed. The folder holds `plan.json`, `study.md` and `draft.json`, and in `draft.json` each gap that a declaration has closed names that declaration under `closed_by`, each statement and formula names under `element` the element that states it now, and one that had to go carries `"cut": true`. The materials of such a run are what the formal proof of the root rests on together with every declaration that `closed_by` names and the instance has, and everything those rest on, also where the proof of the root does not use them; `materials.md` and the files given to the sessions mark such an element as added for the draft of the paper, and `materials.json` names the declarations under `further`. A statement among them is taken only when its own proof is settled and formal. The command keeps a copy of the draft as `draft.json` when the run begins, and `--resume` and `--open-findings` take the declarations from that copy when they compare the canon with `materials.json`, so the folder of the draft is not needed for that comparison. The `plan.json` and the `study.md` of the draft are not copied when the run begins: they reach the folder of the run only when the plan of the draft has been brought to the materials and stands there as `plan.json`. A run that was stopped before that, as it can be while a planning session repairs the plan, reads them from the folder of the draft again when it is continued, and stops when that folder no longer holds them. Leave the folder of the draft as it is until the run has its own `plan.json`; after that it is not needed again. No session plans the paper again and none reads the collection for a plan. The command brings the plan of the draft to the materials by script: an element that is no longer among the materials leaves the plan; a declaration that closed the gap of a numbered statement becomes the element of that statement, under its kind and its label; a declaration that closed the gap of a formula or an assertion is absorbed into the statement in whose proof the gap stood when that statement rests on it, and otherwise into the running text of the gap's section; a statement whose element now has a source is cited and not proved. The check of the plan then decides. Only when it finds problems does a planning session repair the plan, from the plan, the problems, the account of the papers and the draft, at most three times. The brief of each section carries the statements and formulas of that section as they were drafted, and the writer is told that they stand as drafted. Everything after the writing runs as in any run. `--resume` continues such a run without the folder being named again.
```


## R1-M10
구성: R1-43 · R1-48 · R1-78 · R1-87

### 위치
`.claude/skills/do-math/runtime/tests/test_paper.py` 422행이다. `PaperCase.setUp`이 421행에서 `do-math-paper-` 임시 폴더를 만들고, 423행에서 루트가 증명된 인스턴스를 그 아래에 통째로 복사한다. 그 폴더의 제거는 422행에서 `atexit.register(shutil.rmtree, base, True)`로 등록된다. 수리가 새 이름을 들여와야 하므로 123행(`runtime_support`에서 들여오는 줄)도 함께 고친다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 132행:

```
넷 가운데 하나를 어긴 시험, 어떤 시험도 알아채지 못할 동작, 확인하는 것에 견주어 지나치게 오래 걸리는 시험, 한 번의 실행 뒤에 남는 찌꺼기가 결함이다.
```

Windows에서 지우기가 실패하는 까닭은 `.claude/skills/do-math/runtime/runtime_support.py` 497~498행(`remove_tree`의 설명)이 적는다.

```
    Windows refuses to remove a read-only file or directory. Git creates its object files read-only,
    and shutil.copytree keeps the flag in its copy. Every caller removes a tree whose contents remain
```

### 영향
복사되는 인스턴스는 제 Git 저장소를 담는다. Git은 객체 파일을 읽기 전용으로 만들고, `shutil.copytree`는 그 표시를 사본에 그대로 옮긴다. Windows는 읽기 전용 파일의 삭제를 거부한다. 422행이 넘기는 둘째 인자 `True`는 `ignore_errors`이므로 그 거부가 아무 표시 없이 버려진다. 그래서 Windows에서 `test_paper`를 한 번 돌릴 때마다 `instance/.git/objects`를 담은 `do-math-paper-*` 폴더 하나가 임시 디렉토리에 남는다. 그 값은 이 모듈을 돌리는 모든 실행이 디스크로 치른다.

같은 용도의 폴더를 `.claude/skills/do-math/runtime/tests/support.py` 149행과 209행은 이미 `remove_tree`로 지운다. 그 함수(`runtime_support.py` 494~506행)는 Windows가 거부한 자리에서 읽기 전용 표시를 걷고 다시 지운다. 수리는 422행이 같은 함수를 쓰게 하고, 123행이 그 이름을 들여오게 한다. 시험의 시작 상태와 경로, 단언은 바뀌지 않는다.

### 근거
네 구성 항목(R1-43, R1-48, R1-78, R1-87)은 같은 결함을 같은 기준으로 짚고, 두 조각에 글자 하나 다르지 않은 대체 문면을 냈다. 어긋남이 없으므로 그 문면을 그대로 취했다.

사본에서 확인한 사실은 다음과 같다. 동결문 132행의 인용 문장이 실재한다. `runtime_support.py` 497~498행의 인용과 494~506행의 `remove_tree` 정의가 실재한다. `tests/support.py`는 25행에서 `remove_tree`를 들여오고, 149행과 209행에서 `atexit.register(remove_tree, base)`를 쓴다. `test_paper.py` 123행은 `remove_tree`를 들여오지 않는다. 421~423행은 위치 칸이 적은 대로다. 수리 뒤에도 같은 파일에 `shutil.` 사용처가 남으므로(423행의 `copytree` 등) 112행의 `import shutil`은 그대로 둔다.

구성 항목별로 버린 것이 있다. R1-43이 적은 「임시 디렉토리에 `do-math-paper-` 폴더 69개, 그 가운데 65개는 `.git` 밖 파일이 없음」이라는 실측은 기계 상태라서 사본으로 확인할 수 없다. 결함의 성립은 코드 독해만으로 서므로 그 실측은 옮기지 않았다. R1-87은 실행해 보지 않고 독해로 확인했다고 밝혔으며, 이 병합도 수리본을 실행하지 않았다. R1-78과 R1-87이 적은 「`test_paper.py` 2763행과 `test_containment.py` 83행·152행의 `shutil.rmtree(folder, True)`는 Git 저장소를 담지 않아 같은 결함이 아니다」라는 판단은 이 수리의 범위를 정하는 데만 쓰이므로 영향 칸에 옮기지 않았다. R1-87이 언급한 `test_finalize.py` 262행의 같은 꼴은 별도 항목이 맡는다고 적혀 있으며, 이 묶음의 지급 키 밖이라 손대지 않았다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_paper.py 123~123행
원래:
```
from runtime_support import read_json, write_json
```
대체:
```
from runtime_support import read_json, remove_tree, write_json
```

### 조각 2 — .claude/skills/do-math/runtime/tests/test_paper.py 422~422행
원래:
```
            atexit.register(shutil.rmtree, base, True)
```
대체:
```
            atexit.register(remove_tree, base)
```


## R1-M11
구성: R1-44 · R1-49 · R1-77 · R1-88

### 위치
`.claude/skills/do-math/runtime/tests/test_finalize.py` 261~264행이다. `FinalizeCase.setUp`이 프로세스마다 한 번 게시를 마친 인스턴스를 `do-math-finalize-` 임시 폴더에 복사해 두고, 262행에서 그 폴더의 제거를 `shutil.rmtree(base, True)`로 등록한다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 132행이 시험의 결함을 정한다.

```
넷 가운데 하나를 어긴 시험, 어떤 시험도 알아채지 못할 동작, 확인하는 것에 견주어 지나치게 오래 걸리는 시험, 한 번의 실행 뒤에 남는 찌꺼기가 결함이다.
```

삭제가 실패하는 까닭은 `.claude/skills/do-math/runtime/runtime_support.py` 497~498행(`remove_tree`의 설명)이 적는다.

```
    Windows refuses to remove a read-only file or directory. Git creates its object files read-only,
    and shutil.copytree keeps the flag in its copy. Every caller removes a tree whose contents remain
```

### 영향
263행이 복사하는 인스턴스는 `.git`을 담고 있다. Git의 객체 파일은 읽기 전용이고 `shutil.copytree`가 그 표지를 사본에 옮기므로, Windows는 그 파일의 삭제를 거부한다. 262행의 둘째 인자 `True`(`ignore_errors`)가 그 거부를 소리 없이 버리기 때문에, Windows에서 `test_finalize`를 한 번 돌릴 때마다 `do-math-finalize-*` 폴더 하나가 임시 디렉토리에 남는다. 값을 치르는 쪽은 이 모듈을 돌리는 모든 실행이다.

이 모듈은 120행에서 이미 `remove_tree`를 들여와 1001행에서 `.git`을 지울 때 쓰고, `runtime/tests/support.py` 149행과 209행도 같은 종류의 임시 폴더에 `atexit.register(remove_tree, base)`를 등록한다. 수리는 262행이 그 함수를 등록하게 한다. 시험의 시작 상태, 경로, 단언은 바뀌지 않는다. `shutil`은 263행 등에서 계속 쓰이므로 들여오기는 그대로 둔다.

### 근거
구성 항목 넷(R1-44, R1-49, R1-77, R1-88)은 같은 자리, 같은 기준, 같은 대체 문면을 낸다. 어긋남은 없다. 사본에서 262행의 축자, 120행의 `remove_tree` 들여오기, 1001행의 사용, `runtime_support.py` 497~498행, `tests/support.py` 149·209행을 확인했고, 동결문 132행의 인용 문장도 원문에서 확인했다. R1-44의 「임시 디렉토리에 `do-math-finalize-` 폴더 41개, 그 가운데 39개는 `.git` 밖 파일이 없다」는 실측은 내가 재확인하지 않았으므로 옮기지 않았다. R1-88이 같은 원인으로 든 `test_paper.py` 422행도 확인하지 않아 옮기지 않았다. 변경을 실행해 보지는 않았다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_finalize.py 262~262행
원래:
```
            atexit.register(shutil.rmtree, base, True)
```
대체:
```
            atexit.register(remove_tree, base)
```


## R1-M12
구성: R1-45 · R1-90

### 위치
`.claude/skills/do-math/runtime/paper.py` 3185~3186행이 모든 명령 세션의 명령을 `worker_command(..., servers or {}, withheld=SELF_SCHEDULING)`로 만든다(`SELF_SCHEDULING`은 같은 파일 335행). 이 동작을 단언하는 시험이 없다. `.claude/skills/do-math/runtime/tests/test_paper.py` 440~442행의 대역 `PaperCase.command`는 `withheld`를 `**options`로 받아 버리고, 2687~2688행(`SessionsTests.test_sessions_are_launched_without_a_paper_with_servers_and_with_files_of_bytes`)은 서버만 단언한다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 132행:

```
넷 가운데 하나를 어긴 시험, 어떤 시험도 알아채지 못할 동작, 확인하는 것에 견주어 지나치게 오래 걸리는 시험, 한 번의 실행 뒤에 남는 찌꺼기가 결함이다.
```

`임시/do-math_검증_20261125-2/맥락.md` 303행:

```
**The pipeline's and the paper command's sessions cannot schedule themselves.** They are launched without the tools `ScheduleWakeup`, `CronCreate`, `CronDelete`, `CronList` and `Monitor`.
```

`임시/do-math_검증_20261125-2/맥락.md` 864행:

```
**A passing test testifies only to what it actually exercised.** A stand-in, a fixture or a patched name lets through every defect outside what it models.
```

### 영향
`paper.py` 3186행에서 `withheld=SELF_SCHEDULING`을 지우거나 335행의 상수에서 이름 하나를 빼도 스위트는 전부 통과한다. `test_context.py`는 `launch.worker_command`가 받은 이름을 `--disallowedTools`로 옮기는 것만 단언하고, 논문 명령과 꾸러미 파이프라인이 그 이름들을 실제로 넘기는지는 보지 않는다. 그 인자가 빠지면 `paper.py` 329~334행의 주석이 적은 일이 다시 일어난다. 세션이 스스로에게 알림을 걸어 두고 턴을 끝내면 CLI가 끝나지 않고, 프로그램은 CLI가 끝난 뒤에만 산출을 읽으므로 운전이 그동안 멈춘다(맥락 문서의 11분 사건). 운전 한 번이 여러 시간 걸리는 명령이라 이 회귀는 실제 운전에서만 드러난다.

수리는 대역이 세션마다 받은 `withheld`를 기록하게 하고, `paper.Sessions`를 직접 띄우는 `SessionsTests`가 세 세션 모두 다섯 도구 없이 떴음을 단언하게 한다. 꾸러미 파이프라인의 세션도 같은 `paper.Sessions.launch`로 뜨므로 이 단언이 두 명령이 지나는 한 줄을 덮는다. 기대값은 `paper.SELF_SCHEDULING`을 읽지 않고 도구 이름을 글자로 적는다. 상수에서 이름이 빠져도 통과하는 단언이 되지 않게 하기 위해서다.

### 근거
두 구성 항목은 같은 결함과 같은 세 조각 좌표를 가리키고 취지가 일치한다. 사본에서 `paper.py` 329~335행의 주석과 상수, 3185~3186행의 호출, `test_paper.py` 432행·440~442행·2687~2688행의 축자를 확인했고, 기준 인용 세 개(동결문 132행, 맥락 문서 303행·864행)의 실재를 원문에서 확인했다.

어긋남은 두 가지였다. 대역의 서명에 대해 R1-45는 `withheld=()` 매개변수를 새로 두었고 R1-90은 서명을 그대로 두고 `options.get('withheld')`로 읽었다. 인자가 빠졌을 때 R1-45는 `()`를, R1-90은 `None`을 기록하며, 어느 쪽이든 단언이 실패한다. 서명을 바꾸지 않는 R1-90 쪽이 변경이 작아서 그쪽을 취했다. 기록 목록의 초기화는 R1-45의 별도 줄 형태를 취해 기존 줄을 고치지 않았다. 단언 앞의 주석은 R1-90처럼 기존 주석을 그대로 두고 새 단언에 한 줄 주석을 붙였다.

R1-90이 언급한 `test_finalize.py` 287~288행의 대역은 지급 키 밖이라 변경하지 않았다. 파이프라인 세션이 `paper.Sessions.launch`를 지나므로 `SessionsTests`의 단언이 그 경로를 덮는다는 R1-90의 논거를 따랐고, 그 논거의 근거인 `finalize.py` 462행·525행은 이번에 대조하지 않았다.

### 조각 1 — .claude/skills/do-math/runtime/tests/test_paper.py 432~432행
원래:
```
        self.servers = []
```
대체:
```
        self.servers = []
        self.withheld = []
```

### 조각 2 — .claude/skills/do-math/runtime/tests/test_paper.py 440~442행
원래:
```
    def command(self, cli, model, effort, cwd, servers=None, **options):
        self.servers.append(servers)
        return Command(provider_for_model(model), [sys.executable, '-B', str(THIS), 'session', str(self.scenario)], Path(cwd))
```
대체:
```
    def command(self, cli, model, effort, cwd, servers=None, **options):
        self.servers.append(servers)
        self.withheld.append(options.get('withheld'))
        return Command(provider_for_model(model), [sys.executable, '-B', str(THIS), 'session', str(self.scenario)], Path(cwd))
```

### 조각 3 — .claude/skills/do-math/runtime/tests/test_paper.py 2687~2688행
원래:
```
        # Every session received the servers it was launched with, and the log is beside the sessions.
        self.assertEqual(self.servers, [servers] * 3)
```
대체:
```
        # Every session received the servers it was launched with, and the log is beside the sessions.
        self.assertEqual(self.servers, [servers] * 3)
        # Every session was launched without the tools by which it could arrange to be called again later.
        self.assertEqual(self.withheld, [('ScheduleWakeup', 'CronCreate', 'CronDelete', 'CronList', 'Monitor')] * 3)
```


## R1-72
제목: 간결화와 되접기 세션에게 루트와 주 정리의 이름·진술이 고정이라는 것이 전해지지 않는다

### 위치
`.claude/skills/do-math/runtime/package.py` 601~609행(`interface`), `.claude/skills/do-math/runtime/finalize.py` 841행과 1209행(두 단계가 `part.json`의 `interface`를 만드는 자리), `.claude/skills/do-math/finalize/simplify.md` 25행, `.claude/skills/do-math/finalize/foldback.md` 25행과 49행.

### 기준
`임시/do-math_검증_20261125-2/맥락.md` 286행:

```
One proof per package. The selection ends in a written decision that fixes the main theorem before any library work.
```

`.claude/skills/do-math/finalize/arrange.md` 34행:

```
`{{root}}` and `{{main}}` keep their names and their statements.
```

`.claude/skills/do-math/finalize/simplify.md` 31행:

```
Inside your part you may restate, merge, rename, move between your modules, make private or delete whatever the list `interface` does not name
```

### 영향
주 정리는 선택이 정하고, 그 뒤의 모든 단계가 `state['main']`의 이름으로 찾는다. 배열 지침은 루트와 주 정리가 이름과 진술을 지킨다고 적지만, 그보다 앞서 도는 간결화 지침과 뒤에 도는 되접기 지침에는 그 말이 없다. 두 지침에서 세션을 묶는 것은 `interface` 목록뿐이고, `interface`는 다른 부분의 모듈이 쓰는 선언만 담는다. 주 정리가 루트와 같은 부분에 있고 다른 부분이 쓰지 않으면 목록에 없다. 루트도 다른 부분의 선언이 쓰지 않는 한 목록에 없다.

재현 경로는 그런 부분의 간결화 세션이 지침대로 주 정리의 이름을 바꾸거나 `private`으로 만든 경우다. 그 부분은 빌드만으로 수락되고(`finalize.py` 850~851행), 합친 라이브러리의 검사도 주 정리를 보지 않는다. 배열 세션의 산출은 「the main theorem ... is not in the arranged library」로 두 번 거절되어 배열이 버려지고(952~953행), `state['main']`은 라이브러리에 없는 이름으로 남아 초안 단계에서 논문 명령에 넘겨진다(1172행). 논문 명령이 없는 이름을 받았을 때 어디에서 서는지는 확인하지 않았다. 늦어도 동결의 `entries[main]`(1455행)에서 `KeyError`로 선다. 진술만 바꾼 경우에는 아무 검사도 걸리지 않고, README가 싣는 주 정리의 진술이 선택이 적은 `sentence`와 `account`가 말한 정리와 달라진다. 되접기 지침 49행은 다른 부분이 쓰지 않는 선언을 제자리에서 고쳐 써도 된다고 하므로 같은 일이 동결 직전에도 가능하다.

세션에게 이미 「`interface`의 선언은 이름과 진술을 지킨다」는 규칙이 있으므로, 루트와 주 정리를 그 목록에 넣고 두 지침이 목록을 설명하는 문장을 맞춘다. 새 검사나 새 칸은 더하지 않는다. 지침 세 줄은 고쳐 쓰는 것이고 지우는 글은 없다. `runtime/tests/`에 이 문장들을 단언하는 시험은 없다(시험은 지침 파일을 한 줄짜리 대역으로 바꾼다).

시험은 주 정리가 루트와 같은 부분에 있는 기존 시나리오에서 간결화 세션이 받은 `part.json`의 `interface`를 본다. 고치기 전의 코드에서는 그 목록이 비어 있어 단언이 실패한다.

### 조각 1 — .claude/skills/do-math/runtime/package.py 601~609행
원래:
```
def interface(index, modules):
    """The declarations of a set of modules that elements of other modules use, with their statements."""
    modules = set(modules)
    used = set()
    for entry in index['entries'].values():
        if entry['module'] not in modules:
            used.update(entry['uses'] + entry['statement_uses'])
    return [{'declaration': name, 'statement': index['entries'][name]['statement']}
            for name in sorted(used) if name in index['entries'] and index['entries'][name]['module'] in modules]
```
대체:
```
def interface(index, modules, fixed=()):
    """The declarations of a set of modules that keep their names and statements, with their statements.

    They are the declarations that elements of other modules use, and those of `fixed` that lie in these
    modules: the root and the main theorem, which every later step of a run finds by name."""
    modules = set(modules)
    used = set(fixed)
    for entry in index['entries'].values():
        if entry['module'] not in modules:
            used.update(entry['uses'] + entry['statement_uses'])
    return [{'declaration': name, 'statement': index['entries'][name]['statement']}
            for name in sorted(used) if name in index['entries'] and index['entries'][name]['module'] in modules]
```

### 조각 2 — .claude/skills/do-math/runtime/finalize.py 841~841행
원래:
```
                'interface': package.interface(index, part['modules']),
```
대체:
```
                'interface': package.interface(index, part['modules'], (self.root, self.state['main'])),
```

### 조각 3 — .claude/skills/do-math/runtime/finalize.py 1209~1209행
원래:
```
                'inside': '', 'interface': package.interface(index, [m for m in modules if inside(m)]), 'cross': []})}
```
대체:
```
                'inside': '', 'interface': package.interface(index, [m for m in modules if inside(m)],
                                                             (self.root, self.state['main'])), 'cross': []})}
```

### 조각 4 — .claude/skills/do-math/finalize/simplify.md 25~25행
원래:
```
`modules` are the modules of your part. `inside` is what the reviewing session found worth simplifying in them; it read the whole library once and compiled nothing, so take its findings as the starting point of your reading and its proposals as proposals. `interface` lists the declarations of your part that modules of other parts use, each with its statement. `cross` lists the simplifications that reach beyond your part and that the review gave to you.
```
대체:
```
`modules` are the modules of your part. `inside` is what the reviewing session found worth simplifying in them; it read the whole library once and compiled nothing, so take its findings as the starting point of your reading and its proposals as proposals. `interface` lists the declarations of your part that keep their names and their statements, each with its statement: those that modules of other parts use, and the root and the main theorem where they lie in your part. The steps after this one find the root and the main theorem by name, and the package states the main theorem as it was chosen. `cross` lists the simplifications that reach beyond your part and that the review gave to you.
```

### 조각 5 — .claude/skills/do-math/finalize/foldback.md 25~25행
원래:
```
- `part.json`: your part. `modules` are the modules you may change. `interface` lists the declarations of your part that modules of other parts use, each with its statement. The fields `inside` and `cross` belong to an earlier step and may be empty.
```
대체:
```
- `part.json`: your part. `modules` are the modules you may change. `interface` lists the declarations of your part that keep their names and their statements, each with its statement: those that modules of other parts use, and the root and the main theorem where they lie in your part. The fields `inside` and `cross` belong to an earlier step and may be empty.
```

### 조각 6 — .claude/skills/do-math/finalize/foldback.md 49~49행
원래:
```
- A declaration of your part that no other part uses can be restated in place, and then every use of it inside your part is brought along.
```
대체:
```
- A declaration of your part that `interface` does not list can be restated in place, and then every use of it inside your part is brought along.
```

### 조각 7 — .claude/skills/do-math/runtime/tests/test_finalize.py 행 1367 뒤
대체:
```
        # The root and the main theorem keep their names and statements, and the part that holds them is told so.
        core = next(call for call in self.calls('simplify') if call['section'] == 'core')
        part = read_json(self.work / 'sessions' / core['folder'] / 'part.json')
        self.assertEqual([item['declaration'] for item in part['interface']], ['Small.root', 'Small.twice_zero'])
```

