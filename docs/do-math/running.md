# Running do-math

This guide covers the requirements, what a run does on your machine, starting a run through the skill or by hand, the settings, the runner commands, ending a run, and interruptions and completion. The repository [README](../../README.md) gives a quick start taken from it; the [operating guide](../../.claude/skills/do-math/reference/operations.md) in the skill is the complete reference for every setting and state. Terms such as runner, broker, session host, frontier, standing input, retained work and comprehensive review are defined in the README under "How the research is organized" and "What counts as established".

## Requirements

The runtime needs Python 3.12 or later and Git, and uses only Python's standard library. It needs the Codex CLI, the Claude Code CLI, or both, installed and logged in; it launches them as processes and does not call model APIs directly, so usage is billed or metered however those CLIs are configured, and do-math adds no accounting of its own.

The runtime needs Lean 4 in every case, because the settings name a Lean installation and the broker starts with the runner; it needs Mathlib when the proofs the sessions write will draw on it, which the user judges from the problem at setup. External tools such as scholarly-mcp, a local server for academic literature search, are optional; the `mcp_servers` field of an instance's `settings.json` names the tool servers its sessions may use, and nothing else is available to them beyond the CLIs' built-in tools, which include shell commands and web search.

Development and live verification were done on Windows. The process helpers also support Linux, where they read `/proc`; Linux execution has not been verified in a live run, and macOS is not supported, because process identification is not implemented for it.

## Permissions, caps and outbound traffic

Sessions run unattended with file and command access under your account: Claude Code is launched with permission prompts disabled, and Codex with its approval policy set to never and its sandbox set to full access. Their workspace boundaries are instructions, not an operating-system sandbox, and their model providers receive the material they read, as in ordinary CLI use. A run has no cap on time, on the number of sessions, or on usage, and do-math collects no usage figures; it ends when the root is formally settled and the remaining work has been processed, or when you end it as described below.

do-math itself sends nothing outside your machine: publication means a commit to the instance's local Git repository, and the Zenodo deposit of the first run was made by hand. The outbound traffic is the CLIs' own, to their model providers and to the web tools the sessions use.

## Starting through the skill

To install, clone this repository. The skill is the folder `.claude/skills/do-math`, and its mirror for Codex is `.agents/skills/do-math`. From Claude Code or Codex started in the repository, ask the do-math skill to start research on a proposition. The conversation that handles that request is the operator; it prepares the statement and settings, launches the detached runner and reports where the work lives. The [operator entry point](../../.claude/skills/do-math/SKILL.md) and the [operating guide](../../.claude/skills/do-math/reference/operations.md) explain the full path.

## Starting by hand

For a manual launch, write a UTF-8 `root.md` containing the exact proposition, for example:

```text
For every natural number n, including zero, n + 0 = n.
```

Prepare `settings.json` with your actual executable paths. The operating guide lists every field with its default. This minimal file names the Lean installation, with the command that compiles a file and the command that prints the Lean version, and keeps the default models and scheduling:

```json
{
  "lean": {
    "command": ["C:/tools/lean.exe"],
    "version_command": ["C:/tools/lean.exe", "--version"]
  }
}
```

The defaults are eight concurrent sessions (`max_sessions`), attempts and explorers launched at least 180 seconds apart (`launch_interval`), an explorer requested each time an attempt is launched (`explore_every`; the request is granted when a question is free and the interval has passed), an organizer after four research publications (`organizer_every_records`), and up to three reconsideration turns before a session may end (`max_end_resumptions`).

The `models` list is the ordered model preference for every role, and an entry under `roles` replaces it for that role; each entry names a model as `provider/model` with the CLI's reasoning-effort setting, of which `xhigh` is the highest. The default `models` list puts Codex `gpt-6.1-sol` first and Claude `opus` second, and the default `roles` entries for peer and review reverse that order. With only Claude Code installed, give the common list and the two role entries Claude models only, as here with the Opus alias the Claude CLI resolves:

```json
{
  "models": [{"model": "claude/opus", "effort": "xhigh"}],
  "roles": {
    "peer": [{"model": "claude/opus", "effort": "xhigh"}],
    "review": [{"model": "claude/opus", "effort": "xhigh"}]
  },
  "lean": {
    "command": ["C:/tools/lean.exe"],
    "version_command": ["C:/tools/lean.exe", "--version"]
  }
}
```

