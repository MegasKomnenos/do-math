"""Storage families and their producers name the same fields (의무 1-A for the storage-family pair; 설계 10절 A22).

Most writers of stored records are engine methods, so their outputs are checked
where the new tests publish through the real storage validation (설계 4.3) and
the write branches are reached (의무 1-B, T3). Two checks here cover the whole
product at once:

- Every lifecycle event call (``_lifecycle_event(kind, **fields)``) passes only
  fields the closed event schema declares (조사 C-03, C-17, C-22: a producer field
  the closed schema does not declare stops the instance on publication).
- Every field of a closed stored family is named somewhere in the product
  outside the schema modules, so a receiver does not require or accept a field
  no producer writes (조사 B-02). ``UNPRODUCED`` declares the fields no code
  names, each with its reason; a new such field, or a declared one that gains a
  producer, fails. The check is by name: a field whose name the code uses for
  anything counts as produced, so it finds only names no code uses at all.
"""
import ast
import inspect
from pathlib import Path
import unittest


PRODUCT = Path(__file__).resolve().parents[2] / 'do_math'
SCHEMA_MODULES = {'record_schemas', 'state_contract.py'}
# Event calls whose fields a static check cannot see or that are known defects.
EVENT_CALLS = {
    ('core_engine.py', 'submission_checked'): 'passes **details; the caller builds only basis (EVIDENCE)',
}
_IGNORED_SETTING = ('accepted by the configuration schema but read or written by no product code, so setting it '
                    'changes nothing; stage 2 removes or wires it')
UNPRODUCED = {('research', 'config', key): _IGNORED_SETTING for key in (
    'contract_revision_limit', 'exhaustion_empty_limit', 'import_rework_limit', 'proposal_version_limit',
    'selection_failure_limit')}


def _event_calls():
    """``(file, kind, fields, has_star)`` for every ``_lifecycle_event`` call."""
    from do_math.lifecycle_engine import LifecycleEngineMixin
    parameters = set(inspect.signature(LifecycleEngineMixin._lifecycle_event).parameters)
    for path in sorted(PRODUCT.rglob('*.py')):
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == '_lifecycle_event':
                kind = node.args[0].value if node.args and isinstance(node.args[0], ast.Constant) else None
                fields = {keyword.arg for keyword in node.keywords if keyword.arg} - parameters
                yield path.name, kind, fields, any(keyword.arg is None for keyword in node.keywords)


def _named_in_product():
    """Every string constant and keyword name in the product outside the schema modules."""
    names = set()
    scripts = PRODUCT.parent
    files = [*PRODUCT.rglob('*.py'), *(path for path in scripts.glob('*.py') if path.name not in {'run_tests.py', 'test_categories.py'})]
    for path in files:
        relative = path.relative_to(PRODUCT).as_posix() if path.is_relative_to(PRODUCT) else path.name
        if relative.split('/')[0] in SCHEMA_MODULES:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                names.add(node.value)
            elif isinstance(node, ast.keyword) and node.arg:
                names.add(node.arg)
    return names


def _event_fields():
    from do_math.state_contract import default_state_contract
    return set(default_state_contract().family('runtime', 'events').schema['properties'])


class StorageFieldTests(unittest.TestCase):
    def test_every_lifecycle_event_call_passes_only_declared_event_fields(self):
        declared, seen = _event_fields(), set()
        for name, kind, fields, star in _event_calls():
            if (name, kind) in EVENT_CALLS:
                seen.add((name, kind))
                continue
            with self.subTest(call=(name, kind)):
                self.assertFalse(star, 'a **details call must be declared with what it passes')
                self.assertEqual(sorted(fields - declared), [], 'fields the closed event schema rejects')
        self.assertEqual(seen, set(EVENT_CALLS), 'declared event calls that no longer exist')

    def test_every_field_of_a_closed_family_is_named_by_the_product(self):
        from do_math.state_contract import default_state_contract
        named = _named_in_product()
        unproduced = {(family.root, family.name, field) for family in default_state_contract().families()
                      if family.shape in ('map', 'list') or family.schema.get('additionalProperties') is False
                      for field in family.schema.get('properties', {}) if field not in named}
        self.assertEqual(sorted(unproduced - set(UNPRODUCED)), [], 'stored fields no product code names')
        self.assertEqual(sorted(set(UNPRODUCED) - unproduced), [], 'declared unproduced fields that now have a producer')

    def test_the_trust_rebind_event_passes_only_declared_event_fields(self):
        declared = _event_fields()
        fields = next(fields for name, kind, fields, _ in _event_calls()
                      if (name, kind) == ('formal_engine.py', 'trust_environment_rebound'))
        self.assertEqual(sorted(fields - declared), [])


if __name__ == '__main__':
    unittest.main()
