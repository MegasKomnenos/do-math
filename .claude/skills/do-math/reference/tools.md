# Tools and working files

Your role guide explains the mathematical work you own. This guide explains how to use the files and commands supplied for that work. You have a directory in which to develop and retain your work, access to the instance's shared knowledge, and tools for coordinating with other sessions and compiling Lean.

The runner records the concrete paths and commands in `input.json`. Its `instance` and `session` identify where you are working, `task` identifies the inputs specific to your role, and `commands` gives the executable argument arrays. Read these values before invoking a command. The forms shown below explain what the commands do; your input supplies the actual executable locations and identifiers.

## Files you work with

Use `work/` for scratch mathematics, source development, computations and intermediate artifacts. Use `output/` for the retained report or role output your successor will read. Keep the files and any generated caches in your own session directory. The runner preserves `pack.md`, `input.json`, instruction references and the available CLI conversation. Your role's output reference states the entry file and fields it needs.

The instance's `knowledge/` holds published records, independent assessments and organization decisions. `frontier.md`, `glossary.md`, `index.md`, the module files under `index/`, and `board.md` are views the runner renders. Read them and follow their sources; write your contributions in your own output. Publication and changes to shared state are the runner's work.

Read required documents in full. If a file-reading tool truncates its output, retrieve the omitted ranges before treating the document as read. A successful read command can still have returned only part of the file.

Working paths can be absolute when invoking tools. Paths inside a published record are relative to that record, separated by `/`. Publish the evidence a later reader needs or link a stable published source. A reference to a producer's private working file cannot support an ordinary attempt that may read only published mathematics.

## Current research and coordination

The research snapshot in your starting context tells you what was available when you launched. To see what has changed, use the commands in your input. Each command is an argument array: pass its elements separately to the process, replacing placeholders. This avoids guessing executable locations or relying on a shell alias.

Run `commands.updates` from your input to obtain the live board with its sections and the question each exploration holds, the node and question leases, the current questions with their state and holder, current root state, concerns, comprehensive review assignments and coordination messages. The user inputs it returns are your original launch snapshot. New user standing instructions apply to sessions launched afterward. Research publications, sections, questions and leases remain live.

Attempts and peers register sections with four commands. Replace `<node>` with the node ID and `<file>` with a file path.

1. `commands.lease` takes the node's lease if no other session holds it. A refusal exits with code 1, records nothing and returns the current holder, the waiting sessions and the node's sections. The lease is also refused when another session holds the whole node or the node is no longer unresolved.
2. `commands.wait` joins the node's queue and returns with exit code 0 once the lease is yours. When its timeout passes first, it exits with code 124 and reports your place; the place is kept, so run the command again to keep waiting. It refuses with exit code 1, giving up your place on the node, when another session holds the whole node or the node is no longer unresolved, whether that is already so when you start waiting or happens while you wait; the response says which. A session stands in one lease relation at a time: taking or waiting for another node gives up its place here.
3. `commands.section` registers a section while you hold the lease, and registering ends the lease. The file is JSON: `{"statement": "<the exact part of the node you take on>", "reasons": {"<section ID>": "<why your section does not overlap it>"}}`, or `{"whole": true}` for the whole node. Give a reason for every section other sessions hold on the node; the lease response lists them with their IDs. The tool refuses an identical statement, a whole-node registration while other sessions hold sections, and missing reasons. A refusal records nothing and keeps your lease, so you can correct the request. It also refuses a node that is no longer unresolved, or that another session now holds whole, when that changed while you held the lease; the response says which, and the remedy is then to release the lease rather than correct the request.
4. `commands.release` gives up the lease, or your place in the queue, without registering. Use it as soon as you decide not to take a section on that node. A lease has no time limit: until you register, release or end your session, everyone waiting for the node waits for you.

A registered section cannot be withdrawn, so register it once you have decided to pursue it. To take on a further section, take the lease again; your own earlier sections need no reasons. The section governs which part of the node you take on; it does not restrict the files, lemmas or connections your mathematics may use.

Explorers occupy questions with four commands of the same shape. Replace `<question>` with the question ID from the frontier. If your assignment already names a question, the runner has recorded your occupation of it and none of these commands is needed.

