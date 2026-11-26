# Comparing the records of one group with the Lean

The library in your folder is what the chosen proof rests on, with `{{root}}` as its root and `{{main}}` as its main theorem. The records of the declarations that were new or had changed have just been written by another session. This session compares each of them with the Lean it describes and corrects what differs. You did not write them, and that is the point: an error of understanding tends to pass its author's own check.

## Why every record is compared

The paper is written from the records by sessions that never see the Lean proofs. A numbered statement of the paper says what the record's statement says, a proof in the paper is written from the record's proof, and the reasons the paper gives are those of the record's explanation. A record that states more or less than the Lean, tells a proof the Lean does not have, or carries a remark that is not true puts an error into the paper, and into the package beside the library, where readers take the record for what the declaration says.

In the first packaging of this kind only some groups of records were compared in this way. Wrong remarks were found in the explanations of every group that was looked at, and thirty-eight records had to be corrected later. Here every record that was written is compared, and after this step nothing reads the records against the Lean again. What you pass stands in the published package.

## What you are given

- `todo.json`: the declarations whose records you compare, each with its `file` under `lean/` and the path of its `record`. The field `why` says why the record was written: the declaration was `new`, it had `changed`, its earlier record named a declaration that is gone, its earlier record claimed under `proves` or `refutes` what Lean did not confirm for the library as it now stands, or a comparison of the paper's draft with the library found that its statement in words said something the Lean statement does not, which the entry then gives under `disagreement`.

```json
[{"declaration": "Lib.count_le", "file": "Lib/Count/Basic.lean", "why": "changed", "record": "records/Lib/count_le.md"}]
```

- `records/`: all records, those of your list in the form their writer left them.
- `lean/`: the whole library.
- `records-format.md`: the form of a record, which a program checks, and the criteria for the weight. It was written for the sessions of the research and also covers texts that this run does not write; read its sections "The record" and "Weight: units and steps" in full first.

You write no Lean and compile nothing.

## What to compare, for every record of the list

Read the declaration in its Lean file, statement and proof, with the private declarations the proof uses. Then read the record against it.

- **The statement.** Does `## Statement` say exactly what the Lean statement says: every hypothesis, every range and its end points, every quantifier and its order, every constant digit for digit, strict against non-strict? Where the record restates a convention of the proof assistant in ordinary terms, such as subtraction of natural numbers, a cast, or an index that starts at zero, is the restatement equivalent under the hypotheses that are there? Check the boundary cases one by one. A true assertion that the Lean statement does not make does not belong in `## Statement` either: a sentence such as "for $R = 0$ both sides are $0$", or the value of a quantity at a boundary row, is true and was passed by comparers for that reason, and the paper then copied it into a numbered statement that Lean had not proved in that form; move such a sentence to `## Explanation`, or take it out. `## Description` is held to the same standard, since lists show it alone.
- **The proof.** Does `## Proof` follow the Lean proof: the same case distinction, the same lemmas at the same places, the same route? Is every public declaration it names one that the Lean proof uses, with the contribution it is said to make? Is the content of every private lemma the proof uses told, with its argument, and told correctly? Is there a step in the record that the Lean does not have, or a step of the Lean that the record passes over where the argument could fail? For a statement established by evaluating a finite check: do the ranges, the counts, the arithmetic and the statement that turns the result into the mathematical fact agree with the Lean definitions of the check?
- **The explanation.** Is every factual remark true: what the declaration is used for and by which declaration, where a hypothesis is needed, how much room a constant leaves, what would fail without a condition, how the statement relates to another? Check each remark on the Lean. A remark that you cannot check, because nothing in the library settles it, does not stay in the record as a fact.
- **What the record says of its use.** A record may say which declaration uses this one and for what, and you check that on the Lean like every other remark. It may not say how often other declarations use this one, nor that the uses it names are all there are: "its one use is", "used only in the proof of", "it is used twice", "nothing else uses it", "nothing uses it", "the library uses it only for". This holds in every part of the record. Such a sentence is a fault of the record also when it is true today. It speaks of the rest of the library and not of the declaration, and it turns false when a declaration elsewhere is added, removed or taken up for another purpose, as when the library is reused for a second proof. Reword the sentence so that it names the use and says what the declaration contributes there, which you read in the Lean, without the count and without the claim that there is no other use. To name two uses is not to say that there are only two. Where nothing would remain, as with a sentence that says only that nothing uses the declaration, take it out. What the declaration's own proof uses is another matter and no fault: a sentence that says where a hypothesis is needed in that proof, where a numerical constant enters it, or that it applies a lemma at two places states a fact of that proof, which you check on the Lean.
- **The header and the form.** The weight against the criteria of `records-format.md`; a `short` name that says what the thing is; every symbol defined or referred to a record that defines it; every declaration named between backticks one that the library has; no Lean name of a private declaration.
- **One proof, presented by itself.** No sentence about the research, its sessions or reviews, another proof, or this run, as the common text requires.

Compare every record of your list, also after you have found something in one of them. If you set out to raise a point and find on checking that the record was right, drop the point.

## What to do with a difference

You correct it. No session comes after you to act on a report, so a difference you describe and leave is a difference that is published.

Where the Lean settles a matter of fact, such as a wrong constant, range or index, a strict sign written as non-strict, or a declaration named that is not the one used, change the words or the formula. Where the difference is larger, such as a proof told by another route than the Lean's, the argument of a private lemma missing, or an explanation that rests on a wrong idea of what the statement is for, write that part again from the Lean. Where a remark of the explanation cannot be borne out, take it out. A corrected record is held to everything a written record is held to: the form of `records-format.md`, notation that agrees with the records around it, and readability for someone who has that record alone.

## What you write

- `output/verdicts.json`, with one entry for each entry of `todo.json`, in this form:

```json
[{"declaration": "Lib.count_le", "verdict": "agrees", "difference": ""}]
```

`verdict` is `agrees` when you compared the record and it says what the Lean says, and `corrected` when you changed it. `difference` is empty for `agrees`; for `corrected` it says what the record said, what the Lean has, and where in the Lean that is seen.

- `output/records/<path>.md` for each record whose verdict is `corrected`: the complete corrected record, at the path `todo.json` gives under `record`.

The program requires a verdict for every listed record and requires every record to parse. Check the corrected records with the parser:

```text
"{{python}}" -c "import sys, pathlib; sys.path.insert(0, sys.argv[1]); import canon; [canon.parse_record(pathlib.Path(p).read_text(encoding='utf-8'), p) for p in sys.argv[2:]]; print('all parse')" "{{skill}}/runtime" <record.md>...
```

A verdict of `agrees` says that you read the declaration's Lean proof and the whole record. The form has no third verdict for a record you could not compare, or could compare only in part. Do not give such a record `agrees` to fill the list. Give it `corrected`, return it with whatever you did correct, and say in `difference` which part you did not compare and why.
