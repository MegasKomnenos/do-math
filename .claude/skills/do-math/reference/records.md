# The written texts of the canon: records, approach entries, understanding texts and descriptions

Beside its Lean library the canon keeps what Lean cannot hold: a record for each declaration, the approaches tried on a statement whose proof is not accepted, the understanding so far of each question, and a description of each module and each folder. The common introduction says what each of these is for. This guide gives their formats, the criteria for the weight of an element and, under "Writing the texts of the canon", how each text is written so that a later session can use it. The line of a module and the description of a folder have a section of their own, "The module line and the folder description", which gives their form, the standard they are written to and the test they are put through.

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
| `## Literature` | For a result taken from the literature: the source, how much of it was read, and where the statement stands in what was read. For a statement that works of the literature pose or have earlier results on: those works, each cited by its key, with what it has of the statement and how much of it was read. |

The self-description is the only part of the record that views of many elements show, so it has to be understandable without the rest. It is the lowest level of the index of the canon, and it is all that a search of the canon reads of the element. Say what the statement asserts or what the definition defines, completely enough that a session looking for that fact recognizes it. It is not the place for the element's history or for its role in some proof: a description such as "a lemma for the main estimate" tells a session that is choosing what to open nothing about the element.

A statement counts as having a proof when its Lean proof is complete or when its record has a nonempty `## Proof`. Whatever stands under that heading is therefore offered as the proof, and review judges it as one. For a statement established by an exact computation, the proof is the account of that computation: what was computed, over which range and in which arithmetic, with the code and its output among the files of evidence. An idea of why the statement should hold belongs under `## Explanation`. An argument that got part of the way belongs among the approaches tried, described below.

The explanation follows a criterion the user gave: an explanation that is attributed to a mathematical object is kept with that object. The reason a definition counts from zero is kept in the record of that definition, and what a lemma shows about a sequence is kept in the record of that lemma, not in the record of the theorem in whose proof the question first came up. An account of how a session arrived at the statement does not belong to the object. What does belong to it may well have been learned on the way: that a weaker form fails, with the case in which it fails, is something a reader of this element needs.

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

A statement whose proof is not accepted carries the approaches that were tried on it, one file for each approach, at `approaches/<Name>/<id>.md`. `<Name>` follows the name of the statement the approach was aimed at. `<id>` is a short identifier of letters, digits, `_` and `-`, beginning with a letter or a digit, chosen by the first author of the entry and kept when the entry is replaced.

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

## The module line and the folder description

Above the self-description of an element the canon keeps a description of each module and of each folder. The three levels together are the index of the canon, which the common introduction describes under "Reading the canon". A session reads one level of the index at a time and decides from the names and the descriptions of that level which item to open. What it does not open it does not see, so the description of a module or a folder decides whether the mathematics beneath it is found.

### Their form

The **module line** is the description of a module. It is one paragraph, a line or two, in the file `descriptions/modules/<Module>.md`. The **folder description** is the description of a folder. It is one or more paragraphs, with no fixed maximum, in the file `descriptions/folders/<Folder>.md`. The path follows the name, one component for each part of it: the line of the module `Tri.Bounds.Gap` is `descriptions/modules/Tri/Bounds/Gap.md`, and the description of the folder `Tri.Bounds`, which is the directory `lean/Tri/Bounds/` of the library, is `descriptions/folders/Tri/Bounds.md`.

A module line:

```text
The difference of two consecutive triangular numbers, and its comparison with n: the exact value of the difference, and the bounds on it that the estimates of this folder use.
```

A folder description:

```text
Bounds on the triangular numbers and on sums of them: upper and lower estimates, each with the range of n on which it holds. The estimates compare a triangular number with squares, with powers of two and with its neighbours.

A session that needs to compare a triangular number with a square or with a neighbouring one finds the comparison here, and so does one that looks for the range in which such a comparison fails.

Boundary: the two modules on the parity of triangular numbers were filed here with the bounds they were first used for. They are about divisibility and would belong with the folder Tri.Parity.
```

Both are plain text without a header. No line begins with `#` or with three backticks, because the text is shown inside views that have headings of their own. A module line has no empty line inside. A paragraph that begins with `Boundary:` has a meaning of its own in a folder description, which "A folder that does not follow a natural boundary" below gives; in a module line the word has no such meaning. The canon stores each text with the blanks at the ends of its lines removed and one empty line between paragraphs, and a listing prints each paragraph on one line.

