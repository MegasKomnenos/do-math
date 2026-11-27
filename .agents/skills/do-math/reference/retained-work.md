# Retaining a session's work

An attempt, an exploration or a formalizer leaves its work for a peer, who takes the same line of work over and writes the change to the canon. What the producing session leaves is material and not a finished product, and the peer reads all of it, including the conversation. Two things make that material usable: a report that says where everything is and what it means, and Lean files in which the session's definitions and statements are written and, as far as possible, compiled.

A peer also receives this guide. The report and the outcome described here belong to the producing session whose work the peer develops; the peer's own output is the candidate that [The candidate change](change-format.md) describes. A peer that hands its task over to a new session writes the same sections, as far as they apply to a candidate under construction, into `work/report.md`: what of the candidate stands in `output/`, what is still to be written or compiled, and what it decided and why. The sections on working Lean files, on handing a task over and on continuing a session apply to the peer as well.

## The report

Use `output/report.md` as the entry point to your retained work. Start it while researching and keep it current. The sections below make the important information findable; add mathematical subsections or companion files wherever the argument needs them.

| Section | What the next researcher needs |
|---|---|
| Current work | The statement under work, by its Lean name, the sections you registered or the question you hold, the current approach and what is being investigated now, with the argument in hand as far as it goes and the point at which it is still open. |
| Lean definitions and statements | Where your Lean files are. For each declaration you wrote: what it is meant to say, whether it compiles and against which revision of the canon, and, if it does not compile yet, what stopped it. |
| Mathematics | Arguments and completed intermediate steps, each with the elements of the canon it uses, by name; computations with their interpretation; literature used, with its application. |
| Results and evidence | What was established, its scope and evidence, and what remains observed, conjectural or unchecked. |
| Approaches and where they stopped | For each approach: the idea, what it established, where it stops and why, and what that failure actually excludes. |
| Remaining work and artifacts | What you would do next and why, unresolved opportunities, remaining obligations, and paths to code, data, logs and notes. |

The peer turns this material into a candidate. Your Lean definitions and statements become elements, each with a record that the peer writes, and your arguments become the proofs in those records. Your account of each approach becomes an entry among the approaches tried on the statement it was aimed at, and what an exploration came to understand enters the understanding so far of its question. You write no records or entries yourself, but you can leave, for each thing you found, what its record will need: what the statement says in words, why it holds, how its Lean form corresponds to the mathematics, and which elements its proof rests on. [The written texts of the canon](records.md), which your peer receives, describes those formats.

State mathematical dependencies where the argument uses them. Identify an element of the canon by its Lean name and explain how you use it. A reference for motivation or history is different from a premise.

Keep scratch work in `work/` and what the peer should treat as your results in `output/`, and link both from the report. Preserve corrected calculations and abandoned arguments when they explain what was learned. For a long computation, keep inputs, code, outputs and the actual execution result. For Lean, name the folder of your working copy, the files you added or changed, the builds you ran and what each returned. Do not label a compilation successful merely because a wait command returned.

## Working Lean files

You write and compile your own Lean against a copy of the canon's library. The copy is made by `commands.canon` with the command `checkout` and a folder of your session directory, for example `checkout work/lean`, and the command prints the revision of the canon it copied.

In the copy, a new definition or statement always goes into a new module file under the library's folder, in the form [The canon](canon.md) gives for the canon's files, since that is how it will enter the canon. To try a new proof of a statement that already exists, change the body of its declaration in your copy and leave its statement as it is.

Compile with the `build` command of the Lean broker. In the `commands.lean` array, replace `<command>` with `build` and append the folder of your copy, the files you want compiled, given as paths relative to that folder, and the two required options:

```text
<commands.lean with build> <folder> <file.lean>... --session <your session ID> --expect-mb <MiB>
```

[Lean](lean.md) describes `checkout` and `build` under "Building against the canon and your own modules", and explains the memory estimate, how to wait for a build that outlasts your shell tool, and how to read a build's result.

