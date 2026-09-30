"""The known-defect ledger (tests/known_defects.json) and the mark that binds a test to it.

During stage 1 (behaviour-preserving refactor) a new test may reproduce a defect
that stage 2 will fix. Such a test carries ``@known_defect('KD-0001')`` and the
ledger holds an open entry naming it. The mark is ``unittest.expectedFailure``,
so the runner counts the reproduction as expected and fails the run when the
test starts passing: a fixed defect must close its entry and drop its mark,
otherwise a later regression would hide as another expected failure.
``ledger_issues`` is the one rule the structure check and the runner share.
"""
import ast
import json
from pathlib import Path
import unittest

TESTS = Path(__file__).resolve().parents[1]
LEDGER = TESTS / 'known_defects.json'
FIELDS = ('id', 'summary', 'category', 'reproduction', 'found_by', 'missed_kind', 'status')
STATUSES = ('open', 'closed')


def known_defect(defect_id):
    def mark(test):
        test = unittest.expectedFailure(test)
        test.do_math_known_defect = defect_id
        return test
    return mark


def read_ledger(path=LEDGER):
    return json.loads(Path(path).read_text(encoding='utf-8'))['defects']


def find_marks(root=TESTS):
    """{defect id: [test ids]} for every ``@known_defect('...')`` under ``root``'s packages."""
    marks = {}
    for path in sorted(Path(root).rglob('test_*.py')):
        module = '.'.join(path.relative_to(root).with_suffix('').parts)
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if not isinstance(node, ast.ClassDef):
                continue
            for method in node.body:
                if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                for decorator in method.decorator_list:
                    if (isinstance(decorator, ast.Call) and getattr(decorator.func, 'id', None) == 'known_defect'
                            and decorator.args and isinstance(decorator.args[0], ast.Constant)):
                        marks.setdefault(decorator.args[0].value, []).append(
                            f'{module}.{node.name}.{method.name}')
    return marks


def ledger_issues(entries, marks, moved=None):
    """Issues between the ledger and the marks.

    An open entry's marks are its reproduction and, beside it, only the moved old
    tests that ``moved`` names for it (설계 9.1, A28): an old test that pinned the
    defect, or that the defect breaks on the real path, is moved as it was and
    keeps the entry's mark. ``moved`` maps a defect id to those new test ids, as
    the migration dispositions' ``known_defect`` fields give them.
    """
    moved = moved or {}
    issues = []
    known = {}
    for entry in entries:
        if set(entry) != set(FIELDS) or entry['status'] not in STATUSES:
            issues.append({'rule': 'entry_shape', 'id': entry.get('id')})
            continue
        known[entry['id']] = entry
        marked = marks.get(entry['id'], [])
        if entry['status'] == 'closed':
            if marked:
                issues.append({'rule': 'closed_entry_still_marked', 'id': entry['id'], 'tests': marked})
        elif not marked:
            issues.append({'rule': 'open_entry_without_mark', 'id': entry['id']})
        elif entry['reproduction'] not in marked or not set(marked) - {entry['reproduction']} <= moved.get(entry['id'], set()):
            issues.append({'rule': 'reproduction_mismatch', 'id': entry['id'], 'tests': marked})
    for defect_id, tests in marks.items():
        if defect_id not in known and not any(issue.get('id') == defect_id for issue in issues):
            issues.append({'rule': 'mark_without_entry', 'id': defect_id, 'tests': tests})
    return issues


def moved_marks(root=TESTS):
    """{defect id: new test ids} of the moved old tests whose dispositions name the defect (``known_defect``)."""
    moved = {}
    for path in sorted((Path(root) / 'migration' / 'dispositions').glob('*.json')):
        for entry in json.loads(path.read_text(encoding='utf-8')).get('legacy', []):
            if entry.get('known_defect'):
                moved.setdefault(entry['known_defect'], set()).update(entry.get('new_ids', []))
    return moved


def open_count(path=LEDGER):
    return sum(entry['status'] == 'open' for entry in read_ledger(path))
