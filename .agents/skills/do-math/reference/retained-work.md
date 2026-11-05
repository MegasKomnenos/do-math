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

This small manifest makes the endpoint easy to find. It is not a success certificate or a publication gate. The runner forwards retained producing material to peer even if interruption prevents the manifest or report from being completed. Save important work throughout so that there is material to recover.

Attempts and peers register sections with the coordination commands, which record them in the session's `declaration.json`. An explorer does not register sections. A formalizer receives its node in its assignment, recorded as a whole-node section. None of these roles directly creates shared nodes or publishes mathematical state; the peer prepares proposals and review assesses them.
