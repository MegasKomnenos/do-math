"""Apply the edits of this folder to the do-math guides and the runner's message, then check the result.

The texts are those of `_조립.py`, the script that assembled the manuscript of the independent reading, so what
is installed is what was read. Every anchor must occur exactly once in its file; the script stops before it
writes anything if one does not. After writing, it checks that the installed files give the manuscript back:
the two guide sections as they stand in it, and the message with the figures of the session it was taken from.
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SKILL = ROOT / '.claude/skills/do-math'

spec = importlib.util.spec_from_file_location('assemble', HERE / '_조립.py')
assemble = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assemble)

# The line of runtime/ending.py that carries the anchor, and the lines that replace it. C_TEXT of the manuscript
# is the text between "and why." and " A peer": the check at the end compares the formatted message with it.
ENDING_OLD = "    'still open, and what you would do next and why. A peer, a review and '\n"
ENDING_NEW = (
    "    'still open, and what you would do next and why. The new session has a whole conversation of its own '\n"
    "    'ahead of it and is not pressed for time, so leave to it how far it pursues a direction and when it ends. '\n"
    "    'A peer, a review and '\n")


def load(path):
    data = path.read_bytes()
    if b'\r' in data:
        raise SystemExit(f'{path} has CR line endings; this script writes LF only')
    return data.decode('utf-8')


def main():
    paths = {name: SKILL / name for name in ('reference/common.md', 'reference/retained-work.md', 'runtime/ending.py')}
    texts = {name: load(path) for name, path in paths.items()}

    common = assemble.replace(texts['reference/common.md'], assemble.A_OLD, assemble.A_NEW)

    retained = texts['reference/retained-work.md']
    retained = assemble.insert_after(retained, assemble.B_ANCHOR, assemble.B_TEXT)
    retained = assemble.insert_after(retained, assemble.D1_ANCHOR, assemble.D1_TEXT)
    retained = assemble.replace(retained, assemble.D1_JOIN_OLD, assemble.D1_JOIN_NEW)
    retained = assemble.replace(retained, assemble.D3_OLD, assemble.D3_NEW)

    ending = assemble.replace(texts['runtime/ending.py'], ENDING_OLD, ENDING_NEW)

    # Every anchor was found once. Write.
    for name, new in (('reference/common.md', common), ('reference/retained-work.md', retained),
                      ('runtime/ending.py', ending)):
        paths[name].write_bytes(new.encode('utf-8'))
        print('written', name, len(new.encode('utf-8')) - len(texts[name].encode('utf-8')), 'bytes added')

    # The installed files give the manuscript back.
    manuscript = (HERE / '원고.md').read_text(encoding='utf-8')
    part = assemble.section(load(paths['reference/common.md']),
                            '### Working directly on the central difficulty', '### Building on what already exists')
    installed = load(paths['reference/retained-work.md'])
    report = assemble.section(installed, '# Retaining a session', '## Working Lean files')
    handing = assemble.section(installed, '## Handing a task over to a new session', '## The outcome')
    for label, text in (('common part', part), ('report section', report), ('hand-over section', handing)):
        if text not in manuscript:
            raise SystemExit(f'installed {label} differs from the manuscript')
        print('same as the manuscript:', label)

    sys.path.insert(0, str(SKILL / 'runtime'))
    sys.dont_write_bytecode = True
    import ending as installed_ending
    message = installed_ending.context_message({'id': '636b15142b5b430a8729a2646ab1be2d', 'context': 802208})
    if message not in manuscript:
        raise SystemExit('the installed message differs from the message of the manuscript')
    if message.count(assemble.C_TEXT) != 1:
        raise SystemExit('the new sentence does not stand once in the installed message')
    print('same as the manuscript: the message, with the new sentence once')


if __name__ == '__main__':
    main()
