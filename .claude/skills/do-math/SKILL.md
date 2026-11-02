---
name: do-math
description: Starts an unattended run that carries a mathematical goal through plan, research, exploration, peer and independent review sessions, and performs status queries, stops, inputs, termination of individual sessions and restarts. Used from Claude Code and Codex conversations.
---

# Using do-math

This document is the entry point for the session that converses with the user. When the user entrusts a mathematical goal, prepare a research instance for that one goal and start the runner as a detached process. After confirming the launch, tell the user the instance location and end the conversation. From then on, plan, research, exploration and review sessions carry the research on, reading the published knowledge, until the goal is achieved. For a query about existing research or an operating request, perform the commands below on the instance concerned.

The primary deliverable of the research is a mathematical exposition a person can understand. Lean formal results support the exposition, and computations, counterexamples, literature searches, partial results, failed approaches and open questions are also used by later research. Independent review distinguishes Lean acceptance, agreement between the exposition and Lean, and goal achievement. A manuscript for submission, a package of material for external reproduction and responses to external refereeing after the goal is achieved are outside the scope of this run.

What the user decides is the goal, the requirements and the permissions. Preserve the conditions already received, and let the AI decide what is to be judged within that scope, such as task decomposition, methods and model choice. Do not create a separate approval step for preparation work where a meaningful default choice is possible. Where only the user can decide the meaning of the goal or a needed permission, ask clearly about the missing content and its effect on the research. Do not record a method the AI chose as a user requirement.

## Preparing a new run

1. Take the actual folder containing this `SKILL.md` as `$skill` and read the preparation and launch contract of [RUNTIME.md](RUNTIME.md). Confirm Python 3.12 or later, Git, the installation paths of the CLIs to use and the existing login and model settings. PowerShell's `Get-Command python, git, codex, claude -ErrorAction SilentlyContinue` can find the paths, and if they are not on PATH, read the known installation locations. For the CLIs it is convenient to use the absolute path of the native executable. Use the settings and tools of the current installation as they are.
2. Write the user's goal, requirements and permissions in a nonempty UTF-8 `goal.md`. Convey in the goal what must be achieved for it to end, but let the plan session decide the research strategy and the detailed tasks. Keep the prepared goal and settings files outside the instance.
   A goal that demands a proof or a disproof is by default judged achieved only when there is a Lean proof. A Lean theorem within the allowed axioms must be accepted in an independent review, and its exposition must be judged to be the same mathematics as Lean. The exact criteria are in 'Formal proof required for goal achievement' of [common.md](common.md). If the user says an informal proof suffices or wants a different assurance level, write that in `goal.md`. If the goal proposition looks hard to state or prove in the Lean environment to be configured (for example, a needed library is missing), tell the user that situation and its effect before starting and fix the assurance level.
3. Write a UTF-8 `settings.json`. The JSON example and explanation in section 1 of [protocol.md](protocol.md) are the authoritative definition of the fields. If the user does not specify a concurrency cap separately, use that section's default. Within the overall concurrent-session cap, only one plan runs at a time. Choose the usable models and paths at that time. Passing the settings format does not mean that login or actual model access succeeds.
4. Choose an instance path that **does not exist yet**. Put it outside the repository or under `.skill-workspace/`, which is excluded from the parent Git. If it is inside the repository, confirm the exclusion with `git check-ignore` or the like. `init` creates the instance's own `.git/`, and this Git must not mix with the main repository's Git.

If a plan specifies a model or effort for a research, exploration, additional peer, additional review or goal-review request, only that field overrides the defaults and the reason is left. The plan itself and automatic peers and bundle reviews use each category's defaults. If existing settings have no peer defaults, the review defaults are inherited. The per-CLI effort values and the authentication and unattended invocation follow [CLI.md](CLI.md). Sessions are instructed to write only in their own folders, and the CLIs' unattended permission options do not provide OS-level folder isolation.