Your copy does not follow the canon. When a publication adds something you need, check the canon out again into a new folder and carry your own files over; say in the report which revision your files were last built against.

Hand on each new module as its file, copied into `output/lean/` at the path its module name gives, and each new proof of an existing statement as the complete text of that declaration, put into `output/replace/` as one file for each declaration, named after the declaration; say in the report which imports the declaration's module gains with it. List all of these files in the report; the working copy stays in `work/`. The peer assembles the candidate from these and has it compiled as a whole on the current canon. Producing sessions do not prepare candidates, and the command for it refuses them. A declaration that does not compile yet is still worth handing on, with what stopped it.

## Handing a task over to a new session

Hours of work fill the context that your conversation can hold, and a conversation that is full cannot go on. Your work then goes on from your files alone. The CLI's record of the conversation does not stand in for them: it holds the commands you ran, their output and the messages you wrote, and little or none of the reasoning between them. An argument that you worked out and wrote nowhere is therefore found by no one who reads that record later, neither a peer nor a session that continues your task.

The runner can tell a session when its conversation is nearly full, by a message of the kind [Tools and working files](tools.md) describes, and the conversation of such a session is not shortened on the way. The message states how much the conversation holds, what fills the room that is left and what happens at the limit. It comes while a part of the window is still free so that you can close your work with care, and nothing in it presses you for time. What it asks for first is that you close the work in the way that hands it over best, and that you judge calmly what to finish, what to check and what to hand on as it stands. It is a request to decide your ending, like the request of a resumed turn under "Continuing an attempt, exploration, formalization or peer session" below, with the request ID that it states, and you answer it in the turn in which it arrives, as the last thing you write in that turn. Two of the answers are the endings that section describes, judged as it describes. The third is for work that is to go on: the basis `handed_over`. The runner then launches a new session of your role on the same task. That session has a folder of its own and receives the pack of your role as it then stands, with the same assignment; the sections you registered or the question you hold stay held for it, and nothing goes to a peer or to review in between. Its assignment lists under `continues` the folders of the sessions that worked on the task before it, yours last. It has your files and not your conversation, so it starts from your report. Before you answer with `handed_over`, the report therefore has to hold everything from which the work can go on without you, in the sections of the table above, and your Lean files are handed on as "Working Lean files" describes. The session that takes the task on has a whole conversation of its own ahead of it and is not pressed for time. What you would do next is therefore written for a session in that position: how far it pursues a direction and when it ends are for it to judge under the role guide, as they were for you, and your report leaves both to it. Handing a task over ends your conversation and not the research. The room after the message is for that closing. A session that takes up new work in it reaches the limit of its window: the CLI refuses the request that no longer fits, the turn ends at that point, and the runner starts the new session from the files as they then stand.

When your own assignment carries `continues`, you are such a new session. Start from the report of the last session before you, which is `output/report.md` in its folder, or `work/report.md` when you are a peer, a review or an organizer, and from what that report points to. The earlier folders stay where they are, and the records of their conversations are there to look something up in, within the limit stated above. A coordination message that another session sent to one of those sessions, about the sections or the question you now hold, is in the `inbox/` of that session's folder and not in your own inbox. How far you pursue a direction and when you end are yours to judge under your role guide, also where an earlier report says otherwise. The same holds for what the common introduction asks of whatever a session pursues, under "Working directly on the central difficulty": ask it of what the earlier sessions chose before you go on with it.

