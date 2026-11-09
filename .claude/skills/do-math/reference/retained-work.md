# Retaining a session's work

Attempts, explorations and formalizers use `output/report.md` as the entry point to their retained work. Start it while researching and keep it current. Use the sections below to make important information findable, adding mathematical subsections or companion files wherever the argument needs them. The peer reads the producing session's complete retained work, including work outside this report and the available conversation.

| Section | What the next researcher needs |
|---|---|
| Current work | The exact statement under work, the registered sections or the question held where applicable, the current approach and what is being investigated now. |
| Definitions and assumptions | Objects and conditions used, links to inherited definitions, and the local terminology introduced here. |
| Mathematics | Arguments and completed intermediate steps, computations with their interpretation, and literature used with its application. |
| Results and evidence | What was established, its scope and evidence, and what remains observed, conjectural or unchecked. |
| Obstacles and failed approaches | What was tried, where it failed, the witness or gap, and what that failure actually excludes. |
| Remaining work and artifacts | Unresolved opportunities, partial formal sources, remaining obligations, and paths to code, data, logs and notes. |

State mathematical dependencies where the argument uses them. Identify published claims by record and claim ID, and explain their use. A reference for motivation or history is different from a premise. Define introduced terminology completely in `output/glossary-local.md`; that file can be empty of entries when you introduce none. Flag proposed global terms with the reason later research would benefit from sharing the name. Inherited definitions are referenced rather than copied into a new local entry.

Keep scratch work in `work/`, publication-ready evidence in `output/`, and link both from the report as needed. Preserve corrected calculations and abandoned arguments when they explain what was learned. For a long computation, keep inputs, code, outputs and the actual execution result. For Lean, identify the source tree, theorem names, broker jobs and any remaining obligations. Do not label a compilation successful merely because a wait command returned.

When finishing normally, write `output/outcome.json`:

```json
{"summary": "Explain what this session established and where its work stopped.",
 "report": "report.md", "remaining": ["State a concrete remaining obligation, if any."]}
```

For a session that undertook research, this small manifest makes the endpoint easy to find. It is not a success certificate or a publication gate. The runner forwards retained producing material to peer even if interruption prevents the manifest or report from being completed. Save important work throughout so that there is material to recover.

Attempts and peers register sections with the coordination commands, which record them in the session's `declaration.json`. An explorer registers no sections; it occupies one question, recorded in the same file either by the runner, when it assigned question `q0` at launch, or by the explorer's own `question_take`. A formalizer receives its node in its assignment, recorded as a whole-node section. None of these roles directly creates shared nodes, questions or published mathematical state; the peer prepares proposals and review assesses them.

## Continuing an attempt, exploration, formalization or peer session

For an attempt that undertook research, an explorer, a formalizer or a peer, ending a CLI turn does not immediately close the session. The session's host, the separate process through which the runner launched your CLI and which stays alive for the whole session, can resume the same conversation with common and role-specific guidance to continue its mathematical work under the role guide. An explorer continues developing understanding; a peer continues developing the retained mathematics into a useful record. Neither is required to settle the root or manufacture novelty to complete its role. The assignment, saved instructions, files, registered sections and occupied question remain those of the same session. This continuation asks you to apply the existing criteria for completing or ending your work; it does not replace those criteria. The installed `resume/common.md` and `resume/<role>.md` are read anew for each resumption, and their exact bytes are retained in that turn's `guidance/` directory. These message updates do not rewrite the original role guide, user conditions or turns already delivered.

If your judgment is that the session should continue, continue the mathematical work in that turn. No decision file is needed before doing so. If your judgment is that the session should end, write `output/end-decision.json` using the request ID in the resumption message or `end-request.json`:

```json
{
  "request_id": "<the current request ID>",
  "decision": "end",
  "basis": "no_way_forward",
  "explanation": "The grounds for ending, from the work actually undertaken."
}
```

Use exactly these fields. `basis` is `task_completed` when the work you took on is complete, or `no_way_forward` when your investigation justifies an unresolved ending under the role guide. The explanation gives the grounds for that judgment. Write the decision only when you have made that judgment for the current ending. A decision from another request cannot authorize this turn's ending. A missing or invalid decision leads to another reconsideration turn while the configured allowance remains.

