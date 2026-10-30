# do-math

do-math runs long, unattended math research with Claude Code and Codex. You give it one mathematical goal, and a Python runner keeps launching planning, research, exploration, peer and review sessions until an independent review judges the goal achieved. A small example goal is: "Prove in Lean that n + 0 = n for every natural number n, and write an explanation faithful to that proof."

This repository holds do-math, the Claude Code skills I use to develop and operate it, and standalone tools I built alongside it.

This README and the roadmap are in English, but most of the detailed documentation they link to is in Korean; those links are marked (Korean). Porting it to English is planned.

## What it does

- **Five session roles.** A plan session decides what to work on next. Research sessions attack an assigned mathematical question; explore sessions instead get familiar with the problem and widen the understanding of it, looking for unexpected connections. A peer session then works through each finished output (everything one research or explore session publishes) as an independent fellow researcher. A review session, independent of both the author and the peer, judges what the work and the peer's response actually establish and which results later sessions may use. A review session is also what finally judges whether the goal has been achieved. Peer and review sessions receive only the published records and their own task, never the author's session folder or logs.
- **A shared knowledge base per research goal.** Each goal runs in its own *research instance*: a folder, with its own Git repository, that holds the goal, the settings, every session's records and the results. Each research instance keeps the records its sessions publish, an index of those records, and a glossary that fixes the objects and notation the research uses. All sessions of the instance read them; nothing is published outside the instance.
- **Formal proof by default.** A goal that asks for a proof or disproof counts as achieved only when a Lean theorem within the allowed axioms passes independent review, and the review judges the written explanation to be the same mathematics as the Lean proof. The allowed axioms are defined in [common.md](.claude/skills/do-math/common.md) (Korean).
- **Restart-safe.** If the runner or the machine stops, running the runner's `start` command again (see [Running do-math](#running-do-math)) resumes the instance. The runner checks recorded sessions by process ID and OS creation time, processes what they left behind, and never relaunches a finished session.
- **Official CLIs only.** Sessions run through `claude --print` and `codex exec` on your own logins and subscriptions. do-math does not call model APIs directly.

## Who it's for

I built do-math for my own math research. It is also meant for anyone who already uses Claude Code or Codex and wants to run one research goal across many sessions with independent checking, or wants a working example of that kind of long-running agent loop.

## Built with

- Python 3.12 or later, standard library only (runner and checker)
- Claude Code CLI and/or Codex CLI
- Lean 4, optionally with Mathlib
- Git (each research instance keeps its own repository)
- scholarly-mcp: Python with the MCP Python SDK, httpx, Playwright and other packages, all pinned in [requirements.txt](services/scholarly-mcp/requirements.txt)

I develop and run it on Windows 11, and the commands below use PowerShell. Other operating systems are untested.

## Repository layout

```
.claude/
  skills/do-math/     the runner, checker, session instructions and tests
  skills/...          11 supporting skills (listed below)
  agents/             fixed model and effort subagent definitions
  CLAUDE.md           project instructions for Claude Code
.agents/              generated copy of the skills for Codex, with Codex's project instructions
.codex/               Codex configuration
.mcp.json             MCP servers registered for Claude Code
AGENTS.md             short project instructions for Codex
services/             standalone tools (listed below)
기억/                 the project's commit-linked working memory
ROADMAP.md            planned work
```

## Running do-math

### Before you open this repository with an agent

The committed settings let agents act without asking. `.claude/settings.json` sets Claude Code's default permission mode to `bypassPermissions`, and `.codex/config.toml` runs Codex with full access (`danger-full-access`) and no approval prompts (`approval_policy = "never"`). That is how I run long unattended research on my own machine. If you do not want that, change these settings before you open the repository with Claude Code or Codex.

The scholarly-mcp entries in `.mcp.json` and `.codex/config.toml` use absolute paths under `C:/math`. Change them to the location of your clone, or remove them if you do not use scholarly-mcp.

### Starting research

The usual way is to open Claude Code or Codex in this repository and ask it to start research on a goal. The do-math skill then prepares the instance, starts the runner as a detached process, and tells you where to read the results.

To do the same by hand:

1. Check that `python` (3.12 or later), `git`, and the CLIs you want to use (`claude`, `codex`) are installed and logged in, and that Lean runs.
2. Write the goal, the conditions the result must meet, and what the sessions are allowed to do, to a UTF-8 `goal.md`. Write a UTF-8 `settings.json` with the models, CLI paths, concurrency limit and Lean command. Section 1 of [protocol.md](.claude/skills/do-math/protocol.md) (Korean) defines every field; its JSON example can be read without the Korean text.
3. Create and start an instance. Choose a path that does not exist yet, outside this repository or under the ignored `.skill-workspace/` folder, because each instance gets its own Git repository.

```powershell
$skill = 'C:/path/to/do-math/.claude/skills/do-math'
$instance = 'C:/path/to/do-math/.skill-workspace/do-math/add-zero'
python "$skill/runner.py" init $instance --goal C:/path/to/goal.md --settings C:/path/to/settings.json
python "$skill/runner.py" start $instance
python "$skill/runner.py" status $instance
```

4. Read the results from `<instance>/knowledge/index.md`. `python "$skill/runner.py" stop $instance` stops new dispatches and lets running sessions finish.

[SKILL.md](.claude/skills/do-math/SKILL.md) and [RUNTIME.md](.claude/skills/do-math/RUNTIME.md) (both Korean) cover the remaining commands: sending input to a running instance, ending a single session, and restarting.

## Standalone tools

None of these is required to run do-math. Research and explore sessions use scholarly-mcp as their default literature search tool when it is registered as an MCP server (see above). I developed the current version of do-math with async-development; do-math does not use it at run time. The tools' READMEs are in Korean.

- [services/scholarly-mcp](services/scholarly-mcp/README.md): a local MCP server that searches 49 academic sources and saves bibliographic data, abstracts, full text and supplements. Some of its sources currently go through one university library's access proxy.
- [services/continuous-development](services/continuous-development/README.md): runs a development goal as phases of parallel Codex task sessions, with a manager session that plans each next phase.
- [services/async-development](services/async-development/README.md): a manager session reviews each Codex worker's result, merges accepted work and assigns the next tasks as soon as their inputs are ready.
- [services/jev-cli](services/jev-cli/README.md): a command-line client for TypeSafe's Jev API, a hosted model that returns a choice, a score and a probability for a question and material you give it. It is unrelated to do-math.

## Supporting skills

| Skill | Purpose |
|---|---|
| graphify | A knowledge graph of do-math's own documents and scripts, for finding where a rule or procedure comes from |
| verify-rounds | Rounds in which several agents review a finished artifact and fix what they find |
| write-for-reader | Designing, writing and revising text that a person or an AI will act on, and interviewing the user when a decision is missing |
| grilling, grill-me | An interview that stress-tests a plan one question at a time |
| skill-creator | Creating, improving and benchmarking skills |
| writing-skills | Principles for writing skill descriptions, structure and tests |
| simplify | A short self-check: is this the simplest way to do what I am trying to do? |
| memory-harness | The structure and rules of the working-memory graph in `기억/` |
| commit-harness | The commit procedure that pairs every commit with a memory node |
| dream-harness | On request, synthesizes accumulated memory nodes into current principles and conventions |

## Language

Most documentation, skill text and commit messages are in Korean. Porting the skills to English with their behavior kept identical is item 3 of the roadmap.

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## License

This project is licensed under the [Mozilla Public License 2.0](LICENSE). Four skill directories are adapted from third-party projects and keep their original licenses; see [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
