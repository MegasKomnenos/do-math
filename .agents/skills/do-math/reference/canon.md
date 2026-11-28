# The canon: reading it and writing in it

The common introduction explains what the canon is. This guide gives what every session needs in order to work with it.

The formats of the written files, namely the record, the approach entry, the understanding text, the line of a module and the description of a folder, and the criteria for the weight of an element are in [The written texts of the canon](records.md).

## Where the canon is

The canon is the folder `canon/` of the instance directory, whose path is the `instance` value of your `input.json`.

```text
canon/
  lean/                       the module root of the library; every module is under <Library>/
  records/<Name>.md           the record of a declaration
  descriptions/modules/<Module>.md   the line of a module
  descriptions/folders/<Folder>.md   the description of a folder
  approaches/<Name>/<id>.md   the approaches tried on a statement whose proof is not accepted
  questions/<question>.md     the understanding so far of a question
  evidence/<Name>/...         files a record refers to, such as code, data and outputs of a computation
  history/<Name>/...          what a replacement left behind
  history/descriptions/...    what the replacement or the removal of a description left behind
  bibliography.bib            the sources of the results taken from the literature
  index.json                  the structural index
  records.json                a summary of the record headers
  descriptions.json           a summary of the descriptions
```

`<Name>` is a path that follows the name of the declaration: the declaration `Parking.Columns.dq_col` has the record `records/Parking/Columns/dq_col.md`. A component of a name that Windows cannot hold as a file name is encoded: a reserved device name such as `Aux` gets a trailing `%`, and a forbidden character becomes `%` followed by its two-digit hexadecimal code.

`<Module>` and `<Folder>` follow the name of the module or the folder, one path component for each part of the name. A folder is a directory under `lean/<Library>/` that holds modules, directly or in folders inside it, and its name is the path written as a Lean name: `lean/Parking/Columns/` is the folder `Parking.Columns`, its description is `descriptions/folders/Parking/Columns.md`, and the line of its module `Parking.Columns.Basic` is `descriptions/modules/Parking/Columns/Basic.md`. No Lean file carries a description, so a description can be written or replaced without anything being compiled.

Four derived views are in the folder `knowledge/` of the instance: `frontier.md`, the frontier followed by the concerns not yet cleared and the questions; `folders.md`, the folder level of the index of the canon, which is the text the command `index` prints; `index.md`, the self-description of every record in the order of the Lean structure, each with its current standing, with the line of each module under the module's heading; and `board.md`, the work underway. The runner renders them. The folder also holds `state.json`, the same state in structured form, and the published judgments: `changes/<id>/` holds one published change with review's assessment and feedback, `reviews/<id>/` a comprehensive review, `organizations/<id>/` an organizer's output, `questions/<id>/` questions the operator placed, and `descriptions/<id>/` the record of descriptions the operator published. Your starting context carries the frontier, the folder level and the board as they stood at your launch. The `frontier` and `index` commands below return the frontier and the folder level as they are now, the files can be read at any time, and `commands.updates`, which [Tools and working files](tools.md) describes, returns the current board, the questions and the concerns.

You read all of these files and write none of them. The commands below are the way to read the canon, because a view joins what Lean knows of an element with what its record says and a descent or a traversal returns the whole of what its rule selects. A session changes the canon only through a candidate, which a peer or an organizer assembles in its own `output/` and the runner applies at publication. `index.json`, `records.json` and `descriptions.json` are made by machine at each publication. The history is kept apart from the other folders so that a text search of `records/` or `lean/` returns the canon as it is and not the texts that were replaced.

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

