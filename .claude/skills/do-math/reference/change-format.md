# The candidate change

A candidate change, called a candidate for short, is the change to the canon that a session proposes. The common introduction describes, under "Turning a session's work into the canon", who writes it, what it consists of, and how review and publication treat it.

This guide gives the form of a candidate. It first says what a candidate can and cannot do to the canon, since everything else follows from that. It then goes through the folder and its manifest part by part, describes the command with which you prepare the candidate before you end, shows one small candidate in full, and says what happens to the candidate after your session. The formats of a record, of an approach entry and of an understanding text are in [The written texts of the canon](records.md), and the conventions of the Lean files are in [The canon](canon.md); neither is repeated here. An organizer writes a candidate of a restricted kind, described at the end.

## What a candidate can do

The common introduction states the rule on which publication rests: the statement of an element is never changed in place. A candidate is accordingly made of additions and of replacements that leave every statement as it is.

- It **adds elements**: new modules of the library, and a record for every declaration in them.
- It **replaces the proof** of a statement of the canon, leaving the name and the statement as they are. Giving a first proof to a statement that stands without one is a replacement in this sense: what is replaced is the body `by sorry`.
- It **replaces written texts**: the record of an element, an approach entry, the understanding so far of a question. It also adds new approach entries.
- It **proposes** questions, and resolutions of existing questions.
- It adds files of evidence and entries of the bibliography.

A candidate cannot change the statement of an existing declaration, change an existing definition, remove a declaration, or add a declaration to an existing file. A statement that should read differently enters as a new declaration under a new name, as the section on superseding statements below describes. A definition that should be different enters as a new definition, together with a statement of how the two are related.

## The folder

The candidate is the `output/` folder of your session.

```text
output/
  change.json                  the manifest
  lean/<Library>/...           new modules
  replace/<file>.lean          the new text of a declaration whose proof is replaced
  records/<Name>.md            new records, and records that replace existing ones
  approaches/<Name>/<id>.md    new approach entries, and entries that replace existing ones
  questions/<question>.md      an understanding text that replaces the existing one
  evidence/<Name>/...          files that records refer to
  bibliography.bib             entries to add to the bibliography
  prepared.json                written by commands.prepare
```

The folders mirror the canon, so a file's place in the candidate is its place in the canon after publication. Of the files you write, only `change.json` is always present; a candidate that adds understanding and no Lean has no `lean/` folder. The folder may not contain filesystem links. Keep your working notes in `work/`, since `output/` is what gets frozen and judged.

## The manifest

`change.json` names what cannot be read from the layout of the folder.

```json
{
  "title": "A name for the contribution",
  "description": "What the change contributes and within which limits.",
  "replace": [
    {"declaration": "<name of the declaration>", "file": "replace/<file>.lean", "imports": ["<module>"]}
  ],
  "questions": [
    {"id": "<your session ID>-<label>", "statement": "What is to be understood.", "grounds": "Why it is asked."}
  ],
  "resolutions": [
    {"id": "<label>", "question": "<question ID>"}
  ]
}
```

`title` and `description` are required and nonempty. The description says what the change contributes to the research and where its limits are; the log of published changes shows it beside review's assessment. `replace`, `questions` and `resolutions` are arrays and may be omitted when empty. Any other key is rejected.

## New elements

A new module is a file under `lean/`, at the path its module name gives: `lean/Small/Step.lean` is the module `Small.Step`. A path that already exists in the canon is refused, because no existing file is edited to add a declaration. The module is written by the Lean conventions of [The canon](canon.md).

Every declaration a new module adds needs a record at `records/<Name>.md`, in the record format of [The written texts of the canon](records.md).

## Replacing a proof

A replacement is an entry of `replace` and a file.

- `declaration` is the full name of the declaration.
- `file` is the path, inside the candidate, of a file that holds the whole declaration as it should stand: the doc comment, any attributes, and `theorem <name> <statement> := <proof>`. It holds this one declaration and not the module around it. The runner puts the text where the declaration stands in its module, so write the name as that module writes it, inside the namespace that is open there. `view <element> --part source` prints the present text to start from.
- `imports` lists modules to add to the header of the declaration's module, for the case where the new proof names statements from modules that module does not yet import. It may be omitted.