1. `commands.question_lease` takes the question's lease if no other session holds it. A refusal exits with code 1, records nothing and returns the holder, the waiting sessions and, under `occupied_by`, the explorations that occupy the question: none, one, or both of the explorations that held two questions an organizer has since merged. The lease is also refused when the question is resolved or another exploration holds it, and for any question other than `q0` while `q0` is free: open, held by no exploration, and under no other session's lease or queue. Once the root is formally proved or refuted, `q0` is resolved; it is refused like any resolved question and no longer holds back a narrower one. An explorer that finds `q0` free takes it before any narrower question; lease and take `q0` instead.
2. `commands.question_wait` joins the question's queue and returns with exit code 0 once the lease is yours, or with code 124 and your place when its timeout passes; the place is kept. It refuses with exit code 1, giving up your place, when the question is resolved, another exploration holds it, or it is a question other than `q0` while `q0` is free, whether that is already so when you start waiting or happens while you wait; the response says which.
3. `commands.question_take` occupies the whole question while you hold the lease, and taking it ends the lease. It refuses a question another exploration holds, a question other than `q0` while `q0` is free, a question that was resolved while you held the lease, or a second question for a session that already holds one. A refusal records nothing and keeps your lease. When the question was resolved or `q0` became free, the remedy is to lease the question you can take rather than to retry; a session stands in one question lease at a time, so leasing or waiting for another question gives up this one.
4. `commands.question_release` gives up the lease, or your place in the queue, without taking the question. Use it as soon as you decide not to take that question, including after `commands.question_take` refused it because you already hold one. A question lease has no time limit: until you take the question, release the lease or end your session, everyone waiting for the question waits for you, and the runner does not count the question as free when it decides whether to launch another explorer.

An occupied question cannot be given back; it stays with your pipeline through peer and review. The `questions` list that `commands.updates` returns shows, for each question, whether it is open or resolved, which explorations hold it (`occupied_by`, a list that is empty for an unoccupied question and names both explorations when an organizer has merged two questions they held), and whether it is free as the runner counts it: open, held by no exploration and under no session's lease. That flag does not set aside the rule above: while `q0` is free, a narrower question is listed as free and is still refused until `q0` is held.

To coordinate an unexpected overlap, write a short message file in your directory and run `commands.message` with the recipient's session ID and that file. If registered sections turn out to overlap, they stay as registered: agree by message which session pursues the shared part, and record the agreement in your report. Use coordination messages for coordination facts and pointers to published evidence. Ordinary attempts do not obtain another session's unfinished mathematics through messages. Delivery creates a file in the recipient's inbox; it does not establish that the recipient has read it. The `messages` that `commands.updates` returns are the files in your own inbox. A coordination message carries the sender's session ID in `from` and its text in `text`. A notice the runner places there when shared research is published carries the publication's `event` and `revision` instead of a sender; it tells you only that the frontier and index have changed since you last read them.

When an attempt runs `commands.updates`, the command saves the unresolved nodes and section assignments in the session's `availability/` directory. It returns an `availability_snapshot` token identifying that snapshot. The attempt can use the token in the availability report described in [Retained work](retained-work.md). The token identifies what the attempt inspected; the attempt still judges whether all work is occupied.

## Lean compilation

All Lean compilation goes through the instance's broker. It manages the memory and thread budgets shared by compiles and retains each job's output and exit result. The `commands.lean` array gives the executable, broker script and instance. Replace `<command>` with `run`, `submit`, `build`, `wait`, `result`, `status`, `cancel` or `version`, adding the arguments described in [Lean](lean.md). Read that guide before your first compile, including its explanation of the memory estimate.

A single-file submission has this form:

```text
python <broker> submit <instance> <absolute-file.lean> --session <your-session-id> --expect-mb <estimated-peak-MiB>
python <broker> wait <instance> <job-id> --timeout 50
```

A `wait` timeout returns exit code 124 while the job continues. Follow the same job to its result. For a single-file job, `finished` includes Lean's actual exit code, while `failed` identifies an execution problem and `cancelled` identifies cancellation. For a module build, inspect the module outcomes: a dependency's compiler rejection can prevent its targets from running and produce an aggregate `failed` result with command exit code 3. A `finished` build can also have a nonzero compiler exit code. [Lean](lean.md) explains how to follow the module job IDs to the original diagnostics. These execution outcomes do not replace examining the source's mathematical validity.

For your own modules, use `build` with a module root and target paths. Independent review uses `--fresh-targets`: dependencies already built from unchanged sources may be reused, while the target is compiled again by the reviewing session. A successful compile must still be accompanied by an audit of every axiom the target uses, including through other lemmas and imports, and a comparison with the exact node.

## Other computations and literature tools

Use the CLI's available shell, file and search tools for the mathematics. For a long computation, write progress and final output to files in your session directory and retain its process or job identifier. When a shell tool stops waiting, recover the actual exit and output through its continuation mechanism. Starting a duplicate computation obscures which input produced which result.

The available external tools are the servers explicitly configured in this instance. If scholarly-mcp is present, its source descriptions explain which databases and operations are supported. If a tool or source is unavailable, record the limitation and use another available source where appropriate. The fact that the operator has a personal tool configuration does not make that tool part of your session.

## Checking and ending

Run the transport check, `commands.check`, against your own session directory before finishing. Exit code 0 with `ok: true` means the transport structure and references passed. A failure identifies a field or missing file to fix. The check does not prove mathematical claims or evaluate the quality of the exposition.

Producing sessions retain useful partial work even if interrupted before their final report is complete. Peers, reviewers and organizers need structurally usable outputs for the runner to apply their decisions. If one of those sessions is interrupted, the runner preserves its partial material and starts a fresh session for that stage. A missing output is an unfinished stage, not a mathematical rejection.
