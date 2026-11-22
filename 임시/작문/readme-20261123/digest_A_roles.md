# Digest A: the six session roles and the life of a session

## How to read this digest

This digest describes one area of the current implementation of do-math, the skill folder `C:\math\.claude\skills\do-math`: the six session roles and what happens to a session from its launch to its end. It was written so that the README and the running guide can be rewritten from it and each new sentence checked against a source. It is a reading of the sources as they stood on 2026-11-23, and it is not itself a source; where a sentence of the new README matters, check it at the location cited here.

**Citations.** Every path without a drive letter is relative to `C:\math\.claude\skills\do-math\`. A citation has the form `path:line` or `path:first-last`. Line numbers are those of the files as read on 2026-11-23.

**Marks.**

- A sentence with no mark restates what the cited guide says.
- `[code]` means the fact was read from a Python file. Where a guide says the same, both are cited.
- `[inferred]` means I derived the fact from the cited places and the sources do not state it in those words.
- Text inside quotation marks is copied exactly from the source.

**Vocabulary of the current system**, since the README uses the vocabulary of the previous one. The sources define each of these terms; the definitions are quoted in Part 1 where the term first matters.

| Current term | Meaning in one line | Defined at |
|---|---|---|
| canon | the instance's Lean library, a written record for each declaration, and written state attached to statements and questions | `reference/common.md:7`, `:101` |
| element | a declaration of the library together with its record; a definition or a statement (`theorem`) | `reference/common.md:103` |
| standing | one of four states of a statement: no proof; proof not confirmed; correct, held back; accepted | `reference/common.md:149-156` |
| settled / formal | settled is computed from review's judgments, formal from Lean | `reference/common.md:166`, `:170` |
| candidate change (candidate) | the change to the canon that a peer proposes | `reference/common.md:119`, `reference/change-format.md:3` |
| frontier | the computed view of what the root rests on and how much of it is settled | `reference/common.md:188` |
| work that remains | every statement of the frontier whose standing is not "accepted" | `reference/common.md:164`, `:203` |

The words "node", "relation", "claim status", "record candidate", "module of records", "shared context" and "glossary", which the README uses, do not occur as concepts in the files I read. Part 2 says what stands in their place.

---

# Part 1. The current facts

## 1. The six roles

### What every session receives

The role names are fixed in code as `attempt`, `explore`, `formalizer`, `peer`, `review`, `organizer`, and the first three are the producers. `[code]` `runtime/settings.py:10-11`

Every session is a fresh Claude Code or Codex conversation that begins without the earlier sessions' conversations. `reference/common.md:3`, `:5`

The runner writes three things into the new session's folder before the CLI starts. `[code]` `runtime/context.py:91-140`

- `pack.md`, the starting context. Its order is: the root statement in words; the root in Lean; the assignment (`task`); the guides; the frontier with the questions as at launch; the understanding so far of question `q0`; the board as at launch; the user conditions; the executable commands. `[code]` `runtime/context.py:105-136`; the guide states the same order at `reference/common.md:295`.
- `input.json`, which holds the session identity, role, pipeline, `task`, the revision of the canon, the user conditions, the settings and the argument arrays of the commands. `[code]` `runtime/context.py:91-95`
- `prompt.txt`, three lines that tell the session to read `pack.md` in full and carry out the role. `[code]` `runtime/context.py:137-140`

The guides embedded in every pack are `reference/common.md` (called "the common introduction" throughout the role guides), the role's own guide, `reference/writing.md`, `reference/canon.md`, `reference/lean.md` and `reference/tools.md`. `[code]` `runtime/context.py:88-90`

Each role receives further references. `[code]` `runtime/context.py:14-25`

| Role | Further references embedded in the pack |
|---|---|
| attempt | `what-research-is-for.md`, `user-writing-preferences.md`, `literature.md`, `sections.md`, `retained-work.md` |
| explore | `what-research-is-for.md`, `user-writing-preferences.md`, `literature.md`, `retained-work.md` |
| formalizer | `retained-work.md` |
| peer | `what-research-is-for.md`, `user-writing-preferences.md`, `literature.md`, `sections.md`, `retained-work.md`, `records.md`, `change-format.md` |
| review | `what-research-is-for.md`, `user-writing-preferences.md`, `literature.md`, `records.md`, `change-format.md`, `review-output.md` |
| organizer | `what-research-is-for.md`, `user-writing-preferences.md`, `records.md`, `change-format.md`, `organizer-output.md` |

The reason for this distribution is given in a code comment: every role states mathematics in Lean and reads the canon, so each receives the canon and Lean guides, and "A guide that only some roles act on goes to those roles: sections.md to the roles that register sections, records.md to the roles that write or judge the written texts of the canon." `[code]` `runtime/context.py:15-17`

A copy of every file of `reference/`, the role guide and `SKILL.md` is saved under the session's `context/` folder at launch. The comment gives the reason: "editing installed guidance does not change a running session's instructions when it follows a reference later." `[code]` `runtime/context.py:60-66`

The starting context "holds no list of definitions"; a session reaches the rest of the canon by traversal. `reference/common.md:243`

Workers "inherit no personal or project instructions, hooks or memories. Their do-math context is supplied directly." `reference/common.md:303`

Everything written inside an instance is written in English. `reference/common.md:297`

### Attempt

**Definition.** "An **attempt** is the role responsible for choosing, among the work that remains for the root, what to take on, and for trying to settle it." `reference/common.md:19`

**Receives.** The common starting context above, with an empty `task`. `[code]` `runtime/runner.py:247-254` creates the producer job with `task or {}`, and the pack says of the assignment "Where it names no work, your role chooses its own." `[code]` `runtime/context.py:114-115`. The guide says "No earlier session assigns its work or writes its mathematical task." `reference/common.md:19`

**Does.** It chooses what to take on (topic 2 below), registers it as a section, and works on it: it "develops proofs, searches for counterexamples, computes or consults literature according to what the statement and the evidence require." `reference/common.md:19`. It states what it finds in Lean as it finds it: "When you have carried an approach as far as you can, state the exact gap that remains as a statement without a proof, and state the result that your target follows once the gap is filled." `roles/attempt.md:55`. A complete Lean proof is optional for this role. `roles/attempt.md:61`. A proof may be written in words, in which case its Lean proof lists the elements the argument uses and ends in `sorry`. `roles/attempt.md:59`

**When it may finish.** "You can finish when the sections you registered are proved or refuted as stated." An unresolved attempt "should end only when, after making its best effort, it sees no meaningful work it can still pursue." `roles/attempt.md:89`. "Session run time has no fixed cap." `roles/attempt.md:91`

**Leaves.** Retained work for a peer (topic 5). The role guide describes it as "material for the peer, a second researcher who takes this line of work over, continues the mathematics and makes the change to the canon." `roles/attempt.md:83`. An attempt changes nothing in the canon itself: "None of these roles changes the canon directly; the peer writes the candidate and review judges it." `reference/retained-work.md:55`

### Explorer

**Definition.** "An **explore** session, or explorer, develops understanding and insight. It works with the objects, examines examples and representations, investigates recurring obstacles and follows connections that may reveal another way of seeing the problem. It has no predetermined theorem to produce." `reference/common.md:180`

**Receives.** The common starting context. Its `task` either names question `q0`, when `q0` was free at launch and the runner assigned it, or names no question. `roles/explore.md:11`, `:13`; `[code]` `runtime/runner.py:285-303`

**Does.** It holds one question and explores the problem through it. "Holding `q0`, you explore the problem without a narrower focus, deciding which angles to pursue and how far to develop them. Holding another question, that question is the focus of your exploration". `roles/explore.md:5`. The question is "the focus of its work, not a boundary on it": the explorer may read across statements and other sessions' sections and may develop a proof inside another session's section when that serves the understanding it pursues. `reference/common.md:273`. A proof it completes of a statement another session holds enters the canon as a separate declaration marked as another proof of that statement, because "Only a pipeline that holds a section on a statement replaces its proof in place". `roles/explore.md:66`. Like the attempt, it states its assertions in Lean: a new object is a definition, a result a statement with its proof, a conjecture a statement without a proof, an observation the exact statement of what was observed over the observed range; an explanation is prose. `roles/explore.md:72`

**Leaves.** Retained work for a peer. "What you leave is what became understood about the question, why it became clearer, and what remains worth pursuing." `roles/explore.md:7`. The peer writes the understanding so far of the question from the explorer's account. `roles/explore.md:80`. It may also leave in its report a question the research should hold onto, for the peer to propose, and a statement that its own question is answered, for the peer to propose as a resolution. `roles/explore.md:86`, `:88`

**When it may finish.** "Session run time has no cap." `roles/explore.md:92`. "Consider finishing when you can explain the understanding gained and further serious mathematical work is no longer adding to it." `roles/explore.md:94`

### Formalizer

**Definition.** "A **formalizer** is the role that supplies those proofs." (The preceding sentence is about complete Lean proofs of every statement the root rests on.) `reference/common.md:170-172`

**Receives.** One element: "you receive one element of the canon, a settled statement whose proof is not yet formal". `roles/formalizer.md:3`. `task.element` names the declaration to prove and `task.previous_changes` lists the changes earlier formalizers of that element published. `roles/formalizer.md:17`, `:21`; `[code]` `runtime/runner.py:1166-1168`. The formalizer does not receive the two research documents or the literature guide. `[code]` `runtime/context.py:21`. The runner records a section on the whole element for the formalizer's pipeline, "which is what lets your peer put your proof in its place, so you use none of the commands that register sections." `roles/formalizer.md:17`; `[code]` `runtime/runner.py:320-328`

**Does.** It writes the Lean proof that replaces the `sorry`, or makes formal a proof whose Lean text is complete and still not formal. `roles/formalizer.md:3`. It may fill gaps, add helper lemmas and definitions, or change the strategy; the statement stays exactly as it is, and "A weaker statement or an added hypothesis would leave the assigned statement without its formal proof." `roles/formalizer.md:5`; `reference/common.md:172`. Before describing the proof as complete it obtains `#print axioms` and compares the result with `settings.lean.allowed_axioms`. `roles/formalizer.md:35`

**Leaves.** For a completed proof: the final text of the assigned declaration under `output/replace/`, every new module under `output/lean/`, a list of the imports the element's module gains, the actual compile and axiom output, and an account connecting the Lean proof to the written one. For unfinished work: the partial Lean sources and each remaining obligation stated exactly. `roles/formalizer.md:57`. When it changed the argument it leaves the peer what is needed to rewrite the proof in the record, because "that proof and the Lean proof are to be one argument"; the reason given is that the paper presenting the result is produced from the natural-language proofs, and "A record whose written proof argues one way while the Lean proof argues another would put into the paper an argument that Lean did not check." `roles/formalizer.md:39-41`

**Continuation.** "If the written proof remains sound and the Lean proof remains incomplete, another formalizer continues from what was published. There is no automatic round cap for lack of progress." `roles/formalizer.md:59`

### Peer

**Definition.** "When an attempt ends, a **peer** takes its work over. The producing session and its peer are two researchers who take one line of work in succession, and each states its own mathematics in Lean." `reference/common.md:117`

Topic 7 gives what it receives, does and writes.

### Review

**Definition.** "A separate **review** session judges the candidate." `reference/common.md:121`. The role guide opens: "As a reviewer, you determine what the offered evidence establishes." `roles/review.md:3`

Topic 8 gives the details. In brief: it receives the frozen candidate, the producing session's directory and the peer's retained work (`roles/review.md:51`; `[code]` `runtime/runner.py:528-531`), and it leaves a feedback document and `output/assessment.json` (`reference/review-output.md:3`). A review can also be a comprehensive review of what the canon already holds. `roles/review.md:7`

### Organizer

**Definition.** "As publications accumulate, an **organizer** keeps the canon usable as one body; the runner launches one after a number of publications." `reference/common.md:184`

Topic 9 gives the details. In brief: it receives a batch of published changes (`roles/organizer.md:5`) and leaves `output/organization.json` and, optionally, a change to the Lean library (`reference/organizer-output.md:3`).

### The pipeline

"The attempt, the peer that takes its work over and the review that judges the candidate together form one **pipeline**." `reference/common.md:125`. The three producing roles share this path: "the three producing roles, attempt, explore and formalizer, share the path from a session's work to a peer's candidate to reviewed publication." `reference/common.md:182`

`[code]` A pipeline has the stages `producing`, `peer`, `review` and `done`. `runtime/runner.py:249`, `:482`, `:527`, `:539`, `:1008`, `:1202`. An organizer and a comprehensive review are jobs without a pipeline. `[inferred]` from `runtime/runner.py:1157`, `:1172`, where they are enqueued without a pipeline argument.

## 2. How an attempt chooses its work

### What it reads

- The frontier, as the starting point. `roles/attempt.md:11`
- The view of an element before choosing it, with the approaches tried read in full and review's assessment of what that work contributed. `roles/attempt.md:17`
- For a statement whose proof is correct and held back, the published proof itself, before acting on review's reason. `roles/attempt.md:19`
- What the canon knows about the objects the statement speaks of, by traversal. `roles/attempt.md:21`. The common introduction asks for this reading "each time": "before you take on a statement, you should traverse, for each definition the statement uses, everything the canon states about that definition", and it adds "Nothing checks that you made it." `reference/common.md:243`
- The understanding so far of `q0`, and of any other question that bears on the choice. `roles/attempt.md:23`
- The statement as Lean states it, with the definitions it uses. `roles/attempt.md:25`
- The live board, for the sections other sessions hold on the element. `roles/attempt.md:27`

### What it may choose

"Three things can be taken on: a statement of the frontier as a whole; an exact part of what such a statement asserts; or a statement the attempt formulates itself, when it judges that no piece of the frontier captures the difficulty and another statement would." `reference/common.md:211`. The role guide repeats the three at `roles/attempt.md:13`.

