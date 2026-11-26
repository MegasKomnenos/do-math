# The canon: reading it and writing in it

The common introduction explains what the canon is. This guide gives what every session needs in order to work with it.

The formats of the written files, namely the record, the approach entry and the understanding text, and the criteria for the weight of an element are in [The written texts of the canon](records.md).

## Where the canon is

The canon is the folder `canon/` of the instance directory, whose path is the `instance` value of your `input.json`.

```text
canon/
  lean/                       the module root of the library; every module is under <Library>/
  records/<Name>.md           the record of a declaration
  approaches/<Name>/<id>.md   the approaches tried on a statement whose proof is not accepted
  questions/<question>.md     the understanding so far of a question
  evidence/<Name>/...         files a record refers to, such as code, data and outputs of a computation
  history/<Name>/...          what a replacement left behind
  bibliography.bib            the sources of the results taken from the literature
  index.json                  the structural index
  records.json                a summary of the record headers
```

`<Name>` is a path that follows the name of the declaration: the declaration `Parking.Columns.dq_col` has the record `records/Parking/Columns/dq_col.md`. A component of a name that Windows cannot hold as a file name is encoded: a reserved device name such as `Aux` gets a trailing `%`, and a forbidden character becomes `%` followed by its two-digit hexadecimal code.

Three derived views are in the folder `knowledge/` of the instance: `frontier.md`, the frontier followed by the pending concerns and the questions; `index.md`, the self-description of every record in the order of the Lean structure, each with its current standing; and `board.md`, the work underway. The runner renders them. The folder also holds `state.json`, the same state in structured form, and the published judgments: `changes/<id>/` holds one published change with review's assessment and feedback, `reviews/<id>/` a comprehensive review, `organizations/<id>/` an organizer's output, and `questions/<id>/` questions the operator placed. Your starting context carries the frontier and the board as they stood at your launch. The `frontier` command below returns the frontier as it is now, the files can be read at any time, and `commands.updates`, which [Tools and working files](tools.md) describes, returns the current board, the questions and the concerns.

You read all of these files and write none of them. The commands below are the way to read the canon, because a view joins what Lean knows of an element with what its record says and a traversal returns the whole of what its rule selects. A session changes the canon only through a candidate, which a peer or an organizer assembles in its own `output/` and the runner applies at publication. `index.json` and `records.json` are made by machine at each publication. The history is kept apart from the other folders so that a text search of `records/` or `lean/` returns the canon as it is and not the texts that were replaced.

## Elements

In the views an element has one of four kinds. A `theorem` is a statement, and only statements have a standing. A `def`, an `opaque` and an `inductive` are definitions; a `structure` is shown as an `inductive`, and an `abbrev` or an `instance` as a `def`. An instance needs a record like any other definition, so give it a name of your choosing instead of leaving Lean to generate one.

Some declarations of the library are not elements and need no record: a declaration marked `private`, and everything Lean generates for a declaration an author wrote, such as the fields and the constructor of a structure, the constructors of an inductive type, equation lemmas and auxiliary proofs. What they use counts as used by the element they belong to, so a proof that reaches a statement through a private helper is recorded as resting on that statement.

## Lean conventions of the canon's files

Every file of the library follows one form.

```lean
module

public import Tri.Defs

@[expose] public section

namespace Tri

/-- Twice the n-th triangular number is n (n + 1). -/
theorem two_mul_tri (n : Nat) : 2 * tri n = n * (n + 1) := by
  have step := tri_succ n
  sorry

end Tri
```

The file begins with `module`: the library is written in Lean's module system. In a module the statement of a theorem is part of what an importing file reads, and its proof is not. This is what allows a proof to be replaced later while the files that import the module are, in the favourable case, not compiled again. Imports are written `public import`, so that a file importing yours also sees what your statements refer to. The declarations stand under `@[expose] public section`, which makes them visible to importing files and lets those files unfold the bodies of your definitions.

All modules of an instance are under one top-level name, the library, which `instance.json` in the instance directory gives; the file `lean/Tri/Closed.lean` is the module `Tri.Closed`. The operator placed the definitions of the root's objects in one module and the statement of the root in a module of its own that imports it. Later modules import the definitions and not the root, so a later proof of the root can import them without a cycle.

