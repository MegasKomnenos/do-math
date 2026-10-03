"""설정 파일의 실제 바이트와 scholarly 쌍의 한 필드 오류를 검사한다."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math.scholarly import _pathlike, _validate, validate_scholarly_server
from do_math.scholarly_config import _absolute_from_config, _from_config, resolve_scholarly_server


class ScholarlyValidationTests(unittest.TestCase):
    def test_command_must_be_nonempty_nul_free_text(self):
        for command in ('', None, 7, 'py\x00thon'):
            with self.subTest(command=command):
                value = {'command': command, 'args': []}
                with self.assertRaisesRegex(ValueError, '^scholarly command must be a nonempty NUL-free string$'):
                    validate_scholarly_server(value)
                self.assertEqual(value, {'command': command, 'args': []})

    def test_args_must_be_a_list_of_nul_free_strings(self):
        for args in (None, (), 'server', [7], ['x\x00y']):
            with self.subTest(args=args):
                value = {'command': 'python', 'args': args}
                before = deepcopy(value)
                with self.assertRaisesRegex(ValueError, '^scholarly args must be NUL-free strings$'):
                    validate_scholarly_server(value)
                self.assertEqual(value, before)

    def test_pathlike_distinguishes_executable_names_from_file_paths(self):
        for value, expected in (('python', False), ('python.exe', True), ('a/b', True), ('a\\b', True), ('--flag', False)):
            with self.subTest(value=value):
                self.assertIs(_pathlike(value), expected)

    def test_relative_paths_require_config_and_result_copies_args(self):
        value = {'command': 'python.exe', 'args': ['server.py', 'literal/path']}
        result = _validate(value, allow_relative_paths=True)
        self.assertEqual(result, value)
        result['args'].append('new')
        self.assertEqual(value['args'], ['server.py', 'literal/path'])


class ScholarlyFileValidationTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.path = self.root / 'config.toml'

    def test_absolute_path_is_preserved_without_rebasing(self):
        absolute = str(self.root / 'not-required-to-exist.exe')
        self.assertEqual(_absolute_from_config(absolute, self.root / 'other', label='command'), absolute)
        self.assertFalse(Path(absolute).exists())

    def test_missing_relative_command_is_rejected(self):
        with self.assertRaisesRegex(ValueError, '^relative scholarly command does not name a file beside its configuration$'):
            _absolute_from_config('missing.exe', self.root, label='command')
        self.assertEqual(list(self.root.iterdir()), [])

    def test_directory_cannot_stand_for_server_file(self):
        (self.root / 'server.py').mkdir()
        with self.assertRaisesRegex(ValueError, '^relative scholarly server file does not name a file beside its configuration$'):
            _absolute_from_config('server.py', self.root, label='server file')
        self.assertTrue((self.root / 'server.py').is_dir())

    def test_malformed_toml_reports_its_source_and_leaves_bytes(self):
        self.path.write_bytes(b'[mcp_servers.scholarly\n')
        before = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, '^invalid Codex configuration at ') as caught:
            _from_config(self.path)
        self.assertEqual(str(caught.exception), 'invalid Codex configuration at ' + str(self.path))
        self.assertEqual(self.path.read_bytes(), before)

    def test_scholarly_entry_must_be_a_table(self):
        self.path.write_text('[mcp_servers]\nscholarly = "python"\n', encoding='utf-8')
        before = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, '^scholarly server configuration must be a table$'):
            _from_config(self.path)
        self.assertEqual(self.path.read_bytes(), before)

    def test_unrelated_or_scalar_server_table_has_no_scholarly_entry(self):
        for text in ('title="synthetic"\n', 'mcp_servers="synthetic"\n', '[mcp_servers.other]\ncommand="python"\n'):
            with self.subTest(text=text):
                self.path.write_text(text, encoding='utf-8')
                self.assertIsNone(_from_config(self.path))
                self.assertEqual(self.path.read_text(encoding='utf-8'), text)

    def test_existing_relative_files_are_resolved_and_literals_preserved(self):
        (self.root / 'python.exe').write_bytes(b'')
        (self.root / 'server.py').write_bytes(b'# synthetic')
        self.path.write_text('[mcp_servers.scholarly]\ncommand="python.exe"\nargs=["server.py", "literal/path"]\n', encoding='utf-8')
        self.assertEqual(_from_config(self.path), {'command': str(self.root / 'python.exe'),
                         'args': [str(self.root / 'server.py'), 'literal/path']})
        self.assertEqual((self.root / 'server.py').read_bytes(), b'# synthetic')

    def test_start_file_uses_nearest_parent_and_skips_unrelated_child_config(self):
        config = self.root / '.codex'
        config.mkdir()
        (config / 'config.toml').write_text('[mcp_servers.scholarly]\ncommand="python"\nargs=[]\n', encoding='utf-8')
        child = self.root / 'child'
        (child / '.codex').mkdir(parents=True)
        (child / '.codex' / 'config.toml').write_text('title="unrelated"\n', encoding='utf-8')
        self.assertEqual(resolve_scholarly_server(None, start=child / 'paper.txt', codex_home=config),
                         {'command': 'python', 'args': []})

    def test_absent_home_after_root_search_returns_none(self):
        # 실제 볼륨 루트에서 시작하면 사용자 홈의 조상 설정을 읽지 않는다.
        # 이 환경 전제를 명시 단언하고, 루트나 사용자 설정을 쓰지 않는다.
        anchor = Path(self.root.anchor)
        self.assertTrue(anchor.is_dir())
        self.assertFalse((anchor / '.codex' / 'config.toml').exists())
        home = self.root / 'absent-home'
        self.assertIsNone(resolve_scholarly_server(None, start=anchor, codex_home=home))
        self.assertFalse(home.exists())

    def test_already_checked_home_after_root_search_returns_none(self):
        anchor = Path(self.root.anchor)
        home = anchor / '.codex'
        self.assertTrue(anchor.is_dir())
        self.assertFalse((home / 'config.toml').exists())
        self.assertIsNone(resolve_scholarly_server(None, start=anchor, codex_home=home))
        self.assertFalse((home / 'config.toml').exists())
