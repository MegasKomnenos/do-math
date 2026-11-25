# Retaining a session's work

An attempt, an exploration or a formalizer leaves its work for a peer, who takes the same line of work over and writes the change to the canon. What the producing session leaves is material and not a finished product, and the peer reads all of it, including the conversation. Two things make that material usable: a report that says where everything is and what it means, and Lean files in which the session's definitions and statements are written and, as far as possible, compiled.

A peer also receives this guide. The report and the outcome described here belong to the producing session whose work the peer develops; the peer's own output is the candidate that [The candidate change](change-format.md) describes. The sections on working Lean files and on continuing a session apply to the peer as well.

## The report

Use `output/report.md` as the entry point to your retained work. Start it while researching and keep it current. The sections below make the important information findable; add mathematical subsections or companion files wherever the argument needs them.

| Section | What the next researcher needs |
|---|---|
| Current work | The statement under work, by its Lean name, the sections you registered or the question you hold, the current approach and what is being investigated now. |
| Lean definitions and statements | Where your Lean files are. For each declaration you wrote: what it is meant to say, whether it compiles and against which revision of the canon, and, if it does not compile yet, what stopped it. |
| Mathematics | Arguments and completed intermediate steps, each with the elements of the canon it uses, by name; computations with their interpretation; literature used, with its application. |
| Results and evidence | What was established, its scope and evidence, and what remains observed, conjectural or unchecked. |
| Approaches and where they stopped | For each approach: the idea, what it established, where it stops and why, and what that failure actually excludes. |
| Remaining work and artifacts | Unresolved opportunities, remaining obligations, and paths to code, data, logs and notes. |

The peer turns this material into a candidate, and it helps to know how. Your Lean definitions and statements become elements, each with a record that the peer writes. Your arguments become the proofs in those records. Your account of each approach becomes an entry among the approaches tried on the statement it was aimed at, and what an exploration came to understand enters the understanding so far of its question. You do not write records or entries yourself. What you can do is leave, for each thing you found, what its record will need: what the statement says in words, why it holds, how its Lean form corresponds to the mathematics, and which elements its proof rests on. [The written texts of the canon](records.md), which your peer receives, describes those formats.

State mathematical dependencies where the argument uses them. Identify an element of the canon by its Lean name and explain how you use it. A reference for motivation or history is different from a premise.

Keep scratch work in `work/` and what the peer should treat as your results in `output/`, and link both from the report. Preserve corrected calculations and abandoned arguments when they explain what was learned. For a long computation, keep inputs, code, outputs and the actual execution result. For Lean, name the folder of your working copy, the files you added or changed, the builds you ran and what each returned. Do not label a compilation successful merely because a wait command returned.

## Working Lean files

You write and compile your own Lean against a copy of the canon's library. The copy is made by `commands.canon` with the command `checkout` and a folder, for example `checkout work/lean`. A relative folder is taken from your session directory; the folder has to be inside that directory and must be new or empty. The command copies the module root of the library into it and prints the folder and the revision of the canon it copied.

In the copy, add your declarations in new module files under the library's folder, in the form [The canon](canon.md) gives for the canon's files. To try a new proof of a statement that already exists, change the body of its declaration in your copy and leave its statement as it is. A new definition or statement always goes into a new file, since that is how it will enter the canon.

Compile with the `build` command of the Lean broker. In the `commands.lean` array, replace `<command>` with `build` and append the folder of your copy, the files you want compiled, and the two required options:

```text
<commands.lean with build> <folder> <file.lean>... --session <your session ID> --expect-mb <MiB>
```

The broker compiles the named files together with every module of the copy that they import. The modules you did not change are the canon's own, and the broker normally takes their compiled form from its cache, so that only your files are compiled. [Lean](lean.md) explains the memory estimate, how to wait for a build that outlasts your shell tool, and how to read a build's result.

