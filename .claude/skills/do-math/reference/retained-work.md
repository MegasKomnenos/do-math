# Retaining a session's work

Attempts, explorations and formalizers use `output/report.md` as the entry point to their retained work. Start it while researching and keep it current. Use the sections below to make important information findable, adding mathematical subsections or companion files wherever the argument needs them. The peer reads the producing session's complete retained work, including work outside this report and the available conversation.

| Section | What the next researcher needs |
|---|---|
| Question and current work | The exact question, registered sections where applicable, current approach and what is being investigated now. |
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

Attempts and peers register sections with the coordination commands, which record them in the session's `declaration.json`. An explorer does not register sections. A formalizer receives its node in its assignment, recorded as a whole-node section. None of these roles directly creates shared nodes or publishes mathematical state; the peer prepares proposals and review assesses them.

## Ending before research starts

You may read the research context and check the frontier and board, yet find no section you can take on. That assessment does not itself begin research. To end a session in which you have only assessed availability and have registered no section, write this to `output/outcome.json`:

```json
{"disposition": "no_research"}
```

No report or glossary is required. Run `commands.check`, correct any errors it reports, and exit. After a successful exit, the runner retains your files and conversation and closes the pipeline without peer or review. That decision is final for this session: later changes in available work do not reopen it.

Use this outcome only for a session that never began mathematical investigation. Developing an argument, investigating a counterexample, running a mathematical computation or beginning formalization is research, even without a successful result. Preserve that work for peer. The runner does not accept `no_research` from a session that registered a section, exited unsuccessfully or received a provider refusal. It sends retained work to peer; a failed launch without retained material is retried.

## Reporting that all unresolved work is occupied

Your session outcome says what you did. An availability report answers a different question: whether another attempt could find work to take on. You can add this report when you have determined that other pipelines' registered sections cover all unresolved questions:

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

An accepted report makes the runner wait before launching further attempts. A section released on an unresolved node, a new or reopened unresolved node, or an operator request gives it reason to reconsider. It then launches one attempt to assess availability again. Registration of work returns the runner to normal attempt scheduling; another applicable report of full occupancy makes it wait again. Exploration continues under its own cycle rule while attempts wait.