A new element is added in a new module file. No existing file is edited to add a declaration, and a candidate whose new module has a path that already exists in the canon is refused. One new module may hold several declarations. The folder you choose for a module is where the index of the canon files it and how the dependency map groups its units. A session that descends through the index opens a folder for what the folder's description says lies there, so choose the folder by the part of the mathematics the module belongs to, where a reader of the library would look for it; `index` prints the folders with their descriptions. Lean rejects a second declaration of a name, and of two candidates that introduce the same name, or a module at the same path, only the first can be published as it is. Two sessions at work on the same part of the mathematics can each choose the same word for it, so give a declaration a name that says what it states, as Mathlib does, name the file of a module after what its declarations establish and not after the topic alone, and avoid names such as `aux` or `lemma1` that another session is likely to choose as well.

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
| `index` | The folder level of the index as it is now: every folder directly under the library with its description and its counts, and the modules directly under the library, each with its line. |
| `index <folder>` | One folder: its description, the folders directly inside it with their descriptions and counts, and the modules directly inside it, each with its line and its number of elements. |
| `index <module>` | One module: its line, and one line for each of its elements. A name that is both a module and a folder returns the module and then the folder. |
| `index --due` | What the index lacks and what has been reported about it: the modules without a line, the folders without a description, the folders whose description has fallen behind, the descriptions published without a blind descent test, the reports that a description did not lead a session to an element, and the folders that do not follow a natural boundary. It is written for the organizer and open to every session. |
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

A list returns one line for each element it selects and ends with the count, and so does each listing of `index`, for the folders, the modules or the elements of its level. The lines come in a fixed order, by name, or in the order in which the elements are reached from the starting element, so the same command on the same canon returns the same lines. These commands start no Lean process. They read the structural index, the records and the summary of the descriptions, which describe the canon as of its latest publication.

The same array has two further commands. `checkout <folder>` copies the library, `canon/lean`, for your own Lean work; [Lean](lean.md) describes it under "Building against the canon and your own modules". `descent-test` takes the blind descent test on the descriptions that a peer or an organizer has written in its output; [The candidate change](change-format.md) describes it under "The blind descent test".

The commands correspond to the ways of reading that the common introduction names under "Reading the canon". The descent is `index`, then `index <folder>`, `index <module>` and `view <element>`; it follows containment, and `list --module` returns the elements of a module and of every module under it in one list, without the descriptions. Use is `list --uses` and `list --used-by`, and the view of an element shows one step of each. Object is `list --about` with a definition. Standing is `frontier` and `list --remaining`. The search has a command of its own, which the section "Searching the canon by meaning" below describes.

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
| `used by` | The elements whose proofs name this one, each with its standing: the first forty, and then the number of the rest with the command that lists them. | The compiled library. |
| `stated with` | For an element that statements mention: how many do, and the command that lists them. | The compiled library. |
| `library` | Theorems of the imported library that the declaration uses, the first twelve and the number of the rest. | The compiled library. |
| `axioms` | The axioms the proof depends on through everything it uses, as Lean reported them for the declaration; it is the list that `#print axioms` prints. `sorryAx` means that this proof, or a proof it rests on, ends in `sorry`. | The compiled library. |
| `verdict` | Review's judgment: of which Lean statement it was made, whether the proof was confirmed, whether it was accepted, the change or later review that carried the judgment, and the reason. | Review. |
| `contested` | Shown when this statement and its negation both carry settled proofs. Nothing rests on either of the two until a comprehensive review has located the failure. | Computed. |
| `refuted by` | Shown when a settled proof establishes the negation of this statement: the elements that carry that proof. No work on a refuted statement remains. | Computed. |
| `names refuted` | Shown when the proof of this element names a statement that has since been refuted. The proof cannot become settled as it stands, and the statement needs another one. | Computed. |
| `questions` | The questions whose statement, grounds or understanding so far name this element between backticks. | The questions. |
| `concern`, `later review` | Each concern about the element with its status, and each finding of a later review. One that is about a proof the element had before its present one has `raised about an earlier proof`, for a concern, or `about an earlier proof`, for a finding, beside its status. | Review. |
| `held by` | One line for each section a session holds on the statement: the session, its role and stage, and whether the section is the whole element, an exact part, or a new statement aimed at it. | The board. |
| `approach` | One line for each approach tried: its identifier, its title, and the beginning of where it stops. | The approach entries. |
| `record parts` | Which parts the record has, and how to read them. | The record. |

In the `verdict` line the first word after the colon is review's judgment of correctness: `confirmed`, `not_confirmed`, `undetermined` when review could not complete the judgment, or `not_applicable` for a definition or a statement without a proof, where the reason carries what review judged of the definition or of the statement itself.

The view of a definition has no `proof`, `rests on` or `settled` line. It shows the Lean text of the definition instead, since the body of a definition is what the definition says.