The peer that adds a module writes its line. The organizer writes the description of each folder, and the line of a module that has none.

### The standard

The user who runs this research set the standard in two statements. The first says what a description has to achieve: "it should be sufficient at providing the sessions with knowledge of what it can find from that folder. rule of thumb, a session who, for any purpose, would want to and benefit from knowing what lies below must be able to be aware of that existence by the description above". The second says how a description is written: "the folder must follow a natural boundary, and the description must be able to be grown. but, it must also be written such that the folder size does not necessarily increase its description size. e.g. a topic that contains a lot of info can still be described sufficiently with simple statements, on what it is, what it is needed for, what it can do, what it is doing. etc etc". The user spoke of folders. The first statement is applied in the same way one level down: the line of a module is sufficient when a session that would want what one of the module's elements holds can tell from the line that it is there.

The first statement speaks of any purpose, and the purposes of the sessions that come later are not the purpose of the session that wrote the mathematics. A module may have been written as a step toward one proof. A later session comes to it for a base case, for a tool, for a definition it was about to introduce, for a counterexample that closes the approach it had in mind, or to see where an earlier line of work stopped. A description that says only what the material was made for serves the first of these readers and none of the others. So a description says what lies beneath as mathematics: which objects it is about, what is established or stated about them, and in which range or under which hypotheses.

The second statement says how this is done without the description growing with every module. A description characterises its topic, and it does not list the contents. A list of the modules of a folder has to be extended with each new module, and it tells a reader nothing about a thing that is not yet on it. Statements of the kind the user names, what the topic is, what it is needed for, what can be done with it, what is being done in it, let a reader infer whether a given thing must lie beneath, including a thing that was added after the description was written. The user's list is open, and other statements serve in the same way: which objects the part is about, which kinds of result it holds, which methods it develops, how it stands to the root. Which of them a given folder needs is a judgment about that folder.

It follows that the size of a folder does not decide the length of its description. A folder that holds hundreds of elements about one topic can be characterised in a few sentences, because every one of those elements is an instance of what the sentences say. A small folder whose modules have little in common needs a sentence for each kind of thing it holds. For the same reason a folder is not divided because it has become large, and a description has no fixed maximum: when a folder receives material that its description does not let a reader expect there, the description gains the statement that covers it.

The words of a description matter as much as its content, because the reader comes without the canon's vocabulary. A session that is looking for a fact has its own words for it, and it meets the names that earlier sessions coined only when it opens the element. A description that says what a folder holds by the Lean names of its definitions tells such a reader nothing. Say what each thing is in the ordinary language of the mathematics, and add the canon's name where a reader who does know it would look for it.

A module line is held to the same standard at a smaller scale. It says what the declarations of the module establish and about which objects, so that a session which needs any one of them recognises that it is there. The reader of a line is choosing among the modules of one folder, so the line has to tell its module apart from the modules beside it: what this module holds that they do not.

### A folder that does not follow a natural boundary

The second statement begins with a condition on the folder itself: "the folder must follow a natural boundary". A folder follows a natural boundary when what it holds is one part of the mathematics, so that statements of the kind above can characterise it. A folder can fail this. It may hold two topics that have nothing to do with each other, or part of a topic whose other part is filed elsewhere.

Such a folder is described as it is. The description says what the folder holds, also where that is mixed, so that a session is led to everything that is in fact there. It then ends with a paragraph that begins with `Boundary:` and says in what the folder departs from a natural boundary and where the material would belong, as the example above does. The label stands at the head of the last paragraph and nowhere else, it is followed by text, and it is never the whole description. A session that reads the level sees the paragraph and knows that the folder holds more than its name suggests, and `index --due` lists every folder that carries one, for the organizer. The paragraph stays until an organizer has moved the modules to where they belong and rewrites the description without it.

### The blind descent test

