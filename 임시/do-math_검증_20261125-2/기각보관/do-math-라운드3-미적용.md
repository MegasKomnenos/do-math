# 라운드 3 — 승인되었으나 적용하지 않은 항목

라운드 3의 심사에서 승인이 확정되었으나 적용에서 뺀 항목 9건의 원문이다. 뺀 까닭과 처리의 경위는 장부의 신호 처리 절에 있다. 좌표와 축자는 그 라운드의 사본 기준이어서 지금의 원본과 맞지 않을 수 있다. 이 파일은 런의 중간물이며 수리자, 병합자, 심사자에게 주지 않는다. 종료 보고가 이 항목들의 결함이 마지막 트리에 남았는지를 맞대어 적는다.

## R3-06
제목: 운영자 문서는 output_checked가 전송 검사의 통과를 뜻한다고만 적는데, 호스트는 후보가 바뀐 경우에도 그 값을 적는다

### 위치
- `.claude/skills/do-math/reference/operations.md` 620행, "Session hosts and continuation turns" 절의 둘째 문단 끝 문장.
- 맞대는 코드: `.claude/skills/do-math/runtime/ending.py` 24~25행과 229~233행.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 128행:

```
그 독자에게 맞지 않는 내용, 같은 사항에 대해 가이드끼리 어긋나는 서술, 코드의 실제 동작과 어긋나는 서술, 더는 없는 것을 말하는 서술, 의도를 정확히 전하지 못하는 서술이 결함이다.
```

`.claude/skills/do-math/reference/operations.md` 622행(사본), 운영자가 그 기록을 읽는다는 약속:

```
`status` exposes the host's `end_check` record in each session's state, including `maximum`, `resumptions`, `status`, the current request and `authorization`.
```

### 영향
620행은 review나 organizer의 `end_check`에 적힌 근거 `output_checked`를 "when the check passed"라고 풀이한다. 코드는 한 경우에 달리 한다. 전송 검사가 찾은 것이 "candidate changed after review assignment" 하나뿐이면, 호스트는 세션을 재개하지 않고 근거를 `output_checked`로, 설명을 그 문장으로 적는다(`ending.py` 230~232행). 검사는 통과하지 않았다. 그 뒤 실행기는 같은 검사를 다시 하고 후보를 되살리는 길로 간다(`runner.py` 485~490행, 운영자 문서 662행이 서술하는 처리).

이 문단의 독자는 `status`에서 한 review 세션의 `end_check`를 읽어 그 세션이 왜 끝났는지를 가리는 운영자다. 문서대로 읽으면 운영자는 그 review의 산출이 검사를 통과했다고 판단한다. 같은 `status`에서 그 일거리는 대기로 돌아가 있고 `last_error`는 후보가 바뀌었다고 말하므로, 두 기록이 서로 어긋나 보인다. 문서에는 이 경우를 가리키는 문장이 없어 운영자는 어긋남의 까닭을 코드에서 찾아야 한다.

수리는 그 문장 뒤에 두 문장을 더해 이 경우와, 그 처리를 서술한 절을 가리킨다. 지우는 글은 없다. 가이드가 "finding"을 review의 판정을 가리키는 낱말로 정의해 쓰므로, 더하는 문장은 그 낱말을 쓰지 않고 이 문단이 이미 쓰는 "what the check found"의 꼴을 따른다. 이 문장을 그대로 단언하는 시험은 `runtime/tests/`에 없다(`output_checked`를 담은 자리는 `test_ending.py` 224행과 271행이고, 둘 다 호스트의 기록을 본다). 271행의 시험이 이 동작을 이미 고정한다.

### 조각 1 — .claude/skills/do-math/reference/operations.md 620~620행
원래:
```
The host of a review or an organizer keeps its session alive in the same way, for a different reason. Such a session ends with its output, an assessment or an organization, and writes no end decision. When one of its turns ends and the output does not pass the transport check, the host resumes the same conversation and tells it what the check found, at most `max_end_resumptions` times. A reviewer's turn can end while the sub-reviewers it delegated to are still at work, and without this the whole review would be made again by a new session. The authorization in the session's `end_check` record then has the basis `output_checked` when the check passed, and `resumption_limit` when it still failed at the limit; in the second case the runner starts a new session for the stage, as it does after an interruption.
```
대체:
```
The host of a review or an organizer keeps its session alive in the same way, for a different reason. Such a session ends with its output, an assessment or an organization, and writes no end decision. When one of its turns ends and the output does not pass the transport check, the host resumes the same conversation and tells it what the check found, at most `max_end_resumptions` times. A reviewer's turn can end while the sub-reviewers it delegated to are still at work, and without this the whole review would be made again by a new session. The authorization in the session's `end_check` record then has the basis `output_checked` when the check passed, and `resumption_limit` when it still failed at the limit; in the second case the runner starts a new session for the stage, as it does after an interruption. One thing the check can find is not put to the session: that the candidate changed after the review was assigned, which no turn of the review can undo. When the check finds that and nothing else, the host resumes nothing and records `output_checked` with it as the `explanation` of the authorization, and the runner deals with the candidate as "Refusals, failed outputs and damaged candidates" below describes.
```


## R3-26
제목: --from-draft에 주는 초안의 문면이 무엇을 말해야 하는지를 운영자 문서가 적지 않는다

### 위치
요구가 있는 자리는 둘이다. `.claude/skills/do-math/reference/paper-method.md` 164행은 닫히지 않은 gap의 자리에서 논문이 라이브러리가 가진 것을 말한다고 정한다. `.claude/skills/do-math/runtime/paper.py` 1398~1406행(`drafted_lines`)은 초안의 문면이 모두 그 요소의 진술과 같다고 작성 세션에게 말한다. 그 내용이 실려야 하는데 없는 자리는 `.claude/skills/do-math/reference/operations.md` 417행의 `--from-draft` 문단이다.

### 기준
동결 목적 진술의 첫째 갈래(`임시/do-math_검증_20261125-2/동결.md` 122행):

```
가이드가 약속하지만 코드가 하지 않는 동작, 코드가 하지만 가이드가 말하지 않아 작업 세션이나 운영자의 행동이 어긋나는 동작도 여기에 든다.
```

방법 문서가 정한 것(`.claude/skills/do-math/reference/paper-method.md` 164행):

```
Where none is added, the paper states what the library has. After that the library is fixed, and every statement and every formula of the draft says what an element states.
```

프로그램이 작성 세션에게 하는 말(`.claude/skills/do-math/runtime/paper.py` 1400~1402행):

```
             'displayed formulas that its later proofs refer to. Each was then compared with the element named with it, '
             'and where the two differed the library or the draft was changed until they said the same. The library '
             'has not changed since, so each text below says exactly what its element says. It stands in the section '
```

### 영향
`--draft`가 남기는 `draft.json`에서, 스케치가 gap을 선언했고 비교가 「differs」라고 본 진술의 `text`는 논문이 바란 문면이다(paper.py 3709~3720행: 선언된 gap이 있으면 `text`는 스케치의 것 그대로이고 gap의 id가 붙는다). gap을 가진 수식은 `element`가 null이다(3722~3725행). `--from-draft`는 이 초안의 계획을 스크립트로 옮기고 계획 검사만 한다(`plan_from_draft`, 3508~3545행). 초안의 문면을 라이브러리와 다시 견주는 단계는 섹션을 쓰기 전에 없다. 그런 다음 `drafted_lines`가 `cut`이 아닌 진술과 수식을 모두 브리프에 싣고, 그 하나하나가 요소의 진술과 정확히 같으며 초안대로 선다고 적는다.

