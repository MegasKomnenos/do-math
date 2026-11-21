# do-math with a Lean canon

Design and decision record · 22 November 2026

## 1. Purpose, scope, and authority

do-math coordinates an unattended research instance around one mathematical problem. Until now the knowledge of an instance has been a repository of reviewed records written in natural language. Lean entered only at the end, when an informal solution that review had accepted was formalized. This document records a redesign in which the knowledge of an instance is a Lean library from its first session on. Every mathematical assertion the research keeps is an **element**: a Lean declaration whose statement compiles, together with a written record attached to it. Sessions find their work, and learn what is already known, by traversing the structure of that library. The dependency map of the research and the paper that presents its result are produced from the library by script.

The document is written for a reader who was not present when these decisions were made, and in particular for the agents that will implement them. It says what changes, what each change is for, what stays as it is, and which points are still unmeasured or undecided. A reader who implements one part should be able to find in the relevant section both the rule and the reason for it, because the reason is what settles the cases the rule does not name.

The existing design record, [rebuild-design.md](rebuild-design.md), remains in force for everything this document does not change. That includes its governing principles (its section 2): a mechanism earns its place by serving the research; sessions exercise judgment, including in following coordination rules; and a proposed mechanism has to say which real uncertainty or coordination problem it addresses and why knowledge, instructions, tools and trust do not suffice. Section 14 below lists what stays as it is. Where the two documents disagree, this one governs.

Three kinds of statement appear here, and they are marked where the difference matters. A **decision** was made by the user in the design conversation of 22 November 2026. An **approved proposal** was put forward by the designer and approved by the user in the same conversation. A **measurement** was taken on the development machine or on the most recent research instance. What was assumed without being measured is collected in section 16. An implementer chooses data structures, file names, command names and formats within these. Changing a decision or an approved proposal requires the user.

One constraint applies to all of the implementation work and is stated here so that it is not missed. The work changes the installed skill under `.claude/skills/do-math` and nothing else. The generated copy under `.agents/skills/do-math` must not be regenerated while the work is in progress, because a research instance is running from that copy (section 15).

### Reading map

Sections 2 and 3 give the reasons for the redesign and the whole of it in one view. Sections 4 to 6 define the canon, the standing of an element, and the frontier from which attempts choose their work; these three carry most of the design. Section 7 says where knowledge about the course of the research is kept. Sections 8 to 11 cover reading, occupancy, publication and the organizer. Section 12 reports what was measured about running Lean. Section 13 covers the dependency map and the paper. Sections 14 to 16 list what is unchanged, the constraints and completion criteria of the implementation, and what is still open.

## 2. What the current structure could not do

The redesign answers five observations about the most recent instance, which had run for three days and published 66 records when it was examined.

**The graph held a small part of the mathematics.** The current system represents a statement worth settling as a **node**, admitted by review, and a proved implication between nodes as a **relation**. The instance had 24 nodes and 27 relations. Almost all of its mathematics was elsewhere, in 2,031 **claims**: the numbered assertions inside a record that review judges one by one. Claims depend on one another (6,135 recorded dependencies), but a claim is identified by its record, so the same fact stated in two records is two claims, and no single entry stands for a proposition. Each claim restates the notation it needs, and the median claim statement was 769 characters long.

**Knowledge was organized by the session that produced it.** A published record is the account of one session's work: what it established, the approaches that failed, the obstacles it met and what remains. The mathematical content and the course of the work are in one unit, and a later session reaches a result through the record of the session that found it.

**Sessions learned what exists by reading prose.** Every session received the views of the repository in full at launch, between 430 KB and 990 KB of text, and then searched the record folders. A structured copy of the state existed, and every reviewing session opened it, but nothing let a session ask a question of it. In the research before this one, one record re-derived three results that earlier records had published, without citing them.

**The map and the exposition were made after the research.** For the previous research, a dependency map of the proof and a long exposition were produced when the research was over, by agents that read the records again and extracted which statement uses which. The information a map needs was not in the record format: a stable identity for each statement, its kind and short name, the uses with their grounds, and the judgment of which statements are units of the proof and which are steps inside one.

**Lean was used at the end only.** Formalization began once an informal solution was accepted and lay on a path to the root. Attempts submitted three Lean compiles in three days and explorations none. Lean sources were copied into the record that used them, so the instance had no library of its own.

## 3. The design in one view

The canon of an instance is one Lean library with a written record beside each declaration. An **element** is a declaration of that library together with its record. A definition is an element. So is a statement, whether it has a formal proof, an informal proof that names in Lean the elements it rests on, or no proof yet. Only what has a Lean statement is an element, and a proof can use a result of the research only if that result is an element; beyond the elements a proof uses the imported library and nothing else. The intended direction is that sessions state what they find in Lean and so keep it, not that what was left unstated is dropped: stating is part of doing the mathematics, from the first session on, and the root itself is fixed in Lean when the instance is created.

The table sets the objects of the current system beside what does their work in this design. Nodes, the glossary, the index with its surveys, and the published record of a session have no counterpart as separate objects; relations and claims become elements. The roles mentioned are those of the current system, which remain: an attempt, an explorer or a formalizer produces work; a **peer** takes that work over, continues it and writes what is to be published; **review** judges it independently; an **organizer** maintains the repository.

| In the current system | In this design |
|---|---|
| A **node**: a statement that review admitted as something to settle. Attempts choose among nodes. | No separate object. The **frontier** is a view derived from the root downward: the ways the root is proved and the elements those proofs rest on, each with its standing (section 6). An attempt chooses its work there, and occupancy attaches to the element it takes on (section 9). |
| A **relation** between nodes, with a rule that derives the standing of one node from others. | A statement whose proof names, in Lean, the elements it rests on. Standing is computed along those uses (section 5). |
| A **claim** inside a record, identified by the record. | An element, with one identity in the library. |
| The **glossary**: terms local to a record, some raised to a shared list by a procedure of candidacy and promotion. | Definitions are elements like any other and are met through the statements that use them (section 4.5). |
| The **index**: records grouped into modules by the organizer, each module with a written survey. | A derived view that shows what the records say about themselves. No survey is written (section 8). |
| A **published record** for each producing session. | No publication per session. Results enter as elements. What a session learned about the course of the work enters as state attached to what the work was aimed at (section 7). The session's own account is retained outside the canon. |

What review judges is unchanged in kind and moves to the element. Review judges whether an element's proof is correct and, separately, whether a correct proof is accepted; a correct proof that can clearly be made simpler, or that closes part of the statement by large computation done without understanding, is published and can be used, and the element stays among the work that remains. An element is settled when its proof is accepted and everything it rests on is settled.

