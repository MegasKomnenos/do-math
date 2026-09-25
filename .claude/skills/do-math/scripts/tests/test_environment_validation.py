"""Cached environments need real validation evidence, not a build-method label."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import setup_lean
from do_math.initialization import digest, trust_environment_errors
from research_fixtures import trust_fixture
from test_categories import test_group


@test_group('unit')
class EnvironmentValidationTests(unittest.TestCase):
    def test_inventory_does_not_silently_collapse_ambiguous_path_identities(self):
        from do_math import trust_inventory
        with tempfile.TemporaryDirectory() as directory:
            request=trust_fixture(Path(directory),['lean'])
            folder=Path(directory)/'synthetic-trust/toolchain/bin'
            (folder/'one.txt').write_bytes(b'one');(folder/'two.txt').write_bytes(b'two')
            key=trust_inventory._key
            def ambiguous(path):
                value=Path(path)
                return key(value.with_name('one.txt') if value.name=='two.txt' else value)
            with patch.object(trust_inventory,'_key',side_effect=ambiguous):
                with self.assertRaisesRegex(ValueError,'ambiguous identity'):
                    trust_inventory.inventory(request['manifest']['scope'])

    def test_compiler_job_does_not_inherit_unregistered_library_overrides(self):
        from do_math import formal
        with tempfile.TemporaryDirectory() as directory, \
             patch.dict('os.environ',{'LEAN_PATH':'outside','LEAN_SYSROOT':'outside','LAKE_HOME':'outside'}), \
             patch.object(formal,'WindowsJob',side_effect=RuntimeError('observe job arguments')) as job:
            with self.assertRaisesRegex(RuntimeError,'observe job arguments'):
                formal._job_run(['unused-compiler'],Path(directory))
        supplied=job.call_args.kwargs['env']
        self.assertNotIn('LEAN_PATH',supplied)
        self.assertNotIn('LEAN_SYSROOT',supplied)
        self.assertNotIn('LAKE_HOME',supplied)

    def test_inventory_detects_omissions_additions_and_unrelated_executables(self):
        from do_math.trust_validation import verify_environment_files
        with tempfile.TemporaryDirectory() as directory:
            request=trust_fixture(Path(directory),['lean'])
            environment={key:value for key,value in request.items() if key!='operation'}
            environment.update(source_ref='test',manifest_sha256=digest(request['manifest']))
            library=Path(directory)/'synthetic-trust/toolchain/bin/runtime.dll'
            library.write_bytes(b'new dependency')
            result=verify_environment_files(environment)
            self.assertEqual(result['status'],'invalid')
            self.assertIn(str(library).lower(),[p.lower() for p in result['missing_files']])
            library.unlink()
            environment['manifest']['files'].pop(0)
            environment['manifest_sha256']=digest(environment['manifest'])
            self.assertTrue(any('configured executable' in error for error in trust_environment_errors(environment)))

    def test_success_label_cannot_replace_failed_or_mismatched_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            request=trust_fixture(Path(directory),['lean'])
            environment={key:value for key,value in request.items() if key!='operation'}
            environment['source_ref']='test'
            record=environment['manifest']['validation']['record']
            for field,value in [('exit_code',17),('source_text','example : False := by sorry'),
                                ('toolchain_after',{}),('stdout',None)]:
                with self.subTest(field=field):
                    old=record[field];record[field]=value
                    environment['manifest']['validation']['sha256']=digest(record)
                    environment['manifest_sha256']=digest(environment['manifest'])
                    self.assertTrue(trust_environment_errors(environment,verify_files=False))
                    record[field]=old

    def test_external_search_roots_are_not_covered_by_an_unchanged_local_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            request=trust_fixture(Path(directory),['lean'])
            environment={key:value for key,value in request.items() if key!='operation'}
            chain=environment['toolchain']
            chain['project']['search_paths']=[str((Path(directory)/'outside').resolve())]
            record=environment['manifest']['validation']['record']
            from copy import deepcopy
            record['toolchain']=deepcopy(chain);record['toolchain_after']=deepcopy(chain)
            environment['manifest']['validation']['sha256']=digest(record)
            environment.update(source_ref='test',manifest_sha256=digest(environment['manifest']))
            self.assertTrue(any('search path is outside' in error for error in trust_environment_errors(environment)))

    def test_membership_changes_during_scan_are_not_verified(self):
        from do_math.trust_validation import verify_environment_files
        with tempfile.TemporaryDirectory() as directory:
            request=trust_fixture(Path(directory),['lean'])
            environment={key:value for key,value in request.items() if key!='operation'}
            environment.update(source_ref='test',manifest_sha256=digest(request['manifest']))
            def add_file(progress):
                (Path(directory)/'synthetic-trust/toolchain/bin/late.dll').write_bytes(b'late')
            result=verify_environment_files(environment,on_progress=add_file)
            self.assertEqual(result['status'],'invalid')
            self.assertIn('inventory membership changed during observation',result['errors'])

    def test_large_manifest_rechecks_every_file_and_keeps_ordered_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = trust_fixture(root, ['lean'])
            environment = {key: value for key, value in request.items() if key != 'operation'}
            files = environment['manifest']['files']
            for i in range(40):
                path = root / 'synthetic-trust/project/.lake/build' / f'module-{i}'
                path.write_bytes(b'original')
                files.append({'role':'mathlib_build', 'path':str(path.resolve()),
                              'sha256':hashlib.sha256(b'original').hexdigest()})
            validation=environment['manifest']['validation']
            validation['record']['inventory_sha256']=digest({'scope':environment['manifest']['scope'],'files':files})
            validation['sha256']=digest(validation['record'])
            environment.update(source_ref='test', manifest_sha256=digest(environment['manifest']))
            self.assertEqual(trust_environment_errors(environment), [])
            changed, missing = files[-2]['path'], files[-1]['path']
            Path(changed).write_bytes(b'changed')
            Path(missing).unlink()
            files.append(dict(files[0]))
            files.append({'role':'checker','path':'relative','sha256':'0'*64})
            environment['manifest_sha256'] = digest(environment['manifest'])
            # A malformed manifest fails before any live observation.
            self.assertEqual(trust_environment_errors(environment), [
                'duplicate manifest path', 'manifest file must have an absolute path'])
            self.assertEqual(trust_environment_errors(environment, verify_files=False), [
                'duplicate manifest path', 'manifest file must have an absolute path'])
            del files[-2:]
            environment['manifest_sha256'] = digest(environment['manifest'])
            self.assertEqual(trust_environment_errors(environment), ['inventory membership differs'])
            Path(missing).write_bytes(b'original')
            self.assertEqual(trust_environment_errors(environment), ['trust file changed: ' + changed])

    def test_structure_never_resolves_host_paths_and_live_hashing_streams(self):
        from do_math.trust_validation import verify_environment_files
        with tempfile.TemporaryDirectory() as directory:
            request = trust_fixture(Path(directory), ['lean'])
            environment = {key:value for key,value in request.items() if key != 'operation'}
            environment.update(source_ref='test', manifest_sha256=digest(request['manifest']))
            with patch.object(Path, 'resolve', side_effect=AssertionError('host access')):
                self.assertEqual(trust_environment_errors(environment, verify_files=False), [])
            with patch.object(Path, 'read_bytes', side_effect=AssertionError('whole file read')):
                result = verify_environment_files(environment, workers=2)
            self.assertEqual(result['status'], 'verified')
            self.assertLessEqual(result['peak_pending'], 4)
            self.assertEqual(result['completed_files'], 6)
            stopped = verify_environment_files(environment, should_stop=lambda:True)
            self.assertEqual(stopped['status'], 'cancelled')
            self.assertEqual(stopped['read_bytes'], 0)

    def test_cached_environment_requires_evidence_and_unchanged_files(self):
        with tempfile.TemporaryDirectory() as directory:
            request = trust_fixture(Path(directory), ['lean'])
            environment = {key: value for key, value in request.items() if key != 'operation'}
            environment.update(source_ref='explicit-test-adoption', manifest_sha256=digest(request['manifest']))
            self.assertEqual(trust_environment_errors(environment), [])
            entry = environment['manifest']['files'][-1]
            Path(entry['path']).write_bytes(b'changed checker')
            self.assertTrue(any('trust file changed' in error for error in trust_environment_errors(environment)))
            environment['manifest']['validation'].pop('record')
            environment['manifest_sha256'] = digest(environment['manifest'])
            self.assertIn('trust validation requires a sealed self-contained record', trust_environment_errors(environment))

    def test_unknown_manifest_field_is_not_silently_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            request = trust_fixture(Path(directory), ['lean'])
            environment = {key: value for key, value in request.items() if key != 'operation'}
            environment['manifest']['unrecognized'] = True
            environment.update(source_ref='test', manifest_sha256=digest(environment['manifest']))
            self.assertIn('trust manifest fields differ from the current contract', trust_environment_errors(environment))

    def test_validation_preserves_source_output_and_exact_toolchain(self):
        with tempfile.TemporaryDirectory() as directory:
            chain = {'identity': 'synthetic test environment','project':{'fixture':True}}
            with patch.object(setup_lean, 'inspect_toolchain', return_value=chain), \
                    patch.object(setup_lean,'collect_inventory',return_value={'scope':{'roots':[]},'files':[]}), \
                    patch('do_math.formal._job_run', return_value=(0, 'ok', '', False)) as run:
                result = setup_lean.verify_environment(['test-lean'], Path(directory))
            self.assertEqual(result['status'], 'verified')
            record = json.loads(Path(result['evidence_path']).read_text(encoding='utf-8'))
            self.assertEqual(record['scope'], 'mathlib_import_and_representative_proofs')
            self.assertEqual(record['command'], run.call_args.args[0])
            self.assertEqual(record['stdout'], 'ok')
            self.assertEqual(record['toolchain_after'], chain)
            self.assertEqual(record['source_sha256'], hashlib.sha256(Path(record['source']).read_bytes()).hexdigest())

    def test_failure_and_toolchain_change_never_produce_verified_evidence(self):
        for exit_code, after in [(1, 'before'), (0, 'changed')]:
            with self.subTest(exit_code=exit_code, after=after), tempfile.TemporaryDirectory() as directory:
                with patch.object(setup_lean, 'inspect_toolchain', side_effect=[{'identity':'before'}, {'identity':after}]), \
                        patch.object(setup_lean,'collect_inventory',return_value={'scope':{'roots':[]},'files':[]}), \
                        patch('do_math.formal._job_run', return_value=(exit_code, '', 'diagnostic', False)):
                    result = setup_lean.verify_environment(['test-lean'], Path(directory))
                self.assertEqual(result['status'], 'failed')
                record = json.loads(Path(result['evidence_path']).read_text(encoding='utf-8'))
                self.assertEqual(record['stderr'], 'diagnostic')

    def test_library_change_with_unchanged_toolchain_metadata_fails_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            chain={'identity':'same executable metadata'}
            before={'scope':{'roots':[]},'files':[{'path':'dependency','sha256':'a'*64}]}
            after={'scope':{'roots':[]},'files':[{'path':'dependency','sha256':'b'*64}]}
            with patch.object(setup_lean,'inspect_toolchain',return_value=chain), \
                 patch.object(setup_lean,'collect_inventory',side_effect=[before,after]), \
                 patch('do_math.formal._job_run',return_value=(0,'','',False)):
                result=setup_lean.verify_environment(['test-lean'],Path(directory))
            self.assertEqual(result['status'],'failed')
            self.assertIsNone(result['inventory_path'])
