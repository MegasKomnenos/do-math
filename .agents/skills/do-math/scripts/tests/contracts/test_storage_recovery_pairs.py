"""Actual recovery owners, validated publication, cold decode and reverse fields."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from contracts.pairs import assert_pair
from do_math import activities, execution_lifecycle as lifecycle
from do_math.canonical import canonical_json
from support.provider_probes import ObservedCalls
from support.sim import Sim, warm_template
from support.state_builders import installed_contract
from support.storage_recovery_pairs import StoredRecoveries, family_pair, proposal_pair, reader

setUpModule = warm_template


class StorageRecoveryPairTests(unittest.TestCase):
    """Cold owner journeys exceed the 0.2s contract budget (roughly 2–40s).

    Real preparation/receipt/storage is the subject. Existing journey builders
    and Git/clock/model/Jobs port doubles keep the scope below external tests.
    """

    def reject(self, engine, tokens, value, message):
        head, instance, runtime = reader(engine).load(engine.head)
        changed = deepcopy(runtime)
        target = changed
        for token in tokens[:-1]:
            target = target[token]
        target[tokens[-1]] = value
        invalid = deepcopy(changed)
        with ObservedCalls(write=engine.ports.git_backend.write_object) as calls:
            with self.assertRaises(ValueError) as error:
                engine.store.save_with_state(head, instance, changed)
            self.assertIs(type(error.exception), ValueError)
            self.assertEqual(str(error.exception), message)
            self.assertEqual(calls.count('write'), 0)
        self.assertEqual(changed, invalid)
        self.assertEqual(engine.store.resolve_snapshot(None), head)
        self.assertEqual(reader(engine).load(head), (head, instance, runtime))

    def test_recovery_sweep_preserves_order_unknown_capacity_and_output_bytes(self):
        from do_math.launch import mark_dispatched
        from support.provider_live import running_execution
        from support.scheduling_slots import reserve
        sim = Sim.activated()
        engine = sim.engine
        samples = StoredRecoveries(self)
        empty = samples.keep(engine, 'before-recovery')
        self.assertNotIn('recoveries', empty[2])
        # An unpublished preparation, a reserved queued attempt, an unknown
        # local process and a confirmed empty Job are different recovery facts.
        engine._register_execution({'id': 'AC-unstarted', 'role': 'maintenance'},
                                   {'id': 'EX-unstarted', 'role': 'maintenance'})
        accepted, queued = reserve(sim, 'EX-reserved')
        self.assertTrue(accepted)
        # Explicit recovery-boundary input: the queued receipt and a held
        # ledger are independent facts. Normal acquire above writes starting;
        # this fixture does not claim an automatic queued-with-capacity writer.
        queued['status'] = 'queued'
        engine._save()
        running_execution(sim, 'EX-unknown', 'maintenance')
        accepted, ended = reserve(sim, 'EX-local', operational=True)
        self.assertTrue(accepted)
        mark_dispatched(ended['launch_ticket'])
        engine._save()
        sim.jobs.programs.insert(0, (lambda argv: argv == ['recovery-fixture', 'empty'], lambda *args: 0))
        job = sim.jobs.launch(['recovery-fixture', 'empty'], name=ended['launch_ticket']['job_name'])
        job.terminate()
        job.close()
        workspace = Path(engine.instance['workspace']) / 'runs/EX-local/workspace'
        workspace.mkdir(parents=True, exist_ok=True)
        raw = 'preserved e\u0301\r\n'.encode()
        (workspace / 'work.txt').write_bytes(raw)
        held = deepcopy(engine.runtime['reservations'])
        before = samples.keep(engine, 'before-sweep')
        sim.restart()
        engine = sim.engine
        expected_ids = [row['id'] for row in engine.runtime['executions'].values() if row['status'] != 'ended']
        started = sim.clock.now()
        def before_save(arguments):
            samples.keep(engine, 'published-before-next-save', head=engine.head)
            return {}
        with ObservedCalls(save=engine._save, capture={'save': before_save}):
            engine._recover_disappeared()
        loaded = samples.keep(engine, 'finished-sweep', previous=before)
        recovery, = loaded[2]['recoveries'].values()
        self.assertEqual(recovery['execution_ids'], expected_ids)
        self.assertEqual(recovery['started_at'], started)
        self.assertEqual(recovery['finished_at'], sim.clock.now())
        self.assertTrue(any(row['execution_ids'] == expected_ids and 'finished_at' not in row
            for _, state in samples.samples for row in state[1].get('recoveries', {}).values()))
        expected_dispositions = {row['execution_id']: row for row in [
            {'execution_id': 'EX-unstarted', 'fact': 'no_execution_or_reservation'},
            {'execution_id': 'EX-reserved', 'fact': 'queued_reservation_requires_reconciliation', 'next_owner': 'operator'},
            {'execution_id': 'EX-unknown', 'local_termination_confirmed': False, 'remote_termination': 'unknown', 'next_owner': 'operator'},
            {'execution_id': 'EX-local', 'local_termination_confirmed': True, 'remote_termination': 'unknown', 'next_owner': 'operational_review'}]}
        self.assertEqual(recovery['dispositions'], [expected_dispositions[eid] for eid in expected_ids])
        runtime = loaded[2]
        self.assertEqual(runtime['executions']['EX-unstarted']['outcome'], 'cancelled')
        self.assertEqual(runtime['executions']['EX-reserved']['status'], 'queued')
        self.assertEqual(runtime['executions']['EX-reserved']['recovery_disposition'], 'preserve_space_and_reservations')
        for key, value in held.items():
            self.assertEqual(runtime['reservations'][key], value)
        self.assertEqual(runtime['executions']['EX-unknown']['status'], 'stopping')
        local = runtime['executions']['EX-local']
        self.assertEqual((local['status'], local['outcome']), ('ended', 'execution_incomplete'))
        output = next(row for row in local['output_files'] if row['path'] == 'work.txt')
        self.assertEqual(reader(engine).read(output['artifact_ref'], engine.head), raw)
        self.assertEqual(output['bytes'], len(raw))
        # Supply a real launch ticket at the recovery boundary without a
        # capacity receipt. The actual recovery producer cannot settle it;
        # this does not certify that normal atomic admission loses capacity.
        from do_math.launch import ticket
        from do_math.execution_profiles import match_profile_ref
        unknown = engine.runtime['executions']['EX-unknown']
        profile = match_profile_ref(engine.instance['execution_profiles'], unknown['execution_profile_ref'])
        unknown['launch_ticket'] = ticket(unknown['id'], profile, jobs=sim.jobs, clock=sim.clock)
        mark_dispatched(unknown['launch_ticket'])
        unknown_raw = b'preserve even while reservation settlement is unconfirmed\r\n'
        unknown_workspace = Path(engine.instance['workspace']) / 'runs/EX-unknown/workspace'
        (unknown_workspace / 'unsettled.txt').write_bytes(unknown_raw)
        job = sim.jobs.launch(['recovery-fixture', 'empty'], name=unknown['launch_ticket']['job_name'])
        job.terminate()
        job.close()
        engine._save()
        sim.restart()
        engine = sim.engine
        engine._recover_disappeared()
        samples.keep(engine, 'settlement-unconfirmed')
        row = list(engine.runtime['recoveries'].values())[-1]
        self.assertIn({'execution_id': 'EX-unknown', 'local_termination_confirmed': False,
            'remote_termination': 'unknown', 'next_owner': 'operator',
            'reason': 'reservation settlement not confirmed'}, row['dispositions'])
        unknown = engine.runtime['executions']['EX-unknown']
        preserved = next(item for item in unknown['output_files'] if item['path'] == 'unsettled.txt')
        self.assertEqual(reader(engine).read(preserved['artifact_ref'], engine.head), unknown_raw)
        checkpoint = json.loads(reader(engine).read(unknown['result_ref'], engine.head))
        self.assertEqual(checkpoint, engine.runtime['checkpoints']['EX-unknown'])
        self.assertEqual(unknown['status'], 'stopping')
        self.check_pair(samples, 'recoveries')
        rid = row['id']
        prefix = 'runtime/recoveries/' + rid
        self.reject(engine, ('recoveries', rid, 'dispositions', 0, 'disposition'), 'obsolete',
            prefix + "/dispositions/0: Additional properties are not allowed ('disposition' was unexpected)")
        self.reject(engine, ('recoveries', rid, 'dispositions', 0, 'local_termination_confirmed'), 'yes',
            prefix + "/dispositions/0/local_termination_confirmed: 'yes' is not of type 'boolean'")
        self.reject(engine, ('recoveries', rid, 'id'), 'RY-other', 'recoveries map key and id differ')

    def check_pair(self, samples, name):
        contract = installed_contract()
        pair = family_pair(contract, name, samples.samples)
        assert_pair(self, pair, samples.samples)
        # An accepted optional field without a writer must still fail reverse.
        from do_math.state_contract import StateContract
        definition = contract.family('runtime', name)
        schema = deepcopy(definition.schema)
        schema['properties']['unproduced_optional'] = {'type': 'string'}
        drift = StateContract()
        drift.register_family('runtime', name, shape=definition.shape, schema=schema, identity=definition.identity)
        with self.assertRaisesRegex(AssertionError, 'unproduced_optional'):
            assert_pair(self, family_pair(drift, name, samples.samples), samples.samples)

    def test_operational_records_keep_review_target_proposal_and_conditional_results(self):
        from support.storage_execution_pairs import stored_operational_dispositions
        samples = StoredRecoveries(self)
        stored_operational_dispositions(samples)
        self.operational_variants(samples)
        self.check_pair(samples, 'operational_dispositions')
        assert_pair(self, proposal_pair(samples.samples), samples.samples)

    def operational_variants(self, samples):
        from support.engine_control import running_work
        from support.observation_inputs import observation_rule, self_check_response, write_checkpoint
        from support.scheduling_model import explicit, scenario_model
        for kind in ('user_decision', 'repair'):
            sim = Sim.activated()
            engine = sim.engine
            with running_work(sim, rules=[observation_rule()] if kind == 'user_decision' else None) as call:
                eid = call.execution_id
                action = {'id': 'AC-review-' + kind, 'role': 'operational_review', 'target': eid}
                obligations = []
                if kind == 'user_decision':
                    write_checkpoint(call.workspace, counters={'attempts': 2})
                    call.observe({'type': 'tick'})
                    obligation, = call.tracker.obligations.values()
                    call.self_check(obligation['id'], self_check_response(obligation, status='indeterminate', evidence=[]))
                    call.receive()
                    action = deepcopy(next(row for row in engine.runtime['queue'] if row.get('obligation_ids')))
                    obligations = [obligation['id']]
                if kind == 'repair':
                    call.finish({'status': 'stopped', 'error': 'Preserve unfinished work'})
                specific = ({'question': 'Which scope?', 'effect': 'Need explicit permission'} if kind == 'user_decision'
                    else {'repair_target': 'installation:scripts/do_math/engine.py', 'meaning_preserving': True,
                          'verification': 'Run the receiver regression'})
                proposal = {'kind': kind, 'basis_refs': [eid, *obligations],
                    'next_owner': 'user' if kind == 'user_decision' else 'installation_recovery',
                    'reason': 'Exact operating judgment e\u0301\r\n', **specific}
                output = {'summary': 'Independent judgment', 'questions': [], 'used_sources': [], 'disposition': proposal}
                engine.runtime['queue'] = [action]
                engine._save()
                scenario_model(sim).on('operational_review').reply(explicit(output))
                times = []
                def applying(arguments):
                    times.append(sim.clock.now())
                    return {}
                with ObservedCalls(apply=engine._apply_operational_disposition, capture={'apply': applying}):
                    sim.step()
                saved = samples.keep(engine, kind + '-received')
                self.assertIn('operational_dispositions', saved[2], repr(sim.waiting()))
                record, = saved[2]['operational_dispositions'].values()
                reviewer = record['execution_id']
                self.assertEqual(record['disposition'], proposal)
                self.assertEqual((record['target_execution_id'], record['created_at'], record['obligation_ids']),
                                 (eid, times[0], obligations))
                review = saved[2]['executions'][reviewer]
                self.assertEqual((review['role'], review['status'], review['outcome']),
                                 ('operational_review', 'ended', 'output_accepted'))
                self.assertNotEqual(reviewer, eid)
                self.assertEqual(review['output']['disposition'], proposal)
                proposal['basis_refs'].append('caller mutation')
                self.assertNotIn('caller mutation', record['disposition']['basis_refs'])
                self.assertNotIn('applied_at', record)
                self.assertNotIn('error', record)
                if kind == 'user_decision':
                    self.assertEqual(record['status'], 'applied')
                    link = next(row for row in saved[2]['question_links'] if row['id'] == record['question_id'])
                    self.assertEqual((link['origin_execution_id'], link['target_ids']), (reviewer, [call.execution['action']['target']]))
                    call.finish({'status': 'stopped', 'error': 'Preserve unfinished work'})
                else:
                    from do_math.repair_execution import installation_sha256
                    self.assertEqual(record['status'], 'installation_repair_pending')
                    self.assertEqual(record['result']['installation_repair'], {
                        'installation_sha256': installation_sha256(engine.installation_root),
                        'evidence_refs': [call.execution['result_ref']]})
                    old_head = engine.head
                    engine._run_pending_operational_repairs()
                    self.assertEqual(engine.head, old_head)
                    self.assertEqual(reader(engine).load(old_head), saved)

        # Reuse the existing source-authorized, returned-task review journey.
        from support.cross_states import operational_task_ready, queued, assert_event
        sim = operational_task_ready()
        action = queued(sim, 'operational_review')
        expected_target = action['target']
        observed = assert_event(sim, action, 'task_operation', 'incomplete')
        saved = samples.keep(sim.engine, 'task-disposition-received')
        record, = [row for row in saved[2]['operational_dispositions'].values()
                   if row['target_execution_id'] == expected_target]
        self.assertEqual(record['disposition'], observed['output']['disposition'])
        self.assertEqual(record['status'], 'applied')
        task = saved[2]['tasks'][record['disposition']['task_id']]
        self.assertEqual((task['status'], task['assessment']['decision']), ('waiting', 'incomplete'))
        self.assertEqual(task['assessment']['execution_id'], record['execution_id'])

    def test_public_fence_preserves_request_barriers_restart_and_release(self):
        from support.engine_control import running_work
        from support.storage_records import apply_control
        from do_math import maintenance_gate
        sim = Sim.activated()
        engine = sim.engine
        samples = StoredRecoveries(self)
        absent = samples.keep(engine, 'absent-fence')
        with running_work(sim) as call:
            held = [row['id'] for row in engine.runtime['reservations'].values() if row['state'] == 'held']
            self.assertTrue(held)
            request = sim.control('quiesce', origin='user', text='정비 원문 e\u0301\r\n')
            envelope = next(row for row in engine._inbox() if row['id'] == request['request_id'])
            engine.process_controls()
            saved = samples.keep(engine, 'blocked-public-fence', previous=absent)
            fence = saved[2]['maintenance_fence']
            self.assertEqual({key: fence[key] for key in ('request_id', 'origin', 'reason', 'created_at')},
                {'request_id': request['request_id'], 'origin': 'user', 'reason': '정비 원문 e\u0301\r\n',
                 'created_at': envelope['created_at']})
            self.assertEqual((fence['state'], fence['pending_executions'], fence['held_reservations']),
                             ('blocked', [call.execution_id], held))
            before = deepcopy(engine.runtime)
            with self.assertRaisesRegex(ValueError, '^operator cannot release a user maintenance fence$'):
                maintenance_gate.apply_control(engine.runtime, {'action': 'release_quiesce', 'id': 'UC-forbidden',
                    'origin': 'operator', 'config': {'fence_id': fence['request_id']}})
            self.assertEqual(engine.runtime, before)
            call.finish({'status': 'stopped', 'error': 'Maintenance barrier'})
        apply_control(sim, 'pause', origin='user', text='Keep separate pause')
        pause = deepcopy(engine.runtime['user_pause'])
        maintenance_gate.settle(engine.runtime, clock=sim.clock)
        engine._save()
        settled = samples.keep(engine, 'quiescent-fence', previous=saved)
        fence = settled[2]['maintenance_fence']
        self.assertEqual((fence['state'], fence['pending_executions'], fence['held_reservations']), ('quiescent', [], []))
        self.assertEqual(fence['settled_at'], sim.clock.now())
        self.reject(engine, ('maintenance_fence', 'state'), 'ready',
            "runtime/maintenance_fence/None/state: 'ready' is not one of ['draining', 'blocked', 'quiescent']")
        sim.restart()
        self.assertEqual(sim.runtime['maintenance_fence'], fence)
        apply_control(sim, 'release_quiesce', origin='user', config={'fence_id': fence['request_id']})
        released = samples.keep(sim.engine, 'released-fence', previous=settled)
        self.assertNotIn('maintenance_fence', released[2])
        self.assertEqual((released[2]['user_pause'], released[2]['status']), (pause, 'paused'))
        self.assertIn(fence, [row['fence'] for row in released[2]['history'] if row.get('kind') == 'maintenance_released'])
        # The early draining shape is produced before settle fills optional fields.
        request = {'id': 'UC-drain', 'action': 'quiesce', 'origin': 'operator',
                   'text': 'installation', 'created_at': sim.clock.now()}
        maintenance_gate.apply_control(sim.runtime, request)
        sim.engine._save()
        early = samples.keep(sim.engine, 'draining-fence')
        self.assertEqual(early[2]['maintenance_fence'], {'request_id': 'UC-drain', 'origin': 'operator',
            'reason': 'installation', 'state': 'draining', 'created_at': request['created_at']})
        self.check_pair(samples, 'maintenance_fence')

    def test_model_mismatch_from_call_is_detached_stored_and_cleared_only_on_resume(self):
        from do_math.provider_engine import record_model_policy_violation
        from support.engine_control import running_work
        from support.storage_records import apply_control
        sim = Sim.activated()
        engine = sim.engine
        samples = StoredRecoveries(self)
        absent = samples.keep(engine, 'before-model-mismatch')
        self.assertNotIn('model_policy_violation', absent[2])
        with running_work(sim) as call:
            assigned = call.execution['model']
            result = {'status': 'failed', 'error_kind': 'model_policy', 'error': 'Unexpected model',
                      'reported_models': ['other-model', 'other-model-2'], 'usage': {}}
            original = deepcopy(result)
            call.finish(result)
            saved = samples.keep(engine, 'call-model-mismatch', previous=absent)
            expected = {'execution_id': call.execution_id, 'assigned_model': assigned,
                        'reported_models': ['other-model', 'other-model-2']}
            self.assertEqual(saved[2]['model_policy_violation'], expected)
            self.assertEqual(saved[2]['status'], 'paused')
            row = saved[2]['executions'][call.execution_id]
            self.assertEqual(json.loads(reader(engine).read(row['result_ref'], engine.head)), original)
            result['reported_models'].clear()
            self.assertEqual(engine.runtime['model_policy_violation'], expected)
        sim.restart()
        self.assertEqual(sim.runtime['model_policy_violation'], expected)
        apply_control(sim, 'resume', origin='user', text='Explicit decision after model mismatch')
        resumed = samples.keep(sim.engine, 'resumed-model-mismatch', previous=saved)
        self.assertNotIn('model_policy_violation', resumed[2])
        # Open evidence has no named fields: exact nested content and isolation
        # are checked directly, including the ended-instance guard.
        for status in ('closed', 'completed'):
            instance, runtime = deepcopy((sim.instance, sim.runtime))
            runtime['status'] = status
            reported = {'reported_models': [{'model': 'wrong', 'observations': ['원문 e\u0301\r\n']}]}
            record_model_policy_violation(instance, runtime, 'EX-ended', 'assigned', reported)
            reported['reported_models'][0]['observations'].clear()
            self.assertEqual(runtime['status'], status)
            self.assertEqual(runtime['model_policy_violation'], {'execution_id': 'EX-ended', 'assigned_model': 'assigned',
                'reported_models': [{'model': 'wrong', 'observations': ['원문 e\u0301\r\n']}]})

    def test_unused_slots_are_not_receiving_fields(self):
        from do_math.state_contract import validate_record
        contract = installed_contract()
        for family, row, field in (
            ('recoveries', {'id': 'RY-one', 'started_at': 'now', 'execution_ids': [], 'dispositions': [
                {'execution_id': 'EX-one', 'disposition': 'unused'}]}, 'disposition'),
            ('operational_dispositions', {'id': 'OD-one', 'execution_id': 'EX-review',
                'disposition': {'kind': 'continue', 'basis_refs': ['EX-target'], 'reason': 'Observe',
                                'next_owner': 'engine', 'next_review': None}, 'applied_at': 'now'}, 'applied_at'),
            ('operational_dispositions', {'id': 'OD-one', 'execution_id': 'EX-review',
                'disposition': {'kind': 'continue', 'basis_refs': ['EX-target'], 'reason': 'Observe',
                                'next_owner': 'engine', 'next_review': None}, 'error': 'unused'}, 'error')):
            with self.subTest(family=family, field=field):
                definition = contract.family('runtime', family)
                with self.assertRaisesRegex(ValueError, "Additional properties are not allowed.*" + field):
                    validate_record(definition.checker, row, 'runtime/' + family)

    def test_model_mismatch_return_preserves_a_closed_instance(self):
        from support.engine_control import running_work
        from support.storage_records import apply_control
        sim = Sim.activated()
        with running_work(sim) as call:
            apply_control(sim, 'close', origin='user', text='End this research')
            self.assertEqual(sim.runtime['status'], 'closed')
            call.finish({'status': 'failed', 'error_kind': 'model_policy', 'error': 'Wrong model',
                         'reported_models': ['other-model'], 'usage': {}})
            self.assertEqual(sim.runtime['status'], 'closed')
            self.assertEqual(reader(sim.engine).load(sim.engine.head)[2]['status'], 'closed')

    def test_operational_target_reference_is_checked_at_storage(self):
        from support.engine_control import running_work
        sim = Sim.activated()
        engine = sim.engine
        with running_work(sim) as call:
            prepared = engine._prepare_call({'id': 'AC-continue', 'role': 'operational_review', 'target': call.execution_id})
            engine._apply_operational_disposition(prepared['action'], {'kind': 'continue', 'basis_refs': [call.execution_id],
                'next_owner': 'engine', 'reason': 'Observe current work', 'next_review': None}, prepared['execution_id'])
            engine._save()
            head, instance, runtime = reader(engine).load(engine.head)
            changed = deepcopy(runtime)
            record, = changed['operational_dispositions'].values()
            record['target_execution_id'] = 'EX-absent'
            with ObservedCalls(write=engine.ports.git_backend.write_object) as calls:
                with self.assertRaisesRegex(ValueError, '^operational_dispositions references unknown record: EX-absent$'):
                    engine.store.save_with_state(head, instance, changed)
                self.assertEqual(calls.count('write'), 0)
            self.assertEqual(reader(engine).load(), (head, instance, runtime))
            for field in ('applied_at', 'error'):
                self.reject(engine, ('operational_dispositions', record['id'], field), 'obsolete',
                    'runtime/operational_dispositions/' + record['id'] +
                    "/: Additional properties are not allowed ('" + field + "' was unexpected)")
            # Corruption bypasses publication only here; the fresh reader must
            # still reject it and retain the valid historical head.
            path = 'runtime/operational_dispositions/' + record['id'] + '.json'
            blob = json.loads(reader(engine).read(path, head))
            blob['record']['target_execution_id'] = 'EX-absent'
            damaged = engine.store._store.publish(head, {path: canonical_json(blob)}).head
            with self.assertRaisesRegex(ValueError, '^operational_dispositions references unknown record: EX-absent$'):
                reader(engine).load(damaged)
            self.assertEqual(reader(engine).load(head), (head, instance, runtime))
