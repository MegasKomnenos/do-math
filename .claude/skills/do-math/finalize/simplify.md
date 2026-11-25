# Simplifying one part of the library

The library in your folder is what the chosen proof rests on: the root `{{root}}`, the main theorem `{{main}}`, and everything beneath them. It compiles. Before it is published, and before its records and the paper are written from it, it is made simpler and easier to follow. A session before this one read the whole library and divided it into parts, and now one session works on each part, all at the same time. Your part is `{{part}}`.

## What the work is for

The library was produced by research in which many sessions each proved one piece, in whatever form got it through the compiler, and later sessions built on top without revisiting what lay beneath. The user's instruction for this work reads:

> iteratively read through it to find rooms to make the lean proof more simple, remove redundancies, combine similar parts, remove unnecessary dependencies, reduce the number of logical steps, simplify the steps taken, reduce the amount of arithmetic computation, etc etc anything to make it be more elegant and digestible

The measure is the mathematics a reader has to take in, more than the number of characters. The library is read twice by people who were not there when it was made: by whoever opens the Lean files, and, through the records and the paper written from them, by a mathematician. Each public declaration becomes a numbered statement of the paper or a step inside one of its proofs. What helps those readers is a formal structure that follows a human argument: a small number of lemmas that each say something, proved from one another by the shortest sound route, with computation where it explains and an argument where one is available. A proof made shorter by putting one opaque automation call in the place of a readable chain of steps does not help, and neither does a lemma stated more generally than anything needs. Where shortness and clarity pull apart, clarity is what was asked for.

Research under pressure leaves things of the following kinds. They are examples of what to look for, and your own reading will show you others. Two lemmas that state one fact in different notation, or a special case proved beside the general one. A lemma used once, whose statement means nothing outside the proof that uses it, where inlining shortens both. A lemma that the imported library already has. A chain from A through B to C in which B is a reformulation that does no work. Hypotheses that a proof never uses, and case splits whose branches run the same argument. A numerical bound reached through many explicit estimates where monotonicity, convexity or one cleaner intermediate bound gives it in a few lines. Long `nlinarith` or `norm_num` certificates for something that follows from a named inequality. Definitions that duplicate one another, with a lemma that bridges them. The same block of proof repeated where one auxiliary statement would carry it. Imports that nothing in the file uses. Comments that describe how the research went, with its identifiers and sessions, where a reader needs the mathematics.

## What you are given

- `lean/`: the whole library. Only the modules of your part are yours to change. The rest is there so that your modules compile and so that you can see what uses your results.
- `part.json`: your part, in this form.

```json
{"id": "counting", "title": "...", "modules": ["Lib.Count.Basic"], "inside": "...",
 "interface": [{"declaration": "Lib.count_le", "statement": "..."}], "cross": [{"id": "x1", "what": "..."}]}
```

`modules` are the modules of your part. `inside` is what the reviewing session found worth simplifying in them; it read the whole library once and compiled nothing, so take its findings as the starting point of your reading and its proposals as proposals. `interface` lists the declarations of your part that keep their names and their statements, each with its statement: those that modules of other parts use, and the root and the main theorem where they lie in your part. The steps after this one find the root and the main theorem by name, and the package states the main theorem as it was chosen. `cross` lists the simplifications that reach beyond your part and that the review gave to you.

Read `part.json` in full, then the modules of your part in full, proofs included, before you change anything.

## What is yours to change, and what stays

Inside your part you may restate, merge, rename, move between your modules, make private or delete whatever the list `interface` does not name, and you may add a module in a folder where modules of your part lie, under a name that says what it holds. Three limits come from the fact that the other parts are being changed at this moment by sessions that cannot see your work, and that nobody sees another's changes until all parts are merged.

**The declarations of `interface` keep their names and their statements.** The statement includes the implicit arguments and the order of all arguments, and an attribute that affects other files, such as `@[simp]`, stays as well. The other sessions are writing proofs against these statements as they stand. Where you want such a statement in another form, the new form enters under a new name and the old declaration stays, derived from the new one in a line. Say so in your report; the session that arranges the library after the merge moves the users to the new form and removes the old.

**No file outside your part changes.** The program rejects a part when any other file differs. A module of yours that a module outside your part imports therefore stays as a file, since you cannot change that import line; it may shrink to what is still needed there.

**A lemma that several parts would use is added only by the part that owns it.** In the first packaging of this kind, two sessions each added the same lemma to their own part, because both had been allowed to, and the merge found the same name declared in two files. The items of `cross` are yours: carry each out inside your own modules, keeping the old declaration under its name where others use it, and leave to the arranging session what follows in the other parts. A simplification that reaches into another part and is not in your `cross` is not yours to carry out; describe it in your report. If your own proofs need a general fact that other parts might equally want, keep it `private` in your module, where its name cannot meet another, and mention it in the report.

The conventions of the common text hold for every file you return.

## How to work

Before your first edit, copy the modules of your part to a folder of your own outside `lean/` and `output/`. At the end you find what you changed by comparing with that copy and not from memory.

Work in passes. Read the part through until you know what it proves and how its pieces depend on one another. Then change, build, and read what you have again, because removing one layer usually exposes the next.

Use the difference between public and private. A declaration that exists only because one proof was written in pieces, and that is used only inside its own module, can be made `private` where inlining it would hurt readability. A private declaration receives no record and is not offered to the paper; its content is told inside the proof of the public statement that uses it. The public declarations of a module should read as the list of things worth knowing about its subject.

Before you delete or rename a declaration, search all of `lean/` for its name, since the list `interface` was made from an index of proof terms and a use in a notation or an attribute line does not show there. Avoid edits that make a module much slower to compile, such as a larger kernel evaluation.

Edit the files in `lean/` in place and build there, as the section "Compiling" describes. While you work, build the modules you changed. A change that you cannot get through the compiler in a reasonable number of attempts is undone and noted in your report.

The program accepts your part when no file outside it differs and the whole library builds with your modules in place, each module with exit code 0. A part that fails this is discarded whole, and the library keeps the form it had there, so everything you did is lost with the one change that broke the build. Before you end, build the whole library once, by naming every `.lean` file under `lean/` as a file to compile, in several commands if the list is too long for one. The modules you did not touch and that import nothing you changed come from the service's store. End on a state that builds: if the last change does not, undo it.

## What you write

- `output/lean/<file>`: each module of your part that you changed or added, at its path under `lean/`, as the complete file. Copy them when your work is done and the library builds, and find them by comparing `lean/` with the copy you made at the start: a changed file that is missing from `output/` leaves the program with the old one.
- `output/report.json`, in this form:

```json
{"deleted": ["Lib/Count/Old.lean"], "cross": [{"id": "x1", "done": true, "note": "..."}], "notes": "..."}
```

`deleted` lists the modules of your part that you removed, as paths under `lean/`. `cross` has one entry for each item of your `part.json`: whether it is done, and in `note` which declarations now carry it and what remains to be done in other parts, or why it is not done. `notes` is read by the session that arranges the library after the merge: say, module by module, what you changed and why the result is simpler; which statements of `interface` have a new form, under which name; which general facts you kept private; and what you saw and did not do, each with its reason, stated so that someone else can act on it. If you did not read some module of the part through, name it there.

When you changed nothing, return no Lean file and a report with empty lists whose `notes` say what you read and that you found nothing to change.