"No rule limits what may be chosen, and no session or reviewer admits a statement to the frontier." `reference/common.md:211`. The tools do not confine an attempt to the frontier: "a section can be registered on any statement of the canon that is not settled, contested or refuted, including one whose own proof is accepted but which is not settled because of what that proof rests on". `reference/common.md:211`

The judgment the attempt is asked to make before choosing: "what the statement asks, what proving or refuting it would contribute to settling the root, where earlier work on it stopped and why, and where you can contribute." `roles/attempt.md:13`. The guide warns against choosing a small element because it can be finished: "A small element is the right thing to take when the difficulty of the problem lies in it, or when the proof above it cannot go on without it and earlier work has not been able to supply it. Taking it because it is the piece you can see how to close is the retreat that the condition describes." `roles/attempt.md:15`. The condition referred to is the user's standing condition "Working directly on the central difficulty". `reference/common.md:45-57`

A statement whose proof is correct and held back "is ordinary work that remains, and you take it on in the same way as the rest." `roles/attempt.md:19`

### What a section is

Three sources define it.

- "An attempt **occupies** a **section** of a statement of the canon: an exact part of what the statement asserts, which the attempt is working to settle." A section can restrict the cases covered or select part of the required conclusion, and "The whole statement is also a possible section." `reference/common.md:251`
- "What you register is a **section**: the whole of an element, an exact part of what it asserts, or a statement of your own aimed at it." `roles/attempt.md:27`
- `[code]` "A section is an exact part of what an element of the canon asserts, up to the whole of it, or a statement not yet in the canon together with the element it is aimed at; an attempt or peer works on it." `runtime/coordination.py:3-5`

The first of these does not mention the third kind, the statement of the session's own; the common introduction adds it a few paragraphs later: "A statement that a session formulated itself and that is not yet in the canon is registered on the element it is aimed at, the one it is meant to settle, and such a registration is a section on that element like any other." `reference/common.md:259`

A section is stated "as precisely as the statement itself, and the statement implies it." The reason: "Settling a section therefore asks for no more than the statement does, and settling sections that together cover all its requirements settles the statement. Several attempts can thus work on one statement at the same time without repeating each other." `reference/sections.md:7`

"A section divides the statement and not the method: two attempts applying different techniques to the same part would still be proving the same results." `reference/sections.md:7`

A statement that is not implied by the element's statement "is not a part of that element, even when proving it would suffice", and is registered as a statement of the session's own. The reason for registering it at all: "Registering it makes it visible. Two attempts that hold different elements and aim at the same intermediate statement can then see each other on the board, which a division into sections cannot show." `reference/sections.md:9`

Breadth: "Take a narrow section when your mathematics is narrow, and a broad one when it is broad." `reference/sections.md:13`. "Do not narrow a section merely to leave room for others or to finish sooner." `roles/attempt.md:27`

The roles that register sections are attempts and peers. `reference/sections.md:3`; `[code]` `runtime/coordination.py:23`, `:220-225`

### The lease that exists while a session is choosing

A lease exists, on the element. "Choosing is serialized by the **lease** of the element. A lease lets one session at a time choose a section there; others who want the element wait in order or choose another, as they judge best. Sections and leases attach to the statement. When a statement has several proofs, all of them are held under the declaration that carries the statement itself." `reference/common.md:259`

The order in which the role guide asks an attempt to act: read the live board for the sections others hold on the element and form the intended section; "Then take the element's lease with the commands in `input.json`, check your section again against the sections the lease reports, and register it, giving for each section another session holds there your reason that the two do not overlap." `roles/attempt.md:27`. So the reading and the forming of the section come before the lease, and the lease covers the final check and the registration. `[inferred]` from that sentence.

What holding the lease guarantees: "While you hold the lease of an element, no other section can appear on the element, so the sections you read are the sections you have to respect. Registering your section ends your lease and lets the next waiting session choose, and a further section is chosen through the lease again." `reference/sections.md:23`

Duration: "A lease has no time limit: until you register, release or end your session, everyone waiting for the element waits for you." `reference/sections.md:36`. `[code]` A lease or a queue place held by a session that is no longer live is dropped, and a free lease passes to the longest waiter. `runtime/coordination.py:157-173`; liveness is defined at `runtime/coordination.py:61-66`.

One relation at a time: "A session stands in one lease relation at a time: taking or waiting for another element gives up its place here." `reference/sections.md:34`; `[code]` `runtime/coordination.py:235-240`

`[code]` Leases and registrations are decided "first-wins under one instance lock". `runtime/coordination.py:8-9`. The lock is a file lock that a command waits for up to 30 seconds. `runtime/coordination.py:21`, `:31-52`

### The four commands and exactly what they refuse

The guide lists the commands at `reference/sections.md:33-36`. The table gives the guide's statement and what the code does.

| Command | Refuses | Guide | Code |
|---|---|---|---|
| `commands.lease` | when another session holds the lease; for a definition; for a statement that is settled, contested or refuted; while another pipeline holds the whole element. A refusal exits with code 1 and records nothing. | `reference/sections.md:33` | `runtime/coordination.py:254-273`, with the reasons at `:202-217` |
| `commands.wait` | joins the queue; returns 0 once the lease is the session's, 124 at the timeout with the place kept; refuses with 1, giving up the place, in the cases in which the lease is refused, except the case that another session merely holds the lease, in which it waits | `reference/sections.md:34` | `runtime/coordination.py:276-307`; default timeout 50 seconds at `:615` |
| `commands.section` | see the list below | `reference/sections.md:35` | `runtime/coordination.py:324-385` |
| `commands.release` | nothing; gives up the lease or the queue place | `reference/sections.md:36` | `runtime/coordination.py:310-321` |

`[code]` The registration command refuses, in this order (`runtime/coordination.py:358-374`):

1. a registration by a session that does not hold the element's lease (`:358-359`);
2. a registration on a definition, or on a statement that is settled, contested or refuted, or of which another pipeline holds the whole (`:360-362`, reasons at `:202-217`);
3. a whole-element registration while sections of other pipelines exist on the element (`:365-366`);
4. a whole-element registration when the session's own pipeline already holds the whole element (`:367-368`);
5. a part or a new statement whose text, with runs of whitespace collapsed, equals the text of a section already registered on the element, by any pipeline including the session's own (`:369-371`; for a statement of the session's own the text compared is its Lean statement, `:346`);
6. a registration that gives no nonempty reason for some section another pipeline holds on the element (`:372-374`).

A request of the wrong shape (for instance `new` together with `whole`, or neither a statement nor `whole`) is an error and not a refusal: the command prints an error and exits with code 1. `[code]` `runtime/coordination.py:338-349`, `:652-654`

The guide states the principle and a shorter list: "The registration tool refuses what it can decide by itself, namely an identical statement, any conflict with a section that covers the whole element, and missing reasons." `reference/sections.md:25`. At `reference/sections.md:35` it gives the longer list: "The tool refuses an identical statement, a whole-element registration while other sessions hold sections, and missing reasons. A refusal records nothing and keeps your lease, so you can correct the request. It also refuses a statement that has become settled, contested or refuted, or that another session now holds whole, when that changed while you held the lease".

What the tool does not decide: "Whether two differently stated sections overlap is a mathematical judgment, and it is yours. A registration therefore records, for every section other sessions hold on that element, your reason that the two sections are disjoint." The guide's criterion for overlap: "Two sections overlap when both ask for the same requirement in the same case." `reference/sections.md:25`

The commands count sections by pipeline. A peer's own pipeline includes the producing session and any earlier peer it replaces; "Your own pipeline's sections need no reasons, and they do not prevent you from registering the whole element unless your pipeline already holds it whole." `reference/sections.md:31`

The three forms of a section request are `{"whole": true}`, `{"statement": ..., "reasons": {...}}` and `{"new": {"lean": ..., "statement": ...}, "reasons": {...}}`. `reference/sections.md:38-55`

`[code]` A registered section is written into the registering session's `declaration.json` with an ID `<session>-<n>`, the element, `whole`, the statement, `new`, the reasons and a time. `runtime/coordination.py:375-381`; the guide says the same at `reference/retained-work.md:55`.

### How long a section counts as occupied

"A registered section cannot be withdrawn, so register it once you have decided to pursue it." `reference/sections.md:57`

"Occupancy continues after the attempt's conversation ends. Its work is then with the peer or the reviewer and is still unavailable to ordinary successors. Releasing the section at that moment would let another attempt repeat mathematical work it has no way to read. A section cannot be withdrawn; it remains occupied until publication makes the work available, or review completes a decision that there is nothing to publish. After that, a part of the statement that still remains can be chosen again with the new knowledge available." `reference/common.md:261`

`[code]` The board lists every pipeline whose stage is not `done`, and a pipeline's sections are those declared by its producer, its earlier peers and its current peer. `runtime/coordination.py:102-106`. The stage becomes `done` when the publication is committed (`runtime/runner.py:1005-1008`), when a completed review excludes the candidate (`runtime/runner.py:536-542`), or when the session ends with a no-research outcome (`runtime/runner.py:1200-1202`). A reviewed exclusion "ends the occupancy its pipeline held: the sections recorded for its producer and peers, including a formalizer's whole element, or the exploration's question." `reference/review-output.md:112`

When to register: "An attempt registers its section once it has decided what to pursue, and then does its research inside that section, because work that is not registered is invisible to other sessions, which may repeat it without knowing." The guide names the cost of registering early as well: "A boundary chosen before the shape of the difficulty is understood tends to follow what looks manageable rather than what the mathematics suggests, and it then fixes what counts as settled." `reference/sections.md:15`

A session can register a further section later; its earlier sections remain its own. `reference/sections.md:19`; `roles/attempt.md:35`

### What a section permits and what it does not enforce

Permission: "Holding a section also carries a permission: a candidate can replace the proof of a statement only when its pipeline holds a section on that statement, the whole of it or a part." `reference/common.md:263`. The transport check enforces this for a peer's candidate. `reference/sections.md:57`; `reference/change-format.md:144`

Boundary between holders: "If another session holds a section of an element, you may use established results and prove statements that assume its part, but leave proving or refuting that part to its holder. If your argument would establish that part itself, stop short of it: state the step in Lean as a statement that takes that part as its hypothesis, and tell the holder with a coordination message." `roles/attempt.md:31`

Not enforced: "The board and the coordination tools give sessions the information and means to cooperate. They do not infer the purpose of a mathematical argument or restrict which files and lemmas a session uses. Respecting other sessions' sections in the mathematics you pursue, within the scope your role has, is therefore your responsibility rather than the tools'". `reference/common.md:265`. Occupancy "does not prevent two sessions from building the same auxiliary step that neither registered, and it does not decide whether two differently worded statements are the same." `reference/common.md:265`

`[code]` Sessions can send each other coordination messages: `commands.message` writes a JSON file into the recipient session's `inbox/`, and `commands.updates` returns the received messages. `runtime/coordination.py:586-600`, `:570`, `:582`. The guide limits their use: "The board and coordination messages communicate work status and decisions about cooperation; they do not provide an alternate channel for treating unfinished mathematics as shared evidence." `reference/common.md:291`

### The board

"The **board** lists producing sessions and the processing of their work. Each entry identifies the producing session and its role, the elements on which it holds sections or the question it holds, and whether the session is running or its work is with a peer or under review; beneath it stand its sections, each with what it covers. An attempt can appear before it has chosen a section; an exploration appears with the question it occupies, or as choosing one." `reference/common.md:257`

The reason the board exists: "The canon tells you what earlier sessions made available. It cannot yet tell you what another attempt is discovering now. If two attempts independently take on the same statement, each may repeat work that the other has already done but that is not yet published." `reference/common.md:249`

The board in the pack is the one saved at launch; the live board comes from `commands.updates`. `roles/explore.md:11`; `[code]` `runtime/coordination.py:559-583`

## 3. Explorers and questions

### What a question is

"Why several unrelated methods stall at the same scale, what an object looks like in the regime where every estimate loses its margin, whether two descriptions that behave alike are the same thing: these are questions about the problem, and an answer to one is an explanation or an understanding rather than a theorem. No statement can hold them. The research therefore keeps a second kind of object, the **question**, and the frontier view lists the questions after the frontier itself." `reference/common.md:219`

"A question has an identifier, a statement of what is to be understood, and the grounds on which it was asked. It has no sections, and it is not located at any one element: a question can range across several statements, regimes and methods, and it can rest on a conjectural possibility or a suspected connection as well as on established facts." `reference/common.md:221`

`[code]` "A question is an object of understanding that one explorer at a time occupies whole." `runtime/coordination.py:5`

Each question carries its **understanding so far**: "a text that says what has come to be understood about what the question asks, and what has not. Its mathematical assertions are elements, to which the text refers by name; the text itself explains, connects and interprets." `reference/common.md:223`

### What `q0` is

"**Question 0**, written `q0`, is always present: it is the root problem itself, taken as a whole." `reference/common.md:221`; `[code]` `runtime/knowledge.py:14-15`

Its understanding so far has a particular place: "It is where the account of the problem as a whole is kept: how the proof goes, what the parts share, where the difficulty lies. Every session receives it in its starting context. No separate document and no separate role maintain such an account; it is the work of the explorers that hold `q0`, and the rules below keep `q0` held whenever an explorer is available for it." `reference/common.md:225`; `[code]` the pack embeds `canon/questions/q0.md`, or the sentence "No exploration has written it yet." when the file is absent, `runtime/context.py:122-125`.

The explorer that holds `q0` is asked to read across the other questions: "When several of them have come down to the same place, or to the same kind of work, that is a fact about the problem which none of those texts holds, and the account of `q0` is where it belongs." `roles/explore.md:82`

### How a question is taken and occupied

An explorer "holds one question, always the whole of it, and one explorer at a time holds a given question. Several explorers can run at once, each on a different question." The reason is the same as for sections: "so that two explorers do not develop the same understanding at the same time without being able to read each other's work." `reference/common.md:267`

