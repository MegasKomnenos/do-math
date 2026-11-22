# Writing review's assessment

Your review leaves two connected outputs. The feedback document explains the examination and its mathematical grounds for later readers. `output/assessment.json` states the judgments the runner applies: a verdict for each element, what the work contributed, the fate of proposed questions, and any concerns and findings. The structured assessment should point into the explanation, so that each recorded judgment can be understood in its actual scope.

Write both outputs in your own directory. The candidate you assess and the canon remain unchanged. The sections below explain the assessment of a candidate, the verdict for each element, the evidence for a proof that is complete in Lean, what an exclusion may not contain, and concerns and findings about what is already published. A comprehensive review uses concerns and findings without assessing a candidate.

## The assessment of a candidate

The assessment has this form. The values are placeholders.

```json
{
  "publish": true,
  "reason": "...",
  "contribution": "...",
  "feedback": "feedback.md",
  "elements": [
    {"element": "<declaration name>", "correct": "confirmed", "accepted": false,
     "replaces": true, "reason": "..."}
  ],
  "questions": [{"proposal": "<proposal ID>", "verdict": "admitted", "reason": "..."}],
  "resolutions": [{"proposal": "<proposal ID>", "resolved": true, "reason": "..."}],
  "concerns": [],
  "findings": [],
  "formal_check": {"build": "<build ID that commands.verify reported>"}
}
```

| Field | Content |
|---|---|
| `publish` | Boolean: whether the candidate enters the canon. |
| `reason` | The reason for publication or exclusion. |
| `contribution` | What this work contributed to the research. Required, and described below. |
| `feedback` | The path of the full feedback document, relative to your `output/`. |
| `elements` | Exactly one entry for each element the candidate adds or whose proof it replaces. |
| `questions` | Exactly one entry for each question the candidate proposes. Omit the field or use an empty array when it proposes none. |
| `resolutions` | Exactly one entry for each resolution the candidate proposes. Omit the field or use an empty array when it proposes none. |
| `concerns` | New concerns about elements, or an empty array. |
| `findings` | Findings on published elements or existing concerns, or an empty array. |
| `formal_check` | Required when you confirm a proof that is complete in Lean. |

The feedback covers the important mathematical assertions of the candidate, including what its records say in prose, and not only the fields above. Explain missing source content, defects, restrictions, checks you did not perform and valuable work. The structured judgment does not limit the mathematical scope of review to what the peer happened to state as elements.

## One entry for each element

The elements you judge are those the candidate adds and those whose proof it replaces. The candidate's `prepared.json` names them in its lists `added` and `replaced`, and `commands.verify` prints the same two lists when you build the candidate yourself. The transport check compares your entries with the lists in `prepared.json` and refuses an assessment that omits a name, repeats one or adds another. Under `entries`, `prepared.json` also says of each of these elements what kind of declaration it is, whether its Lean proof is complete or ends in `sorry`, and whether its record carries a written proof. [A candidate change](change-format.md) describes the candidate and that file.

Each entry has the element's name and four judgments.

**`correct`** is your judgment of the proof.

| Value | Meaning | Standing of the element after publication |
|---|---|---|
| `confirmed` | You examined the proof and found it correct. | accepted, or correct, held back, according to `accepted` |
| `not_confirmed` | You found a gap or an error. | proof not confirmed |
| `undetermined` | You could not complete the judgment. | proof not confirmed |
| `not_applicable` | The element has no proof to judge: it is a definition, or a statement without a proof. | none for a definition; no proof for a statement |

An element has a proof when it is a theorem whose Lean proof is complete or whose record has a nonempty `## Proof`. The transport check holds you to this: an element with a proof needs one of the first three values, and an element without one needs `not_applicable`.

**`accepted`** is Boolean and is your second judgment, made only of a proof you confirmed. It can be true only with `confirmed`. A proof you found correct stays `accepted: false` when the answer to either of the two questions in your role guide is yes: the proof can still clearly be made simpler, or it closes part of the statement by large computation carried out without an understanding of why that part holds. Each question can be turned off for an instance; `settings.acceptance` in your `input.json` says which apply. The element is then published as correct and held back. Other proofs can use it, it stays among the work that remains, and nothing is settled through it. For a definition and for a statement without a proof, `accepted` is false.

**`replaces`** is required, as a Boolean, for each element in the `replaced` list whose declaration already has a proof in the canon. The canon has a declaration under that name with a proof, and the candidate brings a new proof for it. `replaces` says whether the new proof takes the place of the proof the canon has.

- With `true`, the runner puts the candidate's declaration text and record in place, and your `correct` and `accepted` become the verdict of the element.
- With `false`, the runner leaves the declaration and its record as the canon has them, and the element keeps the verdict of the proof it has. What the candidate tried stays among the approaches tried on that statement. When the candidate carries an approach entry for the statement, that entry is published. When it carries none, the runner writes one from the candidate's title and description, the written proof that was offered, and your `reason` for this element, which becomes the entry's account of where the approach stops. Write that reason so that a session reading it there, without your feedback, learns why the proof did not take the place of the old one.

