"""정상 중앙 봉인 생산자의 바이트에서 증거 필드 하나씩 손상한다.
손상 입력마다 새 Git 저장소를 게시하여 봉인 불변성을 지킨다. 실측 최대 0.516초의 단위 예산 초과를 보고한다.
"""
from copy import deepcopy
import hashlib
from pathlib import Path
import re
import tempfile
import unittest

from do_math import submission
from do_math.canonical import canonical_json, exact_content_hash
from do_math.git_store import GitStateStore, GitStateStoreError
from support.fakes.git_backend import make_fake, make_repository
from support.submission_protocol import ProtocolScene, INSTANCE_ID


class SealedEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.scene = ProtocolScene(Path(self.temporary.name))
        self.read_number = 0
        s = self.scene
        self.sealed = submission.seal_submission(s.workspace, s.draft, execution_id='EX-worker',
            context=s.context, schema=s.schema, max_artifact_bytes=1024 * 1024, clock=s.clock)
        self.assertEqual((self.sealed['passed'], self.sealed['check']['issues']), (True, []))
        self.files = {'runtime/artifacts/BA-evidence/' + key: raw
                      for key, raw in self.sealed['artifacts'].items()}
        intent = {**self.sealed['intent'], **{name + '_ref': 'runtime/artifacts/BA-evidence/' + name + '.json'
                  for name in ('output', 'extensions', 'check')}}
        self.execution = {'id': 'EX-worker', 'submission_intent': intent,
            'submission_receipt': {'state': 'accepted', 'execution_id': 'EX-worker', 'payload': {
                'submission_check': {'artifacts': [{'path': path, 'bytes': len(raw),
                    'sha256': hashlib.sha256(raw).hexdigest()} for path, raw in self.files.items()]}}}}
        self.assertEqual(self.read(self.execution, self.files), {
            'output': s.output, 'extensions': {}, 'check': self.sealed['check'], 'output_ref': intent['output_ref']})

    def publish(self, files):
        """손상 변형마다 새 저장소에 게시하여 기존 봉인을 덮어쓰지 않는다."""
        s = self.scene
        self.read_number += 1
        store = GitStateStore(make_repository(s.root / ('read-' + str(self.read_number))),
                              INSTANCE_ID, backend=make_fake(), clock=s.clock)
        head = store.publish(None, {'research/transport-fixture.json': b'{}', **files}).head
        return store, head

    def read(self, execution, files):
        """실제 Git 포트 저장의 입력 바이트를 봉인 수신 함수로 전달한다."""
        store, head = self.publish(files)
        return submission.read_sealed_submission(execution, head,
            lambda path, snapshot: store.read_bytes(snapshot, path))

    def test_snapshot_summary_rejects_receipt_coordinates_mode_and_execution_drift(self):
        evidence = self.execution['submission_receipt']['payload']['submission_check']
        seal = {'event_seq': 1, 'capture_id': 'capture-one', 'execution_id': 'EX-worker',
                'state': 'accepted', 'submission_check': {**deepcopy(evidence),
                    'check_ref': self.execution['submission_intent']['check_ref']}}
        def summarize(row, files):
            store, head = self.publish(files)
            return submission.summarize_snapshot_checks([row], snapshot=head,
                read_artifact=lambda path, snapshot: store.read_bytes(snapshot, path), history_window=5), head
        actual, head = summarize(seal, self.files)
        self.assertEqual(actual, {'history_window': 5, 'window_check_count': 1,
            'rule_failure_counts': {}, 'rule_evidence': {}, 'unresolved': [], 'authority': 'derived_from_sealed_checks',
            'snapshot': head, 'seal_count': 1, 'window_seal_count': 1, 'coverage': 'central_submission_checks'})
        for change in ('path', 'duplicate', 'mode', 'execution', 'receipt'):
            row, files = deepcopy(seal), dict(self.files)
            if change in {'path', 'duplicate'}:
                rows = row['submission_check']['artifacts']
                if change == 'path':
                    rows[0]['path'] = 'research/outside.json'
                else:
                    rows.append(deepcopy(rows[0]))
                reason = 'central check artifact coordinate differs'
            elif change == 'receipt':
                row['state'] = 'rejected'
                reason = 'central check result differs from its published receipt'
            else:
                check = deepcopy(self.sealed['check'])
                check['mode' if change == 'mode' else 'execution_id'] = 'producer' if change == 'mode' else 'EX-other'
                check['id'] = 'MC-' + exact_content_hash({k: v for k, v in check.items() if k != 'id'})[:24]
                path = row['submission_check']['check_ref']
                files[path] = canonical_json(check)
                entry = next(item for item in row['submission_check']['artifacts'] if item['path'] == path)
                entry.update(sha256=hashlib.sha256(files[path]).hexdigest(), bytes=len(files[path]))
                reason = 'central check execution or mode differs'
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                summarize(row, files)

    def test_receipt_identity_and_missing_locators_have_distinct_rejections(self):
        for field, value in (('state', 'rejected'), ('execution_id', 'EX-other')):
            changed = deepcopy(self.execution)
            changed['submission_receipt'][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(submission.SealedSubmissionError,
                    '^execution EX-worker: accepted submission receipt is missing$'):
                self.read(changed, self.files)
        for field in ('output_ref', 'extensions_ref', 'check_ref'):
            for value in (None, '', 0):
                changed = deepcopy(self.execution)
                changed['submission_intent'][field] = value
                with self.subTest(field=field, value=value), self.assertRaisesRegex(
                        submission.SealedSubmissionError,
                        '^' + re.escape(f'execution EX-worker: missing sealed {field} at {value!r}') + '$'):
                    self.read(changed, self.files)

    def test_missing_artifact_names_the_exact_reference(self):
        for field in ('output_ref', 'extensions_ref', 'check_ref'):
            path = self.execution['submission_intent'][field]
            files = {key: raw for key, raw in self.files.items() if key != path}
            store, head = self.publish(files)
            before = deepcopy((self.execution, files))
            reason = f'git cat-file blob {head}:{path} failed: no blob at this path'
            with self.subTest(field=field), self.assertRaisesRegex(submission.SealedSubmissionError,
                    '^' + re.escape(f'execution EX-worker: cannot read {field} at {path}: {reason}') + '$') as caught:
                submission.read_sealed_submission(self.execution, head,
                    lambda ref, snapshot: store.read_bytes(snapshot, ref))
            self.assertIs(type(caught.exception.__cause__), GitStateStoreError)
            self.assertEqual(str(caught.exception.__cause__), reason)
            self.assertEqual((self.execution, files), before)
            self.assertEqual(store.read_snapshot().head, head)

    def test_hash_receipt_and_size_are_independent_evidence(self):
        for field in ('output_ref', 'extensions_ref', 'check_ref'):
            path = self.execution['submission_intent'][field]
            for fault in ('hash', 'receipt', 'size'):
                execution = deepcopy(self.execution)
                files = dict(self.files)
                rows = execution['submission_receipt']['payload']['submission_check']['artifacts']
                entry = next(row for row in rows if row['path'] == path)
                if fault == 'hash':
                    files[path] += b' '
                    reason = f'sealed {field} hash differs at {path}'
                elif fault == 'receipt':
                    # check은 receipt 해시가 유일한 근거라 문자열 형 자체를 손상한다.
                    entry['sha256'] = None if field == 'check_ref' else '0' * 64
                    reason = (f'sealed {field} hash differs at {path}' if field == 'check_ref'
                              else f'{field} receipt differs at {path}')
                else:
                    entry['bytes'] += 1
                    reason = f'sealed {field} size differs at {path}'
                with self.subTest(field=field, fault=fault), self.assertRaisesRegex(
                        submission.SealedSubmissionError, '^' + re.escape('execution EX-worker: ' + reason) + '$'):
                    self.read(execution, files)

    def test_matching_hash_does_not_authorize_malformed_json(self):
        for field in ('output_ref', 'extensions_ref', 'check_ref'):
            execution = deepcopy(self.execution)
            files = dict(self.files)
            path = execution['submission_intent'][field]
            files[path] = b'{'
            sha = hashlib.sha256(files[path]).hexdigest()
            for row in execution['submission_receipt']['payload']['submission_check']['artifacts']:
                if row['path'] == path:
                    row.update(sha256=sha, bytes=1)
            if field != 'check_ref':
                execution['submission_intent'][field.removesuffix('_ref') + '_sha256'] = sha
            with self.subTest(field=field), self.assertRaisesRegex(submission.SealedSubmissionError,
                    '^' + re.escape(f'execution EX-worker: invalid sealed {field} JSON at {path}:')):
                self.read(execution, files)