If Mathlib is needed, set `lean.command` to `["actual path of lake.exe", "env", "lean"]` and `cwd` to the absolute path of the Mathlib project to use. `version_command` may also be set to `["actual path of lake.exe", "env", "lean", "--version"]` so that the version is obtained in the same environment. Put the actual Lean bin path together with the existing PATH into the `env.PATH` needed. `$env:PATH` inside JSON is not expanded, so write the actual string when preparing. A goal that does not need Mathlib can use the installed core Lean directly.

Sessions do not run this command themselves. Every compile in an instance goes through the instance's Lean broker, a process the runner keeps alive, which runs the command on the sessions' behalf and keeps the memory of all running compiles within one budget. The `lean` block accepts further, optional keys for the broker, listed under 'Settings' in [LEAN.md](LEAN.md); their defaults are derived from the machine, so leave them out unless the user names a limit. If the user does name one, for instance how much memory Lean may take in total, or that the machine is shared with another instance, write `memory_budget_mb` and, if needed, `cpu_threads_budget` explicitly.

Below is a **path layout example** for Windows. Run it after replacing the skill path you are reading now and the prepared file and new instance paths. If the example directory already exists, choose a new name.

```powershell
$skill = 'C:/math/.claude/skills/do-math'
$instance = 'C:/math/.skill-workspace/do-math/add-zero'
$goalFile = 'C:/math/.skill-workspace/do-math-inputs/add-zero/goal.md'
$settingsFile = 'C:/math/.skill-workspace/do-math-inputs/add-zero/settings.json'
python "$skill/runner.py" init $instance --goal $goalFile --settings $settingsFile
```

The goal of the small starting example is "Prove in Lean that n + 0 = n for every natural number n, and write an exposition faithful to that proof. Natural numbers include 0." With the default model example of protocol.md, Codex and Claude take part in different categories. If there is an actual user goal, record that goal.

`init` succeeds with exit code 0 and a JSON with the instance path. It creates the goal and settings texts, `knowledge/`, `sessions/`, `runner/`, `control/inputs/` and the instance's own Git. If it fails, resolve the error. Do not reuse or overwrite a folder left over from creation as if it were existing research; prepare at a new path.

## Confirming the detached launch and reporting the location

```powershell
$launchText = python "$skill/runner.py" start $instance
if ($LASTEXITCODE -ne 0) { throw 'Check the launch error and the log paths returned.' }
$launch = $launchText | ConvertFrom-Json
Get-Content -LiteralPath $launch.stdout -Encoding utf8
python "$skill/runner.py" status $instance
```

On Windows, `start` launches a detached runner without a window. Before returning, it confirms the start log carrying the token of **this launch** and the PID and OS creation identity. Keep the `pid`, `stdout`, `stderr` and `instance` of the returned JSON, and confirm the `started` record in the new stdout and `status.runner_alive`. Do not judge the success of this launch from old logs or a PID alone. If an already completed instance exited soon, confirm the start record together with `state.complete`.

Tell the user the absolute path of the instance, the runner PID, the path of the new start log, the current running and waiting state, and `<instance>/knowledge/`, the location of the published results, and end the conversation. There is no need to query repeatedly or keep the calling conversation open until the research is complete. `run` is an observation command that does not return until exit, so use `start` on this start path.

If the launch confirmation does not finish within 10 seconds, first read the new logs named in the error and `status`. Do not decide from the confirmation timeout alone that the child died and launch again. Handle settings, document and Git errors or an instance already running by reading stderr. Exit code 0 from `status` is a successful query, not a verdict that the research succeeded.

## Reading progress and results

The list of published records starts at `<instance>/knowledge/index.md`, the general module of the index. Read the current state of the research in the last plan's research status linked from the preamble, and the definitions of the mathematical objects and symbols the research shares in the global glossary of the same preamble; the names a single record uses internally are in that record's `glossary-local.md`. The preamble also links the latest plan record and lists the other modules the last plan declared, each rendered as `knowledge/index/<name>.md` with a description of what it holds. Choose the records you need by title and summary and go down to the linked `output.json`, exposition and current reviews. The runner updates all index files on publication, review and supersession and rebuilds them on restart. To rebuild only the index while the runner is off, run `python "$skill/runner.py" index $instance`.