The cases are these. A new proof that is correct and accepted replaces the old one. A new proof that is correct and an improvement on the old one in the sense of the two questions, while room remains, also replaces it, and stays held back with a reason that fits the new proof. A new proof that is wrong, or no better than the one the canon has, replaces nothing. When the canon's declaration has no proof at all, there is nothing to keep in its place: the candidate's proof is the first, and it enters with your verdict whatever that verdict is. `replaces` is not asked for such an element: omit it or write `true`. The transport check rejects `false` there, since a first proof that did not enter would leave no trace of the work in the element.

A proof that enters as a separate declaration, marked in its record as another proof of an existing statement, is among the added elements. It receives a verdict like any other, and `replaces` is not written for it: the transport check rejects the field on an added element, because nothing in the canon would be replaced. The statement then has both proofs, each with its own standing, and a proof you find correct and no better than the one the canon has is published beside it with that judgment in its reason.

**`reason`** is required and is read by the sessions that come after you. The view of the element shows it in full beside the verdict, and the frontier shows the beginning of it, about the first 160 characters, on the line of an element whose proof is not confirmed or is held back. Begin it with what a session choosing its work needs.

- For a proof you did not confirm, say where the gap or the error is: the step, and the case in which it fails.
- For a proof you confirmed and held back, say what your check found, and then either where the proof can be simplified and how, or which part of the statement is closed by which computation. A reader of the frontier can then tell that the proof was not found defective, and where work on it begins.
- For a proof that divides its statement into pieces that are themselves left open, the reason also carries your judgment of the division: whether the pieces are worth pursuing, and whether the division follows the mathematics or only restates the difficulty at a boundary where an earlier computation stopped. This judgment informs the attempt that reads it. It admits and blocks nothing.
- For a definition, say whether it denotes the intended object and whether the canon or the imported library already has it. For a statement without a proof, say whether the Lean statement says what its record says, and what settling it would be worth.
- For a replaced proof, say why the new proof does or does not take the place of the old one.

You do not write whether an element is settled or formal. The runner computes both from your verdicts, from what each proof names in Lean and from the axioms it depends on.

## What the work contributed

`contribution` is your assessment of what this work contributed to the research: what it closed, what it let the research see that it could not see before, how it changed the approach, or that it left what is known unchanged; and whether it repeated a kind of work already done on the same statement or question. The role guide describes the judgment.

The runner writes this text, with the change's ID and revision, at the end of every approach entry and every understanding text the change carries, and into the log of changes. It stands there because that is where a session choosing its work will read it: an attempt reading the approaches tried on a statement learns from it whether another round of the same kind is likely to help. The same text goes to each of those places, so when the change touches several statements or a statement and a question, name what each part of your assessment refers to.

## Questions and resolutions

An entry of `questions` has `proposal`, the ID of the proposed question, `verdict` and `reason`. The verdict is `admitted`, `declined` or `revise`. A declined duplicate also names the existing question in `duplicate_of`; that field is allowed only with `declined`. `declined` and `revise` record two different judgments behind a refusal, which later peers read differently; the role guide explains when each applies and what its reason says.

An entry of `resolutions` has `proposal`, the ID of the proposed resolution, `resolved` as a Boolean, and `reason`. A candidate that proposes a resolution carries the text that is to settle the question, as the question's understanding so far. An accepted resolution says in its reason why that text settles what the question asks and not only part of it. The assertions the text relies on are elements, so their verdicts, in this assessment or already in the canon, are part of what you weigh. Question `q0` is not resolved in this way.

## Evidence for a proof that is complete in Lean

`commands.verify` applies the frozen candidate to a copy of the canon as it is now, compiles the modules the candidate changes afresh in your own session, and reports whether the build succeeded, the build's ID, and for each added or replaced statement the axioms its proof depends on through everything of the canon it uses. [Tools](tools.md) describes the command. For a candidate that touches Lean, this is how you see that it builds on the current canon, that every element a proof names exists and fits, and what each proof depends on.

When you give `confirmed` to an element whose proof is complete in Lean, add

```json
"formal_check": {"build": "<the build ID of your last successful commands.verify>"}
```

The transport check confirms that this is a finished build of your own session, that every module compiled, that the modules the candidate changes were compiled by you and not taken from the cache, and that it is the build your last `commands.verify` recorded as successful. Run the command again after a failure before you rely on it, since only the last run counts. The runner keeps the outcome of that run with the published assessment.

The check does not read the axioms; that is your judgment. Compare the axioms printed for each statement with the allowed axioms in `settings.lean.allowed_axioms` of your `input.json`. A proof is formal only when its axioms lie within that list. `sorryAx` in the list of a proof that is itself complete in Lean means that the proof rests, directly or through other elements, on an element whose own Lean proof ends in `sorry`; the proof is then correct as far as Lean has checked it and not yet formal, which is an ordinary state. Any other axiom outside the allowed list means the proof depends on something this instance does not allow, and your reason should name it.

A compile that Lean accepted establishes the proof of the statement as written. Whether the statement says what its record says, and whether the proof in the record is the same argument as the Lean proof, are judgments the role guide asks of you. If the compile cannot be completed, do not confirm a proof on the strength of its Lean text; use `undetermined` and say what prevented the check. If the source fails to compile, say what the specific defect is, and do not treat every kind of failed check as a false mathematical statement.