Sessions read the canon through a command that traverses the Lean structure and returns, for each element, one view joined from the compiled library and the record. A traversal is determined by its starting point and its rule, so its result is the whole of what the rule selects and can be reproduced by another session.

Publication rests on one rule: a statement is never changed in place. New elements are added in new modules. A better proof of the same statement replaces the old proof where it stands. A statement that supersedes another enters under a new name, and the old element remains as a one-line consequence of the new one. A candidate that was frozen for review therefore keeps what it rests on while it waits: every statement it uses still stands as it stood.

## 4. The canon: elements and their records

### 4.1 An element is a Lean declaration whose statement compiles

*Decision.* Every element has a statement that Lean compiles, and only what has such a statement is an element.

The rule has a consequence that follows from section 4.3: an informal proof names the elements it rests on in Lean, so a result that has not been stated in Lean cannot be used by any other proof. The user set the direction in which this consequence is to be met. It is not that what a session failed to state is discarded. It is that the session states it and thereby keeps it. When a session has obtained something worth keeping, stating it in Lean is that session's work, and the work of the peer that takes it over. When the objects it speaks of have no definition in the library yet, building the definition belongs to the same work.

Every kind of mathematical assertion becomes a statement. A conjecture is a statement without a proof. An observation is the exact statement of what was observed, over the range in which it was observed, with the numbers as its grounds. An explanation or an interpretation is not a statement; it is prose in the record of the element it is about (section 4.4).

*Decision.* Expressing mathematics in Lean is part of the work from its start, and is not a step added after work done in natural language. A session receives what it takes on as Lean statements and definitions. It introduces a new object by defining it in Lean, and formulates a result by stating it in Lean. The role guides are to treat this where they treat understanding a statement, deciding what to show, and retaining what was found, and not as a separate procedure at the end.

This concerns definitions and statements. Writing a complete Lean proof is a different matter and stays as it is in the current design: an attempt or a peer may write one and is not obliged to, and the final solution of the root requires one (section 5). The current guidance warns against turning the work into the formalization of easy peripheral results in order to finish with something that looks complete. That warning is about proofs and remains.

The cost of this rule lies in definitions. A statement is cheap to write when the objects it speaks of are already defined, and the cost and the risk of building faithful definitions for the objects of a given research have not been measured (section 16).

### 4.2 The root is fixed in Lean when the instance is created

*Decision.* The operator, the conversational agent that prepares an instance, writes the definitions and the statement of the root in Lean together with the user, compiles them, and fixes them with the natural-language statement once the user has confirmed them. Research begins on that basis.

The root is the user's proposition, and in the current design it is fixed for the life of the instance; a changed proposition requires a new instance. That now applies to the Lean statement. Two things follow. Completion no longer needs a separate judgment that a formal theorem corresponds to the root: the theorem to be proved is the fixed statement itself. The other conditions of completion are those of section 5. And if the Lean statement is later found not to say what was meant, the proposition has changed and a new instance is needed.

Agreement of the Lean definitions with known values is evidence of fidelity and not a proof of it. A root file usually carries values for small cases; the definitions should be evaluated on them and the agreement checked by compilation. The user's own reading of the Lean statement remains part of the confirmation.

The definitions chosen at creation may later prove inconvenient for a proof. A session then introduces another representation as a new definition and establishes, as an element, that the two agree. This is the requirement the current design already places on a formalizer that changes a representation.

### 4.3 What is in the Lean source and what is beside it

*Decision.* What Lean must check is in the Lean source. Prose is in a file whose path follows the name of the declaration.

In the source: the statement, the proof, and, for an informal proof, the names of the elements it rests on. Beside the source: everything in section 4.4. The record of the declaration `Parking.Columns.dq_col` is at a path such as `Parking/Columns/dq_col`.

Two measurements on the installed Lean 4.32.0 stand behind this division.

- The Lean broker, the service through which every compile of an instance runs, caches a compiled module under a key made from its source bytes. Prose kept in the source would recompile the module, and every module that imports it, each time the prose changed. Records of elements that remain open change often (section 7), and those are the elements most other work depends on.
- A theorem whose proof is left as `sorry` after naming the lemmas it rests on, in the form `have h := lemma args`, keeps those lemmas among its dependencies in the compiled environment, and a reference to a lemma that does not exist or does not fit is rejected by the compiler. The uses of an informal proof are therefore checked by Lean and can be read from the environment in the same way as the uses of a formal proof. The plain form is the one to use: a tactic written to do the same lost the references when the proof term was simplified.

A declaration and its record are bound by the name and by a hash of the statement; for a definition the hash is of its type, and the body of a definition is not changed in place either. A check before publication confirms that every element has both and that the hash agrees; it belongs to the transport check, the existing check of structure and references that judges no mathematics. A verdict of review is bound to the hash it saw, so a changed statement shows by itself that its record and its verdicts are to be looked at again.

*Decision.* The library is written in Lean's module system, that is, each file begins with `module`. In a module the statement of a theorem is part of the public compiled output and its proof is not. The broker's cache key for a module is to be made from the module's own source and, for every module of the library that its compile reaches, from that module's public output instead of its source bytes. Section 10 depends on this, and section 12 reports what was measured.

### 4.4 The record of an element

*Decision.* Each element has one record. Its author writes it when the element is written, and review judges it with the element.

The record holds what cannot be in Lean and belongs to this element. The following is what the design needs it to carry; the concrete format is an implementation choice, provided that the parts named here can be read separately by the traversal command (section 8).

- A **self-description**: what this element is, in a line or two. Views that pass over many elements show this as the only prose of the element.
- Its **weight**: whether the element is one of the results that a reader of the proof's structure would name, or a step inside one proof. The dependency map draws the first kind as units and folds the second, and the paper numbers the first kind and absorbs the second (section 13).
- A short name, and, where the element is another proof of a statement that already has one, which statement.
- The statement in natural language.
- **Explanation that belongs to the object**: what the statement says about the object, why it holds, why the definition was chosen, how the Lean form corresponds to the mathematical one. The criterion for what belongs here was given by the user: an explanation attributed to a mathematical object is kept with that object.
- The proof in natural language, written so that it can be read for this element by itself. Where the element has a Lean proof, the natural-language proof is the same argument (section 13.2).
- For a result taken from the literature: the source, how much of it was read, and where the statement stands in the literature that was read. Such a result is an element like any other (*approved proposal*), and the bibliographic entries of all of them are collected in one bibliography file of the canon.
- The verdicts of review and their reasons (section 5).
- For an element whose proof is not accepted: the approaches tried (section 7).

