# Operating a research instance

This guide continues the operator's entry point, [SKILL.md](../SKILL.md). Use it when preparing an instance or acting on an existing run. It explains the files the operator supplies, how to confirm a launch, where to read results, and what the operating commands change.

The runner manages the research sessions after launch. Your commands affect that running process or supply inputs it will use. Understanding the difference matters when operating a run: stopping new dispatch leaves existing sessions alive, and delivering a user input makes it available to future launches without changing the instructions of sessions already underway.

## Prepare the statement and environment

The root file contains the mathematical proposition to settle, with its objects, assumptions, domains and quantifiers defined. A proof of either that proposition or its negation settles the node. Final completion requires an independently reviewed Lean solution with the intended correspondence. Keep the root statement fixed for the lifetime of the instance; changing its mathematics requires a new instance.

Put standing instructions, such as the language of the records or limits on permitted methods, in a separate input file. Submit it before starting the runner to make it part of every initial session's context. Later inputs affect only sessions launched after submission. They do not rewrite existing sessions' instructions or their saved contexts.

The runner needs Python 3.12 or later, Git, authenticated Codex and/or Claude native executables, and a Lean environment. The default models are `codex/gpt-6.1-sol` at `xhigh`, followed by `claude/opus` at `xhigh`. These are ordered alternatives for each role. Defaults are eight concurrent AI sessions, attempt launches at least three minutes apart, exploration requested every three attempt dispatches, and organization after four research publications.

An example settings file is:

```json
{
  "schema": 1,
  "max_sessions": 8,
  "explore_every": 3,
  "organizer_every_records": 4,
  "attempt_launch_interval": 180,
  "models": [
    {"model": "codex/gpt-6.1-sol", "effort": "xhigh"},
    {"model": "claude/opus", "effort": "xhigh"}
  ],
  "roles": {},
  "cli": {"codex": "C:/tools/codex.exe", "claude": "C:/tools/claude.exe"},
  "mcp_servers": {},
  "retry_seconds": 60,
  "retry_max_seconds": 1800,
  "lean": {
    "command": ["C:/tools/lean.exe"],
    "version_command": ["C:/tools/lean.exe", "--version"],
    "cwd": null,
    "env": {},
    "cache_epoch": "initial",
    "allowed_axioms": ["propext", "Classical.choice", "Quot.sound"]
  }
}
```

Replace the executable paths with the actual installations. A role-specific ordered model list under `roles`, such as `"review": [{"model": "claude/opus", "effort": "xhigh"}]`, replaces the common list for that role. An omitted setting receives its default. An unrecognized key, such as a misspelling or a setting carried over from the earlier do-math runtime, is rejected by name rather than ignored, because ignoring it would leave the default in force without notice. The runner checks structure; actual login and model availability are confirmed by execution.

To use Mathlib, configure `lean.command` as `["<lake executable>", "env", "lean"]`, its version command with `"--version"` appended, and `cwd` as the Mathlib project. Supply any necessary PATH value through `lean.env`; JSON does not expand shell variables. The broker handles compilation and dependency builds. [Lean](lean.md) explains resource settings and estimates. When several instances share a machine, set their broker memory budgets explicitly rather than letting each derive a budget for the whole host.

Only explicitly configured external tools enter worker sessions. `mcp_servers` maps server names to configuration objects. A local server uses `command`, `args`, and optional `env`; an HTTP server uses `url` and the provider's supported transport configuration. Configure the tool capabilities the research needs, such as scholarly-mcp, independently from personal instructions and hooks. Authentication remains with the installed CLIs. Worker launches disable personal/project instruction discovery, skills, hooks and memories; all do-math guides and user conditions are supplied explicitly.

## Create and start

Choose a path that does not exist, outside the development repository or in an ignored directory such as `.skill-workspace/`. The instance has its own Git repository. Keep preparation files outside that path.