A new element is added in a new module file. No existing file is edited to add a declaration, and a candidate whose new module has a path that already exists in the canon is refused. One new module may hold several declarations. The folder you choose for a module is how the dependency map groups its units, so choose it by the part of the mathematics the module belongs to, where a reader of the library would look for it. Lean rejects a second declaration of a name, and of two candidates that introduce the same name only the first can be published as it is, so give a declaration a name that says what it states, as Mathlib does, and avoid names such as `aux` or `lemma1` that another session is likely to choose as well.

A statement is a `theorem`, and its proof takes one of three forms.

- A statement without a proof has the body `by sorry`.
- An informal proof names in Lean what it rests on and ends in `sorry`, as in the example above. Each statement the argument uses is named in a line of the plain form `have h := name arguments`, with the arguments given where the argument applies the statement to particular objects. Lean rejects a name that does not exist and arguments that do not fit, and the structural index reads these names as what the proof rests on. Use this plain form and no tactic of your own that wraps it: a wrapper written for the purpose lost the references when Lean simplified the proof term. The argument itself is the `## Proof` part of the record.
- A complete proof is any Lean proof without `sorry`. It may depend only on the axioms the instance allows; [Lean](lean.md) explains which those are and how review checks them.

Whichever form a proof takes, name in it the statements the argument uses, and those only. A statement that the argument uses and the Lean proof does not name is invisible to everyone who later asks what the result rests on, and a statement that is named and not used makes the result depend on it for nothing. Where a statement has several proofs under several declarations, it does not matter for whether your result is settled which of them you name, since a statement is settled as soon as one of its proofs is. It does matter for whether your proof is formal: a declaration whose own Lean proof ends in `sorry` brings `sorryAx` into every proof that names it, although its statement may have a formal proof under another declaration.

Three things are refused. An `axiom` declaration is refused: what you want to assume is stated as a `theorem` whose proof is left open, and the frontier then shows it as work that remains. A definition whose body contains `sorry` is refused, because every statement that used it would be about an unknown object. And a `theorem` whose statement is not a proposition is refused.

Keep prose out of the Lean source apart from a short doc comment: a module is compiled again whenever its source changes in any byte, prose included.

## Reading the canon: the commands

The canon is read with one command, `commands.canon` in your `input.json`. It is an argument array whose third element is the placeholder `<command>` and whose last element is your session directory. Replace the placeholder with the name of one of the commands of the table below, and append what the table writes after that name, the command's arguments, after the last element of the array: they follow the session directory and do not stand before it. With `python` for the interpreter and `<canon tool>` for the script, which are the first two elements of the array, the full view of an element is

```text
python <canon tool> view <session directory> Tri.two_mul_tri --full
```

An element is named by its declaration name as the canon shows it, as `Tri.two_mul_tri` is above. The output is text. An error, for instance that no element has the name given, is reported as a JSON object with the key `error` and exit code 1.

