# The last changes to one part of the library before it is frozen

The library in your folder is what the chosen proof rests on, with `{{root}}` as its root and `{{main}}` as its main theorem. It has been simplified, arranged by subject and given records, and it is about to be frozen: after the freeze no Lean file and no record changes, and the paper, the dependency map and the README are made from the frozen library. This step is the one occasion on which what later work needs from the library is put into it. It is done part by part, a part being a folder of the arranged library, by sessions that work at the same time. Your part is `{{part}}`.

## What the step is for

Three kinds of item are collected before the freeze.

The first kind comes from the sessions that wrote the records. To tell a proof in words they followed it step by step in the Lean, and they noticed what the library itself gets wrong. In earlier packagings such findings arrived after the library had been declared finished.

The second kind comes from a draft of the paper. Before any prose is written, the paper's plan and every one of its numbered statements are drafted in the form a paper would give them, together with the displayed formulas that later proofs refer to, and each is compared with the declaration it states. Where the paper wants to say something that no declaration says, that is a gap: a classical bound that the paper states in its usual strict form while the library proves a weaker one, a numbered bound that is no declaration, inequalities stated at the paper's parameter values, a lemma the paper gives in general form. A library that is extended for such a gap after the paper exists has its records, the dependency map and the README made again.

The third kind comes from the search for sources. The paper cites a result where a source states it in the form the library has, and proves it otherwise. Where the search found a source that states a stronger or a more general form, the paper could do neither well: the source does not state the library's form, and the library does not prove the source's. A paper that then proves at length what a known theorem gives with a better constant draws its readers' objection. So the library is given the chance to state what the source states, and the user's word for it is that the library should ideally already be stating the stronger thing.

The user's decision that this step carries out reads: "the frozen library should already start with all that the paper would need inside as written, it should be worked on such that the paper will not face a situation where it has to write something within it outside of what frozen library contains". So what the draft wants and the library can prove is proved now, as a declaration that says exactly that. What cannot be proved now is reported as not closed, and the paper will then state what the library has; nobody opens the library again for it.

## What you are given

- `items.json`: the items of your part, in this form. Read it in full.

```json
[{"id": "g1", "from": "draft", "declaration": "Lib.tail_le", "kind": "statement", "detail": "...", "wanted": "..."}]
```

`from` is `records`, `draft` or `source`. `declaration` is the declaration the item concerns: the one a record writer's finding is about, the one a gap is nearest to, or the one whose stronger form a source states. For an item from the records, `kind` is `hypothesis`, `conclusion`, `comment` or `other`, and `detail` is what the writer saw. For an item from the draft, `kind` is `statement` (the paper states a numbered statement otherwise than its declaration does), `formula` (a displayed formula that a later proof refers to and that no declaration states) or `assertion` (something a section needs to assert that no declaration states); `wanted` is what the paper wants to say, and `detail` is what the draft recorded about the gap, as a rule what the library has in its place and why the paper wants the other form. For an item from a source, `kind` is `statement` or `assertion`, `wanted` is the statement of the source in the library's notation, as the session that read the source wrote it down, and `detail` names the source and the place in it.

- `part.json`: your part. `modules` are the modules you may change. `interface` lists the declarations of your part that keep their names and their statements, each with its statement: those that modules of other parts use, and the root and the main theorem where they lie in your part.

```json
{"id": "Lib.Count", "modules": ["Lib.Count.Basic"],
 "interface": [{"declaration": "Lib.count_le", "statement": "..."}]}
```

- `lean/`: the whole library. Read the modules that your items concern in full, proofs included.
- `records/`: the records, for what a declaration means and for the notation in which `wanted` is written. You do not change them. The record of every declaration you change or add is written after this step, from the Lean.

## What closing an item means

An item from the draft is closed when a declaration of the library says exactly what `wanted` says: the same objects, the same hypotheses, the same ranges and quantifiers, the same conclusion, strict where it is strict, at the parameter values it names. A session will afterwards compare the drafted text with the declaration you name, and the two have to say the same. A declaration that proves less than was wanted does not close the item. It may still be worth having, and then you add it, report the item as not closed, and say in the note what the declaration states and in what it falls short.