What you leave is again read by someone who is given your folder, a peer or a further session of your role. So before you begin work of your own, carry over into your own `output/`, which starts empty, what still stands in the `output/` of the session before you; for an attempt, an exploration or a formalizer that includes its report. Your folder then holds what that session handed on, also if your own session is cut off early. The working files of the earlier sessions stay in their own `work/` folders, while a path in your report that begins with `work/` is read as a path in your folder. The report you carried over was written in the earlier session's folder, so the files that its `work/` paths name are there: copy each file of theirs that your report relies on into your own `work/`, or write its path with that session's folder. From then on the report is yours, and it is the report of the task as a whole, as the task stands when you leave it. Arrange it anew where your work does not fit the way it was arranged. What the earlier sessions established and what they left open stays in it, a line of work that you leave stays as an approach with where it stopped, and where your work has proved, refuted or carried out something the report speaks of, the passage is brought up to date where it stands. A peer that takes over the work of such a chain is given the folder of its last session as `source`; `continues` in that folder's `input.json` names the folders before it, each with the record of its own conversation. A session of such a chain that was cut off, at the limit of its window or by an interruption, may have ended before its report and its `output/` held the task as a whole. What it had not carried over is then still in the report, the `output/` and the `work/` of the folder before it, and it belongs to what the next session of the role, or the peer, takes over.

If you are sent no such message, you meet a compaction instead, and you recognise it by a summary that stands in your conversation in place of its earlier part. Before the conversation is full, the CLI replaces it up to that point with that summary, and you go on from the summary, the last few messages and the files in your session directory; a long session can meet more than one compaction. The guides you read at launch are part of what is replaced; `pack.md` still holds them. A file comes through as you wrote it: a statement in Lean, an argument in the report or in a note under `work/`, the script and the output of a computation. What stood only in the conversation comes through as far as the summary carries it. The summary is written when the CLI asks for it, from what the conversation holds at that moment, and it has room for a small part of that: it can carry a result as one line, without its exact statement or its proof. What a file holds is not lost when the summary leaves it out; what no file holds is kept by the summary or not at all, because the CLI's record, which the summary may point you to, does not supply what the summary left out. The summary itself stays in the record as one of its messages, and a peer finds there what the producing session still had in mind at a compaction and had not written to a file.

## The outcome

When finishing normally, write `output/outcome.json`:

```json
{"summary": "Explain what this session established and where its work stopped.",
 "report": "report.md", "remaining": ["State a concrete remaining obligation, if any."]}
```

For a session that undertook research, this small manifest makes the endpoint easy to find. It is not a success certificate or a publication gate. The runner forwards retained producing material to a peer even if an interruption prevents the manifest or the report from being completed. Save important work throughout so that there is material to recover.

## Continuing an attempt, exploration, formalization or peer session

For an attempt or explorer that undertook research, a formalizer or a peer, ending a CLI turn does not immediately close the session. The same conversation can be resumed with common and role-specific guidance to continue its mathematical work under the role guide. The assignment, saved instructions, files, registered sections and occupied question remain those of the same session. This continuation asks you to apply the existing criteria for completing or ending your work; it does not replace those criteria.

If your judgment is that the session should continue, continue the mathematical work in that turn. No decision file is needed before doing so. If your judgment is that the session should end, write `output/end-decision.json` using the request ID in the resumption message or in `end-request.json`, which is in your session folder beside `input.json`. A decision counts only as the answer to such a request. One written before any request, in your first turn, is set aside unread, and the session is resumed once to ask; so after your work is done, run the transport check and end, and write the decision when you are asked:

```json
{
  "request_id": "<the current request ID>",
  "decision": "end",
  "basis": "no_way_forward",
  "explanation": "The grounds for ending, from the work actually undertaken."
}
```

Use exactly these fields. `basis` is `task_completed` when the work you took on is complete, or `no_way_forward` when your investigation justifies an unresolved ending under the role guide. A third basis, `handed_over`, answers only the runner's message that your conversation is nearly full, and says that the work is to go on in a new session, as "Handing a task over to a new session" above describes. The explanation gives the grounds for that judgment, or, with `handed_over`, what is done and what remains. Write the decision only when you have made that judgment for the current ending. A decision from another request cannot authorize this turn's ending. A missing or invalid decision leads to another reconsideration turn while the configured allowance remains.