The Lean source of a statement is opened in two situations. One is to read or change the body of a formal proof; `view <element> --part source` prints it, and the `source` line gives the file. The other is a judgment of fidelity that needs more than the printed statement, for example what an implicit argument that the printed form omits is, or what a notation stands for. That judgment belongs above all to review, and it may need a compile.

### The listings of the index

`index` prints the folder level. The values in the examples of this section are invented.

```text
Index of the canon · revision 41 · library Tri: 2 folders, 9 modules, 31 elements.

Folders (2)

- Tri.Bounds · 5 modules · 19 elements
  Bounds on the triangular numbers and on sums of them: upper and lower estimates, each with the range of n on which it holds.
  A session that needs to compare a triangular number with a square or with a neighbouring one finds the comparison here.
- Tri.Parity · 2 modules · 6 elements
  (no description yet; open the folder to see what it holds)

Modules directly under Tri (2)

- Tri.Closed · 4 elements — The closed form of the triangular numbers and the identities that follow from it by algebra alone.
- Tri.Defs · 2 elements — The definition of the triangular numbers by recursion, and the step from n to n + 1.

2 folders and 2 modules at this level.
```

The first line gives the revision, which is the number of the latest publication, the number of folders at this level, and the numbers of modules and of elements in the whole canon. Under the name of a folder stand its counts, the modules and the elements beneath it at any depth, and then its description, each paragraph on one line. A module shows its number of elements and its line. A folder without a description and a module without a line say so in the place of the text.

`index <folder>` prints one folder: the description as it was written, and then the folders and the modules directly inside it in the same form.

```text
Tri.Bounds · folder · 5 modules · 19 elements

Bounds on the triangular numbers and on sums of them: upper and lower estimates, each with the range of n on which it holds.

A session that needs to compare a triangular number with a square or with a neighbouring one finds the comparison here.

Folders (1)

- Tri.Bounds.Upper · 2 modules · 7 elements
  Upper bounds for the triangular numbers by squares and by powers of two.

Modules (3)

- Tri.Bounds.Gap · 2 elements — The difference of two consecutive triangular numbers, and its comparison with n.
- Tri.Bounds.Lower · 5 elements — (no line yet)
- Tri.Bounds.Squares · 5 elements — Triangular numbers between consecutive squares: which squares a triangular number lies between.

1 folder and 3 modules at this level.
```

`index <module>` prints one module: its line, and each of its elements in the one-line form shown at the head of this section.

```text
Tri.Bounds.Gap · module · 2 elements
The difference of two consecutive triangular numbers, and its comparison with n.

Tri.gap_eq · theorem · step · accepted — The (n + 1)-th triangular number exceeds the n-th by n + 1.
Tri.gap_le · theorem · unit · no proof — The difference of two consecutive triangular numbers is at most twice the smaller index plus one.
2 elements.
```

The name of the library, given to `index`, prints the folder level. A name that is neither a folder nor a module, the name of an element included, is an error.

`index --due` prints six lists, each with its count in the heading and each complete; an empty list keeps its heading with `(0)`.

| List | What it holds |
|---|---|
| `Modules without a line` | Each module that has no line, with its number of elements. |
| `Folders without a description` | Each folder, at any depth, that has no description, with its counts. |
| `Folders that received modules after their description was last written or confirmed` | Each folder whose description is older than a module beneath it, at any depth: the revision the description was written or confirmed against, and each module that came to the folder after it, with the revision at which it came and its line. A module that a rearrangement moved into the folder counts as having come then. A module that was published by the same change as the description does not count, since that description was written for the folder with the module in it. |
| `Descriptions published without a blind descent test` | Each line or description that was published while the reader of the test could not be had, with its revision. |
| `Reports that a description did not lead a session to an element, each listed until its description is written or confirmed against a revision of the canon that showed the report` | Each report that a peer entered with its candidate or a review in its assessment, about a folder or a module the canon has, on three lines. The first line says where the report came from, which is a published change, a candidate that its review excluded, or a candidate that its review accepted and whose publication failed; the revision of the report, which is that of its change or, for a candidate that was not published, the one the canon had when the runner kept the report; who entered it; the description and the element. The second line gives the purpose. The third says from which revision on a description answers the report and which revision the description has now. A report stays on the list until the description it names is written or confirmed against a revision of the canon that showed the report. The revision a description is written or confirmed against is the one the canon had when the change that carries it was last prepared, or the one the operator named for descriptions the operator published; when the description was published plays no part. The report of a published change is shown by the canon from the revision of that change on. A report kept from a candidate that was not published is shown for certain only by a later revision than its own, because keeping it publishes nothing, and a description prepared at the same revision may have been prepared before the report was kept. Where the name is both a module and a folder, the report stays until both of its descriptions have reached the revision. |
| `Folders whose description ends in a Boundary paragraph` | Each folder whose description says that the folder does not follow a natural boundary, with that paragraph. |

