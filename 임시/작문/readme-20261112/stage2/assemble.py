"""Assemble the stage-two README and the two docs from the current README and the drafted pieces.

Usage: python -I assemble.py <repo_root> <pieces_dir>
Moved passages are copied byte for byte from the current README; only the patches listed below touch them.
"""
import io, os, re, sys

root, pieces = sys.argv[1], sys.argv[2]
def rd(p): return io.open(p, encoding="utf-8").read()
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)

readme = rd(os.path.join(root, "README.md"))
parts = re.split(r"\n(?=## )", readme)
sec = {}
for p in parts[1:]:
    title = p.splitlines()[0][3:]
    sec[title] = p.rstrip("\n") + "\n"
need = ["How the research is organized", "What counts as established",
        "The first run: unimodality of the maximum-displacement distribution of parking functions",
        "Reading a published knowledge base", "Running do-math",
        "Repository layout, verification and tests", "Standalone tools and supporting skills",
        "Language, roadmap, citation and license"]
missing = [n for n in need if n not in sec]
assert not missing, missing

def patch(t, old, new, count=1):
    assert t.count(old) == count, ("count", t.count(old), old[:60])
    return t.replace(old, new)

# --- README ---
how = sec["How the research is organized"]
anchor = "\nWhat a producing session leaves is its **retained work**"
assert how.count(anchor) == 1
mermaid = rd(os.path.join(pieces, "mermaid.md")).strip("\n")
how = how.replace(anchor, "\n" + mermaid + "\n" + anchor, 1)

repo = sec["Repository layout, verification and tests"]
repo = patch(repo,
    "and recovery after a runner restart, are in [docs/do-math/rebuild-verification.md](docs/do-math/rebuild-verification.md).",
    "and recovery after a runner restart, are in [docs/do-math/rebuild-verification.md](docs/do-math/rebuild-verification.md). The [full account of the first run](docs/do-math/first-run-parking-unimodality.md) and the [running guide](docs/do-math/running.md) are in the same folder.")

new_readme = "\n".join([
    rd(os.path.join(pieces, "lead.md")).rstrip("\n"),
    how.rstrip("\n"),
    sec["What counts as established"].rstrip("\n"),
    rd(os.path.join(pieces, "firstrun_short.md")).rstrip("\n"),
    sec["Reading a published knowledge base"].rstrip("\n"),
    rd(os.path.join(pieces, "running_short.md")).rstrip("\n"),
    repo.rstrip("\n"),
    sec["Standalone tools and supporting skills"].rstrip("\n"),
    sec["Language, roadmap, citation and license"].rstrip("\n"),
]).replace("\n## ", "\n\n## ") + "\n"
new_readme = re.sub(r"\n{3,}", "\n\n", new_readme)

# --- doc 1: first run ---
fr = sec["The first run: unimodality of the maximum-displacement distribution of parking functions"]
fr = re.sub(r"^## .*\n", "", fr, count=1)
fr = re.sub(r"^### ", "## ", fr, flags=re.M)
# drop the placeholder subsection (it stays in the README) and replace with a pointer
m = re.search(r"\n## Artifacts not yet public\n.*\Z", fr, flags=re.S)
assert m
fr = fr[:m.start()] + "\n## Artifacts not yet public\n\nThe artifacts of the run that are being prepared and are not yet public are listed, with their status, in the first-run section of the [README](../../README.md).\n"
fr = patch(fr, "and the default described above, under which the assessing roles prefer a different model, was adopted at the same time.",
           "and the default described in the README, under which the assessing roles prefer a different model, was adopted at the same time.")
fr = patch(fr, 'Whether the mechanisms described under the heading "How the research is organized", such as sections,',
           'Whether the mechanisms described in the README under "How the research is organized", such as sections,')
doc1 = ("# The first run of do-math: unimodality of the maximum-displacement distribution of parking functions\n\n"
        "This document is the full account of the first run of the current do-math implementation, as of 17:45 Korean time on 12 November 2026; the run continues. "
        "The terms it uses, such as node, relation, route, record, review, informally proved and computer-assisted, are defined in the repository [README](../../README.md) "
        "under \"How the research is organized\" and \"What counts as established\", and the README's section \"Reading a published knowledge base\" explains the files of the published evidence.\n\n"
        + fr.lstrip("\n"))

# --- doc 2: running ---
run = sec["Running do-math"]
run = re.sub(r"^## .*\n", "", run, count=1)
run = re.sub(r"^### ", "## ", run, flags=re.M)
run = run.replace("](.claude/", "](../../.claude/")
doc2 = ("# Running do-math\n\n"
        "This guide covers the requirements, what a run does on your machine, starting a run through the skill or by hand, the settings, the runner commands, ending a run, and interruptions and completion. "
        "The repository [README](../../README.md) gives a quick start taken from it; the [operating guide](../../.claude/skills/do-math/reference/operations.md) in the skill is the complete reference for every setting and state.\n\n"
        + run.lstrip("\n"))

wr(os.path.join(root, "README.md"), new_readme)
wr(os.path.join(root, "docs", "do-math", "first-run-parking-unimodality.md"), doc1)
wr(os.path.join(root, "docs", "do-math", "running.md"), doc2)
print("assembled: README %d words, doc1 %d words, doc2 %d words" % (len(new_readme.split()), len(doc1.split()), len(doc2.split())))