*Decision.* A record can be replaced. When A is replaced by A′, A′ is what the canon holds, and what remains of A is the difference and the path to A′. This remainder is the element's **history**. It is not shown by a traversal unless asked for, and it is kept apart from the files of the canon so that a search of the canon does not return it.

### 4.5 Definitions are ordinary elements

*Decision.* There is no glossary. A definition is an element, and its name, symbol, wording and explanation are in its record like those of any other element.

The current glossary did several things, and each is done differently now. That sessions use one name for one object is enforced by use: to use an existing definition a session must refer to it by its Lean name, and Lean rejects a second declaration of a name. Whether a new definition duplicates an existing one is judged by review when it judges the new element, for every definition and not only for those marked as shared. The procedure of candidacy, promotion and refusal has no object, since there is no separate shared list. When two definitions turn out to denote the same object, the fact is established as an element stating that they agree, and both names continue to work.

One thing the current design chose deliberately is given up. The whole shared glossary is delivered to every session at launch so that the existence of each concept is visible before a session has thought of asking for it. In this design a definition is met through a statement that uses it, or by traversal.

## 5. The standing of an element

Review makes two judgments about the proof of an element, as it now does about a proposed solution of a node. The first is whether the proof is correct. The second, made only of a correct proof, is whether it is accepted. The two considerations under which a correct proof is not yet accepted are those of the current review guide and come from the user: the proof can still clearly be made simpler, in the sense that a place in it can be pointed to and the reduction named; or it closes part of the statement by large computation carried out without an understanding of why that part holds. Each can be turned off for an instance by the existing settings.

*Decision.* Every declaration of the canon that states a proposition is in one of four states, according to the proof it carries. The states are kept for every such declaration; the frontier shows them for what the root rests on.

| State | Meaning | Work remains on this proof |
|---|---|---|
| No proof | The statement stands alone. | Yes |
| Proof not confirmed | A proof was offered and review found a gap or could not complete its judgment. | Yes |
| Correct, held back | Review confirmed the proof and did not accept it, with the reason. | Yes |
| Accepted | The proof is correct and accepted. | No |

These states concern statements. A definition has no proof and none of the four states; what review judges of a definition is whether it denotes the intended object and whether the library already has it (section 4.5).

The first three states are the work that remains, and they stand in the frontier together. A proof that is correct and held back is therefore not a special case with a procedure of its own. It is a line in the same list, taken on in the same way, and the work on it is what the current attempt guide describes: it begins from the published proof, at the place review named, and simplifies the argument there or replaces the computation by an argument that says why the part is true.

*Decision.* A hold is attached to the element in which the difficulty lies. Review's reason says where the room to simplify is, or which part is closed by which computation, and with fine-grained elements that place is usually one element. In the most recent instance, one node was established without computation for large values of a parameter and for a middle range, and read from a published table for small values; the node as a whole was shown as unresolved, and the organizer explained the situation in prose. With the three ranges as three elements, the hold is on the third alone.

*Decision.* A proof is **settled** when it is accepted and every statement it names is settled, and a statement is settled when one of its proofs is. For an element with a single proof the two coincide: the element is settled when its proof is accepted and everything that proof rests on is settled. The statements meant are those of the canon that the proof names. Definitions, and the declarations of the imported library, have no standing and do not enter the computation. This is what the current rule, that nothing is derived through a relation from a node whose solution is held back, becomes. The computation is made per statement and not per declaration: when one statement has several proofs, it is settled as soon as one of them is. Each proof keeps its own state among the four, and the frontier shows a statement with all of its proofs. Where the proofs of two statements name each other, neither settles the other: a statement is settled only through a proof whose named statements are settled without it. Which declarations are proofs of one statement is stated in their records (section 4.4), and the check before publication confirms by compilation that their statements are the same. The same means identical as Lean propositions, up to the names of bound variables; two statements that are only proved equivalent remain two elements (section 11). An element held back can still be used by other proofs, as supported claims can be cited now; what it cannot do is make them settled.

*Decision.* Review writes the judgment of acceptance for every element whose proof it reads, since it reads the proof in order to judge its correctness. What appears in the frontier as remaining work is what the root rests on. A hold on an element the root does not rest on stays in its record and comes into the frontier with the element if a later proof of the root uses it.

The result of work on an element that already has a proof is entered according to review's verdict, and review does not send work back to be repaired. Review says, for each proof a candidate would replace, whether the new proof takes the place of the old one, and the runner replaces only those. A first proof of a statement that had none enters with review's verdict, whatever it is (section 10.2).

- The new proof is correct and accepted: it replaces the old one (section 10). Proving this element is then no longer work that remains. Whether the element is settled depends, as always, on what the new proof rests on, and the standing of everything that rests on the element is recomputed.
- The new proof is correct and an improvement in the sense of the two considerations above, and room remains: it replaces the old one, and the hold stays with a reason that fits the new proof.
- The new proof is wrong or no better: nothing is replaced, and the attempt is recorded among the approaches tried.

*Approved proposal.* The obligation to prove formally is unchanged. The final solution of the root requires a Lean proof that review has compiled and audited independently, and a formalizer is launched for a settled statement that has no formal proof yet and that the root rests on. What the root rests on is here every statement reached from the root through what proofs name, whatever the state of a proof on the way and whether or not a statement on the way is settled, since the statements to formalize are the settled ones. Among the proofs that settle the statement, taken with the statement's own declaration first and the others in the order of their names, it is given the first whose named statements are all settled by formal proofs, under whichever of their declarations; until there is such a proof, no formalizer is launched for the statement. The runner reads what the formal proof will need from what the informal proof names in Lean. The root is such an element itself: once it is settled and what its proof names has formal proofs, a formalizer is launched for the root.

The mechanisms by which a later doubt is handled are unchanged and attach to elements: a **concern** is a reported challenge that annotates and changes nothing, a comprehensive review examines it, and a finding of that review can withdraw the confirmation of a proof. A statement and its negation both carrying confirmed proofs is the contested case of the current design and is handled as now.

## 6. The frontier: how an attempt finds and chooses its work

Nodes did four things. They were the list of what is open. They showed, through relations, how settling each would bear on the root. They carried a judgment made in advance, since review admitted a node only with an established connection and after weighing whether it was worth pursuing and whether its division followed the mathematics. And they were where occupancy, solutions and the launching of formalizers attached. The last now attaches to elements (sections 5 and 9). The first two are produced by traversal. The third no longer exists as a step, and its content is kept in another form.