## Searching the canon by meaning

The search reads the index of the canon on your behalf and returns the elements that bear on a need you state in your own words. The common introduction says under "Reading the canon" when it serves and what its answer does and does not assure. This section gives the command, what it reads, the form of its answer and what it costs.

### The command

`commands.search` in your `input.json` is an argument array whose last element is your session directory. Append the options after it. With `python` for the interpreter and `<search tool>` for the script, the first two elements of the array:

```text
python <search tool> <session directory> --file work/need.txt
python <search tool> <session directory> --file work/need.txt --folder Tri.Bounds --folder Tri.Closed
```

| Option | Meaning |
|---|---|
| `--file <file>` | Required. The request: a UTF-8 text file that states one need, in your own words, with a Lean statement where you have one. It is not empty and holds at most 20,000 characters, since it is sent with every part that is read. |
| `--folder <name>` | Narrow the search to a folder, with every module beneath it, or to a module. The option can be given several times. A narrowed search reads those parts of the canon alone, and it does not read the unpublished work. |
| `--history` | Also read the texts that later texts replaced: the files under `canon/history/` of the elements in the scope. |
| `--timeout <seconds>` | How long the command waits before it says that the search continues; 50 when omitted. |

Write the request as you would put the need to a colleague who knows the canon and has not followed your work: what you are looking for or are about to work out, about which objects, and in which formulation you have it. The readers are told that your words and the canon's may differ, and they judge by the mathematics, so you do not have to guess the canon's names; a Lean statement, where you have one, gives them the exact form.

### What is read, and by whom

The search reads the index itself, in full for its scope: for each folder its description, for each module its line, and for each element the one-line form that every listing prints. It cuts this text into parts and gives each part to one **light session**: a single call of a Claude model that has no tools, is given the part and your request and nothing else, and names at most ten hits in its part. Unless the search is narrowed, further light sessions read the unpublished work: for every pipeline whose work is with a peer, under review, or accepted by its review and waiting for its turn to be published, the report of its producing session and, once the work has reached review, the self-descriptions of the records of the frozen candidate. With `--history`, further light sessions read the replaced texts.

The model and the effort of the light sessions are those of `settings.search` of the instance, which your pack shows among the settings, and the first line of the answer names them. At most `settings.search.parallel` searches and blind descent tests are at work at one time in the instance, counted over all sessions, and at most as many light sessions run at one time over all of them. A search can therefore wait for its turn behind others, and it reads nothing until its turn has come. A search is no session of the run.

### The answer

```text
Search of the canon · revision 41 · read by claude/<model> at <effort> effort · 2026-03-02 14:07

Hits in the canon (3): 1 direct, 2 related

Direct: these state or decide what the request asks for, in this or another formulation, more generally, as a special case, or by showing that it fails.

- Tri.tri_le_sq · theorem · unit · accepted — The n-th triangular number is at most the square of n.
  filed in Tri.Bounds.Squares
  why: It bounds a triangular number by a square, which is the comparison the request asks for.

Related: definitions, lemmas, steps and neighbouring statements that the request would use or that do part of its work.

- Tri.two_mul_tri · theorem · unit · correct, held back — Twice the n-th triangular number equals n (n + 1).
  filed in Tri.Closed
  why: The closed form, from which a bound by a square follows by algebra.

- Tri.tri · def · unit — The n-th triangular number, the sum of the natural numbers up to n.
  filed in Tri.Defs
  why: The definition of the object the request speaks of.

Hits in unpublished work (1), not reviewed: 0 direct, 1 related

This work is not in the canon and no review has judged it. A hit says that the work exists; check it yourself before you rest anything on it.

Related: definitions, lemmas, steps and neighbouring statements that the request would use or that do part of its work.

- session s4e6ac5ea8ad04389a3d9d44ec7877dc5 · attempt · with a review · not reviewed
  report <path of that session's report.md> · candidate <path of the frozen candidate>
  where: Part 2 of the report
  why: It proves a sharper bound of the same kind for even n.

Read:
- 31 of 31 elements in 9 of 9 modules: the whole canon
- the unpublished work of 2 sessions: s4e6ac5ea8ad04389a3d9d44ec7877dc5 and s77a2b0c41d5e4f6a8b9c0d1e2f3a4b5c
Not read:
- the replaced texts in the canon's history: not asked for; --history adds them

A search can miss: that it found nothing is no evidence that the canon holds nothing on the matter. The descent returns the whole of a scope: `index`, then `index <folder>` and `index <module>`.
```

