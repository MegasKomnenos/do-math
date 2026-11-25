# Writing a stretch of the research's history

The package contains a history of the research that led to its result: a timeline that a reader can go through from the first event to the last. It also contains an archive with the research's own records, as the research wrote them. This session writes the entries of the timeline for one stretch of the research, at most twelve events in order. Other sessions write the other stretches at the same time, and the program lays all entries out in one file.

## What the timeline is for

The research kept a careful record of itself. Each change to its library was published with a title and a description, a reviewing session wrote a judgment of it with reasons and said what the change contributed, and the approaches tried on each statement and the understanding reached on each question were kept as texts. That record is complete, and it is hard to read: it is spread over a great many files, written for the sessions of the research in their working vocabulary, and nothing in it tells a newcomer which file comes next. The user asked for the history in these words: "a somewhat more digestible version, than just reading them directly, of the research records timeline".

The reading of those words that was agreed with the user has four parts.

- The timeline is the research's own reviewed record in time order, made easier to read. It is written from that record only.
- Each entry says in plain words what happened.
- Each entry points to the record it condenses, so that a reader who wants the substance opens that record in the archive.
- An entry makes no claim of its own and does not retell the mathematics.

Two requirements follow from this reading, and an entry has to meet both.

The first requirement is that the timeline has no authority of its own. Everything an entry says is something the record says. A session that writes about research is drawn to do more: to say which step was the decisive one, to connect two events, to tell the story as a story. Each of these adds something that no record contains and that nobody reviewed, in a package whose other texts were all checked against their sources.

The second requirement is that an entry is easier to read than the record it condenses. The reader of the timeline wants to follow the course of the research: what was added and when, whose work it was, what the reviewing session made of it, what was tried on a statement and how far it came, which question was opened or answered. An entry that tells this lets the reader decide which record to open, and the record then gives the mathematics, complete and reviewed. So an entry reports the event, and the content of the record stays in the record: its proofs, its reasons, its explanations, its formulas.

The second requirement is the harder one to keep, because breaking it feels like care. A record is full of mathematics that is true and reviewed. Each sentence of it can be repeated in an entry without adding a claim, and a session that wants to be faithful and complete repeats it. In an earlier run, the entry for a publication of nineteen elements was a single paragraph of more than nine hundred words, which restated every element with its formula and the reviewing session's remarks one by one. Each of its sentences was in the record, and the entry was harder to read than the record itself. An entry is faithful when what it says is in the record. It is not asked to carry what the record carries.

After you, a second session reads each entry with nothing but the record it points to. What the record does not say it takes out, and an entry that retells its record it cuts back to what happened.

This text is one of the two in the package whose subject is the research, so the rule of the common text that the package's texts do not speak of the research does not apply to it. It may speak of everything the record reports, including approaches that the package's proof does not use. It does not speak of the package or of this run.

## What you are given

- `ledger.json`: your events, in the order of the research, in this form.

```json
[{"event": 17, "date": "2026-11-22", "kind": "change", "by": "explore", "title": "...", "description": "...",
  "elements": ["Lib.x"], "review": "...", "contribution": "...", "questions": ["..."],
  "record": "knowledge/changes/<id>/change.json"}]
```

A program extracted each line from the record that `record` names. A field that does not apply to a line is empty. The lines are of two sorts.

A line of the first sort is a publication: something that entered the research's library or its records at one time. It has a number in the order of the research, `event`, and a date. Its `kind` says what was published.

| `kind` | What was published |
|---|---|
| `change` | A change to the library: definitions, statements and proofs that were added or replaced, with their records. |
| `review` | The result of a reviewing session that examined once more proofs that had already been published. |
| `organization` | A rearrangement of the library by a session that joins what says the same. |
| `questions` | Questions that the operator put to the research. |

`title` and `description` are the publication's own words about itself. `elements` names the elements it added or replaced; for a `review`, it names the elements whose proofs that review found valid or invalid. `questions` says which questions the publication proposed, resolved, reopened or merged. `by` is the kind of session whose work the publication carries, in the research's own word, and it is empty where the record does not say.

