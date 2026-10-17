"""실제 설치의 동결 생산물에서 한 필드씩 바꿔 검증한다.

최초 동결은 전체 설치를 읽는다. 시험별 사본 복사 비용은 아직 미측정이며 흐름 층에서 확인한다.
"""
from contextlib import redirect_stdout
from copy import deepcopy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

import operator_bootstrap as bootstrap
from do_math import file_io
from do_math.values import json_digest
from support.provider_probes import ObservedCalls, settle


class BootstrapContractTests(unittest.TestCase):
    def test_frozen_start_reports_live_target_drift_against_preserved_manifest(self):
        source = self.root / 'small-installation'
        source.joinpath('scripts/do_math').mkdir(parents=True)
        source.joinpath('scripts/do_math/scheduled_operator.py').write_bytes(b'original supervisor\n')
        source.joinpath('SKILL.md').write_bytes(b'original document\n')
        receipt = bootstrap.freeze(source, self.root / 'small-workspace')
        manifest = bootstrap.verify_snapshot(Path(receipt['manifest']))
        self.assertEqual(bootstrap.startup_evidence(manifest)['comparison'], 'match')
        source.joinpath('SKILL.md').write_bytes(b'repaired document\n')
        source.joinpath('added.txt').write_bytes(b'new\n')
        source.joinpath('scripts/do_math/scheduled_operator.py').unlink()
        result = bootstrap.startup_evidence(manifest)
        self.assertEqual(result['comparison'], 'different')
        self.assertEqual(result['snapshot_sha256'], receipt['snapshot_sha256'])
        self.assertEqual(result['differences'], [
            {'path': 'SKILL.md', 'expected_sha256': hashlib.sha256(b'original document\n').hexdigest(),
             'observed_sha256': hashlib.sha256(b'repaired document\n').hexdigest()},
            {'path': 'added.txt', 'expected_sha256': None, 'observed_sha256': hashlib.sha256(b'new\n').hexdigest()},
            {'path': 'scripts/do_math/scheduled_operator.py',
             'expected_sha256': hashlib.sha256(b'original supervisor\n').hexdigest(), 'observed_sha256': None}])
        self.assertEqual(bootstrap.verify_snapshot(Path(receipt['manifest'])), manifest)
        self.assertEqual(bootstrap.startup_evidence(None), {'mode': 'live', 'comparison': 'no_recorded_manifest'})

    @classmethod
    def setUpClass(cls):
        old_path, old_flag = list(sys.path), sys.dont_write_bytecode
        cls.addClassCleanup(setattr, sys, 'dont_write_bytecode', old_flag)
        cls.addClassCleanup(lambda: sys.path.__setitem__(slice(None), old_path))
        temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(temporary.cleanup)
        cls.source = Path(file_io.__file__).resolve().parents[2]
        cls.receipt = bootstrap.freeze(cls.source, Path(temporary.name))
        cls.seed = Path(cls.receipt['manifest']).parent

    def setUp(self):
        old_path, old_flag = list(sys.path), sys.dont_write_bytecode
        self.addCleanup(setattr, sys, 'dont_write_bytecode', old_flag)
        self.addCleanup(lambda: sys.path.__setitem__(slice(None), old_path))
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.snapshot = self.root / self.seed.name
        shutil.copytree(self.seed, self.snapshot)
        self.path = self.snapshot / bootstrap.MANIFEST
        self.manifest = json.loads(self.path.read_bytes())

    def write_manifest(self, value):
        self.path.write_text(json.dumps(value), encoding='utf-8')

    def reseal(self, value):
        # 경로 방어까지 진행하려면 상위 식별자는 실제 제품 해시 규칙으로 다시 봉인한다.
        basis = {key: value[key] for key in ('format', 'installation_root', 'files')}
        value['snapshot_sha256'] = json_digest(basis)
        target = self.snapshot.with_name(value['snapshot_sha256'])
        self.snapshot.rename(target)
        self.snapshot, self.path = target, target / bootstrap.MANIFEST
        self.write_manifest(value)

    def test_source_set_and_hashes_match_actual_installation_bytes(self):
        paths = bootstrap._source_paths(self.source, file_io)
        expected = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()}
        self.assertEqual(bootstrap._source_files(self.source, file_io), expected)
        self.assertEqual(self.manifest['files'], expected)
        self.assertNotIn(bootstrap.MANIFEST, paths)
        self.assertNotIn(bootstrap.MARKS, paths)
        self.assertEqual(bootstrap.verify_snapshot(self.path), self.manifest)

    def test_invalid_manifest_shape_is_rejected_without_rewriting_it(self):
        for value in ([], {**self.manifest, 'extra': True},
                      {key: value for key, value in self.manifest.items() if key != 'files'}):
            with self.subTest(value_type=type(value).__name__):
                self.write_manifest(value)
                before = self.path.read_bytes()
                with self.assertRaisesRegex(ValueError, '^invalid bootstrap manifest$'):
                    bootstrap.verify_snapshot(self.path)
                self.assertEqual(self.path.read_bytes(), before)

    def test_unsupported_format_is_rejected_before_identity(self):
        self.write_manifest({**self.manifest, 'format': bootstrap.FORMAT + 1})
        with self.assertRaisesRegex(ValueError, '^unsupported bootstrap manifest$'):
            bootstrap.verify_snapshot(self.path)
        self.assertEqual(json.loads(self.path.read_bytes())['format'], bootstrap.FORMAT + 1)

    def test_nonobject_files_are_rejected_before_identity(self):
        self.write_manifest({**self.manifest, 'files': []})
        with self.assertRaisesRegex(ValueError, '^unsupported bootstrap manifest$'):
            bootstrap.verify_snapshot(self.path)
        self.assertEqual(json.loads(self.path.read_bytes())['files'], [])

    def test_changed_installation_identity_is_rejected(self):
        self.write_manifest({**self.manifest, 'installation_root': str(self.root / 'other')})
        with self.assertRaisesRegex(ValueError, '^bootstrap manifest identity mismatch$'):
            bootstrap.verify_snapshot(self.path)
        self.assertEqual(self.snapshot.name, self.manifest['snapshot_sha256'])

    def test_wrong_directory_identity_is_rejected(self):
        renamed = self.root / 'wrong-identity'
        self.snapshot.rename(renamed)
        with self.assertRaisesRegex(ValueError, '^bootstrap directory identity mismatch$'):
            bootstrap.verify_snapshot(renamed / bootstrap.MANIFEST)
        self.assertEqual(json.loads((renamed / bootstrap.MANIFEST).read_bytes()), self.manifest)

    def test_noncanonical_and_escaping_file_names_are_rejected(self):
        original_name, digest = next(iter(self.manifest['files'].items()))
        for name in ('../escape', '/absolute', 'scripts//double.py', 'scripts\\escape.py', './SKILL.md'):
            with self.subTest(name=name):
                value = deepcopy(self.manifest)
                del value['files'][original_name]
                value['files'][name] = digest
                self.reseal(value)
                with self.assertRaisesRegex(ValueError, '^invalid bootstrap file path$'):
                    bootstrap.verify_snapshot(self.path)
                self.assertEqual(json.loads(self.path.read_bytes()), value)

    def test_directory_cannot_replace_a_manifest_file(self):
        name = 'SKILL.md'
        target = self.snapshot / name
        target.unlink()
        target.mkdir()
        with self.assertRaisesRegex(ValueError, '^bootstrap file escaped its snapshot$'):
            bootstrap.verify_snapshot(self.path)
        self.assertTrue(target.is_dir())

    def test_changed_frozen_bytes_are_rejected_without_cache_publication(self):
        target = self.snapshot / 'SKILL.md'
        before = (self.snapshot / bootstrap.MARKS).read_bytes() if (self.snapshot / bootstrap.MARKS).exists() else None
        target.write_bytes(target.read_bytes() + b'\nchanged edition\n')
        with self.assertRaisesRegex(ValueError, '^bootstrap file hash mismatch: SKILL.md$'):
            bootstrap.verify_snapshot(self.path)
        marker = self.snapshot / bootstrap.MARKS
        self.assertEqual(marker.read_bytes() if marker.exists() else None, before)

    def test_unlisted_file_is_rejected(self):
        extra = self.snapshot / 'operator-unlisted.txt'
        extra.write_bytes(b'unlisted')
        with self.assertRaisesRegex(ValueError, '^bootstrap snapshot has unlisted or missing files$'):
            bootstrap.verify_snapshot(self.path)
        self.assertEqual(extra.read_bytes(), b'unlisted')

    def test_missing_manifest_entry_is_rejected_after_remaining_files_verify(self):
        value = deepcopy(self.manifest)
        del value['files']['SKILL.md']
        self.reseal(value)
        with self.assertRaisesRegex(ValueError, '^bootstrap snapshot has unlisted or missing files$'):
            bootstrap.verify_snapshot(self.path)
        self.assertTrue((self.snapshot / 'SKILL.md').is_file())

    def test_absent_invalid_and_nonobject_marks_are_rebuilt_from_files(self):
        marker = self.snapshot / bootstrap.MARKS
        for contents in (None, b'{', b'[]'):
            with self.subTest(contents=contents):
                marker.unlink(missing_ok=True)
                if contents is not None:
                    marker.write_bytes(contents)
                self.assertEqual(bootstrap._marks(self.snapshot), {})
                for name in self.manifest['files']:
                    settle(self.snapshot / name)
                self.assertEqual(bootstrap.verify_snapshot(self.path), self.manifest)
                self.assertEqual(set(bootstrap._marks(self.snapshot)), set(self.manifest['files']))

    def test_settled_cache_skips_hashes_and_unchanged_marker_write(self):
        for name in self.manifest['files']:
            settle(self.snapshot / name)
        bootstrap.verify_snapshot(self.path)
        marker = self.snapshot / bootstrap.MARKS
        before = marker.read_bytes()
        with ObservedCalls(hash=file_io.sha256_file, write=file_io.write_bytes_atomic) as calls:
            result = bootstrap.verify_snapshot(self.path)
        self.assertEqual(result, self.manifest)
        self.assertEqual((calls.count('hash'), calls.count('write')), (0, 0))
        self.assertEqual(marker.read_bytes(), before)

    def test_future_file_time_never_becomes_a_trusted_fingerprint(self):
        target = self.snapshot / 'SKILL.md'
        future = 4_102_444_800_000_000_000
        os.utime(target, ns=(future, future))
        with ObservedCalls(hash=file_io.sha256_file) as first:
            self.assertEqual(bootstrap.verify_snapshot(self.path), self.manifest)
        with ObservedCalls(hash=file_io.sha256_file) as second:
            self.assertEqual(bootstrap.verify_snapshot(self.path), self.manifest)
        for observed in (first, second):
            self.assertEqual(sum(Path(call['path']) == target for call in observed.captured('hash')), 1)
        self.assertNotIn('SKILL.md', bootstrap._marks(self.snapshot))

    def test_existing_snapshot_is_verified_and_returns_exact_receipt(self):
        workspace = self.root / 'reuse'
        expected = bootstrap.freeze(self.source, workspace)
        with ObservedCalls(copy=shutil.copyfile) as calls:
            actual = bootstrap.freeze(self.source, workspace)
        self.assertEqual(actual, expected)
        self.assertEqual(calls.count('copy'), 0)
        self.assertEqual(list((workspace / 'operator/bootstrap').iterdir()), [Path(expected['manifest']).parent])

    def test_installation_without_supervisor_creates_no_bootstrap(self):
        installation = self.root / 'empty-installation'
        installation.mkdir()
        workspace = self.root / 'unused-workspace'
        with self.assertRaisesRegex(ValueError, '^installation has no supervisor$'):
            bootstrap.freeze(installation, workspace)
        self.assertFalse(workspace.exists())

    def test_installation_change_during_copy_cleans_only_new_staging(self):
        installation = self.root / 'installation'
        shutil.copytree(self.seed, installation)
        workspace = self.root / 'workspace'
        changed = []
        def change_after_first_read(arguments):
            if not changed:
                path = installation / 'SKILL.md'
                path.write_bytes(path.read_bytes() + b'\nconcurrent change\n')
                changed.append(path)
            return dict(arguments)
        with ObservedCalls(copy=shutil.copyfile, capture={'copy': change_after_first_read}):
            with self.assertRaisesRegex(ValueError, '^installation changed while freezing supervisor$'):
                bootstrap.freeze(installation, workspace)
        self.assertEqual(changed, [installation / 'SKILL.md'])
        self.assertEqual(list((workspace / 'operator/bootstrap').iterdir()), [])
        self.assertTrue((installation / 'SKILL.md').read_bytes().endswith(b'concurrent change\n'))

    def test_concurrent_identical_publication_reuses_verified_winner(self):
        workspace = self.root / 'workspace'
        winners = []
        def publish(arguments):
            source, target = arguments['self'], Path(arguments['target'])
            if source.name.startswith('.building-') and not winners:
                shutil.copytree(source, target)
                winners.append(target)
            return dict(arguments)
        with ObservedCalls(rename=Path.rename, capture={'rename': publish}):
            receipt = bootstrap.freeze(self.source, workspace)
        self.assertEqual(winners, [Path(receipt['manifest']).parent])
        self.assertEqual(list((workspace / 'operator/bootstrap').iterdir()), winners)
        self.assertEqual(bootstrap.verify_snapshot(Path(receipt['manifest']))['files'], self.manifest['files'])

    def test_freeze_cli_prints_exact_verified_receipt(self):
        workspace = self.root / 'cli-workspace'
        output = io.StringIO()
        with redirect_stdout(output):
            code = bootstrap.main(['--freeze', '--installation-root', str(self.source), '--workspace', str(workspace)])
        actual = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(actual, {'entrypoint': str(workspace / 'operator/bootstrap' / self.seed.name / 'scripts/operator_bootstrap.py'),
            'manifest': str(workspace / 'operator/bootstrap' / self.seed.name / bootstrap.MANIFEST),
            'snapshot_sha256': self.seed.name})
        self.assertEqual(bootstrap.verify_snapshot(Path(actual['manifest'])), self.manifest)

    def test_live_info_does_not_create_a_manifest(self):
        output = io.StringIO()
        with redirect_stdout(output):
            code = bootstrap.main(['--bootstrap-info'])
        self.assertEqual((code, json.loads(output.getvalue())), (0, {'mode': 'live', 'manifest': None}))
        self.assertFalse((self.source / bootstrap.MANIFEST).exists())

    def test_bootstrap_loads_local_file_helpers_and_uses_canonical_digest(self):
        old_path, old_flag = list(sys.path), sys.dont_write_bytecode
        self.addCleanup(setattr, sys, 'dont_write_bytecode', old_flag)
        self.addCleanup(lambda: sys.path.__setitem__(slice(None), old_path))
        self.assertIs(bootstrap._file_io(), file_io)
        self.assertTrue(sys.dont_write_bytecode)
        self.assertEqual(sys.path[0], str(Path(bootstrap.__file__).resolve().parent))
        self.assertEqual(bootstrap._json_digest({'b': 2, 'a': 1}), hashlib.sha256(b'{"a":1,"b":2}').hexdigest())