**Finding.** The statement of the root has one or more ways of being proved. A way is a proof that names the pieces from which the root follows, and each piece has ways in turn. Starting from the root and following what each proof rests on, stopping at statements that are settled and opening those that are not, gives the frontier. A statement whose own proof is accepted is opened as long as something that proof rests on is not settled, as way 1 is in the illustration below. The proofs followed are all those a statement has, whatever their state; a proof that review did not confirm is shown as such, with what it names beneath it. A statement already shown is listed again where another proof names it, without what lies beneath it, so statements whose proofs name each other end the descent. It is a derived view; nobody writes it. The following shows its form. The ways are those recorded in the most recent instance; the standings are invented for the illustration.

```text
root   every row is unimodal                                not settled
  way 1  from (Col) and (Mono)                              proof of the way: accepted
     Col    a column difference, once nonnegative, ...      correct, held back (room to simplify) · held by 2 sessions
     Mono   the crossing row does not decrease in k         correct, held back (k <= 124 read from a table)
  way 2  from (Col) and (Diag)                              proof of the way: accepted
     Col    (shown above)
     Diag   ...                                             no proof · 3 approaches tried · held by 1 session
  way 3  from target T                                      ...
```

At the start of an instance the root has no proof, and the frontier is the root alone, in the state "no proof".

A session receives this view in its starting context, at the level of the elements whose weight marks them as units of the proof, and descends where it is interested. A step whose own proof is accepted is passed through to what it names; a step that is itself work that remains is shown. An open statement that no proof of the root uses yet, such as a conjecture left as a lead, is not in this view; it is met through the objects it speaks of or through a question (section 7).

**Choosing.** *Decision.* The attempt judges for itself which of the remaining work to take on for the solution of the root. The judgment is the one the current attempt guide asks for: what the statement asks, what settling it would contribute, where earlier work stopped and why, and where this session can contribute. Three things can be taken on: an element of the frontier as a whole; an exact part of what such an element asserts; or a statement the session formulates itself, when it judges that no piece of the frontier captures the difficulty and another statement would. A proof that the new statement gives an existing element is then a new way.

**The judgment that admission used to make.** *Decision.* When review assesses a new way, it writes its judgment of the division into the record of that way: whether the pieces are worth pursuing, and whether the division follows the mathematics or only restates the difficulty at a boundary where an earlier computation stopped. This is the judgment the current review guide asks for when a node is proposed. It informs the attempt that reads it and admits or blocks nothing.

Without admission, the quality of the frontier depends on how sessions state what they leave open, and the depths of the frontier hold many small pieces that can be finished. The user's standing condition that a session face the core of the problem, and not retreat into a nearby piece that can be finished, is the answer to this, together with what the frontier shows about each element: whether the root rests on it, and what review said of the division that produced it. No rule limits what may be chosen.

*Decision.* The runner does not compute whether work remains. As now, an attempt that finds nothing it can take on reports that, the runner holds further attempts on the strength of the report, and it launches again when an occupation ends or new work appears.

## 7. Knowledge about the course of the work

A session learns two kinds of thing. Some of it is mathematics about the objects and enters the canon as elements and their records. The rest is about the course of the work: which approach was taken to a statement, how far it went, where it stopped and why. The current system publishes this second kind, with the first, in the record of the session. This design does not publish a record per session.

The reason is how such records grow. A record per session is keyed by time. Sessions keep coming, but what is learned about the course of the work does not grow with their number, because sessions approach the same statement in the same way and stop in the same place. In the most recent instance one question received between four and six explorations in three days, and one claim described its own argument as a rediscovery of an earlier record's. Keyed by session, every repetition is another record to read.

*Decision.* The canon must not grow with the number of sessions, and what a session reads must not either. Knowledge about the course of the work is therefore kept in two ways, neither keyed by session.

**What has become exact becomes elements.** An approach that has been made exact consists of statements: a proof that the target follows if a certain gap is filled, the gap itself as a statement without a proof, and, if the approach is closed, the counterexample that closes it. One record of the most recent instance reported an abandoned approach by saying that a certain forcing term is positive in a certain range, so that an argument from its sign fails. What lasts in that report is the positivity of the term, and that is an element. An approach kept in this form is held by the structure, and a session that takes the same approach again finds it there and has nothing to add.

**The rest is current state attached to what the work was aimed at.** Some of what is learned does not become exact: that an estimate fell short by a logarithmic factor and no repair is known, for instance.

- An element whose proof is not accepted carries, in its record, the **approaches tried**, one entry per approach. An entry says what the idea was, which elements the approach established, where it stops, and which sessions contributed to it. It also carries review's assessment of what that work contributed to the research: what it closed, what it let the research see, how it changed the approach, or that it left what is known unchanged, and whether it repeated a kind of work already done there. Review writes this assessment for every record now; here it stands where a session choosing its work will read it.
- A **question** carries its **understanding so far**. A question, in the current design, is something the research wants to understand that has no form as a statement, such as why unrelated methods stall at the same scale; explorers take questions on, and question `q0` is the root problem as a whole. The text says what has come to be understood about what the question asks and what has not. Its mathematical assertions are elements, which it refers to by name. Review's assessment of an exploration's contribution stands here. A question is resolved, as now, when review judges that the text settles what it asks.

A session reads this state when it takes the element or the question on; the traversal meets it there. When the session ends, its peer enters what the work added. A new approach is a new entry. An existing approach carried further replaces its entry. An approach repeated to the same stopping point adds nothing. For a question, the text is replaced by one that includes what was newly understood. Each replacement follows the rule of section 4.4, and review sees the difference, including what the new text removed. Entries are separate because several sessions hold parts of one element at the same time, and a single text would be overwritten at publication. When two sessions carried the same approach further at the same time, the later publication replaces the entry the earlier one wrote, and the earlier text is kept in the history. The approaches tried on a statement are kept with the declaration that carries the statement, whichever of its proofs they concern. When the statement has an accepted proof, under any of its declarations, they go to the history of the declaration that carries the statement, where a session that later works on another proof of it can read them.

The understanding so far of `q0` has a particular place. The current rules give `q0` to an explorer whenever it is free, so it is always held. Its text is therefore where the account of the problem as a whole is kept: how the proof goes, what the parts share, where the difficulty lies. No new role and no new document is needed for this; it is the output of a role that already exists, and it is part of what every session receives at launch (section 8).

The session's own account, its report, conversation and working files, is retained outside the canon as it is now, unchanged and archived. An entry names the sessions that contributed to it, so that a reviewer designated to examine it can reach those originals. The boundary of the current design stays: an ordinary session uses published mathematics and does not read another session's originals.