| Command and arguments | What it returns |
|---|---|
| `frontier` | The state of the root and the frontier as it is now, in the form the common introduction shows under "Seeing what remains: the frontier". The contested statements and the concerns not yet cleared follow, then the number of the frontier's elements that are work that remains, and then the questions: each open question with its statement, its state and its source, each resolved question as one line that says what resolved it, and the number of proposals review did not admit. |
| `view <element>` | One element as one view, described in the next section. |
| `view <element> --full` | The same, followed by every part of the record and by the approach entries in full. |
| `view <element> --part <part>` | One part alone. `statement`, `explanation`, `proof` and `literature` are the parts of the record. `approaches` gives the approach entries in full, with review's assessment of each. `history` gives what replacements left behind: the Lean text of each proof that was replaced, the earlier texts of the record and of approach entries, each as its difference from the text that took its place, and the approach entries that were set aside when a proof of the statement was accepted. `source` gives the Lean text of the declaration. |
| `list` | Every element of the canon. |
| `list --module <module>` | The elements of the named module and of every module under it: `Tri.Bounds` returns the elements of `Tri.Bounds` and of `Tri.Bounds.Upper`. The name is matched by whole components, so `Tri.Bound` returns the elements of neither. |
| `list --uses <element>` | The elements that the proof of the given statement names; for a definition, the elements its body uses. |
| `list --used-by <element>` | The elements whose proofs name the given element. |
| `list --about <element>` | Every element whose statement mentions the given element or whose proof uses it. For a definition, this is what the canon states about that object. |
| `list --remaining` | The work that remains for the root: the elements of the frontier whose standing is not "accepted", and those whose proof names a statement that has since been refuted. A refuted statement is not among them. |
| `question <question>` | A question: its state, its statement and grounds, its understanding so far, and review's assessment of the work that wrote it. With `--history` it adds the earlier texts of the understanding, each as its difference from the text that replaced it. |
| `questions --resolved` | The resolved questions, each with its statement, its source and what resolved it. |
| `questions --proposals` | The proposals of questions that review did not admit: for each its statement, review's verdict, which is `revise` or `declined`, the reason review gave and the change that proposed it. |
| `log` | The most recent changes published through a review, twenty unless `--last <number>` says otherwise: for each its title and description, review's assessment of what it contributed, the elements it added and the proofs it replaced. |

A `list` takes at most one of the selectors `--module`, `--uses`, `--used-by`, `--about` and `--remaining`. With `--uses` or `--used-by`, the option `--deep` follows the use all the way, so `list --uses <element> --deep` returns everything the statement rests on within the canon, at any depth. The option `--units` restricts any list to the units.

A list returns one line for each element it selects and ends with the count. The lines come in a fixed order, by name, or in the order in which the elements are reached from the starting element, so the same command on the same canon returns the same lines. These commands start no Lean process. They read the structural index and the records, which describe the canon as of its latest publication.

The same array has one further command, `checkout <folder>`, which copies the library, `canon/lean`, for your own Lean work; [Lean](lean.md) describes it under "Building against the canon and your own modules".

The commands correspond to the directions of traversal that the common introduction names. Containment is `list --module`. Use is `list --uses` and `list --used-by`, and the view of an element shows one step of each. Object is `list --about` with a definition. Standing is `frontier` and `list --remaining`.

## What the views show

A view that passes over many elements gives one line for each:

```text
Tri.two_mul_tri · theorem · unit · correct, held back — Twice the n-th triangular number equals n (n + 1).
```

The line holds the name, the kind, the weight, the standing and the self-description. A definition has no standing, and its line goes from the weight to the self-description. A declaration that is another proof of a statement says so after its standing, with the name of that statement.

The view of one element begins with that line and continues as follows. The values here are invented.

```text
Lean          Tri.two_mul_tri (n : Nat) : 2 * Tri.tri n = n * (n + 1)
source        canon/lean/Tri/Closed.lean, lines 9-12
short name    closed form of the triangular numbers
proof         written in the record; its Lean proof ends in sorry
rests on      Tri.tri_succ (accepted, settled, formal)
settled       no
objects       Tri.tri
used by       Tri.tri_even (no proof)
library       Nat.mul_add, Nat.add_comm
axioms        sorryAx
verdict       for statement 7350…-9914…: confirmed, not accepted (c41d…)
              The induction is correct. The polynomial identity is derived twice, in the base case and again in the step.
held by       s4e6ac5ea8ad04389a3d9d44ec7877dc5 (attempt, producing): the whole element
approach      induction: Induction on the number of terms — stops: The inductive step needs ...

record parts  statement, explanation, proof, approaches (read one with --part, all with --full; --part source prints the Lean text)
```

