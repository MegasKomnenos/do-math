# Tools and working files

Your role guide explains the mathematical work you own. This guide explains the files and commands supplied for that work. You have a directory in which to develop and retain your work, the canon of the instance and the views derived from it, commands that read the canon and prepare a change to it, commands for coordinating with other sessions, and a service that compiles Lean.

The runner records the concrete paths and commands in `input.json`. Its `instance` and `session` identify where you are working, `role` and `task` identify your assignment and the inputs specific to it, `settings` holds the settings in force at your launch, and `commands` gives the executable argument arrays. Read these values before invoking a command. The forms shown below explain what the commands do; your input supplies the actual executable locations and identifiers.

Each command is an argument array: pass its elements separately to the process, replacing a placeholder such as `<element>` or `<file>` with your value, and append further arguments after the last element of the array. This avoids guessing executable locations or relying on a shell alias.

## Files you work with

**Your session directory.** Use `work/` for scratch mathematics, Lean files under development, computations and intermediate artifacts. Use `output/` for the retained report or role output your successor will read. Keep the files and any generated caches in your own session directory. The runner preserves `pack.md`, which is your starting context, `input.json`, the copies of the guides under `context/`, and the available CLI conversation. `inbox/` receives messages for you. Your role's guides state the entry file and fields of your output.

**The canon.** `canon/` under the instance holds the knowledge of the research: the Lean library and the written files beside it. [The canon](canon.md) shows where its folders and files are and gives the form of each written file.

You read the canon and never write in it. A change to it is a candidate that a peer or an organizer assembles in its own `output/`, and publication is the runner's work. The commands under Reading the canon below are the way to read it, because a view joins what Lean knows of an element with what its record says and a traversal returns the whole of what its rule selects. The files are there for the cases where you need the source itself: to read or change the body of a Lean proof, or to see more of a declaration than its printed statement.

**The derived views.** `knowledge/` under the instance holds views the runner renders and the published judgments. `frontier.md` is the frontier with the questions, `index.md` the self-descriptions of all elements in the order of the Lean structure, `board.md` the work underway, and `state.json` the same state in structured form. `changes/<id>/` holds one published change with review's assessment and feedback, `reviews/<id>/` a comprehensive review, `organizations/<id>/` an organizer's output, and `questions/<id>/` questions the operator placed. Read these and follow them to the canon; write your contributions in your own output.

Read required documents in full. If a file-reading tool truncates its output, retrieve the omitted ranges before treating the document as read. A successful read command can still have returned only part of the file.

Working paths can be absolute when invoking tools. What a later reader needs has to be in the canon: state the mathematics as elements, publish the files a record relies on as its evidence, or cite a stable published source. A reference to a producer's private working file cannot support an ordinary session, which may read only what is published.

## Reading the canon

`commands.canon` reads the canon. Replace `<command>` with one of the reading commands that [The canon](canon.md) lists under "Reading the canon: the commands" and append its arguments after the array; that guide also describes what each view shows and how to move through the canon with them. No reading command starts Lean; they read the structural index and the records, so they answer at once and cost no memory. The same array has one further command, `checkout <folder>`, which copies the library, `canon/lean`, into a new or empty folder inside your session directory, so that you can build your own Lean files against it.

An element is named by its declaration name as the canon shows it, for example `Parking.Columns.dq_col`. The reading commands print text. A command that cannot answer, for instance because no element has that name, prints `{"error": "..."}` and exits with code 1.

The canon changes while you work, as other sessions' changes are published. A notice arrives in your inbox at each publication, and running a reading command again returns the current state. A copy made with `checkout` does not follow those changes. The command prints, as JSON, the folder and the revision of the canon it copied; note the revision if you will need it, since nothing in the folder records it. A later checkout into another folder gives the current library.

## Preparing and verifying a change

Two commands build a change on the canon. They are for the roles that write or judge one, and each refuses the other roles.

`commands.prepare` is for a peer and for an organizer that submits a change. It applies the candidate in your `output/` to a copy of the current canon, builds the copy through the broker, extracts the structural index of what changed, and checks what a machine can decide. It writes the result to `output/prepared.json` and prints a summary: `ok`, the build ID, the elements `added`, the proofs `replaced`, the `records`, the `errors`, and the axioms each added or replaced statement depends on. Exit code 0 means the candidate is in order as far as a machine can tell, 1 means errors that `errors` lists, and 124 means the build is still running. After 124, run the same command again; it continues with the same build and starts another only when the candidate or the canon has changed. `--timeout <seconds>` sets how long one call waits, 50 by default, and `--expect-mb <MiB>` your estimate of the peak private memory of one module compile, which [Lean](lean.md) explains.