The answer has a section for the canon, one for the unpublished work unless the search was narrowed, and with `--history` one for the replaced texts. In each section the **direct** hits come first: those that, in the reader's judgment, state or decide what you asked for, whether in your formulation or another, as a more general statement, as a special case, or by contradicting it. The **related** hits follow: definitions, lemmas, steps and neighbouring statements that your work would use. A group without hits is not printed, and a section without any hit keeps its heading with `(0)`.

Of a hit in the canon the program takes only the name from the light session, and only when it is the name of an element that stood in the part that session read. A search narrowed with `--folder` therefore prints no hit from outside the named scope. The line of the element, with its kind, weight, standing and self-description, and the module after `filed in` come from the canon. The sentence after `why:` is the reader's own account of how the element bears on your request, and whether a hit is direct or related is the reader's judgment as well; read the element before you rely on either. `view <element>` shows it, and `index <module>` with the module it is filed in shows what stands beside it.

A hit in unpublished work names the producing session, its role and whether its work is with a peer or with a review, the path of its report and, where there is one, of the frozen candidate, and where in that work the reader found the match. Work whose review has ended with the decision to publish, and which waits for its turn in the publication queue, is not printed among these. Its hits stand in a section of their own, `Hits in work accepted by its review and waiting to be published (n)`, which is printed when there is such a hit, under the sentence `This work is not in the canon yet. Its review has accepted it, and it waits for its turn to be published; it enters the canon when its publication has built it on the canon as the canon stands then.`, and the line of such a hit reads `accepted by its review · waiting to be published` where the other reads `with a review · not reviewed`. A hit in the replaced texts names the element and adds the command that prints those texts, `view <element> --part history`.

`Read:` says how many elements of how many modules were read and in which scope, the sessions whose unpublished work was read, and, with `--history`, how many elements' replaced texts. `Not read:` lists everything in the scope of the canon, the unpublished work or the history that no reader examined, each with the reason. An element under `Not read:` was not judged at all, which is a different thing from an element that a reader saw and did not name. The list holds:

- each part whose light session could not be had, named by the folders or modules it held: the reader died, did not end within twenty minutes or answered in another form, twice in a row, or the provider refused it, for instance at a usage limit;
- the unpublished work of a session for which neither a report nor candidate records were found;
- for a narrowed search, the canon outside the named scope and the unpublished work;
- the replaced texts, when `--history` was not given.

When a part could not be read, the line `Incomplete: 1 of the 4 parts of this search was not read; "Not read" below says which. Run the same command again to have them read.` stands directly under the first line. Such an answer is printed once. The same command, given again, reads only the parts that were not read and prints the answer with them.

### Waiting, and the exit codes

A search takes minutes, so the command starts the work in a process of its own and waits for it up to the timeout. While the work is not done the command prints

```json
{"waiting": true, "hint": "the search continues; run the same command again"}
```

and exits with code 124. Give the same command again to come back for the answer: the same request text with the same `--folder` names and the same `--history`, on a canon that has had no publication since, is the same search, whichever session asks, so two sessions with the same request share one search. A complete answer is kept, and every later command with the same request prints it without anything being read again. After a publication the same command is a new search of the canon as it then is. The command exits with 0 when it has printed an answer, a complete one or an incomplete one, and with 1 on an error, which it prints as a JSON object with the key `error`. One such error is not a fault of the request: a search that begins while a publication is being put in place waits a short time for it, and when the publication is still not in place then, it ends with an error that says so and reads nothing. A search with `--history` waits in this way until the publication has ended altogether, because the replaced texts of a publication are set aside last. The same command starts it again.

