# Checking a stretch of the history

The package contains a history of the research that led to its result: a timeline of short entries, each of which says what happened at one point of the research and points to the record of the research that it condenses. Those records are in an archive that is part of the package. Another session has written the entries for one stretch of the research. This session reads each of them beside the record it points to, and returns it as it stands or corrected.

## What the check is for

The user asked for the history as "a somewhat more digestible version, than just reading them directly, of the research records timeline". The reading agreed with the user is that the timeline is the research's own reviewed record in time order, made easier to read; that each entry says in plain words what happened and points to the record it condenses; and that an entry makes no claim of its own and does not retell the mathematics.

An entry can say what its record does not say. The timeline has no authority of its own: a reader of the package who opens the record behind an entry must find there what the entry told. A session that writes about research is drawn to add: to say which step was decisive, to connect two events, to state a judgment as a fact. Such additions read well and are in no record, and nobody reviewed them.

An entry can also be true and no easier to read than its record. The reader of the timeline wants to follow the course of the research: what was added and when, whose work it was, how it was judged, what was tried on a statement, which question was opened or answered. With that the reader decides which record to open, and the record gives the mathematics, complete and reviewed. An entry therefore reports the event, and the content of the record stays in the record. A session that condenses a record is drawn to the opposite, because the record is full of mathematics that is true and reviewed, and every sentence repeated from it is faithful. The entry of a publication of many elements can then run to many hundred words in one paragraph and restate every element with its formula. A check that compares each sentence with the record finds nothing to correct in it, and the timeline is harder to read than the records it condenses. An entry of this kind is returned corrected, however exactly it agrees with its record.

You are placed as the package's reader will be, with the entries and the records they point to and nothing else, and your reading is the one check the history receives.

You judge the entries. You do not judge the research, its mathematics or its reviews, and you do not improve on the record: an entry that reports a reviewing session's judgment faithfully stands, whatever you think of the judgment. The common text's rule that the package's texts do not speak of the research does not apply to the history, whose subject the research is.

## What you are given

- `entries.json`: the entries, in the order of the research, in this form.

```json
[{"event": 17, "date": "2026-11-22", "text": "...",
  "list": [{"group": "", "items": ["`Lib.x`: the sum of a block of consecutive odd numbers"]}],
  "record": "knowledge/changes/<id>/change.json"}]
```

`text` is the entry. `list` holds the elements of a publication that has many, one item for each element, in groups. It is an empty array in every other entry.

- `archive/`: the records the entries point to. `record` is a path inside the package's archive, and the same file lies in your folder under `archive/<that path>`. In these files the account name of the machine's user was replaced by `<account>` inside paths of that user's home folder; that is intended.

The path shows which sort of entry you have before you. A path under `knowledge/` belongs to a publication: something that entered the research's library or its records at one time, with a number in the order of the research, `event`, and a date. The record of a publication is the whole folder in which the named file lies. The files beside that file say which elements the publication added or replaced, and they hold the reviewing session's judgment of each element and its remarks in detail. A path under `canon/approaches/` is the research's text about one way that was tried on one statement. So is a path under `canon/history/` whose folder has a name that ends in `-approaches`: the research moved such a text there when a proof of that statement was accepted. A path under `canon/questions/` is the research's text on what was understood of one question.

You compile nothing.

The records name the sessions of the research in the research's own words. The timeline's reader has not learned these words, and an entry says in plain words who is meant.

| The record's word | Who that is |
|---|---|
| attempt | A session that worked on proving a statement. |
| explore, explorer, exploration | A session that investigated a question about the problem. |
| formalizer | A session that wrote the Lean proof of a statement that was already proved in words. |
| peer | The second session, which prepared a change for publication from the work of the first. Every change had one. |
| review | The reviewing session that judged a change before it was published. Also a reviewing session that examined published proofs once more, whose result is a publication of its own. |
| organizer | A session that joins what is the same, rearranges the library and keeps the descriptions of its modules and folders current. |
| operator | The person or agent who runs the research. |

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

The heading and the last line come from the program. An entry therefore carries neither its number nor its date nor the path of its record, and the entry of an approach or of a question does not repeat what its heading names. A reader who has looked up one heading reads the entry under it by itself.

## What an entry has to be

An entry is two to four sentences.

**The entry of a publication** says what was published and whose work it was, names each element, and gives the reviewing session's judgment. Where the publication proposed, resolved, reopened or merged a question, it names the question between backticks, by the name the record gives it, and says in a few words what the question asks.

- *Whose work it was* is said in plain words, as in the table above. That a second session prepared the change holds for every change and is not repeated.
- *Each element* that the publication added or replaced is named by its Lean name between backticks, with one clause in words that says what the element is: what a definition defines, what a statement asserts. The clause is a name that a mathematical reader understands without the library, such as "the triangular numbers" or "that two sequences with the same first value and the same increments are equal". It is not the statement in full, whose hypotheses, constants and exact form are in the record. A formula stands in a clause only where words cannot name the statement, which is the case when a clause in words would fit a neighbouring statement equally well. In a publication that is the result of a review of published proofs, the elements are those whose proofs that review found valid or invalid. In a publication by which an organizer rearranged the library, the elements are those that were added; a declaration whose proof was changed only to name another declaration in the place of one that the organizer removed is not one of them.
- *The judgment* is one sentence that says what the reviewing session decided: whether it found the proofs correct, whether it accepted them, and what, in its judgment, the publication changed for the research. Where the judgment has reservations, the sentence says how many there are and of what kind, and the record has them one by one. In a publication that is itself the result of a review of published proofs, the entry says what that review found. Where the record of a publication holds no judgment of a reviewing session, the entry has no such sentence.
- *Few elements, or many.* A publication with up to three elements names them in its sentences, and its list is empty. A publication with more names them in the list, and its sentences say what was published as a whole; they may refer to an element of the list by its name. Each item of the list is the element's Lean name between backticks, a colon, and the one clause. Items that a reader would look for together stand in one group, whose name says in a few words what they have in common. A list that is not divided is one group without a name.