운영자 문서 417행은 `draft.json`에 갖춰야 할 것으로 셋을 든다. 닫힌 gap의 `closed_by`, 각 진술과 수식의 지금 `element`, 빠져야 하는 것의 `"cut": true`다. 어떤 선언도 닫지 못한 gap을 가진 진술의 `text`를 어떻게 해야 하는지는 말하지 않는다. 그 문서대로 `--draft`를 돌리고 닫힌 gap에 `closed_by`만 적어 `--from-draft`를 돌린 운영자의 운전에서는, 닫히지 않은 gap의 진술이 요소보다 강한 문면으로 브리프에 실리고 작성 세션은 그것이 라이브러리로 덮였다고 듣고 그대로 쓴다. 어긋남은 원고를 다 쓴 뒤의 진술 비교에서야 드러난다. 그 수리 세션이 받는 브리프는 여전히 같은 문면이 요소의 진술과 같다고 말하므로(수리의 브리프도 초안을 싣는다, 3452행), 세션은 서로 어긋나는 두 지시를 받는다. 요소가 없는 수식은 본문 비교에서 덮이지 않는 문장으로 잡힌다. 초안을 먼저 만드는 까닭이 이런 발견을 쓰기 전으로 당기는 것이므로(방법 문서 160행), 운영자가 손으로 돌리는 경로에서는 그 장치가 제 일을 하지 못한다.

꾸러미 파이프라인은 이 일을 스스로 한다. `compare_draft`가 닫히지 않은 gap의 진술을 요소의 진술로 고쳐 쓰거나 `cut`으로 표시한다(finalize.py 1359~1371행). 그래서 프로그램과 방법 문서는 서로 맞고, 틀린 쪽은 그 전제를 운영자에게 알리지 않는 운영자 문서다. 프로그램에 검사나 단계를 더하지 않고 문서에 한 문단을 더한다. 지우는 글은 없고, `SKILL.md`에서 링크로 닿는 `reference/operations.md` 안의 자리다.

### 조각 1 — .claude/skills/do-math/reference/operations.md 행 417 뒤
대체:
```

`--from-draft` does not compare the texts of the draft with the library before the sections are written. The brief tells each writer that every drafted statement and formula says exactly what its element states, and has it stand in the section as drafted. A draft as `--draft` leaves it does not yet meet this where the sketch declared a gap: the text there is what the paper wanted, which no element states. So in the `draft.json` that `--from-draft` is given, a statement whose gap no declaration closed has under `text` the statement as its element says it, and a formula that no element states carries `"cut": true`. The finalize pipeline brings its own draft to the library in this way before it has the paper written.
```


## R3-39
제목: 제 검사는 통과하고 병합 뒤의 전체 검사에만 걸리는 부분이 버려지지 않아 운전이 같은 자리에서 계속 멈춘다

### 위치
`.claude/skills/do-math/runtime/finalize.py` 885~921행(`Run.merge_parts`), 그 가운데 907~908행. 이 함수를 부르는 자리는 928~936행(`merge`, 단계 `2.4-merge`)과 1258~1262행(`foldback`, 단계 `2.6-foldback`)이다. 부분 하나의 검사가 빌드까지만 보는 자리는 864행(`simplify`의 `read`)과 1237~1238행(`foldback`의 `read`)이다. `.claude/skills/do-math/runtime/tests/test_finalize.py`에는 902~918행의 분기를 지나는 시험이 없다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 122행:

```
첫째는 코드의 결함이다. 실제 입력, 상태, 동시 실행, 실패 경로, Windows와 Linux의 프로세스·파일 동작에서 의도한 동작이 깨지는 것이 여기에 든다. 가이드가 약속하지만 코드가 하지 않는 동작, 코드가 하지만 가이드가 말하지 않아 작업 세션이나 운영자의 행동이 어긋나는 동작도 여기에 든다.
```

`.claude/skills/do-math/reference/operations.md` 510행:

```
Two kinds of failure are handled differently. A simplification that fails its check, whether one part's, the arrangement or one part's last changes, is discarded: that part of the library keeps the form it had, the run goes on, and `decisions.md` records it. Any other step that cannot meet its check stops the run.
```

`임시/do-math_검증_20261125-2/맥락.md` 302행:

```
- **Only simplifications may be discarded.** A part of the simplifying, arranging or fold-back steps that fails its check is dropped and keeps its previous form. Every other failed exit check stops the run with exit code 2, and the same command continues it.
```

`.claude/skills/do-math/finalize/common.md` 76행(세션이 받는 약속, 프로그램이 읽는 것):

```
The program reads that report for every theorem of the library, so a single open proof fails the step.
```

`임시/do-math_검증_20261125-2/동결.md` 132행:

```
넷 가운데 하나를 어긴 시험, 어떤 시험도 알아채지 못할 동작, 확인하는 것에 견주어 지나치게 오래 걸리는 시험, 한 번의 실행 뒤에 남는 찌꺼기가 결함이다.
```

### 영향
부분 하나의 산출을 받아들이는 검사(864행, 1237~1238행)는 `library_ok`를 `extract` 없이 부른다. 그 검사는 파일의 꼴, 정의 모듈의 바이트, 빌드만 본다. Lean의 공리 목록, 대소문자만 다른 이름, 루트의 진술은 `extract=True`일 때에만 `package.index_problems`가 읽는다(394행). 그래서 컴파일은 되지만 증명 하나를 `sorry`로 남긴 부분, `native_decide`를 쓴 부분, 다른 부분의 이름과 대소문자만 다른 선언을 더한 부분은 제 검사를 통과한다.

병합(900~901행)은 추출까지 하므로 그 결함을 찾는다. 그 뒤 902~916행은 부분을 하나씩 더해 보며 어느 부분이 원인인지 가리는데, 이때의 검사(907~908행)는 다시 `extract` 없이 빌드만 한다. 빌드는 통과하므로 모든 부분이 다시 병합되고, 917~918행의 전체 검사가 같은 결함으로 다시 실패하며, 920행이 `Stop`을 던져 운전이 종료 코드 2로 멈춘다.

재현 경로는 이렇다. simplify 세션 하나가 `theorem added : ... := by sorry`를 담은 모듈을 돌려준다. `2.3-simplify`는 그 부분을 받아들이고 통과한다. `2.4-merge`는 `the merged library does not pass its check: ... is not proved from the allowed axioms: sorryAx`로 멈춘다. 같은 명령을 다시 주면 `2.4-merge`가 같은 `lib/3-parts`를 읽어 같은 자리에서 다시 멈춘다. `2.6-foldback`도 같다. 받아들인 세션 산출은 `state.json`의 `accepted`에서 다시 읽히므로 같은 부분이 다시 병합된다. 보고의 「What to do」는 세션이 쓴 것만 가리킬 때 손으로 고칠 것이 없다고 말하므로, 운영자가 할 수 있는 일은 `state.json`을 손으로 지우는 것뿐이다.