### What a search costs

A search costs what it reads. Every part is read by a model in full, and the number of parts follows the size of the scope. On a canon of about 5,800 elements in 1,400 modules, a search that read the whole index and nothing else read about 1.1 million tokens through 12 light sessions, in about a minute and a half. A search of the whole canon reads the unpublished work as well. Such a search was not measured; the unpublished work of that time would have added about as many light sessions again. The tokens and the cost of a search are counted in the usage of the run.

What a part costs also depends on whether its text was read shortly before. The provider keeps a text that a light session has read in a cache, and for an hour it reads the same text from there at a fraction of the cost. The text of a part does not depend on the request, and the index is cut into parts along the folders directly under the library, so a publication changes the parts that hold the folders it touched and leaves the others as they were. A search of the whole canon that follows another within the hour, whichever session gave the first, therefore pays the full cost only for the parts that changed in between. In the measurement above, such a search cost about a twentieth of what the first one cost.

A search narrowed with `--folder` reads the named folders alone: one light session where they fit into one part, and no part of the unpublished work. The folder level of the index is in your starting context, so you can often name the folders in which the matter would be filed. A search of those answers the question for those folders at a fraction of the cost, and it leaves the rest of the canon and all unpublished work unread, as its `Not read:` list says.

## Occasions for reading

**When you take something on.** Read the element in full with `view <element> --full`: its Lean statement, what its record says of it, review's verdict and reason, and the approaches tried. Then, for each definition on its `objects` line, run `list --about` with that definition. This is the reading the common introduction asks for: it shows you whether a piece you were about to build is already there, and under which name. `list --uses <element> --deep` shows what the statement already rests on, and `list --used-by <element>` what depends on it. The `source` line of the view gives the file of the module the element stands in, `canon/lean/Tri/Closed.lean` for the module `Tri.Closed`, and `index` with that module, and with the folder above it, shows what the canon files beside it. For a question, `question <question>` gives the grounds on which it was asked and the understanding so far.

**When you need a tool or a lemma.** A lemma about an object is found from the object: `list --about` with its definition. A part of the mathematics is found through the index: the folder level in your starting context names the folders with what each holds, `index <folder>` gives the lines of the modules in a folder, and `index <module>` the elements of a module. A lemma can also be stated about other objects than the ones you have in hand, or lie in a folder whose description does not let you expect it there. For that case, give the search what you need in your own words, with the Lean statement where you have it, narrowed to the folders where the lemma would be filed when you can name them. These commands cover the instance's own library. The imported library, Mathlib and the toolchain, is searched by its own means and is used directly, without an element; [Lean](lean.md) opens with where its sources lie.

**Before you present something as new.** Before you state a result, look at what the canon states about each definition your statement uses; the result, a stronger one or an equivalent one may be there. Before you define an object, look for a definition the library already has, in the canon and in the imported library. Descend into the folders where such a result would be filed and read the lines of their modules. Because a descent and a traversal return the whole of what their rule selects, you can say exactly what you examined, for example that `list --about Tri.tri` returned fourteen elements and that `index Tri.Bounds.Lower` returned five, and that none of them bounds the sequence from below, and a reviewer can run the same commands. A search with the result in your own words and in Lean is a second way in, and a search of the whole canon is the one reading that also covers the work other sessions have not yet published. What it finds is worth having. That it found nothing shows only that its readers named nothing, so an empty answer is no ground on which a result is new.

**When you are stuck.** Read the approaches tried on your statement and on the statements near it: those beside it on the frontier, and those `list --used-by` returns. Read the understanding so far of `q0` again, which says where the difficulty of the problem as a whole is thought to lie. `log` shows what has been published since you started, and review's assessment of each change says what kind of work has moved the research and what has not. The difficulty you are stuck at may have been met in another part of the canon, under other names: a search with the obstacle described in your own words reads the whole index for it, and the unpublished work of the sessions now with a peer or a review as well.

**When you come upon something the descriptions did not lead you to.** Note the description, the element and the purpose you had, as the common introduction asks under "Reading the canon", while you still know which level you had read and what you were looking for. `index <folder>` or `index` prints the description again as it now stands.