| `by` | Whose work that is |
|---|---|
| `attempt` | A session that worked on proving a statement. |
| `explore` | A session that investigated a question about the problem. |
| `formalizer` | A session that wrote the Lean proof of a statement that was already proved in words. |
| `organizer` | A session that joins what is the same and rearranges the library. |
| `operator` | The person or agent who runs the research. |
| `review` | A reviewing session that examined published proofs once more. |

Every change was prepared for publication by a second session, which the records call the peer, and was judged by a reviewing session before it was published. `review` holds the reason that the reviewing session gave for its judgment, and `contribution` holds what, in its judgment, the change contributed to the research. In a publication of the kind `review`, `review` holds what that review found.

The lines of the second sort follow the publications and have no date. A line of the kind `approach` is what the research kept about one way that was tried on one statement: `elements` names the statement, `title` is the title the research gave the approach, and `description` is the research's text about it. A line of the kind `question` is what the research understood of one question: `questions` names the question, and `description` is the research's text on it.

- `archive/`: the records these lines point to, at the paths the ledger gives. `record` is a path inside the package's archive, and the same file lies in your folder under `archive/<that path>`. For a publication the record is the whole folder in which that file lies: the files beside it hold the reviewing session's judgment of each element and its remarks in detail.

Read the ledger in full. For each line read its record in `archive/` before you write, because the ledger line is an extract and the entry answers to the record. If a record is missing from `archive/`, write the entry from the ledger line alone and keep to its words.

In the archive, the account name of the machine's user was replaced by `<account>`. Leave such places alone, and put no path of a machine into an entry.

## How an entry stands in the timeline

The program lays the entries out under headings, so that a reader can find a date or a publication at a glance.

```markdown
## Publications

### 2 · 2026-11-21 · change

<text>

- **<group>**            (the line is left out when the group is empty)
  - `Lib.x`: <clause>

Record: `knowledge/changes/<id>/change.json`

## What was tried on each statement

### `Lib.statement`: <title of the approach>

<text>

Record: `canon/approaches/...`

## What was understood of each question

### Question `q0`

<text>

Record: `canon/questions/q0.md`
```

You supply `<text>` and, for a publication with many elements, the list under it. The heading of a publication gives its number, its date and its kind. The heading of an approach gives the statement and the title of the approach, and the heading of a question gives the question's name. The last line gives the path of the record. An entry repeats none of these.

A reader who has looked up one heading reads the entry under it by itself. Each entry therefore says what happened in terms that need no other entry.

## What an entry says

An entry is two to four sentences. It reports, and the record explains. How a proof goes, why a statement holds, which picture or idea lies behind it, how one result follows from another, which axioms a proof uses, what the reviewing session remarked on single points: a reader finds all of this by opening the record, and none of it stands in an entry. Where a record says "induction on n, where the defining step oddSum (n + 1) = oddSum n + (2n + 1) meets the identity (n + 1)^2 = n^2 + (2n + 1)", the entry says that a proof by induction was added. A proof may be called by the name of its method in this way, where the record names the method. Its steps are the record's.

### The entry of a publication

The entry of a publication says what was published and whose work it was. It names each element and says in one clause what the element is. It gives the reviewing session's judgment in one sentence. Where the publication proposed, resolved, reopened or merged a question, it says which question and, in a few words, what the question asks.

**Whose work it was.** Say it in the plain words of the table of `by` above. Where `by` is empty, the entry does not say whose work it was. Where `by` holds a word that the table does not have, say what the record itself says about where the publication came from. That a second session prepared the change holds for every change, and an entry does not repeat it.

**The elements.** Name each element of the line's `elements` by its Lean name between backticks, and follow the name with one clause in words that says what the element is: what a definition defines, what a statement asserts. The clause is a name that a mathematical reader understands without the library, and you take it from what the record says of the element. Three clauses of this kind are "the triangular numbers", "that two sequences with the same first value and the same increments are equal", and "a check of the definition on its first six values". The clause is not the statement in full. The hypotheses, the constants and the exact form are in the record and in the library, under the name that the entry gives. A formula stands in a clause only where words cannot name the statement, which is the case when a clause in words would fit a neighbouring statement equally well. The clause then carries the shortest formula that tells the two apart.