Some items from the draft ask for less than a declaration states. A declaration can state several things together, such as a lemma in four parts, and the paper may use two of them. A numbered statement of the paper says exactly what one declaration says, so the paper can state the two parts alone only when a declaration states them alone; otherwise it has to state all four, and its readers ask what the other two are for. In such an item `wanted` gives the parts that the paper uses, and `detail` says which parts of the declaration they are. The item is closed by a declaration of its own that states exactly those parts and is proved from the declaration that states them all, which is as a rule one line. The declaration that states them all stays as it is.

Before you prove a wanted statement, see that it is true. A draft is written by a session that states things as a paper would, and it can ask for more than holds. If the wanted form is false or you cannot prove it, report that, with what you tried and where it stops. Never close an item with a proof that is left open.

An item from a source is closed when a declaration states the source's form, as `wanted` gives it, and is proved, and the declaration under `declaration` then follows from it. State the source's form under a name of its own and prove it. Then derive the old declaration from the new one, which is as a rule a few lines, or, where `interface` does not list the old declaration, let it give way to the new one and bring its uses inside your part along. `wanted` was written by a session that read the source and not the library, so check it against the definitions before you prove it: where it does not make sense in the library's terms, or is false as written, the item is not closed. If you cannot prove the source's form, the item is not closed either, and the library keeps the form it has. The paper then proves the result, and a reader who knows the source will ask why it is not cited; your note is kept as the answer, so say in it what you tried and where it stops.

For an item from the records, read the finding against the Lean first. A hypothesis that the proof does not need is dropped or weakened. A conclusion that nothing uses is removed, unless an item of the draft wants it. A comment is brought to say what its declaration states, in terms it defines. Where the finding turns out to be mistaken, the item is not closed, and the note says why the library is right as it stands.

## What is yours to change, and what stays

The limits have one reason: the other parts are being changed at this moment by sessions that cannot see your work.

- You change only the modules of your part, and a module that you add lies directly in the folder of your part.
- The declarations of `interface` keep their names and their statements, with their implicit arguments, the order of their arguments and any attribute that affects other files. Where an item asks for another form of such a statement, the new form enters as a declaration of its own under a new name, and the old one stays and is derived from it.
- A declaration of your part that `interface` does not list can be restated in place, and then every use of it inside your part is brought along.
- An item was given to the part that holds the declaration it concerns, so whatever the item requires is added by you and by no other part. If closing it needs a fact that belongs to another part, prove what you need inside your own modules, as a `private` declaration where it is only a means, or report the item as not closed.

The conventions of the common text hold for every file you return. A new public declaration needs a name that says what it states and a short doc comment that speaks of the mathematics only; it does not say that a paper wanted it.

This step is not a second simplification. Change what your items ask for and what follows from those changes, and leave the rest of the part as it is.

## Building, and by what your part is judged

Before your first edit, copy the modules of your part to a folder of your own outside `lean/` and `output/`, so that at the end you find what you changed by comparing. Then edit the files in `lean/` in place and build there, as the section "Compiling" describes. The program accepts your part when no file outside it differs and the whole library builds with your modules in place. A part that fails is discarded whole, and all its items then count as not closed. So take the items one at a time, build after each, and undo a change you cannot get through the compiler, reporting that item as not closed. Before you end, build the whole library once, by naming every `.lean` file under `lean/` as a file to compile, in several commands if the list is too long for one, and end on a state that builds.

## What you write

- `output/lean/<file>`: each module of your part that you changed or added, at its path under `lean/`, as the complete file. A changed file that is missing from `output/` leaves the program with the old one.
- `output/report.json`, in this form:

```json
{"deleted": [], "items": [{"id": "g1", "closed": true, "declarations": ["Lib.tail_lt"], "note": "..."}]}
```

`deleted` lists modules of your part that you removed, as paths under `lean/`; it is usually empty. `items` has one entry for each item of `items.json`. `closed` is `true` when the item is done as described above. `declarations` names the declarations that now carry it: for an item from the draft, the one that says what was wanted; for an item from a source, the one that states the source's form; for an item from the records, the ones you changed. For an item from the draft or from a source the program reads the first name alone, so that declaration stands first if you name others. `note` says what you did, or why the item is not closed. The notes of items that are not closed are kept for the user, and the session that brings the paper's draft to the library reads which declaration closed which gap.

When you changed nothing, return no Lean file and a report in which every item is listed as not closed, with its reason.