## Excluding a candidate

Review judges and does not gate. An element whose proof you did not confirm enters the canon in that state, with your reason, and a later session does the repair; a held proof is published and usable. Useful diagnostic mathematics is therefore grounds to publish with the verdicts it deserves, and `publish: false` is for a candidate with nothing worth keeping.

If `publish` is false, nothing of the candidate enters the canon. The assessment may then admit no question, accept no resolution, and report no concern and no finding, because an excluded candidate cannot change shared state; the transport check rejects an exclusion that contains any of these. In every other respect an exclusion is checked like any assessment, so it is as complete as one: `reason`, `contribution` and `feedback`; one entry for each element, with `replaces` for each replaced one, although these entries then change nothing; one entry for each proposed question, with the verdict `declined` or `revise`; one entry for each proposed resolution, with `resolved: false`; and `formal_check` if an entry confirms a proof that is complete in Lean. Preserve your grounds in the feedback. The runner retains the completed exclusion as an operational outcome. It finishes the producer's peer and review processing and ends the occupancy its pipeline held: the sections recorded for its producer and peers, including a formalizer's whole element, or the exploration's question.

At publication the runner adds `change.json`, `applied.json`, `provenance.json` and `verify.json` beside your output files. Do not use those names at the top level of your output: the transport check rejects them.

## Concerns and later findings

A **concern** is a reported challenge to the proof of an element. A new concern has `id`, `targets`, `reason` and `evidence`. `id` consists of letters, digits, `_` and `-`, beginning with a letter or a digit, and is unique within your assessment. `targets` is a nonempty list of element names: elements of the canon, or elements this candidate adds. The reason identifies what is questioned, and the evidence tells another researcher how to inspect it. Publication gives the concern the stable ID `<publication ID>/<your id>` and creates comprehensive review work. A concern annotates and changes nothing; only a finding changes a verdict.

A **finding** has `concerns`, the list of existing concern IDs it addresses, which may be empty; `status`, one of `cleared`, `confirmed` and `undetermined`; and `reason`. The status records your judgment on the named concerns and is shown beside them. A status alone leaves every verdict as it was; verdicts change only through the lists below. A concern you raise in the same assessment has no published ID yet and cannot be named in a finding.

| Field | Effect |
|---|---|
| `invalidates` | Element names. The confirmation of each element's current proof is withdrawn: its standing becomes "proof not confirmed", with your reason. |
| `validates` | Element names. The confirmation of each element's current proof is established or restored. Whether the proof is accepted is not changed: a proof that was accepted before its confirmation was withdrawn is accepted again, and one that never was is correct and held back. |
| `reopens` | Question IDs. The resolution of each question is withdrawn and the question is open again. |

The reason shown beside an element's verdict is replaced by your reason when you invalidate. When you validate a proof whose confirmation a finding had withdrawn, the reason it was confirmed with returns, so that a held proof shows again where it can be improved. A proof that was not confirmed before takes your reason, and a proof that stands confirmed keeps its own. In every case the view of the element also shows your finding, with its reason, as a later review.

Write only consequences supported by your examination of the evidence. Withdrawing the confirmation of one proof leaves the verdicts of the elements that use it as they are. What changes for them is computed: no statement is settled through the withdrawn proof any more, although a statement with another settled proof remains settled through that one. If a proof that uses the withdrawn one is itself wrong for that reason, name it in `invalidates` as well. A confirmed defect can withdraw one proof while another proof continues to settle the same statement. The feedback explains the actual uses and what remains unresolved.

When a review that publishes its candidate finds a defect in an element the canon already holds, it can report a concern, or a finding with the consequences it has established. When such a finding withdraws a confirmation without naming an existing concern, the runner opens a concern on those elements, so that a comprehensive review examines the broader consequences. Do not claim that those consequences have all been assessed merely because the original defect was found.

## Comprehensive assessment

A comprehensive assignment has `kind: "comprehensive"` in its `task`, with `concerns`, the concern IDs to examine; `conflicts`, each of the form `<statement>:<change IDs of the opposing judgments>`, for a statement that is contested because both it and its negation carry settled proofs; `requested_elements`, when the operator asked for particular elements to be examined; and `purpose`.

For such an assignment, `assessment.json` contains `feedback`, `findings` and optional `concerns`, in the forms above. `findings` is required and can be an empty array when your examination changes nothing. The assessment has no publication decision, no entries for elements and no `contribution`, because no candidate is assessed. A concern's targets are then elements of the canon. Address the assigned concerns, conflicts and requested elements in the feedback, following the actual uses described in the role guide. The runner publishes this assessment directly under `knowledge/reviews/` and applies its findings: the view of each element they touch shows them as a later review, and the frontier shows the changed standings and the status of each concern. No peer or further review is needed for your judgment to take effect.

Run the transport check on your session directory before finishing. A completed assessment can state uncertainty; an interrupted assessment has not finished the stage. The runner preserves partial work and supplies it, with the original assignment, to a replacement reviewer.