This state is written prose that describes where work stands, and it is the kind of text section 11.1 of the existing design record excludes for the organizer, on the ground that a second authored account can drift from its evidence. The same risk exists here: a later session can drop a qualification when it replaces an entry, and an entry nobody replaces grows stale. Two things differ from what that section excluded. The text is written by the sessions that did the mathematics and their peers. And it enters through review, with each change before the reviewer as a difference. The user kept the decision with this stated.

## 8. Reading the canon

*Decision.* A session learns what the canon holds by **deterministic traversal** of the Lean structure, and records are designed in advance so that traversal gives sufficient information.

A traversal is determined by a starting point and a rule. Its result is everything the rule selects, in an order fixed by the structure, with the count. No step asks the session to choose search words or to guess at relevance. A session can therefore say that it has seen the whole of a given scope, and a reviewer can run the same traversal to see what the session could have seen.

The Lean structure offers at least four axes.

- **Containment.** The modules and namespaces, and everything declared in one.
- **Use.** What a declaration uses in its statement and in its proof, and, in the other direction, everything that uses it.
- **Object.** Every declaration whose statement mentions a given definition: what the canon knows about an object.
- **Standing.** From the root downward along what each proof rests on, opening every statement that is not settled: the frontier of section 6. The work that remains is the declarations in it whose own proof is not accepted.

From an element, the steps to what is attached to it are fixed as well: its record, its history, the approaches tried, the questions that refer to it, the literature it cites.

**The structural index.** At each publication the runner extracts an index from the compiled library by machine: for each declaration its name, kind and module, the text of its Lean statement, what it uses and what uses it, whether its own Lean proof is complete or ends in `sorry`, and the axioms its proof depends on through everything it uses. Whether a statement whose Lean proof ends in `sorry` has an informal proof or none is read from its record. What a statement uses and what a proof uses are recorded separately: the first says what must be defined for the statement to be made, the second what the argument rests on. The index is never edited by hand. Reading does not start a Lean process; section 12 gives the reason.

The compiled environment holds far more than the elements. The elaborator generates auxiliary declarations for a declaration the author wrote, and automation brings library lemmas into proof terms that the author never named. The extraction therefore fixes three rules. The entries of the index are the declarations of the instance's own library. An auxiliary declaration is folded into the declaration it was generated for. A declaration of an imported library, such as Mathlib, is kept as a named leaf of the uses and is not an entry.

**The joined view.** The traversal command joins the index and the record by name and returns one view of an element. The form, with invented standings:

```text
Parking.Columns.dq_col        theorem · unit of the proof · correct, held back
one line     the recursion satisfied by the difference of column k         <- record
Lean         theorem dq_col (k n : ℕ) (hk : 2 ≤ k) ... : ...               <- source, by machine
uses         zr_isWSol, IsWSol.ez, bq_eq_zero                              <- environment, by machine
used by      dq_sign (formally proved), col_crit (no proof)                <- environment, by machine
verdict      for statement hash 3fa1...: correct; held back, reason ...    <- record
explanation · proof in natural language · approaches tried                 <- record
```

A view that passes over many elements shows one line for each: its name, kind, weight and standing, and the self-description. A view of one element shows all of it. The record format has to allow this, which is why section 4.4 names its parts.

The view of a definition includes its Lean text, since the body of a definition is what the definition says. Beyond that, the source itself is opened in two situations: to read or change the body of a formal proof, and when a judgment of fidelity needs more than the printed statement, for example what an omitted implicit argument or a notation elaborates to. The second is review's work and may need a compile.

**The derived index.** *Decision.* What the current system calls the index, which is not the structural index above, becomes a derived view: the self-descriptions of the records, in the order of the Lean structure, each with its current standing beside it. The organizer writes no survey. In the most recent instance the organizer's surveys were assembled from the wording of claims and of reviews, without reading the proofs; they reported state that this design computes, and they grew with every pass.

**What a session receives at launch.** The role guides and references; the root in Lean and in natural language; the frontier at the level of the units of the proof; the understanding so far of `q0`; the board; the user's conditions. It does not receive a glossary or a survey. Definitions used by the statements of the frontier are one step away from them.

**When to traverse.** *Approved proposal.* The occasions are those the current common introduction gives for consulting earlier work: when taking something on, when a tool or a lemma is needed, before presenting something as new, and when stuck. They are occasions and not a schedule, and nothing checks that a traversal was made. What changes is the means. The guides ask a session, before it takes on a statement, to traverse the object axis for the definitions that statement uses; like the other occasions, this is asked and not checked. This traversal, and not occupancy, is what keeps a session from doing again what the canon already has.

## 9. Occupancy

The current device is kept. An attempt registers a **section**: an exact part of what a statement asserts, up to the whole of it. It does so while holding the statement's **lease**, which lets one session at a time choose there. With the registration it records, for each section other sessions hold on the same statement, why the two do not overlap; whether differently worded sections overlap is the session's judgment, and the tool refuses only what a machine can decide. A section cannot be withdrawn and stays occupied until the work is published or review decides there is nothing to publish, because until then no other session can read that work.

*Decision.* Sections and leases attach to elements instead of nodes, and nothing else about them changes. They attach to the statement: when a statement has several proofs, all of them are held under the declaration that carries the statement itself.

*Decision.* An attempt can also register a statement it has formulated that is not yet in the canon, together with the element it is aimed at; the lease is that element's. In the current system only a node can be taken on, and a new statement becomes available to others after it has been published and admitted. With no admission, a session's own statement can be registered when the session decides to pursue it. The gain is that two attempts holding different elements and aiming at the same intermediate statement see each other on the board, which the current device cannot show: a section divides a statement and not a method. What is added is information, since a session already has the exact statement in Lean when it decides.

Replacing the proof of an element requires holding the element, whole or in part. Section 10.3 says what happens when two holders of parts replace the same proof.

Occupancy does not prevent two sessions from building the same unregistered auxiliary step, and it does not decide whether two differently worded statements are the same. Explorers and questions are occupied as now.

## 10. Producing and publishing

### 10.1 The producer and the peer

*Decision.* The producing session and its peer are two researchers who take one line of work in succession, and each states its own mathematics in Lean.

The relation is that of the existing design record (its section 8). The producer does mathematics and leaves what it did; what it leaves is material, not a finished product. The peer reads all of it, works the mathematics itself, completes what was left unfinished where it can, and makes the most valuable account it can. In this design that account is the change to the canon: new elements, replaced proofs, records, and the entries of section 7. The producer's Lean statements are part of the material the peer receives; the peer reads them, corrects them, completes them and adds its own.