운영자 문서와 맥락 문서는 제 검사에 실패한 simplification을 버리고 운전을 계속한다고 약속한다. 부분을 하나씩 더해 보는 분기는 병합 검사의 실패를 한 부분에 돌리려고 있는 것인데, 그 분기를 여는 조건(추출을 포함한 검사의 실패)보다 그 분기가 가릴 수 있는 것(빌드의 실패)이 좁다. 틀린 쪽은 코드다. 수리는 그 분기의 검사를 병합 검사와 같은 검사로 맞춘다. 추출이 한 번 더 드는 것은 병합이 실패한 때뿐이다.

이 분기를 지나는 시험이 없어서 지금의 동작도 수리 뒤의 동작도 어떤 시험이 알아채지 못한다. 조각 3이 그 시험을 더한다. 대역 컴파일러는 `sorry`가 든 정리를 경고와 함께 컴파일하고 추출에서 `sorryAx`를 낸다(`runtime/tests/canon_lean.py` 157행, 223~224행). 이 항목은 시험을 돌리지 않고 읽기로만 확인했다.

### 조각 1 — .claude/skills/do-math/runtime/finalize.py 888~889행
원래:
```
        `parts` are (id, files, deleted) in the order they are added. A part that touches a file an
        earlier part touched, or whose addition does not build, is discarded and the fact recorded.
```
대체:
```
        `parts` are (id, files, deleted) in the order they are added. A part that touches a file an
        earlier part touched, or with which the library does not pass that check, is discarded and the
        fact recorded. Each addition is held to the whole check, the extraction included: a part that
        builds and leaves a proof open fails only where Lean's axioms are read.
```

### 조각 2 — .claude/skills/do-math/runtime/finalize.py 907~912행
원래:
```
                found, _ = self.library_ok(f'{label}-{pid}', base=base, replace={**replace, **files},
                                           delete=delete + deleted)
                if found:
                    discarded.append(pid)
                    self.decide(what, f'The part {pid} was discarded: the library does not build with it added. '
                                + found[0][:600])
```
대체:
```
                found, _ = self.library_ok(f'{label}-{pid}', base=base, replace={**replace, **files},
                                           delete=delete + deleted, extract=True, records=records)
                if found:
                    discarded.append(pid)
                    self.decide(what, f'The part {pid} was discarded: the library does not pass its check with it '
                                'added. ' + found[0][:600])
```

### 조각 3 — .claude/skills/do-math/runtime/tests/test_finalize.py 1455~1455행
원래:
```
        self.assertTrue((self.solved / 'README.md').is_file())
```
대체:
```
        self.assertTrue((self.solved / 'README.md').is_file())

    def test_a_part_that_builds_and_leaves_a_proof_open_is_discarded_at_the_merge(self):
        """The part passes its own check, which is the build; only the check of the merged library reads Lean's axioms."""
        left_open = module_text('\n\n'.join([part for part in HELPER_PARTS if part != UNUSED]
                                            + [theorem('added_six', ': oddSum 6 = 36')]))  # the proof ends in `sorry`
        plan = script()
        plan['simplify:core'] = [{'output/lean/Small/Helper.lean': left_open, 'output/report.json': json.dumps(
            {'deleted': [], 'cross': [{'id': 'x1', 'done': True, 'note': ''}], 'notes': ''})}]
        with patch('finalize.Run.arrange', side_effect=paper.Stop('halted for the test')):
            self.assertEqual(self.run_command(plan, config=self.config()), 2, self.said)
        self.assertIn('The run stopped at the step `2.4-arrange`', (self.work / 'report.md').read_text(encoding='utf-8'))
        self.assertEqual(read_json(self.work / 'lib' / '3-parts' / 'parts.json')['accepted'], ['core'])
        self.assertEqual(read_json(self.work / 'lib' / '4-merged' / 'merge.json'), {'merged': [], 'discarded': ['core']})
        self.assertIn('The part core was discarded: the library does not pass its check with it added. Small.added_six is '
                      'not proved from the allowed axioms: sorryAx', self.decisions())
        self.assertNotIn('added_six',
                         (self.work / 'lib' / '4-merged' / 'lean' / 'Small' / 'Helper.lean').read_text(encoding='utf-8'))
```


## R3-40
제목: 기록의 `proves`·`refutes` 주장을 Lean이 확인하지 않았는데도 그 기록이 다시 쓸 목록에 들지 않아 기록 단계의 종료 검사를 통과할 길이 없다

### 위치
`.claude/skills/do-math/runtime/package.py` 477~502행(`record_todo`). 이 목록을 쓰는 자리는 `.claude/skills/do-math/runtime/finalize.py` 1004행이고, 같은 색인으로 주장을 요구하는 종료 검사는 1154~1155행(`package.index_problems`, 그 안의 `canon.check_applied`는 `.claude/skills/do-math/runtime/canon.py` 1131~1142행)이다. 쓰는 세션과 대조하는 세션에게 `why`의 값을 알려 주는 자리는 `.claude/skills/do-math/finalize/records-write.md` 33행과 `.claude/skills/do-math/finalize/records-compare.md` 13행이다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 122행:

```
첫째는 코드의 결함이다. 실제 입력, 상태, 동시 실행, 실패 경로, Windows와 Linux의 프로세스·파일 동작에서 의도한 동작이 깨지는 것이 여기에 든다. 가이드가 약속하지만 코드가 하지 않는 동작, 코드가 하지만 가이드가 말하지 않아 작업 세션이나 운영자의 행동이 어긋나는 동작도 여기에 든다.
```

`.claude/skills/do-math/runtime/package.py` 422~423행(종료 검사가 기록에 요구하는 것):

```
    nothing. With `records` (by name path) the records are due: every element has one, every record
    has an element, and what a record claims to prove or refute Lean confirmed. Without, the same
```

`.skill-workspace/finalize-pipeline/agreement.md` 25행:

```
- Fixing an issue when it is found is fine, even late. Not acceptable: an issue that appears in a later stage and should have been caught in its own stage; an order of work that makes earlier products need updating after later work when a better order would have avoided it.
```

`임시/do-math_검증_20261125-2/동결.md` 179행:

```
- 프로그램이나 다른 지침이 글자 그대로 가리키는 것은 가리키는 쪽과 가리켜지는 쪽을 같은 항목에서 함께 고친다. `runtime/paper.py`의 프롬프트가 이름으로 드는 `reference/paper-method.md`의 절 제목, `runtime/finalize.py`가 부르는 `finalize/`의 파일 이름과 시험이 가진 그 목록, 지침이 세션에게 쓰게 하는 산출 파일의 이름과 JSON의 키와 값, 지침이 이름으로 드는 다른 문서의 절 제목, 지침이 적은 수치와 프로그램의 상수가 그런 것이다(맥락 문서 7.2절의 표). 한쪽만 고쳐 둘이 어긋나게 하는 수리는 위반이다.
```

