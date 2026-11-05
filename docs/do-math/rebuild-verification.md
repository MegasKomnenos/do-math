# do-math rebuild: verification

The new do-math runner launches attempt, explore, formalizer, peer, review and organizer sessions. Its implementation is in `.claude/skills/do-math/runtime/`; worker guides are in the same skill directory's `roles/` and `reference/` folders. The [operator entry point](../../.claude/skills/do-math/SKILL.md) explains how to prepare a run, and the [common worker guide](../../.claude/skills/do-math/reference/common.md) explains the research process and shared resources.

This report records the execution and documentation checks performed during the rebuild. The [verification results](rebuild-verification-results.json) contain the test results, live-run identifiers and source hashes. The design basis is `.skill-workspace/do-math-reconstruction-20261104-105720/reconstructed.md`, subsequent decisions in conversations `01a1a4bd-154d-7171-b713-07768aebc4a4` and `01a1a67d-46e5-7212-aacc-cd85b5586023`, and the current development conversation.

## Automated tests

The full runtime suite passed **84 tests**. It uses scripted CLI workers, the runtime's actual structural output checker and Git, and a controlled program standing in for Lean. It tests the orchestration and interpretation of explicit outputs without asking a model to invent the test scenario.

The tests cover work selection and occupancy, role scheduling, interrupted work, provider fallback, publication and restart recovery, local and global glossary decisions, record grouping, formal-proof evidence, instruction snapshots and compilation management. Mathematical-state tests distinguish proving a statement from proving its negation. For example, if a recorded implication requires A and not-B, a proof of A and a refutation of B satisfy its premises. A refutation of Q alone does not settle P through Q implies P. Other tests preserve alternative proofs when one supporting argument is withdrawn.

Run the suite from the repository root:

```powershell
python -B -m unittest discover -s .claude/skills/do-math/runtime/tests -v
```

One earlier full run exposed an ordering assumption in a broker test. Windows assigned the same timestamp to several requests, so their file names could determine ingestion order. The test now waits for its intended first request to enter the queue before submitting later requests. It retains the assertions that no more than the configured three later jobs can pass that waiting request and that the request eventually runs.

A separate probe reproduced failure of a status command with a Korean instance path and an inherited ASCII output encoding. Public command JSON now escapes non-ASCII characters, preserving their values when decoded. A regression covers runner status, coordination updates and broker status in that environment.

After the final terminology edit changed generated concern labels and the name of the update field listing comprehensive reviews, the seven context tests and 23 research-state tests passed again. That edit changes presentation and field naming; it does not change scheduling or mathematical-state transitions. The results file distinguishes the full-suite source hashes from the final installed files.

## Actual Codex and Claude launches

Both installed CLIs were launched through the worker command builder with a small, explicitly configured local MCP server. Each test directory also contained instruction markers in `AGENTS.md` and `CLAUDE.md`, and a Claude project hook that would create a marker file if executed.

Both successful probes called the configured tool and wrote its exact result, `MCP_PROBE_OK`, in their own directories. Neither followed the forbidden instruction marker, and the project hook marker was not created. Native transcripts were retained. These checks exercise existing authentication and explicit tool access alongside the worker configuration that excludes personal/project instructions, hooks and memories.

The first Codex probe did not see the configured tool. Inspection showed that quotation marks in a dotted configuration override had become part of the server's name. Supplying the complete `mcp_servers` TOML table fixed the configuration, and the repeated live probe succeeded. The generated table also has a regression check.

These results apply to the installed CLIs and tested local MCP configuration. They do not establish behavior for every future provider release, external-tool transport or centrally managed organizational policy.

## Actual research and Lean verification

A fresh instance researched the proposition “For every natural number n, including zero, n + 0 = n.” It used two concurrent AI sessions, organization after each research publication, and Claude-first reviews with Codex as their alternative. Other roles used the default Codex-first model list. Core Lean 4.32.0 ran through the instance's broker.

This test's initial user conditions asked attempts, explorers and their peers to leave formalization to the formalizer. That made the elementary problem exercise the formalizer handoff as well. It is a condition of this test instance, not a product restriction on attempts or peers.

