"""Sentence-level polish of the two docs and the Zenodo description in the accepted register. Facts unchanged."""
import io, os, sys
root = sys.argv[1]
def apply(path, pairs):
    p = os.path.join(root, path); t = io.open(p, encoding="utf-8").read()
    for old, new in pairs:
        n = t.count(old)
        assert n == 1, (path, n, old[:70])
        t = t.replace(old, new)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)

apply("docs/do-math/first-run-parking-unimodality.md", [
 ("The session counts differ from the record count because a producing session that ends without having begun research gets no peer, interrupted peers and reviews are replaced by new sessions, some candidates are not published, and some pipelines were still in progress; the commits outnumber the records because organizer outputs, comprehensive reviews and question publications are committed too.",
  "The session counts differ from the record count for several reasons: a producing session that ends without having begun research gets no peer, interrupted peers and reviews are replaced by new sessions, some candidates are not published, and some pipelines were still in progress. The commits outnumber the records because organizer outputs, comprehensive reviews and question publications are committed too."),
 ("The last open premise on the routes was one node, pair-beats-capped-threshold, whose exact statement in the frontier is an inequality between two counts of configurations for n between 2ℓ and about 2ℓ^(3/2); the record that proved it, r5909c9e7, was published on 11 November at 16:14 Korean time. Its review supported the proof's claims, accepted the proof, marked one peripheral claim about a table's coverage unsupported, and stated that the proof inherits computer-assisted inputs from earlier records: several in binary64 floating point, and the certification that the root holds for all n ≤ 20000 (record r15df76b5, 8 November), which checked the steps at or beyond the middle in integer interval arithmetic and the steps below the middle twice, in integer interval arithmetic and in floating point with directed rounding. With that node proved, the runner derived the root through the relations.",
  "The last open premise on the routes was a single node, pair-beats-capped-threshold. Its exact statement is in the frontier; in outline, it is an inequality between two counts of configurations for n between 2ℓ and about 2ℓ^(3/2). The record that proved it, r5909c9e7, was published on 11 November at 16:14 Korean time. Its review supported the proof's claims and accepted the proof, marking one peripheral claim about a table's coverage as unsupported. The review also stated that the proof inherits computer-assisted inputs from earlier records: several in binary64 floating point, and the certification that the root holds for all n ≤ 20000 (record r15df76b5, 8 November), which checked the steps at or beyond the middle in integer interval arithmetic and the steps below the middle twice, in integer interval arithmetic and in floating point with directed rounding. With that node proved, the runner derived the root through the relations."),
 ("Every review was an AI session; no person has reviewed the records as a referee would. Several records",
  "Every review was an AI session, and no person has refereed the records. Several records"),
])

apply("docs/do-math/running.md", [
 ("External tools such as scholarly-mcp, a local server for academic literature search, are optional; the `mcp_servers` field of an instance's `settings.json` names the tool servers its sessions may use, and nothing else is available to them beyond the CLIs' built-in tools, which include shell commands and web search.",
  "External tools such as scholarly-mcp, a local server for academic literature search, are optional. The `mcp_servers` field of an instance's `settings.json` names the tool servers its sessions may use; beyond those, the sessions have only the CLIs' built-in tools, which include shell commands and web search."),
 ("`init` creates the instance at a new path, which should lie outside this repository or under its `.skill-workspace/` directory, which Git ignores, so that the instance's own repository is not nested in a tracked tree. `start` then launches the runner:",
  "`init` creates the instance at a new path. The path should lie outside this repository, or under its `.skill-workspace/` directory, which Git ignores, so that the instance's own Git repository is not nested inside a tracked tree. `start` then launches the runner:"),
 ("To end a run before the root is settled, use `stop`, so that no peer or review follows what you end next; then `kill-session` for each running session, which also ends its session host; then end the runner process whose ID is in the instance's `runner/process.json`, with `Stop-Process` on Windows or `kill` on Linux.",
  "To end a run before the root is settled, take three steps in order. First run `stop`, so that no peer or review follows the sessions you are about to end. Then run `kill-session` for each running session; this also ends the session's host process. Finally, end the runner process, whose ID is in the instance's `runner/process.json`, with `Stop-Process` on Windows or `kill` on Linux."),
])

apply("임시/작문/readme-20261112/stage3/zenodo-description.md", [
 ("Every record is the work of three sessions in turn. One did the mathematics, a second read everything the first left behind and wrote it up for others, and a third compared the write-up with the originals and assessed every claim in it.",
  "Every record was produced in three stages by three different sessions: one worked on the problem, a second read everything the first left behind and developed it into the record, and a third checked that record against the first session's files and assessed every claim in it."),
 ("Every judgment in this archive was made by an AI session, and no person has reviewed its records as a referee would.",
  "Every judgment in this archive was made by an AI session, and no person has refereed its records."),
])
print("docs polished")
