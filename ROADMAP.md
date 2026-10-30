# Roadmap

Below is the work I plan to do next, roughly in order of how much it matters for long research runs.

## 1. Keep each session's shared context small

Every session starts by reading its research instance's glossary (`glossary.md`) and the record index (`knowledge/index.md`). Both grow for as long as the run continues. The index gains an entry for every plan, research and exploration record, and the glossary gains an entry for every object that the research shares across sessions. On a long run they take up a growing share of each session's context, which leaves less room for the mathematics the session is working on.

I plan to split the glossary into a local part and a global part, and to prune the index periodically. The exact design is still to be worked out.

## 2. Make scholarly-mcp a general, credential-free tool

scholarly-mcp reaches many of its sources through one university library's login, so other people cannot use those sources. I plan to rework it into a general academic search tool that needs no credentials, centered on arXiv and open repositories. As part of that, I will replace the test fixtures captured from subscription databases with made-up sample data.

## 3. Port the skills to English with identical behavior

Most skill documents, project instructions and directory names are in Korean, including the instructions that every do-math session reads. I plan to port them to English so that each skill behaves exactly as it does now, and to verify that it does.

## 4. Long consistency runs over the project itself

I plan to run verify-rounds for long stretches over the project's own code and documents, to find and fix places where they contradict each other. Two known starting points:

- The graphify skill's example commands still name files that no longer exist in do-math, such as `contracts.py` and `계약/연구-수행.md`.
- The simplify skill's description is the placeholder `foo`.

## 5. Central Lean execution

Each session runs Lean itself, using the command in the instance's settings. With up to `max_sessions` sessions running at once, nothing limits how many Lean compilations run at the same time or how much memory they use together. That matters with Mathlib, where a single compile on a cold cache took over seven minutes on my machine. I plan to run Lean compilations through one central pool, shared by all sessions, with a fixed resource limit.

## 6. Post-mortem of past long runs

I plan to analyze the records of past long research runs without deciding in advance what went well or badly, then derive improvements to the runner and the skills from what the records show, and apply them.