### 영향
기록 단계(`2.5-records`, `2.6-records`)는 `record_todo`가 고른 기록만 세션에게 다시 쓰게 하고, 끝에서 모든 기록을 색인과 맞댄다. 종료 검사는 머리의 `proves`나 `refutes`가 가리키는 선언이 라이브러리에 있고 그 주장이 색인의 `pairs`에서 확인되었을 것을 요구한다(`canon.py` 1138~1142행). 그런데 `record_todo`가 기록을 고르는 조건은 셋뿐이다. 기록이 없거나, 선언의 원문이 달라졌거나, 본문이 없어진 선언의 이름을 백틱 안에 적은 경우다. 머리의 주장은 보지 않는다. 그래서 주장이 확인되지 않은 기록이 세 조건에 들지 않으면 그 기록은 다시 쓰이지 않고, 종료 검사는 `the records do not pass their check`로 멈춘다. 다시 시작해도 같은 기록이 같은 자리에서 걸린다. 그 기록을 고칠 수 있는 세션이 불리지 않기 때문이다.

읽기로 따라간 경로는 둘이다. 어느 것도 실행해 보지는 않았다.

첫째, 주장의 대상이 take에서 빠진 경우다. 연구는 진술 `T`를 증명 없이 두고 다른 선언 `D`가 `proves: T`로 그것을 증명하는 꼴을 흔히 남긴다. 이 기계의 `sunflower-20261122` 정본에는 그런 머리를 가진 기록이 119건 있다. 루트의 형식 증명은 `sorry`가 든 `T`를 쓸 수 없으므로 `D`를 쓰고, take는 루트에서 닿지 않는 `T`를 지운다. `D`의 기록 본문이 `T`를 백틱으로 적었으면 지금 규칙으로도 목록에 든다(그 119건 가운데 117건이 그렇고, 나머지 둘은 지워지지 않는 루트가 대상이다). 본문이 대상을 백틱으로 적지 않은 기록은 목록에 들지 않고 종료 검사에서 `"proves: T" names no declaration of the canon`으로 걸린다.

둘째, arrange가 주장의 대상 이름을 바꾼 경우다. arrange의 검사는 take 때의 기록으로 짝을 묻는다(`finalize.py` 942행, 958행). 그 기록은 옛 이름을 담고 있으므로 Lean은 그 짝을 확인하지 못한다. 그 뒤 `follow_renames`가 머리를 새 이름으로 고친다(`package.py` 540행). `D`의 원문은 그대로이고 본문의 이름도 새 이름으로 바뀌었으므로 `D`의 기록은 목록에 들지 않는다. 종료 검사는 새 이름의 짝을 색인에서 찾지 못해 `Lean did not confirm that its statement is the statement of ...`로 멈춘다. 이 경로는 본문의 백틱과 무관하다.

수리는 목록의 조건을 종료 검사의 조건과 맞춘다. 머리의 주장이 그 색인에서 확인되지 않은 기록을 목록에 넣고, 까닭을 `why`의 넷째 값으로 알린다. 그 기록을 받은 쓰는 세션이 주장을 그대로 두면 프로그램은 이미 `leave it out`이라고 돌려보낸다(`finalize.py` 1021~1024행). `why`의 값은 두 지침이 세션에게 글자 그대로 알려 주는 것이므로 두 지침을 같은 항목에서 고친다. 지침에서 지우는 글은 없다. 시험 `test_the_list_holds_new_and_changed_elements_and_records_that_name_what_is_gone`의 기존 단언은 바뀌지 않는다. 그 시험의 기록에는 `proves`나 `refutes`가 없기 때문이다.

### 조각 1 — .claude/skills/do-math/runtime/package.py 480~482행
원래:
```
    Those without a record; those whose declaration is not in the base index with the same source;
    and those whose record names, between backticks, a declaration the base index had and the library
    no longer has, by its full name or by its name without the library's first component."""
```
대체:
```
    Those without a record; those whose declaration is not in the base index with the same source;
    those whose record names, between backticks, a declaration the base index had and the library
    no longer has, by its full name or by its name without the library's first component; and those
    whose record claims, under `proves` or `refutes`, what Lean did not confirm when `index` was
    extracted. The check of the records requires every such claim to be confirmed (index_problems),
    and a record is changed only by a session, so a record with such a claim is written again."""
```

### 조각 2 — .claude/skills/do-math/runtime/package.py 488~488행
원래:
```
    todo = []
```
대체:
```
    confirmed = index.get('pairs', {})

    def unconfirmed(name, text):
        try:
            meta = parse_record(text, name)['meta']
        except CanonError:
            return False  # the check of the records reports a record that does not parse
        return any(meta.get(key) and not confirmed.get(f'{kind}|{name}|{meta[key]}')
                   for key, kind in (('proves', 'same'), ('refutes', 'negation')))

    todo = []
```

### 조각 3 — .claude/skills/do-math/runtime/package.py 497~498행
원래:
```
        elif set(BACKTICKED.findall(read_text(path))) & names:
            why = 'names a declaration that is gone'
```
대체:
```
        elif set(BACKTICKED.findall(text := read_text(path))) & names:
            why = 'names a declaration that is gone'
        elif unconfirmed(name, text):
            why = 'claims what Lean did not confirm'
```

### 조각 4 — .claude/skills/do-math/finalize/records-write.md 33~33행
원래:
```
`file` is the declaration's file under `lean/`. `why` is `new` (the declaration has no record), `changed` (its Lean text differs from the one its record was written for) or `names a declaration that is gone` (its record mentions, between backticks, a declaration the library no longer has). `record` is the path of the record as it stands, or `null` when there is none.
```
대체:
```
`file` is the declaration's file under `lean/`. `why` is `new` (the declaration has no record), `changed` (its Lean text differs from the one its record was written for), `names a declaration that is gone` (its record mentions, between backticks, a declaration the library no longer has) or `claims what Lean did not confirm` (the header of its record says, under `proves` or `refutes`, that the declaration states what another declaration states, or the negation of it, and Lean did not confirm this for the library as it now stands, for instance because that other declaration is gone or was renamed; the new record leaves that key out). `record` is the path of the record as it stands, or `null` when there is none.
```

### 조각 5 — .claude/skills/do-math/finalize/records-compare.md 13~13행
원래:
```
- `todo.json`: the declarations whose records you compare, each with its `file` under `lean/` and the path of its `record`. The field `why` says why the record was written: the declaration was `new`, it had `changed`, or its earlier record named a declaration that is gone.
```
대체:
```
- `todo.json`: the declarations whose records you compare, each with its `file` under `lean/` and the path of its `record`. The field `why` says why the record was written: the declaration was `new`, it had `changed`, its earlier record named a declaration that is gone, or its earlier record claimed, under `proves` or `refutes`, what Lean did not confirm for the library as it now stands.
```

### 조각 6 — .claude/skills/do-math/runtime/tests/test_finalize.py 531~531행
원래:
```
        self.assertFalse((records / 'Small' / 'stray.md').exists())
```
대체:
```
        self.assertFalse((records / 'Small' / 'stray.md').exists())
        # A record that claims, under `proves`, what Lean did not confirm for this index is written again: the check
        # of the records requires every such claim to be confirmed, and only a writer can leave the claim out.
        (records / 'Small' / 'twice_zero.md').write_text(
            record_text('Twice the empty sum is zero.', weight='unit', proves='Small.helper_zero'),
            encoding='utf-8', newline='\n')
        listed = lambda: {item['declaration']: item['why'] for item in package.record_todo(now, base, records)}
        self.assertEqual(listed().get('Small.twice_zero'), 'claims what Lean did not confirm')
        now['pairs'] = {'same|Small.twice_zero|Small.helper_zero': True}
        self.assertNotIn('Small.twice_zero', listed())
```


