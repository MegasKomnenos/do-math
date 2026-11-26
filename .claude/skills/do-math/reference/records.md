# The written texts of the canon: records, approach entries and understanding texts

Beside its Lean library the canon keeps what Lean cannot hold: a record for each declaration, the approaches tried on a statement whose proof is not accepted, and the understanding so far of each question. The common introduction says what each of these is for. This guide gives their formats, the criteria for the weight of an element and, under "Writing the texts of the canon", how each text is written so that a later session can use it.

## The record

A record is a Markdown file. It begins with a header between two lines `---`, in which each line has the form `key: value`, and continues with parts, each under a heading of the second level.

```markdown
---
weight: unit
short: closed form of the triangular numbers
---
## Description

Twice the n-th triangular number equals n (n + 1).

## Statement

For every natural number $n$, $2 (0 + 1 + \dots + n) = n (n + 1)$.

## Explanation

The statement is written with the factor 2 on the left so that no division of natural numbers occurs. `Tri.tri n` is the sum up to and including $n$, so `Tri.tri 0 = 0`.

## Proof

By induction on $n$. For $n = 0$ both sides are $0$. For the step, `Tri.tri_succ` gives $T_{n+1} = T_n + (n + 1)$, so $2 T_{n+1} = n (n + 1) + 2 (n + 1) = (n + 1)(n + 2)$.
```

The example names `Tri.tri_succ` and gives the equation it supplies. That step reads the same way if another session later formalizes the lemma. Describe each premise by what it contributes to the argument and not by how it stands when you write: a sentence saying that a premise is not yet proved stays in the record after the premise has been proved, while the view of the element shows the current standing, settlement and formality of each premise, from the compiled library and the published judgments. When a change of status is itself worth recording as history, identify the revision at which it occurred.

The header has these keys, and a key outside this list is rejected.

| Key | Content |
|---|---|
| `weight` | Required. `unit` or `step`, by the criteria of the next section. |
| `short` | A short name of a few words. The frontier shows it in place of the self-description, and the dependency map uses it as the label of the element. |
| `proves` | The name of a statement of which this declaration is another proof. |
| `refutes` | The name of a statement whose negation this declaration states. |
| `source` | For a result taken from the literature, the key of its entry in the bibliography. |

A record has `proves` or `refutes`, never both. [The candidate change](change-format.md) explains when a declaration enters with one of them and what Lean has to confirm about it.

The parts are the following. Each may occur at most once, in any order, and their headings are exactly these. Nothing may stand before the first heading, and any other heading of the second level is rejected, so inside a part use headings of the third level and below.

| Part | Content |
|---|---|
| `## Description` | Required. The **self-description**: what this element is, in one or two lines. |
| `## Statement` | The statement in natural language; for a definition, the definition in words. |
| `## Explanation` | What belongs to this object: what the statement says about it, why it can be expected to hold, why a definition was chosen in this form, how the Lean form corresponds to the mathematical one. |
| `## Proof` | The proof in natural language. |
| `## Literature` | For a result taken from the literature: the source, how much of it was read, and where the statement stands in what was read. |

The self-description is the only part of the record that views of many elements show, so it has to be understandable without the rest. Say what the statement asserts or what the definition defines, completely enough that a session looking for that fact recognizes it. It is not the place for the element's history or for its role in some proof: a description such as "a lemma for the main estimate" tells a session that is choosing what to open nothing about the element.

A statement counts as having a proof when its Lean proof is complete or when its record has a nonempty `## Proof`. Whatever stands under that heading is therefore offered as the proof, and review judges it as one. For a statement established by an exact computation, the proof is the account of that computation: what was computed, over which range and in which arithmetic, with the code and its output among the files of evidence. An idea of why the statement should hold belongs under `## Explanation`. An argument that got part of the way belongs among the approaches tried, described below.

The explanation follows a criterion the user gave: an explanation that is attributed to a mathematical object is kept with that object. The reason a definition counts from zero is kept in the record of that definition, and what a lemma shows about a sequence is kept in the record of that lemma, not in the record of the theorem in whose proof the question first came up.

## Weight: units and steps

The weight of an element says how it stands in the structure of the mathematics. A **unit** is a result that someone describing how the proof goes would name: it is obtained in one place and handed to another as an input. A **step** is a result that lives inside one proof and exists because that proof was written in pieces.

Several things are made from the weight. The frontier passes through a step whose own proof is accepted and shows what that step rests on in its place, so that the view stays at the level of the units. The reading commands can restrict a list to units. The dependency map of the research draws units and folds each step into the connections that pass through it, and the paper that presents the result, which is produced once the root is settled through a formal proof, numbers units and absorbs steps into the proofs that use them. In none of these is a step lost. It remains an element, proofs name it, and a traversal that selects it returns it.

The choice matters because the same body of results gives very different pictures. If every lemma is a unit, the picture is the whole dependency graph, and the structure of the proof is buried under hundreds of entries. If only the root and the last derivation of it are units, everything between them is hidden. The level to aim at is the one at which an author describes the structure of a proof: the results that are named when someone says what a result rests on and where it is used.

Four signs point toward a unit.

- A proof of the root, or of another unit, names the element as one of the pieces from which that result follows, and an account of how the proof goes mentions it by name. The understanding so far of `q0` and the natural-language proofs of the elements near the root are such accounts.
- The element is where the proof's guarantees come from: it is taken from the literature, or its truth rests on a computation. Which computation and which cited theorem a conclusion stands on is part of the structure of a proof, so such an element is a unit even when a single proof uses it. A lemma of the same size that is not on such a chain may well be a step. The difference is intended, and an element of this kind is not made a step for lacking the other signs.
- The element gathers the results of several units into one result and hands that on. If it were folded, the inputs it gathered would be scattered over separate connections.
- Proofs in two or more parts of the library, in different folders of modules, rest on it. If it were folded, the flow from one part to the other would no longer be visible.

