"""Assemble the stage-three README: current lead + rewritten middle + polished tail. Usage: assemble3.py <repo_root> <stage3_dir>"""
import io, os, sys
root, s3 = sys.argv[1], sys.argv[2]
rd = lambda p: io.open(p, encoding="utf-8").read()
lead = rd(os.path.join(s3, "lead_current.md")).rstrip("\n")
middle = rd(os.path.join(s3, "middle.md")).rstrip("\n")
tail = rd(os.path.join(s3, "tail_sections.md")).rstrip("\n")
def rep(t, old, new):
    assert t.count(old) == 1, old[:60]
    return t.replace(old, new)
# lead: the at-a-glance 'State of the root' cell says 'as a referee would'; align with the lead's 'refereed'
lead = rep(lead, "No person has reviewed the records as a referee would. Several steps rest on computer-assisted inputs, some in binary64 with error models assumed in advance. |",
           "No person has refereed the records. Several steps rest on computer-assisted inputs, some in binary64 with error models assumed in advance. |")
# tail polish
tail = rep(tail, "Its entry point is `index.md`, which lists records the organizer selected as shared context for new sessions, a directory of modules with their descriptions, and recent records not yet organized. Each entry shows the record's own description, written by its peer, and the review's short assessment beside it.",
           "Its entry point is `index.md`, which lists the records that the organizer selected as shared context for new sessions, a directory of modules with their descriptions, and the recent records not yet organized. Each entry shows the record's own description, written by its peer, with the review's short assessment beside it.")
tail = rep(tail, "`frontier.md` gives every node's exact statement, its state (unresolved, informally proved or refuted, formally proved or refuted, or contested), the proofs that support that state with links to their records, the accepted relations with their premises and conclusions, how the node stands to the root, and any pending concern. After the nodes it lists the questions with their statements, grounds, state and source; a question the operator placed directly shows the operator as its source instead of a reviewed record. `glossary.md` is the shared vocabulary with each term's definition and its source record.",
           "`frontier.md` gives, for every node, its exact statement; its state, which is unresolved, informally proved or refuted, formally proved or refuted, or contested; the proofs that support that state, with links to their records; the accepted relations with their premises and conclusions; how the node stands to the root; and any pending concern. After the nodes it lists the questions with their statements, grounds, state and source; a question that the operator placed directly shows the operator as its source instead of a reviewed record. `glossary.md` is the shared vocabulary, with each term's definition and its source record.")
tail = rep(tail, "The runtime needs Python 3.12 or later and Git, and uses only Python's standard library. It needs the Codex CLI, the Claude Code CLI, or both, installed and logged in; it launches them as processes and does not call model APIs directly, so usage is billed or metered however those CLIs are configured. It needs Lean 4 in every case and Mathlib when the proofs will draw on it. Development and live verification were done on Windows; Linux is supported by the process helpers but has not been verified in a live run, and macOS is not supported.",
           "The runtime needs Python 3.12 or later and Git, and it uses only Python's standard library. It needs the Codex CLI, the Claude Code CLI, or both, installed and logged in; it launches them as processes and does not call model APIs directly, so usage is billed or metered however those CLIs are configured. It needs Lean 4 in every case, and Mathlib when the proofs will draw on it. Development and live verification were done on Windows. Linux is supported by the process helpers but has not been verified in a live run, and macOS is not supported.")
tail = rep(tail, "do-math itself sends nothing outside your machine; publication is a commit to the instance's local Git repository, and the outbound traffic is the CLIs' own.",
           "do-math itself sends nothing outside your machine; publication is a commit to the instance's local Git repository, and the only outbound traffic is the CLIs' own.")
tail = rep(tail, "Clone this repository. From Claude Code or Codex started in the repository, ask the do-math skill to start research on a statement; the conversation that handles the request is the operator, and it prepares the statement and settings, launches the detached runner and reports where the work lives. The skill is the folder `.claude/skills/do-math`, with its mirror for Codex at `.agents/skills/do-math`.",
           "Clone this repository. Then, from Claude Code or Codex started in the repository, ask the do-math skill to start research on a statement. The conversation that handles that request is the operator: it prepares the statement and the settings, launches the detached runner and reports where the work lives. The skill is the folder `.claude/skills/do-math`, with a mirror for Codex at `.agents/skills/do-math`.")
out = lead + "\n\n" + middle + "\n\n" + tail + "\n"
for f in ["README.md", "임시/작문/readme-20261112/README.md", "임시/작문/readme-20261112/stage3/README.md"]:
    io.open(os.path.join(root, f), "w", encoding="utf-8", newline="\n").write(out)
print("assembled README:", len(out.split()), "words")