## R3-41
제목: 운전의 브로커가 뜨지 않는 것을 라이브러리의 결함으로 돌려, 고칠 수 없는 세션을 다시 띄우고 부분을 버린다

### 위치
`.claude/skills/do-math/runtime/finalize.py` 424~428행(`Run.build`). 이 반환값을 세션 산출의 결함으로 쓰는 자리는 864~866행(simplify), 958~968행(arrange), 1237~1240행(fold-back), 712~726행(selection의 derivation), 752~775행(take와 restore)이다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 122행:

```
첫째는 코드의 결함이다. 실제 입력, 상태, 동시 실행, 실패 경로, Windows와 Linux의 프로세스·파일 동작에서 의도한 동작이 깨지는 것이 여기에 든다. 가이드가 약속하지만 코드가 하지 않는 동작, 코드가 하지만 가이드가 말하지 않아 작업 세션이나 운영자의 행동이 어긋나는 동작도 여기에 든다.
```

`.claude/skills/do-math/reference/operations.md` 510행:

```
Two kinds of failure are handled differently. A simplification that fails its check, whether one part's, the arrangement or one part's last changes, is discarded: that part of the library keeps the form it had, the run goes on, and `decisions.md` records it. Any other step that cannot meet its check stops the run.
```

`.claude/skills/do-math/finalize/common.md` 49행:

```
No session runs `lean` or `lake` itself. Every compile of the run goes through one service, which starts a compile when the machine has memory for it and keeps what it compiled. In the packaging work that preceded this program, several Lean processes were started at once, the machine ran out of memory, and a compile that had died that way was read as Lean rejecting a proof. With one service this does not happen, and a module is compiled once for given bytes, whoever asks for it.
```

`.claude/skills/do-math/finalize/common.md` 67행:

```
`result` in the place of `wait`, without the timeout, prints the build's record, which names the job of each module; Lean's messages for a module you did not name as a target are in `{{work}}/runner/lean/jobs/<job>/stdout.log` and `stderr.log`. If the command reports that no broker is alive, the program is restarting the service; give the same command again a little later.
```

### 영향
`Run.build`는 브로커가 준비되지 않아 `RuntimeError`가 여섯 번 이어지면 `the Lean broker of the run does not stay alive`라는 문장을 라이브러리의 결함 목록으로 돌려준다. `library_ok`는 그 목록을 그대로 돌려주고, 부르는 쪽은 그것을 세션 산출의 결함으로 다룬다.

재현 경로는 이렇다. 운전 도중 브로커가 다시 뜨지 못한다(메모리 부족, Lean 환경의 고장 따위). simplify의 `read`는 그 문장으로 `Unusable`을 던지고(866행), `Sessions.session`은 같은 일을 맡을 세션을 하나 더 띄우며 까닭으로 그 문장을 준다. 세션은 `lean`도 브로커도 스스로 돌리지 않으므로 고칠 수 없다. 두 번째 세션 뒤 `Stop`이 나오고 `discardable`은 그 부분을 버린다(286행). 부분마다 세션 둘이 헛돌고, `2.3-simplify`는 모든 부분이 버려진 채 통과한 것으로 `state.json`에 적힌다. 그다음 `2.4-merge`의 빌드가 같은 까닭으로 실패해 운전이 멈춘다. 운영자가 브로커를 고치고 같은 명령을 다시 주어도 `2.3-simplify`는 통과한 단계이므로 다시 하지 않는다. 꾸러미는 단순화되지 않은 라이브러리로 만들어지고, `decisions.md`에는 부분들이 브로커 때문에 버려졌다고 남는다. arrange와 fold-back의 부분도 같은 방식으로 버려진다. take에서는 고칠 것이 없는 restore 세션이 둘 뜬 뒤에 멈춘다.

운영자 문서가 버린다고 약속한 것은 제 검사에 실패한 simplification이다. 브로커가 살아 있지 않은 것은 그 부분의 실패가 아니고, 공통 지침은 죽은 컴파일을 Lean의 거절로 읽던 앞선 실패를 이 서비스가 막는다고 세션에게 말한다. 틀린 쪽은 코드다. 수리는 그 경우를 결함 목록으로 돌려주지 않고 `RuntimeError`로 올린다. `Sessions.session`은 그 예외를 산출의 결함으로 잡지 않고(`runtime/paper.py` 3313~3318행), `discardable`은 `Stop`만 잡으며, `step`은 `RuntimeError`를 `Halt`로 바꾼다(205~207행). 그래서 그 단계에서 운전이 종료 코드 2로 멈추고, 버려지는 것이 없으며, 같은 명령이 그 단계부터 이어 간다. 복구 경로를 더하는 수리가 아니다. 이미 있는 「그 밖의 실패는 운전을 멈춘다」는 경로로 보내는 것이다.

Lean이 끝까지 돌지 못한 컴파일(`failed`·`cancelled`이면서 거절이 아닌 경우)을 431~434행이 결함으로 돌려주는 것은 같은 갈래의 문제이나, 그 구별은 이 항목에서 다루지 않았다.

이 분기를 지나는 시험이 없다. 조각 2가 `build`를 직접 불러 브로커 쪽 경계(`canon.start_build`)만 대역으로 두고 단언한다. 그 시험은 `time.sleep`을 그 블록 안에서만 바꾸며, 그 동안 도는 다른 스레드가 없다. 시험은 돌리지 않았다.

### 조각 1 — .claude/skills/do-math/runtime/finalize.py 424~428행
원래:
```
            except RuntimeError as error:  # no broker became ready; it is started again and asked again
                failures += 1
                if failures > 5:
                    return [f'the Lean broker of the run does not stay alive: {error}'], None
                time.sleep(BROKER_SECONDS)
```
대체:
```
            except RuntimeError as error:  # no broker became ready; it is started again and asked again
                failures += 1
                if failures > 5:
                    # This is no fault of the library, so it is not returned as one: no session can repair it, and
                    # no part is discarded for it. The step stops the run, and the same command continues there.
                    raise RuntimeError(f'the Lean broker of the run does not stay alive: {error}')
                time.sleep(BROKER_SECONDS)
```

### 조각 2 — .claude/skills/do-math/runtime/tests/test_finalize.py 1006~1006행
원래:
```
        self.assertEqual((code, made.kwargs['resume'], out.exists()), (7, False, False))
```
대체:
```
        self.assertEqual((code, made.kwargs['resume'], out.exists()), (7, False, False))


class BuildTests(FinalizeCase):
    def test_a_broker_that_does_not_come_up_stops_the_step_and_is_no_fault_of_the_library(self):
        # What `build` returns as faults goes to a session as the faults of its output, and a part is discarded for them.
        run = finalize.Run(self.instance, 'odd', finalize.default_config())
        run.library, run.expect_mb = 'Small', 64
        absent = RuntimeError('No Lean broker became ready')
        with patch('finalize.Run.ensure_broker'), patch('finalize.time.sleep') as slept, \
                patch('canon.start_build', side_effect=absent) as asked, self.assertRaises(RuntimeError) as raised:
            run.build(self.instance / 'canon' / 'lean', False, None, None, None)
        self.assertEqual(str(raised.exception),
                         'the Lean broker of the run does not stay alive: No Lean broker became ready')
        self.assertEqual((asked.call_count, slept.call_count), (6, 5))
```