```powershell
$skill = 'C:/math/.claude/skills/do-math' # replace with the installed skill folder
$instance = 'C:/research/my-problem'     # a new path
python "$skill/runtime/runner.py" init $instance --root C:/research-input/root.md --settings C:/research-input/settings.json
python "$skill/runtime/runner.py" input $instance --file C:/research-input/conditions.md
python "$skill/runtime/runner.py" start $instance
python "$skill/runtime/runner.py" status $instance
```

The `input` command is optional when there are no additional standing conditions. `init` creates the statement, configuration, empty knowledge views, session directories and initial Git commit. A failed initialization may leave a partial directory; fix the cause and use a new path. `start` launches a detached runner and returns its PID and new stdout/stderr paths after confirming this launch's readiness token. Read those logs and `status` to confirm the actual launch.

The caller can then end its conversation. The runner and session hosts continue independently. If readiness is not confirmed within ten seconds, inspect the named logs and liveness before retrying; a wait timeout alone does not show that the child died.

## Read progress and results

Begin with `knowledge/index.md`. It contains records the organizer selected as common orientation for new sessions (shared context), descriptions of grouped records (modules), and new publications awaiting placement (unfiled arrivals). Open a record's exposition and its review to understand what was established. The original description remains visible beside the review's short assessment. Later findings appear separately, with links to the review that supplies them.

`knowledge/frontier.md` shows exact node statements, current informal/formal outcomes, reviewed relations and concerns. `knowledge/glossary.md` supplies the full current shared vocabulary. `knowledge/board.md` shows the sections producing work holds, its processing stages and the node leases; a session's declaration lists the sections it has registered. The status command reads those declarations directly, including changes since the board file was last rendered. `knowledge/state.json` is a structured projection of published evidence for detailed inspection.

Unresolved means that no accepted proof or refutation has settled a node informally. An informally proved or refuted node is settled as mathematics and awaits the remaining Lean assurance. A formally proved or refuted node has that independently reviewed assurance. Opposing accepted outcomes are shown as contested for review. A contested node is not treated as formally settled for completion; the opposing evidence must be resolved.

`status` returns the root's current state, whether the runner has finished, active and pending jobs, the board, provider/model blocks and the Lean broker state. A successful status command means the query succeeded. A formal root and a finished runner are different states: after formal completion, new attempts and explorations stop, while existing sessions continue and the runner still prepares their peer and review stages, ready formalizations and due organization batches. If later review removes the root's last formal solution before exit, the same scheduler resumes research.

## Commands

Every command below is `python <skill>/runtime/runner.py <command> <instance> ...`.

| Command | Effect |
|---|---|
| `start` | Launch or restart the detached runner, checking its new readiness record. |
| `run` | Run in the foreground for observation; remains attached until the runner exits. |
| `status` | Read current liveness, mathematical state and operational queues. |
| `stop` | Stop new dispatch. Running sessions finish their current stage; queued follow-ups wait. |
| `resume` | Remove the dispatch stop. If the runner is not alive, also use `start`. |
| `input --file <file>` | Preserve standing information for future launches. It does not notify running sessions of new instructions. |
| `review --record <id>` or `review --node <id>` | Request a comprehensive assessment of published evidence; targets may be repeated. `--concern <id>` and `--reason <text>` can identify the issue. |
| `organize` | Request organization of the currently unprocessed research records. |
| `kill-session <session-id>` | Terminate the identified CLI process after confirming its OS creation identity. Retained producing work still goes to peer. |
| `render` | Rebuild the knowledge views while the runner is off. |
| `restart-broker` | With dispatch stopped and active sessions and compiles finished, replace the broker after an environment change. |

Use status to identify the intended session before termination. The command targets that CLI, not arbitrary child processes. The broker cancels its compiles after observing that the session has ended. Other computations must be interpreted from their retained outputs and actual process state.

## Waiting, fallback and recovery

