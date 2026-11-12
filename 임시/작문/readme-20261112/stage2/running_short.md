## Running do-math

### Requirements and what a run does on your machine

The runtime needs Python 3.12 or later and Git, and uses only Python's standard library. It needs the Codex CLI, the Claude Code CLI, or both, installed and logged in; it launches them as processes and does not call model APIs directly, so usage is billed or metered however those CLIs are configured. It needs Lean 4 in every case and Mathlib when the proofs will draw on it. Development and live verification were done on Windows; Linux is supported by the process helpers but has not been verified in a live run, and macOS is not supported.

Sessions run unattended with file and command access under your account: Claude Code is launched with permission prompts disabled, and Codex with its approval policy set to never and its sandbox set to full access. Their workspace boundaries are instructions, not an operating-system sandbox, and their model providers receive the material they read. A run has no cap on time, on the number of sessions, or on usage, and do-math collects no usage figures. do-math itself sends nothing outside your machine; publication is a commit to the instance's local Git repository, and the outbound traffic is the CLIs' own.

### Quick start

Clone this repository. From Claude Code or Codex started in the repository, ask the do-math skill to start research on a proposition; the conversation that handles the request is the operator, and it prepares the statement and settings, launches the detached runner and reports where the work lives. The skill is the folder `.claude/skills/do-math`, with its mirror for Codex at `.agents/skills/do-math`.

To launch by hand instead, write a UTF-8 `root.md` containing the exact proposition and a `settings.json` that names your Lean installation, with the command that compiles a file and the command that prints the Lean version:

```json
{
  "lean": {
    "command": ["C:/tools/lean.exe"],
    "version_command": ["C:/tools/lean.exe", "--version"]
  }
}
```

This keeps the default models, which put Codex first and Claude second for every role and the reverse for peer and review; with only Claude Code installed, give the `models` list and the `roles` entries for peer and review Claude models only, as the running guide shows.

Then create the instance at a path outside this repository, or under its Git-ignored `.skill-workspace/` directory, and start the runner:

```powershell
$skill = 'C:/path/to/do-math/.claude/skills/do-math'
$instance = 'C:/research/add-zero'
python "$skill/runtime/runner.py" init $instance --root C:/research-input/root.md --settings C:/research-input/settings.json
python "$skill/runtime/runner.py" start $instance
python "$skill/runtime/runner.py" status $instance
```

The runner continues after the terminal or operator conversation ends, and `knowledge/` is updated with every publication. The [running guide](docs/do-math/running.md) covers the model and scheduling settings, Mathlib, the allowed Lean axioms, standing inputs, every runner command, how to end a run, and what happens on interruption and completion; the [operating guide](.claude/skills/do-math/reference/operations.md) in the skill is the complete reference for every setting and state.