## R3-47
제목: 운영자 문서는 사용 한도에 걸린 운전이 「기다렸다가 스스로 이어 간다」고만 말하나, 프로그램은 한 세션을 열두 번까지만 다시 띄운다

### 위치
- `.claude/skills/do-math/reference/operations.md` 480행의 마지막 문장.
- `.claude/skills/do-math/runtime/paper.py` 230행(`LIMIT_WAITS`)과 3258~3302행(`Sessions.launch`의 되풀이).

### 기준
동결문 `임시/do-math_검증_20261125-2/동결.md` 128행:

```
그 독자에게 맞지 않는 내용, 같은 사항에 대해 가이드끼리 어긋나는 서술, 코드의 실제 동작과 어긋나는 서술, 더는 없는 것을 말하는 서술, 의도를 정확히 전하지 못하는 서술이 결함이다.
```

프로그램의 동작, `.claude/skills/do-math/runtime/paper.py` 230행:

```
LIMIT_WAITS = 12       # times one session is started again after the account's usage limit
```

같은 파일 3258행과 3297~3302행:

```
        for _ in range(LIMIT_WAITS + 1):
```

```
            if limit is None:
                break
            # The same session is started again when the limit ends.
            if self.stopping.wait(max(0.0, limit.retry_at - time.time())):
                raise Stop('the command was interrupted')
        return folder
```

횟수를 정해 둔 쪽이 승인된 설계라는 근거, `임시/do-math_검증_20261125-2/맥락.md` 293행:

```
that every loop has a fixed number of passes
```

### 영향
운영자 문서는 사용 한도에 걸린 운전이 기다렸다가 스스로 이어 간다고 조건 없이 말하고(480행의 마지막 문장), 운영자는 이 말을 사용자에게 전한다. 프로그램은 한도에 걸린 세션을 한도가 끝날 때 다시 띄우되 열두 번까지만 그렇게 한다. 제공자가 한도의 끝을 알려 주지 않으면 한 번의 기다림은 인스턴스 설정의 `retry_max_seconds`(기본 1,800초)다(`paper.py` 3292~3293행). 열세 번째 실행도 한도에 걸리면 `launch`는 산출이 없는 폴더를 돌려주고, 그 세션은 쓸 수 있는 산출을 남기지 않은 세션으로 다뤄진다. 그 결과 단순화는 버려지고(`finalize.py` 276~287행), 그 밖의 단계는 운전을 세운다.

그래서 한도가 오래가는 계정에서는 운전이 스스로 이어 가지 않고 서거나, 한도 때문에 단순화를 잃는다. 가이드의 문장만 읽은 운영자는 선 운전의 원인을 한도에서 찾지 않는다. 보고는 세션이 쓸 수 있는 산출을 남기지 않았다는 것만 말하기 때문이다. 원인을 알려 주는 것은 `log.json`의 `session` 사건에 있는 `usage_limit_until`인데, 가이드는 이 칸을 말하지 않는다.

어느 쪽이 틀렸는지는 다음으로 가렸다. 되풀이마다 횟수를 정해 두는 것은 사용자가 승인한 요약에 든 선택이므로(맥락 문서 293행) 프로그램의 상한을 그대로 두고, 상한을 말하지 않는 가이드의 문장을 고친다. 대체 문면의 「twelve」는 `LIMIT_WAITS`와 같은 값이다. 이 문장을 그대로 단언하는 시험은 `runtime/tests/`에 없다(「goes on by itself」와 「usage limit」으로 검색해 확인했다).

### 조각 1 — .claude/skills/do-math/reference/operations.md 480~480행
원래:
```
The command stays in the foreground until the run ends, which is far longer than a shell tool waits, so start it as a background process with its output in a file. It launches many sessions, among them several for each part of the library, for each group of records and for each dozen events of the history, and those of the paper. Tell the user beforehand that the run draws on the account's usage accordingly. When the usage limit is reached, the run waits and goes on by itself.
```
대체:
```
The command stays in the foreground until the run ends, which is far longer than a shell tool waits, so start it as a background process with its output in a file. It launches many sessions, among them several for each part of the library, for each group of records and for each dozen events of the history, and those of the paper. Tell the user beforehand that the run draws on the account's usage accordingly. When a session meets the usage limit, the run waits until the reset that the provider named, or for `retry_max_seconds` of the instance's settings when it named none, and starts that session again, twelve times at the most for one session. A session that the limit still stops after that counts as one that left no output the program can use, with what "What the run does" below says of such a session, and a run that stops for it is continued by the same command once the account can launch sessions again. Each `session` event of `log.json` gives under `usage_limit_until` the time until which the run waited for that session, or null.
```


## R3-M3
구성: R3-42 · R3-45

### 위치
`.claude/skills/do-math/runtime/finalize.py` 92~95행(`load_config`의 `authors` 검사). 저자 객체의 값은 문자열이기만 하면 통과한다. 그 값을 읽는 자리는 같은 파일 1616~1620행(`write_paper`가 설정의 저자를 그대로 `title-page.json`에 써서 논문 명령에 넘김)과 `.claude/skills/do-math/runtime/paper.py` 1636~1640행(`read_title_page`가 빈 `address`·`email`에서 멈춤)이다. 운영자에게 설정을 설명하는 `.claude/skills/do-math/reference/operations.md` 472행(설정 표의 `authors` 행)은 빈 값을 쓰면 안 된다는 것을 말하지 않는다.

### 기준
`임시/do-math_검증_20261125-2/동결.md` 122행:

```
첫째는 코드의 결함이다. 실제 입력, 상태, 동시 실행, 실패 경로, Windows와 Linux의 프로세스·파일 동작에서 의도한 동작이 깨지는 것이 여기에 든다. 가이드가 약속하지만 코드가 하지 않는 동작, 코드가 하지만 가이드가 말하지 않아 작업 세션이나 운영자의 행동이 어긋나는 동작도 여기에 든다.
```

`.claude/skills/do-math/reference/operations.md` 458행:

```
Before it creates anything but its work folder, the command checks the following and refuses with exit code 1 when one fails: the instance is an instance of this runtime with a Git repository; `solved/<name>` does not exist yet; the configuration is valid and the licence text is available;
```

같은 파일 478행:

```
The configuration cannot be changed once a run has begun, because a continued run confirms that it is the configuration it started with.
```

`.skill-workspace/finalize-pipeline/agreement.md` 25행:

```
- Fixing an issue when it is found is fine, even late. Not acceptable: an issue that appears in a later stage and should have been caught in its own stage; an order of work that makes earlier products need updating after later work when a better order would have avoided it.
```

값을 읽는 쪽의 규칙, `.claude/skills/do-math/runtime/paper.py` 1636~1640행:

```
    if not isinstance(authors, list) or not all(
            isinstance(author, dict) and is_text(author.get('name'))
            and all(key not in author or is_text(author[key]) for key in ('address', 'email')) for author in authors):
        raise Stop(f'the title page {path} holds {{"authors": [...]}}, an array that may be empty; each author has a '
                   '"name" that is not empty and may have an "address" and an "email", each a text that is not empty')
```