The peer is neither a translator of the producer's mathematics into Lean nor a checker of it. Writing a statement in Lean is not a task separate from doing the mathematics that could be given to one of the two. Independent judgment, including the judgment that a Lean statement says what was meant, belongs to review.

### 10.2 Review judges and does not gate

*Decision.* Review is not a gate. It decides, as now, whether a candidate holds material worth publishing, records its judgment of each element, and what is published carries those judgments. An element whose proof was not confirmed enters the canon in that state, with review's reason. Nothing is returned to a session for repair; a later session does the repair. This is the rule of the existing design record (its sections 9.3 and 9.5) applied to elements.

### 10.3 Publication adds, and replaces proofs in place

In the current system a candidate is frozen when the peer's session ends, review then takes its time, and the runner publishes the candidate's bytes unchanged. Each record is complete in its own folder, with its Lean sources copied into it, so one publication cannot conflict with another. A single library removes that separation: between the freezing of a candidate and its publication, other publications change the canon, and no session is left that could adapt the candidate.

*Decision.* The following rules govern publication. They rest on one invariant: the statement of an element never changes in place. A frozen candidate rests on statements, so nothing that the candidates of other sessions published while it waited takes away what it rests on. The failures that remain possible are those of section 10.4, and the organizer's removal of a separate proof declaration (section 11).

1. **New elements are added in new modules.** No existing file is edited to add a declaration.
2. **A proof that replaces another proof of the same statement is put in its place.** At publication the runner replaces the body of that declaration's proof. Name and statement stay, and the old proof does not remain in the library. A session replaces the proof of an element it holds, whole or in part. Since two sessions can hold parts of one element, a replacement also says which text of the proof it was written against. When another publication has replaced that proof in between, the runner finds this as it applies the candidate, before any build; it does not apply the candidate over the other proof, and the candidate takes the path that section 10.4 gives for one that does not build. The same holds when rule 3 replaces the proof of the old element by a one-line derivation.
3. **A statement that supersedes another enters as a new declaration.** The old element keeps its name and its statement, and its proof becomes one line deriving it from the new one. Whatever rested on the old element still compiles, and the old proof does not remain.
4. **What was replaced is kept in the history only** (section 4.4).

The replacement in rule 2 is done by the runner, on one declaration, and not by overwriting a file with the peer's copy. The runner publishes a candidate after the peer's session has ended and review has finished, and the file in the canon at that moment may differ from the one the peer saw.

Rule 2 recompiles the module that contains the declaration. Whether the modules that import it are recompiled depends on the public output of the module, which the cache key follows (section 4.3). A new proof that adds no import and makes the elaborator generate the same auxiliary declarations as the old one leaves the public output unchanged, and nothing else is recompiled; one that generates a different set changes it, and the modules downstream are recompiled (section 12).

A replacement may add imports to the module of the declaration it replaces, when the new proof needs later modules and no cycle of imports results. Rule 2 cannot always be applied. A new proof may rest on something that did not exist at the place of the old proof, for instance theory built later on top of the element itself by another route. Lean modules cannot import one another in a cycle, so such a proof cannot be put where the old one stood. It then enters as a new declaration in a later module, marked in its record as another proof of the same statement, and the old proof stays in the source until the organizer rearranges the modules (section 11), where a rearrangement without a cycle exists. Rule 3 meets the same obstacle when the superseding declaration is built on the module of the old element: the one-line derivation of the old statement then enters in the same way, as a new declaration that is another proof of it. How often either happens is not known.

### 10.4 The build check at publication

*Decision.* Before it publishes a candidate, the runner confirms that the candidate builds on the canon as it then is. The rules above leave few causes of failure, the main one being two candidates that introduced the same name. On failure the runner uses the path that exists for a candidate that changed during review: a replacement peer receives the original work, the earlier peer's work and the error, makes a new candidate, and that candidate receives a new review.

The check is a mechanism and so needs its reason. A candidate that does not build would break the canon for every session, and the peer cannot know what was published after its session ended; instructions and trust cannot cover this.

### 10.5 What still accumulates

The history gains a piece with each replacement; it is kept outside the files a traversal reads. Each superseded statement leaves a one-line consequence, which other elements use. Old proofs that could not be replaced in place remain until modules are rearranged. The last two are declarations of the library, and a traversal that selects them returns them.

## 11. The organizer

*Decision.* The organizer has three jobs.

1. **Joining what is the same.** It finds two definitions of one object, or two statements with the same content, and establishes as an element that they agree, with a Lean proof. Lean checks the proof, so the result does not go through review. Such an element has a complete Lean proof from the allowed axioms and enters as accepted: Lean's check stands for the judgment of correctness, and the two considerations of section 5 are not asked of it. An identity that it cannot prove in Lean it does not establish; that identity is mathematics and belongs to an attempt. Two statements shown to agree remain two elements. Each is settled through its own proof, and the agreement lets that proof be the one-line derivation from the other.
2. **Rearranging modules.** It moves declarations so that a proof which had to enter as a separate declaration (section 10.3) can stand under the statement's own name; the separate declaration is then removed, and the proof that stood under the statement's own name before is gone from the source. The organizer turns the published references to the removed declaration into references to the statement's own declaration; a rearrangement that left one would not compile. A candidate under review that names the removed declaration no longer builds when its turn comes, and takes the path of section 10.4. The rearrangement is valid when every other element has the name and statement it had and everything compiles, which a machine confirms. It does not go through review.
3. **Merging questions that ask the same thing.** This is by its judgment, as now.

The organizer is launched as now, after a number of publications. It finds its work with the traversal commands every session has. In the existing design the organizer's identifications are entrusted to its judgment without a separate review; that stays, and in the first two jobs Lean's check now stands where trust in that judgment stood. The organizer no longer groups records, writes surveys, or promotes and refuses terms, since sections 4.5 and 8 leave nothing of those to do. It does not retire elements that nothing uses: a true result that is unused is still knowledge, and it does not appear in the frontier.

## 12. Running Lean: what was measured

**Waiting, not compiling, is the cost.** Of 481 finished compiles in the most recent instance, the median ran for 24 seconds and waited in the queue for 179 seconds. The runs came to 11.6 hours in all and the waits to 51.2 hours.

