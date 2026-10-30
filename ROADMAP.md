# Roadmap

Work I plan to do next, roughly in order of how much it affects long research runs.

## 1. Keep each session's shared context small

Every session reads its research instance's glossary and record index, and both grow without limit during long runs, so they take up more of each session's context over time. I plan to split the glossary into a local part and a global part, and to prune the index periodically. The exact design is still to be worked out.

## 2. Make scholarly-mcp a general, credential-free tool

scholarly-mcp currently reaches many of its sources through one university library's login. I plan to rework it into a general academic search tool that needs no credentials, centred on arXiv and open repositories. As part of that, the test fixtures captured from subscription databases will be replaced with made-up sample data.

## 3. Port the skills to English with identical behavior

Most skill documents, project instructions and directory names are in Korean. I plan to port them to English in a way that keeps each skill's behavior the same, and to check that it does.

## 4. Long consistency runs over the project itself

Run verify-rounds for extended periods over the project's own code and documents to find and fix internal inconsistencies. Known starting points: the graphify skill's examples still point at paths that no longer exist, and the simplify skill has a placeholder description.

## 5. Central Lean execution

Today each session starts its own Lean processes. I plan to run Lean checks through one central pool with a fixed resource limit, shared by all sessions.

## 6. Post-mortem of past long runs

Analyse the records of past long research runs without assuming in advance what went well or badly, then derive improvements to the runner and skills and apply them.