`q0` comes first: "Question 0 comes before any narrower question while it is free, so that the root problem as a whole is never left unattended while narrower questions are taken up: the runner assigns question 0 to an explorer launched while it is free, and an explorer still choosing when it becomes free takes it." `reference/common.md:269`. `[code]` At launch, under the coordination lock, the runner writes the explorer's `declaration.json` with `q0` and `"by": "runner"` when `q0` is free. `runtime/runner.py:285-303`. The code comment explains why the commands also enforce the priority: "the runner's assignment at launch cannot reach an explorer that is already choosing when question 0 becomes free." `runtime/coordination.py:405-407`

When the assignment names no question, choosing one is the explorer's first work: it reads the questions the frontier lists, the understanding so far of those it considers, the board and the result of `commands.updates`; among the open questions no exploration holds it chooses "the one your understanding and interest best serve." `roles/explore.md:13`, `:15`

The four question commands (`roles/explore.md:21-26`; `[code]` `runtime/coordination.py:455-556`):

- `commands.question_lease` takes the question's lease if no other session holds it. It is refused when the question is resolved, when another exploration holds the question, when another session holds the lease, "and for any question other than `q0` while `q0` is free: open, held by no exploration, and under no other session's lease or queue." `roles/explore.md:23`; `[code]` `runtime/coordination.py:402-441`, `:455-474`
- `commands.question_wait` joins the queue, returns 0 when the lease is the session's and 124 at the timeout with the place kept, and refuses with 1 in the same cases. `roles/explore.md:24`; `[code]` `runtime/coordination.py:477-508`
- `commands.question_take` occupies the whole question while the session holds the lease, and taking ends the lease. "It refuses a question another exploration holds, a question other than `q0` while `q0` is free, a question that was resolved while you held the lease, or a second question for a session that already holds one." `roles/explore.md:25`; `[code]` `runtime/coordination.py:525-556`, which also refuses a take without the lease at `:541-542`
- `commands.question_release` gives up the lease or the queue place. "A question lease has no time limit: until you take the question, release the lease or end your session, everyone waiting for the question waits for you, and the runner does not count the question as free when it decides whether to launch another explorer." `roles/explore.md:26`

"A question you take cannot be given back, so take it once you have decided to pursue it." `roles/explore.md:17`

Duration: "The occupation lasts through the explorer's peer and review, until its work is published or review decides there is nothing to publish; only then can another explorer take the same question with that work available." `reference/common.md:271`

The one exception to a single holder is an organizer's merge of two questions that explorations already hold: "both explorations keep the merged question." The reason given: "Each took what was then a separate question in good order, and its work is under way or with its peer and review; the merge cuts neither occupation short." `reference/common.md:271`

`[code]` How many explorers run: a question is free when it is open, no unfinished exploration holds or was assigned it, and no live session holds or waits for its lease; "The runner launches another explorer only while free questions outnumber the choosing ones, so that each explorer launched can find a question." `runtime/coordination.py:126-130`, `:148-154`; `runtime/runner.py:1281-1291`. An exploration is requested at every `explore_every`-th attempt launch, and `explore_every` is 1 by default. `runtime/runner.py:334-338`; `runtime/settings.py:32`. Capacity that no attempt can use also goes to exploration. `runtime/runner.py:1339-1345`

Only explorers occupy questions. Attempts and formalizers read a question's statement, grounds and understanding so far. `reference/common.md:233`; `[code]` `runtime/coordination.py:24`, `:388-393`

### How questions enter

"Questions come into being in three ways." `reference/common.md:227`

1. "The peer of any producing session can propose one in its candidate when the work has made such a question visible, and review decides whether to admit it." Review asks whether the question concerns something important enough, whether it is stated specifically and clearly enough "that an explorer can take it up and a later reviewer can tell whether an account answers it", and whether an existing question already asks it. `reference/common.md:227`. Review's verdict on a proposal is `admitted`, `declined` or `revise`. `reference/review-output.md:90`. "The frontier view lists the proposals review did not admit, with those reasons, so that a question worth asking again is not lost." `reference/common.md:227`
2. "The operator who runs the instance can also place questions there directly, outside peer and review; the view names an operator publication as the source of such a question." `reference/common.md:227`; `[code]` the runner has a `questions` command, and the check of its input file is at `runtime/runner.py:48-84`, `:1584`. An operator's question cannot have the ID `q0`. `[code]` `runtime/runner.py:74-75`
3. "And the organizer merges questions that turn out to ask the same thing, after which the old identifiers remain as aliases." `reference/common.md:227`

### How a question is resolved

"A question is **resolved** when review judges that its understanding so far answers what its statement asks. The answer can be that something holds, that it does not hold within a scope the text states and its elements establish, or that the premise of the question fails. What an answer leaves to be done does not keep the question open: the change that resolves the question carries the remainder, as exact statements or as a sharper question." `reference/common.md:229`

The reason for closing an answered question although something remains: "A question that stayed open after it was answered would go to the next explorer in its first wording, and a proposal asking for what actually remains would be declined as a duplicate of it." `reference/common.md:229`; developed at `roles/review.md:99`.

The peer proposes the resolution in its candidate, with the text, and review decides. `reference/common.md:229`; `reference/change-format.md:124`. A resolved question is no longer available to explorers; a later finding can reopen it. `reference/common.md:229`; `reference/review-output.md:126`

`q0` is resolved differently: "No explanation resolves it, because what it asks is the root proposition itself, and only a proof or a refutation of the root answers that. It stays open until the root is settled through a formal proof, in either direction". An informal settlement does not close it, and a contested root does not close it. "This is derived from the root's state each time the view is computed, so a later finding that withdraws the root's formal settlement reopens `q0`." `reference/common.md:231`; `[code]` `runtime/knowledge.py:393-413`

## 4. The formalizer: what it receives and when one is launched

**The launch condition in the guide.** "The runner launches one for a settled statement that the root rests on and that has no formal proof yet, once every statement that its proof names has a formal proof. When a refutation of the root is settled, the runner launches formalizers in the same way for the refutation and for the statements it rests on." `reference/common.md:172`

**The launch condition in the code.** `[code]` `runtime/knowledge.py:443-469`. For every statement reached from the root, or from a settled refutation of the root, through what proofs name: if the statement is not yet formal and not contested, the runner takes the first of its proofs that is settled, is not formal, and names only statements that are formal. The docstring adds that the proof chosen is "the statement's own declaration before any other". The condition "not contested" is in the code (`:460`) and not in the sentence of the guide quoted above.

`[code]` The runner creates a formalizer pipeline for each such proof unless a formalizer pipeline that is not `done` already exists for the same statement. `runtime/runner.py:1159-1168`. A pending formalizer job whose element is no longer formalizable is cancelled. `runtime/runner.py:1307-1311`

**A proof whose Lean text is already complete can still be assigned.** "A proof whose own Lean text is already complete is assigned as well while it is still not formal: it names a declaration whose Lean proof ends in `sorry` although that declaration's statement has a formal proof under another declaration, or it uses an axiom the instance does not allow." `reference/common.md:172`; `roles/formalizer.md:3`

**Why the formalizer has what it needs.** "You were launched because every statement that this proof names already has a formal proof, so the pieces you need are in the canon and can be used by name." `roles/formalizer.md:5`

**When no formalizer is needed.** "An attempt or a peer may already have written a complete Lean proof; if it passes the same review, no formalizer is needed for that statement." `reference/common.md:174`

**Why formalizers exist at all.** "Being settled is a matter of review's judgments. Being **formal** is a matter of Lean. A statement is formal when its Lean proof is complete and depends, through everything of the canon it uses, only on the axioms the instance allows." "The instance is complete when the root is settled through a proof that is formal, or when a statement that Lean has confirmed to be the negation of the root is. An informal proof is therefore never the end". `reference/common.md:170`. `[code]` The default allowed axioms are `propext`, `Classical.choice` and `Quot.sound`, and the settings check rejects `sorryAx` among them. `runtime/settings.py:18`, `:125-126`

**What it receives** is given under "Formalizer" in topic 1.

## 5. Retained work

**Definition.** The sources give no sentence of the form "retained work is ...". The guide that carries the name opens: "An attempt, an exploration or a formalizer leaves its work for a peer, who takes the same line of work over and writes the change to the canon. What the producing session leaves is material and not a finished product, and the peer reads all of it, including the conversation. Two things make that material usable: a report that says where everything is and what it means, and Lean files in which the session's definitions and statements are written and, as far as possible, compiled." `reference/retained-work.md:3`

**What it contains.**

- `output/report.md`, "the entry point to your retained work", with six sections: Current work; Lean definitions and statements; Mathematics; Results and evidence; Approaches and where they stopped; Remaining work and artifacts. `reference/retained-work.md:9-18`
- Lean files. New modules are copied into `output/lean/`, each at the path its module name gives. The text of a declaration whose proof was written anew goes into `output/replace/`, one file per declaration. The working copy of the library stays in `work/`. `reference/retained-work.md:42`. "A declaration that does not compile yet is still worth handing on, with what stopped it." `reference/retained-work.md:42`
- Scratch work in `work/` and results in `output/`, both linked from the report; corrected calculations and abandoned arguments "when they explain what was learned"; for a long computation the inputs, code, outputs and the actual execution result. `reference/retained-work.md:24`
- `output/outcome.json`, with `summary`, `report` and `remaining`. "It is not a success certificate or a publication gate. The runner forwards retained producing material to a peer even if an interruption prevents the manifest or the report from being completed." `reference/retained-work.md:46-53`
- The conversation. The peer reads "the retained conversation from beginning to end"; `retention.json` identifies the available transcript and any limitation in its capture, and `conversation.md` preserves readable message and tool content. `roles/peer.md:19`
- The session's `declaration.json`, with its sections or its question. `reference/retained-work.md:55`

**What the producing session does not write.** "You do not write records or entries yourself." The peer turns the Lean definitions and statements into elements with records, the arguments into the proofs in those records, the account of each approach into an entry among the approaches tried, and what an exploration understood into the understanding so far of its question. `reference/retained-work.md:20`. "Producing sessions do not prepare candidates, and the command for it refuses them." `reference/retained-work.md:42`

**Where it stays.** "The session's own account is kept outside the canon: its report, its conversation and its working files are retained unchanged." "An ordinary session uses the canon and does not read another session's originals." `reference/common.md:137`. The reason no account of a session is published: "Sessions keep coming, but what is learned about the course of the work does not grow with their number, because sessions approach the same statement in the same way and stop in the same place." `reference/common.md:131`

**Why Lean files are part of it.** "Only what has a Lean statement is kept there as a result, and a proof can use a result of this research only by naming its declaration. A result that was found and never stated in Lean therefore cannot be used by any later proof, however carefully it was written up." `reference/common.md:85`. "A result that you obtained and left in prose can be read by your peer, and by no session after it unless the peer states it." `roles/attempt.md:53`

## 6. How a session ends

### The session host

"The session's host, the separate process through which the runner launched your CLI and which stays alive for the whole session, can resume the same conversation with common and role-specific guidance to continue its mathematical work under the role guide." `reference/retained-work.md:59`

`[code]` The runner starts the host as a detached process for every session, and the host starts the CLI only after the runner has recorded the host's identity and written a `GO` file. `runtime/runner.py:360-368`; `runtime/runtime_support.py:427-451`. Every one of the six roles is supervised across turns by its host; the role in the launch policy tells the host which of two kinds of continuation applies. `runtime/runner.py:349-359`

Why the host stays alive: "The host remains alive across those turns, so the session retains its capacity slot and coordination identity, and downstream processing and archiving do not begin midway." `reference/retained-work.md:78`; `[code]` module docstring, `runtime/ending.py:1-5`

Processes: "Processes the session starts belong to it, including computations left running in the background between turns: they continue while the host lives, and on Windows they all end when the session ends, so results a computation has not written to your files by then are lost." `reference/retained-work.md:78`; `[code]` the host puts itself and its descendants in one Windows job that the system terminates when the host exits, `runtime/runtime_support.py:391-424`.

### Two kinds of continuation turn

`[code]` `runtime/ending.py:18-23` names the two groups.

**Attempt, formalizer, explorer and peer** are asked to reconsider ending. `[code]` `runtime/ending.py:18`. The guide: "For an attempt or explorer that undertook research, a formalizer or a peer, ending a CLI turn does not immediately close the session." `reference/retained-work.md:59`

**Review and organizer** are not asked for a decision. "A review and an organizer end with their output, an assessment or an organization, and write no end decision. When a turn of theirs ends and that output does not pass the transport check, the host resumes the same conversation with what the check found, instead of leaving the whole assignment to a new session: the turn of a reviewer can end while the sub-reviewers it delegated to are still at work." `[code]` `runtime/ending.py:19-22`. The guide says the same at `reference/tools.md:57` and `roles/review.md:41`.

### What is asked in a reconsideration turn

The prompt of a reconsideration turn is `resume/common.md` with the role's file from `resume/` placed where `{{role_guidance}}` stands, the request ID where `{{request_id}}` stands, and the problem found in the previous turn where `{{previous_error}}` stands. `[code]` `runtime/ending.py:71-97`; `resume/common.md:1`, `:7`, `:11`

The common frame asks the session to apply its role guide's standard for ending to the investigation as a whole. Its central sentences: "That conclusion must come from sustained, serious mathematical effort in the responsibility your role describes, including pursuing possibilities beyond the approaches that failed. Being able to explain difficulties, list attempted methods, or write a persuasive account of why you stopped is not itself grounds for ending." "If there is still a meaningful mathematical direction you can pursue within your role, pursue it in this conversation, even when it is difficult, substantial, or offers no quick result. A direction is meaningful when it can change what is known, in the sense the common introduction describes; more of the same activity without that prospect is not such a direction." "A completed role assignment may end under the role guide even when the root remains unresolved." `resume/common.md:5`