| Line | What it says | Where it comes from |
|---|---|---|
| `Lean` | The statement as Lean prints it. | The compiled library. |
| `source` | The file and lines of the declaration. | The compiled library. |
| `proof` | For a statement: `complete in Lean`, `written in the record; its Lean proof ends in sorry`, or `none`. | The compiled library and the record. |
| `rests on` | The statements the proof names, with the current standing, settlement and formality of each named declaration. | The compiled library and the published judgments. |
| `settled` | Whether this proof is settled. Where the proof is formal, the line adds that it is proved in Lean from the allowed axioms. | Computed. |
| `proofs` | Shown when the statement has several proofs: all of them, each with its standing. | The records. |
| `objects` | The definitions of the canon that the statement or the proof uses. | The compiled library. |
| `used by` | The elements whose proofs name this one, each with its standing. | The compiled library. |
| `stated with` | For an element that statements mention: how many do, and the command that lists them. | The compiled library. |
| `library` | Theorems of the imported library that the declaration uses, the first twelve and the number of the rest. | The compiled library. |
| `axioms` | The axioms the proof depends on through everything it uses, as Lean reported them for the declaration; it is the list that `#print axioms` prints. `sorryAx` means that this proof, or a proof it rests on, ends in `sorry`. | The compiled library. |
| `verdict` | Review's judgment: of which Lean statement it was made, whether the proof was confirmed, whether it was accepted, the change or later review that carried the judgment, and the reason. | Review. |
| `contested` | Shown when this statement and its negation both carry settled proofs. Nothing rests on either of the two until a comprehensive review has located the failure. | Computed. |
| `refuted by` | Shown when a settled proof establishes the negation of this statement: the elements that carry that proof. No work on a refuted statement remains. | Computed. |
| `names refuted` | Shown when the proof of this element names a statement that has since been refuted. The proof cannot become settled as it stands, and the statement needs another one. | Computed. |
| `questions` | The questions whose statement, grounds or understanding so far name this element between backticks. | The questions. |
| `concern`, `later review` | Each concern about the element with its status, and each finding of a later review. | Review. |
| `held by` | One line for each section a session holds on the statement: the session, its role and stage, and whether the section is the whole element, an exact part, or a new statement aimed at it. | The board. |
| `approach` | One line for each approach tried: its identifier, its title, and the beginning of where it stops. | The approach entries. |
| `record parts` | Which parts the record has, and how to read them. | The record. |

In the `verdict` line the first word is review's judgment of correctness: `confirmed`, `not_confirmed`, `undetermined` when review could not complete the judgment, or `not_applicable` for a definition or a statement without a proof, where the reason carries what review judged of the definition or of the statement itself.

The view of a definition has no `proof`, `rests on` or `settled` line. It shows the Lean text of the definition instead, since the body of a definition is what the definition says.

The Lean source of a statement is opened in two situations. One is to read or change the body of a formal proof; `view <element> --part source` prints it, and the `source` line gives the file. The other is a judgment of fidelity that needs more than the printed statement, for example what an implicit argument that the printed form omits is, or what a notation stands for. That judgment belongs above all to review, and it may need a compile.

## Occasions for reading

**When you take something on.** Read the element in full with `view <element> --full`: its Lean statement, what its record says of it, review's verdict and reason, and the approaches tried. Then, for each definition on its `objects` line, run `list --about` with that definition. This is the reading the common introduction asks for: it shows you whether a piece you were about to build is already there, and under which name. `list --uses <element> --deep` shows what the statement already rests on, and `list --used-by <element>` what depends on it. For a question, `question <question>` gives the grounds on which it was asked and the understanding so far.

**When you need a tool or a lemma.** A lemma about an object is found from the object: `list --about` with its definition. A part of the mathematics is found from its modules: `list --module` with a prefix. These commands cover the instance's own library. The imported library, Mathlib and the toolchain, is searched by its own means and is used directly, without an element; [Lean](lean.md) opens with where its sources lie.

**Before you present something as new.** Before you state a result, look at what the canon states about each definition your statement uses; the result, a stronger one or an equivalent one may be there. Before you define an object, look for a definition the library already has, in the canon and in the imported library. Because a traversal returns the whole of what its rule selects, you can say exactly what you examined, for example that `list --about Tri.tri` returned fourteen elements and none of them bounds the sequence from below, and a reviewer can run the same command.

**When you are stuck.** Read the approaches tried on your statement and on the statements near it: those beside it on the frontier, and those `list --used-by` returns. Read the understanding so far of `q0` again, which says where the difficulty of the problem as a whole is thought to lie. `log` shows what has been published since you started, and review's assessment of each change says what kind of work has moved the research and what has not.
