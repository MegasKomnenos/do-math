# The written texts of the canon: records, approach entries and understanding texts

Beside its Lean library the canon keeps what Lean cannot hold: a record for each declaration, the approaches tried on a statement whose proof is not accepted, and the understanding so far of each question. The common introduction says what each of these is for. This guide gives their formats and the criteria for the weight of an element. [Writing](writing.md) says under "Writing the texts of the canon" how each text is written so that a later session can use it.

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

The self-description is the only part of the record that views of many elements show, so it has to be understandable without the rest. Say what the statement asserts or what the definition defines. A description such as "a lemma for the main estimate" tells a session that is choosing what to open nothing about the element.

A statement counts as having a proof when its Lean proof is complete or when its record has a nonempty `## Proof`. Whatever stands under that heading is therefore offered as the proof, and review judges it as one. A proof under this heading is written so that it can be read for this element by itself, it refers to the elements it uses by their Lean names, and where the element has a Lean proof it is the same argument as that Lean proof. For a statement established by an exact computation, the proof is the account of that computation: what was computed, over which range and in which arithmetic, with the code and its output among the files of evidence. An idea of why the statement should hold belongs under `## Explanation`. An argument that got part of the way belongs among the approaches tried, described below.

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

Folding a step that nothing else uses means that the picture no longer shows that input. This alone is not a reason to make it a unit. The picture is a picture of the structure and not the whole graph, and if every basic input were shown the level would be lost.

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

The peer of each exploration of the question replaces the text as a whole. The text it replaces is kept in the question's history, as its difference from the new text, and `question <question> --history` prints it. A replacement therefore destroys nothing, and the text can be what its readers need now: the present state of understanding, and not everything that was ever written under the question. Only the text of `q0` has a fixed room, for the reason the next part gives. The texts of the other questions are read by the sessions that open them, and they are kept to what they are about for the sake of those readers.

### The account of the problem as a whole

The understanding so far of `q0` is the account of the problem as a whole, and it is read differently from every other text of the canon. Any other text is opened by a session that has a reason to open it. This one is placed in the starting context of every session, in every role, and each session reads all of it before it begins the work it was launched for: an attempt before it chooses a statement, an explorer before it chooses where to look, a peer and a reviewer before they judge what a piece of work changed in what is known. What these sessions need from it is the state of the problem at the level of the whole. For a problem in the middle of its research that usually includes what is asked and what is known; how the existing proofs and reductions go; where the root is held up, and why there; what the places at which different lines of work stopped have in common; and what is not understood. A session that has read nothing else should come away able to say where the difficulty lies, and to recognise work that would bear on it.

Because every session reads all of it, the account has a fixed room. Its text, as the peer writes it in the candidate and without the `## Review` part that the runner adds at publication, is at most 40,000 characters. No program checks this. The peer counts the characters of its file, and review says so when a text is over. The reason for the room is what happened in one research while the account had none. The account was written nine times there, by the peers of nine successive explorations. The guides of that time asked each peer to keep what the text held and to add what its exploration had found, and each peer did so with care. Within three days the text grew from 20,000 characters to 180,000, and it came to name more than five hundred elements in sixty paragraphs, some of them ten thousand characters long. The text was not careless: its statements were exact, and they named the elements they rested on. But the passage that said where the root was held up was by then one among many of the same standing, and a session reading the text could no longer tell it from the rest. And the text by itself took up about a fifteenth of everything a session can keep in view while it works, in every session, before that session had read a line of what it was launched to do. The room is twice the length of the first of those nine texts, which told a session what it needed at that stage of the research. It leaves a later account, of a problem about which more is known, twice that space.

The room states what every session gives up in order to read the account. It is not a measure of the account. A text can be within its room and of no use to anyone, and whether an account serves its readers is judged by reading it, as the common introduction asks of every judgment under "Judging from the text itself".

The room suffices because the account is not where the research keeps its results. The canon keeps each thing in one place, and a session reaches it there. The statement of a result, its proof and the explanation of what it shows are in its element. How an approach to a statement went and where it stopped is among the approaches tried on that statement. What is understood about a narrower question is in that question's own text. Which results exist about an object is what a traversal from that object returns. What the account holds is what none of these places can hold, because it concerns how they stand to one another: how the results combine, which of them the progress so far rests on, why lines of work that look different stop at what is one difficulty, and where all this leaves the root. So the account names an element where its argument turns on that element, and says what the element gives at the length the argument needs: a clause for a result that is used, the construction itself for an example on which the argument rests. It does not retell an element for the element's sake, and it does not list the elements that exist. A passage that is about one statement, one object or one narrower question, and not about the problem as a whole, belongs with that statement, object or question, and the account needs at most a sentence that says it is there. The dependence runs one way. Because the account is rewritten, no other text of the canon can rely on a passage of it: a record that needs a point states the point, and does not send its reader to the account for it.

A text is brought within its room by deciding what it is about, and not by saying the same things in fewer words. The difference shows on a case. Suppose the account contains this paragraph:

> The induction on $n$ needs a bound for the sum over the short intervals. The estimate of `Sum.short_le` loses a factor $\log n$ there, because it bounds every term by the largest one. Near the endpoints the terms are smaller than the largest by a factor $n^{1/2}$, and no argument in the canon uses this yet.

A writer who is short of room is tempted in two directions. One is to keep every fact and press the words together: "Induction blocked at short-interval log loss (SIL); endpoint slack $n^{1/2}$ unused." A session that has not read the earlier text cannot read this. It has to guess what is blocked, what "SIL" abbreviates and which slack is meant, and the reason for the loss, which was the part it could have used, is gone. The other direction is to keep the sentence and let its content go: "The inductive approach meets difficulties with certain sums." This is true and reads smoothly, and a session can do nothing with it. Each of the two took a paragraph that did its work and left one that does not, to save about two hundred characters. The paragraph should have stayed as it was. Space for it is made by taking out something whole that the canon holds in another place: the list of the ranges in which the bound was verified, for instance, which the record of the verifying element gives, or the story of a second approach that its approach entry already tells.

Those two are the most frequent forms of one failure, and the failure takes other forms as well: a name coined for the occasion and then used as if the reader knew it; a noun phrase that packs a process into three words; a row of element names with nothing said of what each contributes; a "see `X`" standing where the explanation was the point; a claim that stays while the range or the hypothesis that made it true is dropped; a "so" or a "because" removed, so that two facts stand side by side without their relation. In each of them the cost of the shortening has been moved from the writer to the reader, and the reader of this text is every session. [How this user likes to be written for](user-writing-preferences.md) describes the same thing from the side of the user who reads the research: plain writing shows all of what it has to say, and compressing or hinting is not a way of being plain. Whatever stays in the account therefore stays at the length its content needs. Its objects are introduced before they are used, its claims have the exact form and scope that their elements give them, and the step from each claim to the next is written out. This holds most of all for the passages that carry the account's own subject. Where the root is held up, and why there, is told with the particulars that let a session act on it: the step that fails, the example that shows the failure, the quantity that is lost and the reason it is lost. Those particulars are what the account exists to give, and no space is saved on them; that this part takes the largest share of the room is to be expected.
