# Writing the two prose sections of the package's README

The package is nearly complete: the library is frozen, the paper is typeset, the history is written. Its `README.md` is the first file a visitor opens. Most of that file is written by the program from the finished products: the title, the result in a sentence, as the record of the root states it and as Lean states it, what was checked and what was not, how to build, what each folder holds. Two sections need prose that no script can assemble, and this session writes them: an outline of the proof, and an account of how the result was obtained.

## Why the README is written last, and why you write no figure

In the first packaging of this kind the READMEs were written beside the work, before what they describe had settled. Their counts of modules, declarations and lines were rewritten several times as the library changed. Here the documents come after everything they describe, and every figure in them is read by the program from the finished products.

For your two sections this means that you write no figure yourself. Wherever a count, a size, a duration, a date or a version number would stand, you write a placeholder of this form:

```text
{{facts.<key>}}
```

with `<key>` replaced by a key of `facts.json`. The two opening braces, the word `facts`, the full stop, the key and the two closing braces are literal text of what you write. The program replaces each placeholder by the value of that key after you have ended, and it refuses a placeholder whose key `facts.json` does not have. This is the only place in this instruction where braces are meant literally, and these placeholders are yours to write, not something that has been filled in for you.

If the figure you would like to give has no key in `facts.json`, write the sentence without the figure. Numbers that belong to the mathematics, as in a statement about every $n \ge 1$, are not figures in this sense and are written as mathematics.

## What you are given

- `facts.json`: the figures the program computed from the finished package, by key. Read it in full, so that you know which figures you can use.
- `introduction.tex`: the introduction of the paper, in LaTeX. It states the result, places it, and outlines the proof for a mathematical reader. The paper does not mention Lean.
- `account.md`: an account of the chosen proof as a whole: what is proved, how the proof goes from its main results to the main theorem and to the root, and where its difficulty lies. It names the library's declarations.
- `timeline.md`: the history of the research, one entry for each event in time order. Every entry was checked against the research's own record.
- Only when this is the correcting session: `findings.json` and `previous/`. The last section says what they are.

Read all of them in full. They are your only sources: both sections say what these files say and nothing else.

## The outline of the proof

`outline.md` tells a visitor how the proof goes. The visitor may be a mathematician who wants to know whether the paper is worth opening, or someone who works with Lean and wants to find their way into the library. The section that precedes yours in the README has already given the result, so the outline begins with the proof.

Say which results the proof is built from, how the main theorem follows from them and the root from the main theorem, which idea carries the argument, and where its difficulty lies. `introduction.tex` and `account.md` say this for two different readers; take the mathematics from them and write for a reader between the two. Where it helps the visitor find a result in the library or on the dependency map, name its declaration between backticks, using only names that `account.md` gives. Formulas are written in LaTeX between dollar signs and kept few.

The outline presents the chosen proof by itself, as the common text requires of every text that presents mathematics: no other route, no word about how the proof was found.

## How the result was obtained

`obtained.md` tells the visitor where the proof comes from: that it was found by a research run in which AI sessions worked on the proposition in succession, how that research went in its main stages, and how its work was reviewed along the way. `timeline.md` is the source. Condense it to the course a visitor needs: where the research began, the turns the timeline itself reports, and how the root came to be settled. This section and the history are the two texts of the package whose subject is the research, so it may speak of approaches that were tried and left. The research usually proved more than the package keeps: the library under `lean/` holds the one proof the package presents. Where you name results or declarations of the research that are not part of that proof, say that they are in the knowledge archive and not in the library, so that a visitor does not look for them under `lean/`.

Hold it to the standard of the timeline it is written from. Say nothing that the timeline does not say, give judgments as the judgments of the reviews that made them, and add no assessment of your own. The section is not the place for the mathematics, which the outline and the paper carry, nor for what was checked and by whom, which the program's own section states from its logs.

## The form of both files

Each file is the body of one section in Markdown, without its heading, which the program supplies. Write plain paragraphs; use a short list only where the content is a list. Length follows content, at the scale of a README: a visitor reads these sections to decide what to open next.

You may link to files of the package by a path relative to the package's root, where the README stands. The paper is `paper/paper.pdf`, the history `history/timeline.md`, the dependency map `dependency-map/dependency_map.html`, the library `lean/` and the records `records/`. Link to nothing outside the package, and write no path of a machine and no name of an account: the package has to stand alone once it is unpacked elsewhere, and the program checks every link and every path before it finishes.

## What you write

`output/outline.md` and `output/obtained.md`, both complete.

Before you end, search both files for digits and see that each one belongs to the mathematics or stands inside a placeholder, and compare every key you used with `facts.json`. Then read both sections as a visitor who has only the README.

## When this is the correcting session

After the README was assembled, a session that had the package and nothing else read its documents against it and reported what it found. If your folder holds `findings.json` and `previous/`, you are correcting: `previous/` holds the two files as they were written, and `findings.json` lists the findings that concern them, each with the `file`, a `quote` from it and the `problem`.

```json
[{"file": "README.md", "quote": "...", "problem": "..."}]
```

Answer every finding in the text. Where the reader is right, correct the passage from your sources. Where the reader stumbled over a passage that is correct, a visitor may stumble there as well, so make the passage plainer. Change what the findings concern and leave the rest. Return both files complete, also when one of them did not change, and hold them to everything above.