Your copy does not follow the canon. When a publication adds something you need, check the canon out again into a new folder and carry your own files over; say in the report which revision your files were last built against.

What you hand on is this: for a new module, its file; for a new proof of an existing statement, the complete text of that declaration. Copy the new modules into `output/lean/`, each at the path its module name gives. Put the text of a declaration whose proof you wrote anew into `output/replace/`, one file for each declaration, named after the declaration, and say in the report which imports the declaration's module gains with it. List all of these files in the report; the working copy stays in `work/`. The peer assembles the candidate from these and has it compiled as a whole on the current canon. Producing sessions do not prepare candidates, and the command for it refuses them. A declaration that does not compile yet is still worth handing on, with what stopped it.

## The outcome

When finishing normally, write `output/outcome.json`:

```json
{"summary": "Explain what this session established and where its work stopped.",
 "report": "report.md", "remaining": ["State a concrete remaining obligation, if any."]}
```

For a session that undertook research, this small manifest makes the endpoint easy to find. It is not a success certificate or a publication gate. The runner forwards retained producing material to a peer even if an interruption prevents the manifest or the report from being completed. Save important work throughout so that there is material to recover.

Attempts and peers register sections with the coordination commands, which record them in the session's `declaration.json`. An explorer registers no sections; it occupies one question, recorded in the same file either by the runner, when it assigned question `q0` at launch, or by the explorer's own `question_take`. A formalizer receives its statement in its assignment, and the runner records for it a section that covers the whole of that statement. None of these roles changes the canon directly; the peer writes the candidate and review judges it.

## Continuing an attempt, exploration, formalization or peer session

For an attempt or explorer that undertook research, a formalizer or a peer, ending a CLI turn does not immediately close the session. The session's host, the separate process through which the runner launched your CLI and which stays alive for the whole session, can resume the same conversation with common and role-specific guidance to continue its mathematical work under the role guide. The assignment, saved instructions, files, registered sections and occupied question remain those of the same session. This continuation asks you to apply the existing criteria for completing or ending your work; it does not replace those criteria.

If your judgment is that the session should continue, continue the mathematical work in that turn. No decision file is needed before doing so. If your judgment is that the session should end, write `output/end-decision.json` using the request ID in the resumption message or in `end-request.json`, which is in your session folder beside `input.json`. A decision counts only as the answer to such a request. One written before any request, in your first turn, is set aside unread, and the host resumes the session once to ask; so after your work is done, run the transport check and end, and write the decision when you are asked:

```json
{
  "request_id": "<the current request ID>",
  "decision": "end",
  "basis": "no_way_forward",
  "explanation": "The grounds for ending, from the work actually undertaken."
}
```

Use exactly these fields. `basis` is `task_completed` when the work you took on is complete, or `no_way_forward` when your investigation justifies an unresolved ending under the role guide. The explanation gives the grounds for that judgment. Write the decision only when you have made that judgment for the current ending. A decision from another request cannot authorize this turn's ending. A missing or invalid decision leads to another reconsideration turn while the configured allowance remains.

The runner records end authorization after a valid decision or after the configured maximum number of resumptions. At the maximum it authorizes the handoff itself, recording `source: runner` and `basis: resumption_limit`. That is an operational limit, not the worker claiming completion or an impasse. A valid worker decision is recorded with `source: worker`. Neither kind of end authorization changes the standing of any statement; the peer and independent review still assess the retained work. The session's `end-check.json` is the host's record, not a worker output file. A submitted `output/end-decision.json` is likewise not role output: when the turn ends, the host moves it out of `output/` before checking it. A later turn in which you continue the work therefore starts without it, and a peer's candidate does not contain it. The receipt of `commands.prepare` leaves the decision file out of what it records as the candidate, so writing the decision after you have prepared a candidate calls for no new preparation.

The initial turn's prompt and CLI streams remain at the session root. Resumed turns have separate prompts, commands, process receipts, streams, submitted decisions (`submitted-end-decision.json`) and decision checks under `turns/`.

