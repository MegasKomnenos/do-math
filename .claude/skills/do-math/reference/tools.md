# Tools and working files

Your role guide explains the mathematical work you own. This guide explains the files and commands supplied for that work; the service that compiles Lean is explained in [Lean](lean.md). The commands that only some roles use are described where those roles receive them: registering a section in [Sections](sections.md), taking a question in the explorer's role guide, preparing a change in [The candidate change](change-format.md), and verifying one in [Review output](review-output.md).

The runner records the concrete paths and commands in `input.json`. Its `instance` and `session` identify where you are working, `role` and `task` identify your assignment and the inputs specific to it, `settings` holds the settings in force at your launch, and `commands` gives the executable argument arrays. Read these values before invoking a command. The forms shown below explain what the commands do; your input supplies the actual executable locations and identifiers.

Each command is an argument array: pass its elements separately to the process, replacing a placeholder such as `<element>` or `<file>` with your value, and append further arguments after the last element of the array. This avoids guessing executable locations or relying on a shell alias.

## Files you work with

**Your session directory.** Use `work/` for scratch mathematics, Lean files under development, computations and intermediate artifacts. Use `output/` for the retained report or role output your successor will read. Keep the files and any generated caches in your own session directory. The runner preserves `pack.md`, which is your starting context, `input.json`, the copies of the guides under `context/`, and the available CLI conversation. `inbox/` receives messages for you. Your role's guides state the entry file and fields of your output.

**The canon.** `canon/` under the instance holds the knowledge of the research: the Lean library and the written files beside it. [The canon](canon.md) shows where its folders and files are.

You read the canon and never write in it. A change to it is a candidate that a peer or an organizer assembles in its own `output/`, and publication is the runner's work. The commands under Reading the canon below are the way to read it, because a view joins what Lean knows of an element with what its record says and a traversal returns the whole of what its rule selects. The files are there for the cases where you need the source itself: to read or change the body of a Lean proof, or to see more of a declaration than its printed statement.

**The derived views.** `knowledge/` under the instance holds views the runner renders and the published judgments. `frontier.md` is the frontier with the questions, `index.md` the self-descriptions of all elements in the order of the Lean structure, `board.md` the work underway, and `state.json` the same state in structured form. `changes/<id>/` holds one published change with review's assessment and feedback, `reviews/<id>/` a comprehensive review, `organizations/<id>/` an organizer's output, and `questions/<id>/` questions the operator placed. Read these and follow them to the canon; write your contributions in your own output.

Read required documents in full. If a file-reading tool truncates its output, retrieve the omitted ranges before treating the document as read. A successful read command can still have returned only part of the file.

Working paths can be absolute when invoking tools. What a later reader needs has to be in the canon: state the mathematics as elements, publish the files a record relies on as its evidence, or cite a stable published source. A reference to a producer's private working file cannot support an ordinary session, which may read only what is published.

## Reading the canon

`commands.canon` reads the canon. [The canon](canon.md) lists its reading commands under "Reading the canon: the commands" and describes what each view shows. The same array has one further command, `checkout <folder>`, which copies the library, `canon/lean`, into a new or empty folder inside your session directory, so that you can build your own Lean files against it.

An element is named by its declaration name as the canon shows it, for example `Parking.Columns.dq_col`.

The canon changes while you work, as other sessions' changes are published. A notice arrives in your inbox at each publication, and running a reading command again returns the current state. A copy made with `checkout` does not follow those changes. The command prints, as JSON, the folder and the revision of the canon it copied; note the revision if you will need it, since nothing in the folder records it. A later checkout into another folder gives the current library.

## Current research and coordination

The views in your starting context tell you what the research held when you launched. To see what has changed since, use the reading commands above for the canon and `commands.updates` for the work underway.

`commands.updates` returns the current revision and the state of the root; the live board, with each pipeline's sections and the question each exploration holds; the element and question leases; the current questions with their state and holder; the concerns; the comprehensive review assignments; and the messages in your inbox. The user inputs it returns are your original launch snapshot. Publications, sections, questions and leases remain live.

### Messages

To coordinate an unexpected overlap, write a short message file in your directory and run `commands.message` with the recipient's session ID and that file. If registered sections turn out to overlap, they stay as registered: agree by message which session pursues the shared part, and record the agreement in your report. Use coordination messages for coordination facts and pointers to published elements. Ordinary attempts do not obtain another session's unfinished mathematics through messages. Delivery creates a file in the recipient's inbox; it does not establish that the recipient has read it. The `messages` that `commands.updates` returns are the files in your own inbox. A coordination message carries the sender's session ID in `from` and its text in `text`. A notice the runner places there at each publication carries the publication's `event`, `kind` and `revision` instead of a sender; it tells you only that the canon has changed since you last read it.