```powershell
python "$skill/runner.py" status $instance
```

`runner_alive` shows whether the runner is alive now, and `dispatch_blocks` the conditions that block new dispatch. `state.sessions` holds the category, model, status and request, and `state.requests` holds all posted requests with their `status` (`pending` undispatched, `assigned` assigned, `finished` integration complete, `failed` failed). `lean` shows the Lean broker: whether it is alive, the memory and thread budgets it is using, the Lean version, and the compiles that are queued and running, each with its estimate and its measured memory. If a user asks why a session is waiting on Lean, this is where the answer is; `python "$skill/lean_broker.py" status $instance` prints the same in more detail. If the runner is dead, the saved session states are the values at the time of the last collection. Read the meaning of the fields and events in the state table of [RUNTIME.md](RUNTIME.md).

Published results start at `knowledge/<record ID>/output.json`. Read the exposition pointed to by a research record's `results[].exposition`, its `verification` and the `lean.sources` concerned, and also confirm `failed_attempts` and `open_questions`. Read the independent judgment in the standalone review that points to the research with target.record or in the bundle review that points to it with target.work. A bundle review also judges the peer response of target.peer. Confirm the result's source and the actual scope of the verdict. Having been published means having passed the structure-and-reference check; mathematical establishment is judged by the reviews. An unreviewed result is the author's claim, and if the current reviews conflict it is not used as an established result. `category: "explore"` is an exploration, and `peer` is a peer response that read and worked a published work independently. Both records are unreviewed at the time of publication. Research records and explorations get an automatic peer, and after the peer a review that sees the work and the peer together. When reading as mathematical evidence, confirm the review that designated the claim and scope concerned.

`supersedes` supersedes the whole existing record. Read the body at the end of the supersession chain and the history needed, and if the branches diverge, read both. The reviews of old research are not passed on to new research automatically. The detailed reading rules are in 'Judging published knowledge' of [common.md](common.md) and section 3 of [protocol.md](protocol.md).

If `state.complete` is a record ID, read the grounds of achievement in the goal review's `goal.verdict` and `goal.reason` in `knowledge/<that ID>/output.json`. The `achieved` of a re-checked and integrated goal review is the completion signal. After completion, no new plans or automatic reviews are dispatched either, and after the sessions already running have their finished outputs checked and integrated, the runner exits. Distinguish the completion verdict from the running sessions still remaining when telling the user.

## Stop, input and usage-limit wait

| User request | Command to run and follow-up action |
|---|---|
| Stop new dispatch | `python "$skill/runner.py" stop $instance` — creates `control/STOP`. Existing sessions keep running and are exited, checked and integrated. |
| Release the stop | `python "$skill/runner.py" resume $instance` — removes only STOP. Confirm the other wait conditions and the runner's liveness in `status`. If it is off, `start`. |
| Deliver information, a request or an answer | Write the text as a nonempty UTF-8 file and run `python "$skill/runner.py" input $instance --file 'C:/research-input/answer.txt'`. Replace the path with the actual file. Keep the returned input path. |

Inputs are preserved under unique names in `control/inputs/` and delivered by the runner as the `user_input` event of the next plan. Command success is successful delivery of the file; it does not mean the plan has already read it. An external-input wait is released by reading the needed answer and the reason in `state.wait.needed/reason` and entering the input in the way above. The runner stays alive during the wait, so no further launch is needed while it is alive. If it is off, enter the input and `start`. The processing state can be seen in `state.seen_inputs`, `events` and the input of the plan concerned.

Under a provider usage limit, new dispatch of all categories stops until `state.limit_until`. The value is UTC Unix seconds; if the session's `limit.source` is `provider`, it is the provider's reset time, and if `fallback`, the processing time plus `limit_wait_seconds`. The runner stays alive and waits, and continues the exit and output processing of sessions already started. A finished session is not restarted as it is; later plans decide whether to make a new request.