Other features point toward a step: a technical lemma that only one proof uses, in the same part of the library; a numerical inequality, or a tool, set up to certify a computation; a corollary or reformulation that restates the result of one unit in other words; the stages into which one proof was divided for writing. A definition is judged by the same question. The objects the root speaks of, and an object that several results are about, are units. A device introduced for one proof is a step.

Folding a step that nothing else uses means that the picture no longer shows that input. This alone is not a reason to make it a unit: if every basic input were shown, the level would be lost.

An element that no proof uses yet is judged by the role it would have. A conjecture on which a route depends, and a counterexample that closes an approach, are results a session describing the state of the problem would name. An observation recorded only as the grounds of another element is not.

The signs are material for a judgment and not conditions. A result that an account names can still be a short identity used once, and a result that shows none of the signs can be one that several proofs call by name. Read what the element does in the proofs that use it and decide whether it is handled there as a unit of the structure. The author of the record writes the weight, review judges it, and a later record can correct it when the element's role has become clearer.

## Approaches tried

A statement whose proof is not accepted carries the approaches that were tried on it, one file for each approach, at `approaches/<Name>/<id>.md`. `<Name>` follows the name of the statement the approach was aimed at. `<id>` is a short identifier of letters, digits, `_` and `-`, chosen by the first author of the entry and kept when the entry is replaced.

```markdown
---
title: Induction on the number of terms
sessions: s41c0e, s77a2b
---
## Idea

Compare the sum for n + 1 with the sum for n and reduce the statement to an identity between polynomials in n.

## Established

`Tri.tri_succ`

## Where it stops

The inductive step needs $2 (n + 1) + n (n + 1) = (n + 1)(n + 2)$. This identity has been checked by hand and is not yet stated; nothing else is open.
```

The header has `title`, which is required, and `sessions`, the IDs of the sessions that contributed to the approach, separated by commas: the producing session and its peer, and, in an entry that replaces an earlier one, the sessions that entry named. The parts are `## Idea` and `## Where it stops`, both required, and `## Established`, which names the elements the approach produced, separated by commas or one to a line. At publication the runner adds a part `## Review` with review's assessment of what the work contributed to the research. A session never writes that part, and a candidate that contains it is rejected.

## The understanding so far of a question

The understanding so far of a question is one file, `questions/<question>.md`, named by the question's identifier. It is free Markdown without a header. At publication the runner adds a part `## Review` at its end, as it does for an approach entry; the text a session writes therefore has no heading `## Review` of its own.

The peer of each exploration of the question replaces the text as a whole. The text it replaces is kept in the question's history, as its difference from the new text, and `question <question> --history` prints it.

## Writing the texts of the canon

The texts of the canon differ from an account written from beginning to end. No reader goes through them in order. A session opens the element its work concerns and reads that element by itself, having seen of the others only a line each. Each text therefore has to do its work alone, and each kind of text has a different job. The sections above give their formats.

The **statement in words** says what the Lean statement says, in the ordinary conventions of mathematics. Where the Lean form differs from it, for instance by counting from zero or by a normalization, say so in the explanation, so that a reader can pass between the two.

The **explanation** holds what belongs to this object and to no other. An account of how a session arrived at the statement does not belong to the object. What does belong to it may well have been learned on the way: that a weaker form fails, with the case in which it fails, is something a reader of this element needs.

The **proof** is written so that it can be read for this element by itself. Refer to every other element the argument uses by its Lean name, and say what that element gives at the point where it is used, so that the reader does not have to open it in order to follow the step. Use notation the record itself introduces. Where the element has a Lean proof, the proof in the record is the same argument; when a formal proof takes a different route from the informal one it replaces, the proof in the record is rewritten to follow it. Inside the canon there is no continuous exposition of the whole proof. The proofs of the elements near the root are where a reader learns how the pieces beneath them combine, so write those proofs with that reader in mind, and the understanding so far of `q0` carries the account of the whole.

An **approach entry** is read by a session about to choose how to work on a statement. Tell the idea plainly enough that this session recognizes an approach it was about to take. State where the approach stops as exactly as the mathematics allows: which step fails or is missing, and what would be needed to pass it. Say what the failure excludes and what it leaves open: that one estimate falls short by a logarithmic factor excludes that estimate and not the method. Whatever the approach established exactly is named in the entry as elements and is not retold there.

The **understanding so far** of a question is one text that successive sessions maintain. When you replace it, you answer for the whole text and not only for what you add. Write it as what its readers need now, the present state of understanding: what is understood about what the question asks, on which elements that rests, and what is not understood. The text is not an archive of everything that was ever written under the question. The text you replace is kept in the question's history, so a replacement destroys nothing, and what the canon holds in an element, in an approach entry or in the text of another question is not told again here; it is named where the argument turns on it. So the text does not grow by one paragraph for each session, and it is not told as a sequence of sessions. Review reads the new text against the old one: a claim that stays keeps the qualification that makes it true, and a subject that is left out is one that the canon holds elsewhere or one meant to be left to the history. Only the understanding so far of `q0`, the account of the problem as a whole, has a fixed room, because every session reads it in full at launch; [The account of the problem as a whole](q0-account.md) says what the account is for and how it is kept within its room. The texts of the other questions are read by the sessions that open them, and they are kept to what they are about for the sake of those readers.

Write formulas in LaTeX notation between dollar signs and the names of elements in backticks. The paper that presents the result at the end is produced from these texts, so a statement, an explanation or a proof that reads as mathematics there is one a reader of a paper can follow as well, and a written proof that argued otherwise than the Lean proof would put into the paper an argument that Lean did not check.