It tells the session how to answer: "Continue without submitting an ending decision while you are pursuing the research. When ending is justified, use the exact output/end-decision.json format in context/reference/retained-work.md." "Use basis=task_completed only if the work you took on is complete; otherwise basis=no_way_forward requires the judgment described above." `resume/common.md:7`

It states what the decision is not: "Your judgment does not constitute independent review, and it does not change the standing of any statement in the canon. Your original assignment, instructions, working directory, and registered sections or occupied question remain in force." `resume/common.md:9`

The role-specific parts:

- Attempt: "Stay with the unresolved difficulty." "Neither does finishing a smaller statement nearby when that leaves the difficulty where it was. Carrying a verification further when it closes nothing and has taught you nothing more about the object does not continue the research on what you took on; it is a sign to look at the problem differently." `resume/attempt.md:3`. It also restates that what was found is kept only when stated in Lean. `resume/attempt.md:5`
- Explorer: "Finding one interesting phenomenon or describing a promising direction does not itself complete the exploration." `resume/explore.md:3`. "If you hold no question yet, taking one comes first". `resume/explore.md:1`
- Formalizer: "A compiled helper lemma, a proof under an added hypothesis, or identifying a missing input does not complete the assigned proof." `resume/formalizer.md:3`
- Peer: "A candidate that prepares without errors or a successful transport check does not itself complete that responsibility." "Judge completion by the role guide: a sound confirmation or clarification may be the right contribution, and you need not manufacture novelty, pursue every possible extension, or settle the root to finish a valuable change." `resume/peer.md:3`

The guide describes the purpose of the turn: "This continuation asks you to apply the existing criteria for completing or ending your work; it does not replace those criteria." `reference/retained-work.md:59`

### The end decision

The file is `output/end-decision.json` with exactly four fields: `request_id`, `decision` (the value `end`), `basis` (`task_completed` or `no_way_forward`) and `explanation`. `reference/retained-work.md:63-72`; `[code]` `runtime/ending.py:51-68`

"A decision counts only as the answer to such a request. One written before any request, in your first turn, is set aside unread, and the host resumes the session once to ask". `reference/retained-work.md:61`. `[code]` After the first turn no request exists yet, so the submitted file is moved out of `output/` and not checked. `runtime/ending.py:187-191`, `:228-235`

"A missing or invalid decision leads to another reconsideration turn while the configured allowance remains." `reference/retained-work.md:72`

The host moves a submitted decision out of `output/` before checking it; the code comment gives the reason: "Left in output/, it would be frozen into a peer's candidate and checked again after a later request." `[code]` `runtime/ending.py:187-191`; `reference/retained-work.md:74`

### What ends the continuation turns

`[code]` `runtime/ending.py:172-273`, in the order in which the host tests after each turn:

1. **Interruption.** The session was cancelled, or the turn ended with a provider or model refusal, or the turn exited with a nonzero code that was not caused by the output-token limit. The host records an authorization with `source: runner`, `basis: interrupted`. `:192-199`
2. **A valid no-research outcome** (attempt and explorer only). `basis: no_research`. `:203-209`
3. **A changed conversation identity** on a resumed turn. `basis: resume_unavailable`. `:210-217`
4. **For review and organizer: the transport check of the output passes**, or its only finding is that the candidate changed after the review was assigned, which the runner deals with. `basis: output_checked`. `:219-226`
5. **For the other four roles: a valid end decision for the current request.** `source: worker`, with the worker's basis. `:228-233`
6. **The limit.** When the number of resumptions already made is not below the configured maximum, the runner authorizes the end itself with `basis: resumption_limit`. `:239-246`
7. **No conversation identity available for resuming.** `basis: resume_unavailable`. `:247-254`

Otherwise the host writes a new request, waits while dispatch is stopped or the provider or model is blocked, and starts the next turn by resuming the same conversation. `:255-273`

The maximum is the setting `max_end_resumptions`, 3 by default; 0 is allowed. `[code]` `runtime/settings.py:38`, `:78-79`; `runtime/runner.py:353`. With the default a session therefore has its first turn and at most three resumed turns. `[inferred]` from `runtime/ending.py:181`, `:239`.

The guide on the limit: "At the maximum it authorizes the handoff itself, recording `source: runner` and `basis: resumption_limit`. That is an operational limit, not the worker claiming completion or an impasse." "Neither kind of end authorization changes the standing of any statement; the peer and independent review still assess the retained work." `reference/retained-work.md:74`

A turn that ended because one response exceeded the output-token limit is resumed, and the next turn is told what happened. The code comment: "Only the output-token cap is resumable: the conversation and files survive it." `[code]` `runtime/ending.py:26-30`, `:193-195`, `:236-238`

"Dispatch stop also holds new resumption turns." `reference/retained-work.md:80`; `[code]` the host waits while `control/STOP` exists, `runtime/ending.py:116-134`.

The files: the first turn's prompt and CLI streams stay at the session root; resumed turns have their own folders under `turns/`; the host's record is `end-check.json`. `reference/retained-work.md:74`, `:76`; `[code]` `runtime/ending.py:33-34`, `:106-113`

### What the review and the organizer are told

Their prompt is `resume/output.md` with the role's file inserted. It says: "Your previous turn ended, and the transport check of your session does not yet accept your output." and names the problem. `resume/output.md:3-5`. It explains what was lost: "Ending a turn ends the CLI. An agent you had delegated to and that was still at work at that moment ended with it: what it had already written under `work/` is still there, and the rest of its work is lost." `resume/output.md:7`. "The session is finished when that check passes." `resume/output.md:9`

For a review: "A sub-review whose report is under `work/` stands as it is. One that had not reported when your turn ended has to be dispatched again, with the same complete briefing, and its report has to be written before you judge." `resume/review.md:1`. For an organizer: `resume/organizer.md:1-3`.

The same maximum applies to these turns; at the limit the explanation recorded is "The configured maximum of resumptions has been reached, and the output still does not pass the transport check." `[code]` `runtime/ending.py:239-246`. After that "a fresh session takes the stage". `reference/tools.md:57`

### A session interrupted from outside

"A provider refusal, execution failure or operator cancellation ends the interrupted work through the existing retention path; an unavailable native conversation identity is recorded as `resume_unavailable`, without substituting a fresh conversation." `reference/retained-work.md:80`

"If an external interruption ends an attempt, explorer or formalizer, what it retained still goes to a peer. The interruption is an execution outcome, not a judgment that the researcher exhausted the mathematics." `reference/common.md:305`

`[code]` What the runner does when it collects a session, `runtime/runner.py:408-552`:

- **A producing session** (`:458-488`). A no-research outcome is read only when the session exited with code 0, without refusal or launch error, and was not interrupted (`:459-469`). Otherwise, if the session left any material (CLI or native conversation activity, or any file under `output/` or `work/`), the pipeline moves to the stage `peer` and a peer job is created with the session's directory, role, element, sections and question (`:470-488`). If it left no material, the job is retried with a new session (`:472-478`). The guide: "It sends retained work to a peer; a failed launch without retained material is retried." `reference/retained-work.md:92`
- **A peer, a review or an organizer** (`:489-512`). If the session was interrupted, refused, failed to launch or exited unsuccessfully, the job is retried with a fresh session, and the failed session's folder is added to `previous_partial_sessions` in the task (`:396-402`). A failed peer's sections stay with its pipeline (`:403-405`). If the session ended normally and its output does not pass the transport check, the job is likewise retried (`:504-512`). The guide: "If one of those sessions is interrupted, the runner preserves its partial material and starts a fresh session for that stage." `reference/tools.md:57`; for a review, `reference/review-output.md:140`.
- If the host itself was lost before recording an authorization, the runner records `interrupted`: "Host loss is an interruption, never the worker deciding to end." (`:419-424`)

### A producing session that found no work

"An attempt may read the research context and check the frontier and the board, yet find nothing it can take on. An explorer launched without an assigned question may find, after reading the questions and the board, that every open question is already held. That assessment does not itself begin research." Such a session writes `{"disposition": "no_research"}` to `output/outcome.json`. "After a successful exit, the runner retains your files and conversation and closes the pipeline without a peer or a review. That decision is final for this session: later changes in available work do not reopen it." `reference/retained-work.md:84-90`

What counts as research: "Reading the canon to understand the statements and questions, what is established about them and whether they are available can be part of choosing work. Developing or testing your own mathematical approach is research, including before a section is registered: this includes developing an argument, investigating a counterexample, running a mathematical computation, or writing definitions and statements of your own in Lean, even without a successful result. Preserve that work for a peer." `reference/retained-work.md:92`

A free part for which the attempt sees no approach is not "no work": "It is available work, and finding a way into it is the research an attempt is launched to do, because the absence of an idea at the moment is not the exhaustion of means." `roles/attempt.md:37`

`[code]` The outcome is accepted only from an attempt or an explorer, only when the session's `declaration.json` holds no section and no question, and only with the exact value `no_research`. `runtime/availability.py:50-73`. A formalizer cannot use it. `[inferred]` from `:61-62`. An invalid outcome does not discard the work: "An invalid opt-out cannot discard retained research." `runtime/runner.py:463-466`. A valid outcome ends the session at once, without a reconsideration turn. `runtime/ending.py:203-209`. The runner then marks the session and the pipeline with `disposition: no_research` and the stage `done`. `runtime/runner.py:1200-1202`

**The availability report.** An attempt's no-research outcome can also report that other pipelines' sections cover all the work that remains, with `"status": "all_unresolved_work_occupied"` and the `availability_snapshot` token returned by `commands.updates`. `reference/retained-work.md:94-106`. "You judge whether those sections cover the work. The runner checks whether that state has changed; it does not prove coverage or interpret a prose explanation. Not seeing a promising approach yourself is not enough to report that all the work is occupied." `reference/retained-work.md:108`. An explorer's outcome carries no such report, "because the runner sees which questions are free without a judgment." `reference/retained-work.md:96`; `[code]` `runtime/availability.py:71-72`

"An accepted report makes the runner wait before launching further attempts. Three things give it reason to reconsider." They are the end of a section's occupancy on an element that still remains, an element that is new among the work that remains or has become work again, and an operator request. "The runner then launches one attempt to assess availability again." "Exploration continues on its own questions while attempts wait." `reference/retained-work.md:112`; `[code]` `runtime/runner.py:1178-1229`; `runtime/availability.py:40-47`

`[code]` Independently of any report, the runner does not launch an attempt when every element of the work that remains is held whole or already has a session waiting for its lease, "since launching another attempt there would only lengthen that queue." `runtime/runner.py:1231-1244`, `:1315-1316`

### After the root is formally settled

"Once the root is settled through a formal proof, in either direction, the runner stops launching attempts and explorations. Existing sessions retain their normal scope, and peer, review, formalizer and organizer work continues as its inputs become ready. The runner finishes after this remaining processing ends." `reference/common.md:309`; `[code]` `runtime/runner.py:1014`, `:1298-1303`, `:1334-1335`

## 7. The peer

### What it receives

`task` in `input.json` gives "the producer's directory (`source`) and role (`source_role`), the sections it registered (`sections`) or the question it held (`question`), and, for a formalizer, the element it was assigned (`element`). When you take the place of an earlier peer, `previous_error` says why and `previous_partial_sessions` lists the folders of the earlier peers." `roles/peer.md:19`; `[code]` `runtime/runner.py:483-486`, `:605-610`

It reads the producer's context, its report, "the retained conversation from beginning to end and all the artifacts the producer left." `roles/peer.md:19`. The common introduction: "The peer receives the attempt's original context, its available conversation, its notes, its working files and the Lean statements it wrote. It reads all of it and forms its own understanding of the mathematics. A valid identity in an abandoned proof or a restriction explained earlier in the conversation can matter even if the attempt's final account barely mentions it." `reference/common.md:117`

### What it is asked to do with the mathematics

"As a peer, you are the second researcher on a line of work." "What it left is material, not a finished product. You read all of it, work the mathematics yourself, complete what was left unfinished where you can, and then make the change to the canon through which every later session will meet this work. You are neither a translator of the producer's mathematics into Lean nor a checker of it." `roles/peer.md:3`. The reason given in the common introduction: "writing a statement in Lean is part of doing the mathematics and cannot be handed to one of the two." `reference/common.md:119`

The mathematical work "comes first and takes most of your effort". `roles/peer.md:5`

- Ambition: "The producer's unfinished opportunity can become your proof, counterexample, clearer formulation or explanation of an obstruction. Its endpoint does not set the ceiling for the contribution. At the same time, there is no obligation to disagree or manufacture novelty." `roles/peer.md:13`
- "Do not hand onward by habit a problem you can settle yourself." `roles/peer.md:29`
- The producer's own labels are examined: "The producer's final answer and its labels of success or failure are assertions to examine against this material." `roles/peer.md:21`
- Earlier work: "You are the last session that can notice, before the work enters the canon, that something the producer derived was already there or already in the literature." It traverses the canon for the definitions the work speaks of and searches the literature for the producer's main tools and results. `roles/peer.md:33`
- Scope: for an attempt it inherits the registered sections; for a formalizer the assigned element; it may register a further free section through the element's lease; "An exploration brings no registered section with it. Its freedom to work across the problem passes to you". `roles/peer.md:35`
- "A complete Lean proof is something you may write when it is useful, and are not obliged to write." `roles/peer.md:39`
- Before offering a proof it reads it once more under the two considerations of review and simplifies it; "Simplify for the sake of the proof, and do not treat these considerations as a reason to withhold it. If you have proved something and are unsure how review will judge it under one of them, enter the proof and say what you are unsure of. That judgment is review's, and review can judge only what is offered." `roles/peer.md:61`

### What the candidate contains

"A candidate change, called a candidate for short, is the change to the canon that a session proposes." `reference/change-format.md:3`. "A candidate is the proposed change to the canon: new elements with their records, new proofs for statements that already stand there, and the written state the next paragraphs describe." `reference/common.md:119`

