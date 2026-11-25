# Reviewing the whole library before it is simplified

The library in your folder is what the chosen proof rests on: the root `{{root}}`, the main theorem `{{main}}`, and everything beneath them. It compiles, and it is about to be simplified before it is published and before its records and the paper are written from it. The simplifying is done by several sessions side by side, each on one part of the library. This session comes before them. It reads the whole library once, divides it into those parts, and says what is worth simplifying, inside each part and across them. It changes nothing.

## Why one reader of the whole comes first

A session that simplifies one part sees that part closely and the rest hardly at all. It cannot know that another part proves the same lemma under another name, that a statement it could improve is used in a form every user has to convert, or that a general fact it is about to add is being added next door as well. In the first packaging of this kind, two sessions each added the same lemma to their own part, because both had been allowed to, and the merge found the same name declared in two files. What crosses parts therefore has to be seen by one reader and assigned by that reader, each item to exactly one part.

The parts work at the same time and nobody sees another's changes until all are merged. This fixes what an assignment can be. The session of a part may change only the modules of its part, and the declarations of its part that other parts use keep their names and statements. An item that crosses parts is carried out by its owner inside the owner's modules, with the old declaration kept under its name. What then follows in the other parts, such as moving their proofs to the new form, is done after the merge by one session that reads the whole library again and arranges it.

## What simpler means

The library was produced by research in which many sessions each proved one piece, in whatever form got it through the compiler, and later sessions built on top without revisiting what lay beneath. The user's instruction for simplifying such a library reads:

> iteratively read through it to find rooms to make the lean proof more simple, remove redundancies, combine similar parts, remove unnecessary dependencies, reduce the number of logical steps, simplify the steps taken, reduce the amount of arithmetic computation, etc etc anything to make it be more elegant and digestible

The measure is the mathematics a reader has to take in, more than the number of characters. Each public declaration will receive a record and will be offered to the paper as a numbered statement or as a step of a proof, so what helps is a formal structure that follows a human argument: a small number of lemmas that each say something, proved from one another by the shortest sound route, with computation where it explains and an argument where one is available. A proof made shorter by putting one opaque automation call in the place of a readable chain of steps does not help, and neither does a lemma stated more generally than anything needs.

Research under pressure leaves things of the following kinds. They are examples of what to look for, and your reading will show you others. Two lemmas that state one fact in different notation, or a special case proved beside the general one. A lemma used once, whose statement means nothing outside the proof that uses it. A lemma that the imported library already has. A chain from A through B to C in which B is a reformulation that does no work. Hypotheses that no proof uses, and case splits whose branches run the same argument. A numerical bound reached through many explicit estimates where monotonicity, convexity or one cleaner intermediate bound gives it in a few lines. Definitions that duplicate one another, with a lemma that bridges them. The same block of proof repeated where one auxiliary statement would carry it. Statements in a form that every user converts before applying them. Comments that describe how the research went and not the mathematics.

## What you are given

- `lean/`: the whole library. Read it in full, proofs included. The finding that matters most to this step, the same fact proved in two places, is found only by a reader who has seen both places.
- `records/`: the record of each element, as the research left it. Open a record where the Lean shows how a step is verified and not what the argument is for.
- `rests-on.md`: for each element of the library, the elements that its statement names and the elements that its proof names, from the research's index. Read it in full; by looking for a name in the lists of the other elements you see which declarations are used once, which are used only inside their own module, and what crosses from one group of modules to another.

## The parts

A part is a set of modules that one session will simplify. Every module of the library outside the definition modules lies in exactly one part; the definition modules, which the common text says how to recognize, lie in none, because nobody changes them. The module of the root lies in a part like any other, and only the statement of the root is fixed.

Cut the library where the mathematics cuts. A part should be one portion of the argument, such that the session that takes it can read all of it, proofs included, more than once, and can understand what it proves without the rest. As a sense of scale and not a rule, that is a few thousand lines of Lean. Count what crosses a cut: every declaration that another part uses is frozen in name and statement for the session that owns it, so a cut through the middle of one argument freezes much of what most needs improving, while a cut between two arguments that meet in a few stated results freezes only those. Where two modules hold duplicates of each other, putting them into one part lets one session resolve the duplication without any item.

For each part, write what is worth simplifying inside it. The session of that part reads your text as the starting point of its work, and it knows nothing of your reading. Name declarations and modules, say what you saw and what would be simpler, and say where a proposal is something you read and did not try, since you compile nothing. That session will read its part for itself and find more; you need not be exhaustive, and you should not withhold a finding because it is small. If you read a part and found nothing worth changing, say that in those words, so that silence is not taken for a part that was not read.

## What crosses parts

A cross-part item is a simplification that one part cannot carry out by itself: a lemma that two parts each prove; a lemma that several parts would use and that does not exist yet; a statement in one part that the proofs of another convert each time they apply it; two definitions in different parts that denote one object.

Each item has one owner, which is a part. The owner is the part in whose modules the form that is to remain stands or will stand. Choose it so that the parts that will use the result can import the owner's module without an import cycle. Write under `what` the task of the owner, in a form the owner can carry out alone: which declaration it adds or restates, under which name the new form enters where a statement used by others would have to change, and that the old declaration stays under its name, derived from the new one. Under `touches`, name the other parts whose modules use what the item changes; the session that arranges the library after the merge reads this to finish the item there.

A shared lemma is added only by the owner you name. If an item cannot be given to one part in a way that part can carry out alone, change the cut so that the modules concerned lie in one part, or leave the item out.

## What you write

`output/review.json`, in this form:

```json
{"parts": [{"id": "counting", "title": "...", "modules": ["Lib.Count.Basic"], "inside": "..."}],
 "cross": [{"id": "x1", "owner": "counting", "what": "...", "touches": ["series"]}]}
```

- `parts`: for each part an `id` (a short lowercase word, of letters, digits and hyphens, beginning with a letter; it names folders), a `title` that says which portion of the mathematics the part is, its `modules` by module name, and `inside`, the text described above.
- `cross`: for each item an `id`, the `owner` (the id of a part), `what`, and `touches` (ids of parts). An empty array when you found none.

The program accepts the review when the partition is exact, that is, when every module outside the definition modules is in exactly one part and no listed module is missing from the library, and when every cross-part item has one owner that is a part. Check both before you end, with a short script if the library is large.
