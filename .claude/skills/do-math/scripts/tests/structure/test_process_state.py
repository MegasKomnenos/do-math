"""New empty mutable process tables cannot quietly escape the restart registry."""
import ast
from pathlib import Path
import unittest

from support.process_state import MAPPINGS, PRODUCT

DECLARATIONS = {
    ('layers', 'PENDING'): 'layer declarations, not observed process facts',
    ('record_schemas.schemas', 'RECORDS'): 'schema declarations filled during import',
}


def empty_table(value):
    if isinstance(value, ast.Dict):
        return not value.keys
    if isinstance(value, (ast.List, ast.Set)):
        return not value.elts
    return (isinstance(value, ast.Call) and not value.args and not value.keywords
            and isinstance(value.func, ast.Name)
            and value.func.id in {'dict', 'list', 'set', 'OrderedDict'})


class ProcessStateRegistryTests(unittest.TestCase):
    def test_empty_mutable_product_globals_are_process_facts_or_reasoned_declarations(self):
        registered = {(module, attribute) for module, attributes in MAPPINGS.items()
                      for attribute in attributes}
        found = set()
        for path in PRODUCT.rglob('*.py'):
            module = path.relative_to(PRODUCT).with_suffix('').as_posix().replace('/', '.')
            for node in ast.parse(path.read_text(encoding='utf-8')).body:
                if not isinstance(node, (ast.Assign, ast.AnnAssign)) or not empty_table(node.value):
                    continue
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                found.update((module, target.id) for target in targets if isinstance(target, ast.Name))
        self.assertEqual(sorted(found - registered - set(DECLARATIONS)), [],
                         'a new process table needs reset or a declaration reason')
        self.assertEqual(sorted(set(DECLARATIONS) - found), [], 'a stale declaration exemption')
        self.assertTrue(all(reason.strip() for reason in DECLARATIONS.values()))