The cause is the kind of memory that is scarce. Windows keeps an account, the commit charge, of the memory it has promised to processes; its limit is physical memory plus the page file, and an allocation beyond it fails. The development machine has four logical cores and 15.9 GB of memory, a commit limit of 25.2 GB, and, with sixteen sessions running, about 3.4 GB of that limit free. A Lean process that imports the Lean metaprogramming library was measured at a commit charge of 2,078 MB, while 803 MB of physical memory was touched and 98 MB was private to the process. Lean maps the compiled library into memory, and Windows appears to charge the whole size mapped: the files loaded came to about 1.6 GB, close to the increase in the charge. Most of those pages are shared or never touched. The broker admits compiles by commit charge, which is the right measure on Windows, and the result is that compiles run one at a time while physical memory is free. The median compile of the instance peaked at 4.2 GB, and a compile that imports the analysis part of Mathlib held between 2 and 3.9 GB for the import alone.

Two consequences shape the design. A session cannot keep a Lean process loaded, since each holds two to four gigabytes of commit charge; reading therefore goes through the structural index (section 8). And compiles that sessions batch at natural points are affordable, since what is short is concurrency and not total time.

**What was measured to help.** All on Lean 4.32.0, on a file importing the Lean metaprogramming library unless stated.

| Measure | Without | With |
|---|---|---|
| File written as a `module`: commit charge | 2,078 MB | 1,680 MB |
| File written as a `module`: physical memory touched | 803 MB | 354 MB |
| File written as a `module`: elapsed | 8.7 s | 5.7 s |
| Snapshot of the state after import, reloaded (`--incr-header-save`, `--incr-load`): elapsed | 9.7 s | 2.8 s |
| Snapshot reloaded: physical memory touched | 800 MB | 118 MB |
| A minimal module, proof changed, statement unchanged: public `.olean` | | byte-identical |
| A minimal module, statement changed: public `.olean` | | different |
| A module of several declarations, one proof replaced by another that makes the elaborator generate the same auxiliary declarations: public `.olean` of the module and of a module importing it | | byte-identical |
| The same, with lines shifted and no proof changed | | byte-identical |
| The same, one proof replaced by another that generates a different set of auxiliary declarations (an `omega` proof by a term): public `.olean` of the module, of a module importing it, and of a module importing that one | | different |
| A statement changed in a module E; D imports E and does not use the statement; M imports D and uses it: every output file of D | | byte-identical, while M no longer compiled |

The installed Mathlib is itself compiled as modules, with 1,735 MiB of public output and 3,378 MiB of private output, which is where proofs are.

The row on the `omega` proof limits what the public-output key saves. Automation such as `omega` adds auxiliary declarations of its own to the module, and a replacement proof that adds a different set of them changes the public output, although no statement changed; the change then reached every module downstream that was tried. A replacement that leaves the auxiliary declarations as they were recompiles its own module and nothing else. The key is correct in both cases, since it follows the output and not an assumption about it; how often the favourable case occurs in real proofs is not known.

The row about E, D and M is why the key takes every module of the library that a compile reaches and not only those it imports directly: a key made from D's output alone would have returned M's earlier files as a success. A plain file, one without the `module` header, reads the private data of the modules it reaches, and so does a `module` file through `import all`; for these the key takes the whole output of each module reached.

The two means act on different quantities. Writing a file as a module lowers the commit charge, which is what limits how many compiles run together. Reloading a snapshot shortens the run and lowers the memory touched, and leaves the commit charge almost where it was (2,079 MB without, 1,996 MB with), so by itself it does not let more compiles run together. Making the snapshot took 19 seconds once, and the file is 73 MB.

**What is adopted.**

- The library is written as modules, and the cache key uses public output (*decision*, section 4.3).
- The broker reuses a snapshot of the state after import, and falls back to the present way when the snapshot cannot be used (*approved proposal*). The option is marked experimental by Lean, and its behaviour may change between versions. Three things found while implementing it fix its form. Lean stores the name of the module being compiled in the snapshot and matches the header line by line, so a snapshot serves compiles with the same header text and the same module name, and it is used for compiles whose imports are all from the imported library. Saving a snapshot costs more than one compile saves, so it is saved at the second compile with a given header and not at the first. And a compile that used a snapshot and did not succeed is run once more without it before its result is reported; a snapshot whose result differed is deleted, and that header gets none again.
- Raising the commit limit by enlarging the page file would let the broker admit several compiles at once. It is a setting of the user's machine and is recommended to the user, not done by the implementation.

Extracting the structural index adds one compile to each build that changes the library: a plain file that imports the changed modules and the Lean metaprogramming library. In a run of a scripted research against the real compiler, on the machine while it was loaded, the five such compiles took a median of 57 seconds and 2.1 GB of commit charge each; the module compiles of the same run took a median of 1.9 seconds.

The toolchain also has means that were not measured and may be used: a command that removes unused imports, structured output of messages, limits on memory and on allocations for a compile, and per-declaration timing.

A single resident Lean process serving every session's small checks was considered and is not adopted. If the snapshot works at scale it gives the same gain without a process to build and keep alive.

The effect of the means adopted above was not measured on files that import Mathlib. Such a compile holds more than 3 GB of commit charge, and the experiment would have taken memory from the running instance.

## 13. The dependency map and the paper

### 13.1 The dependency map

*Approved proposal.* The map is drawn by script from the structural index and the records, at any time. The units of the map are the elements whose weight marks them as results a reader of the proof's structure would name; steps inside one proof are folded into the edges that pass through them. An edge between two statements comes from what a proof of one uses, for each of its proofs; a definition that is a unit is joined to the statements that mention it. Units are grouped by the folder of their module, and the peer chooses the folder when it adds a module. The author writes the weight, the short name and, for another proof of an existing statement, which statement; review judges them. The criteria for a unit are those worked out for the existing map of the previous research, in `임시/주차함수_증명/dependency_map/지도의_단위.md`, generalized from a manuscript to the canon, and the drawing follows the generator made for that map, under `임시/주차함수_증명/dependency_map/scripts`; what the script needs of it is brought into the skill, which does not depend on that folder.

### 13.2 The paper

*Decisions.* One command produces the paper to the end, without stopping for the user. The method it follows is fixed in advance and shipped with the script; the sessions the script launches do not decide the reader, the structure or the manner of writing. The starting point is the Lean proof that settles the root. From the natural-language information corresponding to what that proof rests on, and whatever else a paper needs, the script produces a mathematical paper in English that follows the standard form, structure, expression and writing of such papers. The manuscript is LaTeX and the PDF is typeset by TeX.

The paper is generated once the root is settled by a formal proof that review has compiled and audited, and its body is what that proof rests on. Results the proof does not use, abandoned approaches and open questions are not in the body.

*Decision.* The implementation details of the canon do not appear in the paper. The paper states the mathematics cleanly, accurately and concisely. In particular it does not list theorems of the form "A is proved by B".