시험에 관한 불변식, 동결문 181행:

```
코드의 동작을 바꾸는 수리는 그 동작을 단언하는 시험의 수리를 같은 항목의 조각으로 함께 낸다. 고친 동작을 알아챌 시험이 없었다면 그 시험을 더한다.
```

### 영향
재현 경로는 이렇다. 운영자가 저자의 이름만 받고 없는 칸을 빈 글로 채워 `{"authors": [{"name": "A. Author", "email": ""}]}`을 설정으로 준다. `load_config`는 값이 문자열인지만 보므로 이 설정을 받아들이고, 운전은 선택부터 동결과 지도까지 모든 단계를 지난다. `4-paper`에서 `write_paper`가 `"email": ""`을 담은 `title-page.json`을 쓰고 논문 명령을 부르면, `read_title_page`가 `Stop`을 내어 운전이 종료 코드 2로 선다.

이 정지는 이어 갈 수 없다. 같은 명령을 다시 주면 같은 자리에서 같은 이유로 선다. 설정을 고치면 시작이 `finalize.py` 463~471행에서 설정이 달라졌다는 이유로 거절한다. 남는 길은 작업 폴더를 지우고 처음부터 다시 도는 것이고, 그때까지의 세션과 컴파일을 모두 잃는다.

가이드는 시작이 설정의 유효성을 검사한다고 약속하고(458행), 시작한 운전의 설정은 바꿀 수 없다고 말한다(478행). 그러므로 뒤 단계가 쓸 수 없는 설정은 시작에서 거절되어야 하고, 틀린 쪽은 시작의 검사다. 논문 명령의 규칙은 `--title-page`를 직접 쓰는 운영자에게도 같은 규칙이므로 그대로 둔다. 수리는 저자의 모든 칸이 비어 있지 않은 글이기를 시작에서 요구하고(조각 2), 그 거절과 사유를 실제 명령 호출로 단언하는 시험을 더하며(조각 3), 설정 표가 운영자에게 없는 칸은 빼라고 알리게 한다(조각 1). 시험은 돌리지 않았다.

### 근거
두 구성 항목은 같은 결함을 같은 재현 경로로 지적하고, 틀린 쪽을 시작의 검사로 판정하는 데서도 일치한다. 어긋난 곳은 거절할 칸의 범위 하나다. R3-42는 저자의 모든 칸에 빈 글을 거절하고, R3-45는 읽는 코드가 있는 `address`·`email`만 거절한다. 사본에서 `orcid`와 `github`를 찾으니 `finalize.py`의 검사(93·95행) 밖에서는 쓰이지 않았다. 그래서 두 칸의 빈 값이 운전을 세우지는 않는다는 R3-45의 사실은 성립한다. 그래도 R3-42의 규칙을 취했다. 빈 ORCID나 빈 GitHub 이름은 아무것도 말하지 않는 값이고, 꾸러미를 낸 적도 없는 입력이다. 모든 칸에 한 규칙을 두면 검사와 거절문과 가이드의 문장이 함께 짧아지고, 뒤에 그 칸을 읽는 코드가 생겨도 같은 결함이 다시 생기지 않는다. 기존의 `text` 함수(90행)를 그대로 쓰므로 공백만 있는 값도 거절된다. 이는 `paper.py`의 `is_text`와 같은 판정이라고 사본에서 확인하지는 않았다.

R3-45가 조각 1에 넣은 두 줄 주석은 버렸다. 값이 비어 있으면 안 된다는 것은 거절문과 가이드가 말하고, 주석은 다른 모듈의 함수 이름에 기대어 낡기 쉽다. R3-45의 조각 3(설정 표의 한 문장)은 취해, 모든 칸의 규칙에 맞게 고쳐 썼다. 동결문 122행의 둘째 문장, 곧 코드가 하지만 가이드가 말하지 않는 동작이 이 문장의 근거다.

기준 인용은 다음을 원문에서 대조했다. 동결문 122·181행, `operations.md` 458·478행, `agreement.md` 25행, `paper.py` 1636~1640행이다. R3-42가 인용한 `operations.md` 519행과 `agreement.md` 36행, R3-45가 인용한 동결문 134행(같은 규칙의 두 구현)과 `맥락.md` 273행은 같은 취지를 되풀이하므로 옮기지 않았다. 시험의 위치는 사본 `test_finalize.py` 1046~1048행에서 확인했다. `refused`가 종료 코드 1, 거절문의 포함, 상태 파일의 부재, 세션 호출의 부재를 단언한다(1040~1044행). `config`는 `tex`와 `parallel`에 덧붙은 키를 받는다(382~383행). 지급 키 밖의 새 결함은 보지 못했다.

### 조각 1 — .claude/skills/do-math/reference/operations.md 472~472행
원래:
```
| `authors` | `[]` | A list of objects with `name` and optionally `address`, `email`, `orcid`, `github`. An empty list means that no author is named anywhere: the paper has no author line and no file of the package names an author. |
```
대체:
```
| `authors` | `[]` | A list of objects with `name` and optionally `address`, `email`, `orcid`, `github`, each a text that is not empty: leave out a field that an author does not have, since the command refuses an empty one. An empty list means that no author is named anywhere: the paper has no author line and no file of the package names an author. |
```

### 조각 2 — .claude/skills/do-math/runtime/finalize.py 92~95행
원래:
```
    if not isinstance(authors, list) or not all(
            isinstance(a, dict) and text(a.get('name')) and not set(a) - {'name', 'address', 'email', 'orcid', 'github'}
            and all(isinstance(value, str) for value in a.values()) for a in authors):
        raise Refusal('"authors" is a list of objects with "name" and optionally "address", "email", "orcid", "github"')
```
대체:
```
    if not isinstance(authors, list) or not all(
            isinstance(a, dict) and text(a.get('name')) and not set(a) - {'name', 'address', 'email', 'orcid', 'github'}
            and all(text(value) for value in a.values()) for a in authors):
        raise Refusal('"authors" is a list of objects with "name" and optionally "address", "email", "orcid", "github", '
                      'each a text that is not empty')
```

### 조각 3 — .claude/skills/do-math/runtime/tests/test_finalize.py 행 1048 뒤
대체:
```
        self.refused('each a text that is not empty', config=self.config(authors=[{'name': 'A. Author', 'email': ''}]))
```


## R3-M4
구성: R3-43 · R3-46

### 위치
`.claude/skills/do-math/runtime/finalize.py` 98~101행(`load_config`의 `human_review` 검사)은 `reviewers`가 목록인지만 보고 원소는 보지 않는다. 그 원소를 쓰는 자리는 `.claude/skills/do-math/runtime/package.py` 1410~1411행(`readme_text`)이고, 원소를 글자열로 이어 붙인다. `.claude/skills/do-math/reference/operations.md` 474행(설정 표의 `human_review` 행)은 `reviewers`의 원소가 어떤 꼴인지 말하지 않는다.

### 기준
동결문 `임시/do-math_검증_20261125-2/동결.md` 122행:

```
첫째는 코드의 결함이다. 실제 입력, 상태, 동시 실행, 실패 경로, Windows와 Linux의 프로세스·파일 동작에서 의도한 동작이 깨지는 것이 여기에 든다. 가이드가 약속하지만 코드가 하지 않는 동작, 코드가 하지만 가이드가 말하지 않아 작업 세션이나 운영자의 행동이 어긋나는 동작도 여기에 든다.
```

가이드가 시작 검사에 맡긴 일, `.claude/skills/do-math/reference/operations.md` 458행:

```
Before it creates anything but its work folder, the command checks the following and refuses with exit code 1 when one fails: the instance is an instance of this runtime with a Git repository; `solved/<name>` does not exist yet; the configuration is valid and the licence text is available;
```

같은 파일 478행:

```
The configuration cannot be changed once a run has begun, because a continued run confirms that it is the configuration it started with.
```

그 값을 쓰는 코드, `.claude/skills/do-math/runtime/package.py` 1410~1411행:

```
             f"Review by a person: {review['status']}"
             + (', by ' + ', '.join(review['reviewers']) if review['reviewers'] else '') + '.'
```

그 실패가 가는 자리, `.claude/skills/do-math/runtime/finalize.py` 208~209행:

```
        except Exception:
            raise Halt(sid, 'the program failed in this step:\n' + traceback.format_exc())
```

사용자의 기준, `.skill-workspace/finalize-pipeline/agreement.md` 25행:

```
- Fixing an issue when it is found is fine, even late. Not acceptable: an issue that appears in a later stage and should have been caught in its own stage; an order of work that makes earlier products need updating after later work when a better order would have avoided it.
```

시험에 관한 불변식, 동결문 181행:

```
코드의 동작을 바꾸는 수리는 그 동작을 단언하는 시험의 수리를 같은 항목의 조각으로 함께 낸다. 고친 동작을 알아챌 시험이 없었다면 그 시험을 더한다.
```

### 영향
설정 표는 `human_review`의 기본값만 보이고 `reviewers`의 원소가 어떤 꼴인지 말하지 않는다. 바로 위 `authors` 행이 객체의 목록이므로, 운영자가 `{"human_review": {"status": "self-assessed", "reviewers": [{"name": "R. Reader"}]}}`처럼 쓰는 것은 자연스러운 입력이다. `load_config`는 목록이라는 것만 확인하고 통과시킨다. 동결도 통과한다. `formalization.yaml`은 목록을 그대로 받아 적고, 동결의 검사는 `review.status`만 보기 때문이다. 논문 단계까지 끝난 뒤 `5-documents`에서 `readme_text`가 `', '.join(review['reviewers'])`를 실행하면 `TypeError`가 나고, `Run.step`이 그것을 프로그램의 실패로 적는 `Halt`로 바꾸어 운전이 선다.

이 정지는 이어 갈 수 없다. 다시 시작하면 같은 자리에서 실패하고, 설정을 고치면 시작이 설정이 달라졌다고 거절한다(`finalize.py` 463~471행). 작업 폴더를 지우고 논문 단계를 포함한 운전 거의 전부를 다시 돌아야 한다. 보고는 프로그램의 실패라고만 말하므로 운영자는 원인이 자기 설정이라는 것도 알기 어렵다.

틀린 쪽은 시작의 검사다. 가이드는 설정의 유효성을 시작 검사에 맡기고(458행), README가 이름들을 한 문장으로 잇는 것은 그 문장의 뜻에 맞는다. 수리는 시작 검사가 원소마다 비어 있지 않은 글을 요구하고 거절문이 그 꼴을 말하게 한다. 조각 3이 그 거절과 사유를 실제 명령 호출로 단언하고, 조각 1은 표의 행에 `reviewers`의 꼴을 적어 운영자가 처음부터 맞는 설정을 쓰게 한다. 시험은 돌리지 않았다.

### 근거
두 구성 항목은 같은 결함을 같은 재현 경로로 말하며 어긋나지 않는다. 위치·기준은 R3-46의 더 넓은 쪽(가이드 458·478행, 표의 474행, 시험 불변식)을 취하고, R3-43의 `agreement.md` 25행 인용을 더했다. R3-46이 인용한 `맥락.md` 273행은 같은 취지의 `agreement.md` 25행과 겹치므로 옮기지 않았다. R3-43의 「등록소의 양식에서도 원소는 글자열」이라는 말은 이 묶음의 기준 원문에서 확인하지 않았으므로 옮기지 않았다. `finalize.py` 90행의 `text`가 `isinstance(value, str) and bool(value.strip())`인 것을 사본에서 확인했다.

코드 조각은 R3-46의 구간(98~101행 전체)이 지급 키이므로 그 구간을 다시 쓰되, 주석 한 줄로 원소가 이름의 글인 이유를 남긴 R3-46의 꼴과, 괄호로 꼴을 밝혀 쉼표 나열과 섞이지 않는 R3-43의 거절문(`"reviewers" (a list of names)`)을 취했다. 시험은 R3-46의 `self-assessed`·`notes` 없는 입력을 취했다. `notes`가 빠져도 다른 검사를 통과하는 입력이라 원소 검사만이 거절의 원인이 되기 때문이다. 시험의 기대 문자열은 거절문의 부분 문자열과 맞춘다. 가이드 조각은 R3-46의 문면을 거절문과 같은 말로 다듬었다.

### 조각 1 — .claude/skills/do-math/reference/operations.md 474~474행
원래:
```
| `human_review` | `{"status": "none", "reviewers": [], "notes": ""}` | What a person reviewed. `none` says that no person reviewed the proof or read the Lean statement against the proposition. The other values of `status` are the registry's words, `self-assessed`, `peer-reviewed` and `author-verified`, or a free text. |
```
대체:
```
| `human_review` | `{"status": "none", "reviewers": [], "notes": ""}` | What a person reviewed. `none` says that no person reviewed the proof or read the Lean statement against the proposition. The other values of `status` are the registry's words, `self-assessed`, `peer-reviewed` and `author-verified`, or a free text. `reviewers` is a list of the names of the people who reviewed, each a nonempty text; the command refuses any other form. |
```

### 조각 2 — .claude/skills/do-math/runtime/finalize.py 98~101행
원래:
```
    review = config['human_review']
    if (not isinstance(review, dict) or set(review) - {'status', 'reviewers', 'notes'} or not text(review.get('status'))
            or not isinstance(review.get('reviewers', []), list) or not isinstance(review.get('notes', ''), str)):
        raise Refusal('"human_review" is an object with "status", "reviewers" and "notes"')
```
대체:
```
    review = config['human_review']
    # The README names the reviewers in one sentence (package.readme_text), so each of them is a name in words.
    if (not isinstance(review, dict) or set(review) - {'status', 'reviewers', 'notes'} or not text(review.get('status'))
            or not isinstance(review.get('reviewers', []), list) or not all(map(text, review.get('reviewers', [])))
            or not isinstance(review.get('notes', ''), str)):
        raise Refusal('"human_review" is an object with "status", "reviewers" (a list of names) and "notes"')
```

### 조각 3 — .claude/skills/do-math/runtime/tests/test_finalize.py 행 1049 뒤
대체:
```
        self.refused('"reviewers" (a list of names)',
                     config=self.config(human_review={'status': 'self-assessed', 'reviewers': [{'name': 'R. Reader'}]}))
```


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