The candidate is the `output/` folder of the peer's session. `reference/change-format.md:21`. Its parts (`reference/change-format.md:23-34`):

| Part | Content |
|---|---|
| `change.json` | the manifest: required `title` and `description`; optional `replace`, `questions`, `resolutions`; any other key is rejected (`reference/change-format.md:40-58`) |
| `lean/<Library>/...` | new modules |
| `replace/<file>.lean` | the new text of a declaration whose proof is replaced |
| `records/<Name>.md` | new records, and records that replace existing ones |
| `approaches/<Name>/<id>.md` | new approach entries, and entries that replace existing ones |
| `questions/<question>.md` | an understanding text that replaces the existing one |
| `evidence/<Name>/...` | files that records refer to |
| `bibliography.bib` | entries to add to the bibliography |
| `prepared.json` | written by `commands.prepare` |

What a candidate can do (`reference/change-format.md:9-15`): add elements; replace the proof of a statement, leaving name and statement as they are (a first proof of a statement without one counts as a replacement of the body `by sorry`); replace written texts and add approach entries; propose questions and resolutions; add evidence and bibliography entries.

What it cannot do: "A candidate cannot change the statement of an existing declaration, change an existing definition, remove a declaration, or add a declaration to an existing file." `reference/change-format.md:17`. The invariant behind this is "the statement of an element is never changed in place", and its reason is the time a candidate waits: "A candidate is frozen when its peer ends, review then takes the time it needs, and meanwhile other candidates are published. A candidate rests on statements, so nothing that others published in the meantime takes away what it rests on: every statement it uses still stands as it stood." `reference/common.md:127`

Further content the peer decides:

- Every mathematical assertion the research should keep is stated in Lean as an element. `roles/peer.md:47`
- Each element has a record, with a self-description and a weight (unit or step). `roles/peer.md:65-67`
- What the work learned about the course of the work is entered among the approaches tried on the statement it was aimed at, in one of three ways: "a new approach as a new entry, an approach carried further as the replacement of its entry, and nothing for an approach repeated to the same stopping point." `roles/peer.md:73`
- When the source was an exploration, the understanding so far of the question it held is replaced by a complete new text. `roles/peer.md:77`
- A question the work brought into view may be proposed, and a resolution of an existing question may be proposed with the text that settles it, whichever role produced the source. `roles/peer.md:81`, `:83`
- The title and description say what the work changed in what is known, and "what the producer established and what you added, so that review can assess both; your additions receive the same scrutiny as the producer's work." `roles/peer.md:89`

Before ending, the peer runs `commands.prepare`, which applies the candidate to a copy of the current library, compiles it through the Lean broker and checks what a machine can decide. `roles/peer.md:95`; `reference/change-format.md:126-140`. "The transport check, `commands.check`, refuses a candidate that was not prepared, that changed after it was prepared, or whose preparation reported errors." "Neither command judges mathematics." `reference/change-format.md:144`

After the peer's session ends, "the runner copies `output/` to a fixed place, records the identity of every file, and gives that copy and the producing originals to a fresh reviewer. The candidate is then frozen; nothing in it changes during review." `reference/change-format.md:279`; `[code]` `runtime/runner.py:513-533`. "A peer's candidate is frozen only after its logical session ends; resumed turns can still develop its output before independent review." `reference/retained-work.md:78`

## 8. The review

### The sub-reviewers

"One reading, however careful, has one set of blind spots. Every review assignment, candidate or comprehensive, is therefore examined by three sub-reviewers before you judge it, and the final judgment is yours, made from the evidence with their reports beside you. The two parts are both required: the sub-reviews widen the examination, and your own direct examination keeps the assessment from becoming a vote." `roles/review.md:35`

- The reviewer reads the assignment first and does not form a verdict yet. `roles/review.md:37`
- It dispatches three sub-reviewers, "each as a separate delegated agent that works inside your session directory". Each receives the same complete briefing and must judge every element and proposal, give the exact location of every defect it asserts, say what it reproduced and what it could not examine, and write its report to its own folder under `work/`. `roles/review.md:39`
- Independence: "none sees another's report or your preliminary reading, and you do not tell them what you expect them to find." `roles/review.md:39`
- Model: "Give each the strongest model available to your session and the effort level you were launched with." They may be given different emphases, "provided every one of them still decides every element." `roles/review.md:39`
- A session that cannot delegate, "as a Codex session cannot", performs the three examinations itself as separate complete passes and says so in the feedback. `roles/review.md:39`; `reference/tools.md:51`
- The turn stays open until the three reports are under `work/`, because a sub-reviewer ends with the CLI turn that launched it. `roles/review.md:41`
- The reports are read "as evidence about the examination, not as verdicts to count." "Where they agree, confirm the agreement against the sources yourself at the places that carry the judgment; three readers can share one misreading." "your judgment is not the majority's, and it is not a compromise between the reports." `roles/review.md:43`
- The sub-review reports stay under `work/`; "nothing they wrote is published as a judgment of the research unless you adopt it, and then the judgment is yours." `roles/review.md:45`

A sub-reviewer is a delegated agent inside the review session and not a session launched by the runner. `[inferred]` from `roles/review.md:39` and `reference/tools.md:51` ("A delegated agent runs as part of your session").

### What the review compiles and checks itself

"The compile of a proof that is complete in Lean and the reading of its axioms are your own work: they belong to this reviewing session, and a sub-reviewer's reading of the sources does not replace them." `roles/review.md:47`

"When a candidate offers a proof that is complete in Lean, confirming it requires your own compile of the candidate and your own reading of the axioms the proof depends on." The compile is made with `commands.verify`. `roles/review.md:145`

`commands.verify` "applies the frozen candidate to a copy of the canon as it is now, compiles the modules the candidate changes afresh in your own session, and reports whether the build succeeded, the build's ID, and for each added or replaced statement the axioms its proof depends on through everything of the canon it uses." `reference/review-output.md:96`. When the review confirms a proof that is complete in Lean it adds `"formal_check": {"build": ...}`; the transport check confirms that this is a finished build of the review's own session and "that the modules the candidate changes were compiled by you and not taken from the cache". `reference/review-output.md:98-104`

"The check does not read the axioms; that is your judgment". `reference/review-output.md:106`. `sorryAx` among the axioms means the proof or something it names is not complete in Lean; "Any other axiom outside the allowed list is to be named in your reason: a compile that succeeds can still depend on an axiom the instance does not allow, and searching the source for the word `sorry` misses what enters through other declarations." `roles/review.md:147`

What the compile does not settle: "A compile checks the proof of the Lean statement. It does not check that the statement says what was meant". The root is the exception, because its Lean statement was fixed when the instance was created; "For that reason your compile and your reading of the axioms are the last check before the research counts as complete". `roles/review.md:149`

If the compile cannot be completed: "do not confirm a proof on the strength of its Lean text; use `undetermined` and say what prevented the check." `reference/review-output.md:108`

### The judgments it makes

For a candidate the review judges "every element the candidate adds and every element whose proof it replaces: whether its Lean statement says what was meant, whether its proof is correct, whether a correct proof is accepted, and whether its record describes it truly. You also say what the work contributed to the research." `roles/review.md:5`

The judgments of an element, each with its place in the role guide:

| Judgment | Source |
|---|---|
| Whether the Lean statement says what was meant. "Lean does not confirm that the statement is the one the work intended. That judgment is yours, and no later step repeats it." | `roles/review.md:57` |
| Whether a definition denotes the intended object, and whether the canon already has it. "A duplicate still publishes, with your reason naming the existing definition". | `roles/review.md:59` |
| Whether a statement without a proof is worth holding. | `roles/review.md:61` |
| Whether the proof is correct. A proof is judged "as an argument from the statements it names, each taken as stated"; that a named statement has no proof yet "is not a defect of this proof". | `roles/review.md:63` |
| Whether a correct proof is accepted (the two considerations below). | `roles/review.md:67` |
| Whether a new proof takes the place of the old one. | `roles/review.md:69` |
| What the review thinks of a division, written into the reason. "It admits nothing and blocks nothing, and it is separate from whether that proof is correct." | `roles/review.md:71` |
| Whether the record describes the element truly, including that the proof in natural language is the same argument as the Lean proof. | `roles/review.md:73` |

In `output/assessment.json` each element has one entry with four judgments (`reference/review-output.md:48-72`):

- `correct`: `confirmed` ("You examined the proof and found it correct."), `not_confirmed` ("You found a gap or an error."), `undetermined` ("You could not complete the judgment."), or `not_applicable` (a definition, or a statement without a proof). `reference/review-output.md:52-57`
- `accepted`: Boolean, "made only of a proof you confirmed". `reference/review-output.md:61`
- `replaces`: Boolean, required for each replaced element whose declaration already has a proof in the canon. With `true` the runner puts the candidate's declaration text and record in place; with `false` it leaves the declaration and its record as they are, and what was tried stays among the approaches tried. `reference/review-output.md:63-66`
- `reason`: required; the view of the element shows it in full and the frontier shows about its first 160 characters on the line of an element whose proof is not confirmed or is held back. `reference/review-output.md:72`

Beside the elements the assessment holds `publish`, `reason`, `contribution`, `feedback`, `questions`, `resolutions`, `concerns`, `findings` and `formal_check`. `reference/review-output.md:11-40`

"You do not write whether an element is settled or formal. The runner computes both from your verdicts, from what each proof names in Lean and from the axioms it depends on." `reference/review-output.md:80`

The review also judges the written state the change attaches: approach entries against the originals, and a replacing understanding text against the text it replaces, reading "what the new text removed as carefully as what it added." `roles/review.md:85`

The contribution: review says "what it changed in what is known, for example what it closed, what it let the research see that it could not see before, or how it changed the approach, or that it left what is known unchanged." `roles/review.md:79`. The runner writes this text at the end of every approach entry and every understanding text the change carries and into the log of changes, "because that is where a session choosing its work will read it". `reference/review-output.md:86`

### The standings a statement can have

"According to the proof it carries and to review's judgments of that proof, every statement of the canon is in one of four states. This state is the **standing** of the statement." `reference/common.md:149`

| Standing | Meaning | Work remains on this proof |
|---|---|---|
| no proof | "The statement has neither a complete Lean proof nor a proof written in its record." | Yes |
| proof not confirmed | "A proof was offered, and review found a gap in it, could not complete its judgment, or has not judged it." | Yes |
| correct, held back | "Review confirmed the proof and did not accept it, and gave the reason." | Yes |
| accepted | "The proof is correct and accepted." | No |

`reference/common.md:151-156`; `[code]` the four names at `runtime/knowledge.py:18-20`.

"A definition has no proof and none of the four states". `reference/common.md:160`. The standing is, strictly, that of the declaration that carries the proof; a statement can have further proofs under further declarations, each with a standing of its own. `reference/common.md:162`

Three further terms sit on top of the standing.

- **Settled.** "A proof is **settled** when it is accepted and every statement of the canon that it names is settled, and a statement is settled when one of its proofs is." "So a statement whose own proof is accepted can still be unsettled, because something that proof rests on is not." `reference/common.md:166`
- **Formal.** Quoted in topic 4. `reference/common.md:170`
- **Refuted and contested.** A statement is refuted when a settled proof establishes a statement that Lean has confirmed to be its negation. `reference/common.md:205`. `contested` means that both a statement and its negation are settled; such a statement "counts as neither open nor finished until a later review locates the failure". `reference/common.md:209`

The elements the instance began with are a special case: among them a statement whose Lean proof is complete stands as accepted, and one with only a written proof stands as not confirmed until a review judges it. `reference/common.md:158`

### The considerations that decide whether a correct proof is accepted

"Review makes two judgments about a proof. The first is whether the proof is correct. The second is made only of a correct proof: whether it is accepted. The second judgment exists because a correct proof is not always the proof the research should stop at." `reference/common.md:145`

Both considerations "come from the user who runs the research. Both are questions about the mathematics in front of you, and you answer them by reading the proof." Each can be turned off by the settings `acceptance.decline_reducible_proofs` and `acceptance.decline_uncomprehended_computation`. `roles/review.md:109`; `[code]` both default to true, `runtime/settings.py:39-41`.

**First: can the proof clearly be made simpler?** "You should not yet accept a correct proof when you judge that it can still clearly be made simpler. The reason is that a proof which can be made simpler becomes more concise when that is done, and the research should have the concise proof. The reason is not the cost of formalization. Nor is it the number of elements that the proof names." `roles/review.md:113`. The threshold: "A simplification clearly remains when you can point to the place in the proof and say how the proof could be simplified there. Any proof may one day be replaced by a better one. That general possibility does not count; if it did, no proof could ever be accepted. You do not have to carry out the simplification." `roles/review.md:117`. Two things are named as not being simplifications: deleting the use of a published result because only part of it is needed, and comparing how many published results each version depends on. `roles/review.md:121`. A proof that derives its statement from other statements is read together with the published proofs of what it names. `roles/review.md:123`

**Second: is part of the statement established only by large computation done without understanding?** "You should not yet accept a proof when it shows some part of its statement to be true by computing over a large range, and gives no account of why that part is true. The computation does show that the part holds, and the proof is correct. The reason for not yet accepting it is this. Even where a computation can show at once that something is true, the more mathematical work of explaining why it is true should continue. A statement whose proof is accepted is no longer work that remains, and no session then takes up that explanation." `roles/review.md:127`. Its limits: "This question is not directed at computation in general." "There is no numerical boundary." `roles/review.md:129`. One case the user decided is given for comparison: a lookup of a few dozen inequalities and a few thousand entries in an exact table that an existing paper had computed "is not a large computation in the sense meant." `roles/review.md:131`

