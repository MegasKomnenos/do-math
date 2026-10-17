"""Source-relative logical snapshot size at the actual academic record producer.

The source text is counted once, independently of its repeated references.
This is a repository/Git-port test, not a Git compression measurement.
"""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from copy import deepcopy

from do_math import academic
from do_math.canonical import canonical_json
from do_math.payloads import LIMIT
from support.record_builders import execution_state
from support.storage_records import approved_governance_instance, record_store
from support.state_builders import current_state
from support.storage_snapshot_cases import fresh_reader, snapshot_files


class StorageScaleTests(unittest.TestCase):
    def test_review_revision_prefixes_store_each_independent_small_body_once(self):
        """Real start_review/record_turn -> repository -> fresh read/query.

        16384 per cycle pays 36 envelope coordinates and 28 structural nodes
        at 256 bytes each; 6x source allows JSON escaping. Fixed before running.
        The per-body and shared-prefix checks also prevent a generous overhead
        from hiding the old quadratic copy. There are no model executions here;
        live revision admission/sealed replay are covered by the review tests.
        Two publications and forced decoding take about 1.2 s, above 0.2 s;
        the bound concerns bytes, not runtime acceleration.
        """
        from do_math import review_cycle as rc
        with tempfile.TemporaryDirectory() as directory:
            store = record_store(Path(directory))
            instance, runtime = current_state()
            head = store.initialize(instance, runtime)
            baseline = sum(map(len, snapshot_files(store, head).values()))
            source_bytes, expected, previous = 0, {}, None
            for revision in range(1, 9):
                # Every body is below the text codec threshold; no large leaf.
                proposal = {'revision': revision, 'statement': f'SOURCE-body-{revision:03d}-' + '원천\\"\n' * 512}
                source_bytes += len(canonical_json(proposal))
                cycle = rc.start_review(proposal, reviewers=1, previous=previous)
                cycle['id'] = f'RC-prefix-{revision}'
                cycle = rc.record_turn(cycle, 'scope', [{'role': 'user', 'kind': 'proposal',
                    'message_id': f'proposal-{revision}', 'content': proposal}])
                expected[cycle['id']] = deepcopy(cycle)
                runtime.setdefault('review_cycles', {})[cycle['id']] = cycle
                previous = cycle
                if revision not in (1, 8):
                    continue
                head, instance, runtime = store.save_with_state(head, instance, runtime)
                files = snapshot_files(store, head)
                print('R22 review bytes', {'revisions': revision, 'source': source_bytes,
                    'logical': sum(map(len, files.values())), 'baseline': baseline,
                    'bound': baseline + 6 * source_bytes + 16384 * revision})
                self.assertLessEqual(sum(map(len, files.values())), baseline + 6 * source_bytes + 16384 * revision)
                for index in range(1, revision + 1):
                    marker = f'SOURCE-body-{index:03d}-'.encode()
                    self.assertEqual(sum(raw.count(marker) for raw in files.values()), 1)
                # A fresh installed contract forces actual artifact decoding.
                reader = fresh_reader(store)
                self.assertEqual(reader.load(head)[2]['review_cycles'], expected)
                restored = reader.read_record(cycle['id'], head)['record']
                self.assertEqual(restored, expected[cycle['id']])
                context = rc.context_for(restored, rc.next_actions(restored)[0])
                self.assertEqual([row['revision'] for row in context['previous_reviews']], list(range(1, revision)))
                self.assertEqual(len(context['source_refs']), revision)
                rc.validate_transcript(restored, 'scope')
                # No mutable aliases across editions, or within restored graphs.
                loaded = reader.load(head)[2]['review_cycles']
                loaded[cycle['id']]['turns']['scope'][0]['content']['statement'] = 'caller change'
                self.assertEqual(reader.read_record(cycle['id'], head)['record'], expected[cycle['id']])
                if revision > 1:
                    self.assertEqual(loaded['RC-prefix-1'], expected['RC-prefix-1'])

    def test_resolution_history_shares_one_source_and_stores_only_evidence_hashes(self):
        """Small and externalized UTF-8/escaped text, at 1 and 10 actual records.

        The bound is fixed before measurement: JSON escaping costs at most six
        bytes per source UTF-8 byte, and 4096 per rejection/resolution pair pays
        for their closed fields, IDs, hashes, envelopes and manifest membership.
        The baseline pays for unrelated installed state, not produced records.
        About 1 s exceeds the 0.2 s unit budget: four full repository snapshots
        check actual validation, publication, load and record reads.
        """
        for repeats in (1, LIMIT):
            with self.subTest(repeats=repeats), tempfile.TemporaryDirectory() as directory:
                store = record_store(Path(directory) / 'repository')
                instance, runtime = execution_state('research_plan')
                instance.update(approved_governance_instance())
                basis = {'goal_ref': 'CH-1', 'records': []}
                runtime['executions']['EX-1'].update(input_solution_basis=basis)
                head = store.initialize(instance, runtime)
                baseline = sum(map(len, snapshot_files(store, head).values()))
                # These are independent producer inputs, not final-state bytes.
                text = '원천\\"\n\x00' * repeats
                evidence = b'independent immutable answer\n' * (LIMIT // 16)
                path = 'runtime/artifacts/BA-scale/answer.txt'
                source_bytes = len(text.encode('utf-8')) + len(evidence)
                expected = []
                for index in range(10):
                    rejection = {'id': f'RJ-scale-{index}', 'actor': 'reviewer',
                                 'text': f'objection {index}', 'source_ref': 'input',
                                 'solution_basis': basis}
                    runtime.setdefault('external_rejections', []).append(rejection)
                    row = academic.record_resolution(instance, runtime, basis,
                        {'id': rejection['id'], 'decision': 'resolved',
                         'evidence': text, 'evidence_refs': [path]}, execution_id='EX-1',
                        resolve_evidence=lambda ref: evidence if ref == path else None)
                    expected.append(row)
                    if index not in (0, 9):
                        continue
                    count = index + 1
                    head, instance, runtime = store.save_with_state(head, instance, runtime,
                        artifacts={path: evidence} if index == 0 else None)
                    _, loaded_instance, loaded_runtime = store.load(head)
                    self.assertEqual(loaded_instance, instance)
                    self.assertEqual(loaded_runtime['academic_resolution_records'], expected)
                    self.assertEqual(store.read(path, head), evidence)
                    files = snapshot_files(store, head)
                    self.assertLessEqual(sum(map(len, files.values())),
                                         baseline + 6 * source_bytes + 4096 * count)
                    self.assertEqual(sum(raw == evidence for raw in files.values()), 1)
                    encoded_text = canonical_json(text)
                    if len(encoded_text) >= LIMIT:
                        self.assertEqual(sum(raw == encoded_text for raw in files.values()), 1)
                    for result in expected:
                        saved = store.read_record(result['id'], head)
                        self.assertEqual(saved['record'], result)
                        self.assertEqual(result['evidence_hashes'],
                                         {path: hashlib.sha256(evidence).hexdigest()})
                        envelope = json.loads(files[saved['path']])
                        self.assertNotIn(evidence.decode(), json.dumps(envelope))
                        if len(encoded_text) >= LIMIT:
                            self.assertIsNone(envelope['record']['evidence'])
                            self.assertEqual(len(envelope['payloads']), 1)
                            self.assertEqual(envelope['payloads'][0]['tokens'], ['evidence'])
                            self.assertEqual(files[envelope['payloads'][0]['path']], encoded_text)