The run completed **16 sessions across all six roles**: one attempt, two explorations, one formalizer, four peers, four reviews and four organizers. It published four research records and four organization decisions. No session failed. All 16 native conversations were retained without a reported capture limitation.

The final formal record is `r3f9215233b0d40218fe6fcf1532aaed8`. Reviewer session `s8be216c129034e3389ecae40848616c5` submitted fresh build `b31a587b2b06249cdaf93597a70c7444e` to check:

```lean
DoMath.root : ∀ (n : Nat), n + 0 = n
```

The retained compiler output reports that this theorem depends on no axioms. The review's source hashes match the final published candidate files, and its assessment confirms correspondence with the original proposition. The instance reached `formal_proved` and finished its remaining work.

The controlled tests run during the rebuild exercised dependency ordering and cache reuse. That suite did not call the fresh-target build option; its scripted lifecycle used a single-file reviewer compile. The real Lean run confirms a reviewer-owned fresh build, the actual axiom output, final-source identity and the handoff into a published formal result. No new Mathlib research run was performed.

## Follow-up Lean 4.32 module-cache check

A later development probe used the actual broker and Lean 4.32.0 on Windows with two local modules. `Basis.lean` used `module` and `public import Init` and exported `basis : True`; `Target.lean` used `module` and `public import Basis`, proved `target : True` from `basis`, and printed its axioms. The first build compiled both modules successfully and reported no axioms for `target`. A fully cached build was then correctly rejected as independent review evidence because the target had not been compiled freshly.

In that first probe, the next build requested a fresh target compile while reusing the cached `Basis` dependency. That target compile exited with code 1: Lean could not open `Basis.olean.server` in the new build's library directory. The first build had emitted `Basis.olean`, `Basis.olean.private`, `Basis.olean.server` and `Basis.ir`. The probe stopped at its fresh-target success assertion, before the final `audit_formal` call, leaving actual formal-evidence acceptance unchecked at that stage.

The initial failure is retained in the local verification input `임시/do-math_검증_20261105/sources/lean-4.32-observation.json`; `lean-4.32-probe.py` in the same directory contains the reproduction program. Closing this failure requires four actual-compiler outcomes: a successful cold build, rejection of cached-target review evidence, a successful fresh-target build using cached dependencies, and acceptance by the actual formal-evidence checker. A controlled compiler test cannot establish these outcomes.

A separate actual-broker observation, `임시/do-math_검증_20261105/sources/lean-4.32-after-repair.json`, records all four outcomes after the approved round 3 repairs and before that round's commit. With the same Lean 4.32.0 Windows toolchain, the cold build compiled both `Basis` and `Target` successfully and printed that `target` depends on no axioms. A fully cached target was rejected as independent review evidence. The fresh review build reused cached `Basis`, compiled `Target` successfully in job `j509044b15d3444b8ae95f48c572a9553`, and passed the actual `audit_formal` check. This resolves the recorded failure for the tested two-module core Lean path.

The JSON results distinguish the two observations and record the later broker and checker SHA-256 identities separately from the earlier rebuild source hashes. These supplied observations and the reproduction program were inspected for this report update; the probe was not rerun for the update. Their paths identify local inputs, not evidence distributed with a clone. The later success does not establish behavior for every Lean or Mathlib project or repeat the earlier full runtime suite or live research. The earlier results and their source identities retain their original scope.

## Follow-up broker and checker observations

Three later development observations ran actual runtime consumers on controlled inputs instead of compiling with Lean. Each was recorded before and after an approved repair. The observation files and their reproduction programs are local verification inputs in `임시/do-math_검증_20261105/sources/`.

The theorem-name observation called the actual `audit_formal` checker with the existing controlled formal-evidence fixture. Only the theorem name in the printed axiom line varied. With the checker identity recorded in the original rebuild results, output naming `target`, `not_target` or `Namespace.target` was accepted as evidence for the theorem `target`. After the round 3 repairs, the checker accepted only `target`. It rejected the other two because the review compile had not printed the target's axiom dependencies (`formal-name-observation.json`).