The host remains alive across those turns, so the session retains its capacity slot and coordination identity, and downstream processing and archiving do not begin midway. Processes the session starts belong to it, including computations left running in the background between turns: they continue while the host lives, and on Windows they all end when the session ends, so results a computation has not written to your files by then are lost. A peer's candidate is frozen only after its logical session ends; resumed turns can still develop its output before independent review.

Dispatch stop also holds new resumption turns. A provider refusal, execution failure or operator cancellation ends the interrupted work through the existing retention path; an unavailable native conversation identity is recorded as `resume_unavailable`, without substituting a fresh conversation. Availability-only `no_research` outcomes use the separate path below.

## Ending before research starts

An attempt may read the research context and check the frontier and the board, yet find nothing it can take on. An explorer launched without an assigned question may find, after reading the questions and the board, that every open question is already held. That assessment does not itself begin research. To end a session in which you have only assessed availability, have registered no section and occupy no question, write this to `output/outcome.json`:

```json
{"disposition": "no_research"}
```

No report is required. Run `commands.check`, correct any errors it reports, and exit. After a successful exit, the runner retains your files and conversation and closes the pipeline without a peer or a review. That decision is final for this session: later changes in available work do not reopen it.

Use this outcome only for a session that never began mathematical investigation. Reading the canon to understand the statements and questions, what is established about them and whether they are available can be part of choosing work. Developing or testing your own mathematical approach is research, including before a section is registered: this includes developing an argument, investigating a counterexample, running a mathematical computation, or writing definitions and statements of your own in Lean, even without a successful result. Preserve that work for a peer. The runner does not accept `no_research` from a session that registered a section or occupies a question, exited unsuccessfully or received a provider refusal. It sends retained work to a peer; a failed launch without retained material is retried.

## Reporting that all the work that remains is occupied

Your session outcome says what you did. An availability report concerns something else: whether another attempt could find work to take on. The report is part of an attempt's `no_research` outcome, as in the example below; an explorer's outcome carries no such report, because the runner sees which questions are free without a judgment. The runner and the transport check read the `availability` field only beside that disposition; in the ordinary outcome of a session that undertook research, the field is not read. You can add this report when you have determined that the sections other pipelines hold cover all the work that remains for the root:

```json
{
  "disposition": "no_research",
  "availability": {
    "status": "all_unresolved_work_occupied",
    "snapshot": "<availability_snapshot returned by commands.updates>"
  }
}
```

Read the current `commands.updates` result and copy its `availability_snapshot` token into the report. When an attempt runs that command, the command saves, in the session's `availability/` directory, the elements of the work that remains together with the sections registered on each, as they were when you examined them, and the token identifies that snapshot. These are the elements that `list --remaining` returns: the frontier's elements whose proof is not accepted, and those whose proof names a statement that has since been refuted. You judge whether those sections cover the work. The runner checks whether that state has changed; it does not prove coverage or interpret a prose explanation. Not seeing a promising approach yourself is not enough to report that all the work is occupied.

The runner processes the availability report separately from `disposition`. A stale or invalid report cannot prevent a valid `no_research` outcome from closing your session. It only means that the report cannot suppress new attempts. The transport check reports invalid fields or snapshot tokens so you can correct them before exiting.

An accepted report makes the runner wait before launching further attempts. Three things give it reason to reconsider. One is the end of a section's occupancy on an element that still remains; publication, or a completed review decision that there is nothing to publish, ends that occupancy, and this differs from releasing a lease or a place in its queue. Another is an element that is new among the work that remains, or that has become work again, as when a finding withdraws the confirmation of a proof. The third is an operator request. The runner then launches one attempt to assess availability again. Registration of work returns the runner to normal attempt scheduling; another applicable report of full occupancy makes it wait again. Exploration continues on its own questions while attempts wait.
