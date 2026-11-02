# Roadmap

Below is the work I plan to do next, roughly in order of how much it matters for long research runs.

## 1. Keep each session's shared context small (done)

Every session starts by reading its research instance's glossary and the record index (`knowledge/index.md`), and on a long run both used to grow for as long as the run continued: the index gained an entry for every plan, research and exploration record, and the glossary an entry for every object any session wanted to share. Two changes now keep them small.

The index is split into modules. `knowledge/index.md` is the general module, holding the records every session needs as base context; plan records no longer have entries there. Each plan declares further modules in the `index` field of its output, naming the records that only some tasks need, and the runner renders them as files under `knowledge/index/` with a description each, so that a session opens only the modules its task concerns. The glossary is split into a global part and a local part. The plan's `glossary.md` holds only the names the whole run shares, while every research, exploration and peer record publishes a `glossary-local.md` for the names it uses internally and flags the entries it thinks should be shared; the plan adopts or declines those candidates. The guidance for both decisions is in `plan.md` and `common.md`.

## 2. Make scholarly-mcp a general, credential-free tool

scholarly-mcp reaches many of its sources through one university library's login, so other people cannot use those sources. I plan to rework it into a general academic search tool that needs no credentials, centered on arXiv and open repositories. As part of that, I will replace the test fixtures captured from subscription databases with made-up sample data.

## 3. Port the remaining skills to English with identical behavior

The do-math skill — the instructions that every session reads, the file contract, the operating documents and the runner's own strings — has been ported to English, with one fixed English name for every term that carries a do-math-specific meaning. The supporting skills, the project instructions, the standalone tools' documentation and the Korean directory names (`기억/`, `임시/`) have not. I plan to port them the same way — fix the vocabulary first, then the text — so that each skill behaves exactly as it does now, and to verify that it does.

## 4. Long consistency runs over the project itself

I plan to run verify-rounds for long stretches over the project's own code and documents, to find and fix places where they contradict each other. Two known starting points:

- The graphify skill's example commands still name files that no longer exist in do-math, such as `contracts.py` and `계약/연구-수행.md`.
- The simplify skill's description is the placeholder `foo`.

## 5. Central Lean execution (done)

Each session used to run Lean itself, using the command in the instance's settings. With up to `max_sessions` sessions running at once, nothing limited how many Lean compilations ran at the same time or how much memory they used together. That mattered with Mathlib, where a single compile on a cold cache took over seven minutes on my machine.

Every compile now goes through a single Lean broker per instance, a process the runner starts and keeps alive for as long as it runs, and which outlives the runner. A session submits a file with its estimate of the compile's peak memory. The broker measures the cost of each set of imports once and keeps a table of what compiles have cost since, and it admits queued compiles within one memory budget and one thread budget by a rule that reserves each compile's certain memory in full and pools the uncertain parts, so that several compiles share the budget without adding up their worst cases; small compiles may pass a large one that cannot start yet, a limited number of times, so that none is starved. Every compile's peak and duration are measured and returned to the session. Nothing is stopped for exceeding an estimate; only the compiles of sessions that have ended are cancelled. `LEAN.md` explains the whole of it, including how to write Lean that compiles cheaply, and `common.md`, `research.md` and `review.md` direct the sessions to it.

## 6. Post-mortem of past long runs

I plan to analyze the records of past long research runs without deciding in advance what went well or badly, then derive improvements to the runner and the skills from what the records show, and apply them.