The cancellation observation used the actual broker functions and files with a controlled compiler process. Test hooks chose deterministic interleavings around request ingestion. Before the round 5 repairs, a cancellation sent before ingestion was acknowledged but left no final outcome. A cancellation sent after the broker had read the request was acknowledged as made "before the broker read it", yet the job or build still compiled and finished; the build returned 0. A cancellation during a cached restore also ended as a finished build returning 0 (`broker-outcomes-observation.json`). After the round 5 repairs, each of those cancellations ended with status `cancelled` and started no new compile, and each cancelled build returned 4. The cached module row kept its completed outcome. A build whose compiler exited with 1 still finished and returned 1 (`broker-outcomes-after-repair.json`).

The exit-code observation called the actual `report_build` consumer with controlled result records. Each record had a cached dependency with code 0 and a target whose compiler returned 0, 1 or -9. Python reports a process ended by a POSIX signal as a negative return code. Before the round 6 repairs, the successful dependency masked the target's -9, and the build report returned 0 (`exit-code-observation.json`). After those repairs it returned -9, and the results for 0 and 1 were unchanged (`exit-code-after-repair.json`). This checks the consumer with controlled records; it is not a Linux execution or a new Lean compile.

These observations were inspected for this report update; their probes were not rerun for it. The broker identity recorded with the post-repair module-cache observation above predates the round 5 and round 6 broker changes. The JSON results record the broker or checker identity of each observation separately. None of these observations repeats the earlier full runtime suite or the live research.

## Recovery

The live test runner was terminated and restarted while one worker remained active. That worker's recorded host and CLI identities were preserved. The run subsequently finished.

Restarting the completed instance exited normally without changing its publication events or Git history. Its records, assessments, organization decisions and publication events had no uncommitted changes. This checks both continuation of active work and the absence of duplicate publication after completion.

Detailed local evidence is under `.skill-workspace/do-math-development-20261105/`, including `live-research/`, `live-evidence.json`, `live-restart.json`, `completed-restart.json`, isolation probe folders and test logs. This workspace is ignored by Git. Those paths identify evidence in the development workspace, not files included in a clone.

## Documentation

Independent readers receive the actual starting context assembled for one worker role, without the development conversation or other roles' guides. The operator's entry point and operating guide are read together; README is read separately. Each reader explains what it understood, cites the supporting passages and identifies relationships the supplied text leaves unclear. The main author compares those observations with the settled requirements and decides what to revise or retain.

The final worker order is common introduction, role guide, writing guidance, tools and the role's output reference. The common introduction develops the question and the roles before introducing the resources they use. The board, for example, is explained through the risk of repeating unpublished work, then through declarations and their lifetime. Each role guide builds on that foundation and gives its mathematical attitude and responsibilities room to develop before the output contract specifies the handoff.

The final wording uses **instance** for the whole research run and **a session's work** for the contribution later processed by peer and review. Characteristic role guidance emphasizes tenacity and initiative, patient curiosity, independent mathematical engagement, faithful formal construction, exacting fairness and thoughtful organization. Concrete methods support those dispositions with explanations and examples.

The live lifecycle run preceded these final prose and reading-order revisions. The revised documents are checked through independent role-specific readings, and the context tests check their actual assembly and retained references. Static reading checks address what the text communicates; they do not certify research mathematics or guarantee future model behavior.

## Installation and scope

The canonical files in `.claude/skills/do-math/` are compared byte for byte with their copies in `.agents/skills/do-math/`: `SKILL.md` and the sources under `runtime/`, `roles/` and `reference/`. Fresh instances use the new runtime. The old top-level runner, broker and worker documents remain unchanged for an existing research instance that continued running during development.

Execution verification in this rebuild was on Windows with the installed Codex and Claude CLIs and core Lean. The new runtime's Linux process paths were not exercised. The elementary live problem confirms the workflow and evidence handoffs; performance on difficult, sustained mathematical research remains a matter for actual use.