Whether a description leads a reader to what lies beneath is tested before the description is published. In the **blind descent test** a reader is given one level of the index, the level in which the item under test stands: the names and the descriptions of the folders and the modules of that level, without counts and without anything of what lies inside them. It is also given a purpose in plain words. It names the items it would open for that purpose, at most five, and the description passes for the purpose when its item is among them. The reader is a model without tools that has been given the level and the purposes and nothing else, so it cannot know more than the descriptions say. The writer of the description supplies the purposes and has the test taken, the peer for the line of a module and the organizer for the description of a folder. A module line is tested on at least one purpose and a folder description on at least three different ones. [The candidate change](change-format.md) gives the file of the purposes, the command and its receipt under "The blind descent test".

The test is taken at the level, among the neighbours. A description can be accurate and still fail, because the description of the folder or module beside it reads as the better place for the purpose. That failure is a true finding about the level: a session with that purpose would have opened the neighbour.

What the test shows depends on whether the purposes are fair. A fair purpose is drawn from what lies beneath. Take an element of the module, or a module of the folder, and write what a session would be looking for, or about to work out, when that element is what it needs. Write it in the words such a session has before it has found the element: its own description of the mathematics, without the name of the declaration, the name of the module, or the phrases of the description under test. A reader that is handed the description's own words finds the item whatever the description fails to say, and the test then shows nothing. Draw the purposes for a folder from different parts of what it holds, and include the part that is least like the rest, since the standard speaks of any purpose and the material that a description most easily fails is the material that does not fit its first sentence. A purpose also has to ask for something the item holds. When the reader does not open the item because the purpose asks for something that is not there, the purpose is what needs correcting.

When a purpose fails, the answer names the items the reader opened instead. Read them as what the level told the reader. Usually the description lacks a statement from which the need could be inferred, or it says the thing in terms that a session without the canon's names does not connect with its need. Rewrite the description so that it says what the folder or the module holds for purposes of that kind. Copying the phrase of the failed purpose into the description makes that one purpose pass and leaves the next purpose of the same kind where it was.

## Writing the texts of the canon

The texts of the canon differ from an account written from beginning to end. No reader goes through them in order. A session opens the element its work concerns and reads that element by itself, having seen of the others only a line each. Each text therefore has to do its work alone, and each kind of text has a different job.

The **statement in words** says what the Lean statement says, in the ordinary conventions of mathematics. Where the Lean form differs from it, for instance by counting from zero or by a normalization, say so in the explanation, so that a reader can pass between the two.

The **proof** is written so that it can be read for this element by itself. Refer to every other element the argument uses by its Lean name, and say what that element gives at the point where it is used, so that the reader does not have to open it in order to follow the step. Use notation the record itself introduces. Where the element has a Lean proof, the proof in the record is the same argument; when a formal proof takes a different route from the informal one it replaces, the proof in the record is rewritten to follow it. Inside the canon there is no continuous exposition of the whole proof. The proofs of the elements near the root are where a reader learns how the pieces beneath them combine, so write those proofs with that reader in mind, and the understanding so far of `q0` carries the account of the whole.

An **approach entry** is read by a session about to choose how to work on a statement. Tell the idea plainly enough that this session recognizes an approach it was about to take. State where the approach stops as exactly as the mathematics allows: which step fails or is missing, and what would be needed to pass it. Say what the failure excludes and what it leaves open: that one estimate falls short by a logarithmic factor excludes that estimate and not the method. Whatever the approach established exactly is named in the entry as elements and is not retold there.

The **understanding so far** of a question is one text that successive sessions maintain, written as the present state of understanding. It is not an archive of everything that was ever written under the question: the question's history is that archive, and what the canon holds in an element, in an approach entry or in the text of another question is named where the argument turns on it and not told again. How a peer writes the text is in the peer's role guide, and how review reads it against the text it replaces is in the reviewer's. Only the understanding so far of `q0`, the account of the problem as a whole, has a fixed room, because every session reads it in full at launch; [The account of the problem as a whole](q0-account.md) says what the account is for and how it is kept within its room. The texts of the other questions are read by the sessions that open them, and they are kept to what they are about for the sake of those readers.

Write formulas in LaTeX notation between dollar signs and the names of elements in backticks. The paper that presents the result at the end is produced from these texts, so a statement, an explanation or a proof that reads as mathematics there is one a reader of a paper can follow as well, and a written proof that argued otherwise than the Lean proof would put into the paper an argument that Lean did not check.