**When the answer is yes.** "Answering yes to either question does not mean that the proof is wrong. Confirm the proof as you otherwise would, and decide publication as you otherwise would. The element is published, and other proofs can use it. The difference is that the proof is not accepted: the statement's standing is "correct, held back", it stays among the work that remains, and nothing that rests on it is settled through it." `roles/review.md:137`. The hold is placed "on the element in which the difficulty lies." `roles/review.md:139`. The reason is written so that a later reader can tell that the proof was not rejected for a defect. `roles/review.md:141`

### Publication and replacement

"Review is a judgment and not a gate." It decides whether a candidate holds anything worth keeping and whether a new proof takes the place of an old one. "What it does not do is hold useful material back until it has been repaired." "An element whose proof review could not confirm enters the canon in that state, with review's reason beside it". "Nothing is returned to a session for repair; a later session does the repair, starting from what was published and from the reason." `reference/common.md:123`

"Exclude a candidate only when no useful substance can be recovered for publication." `roles/review.md:89`. With `publish: false` nothing of the candidate enters the canon, and the assessment may admit no question, accept no resolution and report no concern or finding. `reference/review-output.md:112`

Replacement cases: a new proof that is correct and accepted replaces the old one; one that is correct, improves on the old one and still leaves room replaces it and the statement stays held back; one that is wrong or no better replaces nothing. "Where the statement is settled through the old proof alone, a new proof takes its place only when you confirm and accept it, since under any other verdict a settled statement would stop being settled". `roles/review.md:69`

### What the review is asked not to do

- Not to supply a missing argument and then certify it. "Supplying an essential new proof and certifying that proof in the same act does not provide independent assessment. If confirming a proof would require such a contribution, identify the missing argument and preserve useful diagnostic work." `roles/review.md:27`. "do not count a proof as confirmed merely because you devised an argument the candidate did not supply." `roles/review.md:29`
- Not to treat difficulty of reading as a defect. "An unusual notation, an omitted explanation that follows directly from the supplied material, or your own initial difficulty following an argument does not establish a mathematical defect." `roles/review.md:13`
- Not to let one defect or one elegant proof decide the rest of the candidate. `roles/review.md:15`, `:53`
- Not to replace reading by numbers that are easy to count. `roles/review.md:25`
- Not to adopt earlier assessments as the frame before forming its own judgment. `roles/review.md:31`
- Not to form a verdict before the sub-reviews, not to tell the sub-reviewers what it expects, and not to count their reports as votes. `roles/review.md:37`, `:39`, `:43`
- Not to repair a statement that does not say what was meant: "a statement never changes in place: say exactly what the Lean statement asserts and what was intended, so that the intended statement can enter under a new name." `roles/review.md:57`
- Not to reword a proposed question: "do not reword the proposal yourself, but say in the reason what is unspecific and what would have to be made explicit". `roles/review.md:93`
- Not to author replacement proofs in a comprehensive review: "If fundamental mathematics is missing, report that work and do not author replacement proofs." `roles/review.md:163`
- Not to change the candidate, the canon or the originals. "The candidate you assess and the canon remain unchanged." `reference/review-output.md:5`. "Keep the source directories and archives unchanged". `roles/review.md:157`
- Not to claim that all consequences of a defect have been assessed merely because the defect was found. `reference/review-output.md:132`

### Concerns, findings and a comprehensive review

"A **concern** is a reported challenge to the proof of an element." It has `id`, `targets`, `reason` and `evidence`. "Publication gives the concern the stable ID `<publication ID>/<your id>` and creates comprehensive review work. A concern annotates and changes nothing; only a finding changes a verdict." `reference/review-output.md:118`; also `reference/common.md:287`

