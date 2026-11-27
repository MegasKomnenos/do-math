"""Assemble the manuscript for the independent reading: excerpts of the do-math guides as a session
receives them, with the proposed edits applied to copies. Nothing under .claude/ or the instance is written.

Every edit is anchored on a string that must occur exactly once in its source; the script stops otherwise.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / '.claude/skills/do-math'
HERE = Path(__file__).resolve().parent


def read(path):
    return path.read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def once(text, anchor):
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f'anchor occurs {count} times, expected 1: {anchor[:70]!r}')


def insert_after(text, anchor, addition):
    once(text, anchor)
    return text.replace(anchor, anchor + addition)


def replace(text, old, new):
    once(text, old)
    return text.replace(old, new)


def section(text, start, end):
    """The text from the line that starts with `start` up to the line that starts with `end` (exclusive)."""
    lines = text.split('\n')
    first = [i for i, line in enumerate(lines) if line.startswith(start)]
    if len(first) != 1:
        raise SystemExit(f'heading occurs {len(first)} times: {start!r}')
    last = [i for i, line in enumerate(lines) if i > first[0] and line.startswith(end)]
    if not last:
        raise SystemExit(f'no end heading after {start!r}: {end!r}')
    return '\n'.join(lines[first[0]:last[0]]).rstrip() + '\n'


# ---- Edit A: reference/common.md, "Working directly on the central difficulty"
# The point on time is a paragraph of its own, between the paragraph on trying an obstacle and the sentences on
# the record of failed approaches, which become a paragraph of their own as well (their words are unchanged).
A_OLD = ('it does not mean repeating an approach just as it failed before. What remains open in the research can '
         'carry a long record of approaches that failed.')
A_PARAGRAPH = (
    'Staying with an obstacle takes time, and you are not pressed for time. Session run time has no fixed cap, '
    'so when the obstacle does not give way you can go on thinking about it for as long as that takes. You '
    'should not waste time, but work on something hard may take the time it needs. Being stuck on an obstacle '
    'and thinking about it is good work too, even when it does not yet promise any return, and the user would '
    'much rather have it than a sure result that is worth nothing. What the user wants is a good result. A '
    'half-baked result is not one, nor is a result that came from avoiding work that was needed, nor one that '
    'simply gave up and says so.')
A_NEW = ('it does not mean repeating an approach just as it failed before.\n\n' + A_PARAGRAPH +
         '\n\nWhat remains open in the research can carry a long record of approaches that failed.')

# ---- Edit B: reference/retained-work.md, the paragraph on the session that hands over
B_ANCHOR = 'your Lean files are handed on as "Working Lean files" describes.'
B_TEXT = (
    ' The session that takes the task on has a whole conversation of its own ahead of it and is not pressed for '
    'time. What you would do next is therefore written for a session in that position: how far it pursues a '
    'direction and when it ends are for it to judge under the role guide, as they were for you, and your report '
    'leaves both to it.')

# ---- Edit D: reference/retained-work.md, the paragraph on the session that continues
D1_ANCHOR = "is in the `inbox/` of that session's folder and not in your own inbox."
D1_TEXT = (
    ' How far you pursue a direction and when you end are yours to judge under your role guide, also where an '
    'earlier report says otherwise.\n\n')
D1_JOIN_OLD = D1_TEXT + ' What you leave is again read by'
D1_JOIN_NEW = D1_TEXT + 'What you leave is again read by'

D3_OLD = (
    'Your report is therefore the report of the task as a whole, and you carry over into your own `output/`, '
    'which starts empty, what still stands in the `output/` of the session before you. The working files of the '
    'earlier sessions stay in their own `work/` folders, and a path in your report that begins with `work/` is '
    'read as a path in your folder, so a file of theirs that your report relies on is found only under the path '
    'of its session folder, or as a copy in your own.')
D3_NEW = (
    'So before you begin work of your own, carry over into your own `output/`, which starts empty, what still '
    'stands in the `output/` of the session before you; for an attempt, an exploration or a formalizer that '
    'includes its report. Your folder then holds what that session handed on, also if your own session is cut '
    'off early. The working files of the earlier sessions stay in their own `work/` folders, and a path in your '
    'report that begins with `work/` is read as a path in your folder, so a file of theirs that your report '
    'relies on is found only under the path of its session folder, or as a copy in your own. The report you '
    'carried over was written in the earlier session\'s folder, so its `work/` paths point there and not into '
    'yours: copy the files it relies on into your own `work/`, or write their paths with that session\'s folder. '
    'From then on the report is yours, and it '
    'is the report of the task as a whole, as the task stands when you leave it. Arrange it anew where your work '
    'does not fit the way it was arranged. What the earlier sessions established and what they left open stays '
    'in it, a line of work that you leave stays as an approach with where it stopped, and where your work has '
    'proved, refuted or carried out something the report speaks of, the passage is brought up to date where it '
    'stands.')

# ---- Edit C: the runner's message (runtime/ending.py, CONTEXT_MESSAGE)
C_ANCHOR = 'and what you would do next and why.'
C_TEXT = (
    ' The new session has a whole conversation of its own ahead of it and is not pressed for time, so leave to '
    'it how far it pursues a direction and when it ends.')


def main():
    common = read(SKILL / 'reference/common.md')
    common = replace(common, A_OLD, A_NEW)
    part = section(common, '### Working directly on the central difficulty', '### Building on what already exists')

    retained = read(SKILL / 'reference/retained-work.md')
    retained = insert_after(retained, B_ANCHOR, B_TEXT)
    retained = insert_after(retained, D1_ANCHOR, D1_TEXT)
    retained = replace(retained, D1_JOIN_OLD, D1_JOIN_NEW)
    retained = replace(retained, D3_OLD, D3_NEW)
    report = section(retained, '# Retaining a session', '## Working Lean files')
    handing = section(retained, '## Handing a task over to a new session', '## The outcome')

    # The message as a session of the running research received it, so that the reader sees real figures.
    delivered = sorted((ROOT / '.skill-workspace/sunflower-20261122/sessions/'
                        's8a5b23e169434174b5327885a0823ebd/messages/delivered').glob('*.json'))
    message = json.loads(delivered[0].read_text(encoding='utf-8'))['text']
    source = read(SKILL / 'runtime/ending.py')
    once(source, "'still open, and what you would do next and why. A peer, a review and '")
    message = insert_after(message, C_ANCHOR, C_TEXT)

    parts = [
        '# Excerpts of the guides of a do-math research session',
        '',
        'A session reads the first two excerpts at its launch, as parts of a much longer starting context. The '
        'third is a message that reaches it hours later, while it works. Passages left out are marked.',
        '',
        '## Excerpt 1. From the common introduction, under "How you should do the work"',
        '',
        part,
        '## Excerpt 2. From the guide "Retaining a session\'s work"',
        '',
        report,
        '[The section "Working Lean files" is left out here.]',
        '',
        handing,
        '[The sections "The outcome" and "Continuing an attempt, exploration, formalization or peer session" '
        'and those after them are left out here.]',
        '',
        '## Excerpt 3. The message of the runner to a session whose conversation is nearly full',
        '',
        message,
        '',
    ]
    out = HERE / '원고.md'
    out.write_text('\n'.join(parts), encoding='utf-8', newline='\n')
    print('written', out, len('\n'.join(parts).encode('utf-8')), 'bytes')


if __name__ == '__main__':
    main()