To use Mathlib, set `lean.command` to your Lake executable followed by `env` and `lean`, and `lean.cwd` to a Mathlib project directory that has already been built, as the operating guide shows; a cold compile against Mathlib took about seven minutes and about a gigabyte of memory on the development machine, which is why compiles go through the broker. All sessions request a one-million-token context from their CLI; do-math only requests it, and the CLI and the account decide what the session actually gets. The allowed Lean axioms default to `propext`, `Classical.choice` and `Quot.sound`; the list can be extended in the settings, and `sorryAx` is never allowed.

`init` creates the instance at a new path, which should lie outside this repository or under its `.skill-workspace/` directory, which Git ignores, so that the instance's own repository is not nested in a tracked tree. `start` then launches the runner:

```powershell
$skill = 'C:/path/to/do-math/.claude/skills/do-math'
$instance = 'C:/research/add-zero'
python "$skill/runtime/runner.py" init $instance --root C:/research-input/root.md --settings C:/research-input/settings.json
python "$skill/runtime/runner.py" start $instance
python "$skill/runtime/runner.py" status $instance
```

Standing inputs, such as the language of the records or limits on methods, are plain text files submitted with `input --file <file>`, before `start` when they should reach every session. They apply only to sessions launched after them and accumulate; a later input that changes an earlier one must say which it changes. Changing the root's proposition requires a new instance.

`start` launches the runner as a detached process, waits until the runner has written the record that confirms it is up, and returns its process ID and the paths of its log files under the instance's `runner/` directory. The runner then continues after the terminal or operator conversation ends, and `knowledge/` is updated with every publication.

## Commands

All commands have the form `python <skill>/runtime/runner.py <command> <instance> ...`.

| Command | Purpose |
|---|---|
| `start` | Launch the detached runner when none is alive, including after a crash or reboot; existing sessions and unfinished publications are recovered. |
| `run` | Run the runner in the foreground for observation. |
| `status` | Read the root state, runner liveness, sessions, pending work, provider and model blocks, and the broker state. |
| `stop` / `resume` | Stop or resume the launching of new sessions, including peers and reviews; the runner stays alive and running sessions continue. If the runner process has ended in the meantime, run `resume` and then `start`. |
| `reconsider-attempts` | Launch one attempt to look again for available work after attempts have reported, in a state that `status` shows under `attempt_dispatch`, that every unresolved node is occupied; that report otherwise pauses attempt launches. |
| `input --file <file>` | Supply a standing input to future sessions. |
| `review --record <id>` / `review --node <id>` | Request a comprehensive review of published evidence. |
| `organize` | Request organization of the currently unorganized records. |
| `questions --file <file>` | Place questions on the frontier from a JSON file, without peer or review; the operating guide gives the format. |
| `kill-session <id>` | End the identified session's CLI process; session IDs are in the `status` output. Retained research is still processed once launching is allowed. |
| `render` | Rebuild the knowledge views when no runner process is alive. |
| `restart-broker` | Replace the Lean broker after an environment change, with launching stopped. |

## Ending a run

To end a run before the root is settled, use `stop`, so that no peer or review follows what you end next; then `kill-session` for each running session, which also ends its session host; then end the runner process whose ID is in the instance's `runner/process.json`, with `Stop-Process` on Windows or `kill` on Linux. The Lean broker is a separate process whose ID is in `runner/lean/process.json`; it exits on its own when the instance's sessions and follow-up work have finished and no compile is queued or running, and it can be ended the same way.

## Interruptions and completion

A session interrupted by a provider's usage limit or another failure leaves its retained work for a peer. When a provider refuses a launch because of a usage limit, launches through that provider are blocked until the limit resets; a refusal specific to one model blocks only that model, and the configured alternatives serve later launches. Interrupted peers, reviews and organizers are replaced by fresh sessions that receive the partial work.

Formal settlement of the root stops new attempts and explorers; existing sessions finish, their peers and reviews, formalizations and organizations still launch as their inputs become ready, and the runner finishes when that work has ended. The [operating guide](../../.claude/skills/do-math/reference/operations.md) explains states, failures, fallback and Lean environment changes; the [Lean guide](../../.claude/skills/do-math/reference/lean.md) explains the broker's commands, memory estimates and settings.
