# Bringing the paper's draft to the library

A paper will be written from the library in your folder, which is what the chosen proof rests on, with `{{root}}` as its root and `{{main}}` as its main theorem. Before the library is frozen, the paper was drafted at the level of its statements: every numbered statement in the form a paper would give it, and the displayed formulas that later proofs refer to. Where the draft wanted to say something that no declaration said, the library was then changed, as far as that could be proved. This session comes after those changes. For each drafted text whose declaration changed, was added or went, it compares the text with the declaration that now stands, and where the two differ it writes the text as the declaration says it, or marks it as cut.

## What the step is for

After this step the library is frozen, and the paper's writers receive the drafted statements with the sentence that they were compared with the library and are to stand as drafted. So this comparison is what makes that sentence true. When a paper states more than its library proves and the difference is found only after the paper is written, the library has to be extended, and its records and the documents around it made again. Here the order is the other way round: by the user's decision, if the paper still wants a sentence the library does not cover, the sentence is cut or reworded in the paper and the library is not reopened.

When you have ended, nothing in the draft says more than a declaration of the library says.

## What you are given

- `rows.json`: the drafted texts to compare, in this form. Read it in full.

```json
[{"id": "g1", "kind": "statement", "label": "lem:tail", "section": "tail", "draft": "...",
  "declaration": "Lib.tail_lt", "lean": "...", "record": "..."}]
```

`kind` is `statement` (a numbered statement of the paper), `formula` (a displayed formula that a later proof refers to) or `assertion` (something a section needs to assert outside its numbered statements). `label` is the LaTeX label of the statement or formula, and `section` the section of the paper it stands in. `draft` is the text as drafted, in LaTeX. `declaration` is the declaration that is now to state it, with its text in the Lean source under `lean` and its record under `record`, whose part `## Statement` is the statement in words; it is `null` when no declaration states it.

- `lean/`: the library, for the definitions a statement uses and for whatever the row does not show.
- `records/`: the records, for the meaning and the notation of the objects.

You write no Lean and compile nothing.

## The comparison

For each row with a declaration, decide whether the drafted text says exactly what the declaration says: the same objects, the same hypotheses, the same quantifiers in the same order, the same ranges with their end points, the same conclusion, neither stronger nor weaker. The Lean statement is what was proved. The statement in words is there to help you read it; where the two disagree, the Lean statement decides.

A difference of notation or of convention is no difference as long as the mathematical content is the same. A paper counts from one where the library counts from zero, writes an ordinary difference where Lean's subtraction of natural numbers stops at zero, and leaves out a cast. Such a restatement is the same statement when it is equivalent under the hypotheses that are there, and that is where slips hide, so check it at the boundary: the first index, the empty case, the value at which the subtraction would stop.

Then give one of three verdicts.

- `same`: the drafted text says what the declaration says. The text stands.
- `rewritten`: the declaration states a version of what was drafted, and the drafted text differs from it. Write the text anew so that it says exactly what the declaration says. Keep the form the draft has: LaTeX as the paper will carry it, the draft's notation and wording wherever they are not what differs, and nothing of the Lean, neither a declaration name nor the word. Change what the difference requires and leave the rest, since the writers of other sections have the same draft and its notation.
- `cut`: nothing in the library states the drafted text or a version of it, so the paper will not carry it. This is the verdict of a row whose `declaration` is `null`, and of a row whose declaration says something that cannot be put in the place of what was drafted.

A statement that the declaration makes and the draft only weakens is rewritten to the declaration's strength, like one that the draft overstates: the paper's numbered statements say what was proved, in both directions. An assertion follows the same three verdicts; its rewritten text is the assertion as the declaration supports it.

Give a verdict to every row, also after you have found a difference in one. Do not rewrite for taste.

## What you write

`output/verdicts.json`, with one entry for each row, in this form:

```json
[{"id": "g1", "verdict": "same", "text": "..."}]
```

`verdict` is `same`, `rewritten` or `cut`. `text` is the text the paper is to carry: for `same` the drafted text unchanged, for `rewritten` your text, for `cut` the empty string. Inside a JSON string a backslash of LaTeX is written twice.

The program then holds every statement and formula of the draft to a declaration and to a text that was found to say the same. Before you end, read each rewritten text once more against the Lean statement alone, as a new comparison.