## Other computations and literature tools

Use the CLI's available shell, file and search tools for the mathematics. For a long computation, write progress and final output to files in your session directory and retain its process or job identifier. When a shell tool stops waiting, recover the actual exit and output through its continuation mechanism. Starting a duplicate computation obscures which input produced which result.

End a computation you started by its process ID, and never by its name. A command that selects processes by image name, such as `taskkill /IM python.exe`, `Stop-Process -Name python`, `Get-Process python | Stop-Process` or `wmic process where "name='python.exe'" delete`, ends every process of that name on the machine. The runner, the Lean broker and each session's host, the process that launched that session's CLI and stays alive for the whole session, all run as `python.exe`, and when a session's host ends, the system ends that session's CLI and everything the session started. Choosing another name, such as `lean.exe` or `claude.exe`, changes nothing, because other sessions run processes of the same names. In an earlier run a delegated agent, meaning to stop one script of its own, issued such a command and ended the runner together with all twelve sessions then running, its own among them. The process ID is the one you noted when you started the computation. If you did not note it, find the process whose command line contains your session directory and the script's name, and end that one.

The available external tools are the servers explicitly configured in this instance. The literature server scholarly-mcp is normally one of them. [Literature](literature.md) explains how to use it and which sources it offers to sessions. The server keeps what it retrieves in one store shared by every session on the machine, so an item that an earlier session retrieved can be read with `extract` from the reference that session recorded. If a tool or source is unavailable, record the limitation and use another available source where appropriate. The fact that the operator has a personal tool configuration does not make that tool part of your session.

## Delegating to sub-agents

A Claude session has the CLI's own tool for launching delegated agents; its general-purpose agent is available, and the agent's model and effort can be chosen when it is launched. A Codex session is launched with its multi-agent feature disabled, so it cannot delegate. A delegated agent runs as part of your session: it works in your session directory, its files belong to your retained work, and a Lean compile it submits carries your session ID, so the broker treats it as a submission of your session. The review role guide specifies the one delegation that a role requires, the three independent sub-reviews; other roles may delegate when it serves their work, and remain responsible for everything a delegated agent produces.

A delegated agent's final message comes back to you as the result of the delegation, and that message is its report. The CLI refuses a delegated agent that tries to write a report or its findings to a file and tells it to put the content in its final message, so ask for the report there and not in a file. The report is kept in the CLI stream of your turn, and once your session has ended the agent's whole conversation is kept with your session's transcript. Files that a delegated agent makes as part of the work itself, such as the script and the output of a computation, go under `work/`.

A delegated agent is launched in the background: the tool that launches it returns at once, and the agent goes on working while your turn continues. It belongs to the CLI process of that turn and ends when that process exits, whether or not it has finished. The process does not exit the moment your turn ends: while an agent is still at work it waits for a limited time, an agent that finishes during the wait starts your next turn, and at the limit the process stops the agents still at work and exits. A result you need from an agent therefore has to arrive before you end the turn, so wait for it within the turn.

A delegated agent begins with nothing but what you hand it. It has not read the guides in your context or the user conditions of this instance, so your briefing has to carry whatever in them bears on the work you delegate: the conditions that govern the judgment you are asking for, that everything is written in English, that its own files go under `work/`, the conventions of the canon if the agent will write Lean, the folders in which the sources of the imported library lie if the agent will read that library ([Lean](lean.md) says where they are), and the paragraph above on ending processes if the agent may run computations.

## Checking and ending

Run the transport check, `commands.check`, against your own session directory before finishing. It prints `{"ok": true, "errors": []}` and exits with code 0 when the structure and references of your output passed. For an attempt, an exploration and a formalizer it checks only that `output/` contains no filesystem links and, for an outcome that reports no research, the conditions of that outcome; it does not read the report, so a passing check says nothing about whether the report is complete. A failure names what to fix: a field, a missing file, a candidate that was not prepared or was edited after it was prepared. The check stops at the first fault it meets, so run it again after each correction until it passes. The check does not prove mathematical statements or evaluate the quality of the exposition.

Producing sessions retain useful partial work even if interrupted before their final report is complete. Peers, reviewers and organizers need structurally usable outputs for the runner to apply their decisions. A missing output is an unfinished stage, not a mathematical rejection.