The result is bound to the exact files it saw. After any edit to the candidate, prepare it again; the transport check refuses a candidate whose files differ from those that were prepared, and one whose preparation reported errors. [A candidate change](change-format.md) describes the layout of a candidate and what the checks decide. The command judges no mathematics.

`commands.verify` is for the review of a candidate. It does the same on the frozen candidate, with one difference: the modules the candidate changes are compiled afresh by your session and are not taken from the cache. It writes the result to `work/verify/outcome.json` and prints the same summary, in which the axioms of each statement are what you compare with the allowed axioms in `settings` of your `input.json`. The build ID it reports is what [Review output](review-output.md) asks for under `formal_check`.

## Current research and coordination

The views in your starting context tell you what the research held when you launched. To see what has changed since, use the reading commands above for the canon and `commands.updates` for the work underway.

`commands.updates` returns the current revision and the state of the root; the live board, with each pipeline's sections and the question each exploration holds; the element and question leases; the current questions with their state and holder; the concerns; the comprehensive review assignments; and the messages in your inbox. The user inputs it returns are your original launch snapshot. New user standing instructions apply to sessions launched afterward. Publications, sections, questions and leases remain live.

### Sections and element leases

Attempts and peers register sections with four commands. Replace `<element>` with the declaration name and `<file>` with a file path. Sections and leases attach to the statement: when a statement has several proofs, each under a declaration of its own, all of them are held under the declaration that carries the statement itself. If you name a declaration that is another proof of a statement, the commands act on the statement's own declaration, and their responses name it.

The commands count sections by pipeline: the sections registered by the producing session whose work a peer takes over, and by any earlier peer it replaces, are the peer's own. Where the descriptions below speak of sections, or a whole element, that another session holds, they mean those of another pipeline. Your own pipeline's sections need no reasons, and they do not prevent you from registering the whole element unless your pipeline already holds it whole.

1. `commands.lease` takes the element's lease if no other session holds it. A refusal exits with code 1, records nothing and returns the reason, the current holder, the waiting sessions and the element's sections. The lease is also refused for a definition, for a statement that is settled, contested or refuted, and while another session holds the whole element.
2. `commands.wait` joins the element's queue and returns with exit code 0 once the lease is yours. When its timeout passes first, it exits with code 124 and reports your place; the place is kept, so run the command again to keep waiting. It refuses with exit code 1, giving up your place on the element, when the element is a definition, when the statement is settled, contested or refuted, or when another session holds the whole element, whether that is already so when you start waiting or happens while you wait; the response says which. A session stands in one lease relation at a time: taking or waiting for another element gives up its place here.
3. `commands.section` registers a section while you hold the lease, and registering ends the lease. The file is JSON in one of the three forms below. Give a reason for every section other sessions hold on the element; the lease response lists them with their IDs. The tool refuses an identical statement, a whole-element registration while other sessions hold sections, and missing reasons. A refusal records nothing and keeps your lease, so you can correct the request. It also refuses a statement that has become settled, contested or refuted, or that another session now holds whole, when that changed while you held the lease; the response says which, and the remedy is then to release the lease rather than correct the request.
4. `commands.release` gives up the lease, or your place in the queue, without registering. Use it as soon as you decide not to take a section on that element. A lease has no time limit: until you register, release or end your session, everyone waiting for the element waits for you.

A section request takes one of three forms:

```json
{"whole": true}
```

```json
{"statement": "<the exact part of what the element asserts that you take on>",
 "reasons": {"<section ID>": "<why your section does not overlap it>"}}
```

```json
{"new": {"lean": "<a Lean statement that is not yet in the canon>",
         "statement": "<the same statement in words>"},
 "reasons": {"<section ID>": "<why your section does not overlap it>"}}
```