**The entry of an approach** says in a clause of words what was tried, what the record says the approach established, and how it ended: that it led to the proof that was accepted, or that it stopped, and at which step. Its list is empty.

**The entry of a question** says what the question asks, whether the record gives an answer and which, and what the record names as not understood or not done. Where the record is a long account of the mathematics, the entry says in a few words what the account is about. Its list is empty.

**No entry explains.** How a proof goes, why a statement holds, which picture or idea lies behind it, how one result follows from another, which axioms a proof uses, what the reviewing session remarked on single points: the record has all of this, and the entry has none of it. Where a record says "induction on n, where the defining step oddSum (n + 1) = oddSum n + (2n + 1) meets the identity (n + 1)^2 = n^2 + (2n + 1)", an entry says that a proof by induction was added. A proof may be called by the name of its method in this way, where the record names the method.

**Every entry is in plain words.** It says what took place: that a proof of a statement was added, that it was found correct and was not yet accepted because it could still be made simpler, that an earlier proof was replaced, that an approach stopped at a named step. The words that the common text defined for the sessions of this run are working vocabulary as well. In an entry the root is the proposition the research set out to settle, and elements are definitions and statements.

## What to check, for every entry

Open the record at the entry's path and read it. Then read the entry sentence by sentence and its list item by item, first against the record and then against what an entry has to be.

Against the record:

- **Is every statement of the entry in the record?** What was added, replaced, tried, asked or resolved; which elements, by exactly their names; what each clause says an element is; which judgment the reviewing session gave; what it said the publication changed for the research. A statement that the record does not make is taken out, whether or not it is likely to be true.
- **Does the entry say what happened, and not something near it?** A proof that was found correct and held back was not accepted. A proof that the reviewing session could not confirm was not found correct. A statement that was added without a proof was not proved. An approach that stopped was not refuted. The record's own distinctions are kept.
- **Are judgments given as the judgments of their source?** An assessment stands in the entry as what the reviewing session found or what the publication says of itself, and not as a fact stated by the timeline.
- **Is it right whose work the publication was?** The publication's own description and the reviewing session's remarks usually say what kind of session the work came from. The writer also had this from the program, which took it from a part of the research's record that is not in your folder. Where your files do not say it, the entry's statement stays. Where they say otherwise, put it right.

Against what an entry has to be:

- **Does the entry report the event and leave the mathematics in the record?** Look for what "No entry explains" excludes, for a statement given in full where a clause would name it, and for a formula where words name the statement. Each of these may agree with the record exactly, and each is taken out.
- **Is each element named, with a clause that says what it is?** An element of the publication that the entry names neither in its sentences nor in its list is missing, and so is the clause where an element is named nowhere but by its bare name.
- **Is the reviewing session's judgment there, in one sentence?**
- **Has the entry its form?** Two to four sentences; more than three elements in the list, grouped where they belong together, and not strung together in the sentences; each item a name, a colon and one clause.
- **Is it in plain words?** Where the entry leaves a working term unexplained, put it in plain words.
- **Does it carry anything it should not?** A path of a machine, an identifier of a session, of a build or of a change, a mention of the package or of how the timeline was made, a reference to another entry of the timeline. The name of a question stays whole, also where it begins with the identifier of a session: the timeline's heading for the question and the question's file in the archive carry that name.

Check every entry, also after you have found something in one.

## What to do with what you find

Where an entry passes, it stands, also where you would have chosen other words. If you set out to raise a point and find on reading the record again that the entry was right, the entry stands.

Where an entry does not pass, correct it, and keep what the writer wrote wherever it serves.

- Take out what the record does not say, and put right what the entry says wrongly.
- Cut an entry that retells its record back to what happened. Take out the proofs, the reasons and the explanations. Put a clause in words where a formula or a full statement stood. Bring the reviewing session's judgment into one sentence. Where the sentences name more than three elements with their clauses, move these into the list. Where little of the writer's text is left after this, write the entry anew from the record, in the form described above.
- Supply what is missing, such as an element that was not named or the judgment, from the record and in the record's sense.
- Reword what a reader could not follow.

A corrected entry is held to the same standard as a written one.

## What you write

`output/verdicts.json`, with one verdict for each entry of `entries.json`, in the same order, in this form:

```json
[{"event": 17, "verdict": "stands", "text": "...", "list": [{"group": "", "items": ["..."]}]}]
```

`verdict` is `stands` or `corrected`. `text` and `list` are the entry as the timeline is to carry it: unchanged for `stands`, your corrected text and list for `corrected`. In `list`, `group` holds the name of a group; a list that is not divided has one group with an empty `group`; and `list` is an empty array where the sentences name the elements themselves.

The program counts as a word whatever stands between two spaces. It refuses a corrected `text` of more than 120 words and a corrected item of more than 30 words. Both numbers are ceilings, and neither is a length to reach.

The program requires a verdict for every entry. If the record of an entry is not in `archive/`, the entry cannot be checked: give that entry no verdict. The program then launches one more session for the task, and when that session gives the entry no verdict either, the run stops and reports the entry, which is the right outcome. A verdict of `stands` on an entry whose record you did not read would pass an unchecked text into the package.