The number of these resumptions is limited by the instance's configuration, `settings.max_end_resumptions` in your `input.json`. At the limit the session ends and its work is handed on without a decision of yours. Neither that ending nor one by your decision changes the standing of any statement; the peer and independent review still assess the retained work. A submitted `output/end-decision.json` is not role output: it is taken out of `output/` when the turn ends. A later turn in which you continue the work therefore starts without it, and a peer's candidate does not contain it. The receipt of `commands.prepare` leaves the decision file out of what it records as the candidate, so writing the decision after you have prepared a candidate calls for no new preparation.

Processes the session starts belong to it, including computations left running in the background between turns: they continue while the session lasts, and on Windows they all end when the session ends, so results a computation has not written to your files by then are lost. A peer's candidate is frozen only after its logical session ends; resumed turns can still develop its output before independent review.

A provider refusal, an execution failure or an operator's cancellation ends the session without a reconsideration turn; what a producing session retained still goes to a peer, as "The outcome" above says. A `no_research` outcome is not followed by a reconsideration turn either, and the next section describes it.

## Ending before research starts

An attempt may read the research context and check the frontier and the board, yet find nothing it can take on. An explorer launched without an assigned question may find, after reading the questions and the board, that every open question is already held, or that it leaves every free one because, of each, its answer is not yes to the question the common introduction asks under "Working directly on the central difficulty". That assessment does not itself begin research. To end a session in which you have made only that assessment, have registered no section and occupy no question, write this to `output/outcome.json`:

```json
{"disposition": "no_research"}
```

No report is required. Run `commands.check`, correct any errors it reports, and exit. After a successful exit, the runner retains your files and conversation and closes the pipeline without a peer or a review. That decision is final for this session: later changes in available work do not reopen it.

Use this outcome only for a session that never began mathematical investigation. Reading the canon to understand the statements and questions, what is established about them and whether they are available can be part of choosing work. Developing or testing your own mathematical approach is research, including before a section is registered: this includes developing an argument, investigating a counterexample, running a mathematical computation, or writing definitions and statements of your own in Lean, even without a successful result. Preserve that work for a peer. The runner does not accept `no_research` from a session that registered a section or occupies a question; it sends the retained work to a peer. A session whose assignment carries `continues` does not use it either, also when it holds no section and no question and the runner would accept it: the sessions before it on the task did research, and that research reaches a peer only when this session ends as one that undertook research, with its report of the task as a whole.

## Reporting that all the work that remains is occupied

Your session outcome says what you did; an availability report says whether another attempt could find work to take on among the work the frontier shows, and it says nothing of statements outside the frontier. The report is part of an attempt's `no_research` outcome, as in the example below; an explorer's outcome carries no such report, because the runner sees which questions are free without a judgment. The runner and the transport check read the `availability` field only beside that disposition, and not in the ordinary outcome of a session that undertook research. You can add this report when you have determined that the sections other pipelines hold cover all the work that remains for the root:

```json
{
  "disposition": "no_research",
  "availability": {
    "status": "all_unresolved_work_occupied",
    "snapshot": "<availability_snapshot returned by commands.updates>"
  }
}
```

Read the current `commands.updates` result and copy its `availability_snapshot` token into the report. When an attempt runs that command, the command saves the elements of the work that remains together with the sections registered on each, as they were when you examined them, and the token identifies that snapshot. These are the elements that `list --remaining` returns: the frontier's elements whose proof is not accepted, and those whose proof names a statement that has since been refuted. You judge whether those sections cover the work. The runner checks whether that state has changed; it does not prove coverage or interpret a prose explanation. Not seeing a promising approach yourself is not enough to report that all the work is occupied.

An accepted report makes the runner wait before launching further attempts. A stale or invalid report does not, and it cannot prevent a valid `no_research` outcome from closing your session. The transport check reports invalid fields or snapshot tokens so you can correct them before exiting.