The first takes the whole of the statement. The second takes an exact part of it. The third registers a statement you have formulated yourself, on the element it is aimed at; other sessions then see on the board that someone is pursuing that statement, which a division of one statement into parts cannot show. `reasons` is needed only when other sessions hold sections on the element. Whether differently worded sections overlap is your judgment, recorded with your reasons; the tool refuses only what a machine can decide.

A registered section cannot be withdrawn, so register it once you have decided to pursue it. It stays occupied through peer and review, until the work is published or review decides that there is nothing to publish, because until then no other session can read that work. To take on a further section, take the lease again; your own earlier sections need no reasons. The section governs what you take on; it does not restrict the files, lemmas or elements your mathematics may use. A candidate that replaces the proof of an element is accepted by the transport check only when its pipeline holds a section on that statement.

A formalizer uses none of these commands: the runner has recorded its assigned element as a whole section before the session starts.

### Questions

Explorers occupy questions with four commands of the same shape. Replace `<question>` with the question ID from the frontier. If your assignment already names a question, the runner has recorded your occupation of it and none of these commands is needed.

1. `commands.question_lease` takes the question's lease if no other session holds it. A refusal exits with code 1, records nothing and returns the holder, the waiting sessions and, under `occupied_by`, the explorations that occupy the question: none, one, or both of the explorations that held two questions an organizer has since merged. The lease is also refused when the question is resolved or another exploration holds it, and for any question other than `q0` while `q0` is free: open, held by no exploration, and under no other session's lease or queue. Once the root is formally proved or refuted, `q0` is resolved; it is refused like any resolved question and no longer holds back a narrower one.
2. `commands.question_wait` joins the question's queue and returns with exit code 0 once the lease is yours, or with code 124 and your place when its timeout passes; the place is kept. It refuses with exit code 1, giving up your place, when the question is resolved, another exploration holds it, or it is a question other than `q0` while `q0` is free, whether that is already so when you start waiting or happens while you wait; the response says which.
3. `commands.question_take` occupies the whole question while you hold the lease, and taking it ends the lease. It refuses a question another exploration holds, a question other than `q0` while `q0` is free, a question that was resolved while you held the lease, or a second question for a session that already holds one. A refusal records nothing and keeps your lease. When the question was resolved or `q0` became free, the remedy is to lease the question you can take rather than to retry; a session stands in one question lease at a time, so leasing or waiting for another question gives up this one.
4. `commands.question_release` gives up the lease, or your place in the queue, without taking the question. Use it as soon as you decide not to take that question, including after `commands.question_take` refused it because you already hold one. A question lease has no time limit: until you take the question, release the lease or end your session, everyone waiting for the question waits for you, and the runner does not count the question as free when it decides whether to launch another explorer.

An occupied question cannot be given back; it stays with your pipeline through peer and review. The `questions` list that `commands.updates` returns shows, for each question, whether it is open or resolved, which explorations hold it (`occupied_by`, a list that is empty for an unoccupied question and names both explorations when an organizer has merged two questions they held), and whether it is free as the runner counts it: open, held by no exploration and under no session's lease. That flag does not set aside the rule above: while `q0` is free, a narrower question is listed as free and is still refused.

### Messages

To coordinate an unexpected overlap, write a short message file in your directory and run `commands.message` with the recipient's session ID and that file. If registered sections turn out to overlap, they stay as registered: agree by message which session pursues the shared part, and record the agreement in your report. Use coordination messages for coordination facts and pointers to published elements. Ordinary attempts do not obtain another session's unfinished mathematics through messages. Delivery creates a file in the recipient's inbox; it does not establish that the recipient has read it. The `messages` that `commands.updates` returns are the files in your own inbox. A coordination message carries the sender's session ID in `from` and its text in `text`. A notice the runner places there at each publication carries the publication's `event`, `kind` and `revision` instead of a sender; it tells you only that the canon has changed since you last read it.

### The availability snapshot

When an attempt runs `commands.updates`, the command saves, in the session's `availability/` directory, the elements of the work that remains together with the sections registered on each. These are the elements that `list --remaining` returns: the frontier's elements whose proof is not accepted, and those whose proof names a statement that has since been refuted. It returns an `availability_snapshot` token identifying that snapshot. The attempt can use the token in the availability report described in [Retained work](retained-work.md). The token identifies what the attempt inspected; the attempt still judges whether all the work that remains is occupied.

## Lean compilation