The runner records end authorization after a valid decision or after the configured maximum number of resumptions. At the maximum it authorizes the handoff itself, recording `source: runner` and `basis: resumption_limit`. That is an operational limit, not the worker claiming completion or an impasse. A valid worker decision is recorded with `source: worker`. Neither kind of end authorization settles a mathematical node; peer and independent review still assess the retained work. The session's `end-check.json` is the host's record, not a worker output file. A submitted `output/end-decision.json` is likewise not role output: when the turn ends, the host moves it out of `output/` before checking it. A later turn in which you continue the work therefore starts without it, and a peer's candidate does not carry it into the published record.

The initial turn's prompt and CLI streams remain at the session root. Resumed turns have separate prompts, commands, process receipts, streams, submitted decisions (`submitted-end-decision.json`) and decision checks under `turns/`. The host remains alive across those turns, so the session retains its capacity slot and coordination identity, and downstream processing and archiving do not begin midway. Processes the session starts belong to it, including computations left running in the background between turns: they continue while the host lives, and on Windows they all end when the session ends, so results a computation has not written to your files by then are lost. A peer's candidate is frozen only after its logical session ends; resumed turns can still develop its output before independent review. Dispatch stop also holds new resumption turns. A provider refusal, execution failure or operator cancellation ends the interrupted work through the existing retention path; an unavailable native conversation identity is recorded as `resume_unavailable`, without substituting a fresh conversation. Availability-only `no_research` outcomes use the separate path below.

## Ending before research starts

An attempt may read the research context and check the frontier and board, yet find no section it can take on. An explorer launched without an assigned question may find, after reading the frontier's questions and the board, that every open question is already held. That assessment does not itself begin research. To end a session in which you have only assessed availability, have registered no section and occupy no question, write this to `output/outcome.json`:

```json
{"disposition": "no_research"}
```

No report or glossary is required. Run `commands.check`, correct any errors it reports, and exit. After a successful exit, the runner retains your files and conversation and closes the pipeline without peer or review. That decision is final for this session: later changes in available work do not reopen it.

Use this outcome only for a session that never began mathematical investigation. Reading existing research to understand the questions, their established coverage and their availability can be part of choosing work. Developing or testing your own mathematical approach is research, including before section registration: this includes developing an argument, investigating a counterexample, running a mathematical computation or beginning formalization, even without a successful result. Preserve that work for peer. The runner does not accept `no_research` from a session that registered a section or occupies a question, exited unsuccessfully or received a provider refusal. It sends retained work to peer; a failed launch without retained material is retried.

## Reporting that all unresolved work is occupied

Your session outcome says what you did. An availability report concerns something else: whether another attempt could find work to take on. The report is part of an attempt's `no_research` outcome, as in the example below; an explorer's outcome carries no such report, because the runner sees which questions are free without a judgment. The runner and the transport check read the `availability` field only beside that disposition; in the ordinary outcome of a session that undertook research, the field is not read. You can add this report when you have determined that other pipelines' registered sections cover all unresolved nodes:

```json
{
  "disposition": "no_research",
  "availability": {
    "status": "all_unresolved_work_occupied",
    "snapshot": "<availability_snapshot returned by commands.updates>"
  }
}
```

Read the current `commands.updates` result and copy its `availability_snapshot` token into the report. The token identifies the unresolved nodes and registered sections you examined. You judge whether those sections cover the remaining work. The runner checks whether that state has changed; it does not prove coverage or interpret a prose explanation. Not seeing a promising approach yourself is not enough to report that all work is occupied.

The runner processes the availability report separately from `disposition`. A stale or invalid report cannot prevent a valid `no_research` outcome from closing your session. It only means that the report cannot suppress new attempts. The transport check reports invalid fields or snapshot tokens so you can correct them before exiting.

An accepted report makes the runner wait before launching further attempts. The end of a section's occupancy on a still-unresolved node gives it reason to reconsider: publication or a completed review decision with no useful record ends that occupancy. This differs from releasing a lease or a place in its queue. A new or reopened unresolved node or an operator request also prompts reconsideration. The runner then launches one attempt to assess availability again. Registration of work returns the runner to normal attempt scheduling; another applicable report of full occupancy makes it wait again. Exploration continues on its own questions while attempts wait.