Four conditions hold for a replacement. The statement is unchanged, down to the names of its bound variables: the check compares the statement as Lean prints it, so start from the text that `view <element> --part source` gives and change the proof only. The declaration is a theorem; a definition is never replaced. Your pipeline holds a section on the statement, the whole of it or a part, registered by the producing session or by you through the element's lease; a settled statement can no longer be taken, and the section on superseding statements below says when its proof can be replaced without one. And the added imports create no cycle: a module that imports the declaration's own module, directly or through others, cannot be imported by it.

A proof always enters through an entry of `replace`, because the elements review judges are those the candidate adds and those it names there. This holds also for an argument that names no statement of the canon: the declaration's text is then the one the canon already has, and the entry is what puts the new proof before review.

A new proof is usually accompanied by two written files. The first is the record of the element, as a replacing record whose `## Proof` part is the new argument; the record in the canon still describes the old proof. The second is an approach entry for the statement that describes the approach this proof takes. The reason for the entry is what review may decide. Review says, for each proof a candidate would replace, whether the new proof takes the place of the proof the canon has. If it does not, the runner leaves the declaration and its record as they are, and the approach entry is then where what was tried remains.

Two sessions can hold parts of one statement, and both may bring a new proof of it. A replacement is therefore tied to the text of the proof it was written against; the preparation records that text's identity for you. If another publication replaces the proof before your candidate's turn comes, the runner does not put your proof over the other one.

## Another proof of a statement, and a refutation

Sometimes a proof cannot stand where the statement's declaration is. The new proof may rest on modules that import the statement's own module, for instance theory built later on top of the statement by another route, and the imports would then form a cycle. And sometimes a second derivation of a statement is worth keeping beside the first, because the two rest on different pieces and both are routes the research may complete. In both cases the proof enters as a new declaration, in a new module and under a new name, whose statement is the same as that of the existing statement and whose record says so in its header:

```markdown
---
weight: unit
short: unimodality from the diagonal statement
proves: Parking.unimodal
---
```

`proves` names the declaration that carries the statement itself. Lean has to confirm that the two statements are the same proposition, up to the names of bound variables. A statement that is only proved equivalent to another remains a different element. The simplest way to meet this is to copy the binders and the type from the source of the existing declaration. What follows for a statement with several proofs is in the common introduction: that the frontier shows all of them, under "Seeing what remains: the frontier"; that the statement is settled as soon as one of them is, under "The standing of a statement"; that its sections and lease stay with the declaration that carries the statement, under "Seeing work that is still underway: the board"; and that the organizer can later move such a proof under the statement's own name, under "Other work that advances the research".

Which of the two forms a proof takes follows from the state of the statement. A statement whose own declaration has no proof receives its first proof by a replacement. A proof that improves on one that is not accepted replaces it. A statement that is settled cannot be taken on through its lease, so a further proof of it, whether a simpler one or a different route, enters as a declaration with `proves`. The same form suits a different route to a statement whose own proof is accepted and not yet settled, when both routes should stay in view: the frontier then shows the statement with both proofs. Adding such a declaration requires no section; only a replacement does.

A proof that a statement is false enters in a similar way, as a declaration whose statement is the negation of that statement and whose record has `refutes` with the name of the statement. Lean has to confirm that the new statement is exactly the negation of the whole of the other: for `theorem root (n : Nat) : P n`, whose statement is `∀ n : Nat, P n`, it is `¬ ∀ n : Nat, P n`. An equivalent form, such as the existence of a counterexample, is a different statement. State that form as an element of its own where it is the natural one, and derive the negation from it. When a declaration with `refutes` is settled, the statement it names is refuted, with the consequences the common introduction gives under "Seeing what remains: the frontier".

## A statement that supersedes another

Work on a statement sometimes shows that a different statement is the right one: a hypothesis turns out to be unnecessary, the range can be widened, the conclusion can be strengthened. The new statement enters as a new declaration under a new name, in a new module, with its record. The old element keeps its name and its statement. Its proof is replaced, by a replacement as described above, with a complete Lean proof of one line that derives it from the new statement. Whatever rested on the old element still compiles and now rests, through it, on the new one.

