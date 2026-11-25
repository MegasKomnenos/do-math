# Writing the records of one group of declarations

Every public declaration of the library has a record: a text that gives its statement in ordinary mathematical language, an explanation, and its proof in words. The library in your folder is what the chosen proof rests on, with `{{root}}` as its root and `{{main}}` as its main theorem, and it has been changed since its records were last written: simplified, rearranged, or extended. Some declarations are new, some were changed, and some records name declarations that no longer exist. This session writes the records of one group of such declarations. Other sessions write the other groups at the same time.

## What the records are used for

The records are published in the package beside the library, for readers who want the mathematics without reading Lean. And the paper is written from them, by sessions that receive for each declaration its Lean statement and its record and nothing else of the library. Three consequences shape the work.

- For the mathematics of your declarations, your records are the paper's only source. A private declaration has no record and is invisible to the paper's writers, so what it contributes has to be told inside the record of the public declaration whose proof uses it.
- A record whose weight is `unit` becomes a numbered statement of the paper, with a proof written from the record's proof. A record whose weight is `step` is absorbed into the proof of the statement that uses it, again from what its record says.
- Each numbered statement of the paper has to say exactly what its declaration says, and that is checked against the Lean statement. A record whose statement is looser or stronger than the Lean statement therefore leads to a paper that has to be corrected.

## Why the records are written now, and from the Lean

In the first packaging of this kind the records were written after the library had been declared finished, and only some groups of them were then compared with the Lean. Thirty-eight records had to be corrected later. Here the records are written while the library can still change, each is compared with the Lean by a session that did not write it, and all of this ends before the library is frozen.

A record is written from the Lean, not from the old record. Where a declaration had a record before, `todo.json` gives its path, and that record is worth reading for what the Lean does not show: what an argument is for, why a definition has its form. But it describes the declaration as the research left it. The statement may since have lost a hypothesis, the proof may go another way, and the names it mentions may be gone. What the Lean says is what was proved; where the old record and the Lean differ, the Lean is right. An old record may also speak of the research, of its sessions and reviews, or of another proof. None of that enters the new record; the common text gives the rule.

## You are also the library's first careful reader

To write the proof of a declaration in words you have to follow its Lean proof step by step, and nobody has read the simplified library that closely before you. In both earlier packagings the record writers were the ones who noticed what was wrong in the library itself: a hypothesis stronger than the proof needs, or never used; a conclusion that nothing uses; a comment that uses a symbol it does not define. Those findings came after the library had been declared finished, and it had to be opened again. Here they are asked for. What you notice is returned in `findings.json`, and it is repaired in the library in the step after this one, before the freeze.

Do not repair the library yourself, and do not bend a record around a finding. The record says what the Lean says now. If the declaration is changed afterwards, its record is written again.

## What you are given

- `todo.json`: the declarations whose records you write, in this form.

```json
[{"declaration": "Lib.count_le", "file": "Lib/Count/Basic.lean", "why": "changed", "record": "records/Lib/count_le.md"}]
```

`file` is the declaration's file under `lean/`. `why` is `new` (the declaration has no record), `changed` (its Lean text differs from the one its record was written for) or `names a declaration that is gone` (its record mentions, between backticks, a declaration the library no longer has). `record` is the path of the record as it stands, or `null` when there is none.

- `lean/`: the whole library. Read in full the modules of your declarations, proofs included, with their private declarations.
- `records/`: all records as they stand. Some belong to declarations on a list like yours and are being rewritten by another session; for those, trust the Lean statement and not the record.
- `bibliography.bib`: the sources the records may cite, by key.
- `records-format.md`: the form of a record, which a program checks, and the criteria for the weight. It was written for the sessions of the research and also covers texts that this run does not write; its sections "The record" and "Weight: units and steps" are yours. Read those in full before you write.
- `user-writing-preferences.md`: how the user prefers to be written for. Read it in full. It asks not to be reduced to rules; read it for what it is after.

## Writing a record

Write one file for each entry of `todo.json`, whatever its `why`.

