"""The actual delegation/import/pending producers on repository-backed engines.

The original decision/delegation prefix is public (r12-r13-fix), not seeded.
Fanout is domain preparation, not a claim of four public authorizations.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math import delegations, governance, knowledge_records, review_cycle
from do_math.canonical import canonical_json, exact_content_hash
from support.governance_delegation import public_replacement_case
from support.knowledge_builders import knowledge_candidate
from support.storage_snapshot_cases import fresh_reader, snapshot_files


class StructuralSnapshotProducerTests(unittest.TestCase):
    def test_public_decision_basis_and_knowledge_owner_fanout_survive_storage(self):
        """Public prefix and schema-backed publications/restart exceed 60 s.

        This checks the storage source relation, not runtime acceleration.
        """
        sim, config = public_replacement_case()
        engine = sim.engine
        # Independent source: many small rows, made once and given to the
        # actual knowledge producer. No text leaf can use the large-text codec.
        source = {'rows': [{'id': f'row-{i}', 'statement': f'SNAPSHOT-source-{i:03d}',
                            'values': [i, True, None]} for i in range(256)]}
        candidate = knowledge_candidate(kind='observation', lean_code='', declaration_names=[],
            uncertainty_assessment=source)
        engine.instance, kid = knowledge_records.create_candidate(engine.instance, candidate,
            source_ref='independent-row-input', actor_ref='user', clock=sim.clock)
        engine._save()
        baseline = sum(map(len, snapshot_files(engine.store, engine.head).values()))
        original = deepcopy(config['review_replacement']['case'])
        apps, case_bytes = [], 0
        for index in range(4):
            case = {**deepcopy(original), 'id': f'CASE-fanout-{index}',
                    'basis_refs': [*original['basis_refs'], kid]}
            case_bytes += len(canonical_json(case))
            apps.append(delegations.prepare_application(engine.instance, engine.runtime, 'DG-public',
                case, now_iso=sim.clock.now()))
        engine._save()
        sim.control('input', text='abcd', request_id='INPUT-snapshot-import')
        engine.process_controls()
        source_input = governance.import_input_source(engine.instance, engine.runtime, 'INPUT-snapshot-import')
        output = {'summary': 'Already preserved evidence', 'used_sources': [], 'questions': [], 'question_details': [],
            'import_units': [{'unit_id': f'U-{i}', 'source_range': {'start': i, 'end': i + 1},
                'interpretation': 'Existing structured observation', 'owner_kind': 'research_record',
                'owner_ref': kid, 'payload': {}, 'decision_refs': [], 'question_refs': []} for i in range(4)]}
        author = next(eid for eid, e in engine.runtime['executions'].items() if e['role'] == 'intent_interpretation')
        bundle = governance.prepare_import(engine.instance, engine.runtime, source_input, output,
            execution_id=author, input_ref='INPUT-snapshot-import', clock=sim.clock)
        engine._save()
        files = snapshot_files(engine.store, engine.head)
        # 32x the fixed independent row input covers list/object cells and
        # child hashes; 16384 per case/unit covers the fixed domain roots.
        source_bytes = len(canonical_json(candidate)) + case_bytes + len(canonical_json(output)) + len(canonical_json(source_input))
        print('R22 producer bytes', {'cases': 4, 'units': 4, 'source': source_bytes,
            'logical': sum(map(len, files.values())), 'baseline': baseline,
            'bound': baseline + 32 * source_bytes + 16384 * 8})
        self.assertLessEqual(sum(map(len, files.values())), baseline + 32 * source_bytes + 16384 * 8)
        for index in range(256):
            marker = canonical_json(f'SNAPSHOT-source-{index:03d}').strip()
            # One inline source record, one immutable graph node; independent
            # of four delegation cases plus four owner units.
            self.assertEqual(sum(raw.count(marker) for raw in files.values()), 2)
        reader = fresh_reader(engine.store)
        _, instance, runtime = reader.load(engine.head)
        for app in apps:
            saved = reader.read_record(app['id'], engine.head)['record']
            self.assertEqual(saved, app)
            self.assertEqual(exact_content_hash(saved['basis']), app['input_sha256'])
            self.assertEqual(delegations.judgment_input(runtime, app['id']), delegations.judgment_input(engine.runtime, app['id']))
        self.assertEqual(reader.read_record(bundle['id'], engine.head)['record'], bundle)
        self.assertEqual(governance.current_import(instance, runtime, bundle['id'], clock=sim.clock), bundle)
        runtime['delegation_applications'][apps[0]['id']]['basis']['references'][kid]['uncertainty_assessment']['rows'][0]['statement'] = 'changed'
        self.assertEqual(runtime['delegation_applications'][apps[1]['id']]['basis']['references'][kid]['uncertainty_assessment'], source)
        self.assertEqual(instance['knowledge'][kid]['uncertainty_assessment'], source)
        instance['knowledge'][kid]['uncertainty_assessment']['rows'][0]['statement'] = 'changed'
        with self.assertRaisesRegex(ValueError, '^import authority or affected targets changed$'):
            governance.current_import(instance, runtime, bundle['id'], clock=sim.clock)
        sim.restart()
        self.assertEqual(sim.runtime['intent_imports'][bundle['id']], bundle)
        self.assertEqual([sim.runtime['delegation_applications'][a['id']] for a in apps], apps)

    def test_pending_seats_share_restored_rows_and_return_detached_transcripts(self):
        with tempfile.TemporaryDirectory() as directory:
            from support.review_sim import opened_sim
            sim = opened_sim()
            sim.step()  # Actual scope worker opens the two initial seats.
            engine = sim.engine
            cid = next(a['review_cycle_id'] for a in engine.runtime['queue'] if a['role'] == 'identity_review')
            source = {'rows': [{'id': f'row-{i}', 'statement': f'PENDING-source-{i:03d}'} for i in range(256)]}
            actions = deepcopy([a for a in engine.runtime['queue'] if a.get('review_cycle_id') == cid])
            for action in actions:
                engine.runtime['review_cycles'][cid] = review_cycle.record_turn(engine.runtime['review_cycles'][cid],
                    action['slot'], [{'role': 'user', 'message_id': 'same-source', 'content': source}])
                ready = engine._prepare_review_context(action, Path(directory) / action['slot'])
                self.assertEqual(ready['disposition'], 'ready')
                self.assertEqual(ready['context']['self_messages'][0]['content'], source)
            pending = deepcopy(engine.runtime['review_inputs'])
            self.assertEqual(len(pending), 2)
            engine._save()
            reader = fresh_reader(engine.store)
            loaded = reader.load(engine.head)[2]
            self.assertEqual(loaded['review_inputs'], pending)
            files = snapshot_files(engine.store, engine.head)
            for index in range(256):
                marker = canonical_json(f'PENDING-source-{index:03d}').strip()
                self.assertEqual(sum(raw.count(marker) for raw in files.values()), 1)
            keys = list(pending)
            loaded['review_inputs'][keys[0]]['restored_messages'][0]['content']['rows'][0]['statement'] = 'changed'
            self.assertEqual(loaded['review_inputs'][keys[1]], pending[keys[1]])
            self.assertEqual(loaded['review_cycles'][cid], engine.runtime['review_cycles'][cid])
            context = engine._prepare_review_context(actions[0], Path(directory) / actions[0]['slot'])['context']
            self.assertEqual(context['self_messages'][0]['content'], source)
            sim.restart()
            self.assertEqual(sim.runtime['review_inputs'], pending)
