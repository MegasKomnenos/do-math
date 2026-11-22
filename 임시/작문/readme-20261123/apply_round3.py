"""Third-round revision: exact replacements, each asserted to match exactly once."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]

README = [
(r'''Every result they keep is written in Lean 4, a proof assistant, as part of one library, with a written record beside it. |''',
 r'''Every result they keep is stated in Lean 4, a proof assistant, as part of one library, with a written record beside it; its proof may have been checked by Lean or only reviewed by an AI session. |'''),
(r'''Before it judges, it has the candidate examined three times, independently, against the producing session's files, and it compiles the candidate itself. It then judges each element on three points: whether its Lean statement says what its record says, whether its proof is correct, and whether a correct proof should also be accepted. The last of these is a second judgment, which is explained below.''',
 r'''Before it judges, it has the candidate examined three times against the producing session's files, and it compiles the candidate itself. It then judges each element, above all whether its Lean statement says what its record says, whether its proof is correct, and whether a correct proof should also be accepted. The last of these is a second judgment, which is explained below.'''),
(r'''The views described below use the weight to show the structure of a proof and not every lemma; a step remains an element, and proofs name it.''',
 r'''The frontier, a view described below, uses the weight to show the structure of a proof and not every lemma; a step remains an element, proofs name it, and the index of all elements lists it.'''),
(r'''and the review judges the element on what was read. If the root comes to rest on such a result,''',
 r'''and the review judges the element on what was read. A statement settled through such a result rests, to that extent, on a proof that is in the source and not in the library. If the root comes to rest on such a result,'''),
(r'''because a further proof is a further declaration that states the same thing, and each proof has a standing of its own.''',
 r'''because a further proof is a further declaration whose statement Lean has confirmed to be identical, and each proof has a standing of its own.'''),
(r'''a term explained under "The choice of work".''',
 r'''a term explained under "The choice of work: frontier, sections and leases".'''),
(r'''A producing session does not write to the canon, which changes only when the runner publishes a candidate.''',
 r'''A producing session does not write to the canon, which changes only when the runner publishes a candidate or an organizer's change.'''),
(r'''an organizer with its account of what it joined, rearranged or merged.''',
 r'''an organizer with its organization, the account of what it joined, rearranged or merged.'''),
(r'''Publication depends on one rule: the statement of an element is never changed in place.''',
 r'''Publication depends on one rule: the statement of an element is never changed in place, and neither is a definition.'''),
(r'''at once if the old statement was not settled and otherwise once the new statement is settled as well.''',
 r'''at once if the old statement was not settled, and otherwise by a later candidate once the new statement is settled as well.'''),
(r'''The judge's verdict holds only if the library was compiled honestly, because Lean code that a session wrote runs when the library is compiled. The comparator has a sandbox in which it can build what it judges, but do-math gives it modules that its own broker has already compiled, so that sandbox does not cover those builds on any system, and on Windows, where it cannot run, it is switched off. What the verdict does not rest on is the structural index, the views, or anything a session reported.''',
 r'''The judge works from modules that the instance's broker has compiled, and Lean code that a session wrote runs while they are compiled, so the judge's verdict holds only if those compiles were made honestly. The comparator has a sandbox in which it could build what it judges, but do-math always gives it modules that are already compiled, so the sandbox does not cover those compiles on any system, and on Windows, where the sandbox cannot run, it is switched off. What the verdict does not rest on is the structural index, the views, or anything a session reported. The verdict on the root is reported beside the root's state and is not part of what makes a run complete: a rejection leads to a comprehensive review of the proof, and with a Lean older than 4.35 there is no judge and no verdict.'''),
(r'''or opened by the runner when a finding withdraws a confirmation without naming a concern.''',
 r'''or opened by the runner when a finding made in the review of a candidate withdraws a confirmation without naming a concern.'''),
(r'''These are the system's own names: *informally proved* means that AI reviews have accepted a proof of the root and of everything beneath it, and that Lean has not yet checked all of it.''',
 r'''These are the system's own names: *informally proved* means that a proof of the root and of everything beneath it has been accepted, and that no such proof is yet formal all the way down.'''),
(r'''and `init` refuses when that server's Python environment is not installed;''',
 r'''and `init` refuses when it cannot find that server's Python;'''),
(r'''and the run's six sessions took it to a formally proved root. All six used one Claude model''',
 r'''and three of the run's six sessions took it to a formally proved root, while the other three published further results. All six used one Claude model'''),
]

GUIDE = [
(r'''`init` refuses to create an instance when that environment is not installed,''',
 r'''`init` refuses to create an instance when it cannot find that environment's Python,'''),
(r'''On Windows, where the session's processes were contained when it was launched, it ends the processes the session started as well, except any that a system service started on its behalf.''',
 r'''On Windows, if the session's processes were contained when it was launched, which the session's `process-job.json` records, it ends the processes the session started as well, except any that a system service started on its behalf.'''),
]


def apply(path, pairs):
    text = path.read_text(encoding='utf-8')
    failed = []
    for index, (old, new) in enumerate(pairs):
        count = text.count(old)
        if count != 1:
            failed.append((index, count, old[:70]))
            continue
        text = text.replace(old, new)
    if failed:
        for item in failed:
            print('NO MATCH', path.name, item)
        return False
    path.write_text(text, encoding='utf-8', newline='\n')
    print('applied', len(pairs), 'to', path.name)
    return True


ok = apply(ROOT / 'README.md', README)
ok = apply(ROOT / 'docs' / 'do-math' / 'running.md', GUIDE) and ok
sys.exit(0 if ok else 1)