**The header.** `weight` follows the criteria of `records-format.md`. Where the old record gives a weight, keep it unless the declaration's role in the proof has changed. `short` is a name of a few words in ordinary mathematical language; the dependency map prints it and the paper's writers start from it. Keep `proves` or `refutes` from the old record where the declaration still is what that key says. Keep `source` and the part `## Literature` as the old record has them: a separate session checks every cited source, and you add no source of your own.

**`## Description`.** One or two lines that say what the declaration states or defines, understandable without the rest of the record. Lists of many declarations show this part alone.

**`## Statement`.** The statement in ordinary mathematical language and notation, complete: every hypothesis, every range with its end points, every quantifier, strict where the Lean is strict. For a definition, the definition. It says exactly what the Lean statement says. Where the Lean form uses a convention of the proof assistant, such as subtraction of natural numbers that stops at zero, division that is defined at zero, a cast, or an index that starts at zero, state the mathematics in the ordinary convention where that changes nothing and put the correspondence into the explanation. Where carrying the convention over would change what is said, keep the Lean form's convention and say so.

**`## Explanation`.** What belongs to this object: what the statement says about it, why it can be expected to hold, why a definition has the form it has, and how the Lean form reads against the mathematical one. The paper's writers find here the reasons that a proof alone does not give.

**`## Proof`**, for a theorem. The proof in words, as the Lean proof goes, complete enough that a mathematician can check it from this record and the statements of the declarations it names. Name each public declaration the argument uses by its Lean name between backticks and say what it contributes at that point. Tell the content of each private lemma in the place where it is used, in mathematical language and without its Lean name, with its argument. Where a step is a routine calculation, say what is calculated and that it is routine; where a step is the one at which the argument could fail, give it the room it needs. Where a statement is established by Lean evaluating a finite check, the proof is the account of that computation: what is computed, over which range, in which arithmetic, and which statement turns the result into the mathematical fact.

Write formulas in LaTeX between dollar signs. Use the notation of the records that already stand, above all of the records of the definitions, so that the records of all groups read as one. A record is read by itself and out of order: it defines every symbol it uses or points by name to the record that does. Length follows content. A step that records the positivity of a quantity needs a few lines in all, while a result on which the argument turns needs its proof told properly. Text that repeats in one record what another record says costs the paper's writers attention; name the other record.

Do not write a proof you have not followed in the Lean. Where you cannot follow a step, tell the proof up to there, say plainly in the record which step is established by which tactic or lemma in the Lean without an account in words, and report the declaration in `findings.json` with the kind `other`.

## What you write

- `output/records/<path>.md` for every entry of `todo.json`. Where `record` is not `null`, the path is the one it gives. Otherwise it follows the declaration's name, with a folder for each component but the last: the record of `Lib.Count.count_le` is `records/Lib/Count/count_le.md`. A component that Windows cannot hold as a file name is encoded: a reserved device name such as `Aux` gets a trailing `%`, and a forbidden character becomes `%` followed by its two-digit hexadecimal code.
- `output/findings.json`, in this form:

```json
[{"declaration": "Lib.count_le", "kind": "hypothesis", "detail": "..."}]
```

`kind` is `hypothesis` (a hypothesis stronger than the proof needs, or one no proof uses), `conclusion` (a conclusion, or a whole declaration, that nothing uses), `comment` (a comment that uses a symbol it does not define, misstates its declaration, or speaks of something other than the mathematics) or `other`. `detail` says what you saw and where, exactly enough that a session with the library and this line can act on it: which hypothesis, at which step the proof would go through without it, what the weaker form would be. Report what you verified in the Lean. An empty array says that you read every declaration of your list and found nothing.

The program accepts a record only if it parses, and you can run the same check on the files you wrote:

```text
"{{python}}" -c "import sys, pathlib; sys.path.insert(0, sys.argv[1]); import canon; [canon.parse_record(pathlib.Path(p).read_text(encoding='utf-8'), p) for p in sys.argv[2:]]; print('all parse')" "{{skill}}/runtime" <record.md>...
```

Before you end, run it over all your files, see that the files you wrote are exactly the entries of `todo.json`, and that every source key your records cite is in `bibliography.bib`. Then read each record once from its description, as a reader who has that record alone.
