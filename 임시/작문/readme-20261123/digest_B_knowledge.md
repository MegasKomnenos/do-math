# Digest B: the knowledge of a do-math instance

## What this file is and how to read it

This file is an account of one area of the current do-math implementation, the skill folder `C:\math\.claude\skills\do-math`: what the knowledge of a research instance consists of, how it is read, and what each state of a result does and does not certify. It was written on 2026-11-23 for the author who is rewriting `C:\math\README.md` and `C:\math\docs\do-math\running.md`, and who will check each sentence of the new text against the sources cited here.

Every fact is followed by its source as `path:line`. Paths are abbreviated as follows.

| Written here | Full path |
|---|---|
| `SKILL.md`, `reference/...`, `runtime/...`, `roles/...` | under `C:\math\.claude\skills\do-math\` |
| `design:N` | `C:\math\docs\do-math\lean-canon-design.md`, line N |
| `README:N` | `C:\math\README.md`, line N, in the working tree (the file has uncommitted changes) |

Line numbers of the skill files are those of the working tree on 2026-11-23, which for the skill folder equals commit `36ef7d48` (the only uncommitted files are `CITATION.cff`, `LICENSE`, `README.md` and `THIRD-PARTY-NOTICES.md`).

Three marks qualify a statement. A sentence without a mark restates what the cited lines say. **[inferred]** means that I drew the statement from the cited lines and that no source says it in those words. **[not established]** means that the sources I read do not answer the point. Quotations between double quotation marks are exact, with two conventions: an ellipsis marks an omission, and double quotation marks inside a quoted passage are shown as single ones (this occurs in four passages, quoted from `SKILL.md:12`, `reference/common.md:190`, `reference/common.md:289` and `reference/common.md:43`).

Where the guides and the code say the same thing I usually cite both, the guide first. The design record `lean-canon-design.md` was written before the implementation; where it differs from a guide or from the code, the difference is listed in Part 4 and the guide and code are taken as the current system. Part 4 also lists which files I read in full and which only in part.

---

## Part 1. The current facts

### 1. The directory of an instance

An instance is "one research run, stored in a directory with its own Git repository" (`SKILL.md:10`).

**What `init` creates at the top level.** `init` creates the folders `knowledge/events`, `knowledge/changes`, `knowledge/reviews`, `knowledge/organizations`, `sessions`, `runner`, `control/inputs`, `control/requests` and `canon` (`runtime/runner.py:116-118`). It writes `root.md` (the root file, copied byte for byte, `runtime/runner.py:125`), `settings.json` (the complete configuration with defaults filled in, `runtime/runner.py:126`; `reference/operations.md:218`), `.gitignore` with the three lines `/sessions/`, `/runner/`, `/control/` (`runtime/runner.py:127`), `runner/state.json` (`runtime/runner.py:128-134`) and `instance.json` (`runtime/runner.py:189-191`). `instance.json` holds `schema: 2`, the SHA-256 of the root file, `root` (the full Lean name of the root declaration), `library` (the one top-level module name) and `root_statement_hash` (`runtime/runner.py:189-191`). The first Git commit adds `root.md`, `settings.json`, `instance.json`, `.gitignore`, `knowledge` and `canon` (`runtime/runner.py:193-195`). So the Git repository of an instance tracks the root, the settings, the canon and the published judgments and views, and does not track `sessions/`, `runner/` or `control/` **[inferred from the `.gitignore` and the `git add` line]**.

**`canon/`, the knowledge.** "The canon is the folder `canon/` of the instance directory" (`reference/canon.md:9`). Its layout is given twice, in the guide (`reference/canon.md:11-22`) and in the module docstring (`runtime/canon.py:9-18`):

| Path under `canon/` | Content | Source |
|---|---|---|
| `lean/` | "the module root of the library; every module is under <Library>/". This is where the Lean sources are. | `reference/canon.md:13` |
| `records/<Name>.md` | "the record of a declaration" | `reference/canon.md:14` |
| `approaches/<Name>/<id>.md` | "the approaches tried on a statement whose proof is not accepted" | `reference/canon.md:15` |
| `questions/<question>.md` | "the understanding so far of a question" | `reference/canon.md:16` |
| `evidence/<Name>/...` | "files a record refers to, such as code, data and outputs of a computation" | `reference/canon.md:17` |
| `history/<Name>/...` | "what a replacement left behind" | `reference/canon.md:18` |
| `bibliography.bib` | "the sources of the results taken from the literature" | `reference/canon.md:19` |
| `index.json` | "the structural index" | `reference/canon.md:20` |
| `records.json` | "a summary of the record headers" | `reference/canon.md:21` |

`<Name>` is a path that follows the declaration name: `Parking.Columns.dq_col` has the record `records/Parking/Columns/dq_col.md`; a name component Windows cannot hold as a file name is encoded (`reference/canon.md:24`; `runtime/canon.py:95-105`).

All modules of an instance are under one top-level name, the library, which `instance.json` gives (`reference/canon.md:59`). The operator placed the definitions of the root's objects in one module and the root statement in a module of its own (`reference/canon.md:59`; reason in `reference/operations.md:35`: a later proof of the root has to import modules that import the definitions, and Lean forbids an import cycle).

**`knowledge/`, the derived views and the published judgments.** "`knowledge/` under the instance holds views the runner renders and the published judgments" (`reference/tools.md:17`).

| Path under `knowledge/` | Content | Source |
|---|---|---|
| `frontier.md` | the frontier, then the pending concerns and the questions | `reference/canon.md:26`; `runtime/knowledge.py:647-653` |
| `index.md` | the self-description of every record in the order of the Lean structure, each with its current standing | `reference/canon.md:26`; `runtime/knowledge.py:654-666` |
| `board.md` | the work underway | `reference/tools.md:17`; `runtime/knowledge.py:667-688` |
| `state.json` | "the same state in structured form" | `reference/tools.md:17`; `runtime/knowledge.py:689-694` |
| `events/*.json` | one file per published event, each with a `sequence`, a `kind` and a `folder`; replay reads them in sequence order | `runtime/knowledge.py:205-210`; `runtime/runner.py:616-617` |
| `changes/<id>/` | one published change: `change.json`, `applied.json`, review's `assessment.json` with its feedback, `provenance.json`, `verify.json` | `reference/operations.md:333`; `reference/tools.md:17` |
| `reviews/<id>/` | a comprehensive review's assessment | `reference/operations.md:334` |
| `organizations/<id>/` | an organizer's output | `reference/operations.md:334` |
| `questions/<id>/` | an operator publication of questions | `reference/operations.md:334`; `runtime/runner.py:631-632` |

**The other folders.** `sessions/<session>/` holds, for each session, `work/` (scratch), `output/` (the retained report or role output), `pack.md` (the starting context), `input.json`, the copies of the guides under `context/`, the available CLI conversation, and `inbox/` (`reference/tools.md:11`); `prompt.txt` is written there as well (`runtime/context.py:137-140`). `control/inputs/*.txt` are the standing inputs, read in file-name order (`runtime/context.py:68-69`; written by the `input` command with a time-stamped name, `runtime/runner.py:1629`). `control/requests/` receives operator requests (`runtime/runner.py:1378`, `1658`). `runner/state.json` is the runner's own state (`runtime/runner.py:134`), a different file from `knowledge/state.json`.

**Which files are derived by the runner, and who may write what.** Sessions "read all of these files and write none of them. A session changes the canon only through a candidate, which the runner applies at publication" (`reference/canon.md:28`). "`index.json` and `records.json` are made by machine at each publication" (`reference/canon.md:28`; `runtime/knowledge.py:697-700`, `runtime/runner.py:187-188`). The three views `frontier.md`, `index.md`, `board.md` are rendered by the runner (`reference/canon.md:26`), and `render` also writes `knowledge/state.json` when the computed model differs from the stored one (`runtime/knowledge.py:689-694`). The reason the history is a separate folder: "so that a text search of `records/` or `lean/` returns the canon as it is and not the texts that were replaced" (`reference/canon.md:28`).

### 2. The canon, an element and a record

**Canon.** Three defining sentences exist.

- "The knowledge of an instance is its **canon**: one Lean library with a written record beside each declaration." (`SKILL.md:10`)
- "The mathematics an instance keeps is a library written in Lean, the proof assistant, with a written record beside each declaration of the library. The library together with those records is called the **canon**." (`reference/common.md:7`)
- "The canon is the body of mathematics that the sessions of an instance share. It consists of the instance's Lean library, a written record for each declaration of that library, and a small amount of written state attached to particular statements and questions, described in the next section." (`reference/common.md:101`)

The third sentence is wider than the first two: it includes the approaches tried and the understanding texts (topic 8).

**Element.**

- "Every mathematical assertion the research keeps is an **element**, which is a declaration of that library whose statement Lean has compiled, together with its **record**." (`SKILL.md:10`)
- "An **element** is a declaration of the library together with its record." (`reference/common.md:103`)
- "An element is a declaration that an author wrote in a module of the library, together with its record." (`reference/canon.md:32`)

**What kinds of declaration are elements.** "A definition is an element. A statement is an element too: in Lean it is a `theorem`, whatever the mathematics would call it." (`reference/common.md:103`). "In the views an element has one of four kinds. A `theorem` is a statement, and only statements have a standing. A `def`, an `opaque` and an `inductive` are definitions; a `structure` is shown as an `inductive`, and an `abbrev` or an `instance` as a `def`." (`reference/canon.md:32`). A statement can stand with or without a proof; "a conjecture and an open piece of the root's proof are both of this kind" (`reference/common.md:105`). A result taken from the literature "is an element like any other" (`reference/common.md:107`).

Not elements: "a declaration marked `private`, and everything Lean generates for a declaration an author wrote, such as the fields and the constructor of a structure, the constructors of an inductive type, equation lemmas and auxiliary proofs. What they use counts as used by the element they belong to" (`reference/canon.md:34`; the rule in code: an entry has a source span, a public non-internal name, and a span not inside that of a declaration whose name it extends, `runtime/canon.py:704-710`, `723-730`). An explanation or an interpretation "is not a statement. It is prose, and it is kept in the record of the declaration it is about" (`reference/common.md:91`).

Beyond the elements there is the **imported library**: "Mathlib and the Lean toolchain, which the instance's own library imports. A proof may use anything in the imported library, and it may use the elements. It can use nothing else. A result of this research that is not an element is, for every other proof, a result that does not exist." (`reference/common.md:103`)

The reason the guides give for keeping mathematics as Lean declarations (`reference/common.md:85-87`): only what has a Lean statement is kept as a result and usable by name by a later proof; in the earlier run, where results were kept in prose, each written assertion restated its notation (median 769 characters), and "the same fact stated in two accounts was two assertions, and nothing stood for the fact itself". The user's direction is "You state what you found, and by stating it you keep it. The direction is not that whatever went unstated is dropped." (`reference/common.md:85`)

**Record.** "What Lean must check is in the Lean source: the statement, the proof, and the names of the statements an informal proof rests on. Everything else is in the **record**, a file whose path follows the name of the declaration." (`reference/common.md:107`). `SKILL.md:10`: "The record holds what cannot be in Lean: a self-description of a line or two, the statement in natural language, the explanation, and a proof in words where there is one."

A record is a Markdown file with a header between two `---` lines and parts under second-level headings (`reference/records.md:7`).

| Header key | Content | Source |
|---|---|---|
| `weight` | Required. `unit` or `step`. | `reference/records.md:35`; `runtime/canon.py:187-188` |
| `short` | A short name of a few words; the frontier shows it in place of the self-description, and the dependency map uses it as a label. | `reference/records.md:36` |
| `proves` | The name of a statement of which this declaration is another proof. | `reference/records.md:37` |
| `refutes` | The name of a statement whose negation this declaration states. | `reference/records.md:38` |
| `source` | For a result from the literature, the key of its bibliography entry. | `reference/records.md:39` |

A key outside this list is rejected (`reference/records.md:31`; `runtime/canon.py:32`, `152-155`); a record has `proves` or `refutes`, never both (`reference/records.md:41`; `runtime/canon.py:194-195`).

| Part | Content | Source |
|---|---|---|
| `## Description` | Required. "The **self-description**: what this element is, in one or two lines." | `reference/records.md:47`; `runtime/canon.py:189-190` |
| `## Statement` | The statement in natural language; for a definition, the definition in words. | `reference/records.md:48` |
| `## Explanation` | What belongs to this object: what the statement says about it, why it can be expected to hold, why a definition was chosen in this form, how the Lean form corresponds to the mathematical one. | `reference/records.md:49` |
| `## Proof` | The proof in natural language. | `reference/records.md:50` |
| `## Literature` | For a result taken from the literature: the source, how much of it was read, and where the statement stands in what was read. | `reference/records.md:51` |

Each part occurs at most once, in any order; no other second-level heading and no text before the first heading is allowed (`reference/records.md:43`; `runtime/canon.py:33`, `167-179`). The self-description is "the only part of the record that views of many elements show" (`reference/records.md:53`). The explanation follows a criterion the user gave: "an explanation that is attributed to a mathematical object is kept with that object" (`reference/records.md:57`).

Who writes records: peers and organizers write them into a change, reviewers judge them; a producing session (attempt, explorer, formalizer) "does not write records" (`reference/canon.md:5`). The operator writes the records of the declarations supplied at creation (`reference/operations.md:96-114`).

Review's verdict is not a part of the record file **[inferred: the record's keys and parts are closed lists that contain no verdict, `runtime/canon.py:32-33`; verdicts are read from `knowledge/changes/<id>/assessment.json` at replay, `runtime/knowledge.py:116-124`]**. The view of an element joins the two (`reference/common.md:160`).

### 3. The forms a proof can take

"A **proof** takes one of two forms. It can be complete in Lean. Or it can be written in natural language in the record, while the Lean source carries a proof that names, one by one, the statements the argument rests on and then ends in `sorry`, Lean's marker for a proof that is left open." (`reference/common.md:105`). `SKILL.md:10` says the same and adds: "Lean checks those names in both cases."

In the Lean source a `theorem` therefore has one of three bodies (`reference/canon.md:63-67`):

- no proof: the body `by sorry` (`reference/canon.md:65`);
- an informal proof: each statement the argument uses is named in a line of the plain form `have h := name arguments`, and the proof ends in `sorry`; "The argument itself is the `## Proof` part of the record." (`reference/canon.md:66`);
- a complete proof: "any Lean proof without `sorry`. It may depend only on the axioms the instance allows" (`reference/canon.md:67`).

Which of the first two a `sorry`-ended theorem is, is decided by the record: "A statement counts as having a proof when its Lean proof is complete or when its record has a nonempty `## Proof`. Whatever stands under that heading is therefore offered as the proof, and review judges it as one." (`reference/records.md:55`; code: `runtime/knowledge.py:221-223`).

**What Lean checks in each form.**

- In both forms: that the statement is well formed (it compiles), and the names. "Lean rejects a name that does not exist and a use whose arguments do not fit the named statement, and the names a proof uses can be read from the compiled library by machine. That is how the instance knows, without anyone writing it down, what each statement rests on and what rests on it." (`reference/common.md:105`)
- In an informal proof, Lean checks nothing of the argument itself: the Lean proof ends in `sorry`, and the argument is prose judged by review **[inferred from `reference/canon.md:66` and `reference/common.md:121`]**. Its axiom list contains `sorryAx`: "`sorryAx` means that this proof, or a proof it rests on, ends in `sorry`" (`reference/canon.md:143`).
- In a complete proof, Lean checks the whole proof. A successful compile is still not the criterion: "A compile that succeeds shows that Lean accepts the file as written. It does not yet show that a statement has been proved formally. A proof may end in `sorry`, as the informal proofs of the canon do by design, or it may rest on an axiom the instance has not allowed, and Lean accepts the file in both cases. What decides is the set of axioms the statement depends on." (`reference/lean.md:212`)

Two conventions have stated reasons. The plain `have` form is required because "a wrapper written for the purpose lost the references when Lean simplified the proof term" (`reference/canon.md:66`). Prose is kept out of the Lean source because the broker keys compiled modules by their source, "so prose in a source would cause the module to be compiled again each time the prose changed" (`reference/canon.md:71`).

Writing a complete Lean proof is optional for an attempt or a peer; "A complete Lean proof is required in the end for the root and for what the root rests on, and formalizers are launched for that." (`reference/common.md:95`). The proof in the record and the Lean proof of one element are the same argument; when a formalizer changes the argument, the peer rewrites the proof in the record and review judges whether the two are one argument (`reference/common.md:172`; `reference/writing.md:53`).

Three things are refused in the source: an `axiom` declaration ("what you want to assume is stated as a `theorem` whose proof is left open, and the frontier then shows it as work that remains"), a definition whose body contains `sorry` ("because every statement that used it would be about an unknown object"), and a `theorem` whose statement is not a proposition (`reference/canon.md:69`; `runtime/canon.py:1075-1078`, `1101-1102`).

### 4. The weight of an element

The weight has two values, `unit` and `step` (`reference/records.md:35`; `runtime/canon.py:31`), and is a required header key of every record (`runtime/canon.py:187-188`).

Definitions: "The weight of an element says how it stands in the structure of the mathematics. A **unit** is a result that someone describing how the proof goes would name: it is obtained in one place and handed to another as an input. A **step** is a result that lives inside one proof and exists because that proof was written in pieces." (`reference/records.md:61`). `reference/common.md:107` words it as "whether the element is one of the results a reader of the proof's structure would name, called a unit, or a step inside one proof."

What the weight is used for (`reference/records.md:63`):

- The frontier "passes through a step whose own proof is accepted and shows what that step rests on in its place, so that the view stays at the level of the units". In code a statement is passed through when its weight is `step`, its standing is `accepted`, it has exactly one proof, and it has not already been passed on this path (`runtime/knowledge.py:517-520`). A step that is itself work that remains, or that has several proofs, is shown, with the mark `(step)` (`reference/common.md:201`; `runtime/knowledge.py:557`).
- "The reading commands can restrict a list to units" (`--units`, `reference/canon.md:92`; `runtime/canon_tool.py:178`).
- "The dependency map of the research draws units and folds each step into the connections that pass through it, and the paper that presents the result, which is produced once the root is settled through a formal proof, numbers units and absorbs steps into the proofs that use them."
- "In none of these is a step lost. It remains an element, proofs name it, and a traversal that selects it returns it."

Why the choice matters: "If every lemma is a unit, the picture is the whole dependency graph, and the structure of the proof is buried under hundreds of entries. If only the root and the last derivation of it are units, everything between them is hidden." (`reference/records.md:65`). Four signs point toward a unit (`reference/records.md:69-72`); one of them is that the element is "where the proof's guarantees come from: it is taken from the literature, or its truth rests on a computation", which makes it a unit even when a single proof uses it (`reference/records.md:70`). "The signs are material for a judgment and not conditions." (`reference/records.md:80`)

"The author of the record writes the weight, review judges it, and a later record can correct it when the element's role has become clearer." (`reference/records.md:80`). The weight does not enter the computation of standing or of settledness **[inferred: `runtime/knowledge.py:226-238` and `253-300` do not read it]**.

### 5. The standings of a statement; settled, formal, contested

**Two judgments.** "Review makes two judgments about a proof. The first is whether the proof is correct. The second is made only of a correct proof: whether it is accepted. The second judgment exists because a correct proof is not always the proof the research should stop at." (`reference/common.md:145`)

Two considerations, both from the user, can keep a correct proof from being accepted (`reference/common.md:147`): the proof "can still clearly be made simpler: review can point to a place in it and name the reduction"; or the proof "establishes part of the statement only by large computation carried out without an understanding of why that part holds". The reason given for the second: "A statement with an accepted proof appears finished, and no session would then go on to explain why it is true." Each consideration can be turned off by a setting (`reference/common.md:147`; the settings are `acceptance.decline_reducible_proofs` and `acceptance.decline_uncomprehended_computation`, both true by default, `reference/operations.md:261`).

**The four standings** (`reference/common.md:149-156`; names in code `runtime/knowledge.py:18-19`):

| Standing | Meaning (quoted) | Work remains |
|---|---|---|
| no proof | "The statement has neither a complete Lean proof nor a proof written in its record." | Yes |
| proof not confirmed | "A proof was offered, and review found a gap in it, could not complete its judgment, or has not judged it." | Yes |
| correct, held back | "Review confirmed the proof and did not accept it, and gave the reason." | Yes |
| accepted | "The proof is correct and accepted." | No |

"This state is the **standing** of the statement." (`reference/common.md:149`). "The first three states are the **work that remains**." (`reference/common.md:164`; `runtime/knowledge.py:20`). A definition "has no proof and none of the four states" (`reference/common.md:160`).

How the standing is computed (`runtime/knowledge.py:226-238`): not a theorem → none; no proof → `no_proof`; no verdict → `accepted` if the Lean proof is complete, else `not_confirmed`; verdict with `correct` other than `confirmed` → `not_confirmed`; otherwise `accepted` if the verdict's `accepted` is true, else `held`. Review's verdict on correctness takes one of `confirmed`, `not_confirmed`, `undetermined`, `not_applicable` (`runtime/check.py:15`; `reference/canon.md:154`), and `accepted` is a Boolean that can be true only with `confirmed` (`runtime/check.py:266`, `274`).

**Elements without a review.** "The elements the instance began with were supplied with the root and no review has judged them. Among these, a statement whose Lean proof is complete stands as accepted, since Lean has checked that proof, and one that has only a written proof stands as not confirmed until a review judges it. This holds for those first elements alone. A proof that a later change brought and that the review of that change left without a verdict stands as not confirmed, whether or not it is complete in Lean, because no review has read its statement against what was meant." (`reference/common.md:158`; `runtime/knowledge.py:125-132`, `232-235`). A statement an organizer adds enters as accepted with the runner-written reason "Proved in Lean from the allowed axioms; added by the organizer." (`runtime/knowledge.py:173-176`; `SKILL.md:40`).

**Standing belongs to a declaration.** "A proof is carried by a declaration, and the standing is, strictly, that of the declaration." A statement can have further proofs, "each a further declaration with the same statement", each with a standing of its own (`reference/common.md:162`). Which declarations prove the same statement is claimed by the record's `proves` key and confirmed by Lean: the two types must be identical (`runtime/canon.py:646-653`, `1092-1100`; `runtime/knowledge.py:241-250`).

**Settled.**

- "A proof is **settled** when it is accepted and every statement of the canon that it names is settled, and a statement is settled when one of its proofs is." (`reference/common.md:166`)
- "A statement is **settled** when one of its proofs is accepted and every statement that proof names is settled." (`SKILL.md:12`)

Further rules in the same paragraph (`reference/common.md:166`): definitions and declarations of the imported library "have no standing and do not enter this computation"; "Where the proofs of two statements name each other, neither settles the other. So a statement whose own proof is accepted can still be unsettled, because something that proof rests on is not." The code computes the settled set as a least fixed point starting from nothing (`runtime/knowledge.py:289-300`), which is what makes mutually naming proofs settle neither **[inferred from the loop]**.

"A correct proof that is held back has not been judged wrong. The element is published, and other proofs can use it. What it cannot do is make them settled." (`reference/common.md:166`)

"Being settled is a matter of review's judgments. Being **formal** is a matter of Lean." (`reference/common.md:170`)

**Formal.**

- "A statement is formal when its Lean proof is complete and depends, through everything of the canon it uses, only on the axioms the instance allows. Such a proof is called a formal proof; a proof that ends in `sorry`, or that rests on a statement whose proof does, is not one." (`reference/common.md:170`)
- "An element is **formal** when its proof is complete in Lean and depends, through everything of the canon it uses, only on the allowed axioms." (`SKILL.md:12`)
- "A statement of the canon is formal when every axiom it depends on is in the instance's allowed list." (`reference/lean.md:214`)

In code, `formal` of an element is exactly this: the element is a theorem and its axiom closure is a subset of the allowed axioms (`runtime/knowledge.py:268`). The three wordings agree because `sorryAx` can never be in the allowed list (`reference/lean.md:214`) **[the equivalence is inferred]**. The element-level `formal` does not require a review verdict; the statement-level value used for the root's state does: a statement is formally settled when one of its proofs is both settled and formal (`runtime/knowledge.py:325-327`).

**Contested.**

- "a **contested** statement, one for which both it and its negation carry settled proofs" (`SKILL.md:60`)
- "`contested` means that both the root and its negation are settled. Correct proofs cannot reach opposite outcomes for one statement, so a contested statement, whether the root or another, counts as neither open nor finished until a later review locates the failure, and the view names every statement in that condition." (`reference/common.md:209`)

In code, both sides of a contested pair are taken out of what any proof can rest on and the settled set is computed again (`runtime/knowledge.py:302-321`); neither side counts as settled (`runtime/knowledge.py:325`). Which declaration states the negation is claimed by the record's `refutes` key and confirmed by Lean as `Not` applied to the other statement (`runtime/canon.py:652`).

**Refuted.** "When a settled proof establishes a statement that Lean has confirmed to be the negation of another, that other statement is **refuted**. Its line says by which element, nothing beneath it is shown, and no work on it remains. A proof that names a refuted statement cannot become settled as it stands, so the line of the statement that proof belongs to says so, and that statement is work that remains whatever the standing of the proof: it needs another proof." (`reference/common.md:205`; `runtime/knowledge.py:309-332`)

**The root's state** (`reference/common.md:209`; `runtime/knowledge.py:345-358`): `unresolved`, `informal_proved`, `formal_proved`, `informal_refuted`, `formal_refuted`, `contested`. `informal_proved` "means that the root is settled and not yet through a formal proof"; the operator's table adds the cause: "somewhere in what it rests on, a proof is still written in a record and not complete in Lean, or depends on an axiom that is not allowed" (`reference/operations.md:353`).

**What each state does and does not certify, for a session that wants to use the statement** (`reference/evidence.md:19-27`):

- no proof: "nothing about it has been established by argument. You may still name it in a proof of your own. Your result then rests on it openly".
- proof not confirmed: review found a gap, could not complete its judgment, or has not judged. "A gap that was found is not a proof that the statement is false".
- correct, held back: "has been confirmed. You can rely on the statement as you would on one whose proof is accepted; the difference is that your own result cannot be settled through it until its proof is accepted."
- accepted: "Whether the statement is settled depends in addition on everything the proof rests on ... A statement whose own proof is accepted and which rests on an open statement is, in effect, established under that open statement as a hypothesis."
- in every state: "what was judged is the proof of the statement as it is written. An accepted proof of a statement about a finite range establishes that finite assertion and no more."

The operator is told to keep these apart when reporting: "A published element, a statement whose proof is correct and held back, a settled statement and a formally settled root mean different things, and a proof written in a record has been judged by review while a proof complete in Lean has also been checked by Lean." (`SKILL.md:62`). And: "Publication preserves useful work with the judgment it needs. It does not certify every element it adds." (`reference/common.md:141`)

**A settled statement's proof.** Once a statement is settled, its lease is refused, so no session takes it on; a further proof enters as a separate declaration. Two replacements remain, under both of which the statement stays settled: a formalizer puts a formal proof in the place of a settled informal one, and the one-line derivation from a superseding statement that has itself become settled (`reference/common.md:168`; machine conditions in `runtime/check.py:110-146`, review's acceptance required at `runtime/check.py:287-290`).

### 6. The frontier, the index and the other derived views

**The frontier.** "The **frontier** is the view of what the root rests on at present and of how much of that is settled. Nobody writes it. It is computed from the canon each time it is shown" (`reference/common.md:188`). `SKILL.md:12`: "The **frontier** is the view derived from the root downward along what each proof names, opening every statement that is not settled. Nobody writes it, and the work that remains is every statement it shows whose standing is not 'accepted', a statement without any proof included."

How it is built (`reference/common.md:188`; `runtime/knowledge.py:472-525`): start at the root and list its proofs; under each proof list the statements of the canon that the proof names; leave out a settled statement; show an unsettled one with its standing and open it in the same way; follow every proof whatever its state; list a statement already shown again without what lies beneath it ("shown above"); pass through an accepted step.

What a line shows (`reference/common.md:201`; `runtime/knowledge.py:550-559`, `530-547`): the name, the mark `(step)` where applicable, the short name or else the self-description, the standing, the beginning of review's reason where the proof is not confirmed or held back (cut at 160 characters, `runtime/knowledge.py:539`), the number of approaches tried, and the number of sessions holding sections on it. A second declaration of the same statement appears as `other proof:`. An example in the exact form is at `reference/common.md:192-199`.

What it does not show: "The frontier shows only what some proof of the root reaches. An open statement that no proof of the root uses yet, such as a conjecture left as a lead, is not in it." (`reference/common.md:207`). At the start of an instance "the frontier is the root alone, in the state 'no proof'" (`reference/common.md:190`).

Nobody admits statements to it: "No rule limits what may be chosen, and no session or reviewer admits a statement to the frontier." (`reference/common.md:211`). The consequence the guide states: "The quality of the frontier therefore depends on how sessions state what they leave open, and on each attempt facing the difficulty that matters" (`reference/common.md:211`). Review's judgment of a division is written in its reason and "admits nothing and blocks nothing" (`reference/common.md:213`).

**`knowledge/frontier.md`.** Rendered by the runner (`reference/canon.md:26`). It holds a first line with the revision, the root declaration and the root's state; the frontier lines; a note naming contested statements; a `## Concerns` list of the concerns not cleared, each with the status of its comprehensive review; and a `# Questions` part with each question's statement, grounds, state, source, resolutions, later reviews and aliases, followed by the question proposals review did not admit (`runtime/knowledge.py:647-653`, `562-576`, `579-615`; `SKILL.md:56`).

**`knowledge/index.md`, the derived index.** "`knowledge/index.md` is the derived index of everything the canon holds, each element with its self-description and standing, including what the root does not rest on." (`SKILL.md:56`). It is grouped by module, modules and elements in name order, one line per element with weight, standing (or kind for a definition) and self-description (`runtime/knowledge.py:654-666`; `reference/operations.md:320`). "Nobody writes a survey of the canon, and none is delivered to you." (`reference/common.md:241`)

**The structural index, `canon/index.json`.** "At each publication the runner, the program that operates the instance, extracts a **structural index** from the compiled library by machine. For each declaration the index holds its name, kind and module, the text of its Lean statement, what the statement uses and what the proof uses, what uses it in turn, whether its Lean proof is complete or ends in `sorry`, and the axioms its proof depends on. Nobody edits the index." (`reference/common.md:113`). It is produced by a generated Lean file that prints one JSON row per constant of the extracted modules (`runtime/canon.py:532-670`) and by `update_index` (`runtime/canon.py:700-818`). An entry stores `name`, `kind`, `module`, `file`, `span`, `source_sha`, `statement`, `statement_hash`, `prop`, `statement_uses`, `uses`, `library`, `direct_axioms`, `lean_proof` (`runtime/canon.py:790-797`). The index also has `revision`, `modules`, `aux`, `hidden`, `judged` and `pairs` (`runtime/canon.py:816-818`).

**`canon/records.json`.** A machine summary of the records so that replay reads one file: weight, short, proves, refutes, source, description, whether there is a `## Proof` and a `## Statement`, the approach identifiers, the path (`runtime/knowledge.py:697-715`). "It holds nothing a record does not." (`runtime/knowledge.py:700`)

**The view of one element.** The reading commands "join the index and the records by name, and return for each element one **view**" (`reference/common.md:113`). Its lines and where each comes from are tabulated at `reference/canon.md:131-152`; code `runtime/canon_tool.py:65-174`. One line not in the guide's table is `judged`, shown when the judge accepted the formal proof at some revision (`runtime/canon_tool.py:107-110`).

**The board, `knowledge/board.md`.** A board exists. "The **board** lists producing sessions and the processing of their work. Each entry identifies the producing session and its role, the elements on which it holds sections or the question it holds, and whether the session is running or its work is with a peer or under review; beneath it stand its sections, each with what it covers." (`reference/common.md:257`). The file's own header says "Saved pipeline state, not process liveness. Sections and questions remain occupied through peer and review." and it ends with the element leases (`runtime/knowledge.py:667-688`). It is derived from the runner's state and the sessions' declarations, not from the canon **[inferred from `runtime/knowledge.py:622` taking `board` and `leases` as arguments and `reference/operations.md:364-366`]**.

**`knowledge/state.json`.** A `state.json` exists in `knowledge/`: "`state.json` the same state in structured form" (`reference/tools.md:17`); "`knowledge/state.json` holds the same derived state in structured form for detailed inspection" (`reference/operations.md:346`). It is the replayed model written as JSON (`runtime/knowledge.py:689-694`): `root`, `library`, `revision`, `allowed_axioms`, `elements`, `pairs`, `axioms`, `verdicts`, `changes`, `organized`, `questions`, `question_aliases`, `question_proposals`, `concerns`, `findings`, `sequence` (`runtime/knowledge.py:50-58`), plus what `settle` adds: `contested`, `root_state`, `frontier`, `remaining` (`runtime/knowledge.py:333`, `358-362`). It has no `proofs` object **[inferred from that key list]**. A second, unrelated `state.json` is `runner/state.json`, the runner's operating state (`runtime/runner.py:128-134`).

**A glossary.** None exists. "There is no glossary and there are no folders of session records: a definition is an element like any other" (`SKILL.md:58`). "Its name, its wording and the reasons for it are in its record as those of a statement are, and there is no separate list of terms. That sessions use one name for one object is ensured by use: to work with an existing definition you refer to it by its Lean name, and Lean rejects a second declaration of a name." (`reference/common.md:109`). `render` writes exactly four files, `frontier.md`, `index.md`, `board.md`, `state.json` (`runtime/knowledge.py:653`, `666`, `688`, `694`).

**How all of it is derived.** "The canon's structural index says which declarations exist and what each uses; the summary of the records says what their authors declared about them; the events carry review's judgments in the order they were published. From these the standing of every element, the frontier and the state of the root are computed afresh on each replay, so no session writes them." (`runtime/knowledge.py:3-6`). "Prose is never interpreted." (`runtime/knowledge.py:1`)

### 7. The commands with which sessions read the canon

"A session learns what the canon holds by **traversal** of the structure of the Lean library. A traversal is determined by a starting point and a rule ... Its result is everything the rule selects, in a fixed order, with the count. No step asks you to choose search words or to guess at relevance. You can therefore say that you have seen the whole of a given scope, and a reviewer can run the same traversal to see what you could have seen." (`reference/common.md:237`)

There is one command, `commands.canon` in the session's `input.json` (`reference/canon.md:75`); it runs `runtime/canon_tool.py <command> <session folder>` (`runtime/context.py:73`). Output is text; an error is a JSON object with the key `error` and exit code 1 (`reference/canon.md:75`). The commands (`reference/canon.md:77-96`; parser at `runtime/canon_tool.py:391-418`):

| Command | Returns |
|---|---|
| `frontier` | The root's state and the frontier as it is now, then contested statements and uncleared concerns, the number of elements that are work that remains, then the questions. |
| `view <element>` | One element as one view. |
| `view <element> --full` | The same, with every part of the record and the approach entries in full. |
| `view <element> --part <part>` | One part: `statement`, `explanation`, `proof`, `literature`, `approaches`, `history`, `source`. |
| `list` | Every element. |
| `list --module <module>` | The elements of a module or of every module under a prefix. |
| `list --uses <element>` | The elements the proof of the statement names; for a definition, what its body uses. |
| `list --used-by <element>` | The elements whose proofs name it. |
| `list --about <element>` | Every element whose statement mentions it or whose proof uses it; for a definition, "what the canon states about that object". |
| `list --remaining` | The work that remains for the root. |
| `question <question>` | A question with its state, statement, grounds, understanding so far and review's assessment; `--history` adds earlier texts. |
| `log` | The most recent changes published through a review (twenty unless `--last`), each with review's assessment. |
| `checkout <folder>` | Copies `canon/lean` into a folder of the session for its own Lean work (`reference/tools.md:25`). |

Options: at most one selector per `list`; `--deep` follows `--uses` or `--used-by` all the way; `--units` restricts a list to units (`reference/canon.md:92`).

"These commands start no Lean process. They read the structural index and the records, which describe the canon as of its latest publication." (`reference/canon.md:94`). The stated reason is in the design record only: a loaded Lean process holds two to four gigabytes of commit charge, so reading goes through the index (`design:318`).

The four directions of traversal are containment, use, object and standing (`reference/common.md:239`; mapped to commands at `reference/canon.md:98`).

The operator uses the same reading commands with the instance folder in place of a session folder: `python <skill>/runtime/canon_tool.py <command> <instance> ...` (`reference/operations.md:336-344`; `runtime/canon_tool.py:25-27`). `prepare`, `verify` and `checkout` refuse the instance folder (`runtime/canon_tool.py:421-422`).

Other ways of seeing the current state: the files under `knowledge/` "can be read at any time", and `commands.updates` returns the current board, the questions and the concerns (`reference/canon.md:26`; `reference/tools.md:35`).

One reading is asked each time: "before you take on a statement, you should traverse, for each definition the statement uses, everything the canon states about that definition. This reading, and not the occupancy described in the next section, is what keeps a session from doing again what the canon already has. Nothing checks that you made it." (`reference/common.md:243`)

### 8. Approaches tried on a statement, and the understanding of a question

**Why nothing is kept per session.** "The canon holds no account of a session." What a session learns about the course of the work is kept in two ways, "and neither is keyed by session. The reason is how accounts keyed by session grow. Sessions keep coming, but what is learned about the course of the work does not grow with their number, because sessions approach the same statement in the same way and stop in the same place." (`reference/common.md:131`)

**What has become exact becomes elements.** "An approach that has been made exact consists of statements: a proof that the target follows if a certain gap is filled, the gap itself as a statement without a proof, and, if the approach is closed, the counterexample that closes it." (`reference/common.md:133`)

**Approaches tried.** "A statement whose proof is not accepted carries its **approaches tried**, one entry for each approach. An entry says what the idea was, which elements the approach established, where it stops, and which sessions contributed to it; review's assessment of what that work contributed to the research is added beneath it at publication." (`reference/common.md:135`). Format: one file `approaches/<Name>/<id>.md` with header keys `title` (required) and `sessions`, parts `## Idea` and `## Where it stops` (both required) and `## Established`; the runner adds `## Review` at publication, and a candidate that contains it is rejected (`reference/records.md:84`, `104`; `runtime/canon.py:34-36`, `199-207`, `374-375`, `1157-1168`). Updating: "a new approach is a new entry, an approach carried further replaces its entry, and an approach repeated to the same stopping point adds nothing" (`reference/common.md:135`). "When the proof of a statement is accepted, its approaches tried go to its history." (`reference/common.md:135`; `runtime/canon.py:1212-1227`)

**Questions and their understanding so far.** A question is "something the research wants to understand that has no form as a statement" (`SKILL.md:14`); "A question has an identifier, a statement of what is to be understood, and the grounds on which it was asked." (`reference/common.md:221`). "**Question 0**, written `q0`, is always present: it is the root problem itself, taken as a whole." (`reference/common.md:221`; `runtime/knowledge.py:14-17`)

"Each question carries its understanding so far. This is a text that says what has come to be understood about what the question asks, and what has not. Its mathematical assertions are elements, to which the text refers by name; the text itself explains, connects and interprets." (`reference/common.md:223`). It is one file `questions/<question>.md`, free Markdown without a header; the runner adds `## Review` at its end (`reference/records.md:110`). On replacement, the peer is told "you answer for the whole text and not only for what you add" (`reference/writing.md:57`), and review reads the new text against the old (`reference/common.md:223`).

The understanding so far of `q0` "is where the account of the problem as a whole is kept: how the proof goes, what the parts share, where the difficulty lies. Every session receives it in its starting context. No separate document and no separate role maintain such an account" (`reference/common.md:225`).

Questions come into being by a peer's proposal that review admits, by the operator placing them directly, and they are merged by the organizer (`reference/common.md:227`). A question is **resolved** "when review judges that its understanding so far answers what its statement asks" (`reference/common.md:229`). `q0` is resolved only by the root's formal settlement, derived at each replay (`reference/common.md:231`; `runtime/knowledge.py:393-413`; a resolution naming `q0` is refused, `runtime/check.py:193`).

**The session's own account** "is kept outside the canon: its report, its conversation and its working files are retained unchanged." An approach entry names the contributing sessions "so that a reviewer designated to examine it can reach those originals. An ordinary session uses the canon and does not read another session's originals." (`reference/common.md:137`)

### 9. Publication

**What publication is.** "When review finds material worth keeping, the runner applies the candidate to the canon, compiles the library, extracts the structural index again and commits the result. This is **publication**. It is a local file and Git operation; the mathematical judgments come from review. Publications are made one at a time." (`reference/common.md:125`). The reason for one at a time: "each changes the one library that every session reads and that every later candidate is built on" (`reference/operations.md:465`).

**What a published change is.** A candidate change is "the proposed change to the canon: new elements with their records, new proofs for statements that already stand there, and the written state the next paragraphs describe" (`reference/common.md:119`). Once published it is recorded as `knowledge/changes/<id>/` with its manifest, what it added and replaced, review's assessment and feedback, the sessions involved and review's own compile (`reference/operations.md:333`), and as an event with a sequence number (`runtime/runner.py:613-617`). Its content is in `canon/`. Four kinds of event exist: `change`, `review` (a comprehensive review), `organization`, `questions` (`runtime/knowledge.py:208-209`).

**Review judges and does not gate.** "Review is a judgment and not a gate. ... What it does not do is hold useful material back until it has been repaired. ... An element whose proof review could not confirm enters the canon in that state, with review's reason beside it, and a correct partial result can stand beside a gap elsewhere in the same candidate. Nothing is returned to a session for repair; a later session does the repair" (`reference/common.md:123`). If review concludes that a candidate contains nothing worth keeping, "nothing is published and the processing ends" (`reference/common.md:139`).

**Can a published statement change afterwards?** No. "Publication follows four rules, and one invariant stands behind them: the statement of an element is never changed in place." (`reference/common.md:127`). The four rules, from the same paragraph:

1. "New elements are added in new modules, and no existing file is edited to add a declaration."
2. "A proof that takes the place of another proof of the same statement is put where the old proof stood; the name and the statement stay, and the old proof does not remain in the library."
3. "A statement that supersedes another enters as a new declaration under a new name, and the old element keeps its name and its statement, its proof becoming one line that derives it from the new one, so that whatever rested on the old element still stands."
4. "a written text that is replaced, a record or one of the texts described below, survives only as its difference in the history."

The reason for the invariant: "A candidate is frozen when its peer ends, review then takes the time it needs, and meanwhile other candidates are published. A candidate rests on statements, so nothing that others published in the meantime takes away what it rests on: every statement it uses still stands as it stood." (`reference/common.md:127`)

The runner enforces the invariant by machine: it compares the statement hash and kind of every declaration before and after (`runtime/canon.py:1010-1029`). A definition's body is not replaced in place either, "because what uses it would change its meaning" (`runtime/canon.py:1032-1034`). One case is refused although the text is unchanged: when a change enlarges what a module imports and Lean then elaborates the same statement text into another term (`runtime/canon.py:1013-1027`; `reference/operations.md:465`).

**What can be replaced.** A record "can be replaced by a better one, and a proof by a better proof" (`reference/common.md:111`); an approach entry and an understanding text can be replaced (`reference/common.md:135`, `223`). A record of an element whose proof the candidate does not replace may not change the written proof or the `proves`/`refutes` keys (`runtime/canon.py:1103-1112`). Replacing a proof requires that the candidate's pipeline holds a section on that statement (`reference/common.md:263`; `runtime/check.py:157-166`), and review says for each such proof whether the new one takes the old one's place (`runtime/check.py:275-290`; outcomes at `reference/common.md:168`). What remains of a replaced text is "the difference between the two texts, kept as the element's **history**, which is stored apart from the files a session reads and is shown only when asked for" (`reference/common.md:111`; format `runtime/canon.py:1124-1132`). The guide for the `history` part says the Lean text of each replaced proof is kept there too (`reference/canon.md:82`).

**Checks before publication.** "Before publishing, the runner confirms that the candidate builds on the canon as it is at that moment." (`reference/common.md:129`). The machine checks repeated at publication: "no statement changed in place, every added declaration has a record and every record a declaration, no axiom was declared, no definition contains `sorry`, and Lean confirms each claim that one declaration proves or refutes the statement of another" (`reference/operations.md:465`; `runtime/canon.py:985-1119`). A candidate that fails goes to a replacement peer and a new review (`reference/common.md:129`; `reference/operations.md:469`), because "A candidate that would not build would break the canon for every session" (`reference/operations.md:469`).

**What a revision is.** The sources use the word for a number that counts publications. Each event gets `sequence` = the previous sequence plus one (`runtime/runner.py:616`, `631`), and `frontier.md`, `index.md` and `board.md` print "Revision:" followed by that sequence (`runtime/knowledge.py:647`, `654`, `667`). The structural index carries its own `revision`, set to the sequence of the publication that last produced it (`runtime/runner.py:798-800`, `805`; 0 at `init`, `runtime/runner.py:149`); `checkout` reports that number as "the revision of the canon it copied" (`reference/tools.md:29`; `runtime/canon_tool.py:385`), and `status` calls it the "library revision" (`reference/operations.md:415`). Whether the index revision also advances on events that do not change the library (comprehensive reviews, operator questions) is **[not established]**; I did not read `runtime/runner.py` in full. No guide I read defines "revision" in a sentence.

### 10. Concerns, findings and comprehensive review

- "A **concern** is a reported challenge to the proof of an identified element. Its explanation names the evidence in doubt and why it matters. A concern annotates and changes nothing: the standing of the element stays as it was." (`reference/common.md:287`). `SKILL.md:60`: "A pending concern does not change the standing of that proof; only a review finding can withdraw its confirmation."
- "A **comprehensive review** is an assignment of the same review role to examine questioned evidence and its actual uses in later arguments. It is triggered by a concern, by a contested statement whose opposing proofs need their failure located, or by a request to examine named elements; it is not another routine stage for every new candidate." (`reference/common.md:287`). The operator's request is `review --element <name>` (`SKILL.md:60`; `reference/operations.md:440`).
- "A **finding** is the judgment such a review, or the review of a later candidate, attaches to existing work. It can withdraw the confirmation of a proof, restore it, or reopen a question." (`reference/common.md:287`)

In code: a concern has an id, `targets` (elements), a `reason` and `evidence`, and starts as `pending` (`runtime/check.py:202-210`; `runtime/knowledge.py:63-66`). A finding has a `status` of `cleared`, `confirmed` or `undetermined`, a `reason`, the concerns it answers, and optional lists `invalidates`, `validates` and `reopens` (`runtime/check.py:213-223`). "A finding is the only thing that changes a judgment already published. ... A status alone changes nothing." (`runtime/knowledge.py:70-73`). `invalidates` sets the verdict to `not_confirmed` with the finding's reason; `validates` sets it to `confirmed` (`runtime/knowledge.py:90-103`). A candidate review's finding that invalidates without naming a concern creates a follow-up concern (`runtime/knowledge.py:108-111`).

Effect of a withdrawal: "A proof that review confirmed keeps its standing, and everything settled through it stays settled, until a finding withdraws the confirmation. When a finding does, the proof becomes 'proof not confirmed', every standing is computed again from what remains, and a statement that was settled through that proof may no longer be settled. The element, its record and the finding all remain visible" (`reference/common.md:289`). A finding that confirms a gap "does not prove the statement false, and another proof of the same statement may still stand" (`reference/evidence.md:43`).

Where they are shown: the frontier view lists the pending concerns, and the view of an element shows the concerns and later reviews about it (`reference/common.md:287`; `runtime/knowledge.py:569-575`; `runtime/canon_tool.py:147-152`). Concerns are attached to the elements they target only (`runtime/knowledge.py:334-337`); I found nothing that marks the elements resting on a questioned element **[inferred from `runtime/knowledge.py` and `runtime/canon_tool.py`]**.

Scheduling: "Whenever no comprehensive review is pending or running, the runner assigns one that covers every concern that is not cleared and every contested statement's current set of opposing judgments it has not yet assigned. When that review leaves the concern uncleared or the statement contested, the runner does not assign it again; a further examination needs an operator `review` request." (`reference/operations.md:360`). A rejection by the root judge also leaves a request for a comprehensive review (`reference/operations.md:415`, `421`).

How a session should treat a questioned element is its own assessment: "The shared state does not make that assessment for you." (`reference/common.md:289`; `reference/evidence.md:41`)

### 11. Results that rest on computation; what `evidence.md` asks

**In the record.** "For a statement established by an exact computation, the proof is the account of that computation: what was computed, over which range and in which arithmetic, with the code and its output among the files of evidence." (`reference/records.md:55`). The files go to `canon/evidence/<Name>/` (`reference/canon.md:17`; `runtime/canon.py:1184-1188`), "so that a later session can check the account against them and run the computation again" (`reference/evidence.md:37`). The writing guide: "State what a computation actually established: inputs, range, arithmetic, code, output, and how to reproduce it. An exact calculation for a finite range proves that finite statement. A pattern in the results can motivate a conjecture; extending it to all inputs requires further reasoning." (`reference/writing.md:33`)

**As a statement.** An observation is itself a statement over its range: "that a quantity is positive for every n up to 2000 is a statement, and a different one from the statement about every n" (`reference/common.md:91`). An element whose truth rests on a computation is a unit even if a single proof uses it (`reference/records.md:70`).

**In review's judgment.** A correct proof that "establishes part of the statement only by large computation carried out without an understanding of why that part holds" is held back, not accepted, unless the setting is turned off (`reference/common.md:147`; `reference/operations.md:261`). Such a proof "is published and can be used, and the statement stays among the work that remains" (`SKILL.md:12`). The hold falls on the element where the difficulty lies; the example given is a statement read from a published table for small parameter values, where with three ranges stated as three elements "the hold falls on the third alone" (`reference/common.md:164`). The guides state a limit of this consideration from an earlier run: the user "did not count that table lookup as the kind of computation the condition meant" (a finite remainder of a few thousand cases looked up in an exact table) (`reference/common.md:283`).

**In Lean.** A computation carried out inside a complete Lean proof is formal only if its axioms are allowed. "Under the default axiom policy, `native_decide` introduces an axiom that is not allowed" (`reference/lean.md:204`); the axiom that `native_decide` adds for each computation counts among the axioms of every statement that rests on it (`reference/lean.md:214`; `runtime/canon.py:714-716`). So a statement proved with `native_decide` is not formal under the default list **[inferred from those lines]**. Whether a proof that rests on a computation described in a record is "informal" follows from topic 3: its Lean proof ends in `sorry` **[inferred]**.

**In the guidance on doing the work.** "The amount of work done and the size of the range covered do not by themselves move the research forward." (`reference/common.md:29`). "This guidance concerns running large computations without understanding what the results mean, and it does not concern computation in general." (`reference/common.md:57`)

**What `evidence.md` is.** `reference/evidence.md` is titled "Reading mathematical evidence" and "develops the judgment that comes next: whether a particular element gives you the mathematical premise your own work needs" (`reference/evidence.md:3`). It is a guide to reading, not a format; nothing in it is machine-checked **[inferred: no code I read refers to it]**. What it asks of a session:

- Compare the element's "objects, hypotheses, domains and quantifier order with the present use, and make the comparison on the Lean statement" (`reference/evidence.md:9`). Lean checks one half (a hypothesis you cannot supply remains an obligation); "The other half Lean cannot check: whether the statement means what you take it to mean." (`reference/evidence.md:11`)
- Read the scope as written (`reference/evidence.md:13`) and the standing for what it says (`reference/evidence.md:17-27`, quoted under topic 5).
- "Name the statements your argument uses, and those only." (`reference/evidence.md:33`)
- Where a record refers to files of evidence, "read what the computation actually covered: its inputs, its range and its arithmetic" (`reference/evidence.md:37`).
- If you continue with a questioned element, say so and say what your result would need if the doubt were confirmed (`reference/evidence.md:41`).

`evidence.md` is not placed in any role's `pack.md`; it reaches a session only as a reference copy under `context/reference/` and through the link in the common introduction (`runtime/context.py:88-90`, `18-25`, `62-63`; `reference/common.md:245`).

The guides contain no rule about floating-point arithmetic, binary64 or assumed error models; a search of every `.md` file of the skill folder for `binary64`, `floating` and `interval arithmetic` found nothing. **[not established: how such a computation is to be classified]**

### 12. Literature

**What `literature.md` asks.** "You should actively look for earlier work you can use, and cite it, instead of building everything again yourself." (`reference/literature.md:3`; the reason, from the earlier run, at `reference/common.md:63`: about one session in eight looked beyond the instance's own work, and several searched separately for the same papers.)

- Decide what the search is for; whether a result is known needs a broad search, and "One relevant paper does not answer the question, and neither does one search that returns nothing." (`reference/literature.md:7-13`)
- Look first at what the instance already has: `canon/bibliography.bib`, and the records whose header names a source key (`reference/literature.md:17`); and at the imported library, whose results are "used directly in a proof, by the library's name for it, without a citation and without an element" (`reference/literature.md:21`).
- Interpret each outcome exactly: "Any assertion that something is new, or absent from the literature, must be bounded by the sources and the search scope actually examined." (`reference/literature.md:33`)
- Keep a search log under `work/literature/`; "The form is a recommendation and nothing checks it." (`reference/literature.md:37-45`). The log is not visible to later sessions, so what they need goes into the canon (`reference/literature.md:47`).

**A result from the literature in the canon.** It "enters the canon as an element, like any other result. Its statement is written in Lean, in terms of the instance's own definitions" (`reference/literature.md:51`). Its record has the header key `source`, a `## Literature` part giving the location in the source, how much was read and where the statement stands, and a `## Proof` part, which "is what makes the statement count as having a proof" and says that the proof is the one in the source and gives the argument from the source's statement to the Lean statement (`reference/literature.md:57-59`). "review judges the element on what was read" (`reference/literature.md:59`). The bibliography entry is BibTeX in `bibliography.bib` (`reference/literature.md:75`); an existing key keeps its entry (`runtime/canon.py:1197-1209`).

Limits the guide states: "A result from the literature can be used as a step of a proof only after its exact statement and its hypotheses have been confirmed at the source" (`reference/common.md:69`); "A citation lets a reader check your account against its source; it does not supply an application argument you left out." (`reference/literature.md:53`). And a consequence: "A cited result that the root comes to rest on is under the same final requirement as every other statement: before the research is complete, it needs a complete Lean proof." (`reference/literature.md:93`)

**Tools.** "The instance's literature tool is scholarly-mcp." Its calls are `list_sources`, `describe_source`, `search`, `extract` and `fetch` (`reference/literature.md:25`). Sessions receive the sources reached through public interfaces, among them zbMATH, OpenAlex, Semantic Scholar, Crossref and arXiv; sources that need an institutional login are not offered, so "MathSciNet cannot be searched and ... the full text of many journal articles cannot be retrieved" (`reference/literature.md:27`). The default settings attach the server with `--public-only` to every instance unless the settings file gives `mcp_servers` itself (`SKILL.md:42`; reason at `reference/operations.md:249`: each session starts its own copy, and without the option each copy would log in to the institutional account). The server's store is shared by every session on the machine (`reference/tools.md:47`). Web search and the pages of preprint servers and authors supplement it (`reference/literature.md:31`).

`literature.md` is in the starting context of attempts, explorers, peers and reviewers, not of formalizers or organizers (`runtime/context.py:18-25`).

### 13. What the guides count as progress

"A piece of work moves the research forward by what it changes in what is known. It may close something: settle a statement or one of its sections ... It may let the research see something it could not see before: why a property holds, where a method's reach ends and what about the object stops it there, which structure two results share. Or it may change how the problem is approached, by showing that a route is closed, that a different formulation isolates the difficulty, or that an obstruction met by several methods has a common cause. These are examples rather than a list, and much real work does several of these things at once." (`reference/common.md:27`)

What does not count: "The amount of work done and the size of the range covered do not by themselves move the research forward. For a statement about every n, raising the bound up to which it has been verified, from ten thousand to twenty thousand for instance, decides nothing on its own, because every case beyond the new bound is as open as before." The same computation does count "when it completes something ... or when examining its results teaches something about the object" (`reference/common.md:29`). "You should not count a result as an accomplishment merely because it is correct, or even because it is useful. You should also understand the result you obtained" (`reference/common.md:55`). A formal proof of a side lemma is the easier kind of work to avoid "whenever it leaves the difficulty you took on where it was" (`reference/common.md:95`). A reworded statement or a division the mathematics does not suggest "leaves the research where it was" (`reference/common.md:255`).

The research also seeks understanding, not only the settling of the root (`reference/common.md:33`).

Where this judgment is recorded: review "says what the work contributed to the research" (`reference/common.md:123`), and that assessment is written beneath each approach entry and understanding text of the change and shown by `log` (`runtime/canon.py:1157-1172`; `reference/canon.md:90`). The runtime stores the contribution as text and computes nothing from it **[inferred from `runtime/knowledge.py:133-136`; `runtime/runner.py` not read in full]**.

All of this is in the common introduction, which every role receives first (`runtime/context.py:88`). I did not read the role guides under `roles/`, so I cannot say what they add.

### 14. The two documents

**`reference/what-research-is-for.md`** ("What mathematical research is for"). An essay. Its authors are "the user who started the investigation and followed it every day, and ... the operator who kept it running"; after an investigation of several days on a problem in combinatorics had left "well over a hundred" session records, they "read all of the records, in the order in which they had been written. This essay is about what we came to think as we read." (`reference/what-research-is-for.md:7`). Its opening sections describe what they saw: a verified range that kept growing while "our understanding of the object had barely grown at all" (`:17`), obstructions located precisely while "very few records set those obstructions side by side and asked what they revealed about the object" (`:27`), and earlier results handed on as conclusions without the understanding behind them (`:31`). It defines "closing" in a sense of its own (`:37`; the common introduction explains how that sense relates to its own use of "close", `reference/common.md:37`). The common introduction describes the essay as developing its ideas "through what mathematicians have sought in their research" (`reference/common.md:35`) and says the essay "explains why its authors chose not to add instructions such as 'look for the underlying structure'" (`reference/common.md:43`). I read lines 1-40 only.

**`reference/user-writing-preferences.md`** ("How this user likes to be written for"). "This document is about the kind of writing one person prefers. That person is the user who runs do-math research and reads what it produces" (`reference/user-writing-preferences.md:5`). The preferences come "mostly from one piece of writing", the essay above, which an AI wrote in five versions with the user's response to each (`:7-11`). "None of what follows is meant as a rule." (`:15`). I read lines 1-40 only.

**Which roles receive them.** `RESEARCH_CONTEXT = ['what-research-is-for.md', 'user-writing-preferences.md']` is part of the references of `attempt`, `explore`, `peer`, `review` and `organizer`, and not of `formalizer` (`runtime/context.py:14`, `18-25`). The guide agrees: "Attempts, explorers, peers, reviewers and organizers receive both documents in their starting context, and every session finds them among the reference copies in its session folder." (`reference/common.md:35`). The second half holds because every `reference/*.md` file is copied to `context/reference/` of every session (`runtime/context.py:62-63`), the formalizer's included.

### 15. The starting context of a session

`assemble` (`runtime/context.py:55-141`) writes three things into the session folder: `input.json`, `pack.md` and `prompt.txt`, and copies the guides.

**Copies.** All `reference/*.md`, the session's role guide `roles/<role>.md`, and `SKILL.md` are copied under `context/` (`runtime/context.py:57-66`). "References are snapshots too: editing installed guidance does not change a running session's instructions when it follows a reference later." (`runtime/context.py:60-61`)

**`input.json`** holds `schema`, `instance`, `session`, `role`, `pipeline`, `task`, `revision`, `references`, `documents`, `user_inputs`, `settings` and `commands` (`runtime/context.py:91-95`). `user_inputs` are all files `control/inputs/*.txt` at launch (`runtime/context.py:67-69`).

**`pack.md`**, in this order (`runtime/context.py:105-136`; summarized at `reference/common.md:295`):

1. a header naming the role, session and instance;
2. "Root statement": the text of `root.md`;
3. "The root in Lean": the root declaration's source text and its statement as Lean prints it (`runtime/context.py:28-37`);
4. "Your assignment": the `task` as JSON;
5. the guides, embedded in full: `reference/common.md`, `roles/<role>.md`, `reference/writing.md`, `reference/canon.md`, `reference/lean.md`, `reference/tools.md`, then the role's references (`runtime/context.py:88-90`);
6. "Frontier at launch": `knowledge/frontier.md` (which includes the questions and concerns);
7. "Understanding so far of the root problem as a whole (question q0)": `canon/questions/q0.md`, or "No exploration has written it yet.";
8. "Board at launch": `knowledge/board.md`;
9. "User conditions supplied at launch", in listed order, with the sentence "Later conditions override earlier conditions on the same matter. Mathematical suggestions remain suggestions; they do not certify claims.";
10. "Executable commands".

The stated reason for the order: "The proposition and the assignment come before the guides, so that the guides are read with both in mind." (`runtime/context.py:104`)

**The role's references** (`runtime/context.py:18-25`):

| Role | References after the six common documents |
|---|---|
| attempt | the two research documents, `literature.md`, `sections.md`, `retained-work.md` |
| explore | the two research documents, `literature.md`, `retained-work.md` |
| formalizer | `retained-work.md` |
| peer | the two research documents, `literature.md`, `sections.md`, `retained-work.md`, `records.md`, `change-format.md` |
| review | the two research documents, `literature.md`, `records.md`, `change-format.md`, `review-output.md` |
| organizer | the two research documents, `records.md`, `change-format.md`, `organizer-output.md` |

The code comment gives the rule: "Every role states mathematics in Lean and reads the canon, so each receives the canon and Lean guides. A guide that only some roles act on goes to those roles" (`runtime/context.py:15-17`).

**`prompt.txt`** tells the session its role and working directory and to read `pack.md` in full (`runtime/context.py:137-140`).

**What a session does not inherit.**

- The earlier researchers' conversations: "You begin without the earlier researchers' conversations in your context, so the mathematics they left must supply the definitions, arguments and evidence you need." (`reference/common.md:5`)
- Personal or project instructions, hooks and memories: "Worker sessions inherit no personal/project instructions, hooks or memories. Their guides, references and standing inputs are supplied by do-math and saved at launch." (`SKILL.md:42`; `reference/common.md:303`; `reference/operations.md:234`)
- Tools from the operator's personal configuration, unless configured in `mcp_servers` (`SKILL.md:42`; `reference/tools.md:47`).
- Standing inputs given after its launch: "Instructions the user gives later apply to the sessions launched after them." (`reference/common.md:285`; `reference/tools.md:35`)
- Another session's originals, except for designated peers and reviewers (`reference/common.md:137`, `291`).
- Any list of definitions or survey: the starting context "holds no list of definitions" (`reference/common.md:243`).

A delegated sub-agent of a Claude session "begins with nothing but what you hand it" (`reference/tools.md:51`).

Research information stays live after launch: publications, standings, sections and questions change, and a session obtains updates at natural pauses (`reference/common.md:285`).

### 16. The language used inside an instance

"Everything written inside an instance is written in English. That covers your notes and working files, your retained report, the records, approach entries and understanding texts of a candidate, assessments and feedback, organization output, coordination messages, what you hand to a delegated agent, and the comments in Lean sources. The root statement and the user conditions reach you in English as well. Sources in other languages are read and cited as they are; what you write about them is in English." (`reference/common.md:297`)

The operator writes "the root statement, the records and every input in English, whatever language the user speaks to you in" (`SKILL.md:34`; `reference/operations.md:19`). A user condition is given as the user's words in English translation, marked as the user's, apart from the operator's own text (`reference/common.md:281`; `reference/operations.md:296`). The operator explains the Lean statement to the user "in the user's language" (`reference/operations.md:159`). Formulas are written in LaTeX between dollar signs and element names in backticks (`reference/writing.md:59`). No source I read gives a reason for English **[not established]**.

### 17. The allowed axioms; what Lean checks, what review judges, what nothing checks

**The allowed axioms.** "The default allowed axioms are `propext`, `Classical.choice` and `Quot.sound`. `sorryAx` is never allowed." (`SKILL.md:40`). The list is `settings.lean.allowed_axioms`; "an instance may explicitly allow more. `sorryAx`, the axiom that stands for a `sorry`, is never allowed, and the settings refuse a list that contains it." (`reference/lean.md:214`). The dependence is followed "through everything the statement uses: the canon elements that its proof and its statement name, what those use in turn, and the declarations of the imported library", and a private axiom or the axiom `native_decide` generates counts as itself (`reference/lean.md:214`; `runtime/canon.py:714-716`, `832-880`). Consequence: "a hole in a lemma appears among the axioms of everything that rests on that lemma, even when the file of the final theorem contains no `sorry`" (`reference/lean.md:216`).

**What Lean (and the runner's machine checks) establish.**

- That every statement and definition is well formed, and that each name a proof uses exists and fits (`reference/common.md:105`).
- That a complete proof proves its statement as written (`reference/lean.md:226`: "Lean checks that a proof proves the statement as written").
- The axioms each statement depends on, through the structural index (`reference/lean.md:214-218`).
- That a declaration claimed to be another proof of a statement has the identical statement, and that a claimed refutation states the negation (`reference/lean.md:224`; `runtime/canon.py:646-653`).
- At publication, by the runner: no statement changed in place, records and declarations correspond, no axiom, no `sorry` in a definition (`reference/operations.md:465`).
- By the **judge**, where the Lean installation provides `leanexport` and `lake comparator` (Lean 4.35 and later, `reference/operations.md:409`): before a change is published, every formal proof it brings is exported and replayed through the kernel and its axioms worked out again, from outside the index; a rejected change is not published (`reference/lean.md:222`; `reference/operations.md:411`). "No session runs the judge." (`reference/lean.md:222`). Its limit is stated: "The verdict therefore rests on those builds having been made honestly: Lean code that a session wrote runs when it is compiled ... What the verdict does not rest on is the structural index, the views, or anything a session reported." (`reference/operations.md:425`)

**What review judges.** "Of a definition it judges whether the definition denotes the intended object and whether the library already has that object. Of a statement it judges whether the Lean form says what the record says. Of a proof it judges whether the proof is correct and, separately, whether a correct proof is accepted" (`reference/common.md:121`). Review also judges the weight (`reference/records.md:80`), the division a proof makes (`reference/common.md:213`), question proposals and resolutions (`reference/common.md:227`, `229`), and the replaced written texts against the old ones (`reference/common.md:135`). For a proof complete in Lean, "Review confirms a proof that is complete in Lean only after compiling the candidate itself and reading the axioms each statement depends on" (`reference/common.md:174`); the transport check confirms that the named build is the reviewing session's own finished fresh compile (`reference/lean.md:220`; `runtime/check.py:226-246`). Review first has three independent sub-reviewers examine the same material; "the judgment recorded with the canon is the reviewer's own" (`reference/common.md:121`). Limit: "If confirming a proof would require an essential new argument, review reports what is missing and does not supply that argument and call it independently validated." (`reference/common.md:121`)

**What stands without a review.** "Two kinds of proof stand without a review. One is a complete Lean proof you supply with the canon at creation, such as a check of a definition on known values: Lean checks it at `init`. The other is a statement an organizer adds, saying that two definitions or two statements agree, or deriving a statement from another that agrees with it: its proof has to be complete in Lean from the allowed axioms, which the runner checks again when it publishes the organizer's change, and it enters as accepted." (`SKILL.md:40`; `runtime/canon.py:1113-1116`). An organizer's rearrangement of modules also goes without review; a machine confirms that every other element keeps its name and statement (`reference/common.md:184`; `runtime/canon.py:1035-1046`).

**What nothing checks.**

- Whether the Lean statement of the root says what the user meant. "The instance is complete when this statement, or its negation, is settled by a formal proof, and no later step judges whether the theorem that was proved corresponds to what the user meant. That correspondence is established now. Lean checks that the definitions and the statement are well formed; it cannot check that they say what the user means." (`SKILL.md:22`). The only judgment of meaning is the user's confirmation before `start`: "it is the only judgment of meaning the Lean statement will receive from the person whose proposition it is" (`reference/operations.md:159`). The check of the definitions on known small values "is evidence that the definitions denote the intended objects, and not a proof of it" (`SKILL.md:24`; `reference/operations.md:146`).
- The root judge does not check meaning either. It "judges the settled root against the root as the instance first fixed it" (`SKILL.md:66`): "the statement proved is the statement posed, with every definition it depends on unchanged" (`reference/lean.md:222`; `reference/operations.md:413`). The runner starts it once the root is formally settled, and `status` gives its verdict under `root_judge` (`SKILL.md:66`; `reference/operations.md:415`). The runner also refuses to run an instance whose root file or root statement in Lean has changed (`reference/operations.md:165`; `runtime/runner.py:204-206`).
- If a session finds a difference between the two forms of the root it "cannot repair it, because a changed root is a different proposition and needs a new instance"; it can state the difference with a case (`reference/common.md:15`).
- Whether any other statement or definition says what was meant is review's judgment, not Lean's (`reference/lean.md:226`); for the elements supplied at creation and for the organizer's additions no review has made it **[inferred from `reference/common.md:158` and `SKILL.md:40`]**.
- Whether a session made the traversal asked of it (`reference/common.md:243`; `reference/canon.md:162`), the form of a search log (`reference/literature.md:45`), whether a session respected other sessions' sections in its mathematics (`reference/common.md:265`), and the content of a producing session's report (`reference/tools.md:55`).
- The transport check "does not prove mathematical statements or evaluate the quality of the exposition" (`reference/tools.md:55`; `runtime/check.py:1`).

### 18. When an instance counts as complete

"The instance is complete when the root is settled through a proof that is formal, or when a statement that Lean has confirmed to be the negation of the root is. An informal proof is therefore never the end: every statement the root rests on needs a complete Lean proof before the research is finished." (`reference/common.md:170`). `reference/operations.md:358`: "The instance is complete when the root is `formal_proved` or `formal_refuted`." In code: `root_solved` is true exactly in those two states (`runtime/knowledge.py:381-390`, `423-424`).

Spelled out: "The root is settled by a formal proof when one of its proofs is accepted, everything that proof rests on is settled, and the proof is formal." (`SKILL.md:64`). "A formal proof of the negation is a refutation of the original proposition and settles the research in the same way." (`SKILL.md:64`). A contested root "is not treated as settled for completion" (`reference/operations.md:360`).

Completion of the instance and the runner finishing are different: "From then on the runner stops launching attempts and explorations. Existing sessions retain their normal scope; the runner carries them through peer and review, still launches formalizations, comprehensive reviews and organization as their inputs become ready, and finishes only when that remaining work has ended. Formalization of other settled statements that the root rests on has no round cap, so the runner can keep working well after the root is settled." (`SKILL.md:64`). Completion can be undone: a later finding that withdraws a confirmation the settlement rests on reopens `q0`, and the runner resumes research (`reference/operations.md:362`, `368`).

Formal proofs are written bottom-up: a formalizer is launched for a settled statement the root rests on that has no formal proof, once every statement its proof names has one (`reference/common.md:172`; `runtime/knowledge.py:443-469`); formalizers are launched whatever the root's state (`reference/operations.md:358`).

After completion two commands produce the dependency map and the paper from the canon (`SKILL.md:66`); the paper command runs only when the root's state is `formal_proved` or `formal_refuted` (`reference/operations.md:388`), while the map can be drawn at any time (`reference/operations.md:376`).

---

## Part 2. The README against the current system

Ranges read: `README:1-36`, `97-145`, `169-181`. Each entry gives the line, the mark, and for every mark other than `true` what is wrong with the current fact and its source. Headings are included because several name things that no longer exist.

### Lines 1-36

- **README:1** (title) — `true`.
- **README:5** (row "What it is") — `partly`. The first sentence is still correct (`SKILL.md:3`, `reference/common.md:3`). "Mathematics is produced, written up and assessed by three different sessions" still describes a pipeline of producer, peer and review (`reference/common.md:125`), with three qualifications: the peer is "neither a translator of the attempt's mathematics into Lean nor a checker of it" and works the mathematics itself (`reference/common.md:119`); review first has three independent sub-reviewers (`reference/common.md:121`); and two kinds of proof enter without a review, complete Lean proofs supplied at creation and statements an organizer adds (`SKILL.md:40`). "every result is published together with its assessment": review writes a verdict with its reason for each element a candidate adds and each proof it would replace (`reference/common.md:121`), but the elements supplied at creation have no verdict (`reference/common.md:158`), and what is published is an element of a Lean library, not a record of a session (`reference/common.md:131`).
- **README:6-10** — `to be deleted`.
- **README:11** (row "Run it") — `true` as a pointer; the anchor `#running-do-math` exists at `README:183`. I did not check `docs/do-math/running.md`.
- **README:12** (row "Cite") — first half `true` as a pointer (I did not open `CITATION.cff`); "the knowledge base by the DOI of the version you read" is a Zenodo sentence, `to be deleted`.
- **README:14** — `partly`.
  - "The sessions have no contact with one another." Too strong: sessions share no conversation, but they see one another's occupancy on the board and can send coordination messages (`reference/common.md:257`, `265`; `reference/tools.md:37-39`).
  - "what survives review is published as a record in a shared knowledge base": `gone`. Nothing is published per session; results enter as elements of the canon, a Lean library with a record beside each declaration (`reference/operations.md:312`; `SKILL.md:10`). "Record" now means the written file beside one declaration (`reference/common.md:107`).
  - "The user supplies the statement ... written out exactly": incomplete. The root is fixed in two forms, in words and as a Lean declaration that the operator writes with the user and the user confirms (`SKILL.md:22`, `26`; `reference/common.md:15`).
  - Standing inputs, the operator and the runner: `true` (`SKILL.md:8`, `14`, `34`; `runtime/context.py:67-69`).
- **README:16** — `partly`; its frame "Every record is produced in three stages" is `gone` (no record per session, `reference/common.md:131`).
  - First stage: the three producing roles exist (`SKILL.md:14`). Missing: producing sessions state their mathematics in Lean from the start (`reference/common.md:83`). The formalizer receives "a settled statement that the root rests on" (`SKILL.md:14`), not "an already reviewed proof".
  - Peer: it writes "the candidate, the change to the canon: new elements, replaced proofs, records, the approaches tried on a statement, and the understanding so far of a question" (`SKILL.md:16`), not an exposition with proposals. No statement is proposed for admission: "no session or reviewer admits a statement to the frontier" (`reference/common.md:211`). Questions are still proposed (`reference/common.md:227`).
  - Review: it "has three independent sub-reviewers examine the candidate and its originals, compiles it itself, and judges each element" (`SKILL.md:16`). There are no "claims"; the judgments are of definitions, statements and proofs (`reference/common.md:121`).
- **README:18** — `partly`.
  - "the candidate is published as a record with that assessment attached, and the record is never edited afterwards": `false`. What never changes is the statement of an element (`reference/common.md:127`); a record and a proof can be replaced, leaving the difference in the history (`reference/common.md:111`).
  - Findings: still exist, attached to elements, and can withdraw or restore a proof's confirmation or reopen a question (`reference/common.md:287`); "on that record" is wrong.
  - "No session plans the work of another": `true` for attempts (`reference/common.md:19`). For explorers, the runner assigns `q0` to an explorer launched while it is free (`reference/common.md:269`).
  - "a formalizer when a reviewed proof or refutation bears on the statement under research": now "for a settled statement that the root rests on and that has no formal proof yet, once every statement that its proof names has a formal proof", and likewise for a settled refutation of the root (`reference/common.md:172`).
- **README:20** — `partly`. Continuity: the memory between sessions is the canon, not session records (`reference/common.md:5`, `7`). Independent judgment: review is a separate session (`reference/common.md:121`), but "no session certifies its own work" has the two exceptions of `SKILL.md:40`, where Lean's check stands in place of review. "useful work that is not yet perfect can still be published": `true` (`reference/common.md:123`). That exactly "two considerations shaped this design" is the README's own framing; the current sources give other reasons for the present design (`reference/common.md:85-87`, `131`; `design:21-33`), and they use "two considerations" for something else, the grounds on which review withholds acceptance (`reference/common.md:147`).
- **README:22** — `to be deleted` (first run).
- **README:24** — first, third and fourth sentences `to be deleted` (first run, Zenodo). The second sentence, "do-math considers a run complete only when a Lean proof of the statement, or of its negation, has been recompiled by a review session, audited for the axioms it uses and matched against the exact statement", is `partly`: completion is the root settled through a formal proof, or a confirmed negation of it (`reference/common.md:170`); review compiles the candidate itself and reads the axioms (`reference/common.md:174`); but nothing is "matched against the exact statement" afterwards, because the theorem to be proved is the fixed root declaration itself (`SKILL.md:22`; `reference/lean.md:224`). What exists instead is the runner-started judge that compares the settled root with the root of the first commit (`reference/lean.md:222`).
- **README:26** — `partly`. The outline names "the first run in outline" and the full account of the first run (`to be deleted`) and "the layout of a published knowledge base", whose layout has changed (see README:173-181 below).
- **README:28** (heading) — `true`.
- **README:30** (heading "Instances, roots and nodes") — `gone` for "nodes".
- **README:32** — `partly`. `true`: an instance is a directory with its own Git repository (`SKILL.md:10`), with `root.md`, `settings.json` and a directory per session (`runtime/runner.py:117`, `125-126`; `reference/tools.md:11`), and the root never changes (`SKILL.md:28`). Wrong: "`knowledge/`, the knowledge base in which reviewed records accumulate". The knowledge is `canon/` (`reference/canon.md:9`); `knowledge/` holds "views the runner renders and the published judgments" (`reference/tools.md:17`). Missing: the root is also a Lean declaration named in `instance.json` (`reference/common.md:15`; `runtime/runner.py:189-191`), and the runner refuses to run if either form has changed (`reference/operations.md:165`).
- **README:34** — `gone`. There are no nodes; "No separate object. The **frontier** is a view derived from the root downward" (`design:43`), and every statement the research keeps is an element (`reference/common.md:103`). The definition of "settled" given here is `false` for the current system: settled now means an accepted proof whose named statements are all settled (`reference/common.md:166`), and it is not symmetric in a statement and its negation; a statement whose negation is settled is "refuted" (`reference/common.md:205`). The last sentence (the run is finished only when the root is settled at the formal level) is `true` for completion of the instance (`reference/common.md:170`), with the distinction of `SKILL.md:64` between completion and the runner finishing.
- **README:36** — `gone`. There are no relations and no admission. An implication is a statement whose proof names, in Lean, the statements it rests on (`design:44`; `reference/common.md:105`). A partial result enters as the settled part, the exact remainder as a statement without a proof, and a proof of the original that names both (`reference/common.md:255`). A conjectured implication can be kept too: a conjecture is a statement without a proof (`reference/common.md:91`).

### Lines 97-145

- **README:97** (heading) — `gone`.
- **README:99** — `gone`, except the last sentence, which is `partly`. No relation is applied "in every direction that propositional logic allows". Standing is computed forward along what proofs name (`reference/common.md:166`; `runtime/knowledge.py:289-300`). Refutation exists only where a settled proof establishes a statement Lean has confirmed to be the negation of another (`reference/common.md:205`); I found no rule that refutes a statement because something it implies was refuted **[inferred from `runtime/knowledge.py:302-332`]**; instead a proof that names a refuted statement "cannot become settled as it stands" (`reference/common.md:205`). The contested sentence is right in substance for a statement: both it and its negation carry settled proofs, it "counts as neither open nor finished until a later review locates the failure" (`reference/common.md:209`), and its lease is refused (`reference/common.md:259`).
- **README:101** — `gone`. No routes and no "necessary condition" (a search of the skill's `.md` files finds neither term in this sense). The frontier shows "only what some proof of the root reaches" (`reference/common.md:207`). Formalizers are launched for settled statements that the root, or a settled refutation of it, rests on (`reference/common.md:172`; `runtime/knowledge.py:443-469`).
- **README:103** (heading) — `true`.
- **README:105** — `partly`. "Beside its nodes" is `gone`; the frontier view lists the questions after the frontier (`reference/common.md:219`). The rest is `true` (`reference/common.md:180`, `182`, `221`, `267`). Missing: each question carries its understanding so far, and that of `q0` is the account of the whole problem that every session receives (`reference/common.md:223`, `225`).
- **README:107** — `partly`. "the way nodes do" is `gone`. A peer proposes a question in its candidate and review admits, declines or returns it for revision (`reference/common.md:227`; `runtime/check.py:302`). The operator sentence is `true` (`reference/common.md:227`; `reference/operations.md:442`; `runtime/knowledge.py:589-594`). "A question is resolved when a published record gives an account of it": now "when review judges that its understanding so far answers what its statement asks" (`reference/common.md:229`); `q0` is resolved only by the root's formal settlement (`reference/common.md:231`).
- **README:109** — `true`, with one correction of place: the description is in the common introduction that every role receives (`reference/common.md:27-29`), which I verified; I did not read the role guides. "the runner applies no such filter itself" agrees with what I read of the runtime **[inferred, `runtime/knowledge.py:133-136`]**.
- **README:111** (heading) — `true`.
- **README:113** — `partly`.
  - The five roles: `true` (`runtime/context.py:18-25`; `reference/common.md:35`).
  - "in the first run ... standing input from 8 November": `to be deleted`.
  - The essay's authorship: `true` as far as lines 1-40 say (the user and the operator, after reading all records of one investigation, `reference/what-research-is-for.md:7`). "under a previous implementation" and "the first run's problem": first-run material, and not stated in lines 1-40. "draws its examples from the history of mathematics rather than from that instance": **[not established]** from the lines I read; lines 5-37 describe that investigation's records at length.
  - The second document: `true` (`reference/user-writing-preferences.md:5-15`).
  - "meant to inform the sessions' judgment rather than to be followed as rules": `true` (`reference/user-writing-preferences.md:15`; `reference/common.md:43`).
  - "files in the skill's reference folder": `true` (`runtime/context.py:62-63`). A running session keeps the copy made at its launch (`runtime/context.py:60-61`).
- **README:115** (heading) — `true`.
- **README:117** — first half `partly`, second half `false`.
  - Formalizer: receives a settled statement the root rests on with its accepted proof (`reference/common.md:172`), not "a node". "filling gaps or changing strategy ... while the statement itself stays fixed", peer and review, continuation by another formalizer, no cap: `true` (`reference/common.md:172`, `174`; `SKILL.md:64`).
  - Organizer: `false`. It no longer groups records, writes surveys, selects shared context or decides a glossary. It "joins what is the same" by an element with a complete Lean proof, "rearranges modules", and "merges questions that ask the same thing"; it "writes no survey of the research and removes no element that nothing uses" (`reference/common.md:184`).
- **README:119** — `true`. Launch order (`reference/operations.md:485`), eight sessions and three minutes (`reference/operations.md:173`), one Lean broker per instance with memory and thread budgets (`SKILL.md:38`), results preserved (`reference/common.md:301`), no inherited instructions, hooks or memories and a saved starting context (`SKILL.md:42`; `runtime/context.py:136`). These are outside my area; I checked them only at the cited lines.
- **README:121** (heading) — `true`.
- **README:123** — `gone`. Claims and the statuses supported, unsupported, undetermined do not exist. Each element carries a verdict (`confirmed`, `not_confirmed`, `undetermined`, `not_applicable`, with a separate Boolean `accepted`; `runtime/check.py:15`, `265-274`), from which one of four standings follows (`reference/common.md:149-156`). The first sentence survives in a new form: "Publication ... does not certify every element it adds." (`reference/common.md:141`). "it counts a proof that includes computer-assisted steps as informal": `partly`; see README:137.
- **README:127** (row "Informal proof") — `partly`. An informal proof is written in the record while its Lean proof names what it rests on and ends in `sorry` (`reference/common.md:105`). "or the runner derived the statement through accepted relations": `gone`. The "does not mean" cell needs a qualification: Lean has checked the statement and the named dependencies, and not the argument (`reference/common.md:105`).
- **README:128** (row "Computer-assisted step") — `partly`. The requirement to state range, arithmetic, code and output stands (`reference/records.md:55`; `reference/writing.md:33`). The binary64 clause has no counterpart in the current guides **[not established]**. Missing: such a proof can be held back (`reference/common.md:147`).
- **README:129** (row "Formal proof") — `partly`. Formal means the Lean proof is complete and depends only on the allowed axioms through everything of the canon it uses (`reference/common.md:170`); review compiles the candidate itself and reads the axioms (`reference/common.md:174`), and where available the judge replays the proof through the kernel (`reference/lean.md:222`). "matched to the exact statement" and the whole "does not mean" cell about relations are `gone`. What a formal proof does not certify now: that the statement says what was meant (`reference/lean.md:226`).
- **README:131** (heading) — `true` as a heading.
- **README:133** — `gone`/`partly`. `informal_proved` is now a state of the root: settled, and not yet through a formal proof (`reference/common.md:209`). For other statements the corresponding condition is "settled" with no formal proof (`runtime/knowledge.py:536-537`). "An informal proof removes the node from the work that new attempts take up": only an accepted proof does, and a statement whose own proof is accepted but which is not settled can still be taken (`reference/common.md:168`); a held-back proof stays work that remains (`reference/common.md:164`). The last sentence (relations) is `gone`.
- **README:135** (heading) — `true` as a heading.
- **README:137** — `partly`. First sentence `true` (`reference/records.md:55`; `reference/writing.md:33`). The two kinds of arithmetic and "the reviews in the first run": first-run material and not in the current guides. "A finite verification proves the finite claim it covers and nothing beyond it": `true` (`reference/writing.md:33`; `reference/evidence.md:27`). "On the frontier, a proof with computer-assisted steps stands at the informal level": true when the computation is described in the record; a computation inside a complete Lean proof is formal if its axioms are allowed, and `native_decide` is not under the default list (`reference/lean.md:204`, `214`) **[inferred]**.
- **README:139** (heading) — `true` as a heading.
- **README:141** — `partly`. Review's own fresh compile through the broker and the reading of the axioms against the allowed list, with the stated default and `sorryAx` never allowed: `true` (`reference/lean.md:214`, `220`; `runtime/canon_tool.py:361-367`). "compares the theorem's statement with the node, object by object": `gone`; a statement is its own Lean declaration, review judges whether the Lean form says what the record says (`reference/common.md:121`), and for the root no comparison is made (`reference/lean.md:224`). Missing: the proof must also be accepted and rest on settled statements for the root to count as formally proved (`SKILL.md:64`), and the judge (`reference/lean.md:222`). Last sentence `true` (`reference/common.md:170`).
- **README:143** (heading) — `true`.
- **README:145** — `partly`. A concern is now "a reported challenge to the proof of an identified element" (`reference/common.md:287`), not to a claim. "A pending concern changes no status by itself": `true`. "the outcomes derived from it ... are marked as resting on a questioned claim": I found no such marking; the concern is shown in the element's view and listed in the frontier view (`reference/common.md:287`; `runtime/knowledge.py:334-337`). Comprehensive review and its three triggers: `true` with "statement" for "node" (`reference/common.md:287`). "A withdrawal removes every outcome derived through the claim": now the proof becomes "proof not confirmed" and every standing is computed again (`reference/common.md:289`).

### Lines 169-181

- **README:169**, **171** (headings) — `partly`: the directory that holds the knowledge is `canon/`.
- **README:173** — `false`. `knowledge/` is not the knowledge base (`reference/tools.md:17`). The entry point is `knowledge/frontier.md` (`SKILL.md:56`). `index.md` is a derived list of every element by module with weight, standing and self-description; it has no selected shared context, no module descriptions and no surveys (`runtime/knowledge.py:654-666`; `reference/operations.md:320`).
- **README:175** — `partly`. `frontier.md` exists but shows the root's state, the unsettled statements beneath the root with their proofs and standings, concerns and questions (`SKILL.md:56`); no nodes, relations or routes. The six state names apply to the root (`reference/common.md:209`). The questions sentence is `true` (`runtime/knowledge.py:579-615`). `glossary.md`: `gone` (`SKILL.md:58`). `board.md`: `true` (`runtime/knowledge.py:667-688`). `state.json`: exists (`reference/tools.md:17`), but its keys are those of topic 6 and it has no `proofs` object **[inferred]**.
- **README:177** — `partly`. `records/` under `knowledge/` is `gone`; the per-publication folder is `changes/<id>/` (`reference/operations.md:333`). `events/`, `organizations/`, `questions/`, `reviews/`: `true` (`runtime/runner.py:116`; `reference/operations.md:334`). The sentence on session conversations and working files staying in `sessions/`: `true` (`reference/common.md:137`; `runtime/runner.py:127`).
- **README:179** (heading), **181** — `gone`. No per-record directory exists. The nearest current objects: the record of an element, `canon/records/<Name>.md` (`reference/canon.md:14`); its Lean source under `canon/lean/` (`reference/canon.md:13`); evidence under `canon/evidence/<Name>/` (`reference/canon.md:17`); and the published change `knowledge/changes/<id>/` with `change.json`, `applied.json`, `assessment.json` and feedback, `provenance.json`, `verify.json` (`reference/operations.md:333`). Concerns and findings are still in the assessment of the review that raised them and collected in `knowledge/state.json` (`runtime/knowledge.py:159-160`, `187-190`).

---

## Part 3. What the README lacks

A search of the whole README for `canon`, `element`, `held back`, `traversal`, `Lean library`, `comparator`, `approaches tried` and `understanding so far` found none of them, so the following are absent from the whole file, not only from the ranges of Part 2. Items are ordered by how much a reader who evaluates or runs the system depends on them.

1. **The knowledge is a Lean library.** Canon, element, record, imported library; a result that is not an element does not exist for any other proof (`SKILL.md:10`; `reference/common.md:101-107`). The reasons from the earlier run (`reference/common.md:85-87`).
2. **The root is fixed in Lean with the user, and nothing later checks that it says what the user meant.** The user reads and confirms the Lean statement before `start` (`SKILL.md:22-28`; `reference/operations.md:148-165`); the value checks are evidence, not proof (`SKILL.md:24`); a wrong Lean statement needs a new instance (`SKILL.md:28`). This is the main limit a reader evaluating a result has to know.
3. **The two forms of proof and what Lean checks in each** (`reference/common.md:105`; `reference/canon.md:63-67`), including that an informal proof's dependencies are machine-checked while its argument is not.
4. **The four standings and the two judgments**, with "correct, held back" and the two acceptance considerations (`reference/common.md:145-164`; `reference/operations.md:261`).
5. **Settled against formal**: one is review's judgment, the other Lean's; the root needs both (`reference/common.md:166-170`; `SKILL.md:62-64`). Also refuted and "names refuted" (`reference/common.md:205`).
6. **What stands without review**: complete Lean proofs supplied at creation and the organizer's Lean-proved additions (`SKILL.md:40`; `reference/common.md:158`).
7. **The judge of formal proofs and the root judge**, and what their verdict rests on (`reference/lean.md:222`; `reference/operations.md:407-425`; `SKILL.md:66`).
8. **The statement invariant and the four publication rules**, with the reason of the frozen candidate (`reference/common.md:127`), and what can be replaced with its history (`reference/common.md:111`).
9. **No account per session; approaches tried and understanding so far**, with the reason that accounts keyed by session grow with the number of sessions while what is learned does not (`reference/common.md:131-137`).
10. **The frontier as a derived view that nobody writes and to which nothing is admitted** (`reference/common.md:188`, `211`), and the derived index (`SKILL.md:56`).
11. **Reading by traversal and the reading commands**, which the operator and a reader of a finished instance can run on the instance folder (`reference/common.md:237`; `reference/canon.md:77-96`; `reference/operations.md:336-346`).
12. **Weight: units and steps** (`reference/records.md:59-80`).
13. **The layout of `canon/` and of `knowledge/changes/<id>/`** (`reference/canon.md:11-22`; `reference/operations.md:322-334`).
14. **The structural index and the machine checks at publication** (`reference/common.md:113`; `reference/operations.md:465`).
15. **Results from the literature as elements that still need a Lean proof before completion** (`reference/literature.md:51`, `93`).
16. **The list of things nothing checks** (topic 17), in particular the traversal asked before taking on a statement (`reference/common.md:243`).
17. **The dependency map and the paper produced from the canon by command** (`SKILL.md:66`; `reference/operations.md:370-405`). This borders on another area; I read the section and cite it only for its existence.
18. **The runtime refuses instances of the earlier runtime** (`SKILL.md:82`; `reference/operations.md:451`), which matters to a reader who holds a published knowledge base of the old kind.

The README does mention English (`README:164`, `165`, `258`) and scholarly (`README:236`); I did not read those lines, so I do not list language or the literature server as absent.

---

## Part 4. What could not be established

### Questions the sources do not answer

1. **Floating-point computation.** No guide of the skill mentions binary64, floating point or interval arithmetic. How a proof resting on a binary64 computation with an assumed error model is to be classified is not stated; only the general rules of topic 11 apply.
2. **Whether the index revision advances on events that do not change the library** (topic 9). `runtime/runner.py` was read only in part.
3. **A defining sentence for "revision".** None in the guides I read; the account in topic 9 is assembled from code.
4. **Who can raise a concern.** In the code I read, concerns enter through the assessment of a candidate review or of a comprehensive review (`runtime/knowledge.py:159`, `189`) and through the automatic follow-up (`runtime/knowledge.py:108-111`). Whether a producing session or the operator can create one directly is not established; the operator's `review --concern <id>` names an existing concern (`reference/operations.md:440`).
5. **Whether elements resting on a questioned element are marked.** I found no such marking in `runtime/knowledge.py` or `runtime/canon_tool.py`; I did not read `runtime/coordination.py` or `runtime/runner.py` in full.
6. **Whether the essay draws its examples from the history of mathematics rather than from the earlier instance** (README:113). Lines 1-40 of the essay describe that instance's records; the rest was outside the range I was asked to read.
7. **The reason for English inside an instance.** Not given in the sources I read.
8. **How the three sub-reviews are organized.** `reference/tools.md:51` says the review role guide specifies them; I did not read `roles/review.md`.
9. **The exact format of review's assessment.** Known only through `runtime/check.py:248-329`; `reference/review-output.md` was not read.
10. **What the role guides say about progress** (README:109). Not read.

### Files read in full

`SKILL.md`; `reference/common.md`, `canon.md`, `records.md`, `evidence.md`, `literature.md`, `writing.md`, `tools.md`; `runtime/canon.py`, `canon_tool.py`, `knowledge.py`, `check.py`, `context.py`; `docs/do-math/lean-canon-design.md`.

### Files read in part

- `reference/what-research-is-for.md`, lines 1-40, and `reference/user-writing-preferences.md`, lines 1-40, as asked.
- `README.md`, lines 1-185; lines 186-262 only by keyword search.
- `reference/lean.md`, lines 200-228, opened because `reference/canon.md:67` points to it for the allowed axioms and review's check.
- `reference/operations.md`, lines 1-469 and 483-485, opened because `SKILL.md` points to it for the root, `init`, the reading of results, the judge and the commands.
- `runtime/runner.py`, lines 100-199, 606-635 and 796-809, plus keyword searches, for `init`, the event sequence and the index revision.

### Files not opened

`reference/change-format.md`, `review-output.md`, `sections.md`, `retained-work.md`, `organizer-output.md`, `paper-method.md`, `lean-broker.md`; everything under `roles/`; the other runtime modules; the tests. `C:\math\.agents\skills\do-math` and `docs/do-math/rebuild-design.md` were not used.

### Disagreements between the design record and the current guides or code

In each case the guide and code are the current system.

1. **Binding of a record and of a verdict to a statement hash.** Design: "A declaration and its record are bound by the name and by a hash of the statement ... A check before publication confirms that every element has both and that the hash agrees ... A verdict of review is bound to the hash it saw" (`design:93`). Current: a record has no hash key (`runtime/canon.py:32`); record and declaration correspond by name path (`runtime/canon.py:1047-1054`, `1071-1074`); the statement hash lives in the index and is compared before and after a change (`runtime/canon.py:1012`); the view prints the element's current hash beside the verdict (`runtime/canon_tool.py:133`). Guide: "A verdict belongs to the exact Lean statement it was written about" (`reference/common.md:160`). **[The reading that verdicts store no hash is inferred; `review-output.md` was not read.]**
2. **Where verdicts and approaches are kept.** Design lists "The verdicts of review and their reasons" and "the approaches tried" as contents of the record (`design:110-111`, `197`). Current: verdicts are in the published change's assessment and are joined at replay (`runtime/knowledge.py:116-124`); approaches are separate files under `canon/approaches/` (`reference/canon.md:15`).
3. **"Proof not confirmed".** Design: "review found a gap or could not complete its judgment" (`design:132`). Current adds "or has not judged it" (`reference/common.md:154`), with the rule for the first elements (`reference/common.md:158`). The operator's guide still gives the shorter wording (`reference/operations.md:348`).
4. **Contested.** Design: "A statement and its negation both carrying confirmed proofs" (`design:154`). Current: both carry settled proofs (`SKILL.md:60`; `runtime/knowledge.py:302-321`).
5. **Refuted.** The design has no "refuted" state or "names refuted" mark. Current: `reference/common.md:205`; `runtime/knowledge.py:328-332`.
6. **Replacing the proof of a settled statement.** Design: "The new proof is correct and accepted: it replaces the old one" with no exception (`design:148`). Current: a settled statement cannot be taken, and only two replacements remain (`reference/common.md:168`; `runtime/check.py:110-146`).
7. **Which proof a formalizer is given.** Design: among the proofs that settle the statement, "the first whose named statements are all settled by formal proofs" (`design:152`). Current: "the first that is not formal and whose named statements all have formal proofs", which includes a proof whose own Lean text is complete but not formal (`reference/operations.md:459`; `reference/common.md:172`; `runtime/knowledge.py:443-469`).
8. **The judge.** The design has no judge and says completion "no longer needs a separate judgment that a formal theorem corresponds to the root" (`design:76`). Current: every formal proof is judged before publication where the installation allows, and the settled root is judged against the first commit (`reference/lean.md:222`; `reference/operations.md:407-425`). The two do not contradict each other on meaning: the judge compares statements, not intent.
9. **The object direction of traversal.** Design: "Every declaration whose statement mentions a given definition" (`design:218`). Current: "every declaration whose statement mentions a given definition or whose proof uses it" (`reference/common.md:239`; `runtime/canon_tool.py:205-206`).
10. **Where review writes its judgment of a division.** Design: "into the record of that way" (`design:179`). Current: "in its reason" (`reference/common.md:213`).
11. **The printed form of the frontier and of the joined view.** Design shows "way 1 ... proof of the way" (`design:162-171`) and a seven-line view (`design:229-237`). Current forms: `reference/common.md:192-199` and `reference/canon.md:112-129`.
12. **`canon/records.json`** is not in the design; it exists (`reference/canon.md:21`; `runtime/knowledge.py:697-715`).
13. **Snapshot reuse in the broker** is adopted in the design (`design:347`). I did not check the broker; this is outside my area and is listed only so that the design is not cited for it without a check.

### Disagreements between a guide and the code, or between two guides

Both sides are reported; I do not choose.

1. **Kinds of element.** Guide: "an element has one of four kinds" — `theorem`, `def`, `opaque`, `inductive` (`reference/canon.md:32`). Code: `ENTRY_KINDS = ('theorem', 'def', 'opaque', 'axiom', 'inductive')` (`runtime/canon.py:38`). An `axiom` entry is refused when a candidate adds it and at `init` (`runtime/canon.py:1075-1076`; `reference/operations.md:54`), so a fifth kind should not persist in a published canon **[inferred]**.
2. **What the structural index holds.** Guide: for each declaration the index holds "what uses it in turn" and "the axioms its proof depends on" (`reference/common.md:113`). Code: an index entry stores `uses`, `statement_uses` and `direct_axioms` (`runtime/canon.py:790-797`); the reverse direction and the axioms through the canon are computed at replay (`runtime/knowledge.py:274-280`; `runtime/canon.py:832-880`).
3. **The number of derived views in `knowledge/`.** `reference/canon.md:26`: "Three derived views are in the folder `knowledge/`" (`frontier.md`, `index.md`, `board.md`). `reference/tools.md:17` and `runtime/knowledge.py:689-694` add `state.json`.
4. **The canon layout.** The docstring of `runtime/canon.py:9-18` omits `records.json`; `reference/canon.md:21` lists it and `runtime/runner.py:188` writes it there.
5. **The work that remains.** `reference/common.md:203` and the header of `frontier.md` (`runtime/knowledge.py:648-649`) say it is every line whose standing or proof is not accepted. `reference/canon.md:88` and the code (`runtime/knowledge.py:360-362`) add the lines whose proof names a statement refuted since and exclude refuted and settled statements. `reference/common.md:205` states the same addition in prose, so the difference is one of a short summary against the full rule.
6. **"This holds for those first elements alone"** (`reference/common.md:158`). In code the rule applies to any statement without a verdict (`runtime/knowledge.py:232-235`), and an organizer's retirement of an alternative proof that had no verdict removes the verdict of the statement's own declaration (`runtime/knowledge.py:177-183`). Whether that path can leave a later element without a verdict in practice I did not trace **[inferred from the code; not confirmed]**.