**The reviewing session's judgment.** One sentence says what the reviewing session decided: whether it found the proofs correct, whether it accepted them, and what, in its judgment, the publication changed for the research. Keep the distinctions that the record makes. A proof that was found correct and accepted differs from a proof that was found correct and held back, for instance because the reviewing session saw how it could clearly be made simpler. A proof that the reviewing session could not confirm was not found correct. A statement that was added without a proof was not proved. Where the judgment has reservations, the sentence says how many there are and of what kind, such as two proofs held back or four overstatements in an account, and the record has them one by one. The sentence gives the judgment as the reviewing session's, with words such as "the reviewing session found" or "in its judgment". In a publication of the kind `review` the judgment is itself what was published, and the entry says what that review found of the proofs it examined. Where the record of a publication holds no judgment of a reviewing session, the entry has no such sentence.

**Few elements, or many.** A publication with up to three elements names them in its sentences, and its list is empty. A publication with more elements names them in the list, one item for each element, and its sentences say what was published as a whole: how many elements and of what kind, whose work it was, what the reviewing session judged. The sentences may refer to an element of the list by its name, for instance to say which proofs were held back. The reason for the list is how a reader uses the names. A name with its clause is something a reader looks for singly. In a list the eye finds it, and in a paragraph that strings twenty names together the reader has to start at the beginning. Put the items that a reader would look for together into one group, and say in a few words what they have in common, for example the subject they share. A list that has no such division is one group without a name.

### The entry of an approach

The heading already names the statement and the approach. The entry says in a clause of words what was tried, what the record says the approach established, and how it ended: that it led to the proof that was accepted, or that it stopped, and at which step. Keep to the record's word for how it ended, since an approach that stopped was not refuted. The idea is named, as an element is named, and the account of it stays in the record. The list of such an entry is empty.

### The entry of a question

The heading already names the question. The entry says what the question asks, whether the record gives an answer and which, and what the record names as not understood or not done. A record of this kind is often a long account of the mathematics. The entry says in a few words what that account is about, and the account itself stays in the record. The list of such an entry is empty.

### What holds for every entry

Use plain words. The record speaks in the vocabulary of the research's own procedure, and a reader of the package has not learned it. Say what took place: that a proof of a statement was added, that it was found correct and was not yet accepted because it could still be made simpler, that an earlier proof was replaced, that an approach stopped at a named step. The words that the common text defined for the sessions of this run are working vocabulary as well, and the reader of the timeline has not read that text. In an entry the root is the proposition the research set out to settle, and elements are definitions and statements. Identifiers of sessions, of builds and of changes are not needed in an entry, because the line under the entry gives the path of the record.

Attribute judgments to their source. That a proof is correct, that a step was the important one, that an approach failed for a certain reason: these are the reviewing session's statements or the publication's own, and the entry says whose they are. Add no assessment of your own, however evident it seems from where you stand, and no connection between events that no record draws.

Where a record refers to an earlier publication, the entry may say so as the record does. It does not refer to other entries of the timeline, since you see only your own and cannot know what the other sessions write.

## What you write

`output/entries.json`, with one entry for each line of the ledger, in the same order, in this form:

```json
[{"event": 17, "date": "2026-11-22", "text": "...",
  "list": [{"group": "", "items": ["`Lib.x`: the sum of a block of consecutive odd numbers"]}],
  "record": "knowledge/changes/<id>/change.json"}]
```

- `event`, `date` and `record` are copied from the ledger line exactly.
- `text` is the entry, two to four sentences.
- `list` holds the elements of a publication that has more than three. Each item is the element's Lean name between backticks, a colon, and its one clause. `group` holds what the items of a group have in common, and it is empty in a list that is not divided, which has one group. `list` is an empty array when the text names the elements itself, and for every approach and every question.

The program counts as a word whatever stands between two spaces. It refuses a `text` of more than 120 words and an item of more than 30 words. Both numbers are ceilings, and neither is a length to reach. A text that would pass 120 words is carrying something that belongs to the record. The program also requires that every entry has a path that is a member of the archive.

Before you end, read each entry beside its record once more, and ask three things of it. Where does the record say this sentence? Does any sentence or clause prove, derive or explain something, so that it can go and the reader still knows what happened? Would a reader who has only this entry know what was published, whose work it was and how it was judged, and which record to open for the rest?