"A **finding** has `concerns`, the list of existing concern IDs it addresses, which may be empty; `status`, one of `cleared`, `confirmed` and `undetermined`; and `reason`." "A status alone leaves every verdict as it was; verdicts change only through the lists below." `reference/review-output.md:120`. The lists are `invalidates` (the confirmation of each element's current proof is withdrawn; its standing becomes "proof not confirmed"), `validates` (the confirmation is established or restored; whether the proof is accepted is not changed) and `reopens` (the resolution of each named question is withdrawn). `reference/review-output.md:122-126`

What a withdrawal changes for other elements is computed and not written: "Withdrawing the confirmation of one proof leaves the verdicts of the elements that use it as they are. What changes for them is computed: no statement is settled through the withdrawn proof any more, although a statement with another settled proof remains settled through that one." `reference/review-output.md:130`

Nothing is deleted: "The elements, their records and the earlier judgments stay in the canon with your findings attached." `roles/review.md:163`

A review of a candidate can raise a concern or write a finding about an element already in the canon. `roles/review.md:105`; `reference/review-output.md:132`. "When such a finding withdraws a confirmation without naming an existing concern, the runner opens a concern on those elements, so that a comprehensive review examines the broader consequences." `reference/review-output.md:132`

"A **comprehensive review** is an assignment of the same review role to examine questioned evidence and its actual uses in later arguments. It is triggered by a concern, by a contested statement whose opposing proofs need their failure located, or by a request to examine named elements; it is not another routine stage for every new candidate." `reference/common.md:287`

- Its task has `kind: "comprehensive"`, `concerns`, `conflicts`, `requested_elements` and `purpose`. `reference/review-output.md:136`; `roles/review.md:155`
- `[code]` The runner creates one when no comprehensive review is pending or running and there is a concern that is not cleared and not yet processed, or a conflict not yet processed. `runtime/runner.py:1152-1158`. Comprehensive reviews run one at a time. `runtime/runner.py:1252-1261`
- It is examined through the three sub-reviews as a candidate review is. `roles/review.md:155`
- It traces the questioned element to its evidence and follows the elements that actually use it; "the uses are found by traversal and not by search". "One comprehensive review handles this connected work; the runner does not launch a separate reviewer for every use." `roles/review.md:155`
- It may inspect the originals of the work that added the element, through the `provenance.json` of the change. "This access is confined to originals identified through the elements relevant to your assignment." `roles/review.md:157-159`
- A conflict names a contested statement; the review follows each side until it locates the failure and withdraws the confirmation of the proof it finds defective. "If you cannot determine which argument fails, explain what you examined and what remains open; the statement then stays contested." `roles/review.md:165`
- Its assessment contains `feedback`, `findings` and optional `concerns`; it has no publication decision, no element entries and no `contribution`. "The runner publishes this assessment directly under `knowledge/reviews/` and applies its findings". "No peer or further review is needed for your judgment to take effect." `reference/review-output.md:138`

## 9. The organizer

### What it does

"As an organizer, you look after the coherence of the canon as it grows. Sessions add to it independently and at the same time, so the same object can come to be defined twice, the same content can be stated twice, a proof can be left standing beside the statement it proves instead of under it, and two questions can ask the same thing. None of these is an error in any one change. Each makes the canon harder to use as a whole, and each can be mended without doing new research." It has three jobs: "joining what is the same, rearranging modules, and merging questions that ask the same thing." `roles/organizer.md:3`

**The batch.** "Your assignment names a **batch**: the published changes that no earlier organizer has answered for, fixed when you launch." The organizer acknowledges the batch whether or not it found anything to do. `roles/organizer.md:5`. "The automatic organizer is launched once the number of published changes that no organizer has yet taken into its batch reaches the instance's setting, four by default." "Organizer outputs and comprehensive reviews do not count toward the number." `reference/organizer-output.md:15`; `[code]` `runtime/runner.py:1169-1172`, `:267-269`; the setting is `organizer_every_records`, `runtime/settings.py:33`. Organizers run one at a time. `[code]` `runtime/runner.py:1252-1261`

**Why sameness matters.** A session learns what the canon holds about an object by traversal from its definition. "When the object has two definitions, that answer is half of what is known, and nothing tells the session that the other half exists." `roles/organizer.md:9`. "An element stating that the two agree repairs this. Both names keep working, everything stated for either stays as it is, and a session that traverses one definition meets the agreement and through it the other. That is why you join things by adding an element and never by renaming or removing one of the two." `roles/organizer.md:11`

**Rearranging modules.** A proof that rests on theory built later on top of the statement's own module cannot stand where the statement is declared, because Lean modules cannot import one another in a cycle; it enters as a separate declaration, and the statement then shows two proofs. The organizer moves declarations between modules until the proof can stand under the statement's own name, removes the separate declaration, and turns every reference to it into a reference to the statement's own declaration. "Change nothing else in those proofs." `roles/organizer.md:33-35`. The proof that ends under the statement's name keeps the verdict the separate declaration had. `roles/organizer.md:37`. The cost: a frozen candidate that names the removed declaration no longer builds at its turn, and a replacement peer makes it again. `roles/organizer.md:39`

**Merging questions.** The organizer compares what each question asks, the grounds, and the understanding so far of each; "If they are the same question, merge them with a reason; an exploration holding either continues to hold the merged question." `roles/organizer.md:45`. `q0` is never merged, in either direction. `reference/organizer-output.md:17`

**What is not the organizer's to do.** "You therefore write no survey of the research, and you do not sort its elements into groups. Definitions are ordinary elements, met through the statements that use them, so you keep no list of shared terms and promote no term to one. And you do not remove elements that nothing uses: a true result that is unused is still knowledge, and since no proof of the root names it, it does not appear in the frontier and costs a session nothing." The reason for no survey: "What each element is, where it stands and what uses it are read from the Lean structure and the records, and the view that lists them is derived at every publication." `roles/organizer.md:49`

"An organization that finds nothing to join, rearrange or merge is a complete one." `roles/organizer.md:55`

### What it must prove in Lean

"When two definitions denote one object, state that they agree and prove it in Lean. When two statements have the same content, state that each holds exactly when the other does and prove it in Lean." `roles/organizer.md:23`

The proof of an equivalence must show sameness of content: "it passes from each to the other through the definitions and the agreements between them, and it does not call on a proof of either statement. An equivalence obtained from the fact that both statements are already proved says nothing about their content, although Lean accepts it." `roles/organizer.md:23`

"Every statement you add must have a proof that is complete in Lean and depends, through everything of the canon it uses, only on the allowed axioms. `commands.prepare` reports any statement you add for which this fails, and such a change is not published." `reference/organizer-output.md:40`

"An identity that you cannot prove in Lean you do not establish. Whether the two things agree is then a piece of mathematics that is not yet done, and it belongs to an attempt. Do not record it as an identity in a weaker form, and do not treat the two as one in anything else you do." `roles/organizer.md:27`

What Lean does not check remains the organizer's: "What Lean checks is the proof. What the statement of agreement says is still yours to get right." Two definitions may agree only on a range; the organizer states exactly the agreement it can prove. `roles/organizer.md:25`

Two statements shown to agree "remain two elements, and your element changes the standing of neither." Where the other statement has a formal proof the organizer can add the one-line derivation as a declaration of its own; where it has none, the derivation "enters through a peer's change and review like any other proof." `roles/organizer.md:29`

### What enters the library from an organizer without a review

"Nothing you submit goes through review. For the merging of questions the research relies on your judgment, as it always has. For everything in the change it relies on Lean: the runner publishes what compiles and passes the checks a machine can decide, and what you add enters as accepted. That is why an agreement you cannot prove in Lean is not yours to establish, and why a rearrangement may move a proof and may not change one." `reference/organizer-output.md:5`

Concretely, without review:

- **Elements stating that two definitions or two statements agree**, and derivations of a statement from another that agrees with it, each with a complete Lean proof from the allowed axioms. They enter as accepted: "Lean's check of the proof stands where the judgment of its correctness would stand, and the two considerations under which review holds a correct proof back are not asked of it." `roles/organizer.md:23`; `reference/change-format.md:285`
- **The records of those elements.** "No review reads this record, so give it the care a reviewer would ask for." `roles/organizer.md:23`
- **Rearranged modules and retired declarations**, under machine checks: no declaration disappears other than the retired alternatives; no statement and no kind of declaration changes in place; each retired alternative is gone and the statement's own declaration remains; the proof now under the statement's own name names the elements the alternative's proof named and is complete in Lean exactly if the alternative's proof was. "A retirement moves a proof and does not change it." `reference/organizer-output.md:57-62`. For a definition the text is compared as well: "A definition whose text you altered is refused, because every statement that mentions it would then mean something else while keeping its verdict. A proof that names other elements than before, or that became complete or incomplete, is refused, because no review judged that proof." `reference/organizer-output.md:64`
- **Question merges**, by the organizer's judgment; "the runner does not compare their wording." `reference/organizer-output.md:17`

What an organizer's change may not hold: "It proposes no questions and no resolutions, and it carries no approach entries and no understanding texts; the transport check refuses a change that does." `reference/organizer-output.md:34`

The runner publishes the organizer's output in its turn in the publication queue, applies the change to the canon as it is at that moment, builds it and repeats the machine checks. "If your change no longer applies or does not build, a replacement organizer receives your output and the reason and makes the change again." `reference/organizer-output.md:74`

---

# Part 2. `C:\math\README.md` lines 38 to 119 against the current system

Marks: `true` (still correct as written), `partly` (some of it is wrong), `false`, `gone` (it describes something that no longer exists). Blank lines and Mermaid syntax lines without a label are not listed. Where a line is marked `true` and part of it could not be checked in my sources, the note says so.

| Line | Item | Mark | What is wrong, and the current fact |
|---|---|---|---|
| 38 | heading "Six roles and the pipeline" | true | Six roles: `runtime/settings.py:10`. Pipeline: `reference/common.md:125`. |
| 40 | paragraph on the six roles | partly | "an attempt tries to settle a node": there are no nodes; an attempt chooses among the work that remains and takes on a section of a statement (`reference/common.md:19`, `:251`). "a peer develops it into a record candidate": the peer takes the line of work over and writes a candidate change to the canon (`reference/common.md:117-119`). "keeps the knowledge base navigable": the organizer "keeps the canon usable as one body" (`reference/common.md:184`). The division into three producing roles, two processing roles and the organizer, and the definition of a pipeline, still hold (`reference/common.md:182`, `:125`). |
| 42-43 | table header | true | |
| 44 | attempt row | partly | Receives the starting context (root in words and in Lean, frontier with questions, understanding of `q0`, board, user conditions) and reads the canon by traversal (`reference/common.md:243`, `:295`). It chooses a section, which may be a statement of its own, not "a node" (`reference/common.md:211`). It leaves retained work that includes Lean files (`reference/retained-work.md:3`, `:42`). |
| 45 | explorer row | partly | The explorer may be assigned `q0` by the runner at launch and chooses only when the assignment names no question (`roles/explore.md:11-13`; `runtime/runner.py:285-303`). "retained work on that question" holds, with Lean definitions and statements (`roles/explore.md:72`, `:78`). |
| 46 | formalizer row | partly | It receives one element: a settled statement the root (or a settled refutation of the root) rests on, with no formal proof yet, whose proof names only statements that already have formal proofs (`reference/common.md:172`; `runtime/knowledge.py:443-469`). "whose outcome can reach the root" belongs to the vocabulary of relations, which is gone. It leaves `output/replace/` and `output/lean/` with the compile and axiom output (`roles/formalizer.md:57`). |
| 47 | peer row | partly | "One producing session's complete retained work" holds (`roles/peer.md:19`). It leaves a candidate change: new Lean modules, replaced proofs, records, approach entries, an understanding text, proposed questions and resolutions (`reference/change-format.md:9-15`, `:23-34`). "exposition, claims and proposals" is gone. |
| 48 | review row | partly | It receives the frozen candidate, the producing session's directory and the peer's retained work (`roles/review.md:51`). It leaves feedback and `assessment.json` with one verdict per element (`correct`, `accepted`, `replaces`, `reason`), a publication decision, the contribution, verdicts on proposed questions and resolutions, concerns and findings (`reference/review-output.md:11-40`). "claim statuses" is gone. |
| 49 | organizer row | gone | It receives a batch of published changes no earlier organizer has answered for (`roles/organizer.md:5`). It leaves `organization.json` and optionally a change: elements proving in Lean that two definitions or two statements agree, modules rearranged so that a proof stands under its statement, and question merges (`reference/organizer-output.md:3`). It writes no survey, sorts no elements into groups, keeps no list of shared terms and merges no statements (`roles/organizer.md:49`, `:29`). |
| 51 | paragraph introducing the diagram | partly | "the knowledge base and the record": publication changes the canon; there is no record object in this sense (`reference/common.md:125`). "no two sessions ever converse": sessions can send coordination messages to one another's inbox (`runtime/coordination.py:586-600`; `roles/attempt.md:31`; `reference/common.md:265`), though unfinished mathematics is not to be shared that way (`reference/common.md:291`). "Every box ... is a session, started by the runner" holds for the six roles; the review's three sub-reviewers are delegated agents inside the review session and do not appear (`roles/review.md:39`). |
| 55 | label "knowledge base: frontier, index, board, records" | partly | What is read is the canon (Lean library and records) with the frontier, the questions and the board (`reference/common.md:101`, `:243`). An index of the kind the README describes is not a view delivered to sessions; a derived index of the whole canon exists and is not delivered (`reference/common.md:241`). |
| 56 | label "producing session: attempt, explorer or formalizer" | true | `runtime/settings.py:11`. |
| 57 | label "peer" | true | |
| 58 | label "review" | true | |
| 59 | label "record with its assessment" | gone | Publication applies the candidate to the canon, compiles the library, extracts the structural index and commits (`reference/common.md:125`). Review's verdict and reason are shown in the view of each element (`reference/review-output.md:72`). |
| 60 | label "organizer" | true | |
| 61 | edge label, knowledge base to producing session | partly | "an attempt or explorer chooses its own work" holds, except that the runner assigns `q0` to an explorer when it is free (`reference/common.md:269`). "a formalizer receives an accepted proof or refutation that can reach the root": it receives a settled statement the root rests on whose named statements are all formal (`reference/common.md:172`). |
| 62 | edge label "retained work", producer to peer | true | `runtime/runner.py:483-486`. |
| 63 | edge label "retained work", producer to review | true | `task.source` is the producing session's directory (`roles/review.md:51`; `runtime/runner.py:528-531`). The review also receives the peer's retained work (`task.peer`), which the diagram does not show. |
| 64 | edge label "record candidate" | partly | The thing passed is the frozen candidate change (`reference/change-format.md:279`). |
| 65 | edge label "publish, with claim statuses" | partly | Publication is with a verdict for each element, not claim statuses (`reference/review-output.md:44-72`). |
| 66 | edge, record to knowledge base | gone | See line 59. |
| 67 | edge label "records not yet organized" | partly | The batch is the published changes no earlier organizer has answered for (`roles/organizer.md:5`). |
| 68 | edge label "modules, shared context, glossary" | gone | The organizer's output is agreement elements, rearranged modules and question merges, published without review (`reference/organizer-output.md:3-5`). |
| 71 | paragraph defining retained work | partly | The listed contents still hold in substance (`reference/retained-work.md:9-24`; `roles/peer.md:19`). Missing: the report at `output/report.md` as entry point, the Lean files under `output/lean/` and `output/replace/`, and the separation of `work/` from `output/` (`reference/retained-work.md:9`, `:24`, `:42`). "the contents of its own directory when it ends" is not a sentence of the sources; they describe retained work as "material and not a finished product" made usable by a report and Lean files (`reference/retained-work.md:3`). |
| 73 | heading "The choice of work: frontier, sections and leases" | true | All three terms exist (`reference/common.md:188`, `:251`, `:259`). |
| 75 | paragraph on the three views | partly | "handed no node and no task": no task holds (`reference/common.md:19`); "node" is gone. The frontier now is the computed view of what the root rests on, each statement with its standing and its proofs (`reference/common.md:188`), followed by the questions (`reference/common.md:219`). The index described (shared context, modules of records, recent records) is gone; the starting context holds the root, the frontier with the questions, the understanding so far of `q0`, the board and the user conditions (`reference/common.md:243`). The board still shows work underway (`reference/common.md:257`). A section is "an exact part of what the statement asserts", up to the whole, or a statement of the attempt's own aimed at an element (`reference/common.md:251`; `roles/attempt.md:27`). |
| 77 | paragraph on the lease and on occupancy | partly | The mechanism holds with "element" or "statement" in place of "node": one session at a time, no time limit, ends on registration, release or the end of the session (`reference/common.md:259`; `reference/sections.md:23`, `:36`; `runtime/coordination.py:157-173`). Occupancy until publication or review's decision that there is nothing to publish, and its reason, hold (`reference/common.md:261`). "until the resulting record is published": until publication. Not said: the lease has a queue, and a registered section cannot be withdrawn (`reference/sections.md:34`, `:57`). The role guide places the reading and the forming of the section before the lease (`roles/attempt.md:27`). |
| 79 | paragraph on information and enforcement | partly | The principle holds (`reference/common.md:265`). The three refusals named are the ones the guide names at `reference/sections.md:25`, but the commands refuse more: a registration without the lease, a definition, a statement that is settled, contested or refuted, a whole element another pipeline holds, and a whole element the session's own pipeline already holds (`reference/sections.md:33-35`; `runtime/coordination.py:358-374`). "a whole node while another session holds part of it": a whole element while another pipeline holds a section. The last sentence, on overlap as a mathematical judgment with a recorded reason, holds (`reference/sections.md:25`). |
| 81 | heading "The end of a session" | true | |
| 83 | paragraph on the session host | partly | Holds: no time cap (`roles/attempt.md:91`); the host and its purpose (`reference/retained-work.md:59`, `:78`); the default of three (`runtime/settings.py:38`); the two ways the turns end (`reference/retained-work.md:72-74`). Wrong or incomplete: "each time a CLI process exits it resumes": not after a cancellation, a refusal or a failed exit, which end the session as interrupted, and not after a valid no-research outcome (`runtime/ending.py:192-209`). "explorers that have begun research, that is, that have taken a question and started on it": the sources do not tie research to having taken a question; research can begin before a question is taken, and such work goes to a peer "whether or not it holds a question" (`resume/explore.md:1`; `reference/retained-work.md:92`). "reviews and organizers are not asked to reconsider": they are not asked for an end decision, but their host resumes the same conversation, up to the same maximum, while their output does not pass the transport check (`runtime/ending.py:19-23`, `:219-227`; `reference/tools.md:57`). |
| 85 | paragraph on interruption | partly | An interrupted producing session's retained work goes to a peer (`reference/common.md:305`; `runtime/runner.py:470-488`). The test in code is whether the session left any material, not whether it "had begun research"; a session that left none is retried (`runtime/runner.py:470-478`). Ending without a peer or a review requires the session to declare `no_research` after a successful, uninterrupted exit, and only attempts and explorers can (`reference/retained-work.md:84-92`; `runtime/availability.py:50-73`; `runtime/runner.py:459-469`). So "treated the same" does not hold for the no-research path. The last sentence, on a replaced peer, review or organizer receiving the partial work, holds (`reference/tools.md:57`; `runtime/runner.py:396-402`). |
| 87 | heading "Peer, review and the published record" | partly | "the published record" is gone; publication changes the canon. |
| 89 | paragraph on the peer | partly | Holds: receives the complete retained work including the conversation; is asked to work the mathematics itself and to complete what was unfinished (`roles/peer.md:3`, `:19`, `:29`); says what the producer established and what it added (`roles/peer.md:89`). Gone: "record candidate: an exposition ... together with a structured list of the claims"; "what the record proposes for the frontier and the glossary: new nodes, relations, proofs of nodes, questions and terms". Current: the candidate change of topic 7; the peer proposes questions and resolutions, and nobody admits a statement to the frontier (`reference/common.md:211`). |
| 91 | paragraph on the review | partly | Holds: receives the candidate and the producer's retained work and compares in both directions (`roles/review.md:51-53`); decides publication (`roles/review.md:89`); reports a gap and does not write the proof and certify it (`roles/review.md:27-29`). Gone: the three claim statuses, and "a proposed node, relation or proof is accepted only when the claim it rests on is supported". Current: per element `correct` (`confirmed`, `not_confirmed`, `undetermined`, `not_applicable`), `accepted`, `replaces` and `reason` (`reference/review-output.md:48-72`); verdicts `admitted`, `declined` or `revise` on proposed questions (`reference/review-output.md:90`). Absent: the three sub-reviewers (`roles/review.md:35`) and the review's own compile (`roles/review.md:145`). |
| 93 | paragraph on default models | true | `runtime/settings.py:12-17`, `:34`; fallback in order at `runtime/runner.py:256-263`. The code comment adds that "by default a candidate's review comes from the same model as the peer that wrote it" (`runtime/settings.py:14-15`). The organizer uses the producers' list (`runtime/settings.py:90`). |
| 95 | paragraph on the published record and findings | gone | No record of exposition, evidence, description and terminology is published. "The record never changes afterwards": the invariant now is that "the statement of an element is never changed in place"; a record or a proof can be replaced, and the difference is kept in the history (`reference/common.md:111`, `:127`). A finding attaches to elements and can withdraw or restore the confirmation of a proof or reopen a question (`reference/review-output.md:120-126`). The frontier is computed from the canon (`reference/common.md:188`); there is no index of shared context and no glossary (`reference/common.md:109`, `:241`). "no session writes a separate account of the current state" needs a qualification: the understanding so far of `q0`, written by the peers of the explorers that hold `q0`, is the account of the problem as a whole (`reference/common.md:225`). |
| 97 | heading "Relations, propagation and how nodes stand to the root" | gone | |
| 99 | paragraph on relations and propagation | gone | No relations and no propagation by propositional logic were found in the files read. Current: a proof names in Lean the statements it rests on, and "A proof is **settled** when it is accepted and every statement of the canon that it names is settled" (`reference/common.md:105`, `:166`). A statement is refuted only when a settled proof establishes a statement that Lean has confirmed to be its exact negation (`reference/common.md:205`; `reference/change-format.md:98`). `contested` still exists, for a statement of which both it and its negation are settled; the lease is refused for it and a comprehensive review locates the failure (`reference/common.md:209`; `runtime/coordination.py:209-211`; `roles/review.md:165`). |
| 101 | paragraph on routes and necessary conditions | gone | No "route" and no "necessary condition" were found in the files read. The frontier shows what some proof of the root reaches (`reference/common.md:207`). The current launch condition of a formalizer is in topic 4. |
| 103 | heading "Questions and progress" | true | |
| 105 | paragraph on questions | partly | "Beside its nodes, the frontier keeps questions": the frontier view lists the questions after the frontier (`reference/common.md:219`). The examples, question 0 as the root problem as a whole, and the path through a peer and a review hold (`reference/common.md:219-221`, `:182`). "without any predetermined theorem to produce" holds (`reference/common.md:180`). |
| 107 | paragraph on how questions enter and are resolved | partly | "the way nodes do": statements are not admitted by anyone (`reference/common.md:211`); questions are proposed in a peer's candidate and admitted by review (`reference/common.md:227`). The operator sentence holds (`reference/common.md:227`; `runtime/runner.py:1584`). Resolution: "when review judges that its understanding so far answers what its statement asks" (`reference/common.md:229`), not "a published record gives an account". Absent: organizer merges as a third origin; `q0` is resolved only by the root's formal settlement (`reference/common.md:231`); a finding can reopen a question (`reference/review-output.md:126`). |
| 109 | paragraph on progress | true | `reference/common.md:27-29` ("These are examples rather than a list"). The description now stands in the common introduction, under "What moves the research forward", and the role guides refer to it (`roles/attempt.md:43`; `roles/review.md:79`). "the runner applies no such filter itself" is `[inferred]`: nothing of the kind was seen in the parts of `runtime/runner.py` read. |
| 111 | heading "Two documents on research and writing" | true | |
| 113 | paragraph on the two documents | true | The five roles: `runtime/context.py:14-25`; `reference/common.md:35`. Authorship of the essay: `reference/what-research-is-for.md:7` ("one of us is the user who started the investigation and followed it every day, and the other is the operator who kept it running"). The second document: `reference/user-writing-preferences.md:5`. Not checked in my sources: the statement about the first run and 8 November, and that the essay draws its examples from the history of mathematics (I read only the opening of each document). |
| 115 | heading "Formalizers, organizers, the runner and the broker" | true | |
| 117 | paragraph on the formalizer and the organizer | partly | Formalizer: "a node whose informal proof or refutation the review has accepted" is now a settled statement the root rests on, whose proof names only formal statements (`reference/common.md:172`); filling gaps, changing strategy, the fixed statement, the path through peer and review, and the absence of a cap on continuations hold (`roles/formalizer.md:5`, `:59`). Absent: the written proof in the record must become the argument that was formalized (`roles/formalizer.md:39-41`). Organizer: the whole sentence is gone; see line 49. In particular it does not merge statements: "Two statements shown to agree remain two elements" (`roles/organizer.md:29`). |
| 119 | paragraph on the runner and the broker | true | Order: `runtime/runner.py:41`. Eight sessions and three minutes: `runtime/settings.py:32-33`; one spacing for attempts and explorations at `runtime/runner.py:1246-1250`. Authentication and inheritance: `SKILL.md:42`; `reference/common.md:303`. Starting context saved at launch: `runtime/context.py:60-66`, `:136`. Broker per instance, memory and thread budgets: `reference/lean-broker.md:20`, `:25`, `:63` (read by search only); results preserved: `reference/common.md:301`. Absent: an exploration is requested at every attempt launch by default (`runtime/settings.py:32`; `runtime/runner.py:334-338`), and comprehensive reviews and organizers run one at a time (`runtime/runner.py:1252-1261`). |

---

# Part 3. What exists in this area and is absent from README lines 38 to 119

Each item is something a reader who wants to evaluate or run the system would need. The order follows the life of a piece of work.

**Mathematics is stated in Lean from the start, by every producing role and by the peer.**
- Sessions state definitions and statements in Lean as they work; only what has a Lean statement is kept as a result. `reference/common.md:83-85`; `roles/attempt.md:53-55`; `roles/explore.md:72`
- A proof may be written in words in the record while its Lean proof names what it rests on and ends in `sorry`; a complete Lean proof is optional for attempts and peers. `reference/common.md:95`, `:105`; `roles/attempt.md:59-61`
- The retained work therefore includes Lean files under `output/lean/` and `output/replace/`. `reference/retained-work.md:42`

**The choice of work.**
- The third kind of section: a statement of the attempt's own, registered on the element it is aimed at. `reference/common.md:211`, `:259`; `reference/sections.md:9`
- No one admits a statement to the frontier, and review's judgment of a division "admits nothing and blocks nothing". `reference/common.md:211`, `:213`
- The reading asked of every session before it takes on a statement, and the fact that nothing checks it. `reference/common.md:243`
- The user's standing condition against retreating into a nearby piece that can be finished. `reference/common.md:45-57`; `roles/attempt.md:15`
- A statement whose proof is correct and held back is ordinary work that remains. `reference/common.md:164`; `roles/attempt.md:19`
- A section cannot be withdrawn; a lease has a queue; a session stands in one lease relation at a time; peers register sections as well. `reference/sections.md:3`, `:34`, `:57`
- Holding a section is what permits a pipeline's candidate to replace the proof of that statement. `reference/common.md:263`
- Coordination messages between sessions. `runtime/coordination.py:586-600`; `reference/common.md:265`

**Questions and exploration.**
- The question lease, the four question commands, and the rule that `q0` is taken before any narrower question. `roles/explore.md:21-26`; `reference/common.md:269`
- The runner assigns `q0` at launch, and launches another explorer only while free questions outnumber the explorers still choosing. `runtime/runner.py:285-303`; `runtime/coordination.py:126-130`
- A question's occupation lasts through peer and review and cannot be given back. `reference/common.md:271`; `roles/explore.md:17`
- The understanding so far of a question, and that of `q0` as the account of the whole problem delivered to every session. `reference/common.md:223-225`
- The approaches tried on a statement, the other piece of written state, with review's assessment beneath each entry. `reference/common.md:135`
- Review's three verdicts on a proposed question, `admitted`, `declined` and `revise`, and the list of proposals not admitted. `reference/review-output.md:90`; `reference/common.md:227`
- A resolution is proposed by a peer with the text that settles the question; what remains does not keep the question open. `reference/common.md:229`

**The peer.**
- The candidate change and its parts. `reference/change-format.md:9-34`
- What a candidate cannot do, and the invariant that a statement is never changed in place, with its reason. `reference/change-format.md:17`; `reference/common.md:127`
- `commands.prepare`: the candidate is applied to a copy of the canon and compiled before the peer ends. `reference/change-format.md:126-144`
- The candidate is frozen when the peer's session ends; at publication it is built again on the canon as it then is, and a replacement peer makes a new candidate when it no longer applies. `reference/change-format.md:279-281`; `reference/common.md:129`

**The review.**
- Three independent sub-reviewers before the reviewer's own judgment, and why. `roles/review.md:35-47`
- Two separate judgments of a proof, correct and accepted, and the four standings. `reference/common.md:145-156`
- The two considerations under which a correct proof is held back, their reasons, their limits and the two settings that turn them off. `roles/review.md:107-141`; `runtime/settings.py:39-41`
- Settled against formal. `reference/common.md:166`, `:170`
- The `replaces` judgment and what happens to a declined replacement. `reference/review-output.md:63-68`
- The judgment of whether the Lean statement says what was meant, which no later step repeats. `roles/review.md:57`
- The review's own compile with `commands.verify`, the reading of the axioms and the `formal_check` field. `roles/review.md:145-151`; `reference/review-output.md:94-108`
- "Review is a judgment and not a gate": imperfect work is published with its verdicts and nothing is returned for repair. `reference/common.md:123`
- The contribution text and where the runner places it. `reference/review-output.md:86`
- Concerns, findings with `invalidates`, `validates` and `reopens`, comprehensive reviews, and conflicts on a contested statement. `reference/review-output.md:116-138`; `roles/review.md:153-165`

**The formalizer.**
- The exact launch condition, and that a proof whose Lean text is complete can still be assigned. `reference/common.md:172`; `runtime/knowledge.py:443-469`
- The runner records a whole-element section for the formalizer's pipeline. `roles/formalizer.md:17`; `runtime/runner.py:320-328`
- The written proof and the Lean proof are to be one argument, because the paper is produced from the written proofs. `roles/formalizer.md:39-41`
- The formalizer does not receive the two research documents. `runtime/context.py:21`

**The organizer.**
- Nothing it submits goes through review; what it adds must have a complete Lean proof from the allowed axioms and enters as accepted. `reference/organizer-output.md:5`, `:40`
- It joins by adding an element stating agreement and never by renaming or removing. `roles/organizer.md:11`
- Rearrangement and retirement under machine checks. `reference/organizer-output.md:44-64`
- It is launched after four published changes by default, and its batch is fixed at launch. `reference/organizer-output.md:15`

**The end of a session.**
- The end decision file, its four fields, and the rule that a decision counts only as the answer to a request. `reference/retained-work.md:61-72`
- What the reconsideration turn asks. `resume/common.md:5-9`
- Reviews and organizers are resumed while their output does not pass the transport check. `runtime/ending.py:19-23`; `resume/output.md:3-9`
- A turn that ended at the output-token limit is resumed. `runtime/ending.py:193-195`
- Dispatch stop holds new resumption turns. `reference/retained-work.md:80`
- On Windows every process a session started ends with the session. `reference/retained-work.md:78`
- The `no_research` outcome, what counts as research, and the availability report that makes the runner wait before launching further attempts. `reference/retained-work.md:84-112`
- The transport check that every session runs before ending, and what it requires of each role. `reference/common.md:301`; `reference/tools.md:55`
- After the root is formally settled the runner stops launching attempts and explorations. `reference/common.md:309`
- A session may delegate to sub-agents; a Codex session cannot. `reference/tools.md:51`
- Everything inside an instance is written in English. `reference/common.md:297`

---

# Part 4. What I could not establish

## Questions of Part 1 that the sources do not answer, or answer only in part

1. **A definition of "retained work".** No source gives a defining sentence. `reference/retained-work.md:3` describes what a producing session leaves and what makes it usable. The README's sentence "the contents of its own directory when it ends" is consistent with `runtime/runner.py:483` (the peer's `source` is the session directory) but is not a statement of the guides.
2. **What the board file looks like.** `reference/common.md:257` describes its entries and `runtime/coordination.py:93-120` computes its rows; I did not read the rendering code in `runtime/knowledge.py`.
3. **How the operator requests a comprehensive review of named elements, and how the operator asks the runner to reconsider attempts.** I saw only the command names `review` and `reconsider-attempts` at `runtime/runner.py:1584` and the task field at `runtime/runner.py:1405`. `reference/operations.md` was not in my list and I searched it for two words only.
4. **Whether anything stops a session from ignoring another session's section in its mathematics.** The guides say the tools do not (`reference/common.md:265`). The one enforced consequence I found is the transport check's refusal of a replacement whose pipeline holds no section on the statement (`reference/change-format.md:144`). I did not read `runtime/check.py` beyond lines 380-434.
5. **The first-run history in README line 113** (the standing input from 8 November) is not in any file I read.