When the old statement is settled, the order matters. A statement that is not yet settled is not a better statement than a settled one: deriving the settled statement from it would make an established result depend on one that is not established. So your candidate adds the new statement and leaves the proof of the old one as it is. Once the new statement is settled, the derivation can replace the old proof, in a later candidate of any peer. No section is needed for that replacement, since a settled statement can no longer be taken. `commands.prepare` and the transport check accept it when the old statement stays settled under the new proof: the proof is complete in Lean, every statement it names is settled, and where the old proof made the statement formal, the new proof is formal as well. Review then confirms and accepts the derivation, or leaves the old proof in place. The old proof goes to the history, as with every replacement.

When the new declaration's module imports the module of the old element, the one-line derivation cannot be put in place for the reason given in the previous section. It then enters as a new declaration with `proves` naming the old statement.

## Written texts

**Records.** A record in the candidate either belongs to a declaration the candidate adds or replaces the record of a declaration of the canon. A replacing record is the complete new text, not a list of edits; the canon keeps the difference in the element's history. A record can be replaced without an entry of `replace`, for example to correct an explanation or a weight, and this requires no section. A record that gives a statement a proof or changes its proof, or that adds, changes or removes `proves` or `refutes` in its header, comes together with an entry of `replace`, as the section on replacing a proof says. These parts decide the element's standing, and review judges only the elements a candidate adds and those it names in `replace`, so the preparation refuses such a record for a declaration the candidate does not list there.

**Approach entries.** An entry is at `approaches/<Name>/<id>.md`, where `<Name>` follows the name of the statement the approach was aimed at. That statement is an element of the canon or one the candidate adds. A new approach is a new entry with an identifier you choose. An approach that the work carried further replaces its existing entry: use the same identifier, write the complete new text, and add the producing session and yourself to `sessions`. Leave out the `## Review` part of the entry you are replacing, since the runner writes that part at publication.

**The understanding so far.** `questions/<question>.md` replaces the understanding text of an existing question, named by its identifier. The peer of an exploration writes it for the question the exploration held, which the assignment names. Start from the current text, which `commands.canon` with `question <question>` prints, and write the complete text that should stand afterwards: what was understood before and still holds, and what was newly understood. Review reads your text against the one it replaces, including what yours removed, so a qualification of the old text that you drop should be one you mean to drop.

**Evidence.** Files that a record refers to, such as the code, the input and the output of a computation, go under `evidence/<Name>/`, where `<Name>` follows the name of the element whose record uses them. Refer to such a file in the record by its path from the root of the canon, for example `evidence/Small/root/table.csv`.

**Bibliography.** `bibliography.bib` holds BibTeX entries to add to the canon's bibliography. An entry whose key the bibliography already has is not added again, and the existing entry stays; to cite a source the canon already lists, use its key in the record's `source`. [Literature](literature.md) says what an entry and the record of a cited result should carry.

## Questions and resolutions

A proposed question is an entry of `questions` with exactly three fields. `id` is your peer session ID, a hyphen and a short label of letters, digits, `_` and `-`; the prefix keeps the proposals of concurrent peers apart, and the identifier may not be one that a question already has. `statement` says what is to be understood, and `grounds` says what raises the question and why it matters. Your role guide explains when work has brought a question into view and how exactly it has to be stated; review decides whether to admit it.

A resolution is an entry of `resolutions`. It asserts that the understanding so far of an existing question now settles what the question asks. It has an `id`, a label of your choosing that is unique within the candidate, and `question`, the identifier of the question. A candidate with a resolution carries the text that settles the question, as `questions/<question>.md`. When the answer leaves something to be done, the same candidate carries that as well, as statements or as a proposed question; your role guide explains this. Question `q0`, the root problem as a whole, cannot be resolved this way; the common introduction explains how it is resolved.

## Preparing the candidate

Before you end, have the candidate applied to the canon and compiled. `commands.prepare` in your `input.json` is the complete argument array for this; two options can be appended, `--expect-mb <MiB>`, your estimate of the peak memory of one module compile as [Lean](lean.md) explains it, and `--timeout <seconds>`, which is 50 when omitted. The command is for a peer and for an organizer that submits a change, and it refuses every other role.

The command reads the manifest and the files, applies the candidate to a copy of the current library in your `work/` folder, compiles the result through the Lean broker, extracts the structural index of the modules that changed and of every module that imports one of them, and checks what a machine can decide:

- the library compiles with the candidate applied;
- no statement of an existing declaration changed, and no existing declaration changed other than the ones the manifest replaces. A statement can change although its text did not: Lean reads a declaration in the environment its module imports, so an instance or a notation that your change brings into the scope of an existing module can make an unchanged statement elaborate differently. The check reports such a statement by name, and the remedy is to keep what you add out of that scope, for instance by declaring an instance `local` or `scoped`, or by not importing the new module there;
- no declaration disappeared;
- every declaration the candidate adds has a record, and every record belongs to a declaration;
- every declaration the candidate adds stands in a new module, and no name it adds differs from another name of the canon only in the case of its letters, since the records of two such names would be one file where the file system ignores case;
- no declaration is an `axiom`, whether it is an element or a private declaration beside one, no definition contains `sorry`, and no replacement touches a definition;
- for every record with `proves` or `refutes`, Lean confirmed that the statement is the same as, or the negation of, the statement named.

It then writes `output/prepared.json` and prints a summary: `ok`, the build's ID, the elements `added` and the proofs `replaced`, the records, the `errors`, and for each statement the axioms it depends on. The command exits with 0 when the candidate is in order and with 1 when it is not; read `errors`, correct the candidate and run the command again. A compiler error is reported with Lean's own output. The exit code 124, with `"waiting": true`, means that the build has not finished within the timeout. The build continues, and running the same command again returns its result; it is started afresh only when the candidate or the canon has changed in the meantime.

`added` and `replaced` are exactly the elements review will judge, one verdict each, so read the two lists as a check on your own intention. A declaration you meant to add and do not find there was not picked up as an element, for example because it is private.

`prepared.json` is a receipt for the files the command saw. You do not write or edit it, and it is valid only for those files: after any change to the candidate, including a file added or removed, prepare again. The transport check, `commands.check`, refuses a candidate that was not prepared, that changed after it was prepared, or whose preparation reported errors. For a peer it also confirms that the manifest and the written files are well formed, that every replaced declaration is one your pipeline holds a section on, that approach folders follow the names of elements and understanding files the identifiers of questions, and that the identifiers of proposals carry your session prefix. Neither command judges mathematics.

The canon may change between your preparation and publication. Preparation is made against the canon as it is when you run it, and the runner builds the candidate again on the canon as it is when the candidate's turn comes.

### The builds that `commands.prepare` and `commands.verify` make

Review compiles a candidate with `commands.verify`, which [Review output](review-output.md) describes, and the two commands build in the same way apart from which modules they compile. Each applies the candidate to a fresh copy of the canon as it is at that moment and, when the candidate changes any Lean source, queues one build through the broker. The build waits in the same queue and counts against the same budgets as your other compiles. `commands.prepare` builds every module of the canon with the candidate applied. `commands.verify` builds the modules the candidate changed, with fresh targets, so the reviewing session compiles them itself and takes from the cache only what they import. Both add one further compile to the build. It extracts from the compiled modules the entries of the structural index, the machine-made table of the canon's declarations that the canon command reads from: for each declaration its statement, what it uses and the axioms it depends on. That compile appears in the build's summary as the module `DoMathExtract`. It imports the Lean metaprogramming library, the changed modules and the modules that import them, as a plain file, since it has to read their proofs.

That compile is often the largest compile of the build, which is the one the estimate given with `--expect-mb` is for. It imports the Lean metaprogramming library, which on Windows is a commit charge of about 2 GB before anything else. It was measured at about 10 seconds on an idle machine and at about a minute on a loaded one. It imports those modules as a plain file, so it is compiled again whenever one of those modules, or anything they reach, came out different in any way from the last time. Without `--expect-mb` the commands use the instance's `calibration_expect_mb` setting. [Lean](lean.md) explains under "Estimating what a compile will need" how to arrive at an estimate.

## A small candidate

This example shows the form of a candidate on mathematics small enough to read at a glance. The instance's library is `Small`. The canon holds the definition `Small.oddSum`, the sum of the first n odd numbers, and the root `Small.root`, which states that this sum equals n times n and has no proof. An attempt registered the whole root and found a proof by induction. Its peer writes this candidate:

```text
output/
  change.json
  lean/Small/Step.lean
  replace/root.lean
  records/Small/oddSum_succ.md
  records/Small/root.md
  approaches/Small/root/induction.md
```

