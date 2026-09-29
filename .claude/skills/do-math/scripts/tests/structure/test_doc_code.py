"""The operating and role documents name only commands and options the product has (의무 13-C).

The documents are ``SKILL.md`` and ``references/*.md``. A command is named as
``do_math.py <command>``; an option as a code span starting with ``--``. The
commands are those of the CLI's own parser (``cli_contract.build_parser``); the
options are every ``add_argument`` flag of the product's tools and every flag
string the product puts into a provider CLI's argv. A renamed or removed command
or option then fails here instead of in an operator's session (조사 B-21,
운전 인터페이스 공백).
"""
import ast
from pathlib import Path
import re
import unittest

SKILL = Path(__file__).resolve().parents[3]
SCRIPTS = SKILL / 'scripts'
COMMAND = re.compile(r'do_math\.py ([a-z][a-z-]*)')
OPTION = re.compile(r'`(--[a-z][a-z-]*)')


def _documents():
    return [SKILL / 'SKILL.md', *sorted((SKILL / 'references').glob('*.md'))]


def _vocabulary():
    """``(commands, options)``: the CLI parser's commands, and every flag string in the product's code."""
    from do_math.cli_contract import _command_parsers, build_parser
    commands = set(_command_parsers(build_parser()))
    options = set()
    for path in [*SCRIPTS.joinpath('do_math').rglob('*.py'), *SCRIPTS.glob('*.py')]:
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and re.fullmatch(r'--[a-z][a-z-]*', node.value):
                options.add(node.value)
    return commands, options


class DocumentCodeTests(unittest.TestCase):
    def test_documented_commands_and_options_exist(self):
        commands, options = _vocabulary()
        self.assertGreater(len(commands), 0)
        missing = []
        for document in _documents():
            text = document.read_text(encoding='utf-8')
            missing += [(document.name, 'command', name) for name in COMMAND.findall(text) if name not in commands]
            missing += [(document.name, 'option', name) for name in OPTION.findall(text) if name not in options]
        self.assertEqual(sorted(set(missing)), [])


if __name__ == '__main__':
    unittest.main()