## Files not read in full

Read in full, beyond the listed sources: `reference/common.md`, `runtime/context.py`, `runtime/settings.py`. Opened because the role guides refer to "the common introduction" on almost every point, because the question "what a session receives" is answered only in `context.py`, and because the defaults are in `settings.py`.

Read in part:

- `runtime/runner.py`: lines 1-90, 198-625, 901-1056 and 1137-1376. Opened for the launch of formalizers and organizers, the collection of ended sessions, and the scheduling order.
- `runtime/knowledge.py`: lines 340-499, and single lines found by search (14-20, 217-218, 235-238). Opened for the launch condition of a formalizer, the standings and the resolution of `q0`.
- `runtime/check.py`: lines 380-434. Opened for what the transport check requires of each role.
- `runtime/runtime_support.py`: lines 388-482. Opened for the session host.
- `reference/tools.md`: lines 47-57. Opened for delegation and the transport check.
- `reference/lean-broker.md`, `reference/operations.md`, `SKILL.md`: searched for a few words only, for README line 119.
- `reference/what-research-is-for.md`, `reference/user-writing-preferences.md`: opening paragraphs only, for README line 113.

Not opened: `reference/canon.md`, `reference/records.md`, `reference/lean.md`, `reference/literature.md`, `reference/writing.md`, `reference/evidence.md`, `reference/paper-method.md`, and the remaining runtime modules. Where Part 1 mentions something those files define (for example the criteria for the weight of an element), it cites the place in the files I read that points to them.

Not used, as instructed: `C:\math\.agents\skills\do-math` and `C:\math\docs\do-math\rebuild-design.md`.

## Places where two sources say different things

I report both sides and do not choose.

1. **When occupancy ends.** The docstrings in `runtime/coordination.py` say sections and questions "last until that session's pipeline finishes review" (`:6-7`) and "A pipeline's occupancy ends with its review" (`:94`). The guide says a section "remains occupied until publication makes the work available, or review completes a decision that there is nothing to publish" (`reference/common.md:261`). The code that the board reads sets the pipeline's stage to `done` when the publication is committed (`runtime/runner.py:1005-1008`), which comes after the review has ended and the publication has waited its turn in the queue (`runtime/runner.py:548-551`).
2. **Which sessions receive a continuation turn.** The guide says "For an attempt or explorer that undertook research, a formalizer or a peer" (`reference/retained-work.md:59`). The host does not test whether research was undertaken; it resumes an attempt or explorer unless the session wrote a valid `no_research` outcome (`runtime/ending.py:203-209`). An attempt that did no research and wrote no outcome file is therefore resumed as well. `[inferred]` from the code.
3. **What the registration command refuses.** `reference/sections.md:25` names three things ("an identical statement, any conflict with a section that covers the whole element, and missing reasons"). `reference/sections.md:35` and the code add a statement that has become settled, contested or refuted. The code also refuses a registration without the lease and a whole-element registration when the session's own pipeline already holds the whole (`runtime/coordination.py:358-359`, `:367-368`); the second is mentioned at `reference/sections.md:31` and the first is implied by "registers a section while you hold the lease" (`reference/sections.md:35`). The identical-statement test in code also applies to a section of the session's own pipeline (`runtime/coordination.py:369-371`), which the guide does not say.
4. **Whether the runner decides that work remains for an attempt.** The guide says "The runner does not compute whether work remains for an attempt." (`reference/common.md:215`). The code withholds the launch of an attempt when every element of the work that remains is held whole or has a session waiting for its lease (`runtime/runner.py:1231-1244`); its docstring begins "The runner does not judge whether mathematical work remains; it only refrains from launching an attempt when every element the frontier shows as remaining is held whole or already has a session waiting for its lease".
5. **The launch condition of a formalizer.** The guide's sentence (`reference/common.md:172`) does not mention contested statements; the code skips a contested statement (`runtime/knowledge.py:460`).
6. **The definition of a section.** `reference/common.md:251` defines a section as "an exact part of what the statement asserts"; `roles/attempt.md:27` and `runtime/coordination.py:3-5` include a statement of the session's own aimed at the element. `reference/common.md:259` reconciles them by calling such a registration "a section on that element like any other".

## A limit of this digest's own preparation

The project's writing procedure asks for a separate reading of a new document against a recorded agreement. I did not run it, because it writes further files and my assignment allowed one output file. This digest was checked by its author only: each quotation was copied from the tool output of the file read, and each line number was taken from the same output.