| In the canon | In the paper |
|---|---|
| The one-line consequence left by a superseded statement | Not stated. Where the old statement was used, the new one is called; the step from the new statement to the old is written into the proof that uses it when a reader needs it. |
| Several proofs of one statement | The one the proof of the root rests on. |
| An element stating that two definitions agree | One definition is used; statements about the other are restated with it. |
| Elements whose weight marks them as steps inside a proof | Not numbered; absorbed into the proof that uses them. |
| Conventions of the Lean form, such as indices from zero or normalized quantities | The conventions of the root's natural-language statement. |
| Holds and their reasons, approaches tried, history | Not stated. |
| The arrangement of modules and the order of declarations | Not followed. The order is that in which a reader reads. |
| Results taken from the literature | Cited, not proved again. |

The introduction draws on the understanding so far of `q0` and on the explanations in the records of the elements nearest the root.

This places a requirement on the canon that has to be met when an element is reviewed, not when the paper is made. *Approved proposal.* The natural-language proof in a record is the same argument as the element's Lean proof. A formalizer may fill gaps and change the strategy of an argument; when it does, the peer that takes its work over rewrites the natural-language proof accordingly, and review judges whether the two are one argument. A coherent exposition read from beginning to end does not exist inside the canon; inside it, the proofs of the elements near the root say how the pieces below them combine, and `q0` carries the whole. The paper is where the linear exposition is made.

The method document shipped with the script is written as part of the implementation, from the conventions of mathematical papers, the user's writing preferences, and the table above, and is confirmed once by the user. It has to settle at least these: who the paper is for and what each of its parts does; which elements become numbered theorems, which lemmas, and which are absorbed, with the weight in the records as the material for that choice; an order that respects dependence and still puts the main result first; how the statements of the paper are kept the same as those of the canon and how that is checked; how results from the literature are cited, without saying more than was read; and what is checked after writing. No TeX distribution is installed on the development machine; installing one is confirmed with the user when that part is implemented. Since a session's LaTeX may fail to compile, the script returns compile errors to the session that wrote the part.

## 14. What stays as it is

*Approved proposal.* The following are unchanged.

- The six roles and the order in which the runner launches them.
- The proposal of questions by peers, their admission by review, and the operator's publication of questions.
- Concerns, findings and comprehensive review.
- The two acceptance settings.
- Occupancy lasting until publication.
- The reconsideration of a session's ending.
- The retention of a session's originals, and the boundary on who may read them.
- English as the language inside an instance.
- The governing principles of the existing design record.

## 15. Implementation: constraints and completion

*Decision.* Only the installed skill under `.claude/skills/do-math` is changed, in place. The generated copy under `.agents/skills/do-math` is not regenerated. An instance runs the installation it was launched from, and the commands its sessions call read that installation's code afresh at each call, so regenerating the copy would change the code under a running research instance at that moment. The commit procedure of the repository includes a step that brings generated copies into agreement with their sources; for the commits of this work that step is not applied to do-math.

The running instance is not touched. While it runs, no experiment is made that holds gigabytes of commit charge.

The deliverables are this record; the implementation, that is, the guides, the runtime, its tests, and the scripts for the map and the paper; and a record of verification.

*Decision.* The work is complete when the tests pass; when a new instance on one small proposition goes from a root stated in Lean, through sessions that build elements and a formal proof of the root, to the paper as a PDF and the dependency map produced by script; and when the guides have been read independently. An independent reading is the one this record itself went through: a reader that has the guide and nothing of the design conversation reports what it understood and where it had to guess, and the report is compared with what the guide was written to convey.

A completed small case shows that the path is connected. It does not show that research improves, and it is not to be reported as showing that. The first real run is where the following are to be observed, one for each thing the redesign set out to change: the time compiles wait; the size of a session's starting context; how often review notes that a result was obtained again; the size of the canon against the number of sessions; and whether the map and the paper are produced without rounds of repair by hand.

## 16. Open and unmeasured

| Matter | Standing |
|---|---|
| The effect of modules, of the snapshot, and of the public-output cache key on files that import Mathlib | Not measured. To be measured when the running instance is stopped or the commit limit is raised. |
| The snapshot option | Marked experimental by Lean. |
| How often a proof cannot be replaced in place | Not known before a run. |
| How often a replaced proof leaves the public output of its module unchanged | Not known. It was unchanged in two of three small cases measured (section 12). |
| The cost and the fidelity risk of defining a research's objects in Lean | Not measured. The most recent instance introduced 773 terms in three days. |
| Why the system before the rebuild required proofs to be formalized in the session that found them, and why the rebuild removed that | Not found in the records read. This design asks for statements and definitions, not proofs, from every session. |
| The method document for the paper | To be written; confirmed once by the user. |
| Installing a TeX distribution | To be confirmed with the user at implementation. |
| Enlarging the page file | The user's choice. |

## Appendix. Where each decision is recorded

| Decision | Section | Kind |
|---|---|---|
| Only what has a Lean statement is an element; state and keep; Lean from the start | 4.1 | decision |
| The root fixed in Lean at creation | 4.2 | decision |
| Source and record divided; bound by name and statement hash | 4.3 | decision |
| Library written as modules; cache key from public output | 4.3, 10.3, 12 | decision |
| One replaceable record per element, with self-description and weight | 4.4 | decision |
| No glossary; definitions are elements | 4.5 | decision |
| Two judgments; four states; hold on the element; settled per statement | 5 | decision |
| Formal proof required as now | 5 | approved proposal |
| No nodes; derived frontier; the attempt chooses; review's remark on a division | 6 | decision |
| The runner consumes the attempt's report | 6 | decision |
| No record per session; approaches tried; understanding so far; `q0` | 7 | decision |
| Deterministic traversal; structural index; joined view; derived index | 8 | decision |
| Occasions for traversal | 8 | approved proposal |
| Sections and leases on elements; own statements registrable | 9 | decision |
| Producer and peer | 10.1 | decision |
| Review does not gate | 10.2 | decision |
| Additive publication; proofs replaced in place; superseding statements | 10.3 | decision |
| Build check and fallback | 10.4 | decision |
| The organizer's three jobs | 11 | decision |
| Snapshot reuse in the broker | 12 | approved proposal |
| Enlarging the page file | 12 | recommendation to the user, approved as such |
| Dependency map | 13.1 | approved proposal |
| Paper: one command, fixed method, English, LaTeX, no canon artifacts | 13.2 | decision |
| Natural-language proof agrees with the Lean proof | 13.2 | approved proposal |
| What stays | 14 | approved proposal |
| Only the installed skill is changed; the generated copy is not regenerated; completion | 15 | decision |