All Lean compilation goes through the instance's broker. It manages the memory and thread budgets shared by every session's compiles and retains each job's output and exit result. Read [Lean](lean.md) before your first compile, including its explanation of the memory estimate and of why compiles are batched at natural points of the work.

The `commands.lean` array gives the executable, the broker script and the instance. Replace `<command>` with `run`, `submit`, `build`, `wait`, `result`, `status`, `cancel` or `version`, adding the arguments that guide describes. Your own Lean files import modules of the canon, so they are compiled with `build` against a copy of the library: check the library out with `commands.canon checkout <folder>`, put your files under that folder as modules of the library, and give the folder as the module root. A waiting command that reaches its timeout returns exit code 124 while the job continues; follow the same job to its result. The outcome of a compile says whether Lean accepted the source as written. It does not replace examining whether the statement says what you mean.

`commands.prepare` and `commands.verify` build through the same broker, so their builds wait in the same queue and count against the same budgets as your other compiles.

## Other computations and literature tools

Use the CLI's available shell, file and search tools for the mathematics. For a long computation, write progress and final output to files in your session directory and retain its process or job identifier. When a shell tool stops waiting, recover the actual exit and output through its continuation mechanism. Starting a duplicate computation obscures which input produced which result.

End a computation you started by its process ID, and never by its name. A command that selects processes by image name, such as `taskkill /IM python.exe`, `Stop-Process -Name python`, `Get-Process python | Stop-Process` or `wmic process where "name='python.exe'" delete`, ends every process of that name on the machine. The runner, each session's host and the Lean broker all run as `python.exe`, and when a session's host ends, the system ends that session's CLI and everything the session started. Choosing another name, such as `lean.exe` or `claude.exe`, changes nothing, because other sessions run processes of the same names. In an earlier run a delegated agent, meaning to stop one script of its own, issued such a command and ended the runner together with all twelve sessions then running, its own among them. The process ID is the one you noted when you started the computation. If you did not note it, find the process whose command line contains your session directory and the script's name, and end that one.

The available external tools are the servers explicitly configured in this instance. The literature server scholarly-mcp is normally one of them. [Literature](literature.md) explains how to use it and which sources it offers to sessions. The server keeps what it retrieves in one store shared by every session on the machine, so an item that an earlier session retrieved can be read with `extract` from the reference that session recorded. If a tool or source is unavailable, record the limitation and use another available source where appropriate. The fact that the operator has a personal tool configuration does not make that tool part of your session.

## Delegating to sub-agents

A Claude session has the CLI's own tool for launching delegated agents; its general-purpose agent is available, and the agent's model and effort can be chosen when it is launched. A Codex session is launched with its multi-agent feature disabled, so it cannot delegate. A delegated agent runs as part of your session: it works in your session directory, its files belong to your retained work, and a Lean compile it submits carries your session ID at the broker, so it shares your session's memory and job accounting there. Its conversation is not retained separately; have it write what must be kept to files under `work/`. A delegated agent begins with nothing but what you hand it. It has not read the guides in your context or the user conditions of this instance, so your briefing has to carry whatever in them bears on the work you delegate: the conditions that govern the judgment you are asking for, that everything is written in English, the conventions of the canon if the agent will write Lean, and the paragraph above on ending processes if the agent may run computations. The review role guide specifies the one delegation that a role requires, the three independent sub-reviews; other roles may delegate when it serves their work, and remain responsible for everything a delegated agent produces.

## Checking and ending

Run the transport check, `commands.check`, against your own session directory before finishing. It prints `{"ok": true, "errors": []}` and exits with code 0 when the structure and references of your output passed. For an attempt, an exploration and a formalizer it checks only that `output/` contains no filesystem links and, for an outcome that reports no research, the conditions of that outcome; it does not read the report, so a passing check says nothing about whether the report is complete. A failure names what to fix: a field, a missing file, a candidate that was not prepared or was edited after it was prepared. The check stops at the first fault it meets, so run it again after each correction until it passes. The check does not prove mathematical statements or evaluate the quality of the exposition.

Producing sessions retain useful partial work even if interrupted before their final report is complete. Peers, reviewers and organizers need structurally usable outputs for the runner to apply their decisions. If one of those sessions is interrupted, the runner preserves its partial material and starts a fresh session for that stage. A missing output is an unfinished stage, not a mathematical rejection.