`change.json`:

```json
{
  "title": "The sum of the first n odd numbers by induction",
  "description": "States the passage from n to n + 1 as an element with a complete Lean proof, and gives the root a proof by induction that rests on it. The arithmetic of the inductive step is written in the record and is not yet carried out in Lean.",
  "replace": [{"declaration": "Small.root", "file": "replace/root.lean", "imports": ["Small.Step"]}]
}
```

`lean/Small/Step.lean`, a new module with one new statement and its complete proof:

```lean
module

public import Small.Defs

@[expose] public section

namespace Small

/-- Adding the next odd number. -/
theorem oddSum_succ (n : Nat) : oddSum (n + 1) = oddSum n + (2 * n + 1) := by
  rfl

end Small
```

`replace/root.lean`, the root's declaration with an informal proof that names what it rests on. The statement is the one the canon has:

```lean
/-- The sum of the first `n` odd numbers is the square of `n`. -/
theorem root (n : Nat) : oddSum n = n * n := by
  have step := oddSum_succ
  sorry
```

`records/Small/oddSum_succ.md`:

```markdown
---
weight: step
short: next odd number
---
## Description

Passing from n to n + 1 adds the odd number 2n + 1 to the sum of the first n odd numbers.

## Statement

For every natural number $n$, the sum of the first $n + 1$ odd numbers is the sum of the first $n$ plus $2n + 1$.
```

`records/Small/root.md`, which replaces the root's record and now carries the proof:

```markdown
---
weight: unit
short: odd numbers sum to a square
---
## Description

The sum of the first n odd numbers equals n times n.

## Statement

For every natural number $n$, $1 + 3 + \dots + (2n - 1) = n^2$.

## Proof

By induction on $n$. For $n = 0$ the sum is empty and both sides are $0$. Suppose the sum of the first $k$ odd numbers is $k^2$. By `Small.oddSum_succ` the sum of the first $k + 1$ is $k^2 + (2k + 1) = (k + 1)^2$.
```

`approaches/Small/root/induction.md`:

```markdown
---
title: Induction on the number of terms
sessions: <ID of the producing session>, <your session ID>
---
## Idea

Compare the sum for n + 1 with the sum for n.

## Established

`Small.oddSum_succ`

## Where it stops

The argument is complete on paper. The identity $k^2 + (2k + 1) = (k + 1)^2$ of the inductive step has not been checked in Lean.
```

`commands.prepare` then prints a summary of this kind:

```json
{
  "ok": true,
  "build": "b3f0…",
  "added": ["Small.oddSum_succ"],
  "replaced": ["Small.root"],
  "records": ["Small.oddSum_succ", "Small.root"],
  "errors": [],
  "axioms": {"Small.oddSum_succ": [], "Small.root": ["sorryAx"]}
}
```

Review will judge two elements. For `Small.oddSum_succ` it judges the statement and its Lean proof. For `Small.root` it judges the proof in the record, and says whether that proof takes the place of what the canon had. If both proofs are confirmed and accepted, the root is settled. It is not yet formal, because its Lean proof ends in `sorry`, and since the one statement its proof names has a formal proof, a formalizer is launched for it.

## After your session

When your session has ended, the runner copies `output/` to a fixed place, records the identity of every file, and gives that copy and the producing originals to a fresh reviewer. The candidate is then frozen; nothing in it changes during review. Review writes its assessment in its own folder, and for a proof that is complete in Lean it compiles the candidate itself.

At publication the runner applies the candidate to the canon as it then is, leaving out the replacements that review declined, compiles the library and runs the same checks as the preparation. What happens when the candidate cannot be applied or does not build is described in the common introduction under "Turning a session's work into the canon".

## An organizer's candidate

An organizer's output can contain a candidate of the same layout. It holds Lean modules, replacements and records only: no approach entries, understanding texts, questions or resolutions. The elements it adds state that two definitions or two statements agree, or derive a statement from another that agrees with it, and have complete Lean proofs from the allowed axioms, which the preparation checks; they enter without review. An organizer has two further means that a peer does not, the rearrangement of existing modules and the retirement of a declaration with `proves` whose proof has been moved under the statement's own name. [Organizer output](organizer-output.md) describes these and the organizer's own manifest.