When a producing session ends, its retained material creates peer work. A structurally usable peer candidate creates review work. An accepted informal solution creates formalizer work when the other node results needed by its chosen argument have independently validated Lean proofs available. These results are its formal dependencies. New research publications create organizer work when the configured number of unprocessed publications is reached. Available capacity and an available configured model permit each launch.

Priority is review, peer, formalizer, organizer, eligible explore, then attempt. Fresh attempts require free capacity, no waiting peer or review, an unresolved node that no pipeline holds whole and no session is waiting to lease, and at least `attempt_launch_interval` seconds since the previous attempt launch. The spacing gives each new attempt time to take a lease before the next one reads the board. An infrastructure-blocked review remains waiting under this rule. Running sessions are not preempted when higher-priority work appears.

Exploration is eligible when its request flag is true and no exploration cycle is present. A cycle includes the explorer, its peer and its review. Every third attempt dispatch sets the flag by default; unused capacity also sets it when no unresolved node is available to a new attempt, including when all nodes are informally solved. Repeated triggers coalesce into one request. Launching an explorer clears the flag; it does not reset the attempt counter.

A typed provider usage refusal blocks that provider until its known reset, or a configured backoff when the reset is unavailable. Model-specific refusals block that model. A new launch uses the first available alternative in its role's list. If all are unavailable, the job remains pending. A producer interrupted after doing work ends and proceeds to peer; it is not silently resumed under another model. A session that failed before leaving any research material can be retried as an operational launch.

Interrupted peers, reviewers and organizers receive fresh replacement sessions with their partial material and the error. When a completed session's output fails its structural check, the affected job waits for an exponential retry delay, up to `retry_max_seconds`. That output failure does not block the model for other jobs or change their configured model preference. Actual provider/model refusals and operational launch failures retain their availability handling, so a configured alternative can be used while the affected service is unavailable. Status exposes the pending job's error and retry time as well as availability blocks. Repair broken paths, login or configuration when necessary. Mathematical uncertainty and incomplete formalization are handled through records and reviews, not inferred from process failure.

A successful session launched after an availability block's deadline clears that provider's or model's old backoff history. A later isolated refusal therefore begins with the initial delay. A session that was already in flight before a newer block cannot clear it merely by finishing successfully; the newer refusal still governs new launches.

If a frozen candidate changes during review, retrying the same damaged files cannot complete that review. The runner preserves the damaged candidate and compares the peer's retained output with the hashes fixed at review assignment. Matching output is copied to a new candidate location for a fresh review under the same hashes. If those bytes are unavailable, a replacement peer receives the original research and earlier peer work, develops a new candidate, and sends it through independent review. An assessment of the damaged candidate never authorizes publication of the replacement.

After a runner crash or machine reboot, use `start` on the same instance. The runner identifies existing processes by PID and creation identity, follows those still alive, and collects ended work. Publication uses a saved identity, staging directory and Git commit; restarting completes the same publication and its follow-ups without creating another record. Do not delete locks or edit runner state to force recovery. Use shells at the same privilege level on Windows, because process-query access is part of liveness detection.

Each launch retains its guides, references, user inputs, settings and research snapshot. The available conversation and artifacts are retained for each producing session. The work of one producing session finishes processing after its peer has prepared a candidate and review has either led to publication or decided there is no useful record to publish. The runner launches a separate archiver process to compress each associated session's work/ into work.tar.xz in that session directory. It verifies file names and hashes before removing work/. A standalone review or organizer's work directory becomes eligible when its own job completes. Output files, context and retained conversations remain available; restore archived work with an xz-capable tar reader when needed. The public record contains the evidence later researchers need. Archived originals remain recoverable for the operator and for a designated reviewer examining the relevant published record, within the scope described in the review guide.

Changing Lean or its libraries requires a new `lean.cache_epoch`. Stop new dispatch and let active sessions and compile jobs finish. Update the Lean configuration in the instance's own `settings.json`, including a new `cache_epoch`, then run `restart-broker` and resume. This prevents a module cache identified by an old environment from being treated as evidence for a changed installation.
