"""Fixes from my own full reading of the four documents (2026-11-13)."""
import io, os, sys
root = sys.argv[1]
def apply(path, pairs):
    p = os.path.join(root, path); t = io.open(p, encoding="utf-8").read()
    for old, new in pairs:
        n = t.count(old)
        assert n >= 1, (path, n, old[:70])
        t = t.replace(old, new)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)

readme = [
 # 'route' is a term defined only in the body; the table and the lead must use plain words
 ("every record and every implication on the two routes to the root was accepted by an AI review session.",
  "every record and every implication in the two chains of reasoning that lead to the root was accepted by an AI review session."),
 ("on the two routes that lead from statements proved in earlier records to the conjecture itself, every record and every implication had been accepted by an AI review session. The two routes are not independent confirmations; both pass through one statement, as the first-run section explains.",
  "along the two chains of implications that lead from statements proved in earlier records to the conjecture itself, every record and every implication had been accepted by an AI review session. The two chains are not independent confirmations; both pass through one statement, as the first-run section explains."),
 # Lean named before it is said what it is
 ("or to turn an accepted proof into Lean, and it keeps all of its work,", "or to turn an accepted proof into a formal proof in Lean 4, a proof assistant, and it keeps all of its work,"),
 # 'settled' before its definition
 ("It holds the statement to be settled in `root.md`,", "It holds the statement to be proved or refuted in `root.md`,"),
 # end authorization
 ("once the limit is reached, the host records the runner's authorization and the session ends.", "once the limit is reached, the runner authorizes the end."),
 # model preference sentence
 ("By default the peer and review roles put first a different model from the one the producing roles put first.", "By default the peer and review roles list a different model first than the producing roles do."),
 # version 3 facts now known
 ("A third version, taken later on 12 November, is being deposited: `[placeholder: version 3 DOI, compression time and record count]`.",
  "A third version, taken at 23:25 Korean time on 12 November with 340 records, is being deposited: `[placeholder: version 3 DOI]`."),
 # process helpers
 ("Development and live verification were done on Windows. Linux is supported by the process helpers but has not been verified in a live run, and macOS is not supported.",
  "Development and live verification were done on Windows. The code that identifies and ends processes also supports Linux, but Linux has not been verified in a live run, and macOS is not supported."),
 # quick start sentence
 ("Then, from Claude Code or Codex started in the repository, ask for research on a statement to be started with the do-math skill, a folder of instructions that these CLIs load.",
  "Then, from Claude Code or Codex started in the repository, ask the assistant to start research on a statement with the do-math skill, a folder of instructions that these CLIs load."),
]
for f in ["README.md", "임시/작문/readme-20261112/README.md", "임시/작문/readme-20261112/stage3/README.md"]:
    apply(f, readme)

doc = [
 ("The frontier shows two routes to the root, established by records rce3dc75b and r15524fdd.", "The frontier shows two routes to the root, set out in records rce3dc75b and r15524fdd."),
 ("These four cases cover every way the failure can occur, and each has a reviewed informal proof.", "These four cases cover every way the failure can occur, and each has a reviewed informal proof that it cannot occur."),
 ("The property was then settled at steps at or beyond m and at steps below m separately,", "The property was then proved at steps at or beyond m and at steps below m separately,"),
 ("Both routes therefore pass through that statement, and it was the last part to close.", "Both routes therefore pass through that statement, and it was the last part to be proved."),
 ("do-math's default was changed at the same time so that the assessing roles prefer a model different from the one the producing roles prefer |",
  "do-math's default was changed at the same time so that peer and review prefer a model different from the one the producing roles prefer |"),
 ("A third version, taken late on 12 November, is being deposited: `[placeholder: version 3 DOI, compression time and record count]`.",
  "A third version, taken at 23:25 Korean time on 12 November with 340 records, is being deposited: `[placeholder: version 3 DOI]`."),
]
apply("docs/do-math/first-run-parking-unimodality.md", doc)

run = [
 ("The outbound traffic is the CLIs' own, to their model providers and to the web tools the sessions use.",
  "The outbound traffic is the CLIs' own, to their model providers and to the web tools the sessions use, together with that of any tool servers named in `mcp_servers`."),
 ("From Claude Code or Codex started in the repository, ask the do-math skill to start research on a statement.",
  "From Claude Code or Codex started in the repository, ask the assistant to start research on a statement with the do-math skill."),
]
apply("docs/do-math/running.md", run)
print("self-reading fixes applied")