If `dispatch_blocks` contains `halted`, plan sessions failed consecutively and the runner stopped new dispatch. Confirm the cause in `state.halted.reason` and the tails of `sessions/<ID>/cli.stdout.jsonl` and `cli.stderr.log` of the failed plan sessions. Expired login, or a wrong model name or CLI path in the settings, are common causes. After fixing the cause, confirm the runner's liveness with `status`. If it is still alive, wait for the remaining sessions to exit and be integrated, and after the runner exits, restarting with `start` releases the halt. Since the runner exits by itself once all remaining sessions have finished, `runner_alive` being false is not an anomaly.

STOP, external input, usage limit, halt (`halted`) and completion are separate conditions that may overlap. An input releases the external-input wait, `resume` releases STOP, a limit waits for its expiry, and `halted` is released by a restart. The complete state is not released by an input or by `resume`. If a separate run is requested after the goal is achieved, prepare a new instance.

## Terminating one stuck session

Session run time has no cap. Read the category, model, `started_at` and request in `state.sessions` of `status` to identify the session ID that matches the user's request. The request's instructions can be read in `state.requests[request key].task`. A plan that receives events has `request: null`, and its instructions and events are in its own `sessions/<ID>/input.json`.

```powershell
$sessionId = 's0123456789abcdef0123456789abcdef' # replace with the actual queried ID
python "$skill/runner.py" kill-session $instance $sessionId
python "$skill/runner.py" status $instance
```

The command confirms the CLI PID and OS creation identity of the latest `sessions/<ID>/process.json` on the same handle and terminates **that one CLI**. It is not a command that terminates all descendant processes. The session's Lean compiles are the one exception, and not by this command's doing: they are jobs of the Lean broker, and the broker cancels them once it sees that the session is dead. If the CLI has not been launched yet and there is no information, read the error and confirm the current state again.

The runner judges forced and abnormal exits by the same official check as a normal exit. If the remaining output passes, it is integrated into the published knowledge and Git; if there is no output or it fails, a failure event is handed to the next plan. If the runner is off, continue this processing with `start`. If the request is also to block new dispatch, apply `stop` separately.

## Restarting the runner

If the runner dies or the PC reboots, confirm with `status` in the user's operating conversation and run `python "$skill/runner.py" start $instance` on the same instance. Confirm the new PID and start record as above and report the location. No automatic restart watchdog service is kept.

A restarted runner confirms the actual process liveness of the recorded sessions. If one is alive it waits; if it is dead, it officially checks the remaining output and integrates it or handles it as a failure. It does not relaunch a session that has exited. Undispatched requests and undelivered events are processed in continuation. The settings the runner uses are read at launch. The `lean` settings are read by the Lean broker, which also picks up changes to them while it runs. A restarted runner adopts a broker it finds alive and starts one if none is. The single-runner lock is managed by the OS, so do not restart by deleting `runner/lock` or editing the state files.

## Documents a running session reads

The runner's launch prompt tells the session its own session folder, `input.json` and the official check argv. `input.json.context.common` is [common.md](common.md), [protocol.md](protocol.md) and the instance's `goal.md`, and `context.category` is one of [plan.md](plan.md), [research.md](research.md), [explore.md](explore.md), [peer.md](peer.md), [review.md](review.md). The task-specific elements are the instructions and references of `task`, and the plan's events, the research's supersession intent, or the review target. An exploration receives only instructions and references.

A plan reclaims the existing requests and the failed original tasks according to 'Unfinished requests and events a plan reads' of [RUNTIME.md](RUNTIME.md). A review judges by the published `knowledge/` and `task.target`, and does not accept the author's folder or logs as evidence. A session writes its whole published output in its own `output/`, confirms the format and references with `python <skill>/check.py <own session folder>`, and finishes by itself. The runner performs the same check again regardless of the manner of exit.
