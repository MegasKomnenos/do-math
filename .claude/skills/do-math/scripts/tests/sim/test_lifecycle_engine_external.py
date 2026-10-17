"""External HTTP effects on the real engine: preparation, the send steps, uncertainty, retry and their records (``external_engine``).

The instance adopted explicit HTTP grants at its public activation
(``engine_lifecycle.external_sim``). The engine sends through the HTTP port;
its fake answers from a table by URL path, records every request with its
headers, and runs the product's request checks. One owner start of the queued
action is ``engine_lifecycle.run_machine``. A control that must arrive between
the send steps is written as the owner reads its inbox for the n-th time
(``control_at_inbox_check``), since the external stop judgment reads the inbox
before each step.
"""
from copy import deepcopy
from datetime import datetime, timedelta
import os
import unittest
from unittest.mock import patch

import jsonschema

from do_math.record_schemas import RECORD_RULES, RECORDS
from support.wait_reporting import assert_activity_wait_row
from support.engine_lifecycle import (CREDENTIAL, ORIGIN, applied, control_at_inbox_check, executions, external_sim,
                                      extended, http_fails, http_grant, lifecycle_sim, only, prepared_environment,
                                      run_machine, ticking_clock, transition, warm_external, warm_lifecycle)


def setUpModule():
    warm_external()
    warm_lifecycle()


def assert_times_ordered(test, transitions):
    """On a ticking clock: increasing times, one sample per step (a machine end writes stopping and ended with one)."""
    times = [datetime.fromisoformat(row['at']) for row in transitions]
    test.assertEqual(times, sorted(times))
    shared = [(before['to'], after['to']) for before, after in zip(transitions, transitions[1:]) if before['at'] == after['at']]
    test.assertLessEqual(set(shared), {('stopping', 'ended')}, 'only the end step shares one time sample')
    test.assertEqual(len(set(times)), len(times) - len(shared))
    test.assertGreater(len(set(times)), 1)


def operation(sim, oid='OP-audit'):
    return sim.runtime['external_operations'][oid]


class SendTests(unittest.TestCase):
    def setUp(self):
        self.sim = external_sim()
        self.e = self.sim.engine
        self.http = self.sim.ports.http

    def prepare(self, **options):
        config = http_grant(self.e, **options)
        extended(self.e, 'external', config)
        return config

    def test_http_success_finishes_activity_without_changing_effect_fact(self):
        self.http.table['/effect'] = (201, b'created', None)
        self.prepare()
        run_machine(self.sim, 'external_action')
        op = operation(self.sim)
        self.assertEqual(op['status'], 'confirmed')
        self.assertIs(op['succeeded'], True)
        self.assertEqual(len(self.http.requests), 1)
        ex = self.sim.runtime['executions'][op['execution_id']]
        self.assertEqual(self.sim.runtime['activities'][ex['owner_activity_id']]['status'], 'finished')
        self.assertEqual(ex['outcome'], 'output_accepted')
        self.assertEqual(ex['submission_receipt']['kind'], 'machine_output')

    def test_revocation_before_transport_cancels(self):
        config = self.prepare()
        extended(self.e, 'decision', {'change': {'kind': 'revoke', 'grant_id': config['grant_id']}})
        self.assertEqual(operation(self.sim)['status'], 'cancelled')
        self.e._run_external_action({'role': 'external_action', 'target': config['id'], 'grant_id': config['grant_id']})
        self.assertEqual(self.http.requests, [])
        self.assertEqual(operation(self.sim)['status'], 'cancelled')

    def test_prepare_replay_preserves_unknown_ledger(self):
        config = self.prepare()
        operation(self.sim).update(status='unknown', transmitted=True)
        before = deepcopy(operation(self.sim))
        extended(self.e, 'external', config)
        self.assertEqual(operation(self.sim), before)

    def test_authority_revoked_at_send_gate_prevents_transport(self):
        config = self.prepare()
        # The external stop judgment reads the inbox before each send step; the revocation arrives at the fourth read,
        # the one the send step's own ledger publication makes just before transport.
        with control_at_inbox_check(self.sim, 4, 'decision',
                                    config={'change': {'kind': 'revoke', 'grant_id': config['grant_id']}}) as arrival:
            run_machine(self.sim, 'external_action')
        self.assertIsNotNone(arrival['request'])
        self.assertEqual(self.http.requests, [])
        self.assertEqual(operation(self.sim)['status'], 'cancelled')

    def test_failure_before_any_send_step_is_an_untransmitted_cancellation(self):
        config = self.prepare()
        # A pause arrives at the first inbox read, which the first ledger publication makes: the send fails there.
        with control_at_inbox_check(self.sim, 1, 'pause') as arrival:
            run_machine(self.sim, 'external_action')
        self.assertIsNotNone(arrival['request'])
        self.assertEqual(self.http.requests, [])
        stored = self.e.store.load()[2]['external_operations']['OP-audit']
        self.assertEqual((stored['status'], stored['transmitted'], stored['succeeded']), ('cancelled', False, False))
        RECORD_RULES['external_operations'](stored)  # the storage rules of one operation record
        first = deepcopy(self.sim.runtime['executions'][stored['execution_id']])
        owner = first['owner_activity_id']
        activity = deepcopy(self.sim.runtime['activities'][owner])
        self.assertEqual(activity['waiting']['kind'], 'external_followup')
        self.assertEqual(activity['waiting']['condition'], {'operation_id': stored['id'], 'status': 'cancelled'})
        assert_activity_wait_row(self, self.e.status(), owner, activity)
        retry = {'operation': 'retry', 'id': stored['id'], 'grant_id': config['grant_id']}
        applied(self.sim, 'external', config=retry, request_id='UC-untransmitted-retry')
        self.assertEqual(len([row for row in self.sim.runtime['queue'] if row.get('target') == stored['id']]), 1)
        self.assertEqual(self.sim.runtime['activities'][owner]['status'], 'ready')
        prepared = deepcopy(self.sim.runtime)
        applied(self.sim, 'external', config=retry, request_id='UC-untransmitted-retry')
        self.assertEqual(self.sim.runtime, prepared)
        self.assertEqual(self.http.requests, [])
        self.http.table['/effect'] = (201, b'created', None)
        applied(self.sim, 'resume')
        run_machine(self.sim, 'external_action')
        self.assertEqual(len(self.http.requests), 1)
        self.assertEqual(self.sim.runtime['executions'][first['id']], first)
        current = self.sim.runtime['executions'][operation(self.sim)['execution_id']]
        self.assertEqual((current['owner_activity_id'], current['continuation_of']), (owner, first['id']))
        self.assertEqual(self.sim.runtime['activities'][owner]['status'], 'finished')

    def test_an_unrelated_control_during_the_send_steps_does_not_cancel_the_effect(self):
        self.http.table['/effect'] = (201, b'created', None)
        self.prepare()
        unrelated = {'id': 'GR-unrelated', 'kind': 'local', 'roles': ['maintenance'], 'reuse': 'reusable',
                     'expires_at': (self.sim.clock.wall() + timedelta(days=1)).isoformat()}
        with control_at_inbox_check(self.sim, 1, 'decision', config={'change': {'kind': 'grant', 'grant': unrelated}}):
            run_machine(self.sim, 'external_action')
        self.assertIn('GR-unrelated', self.sim.instance['grants'])  # the owner applied the control
        self.assertEqual(operation(self.sim)['status'], 'confirmed', operation(self.sim).get('error'))
        self.assertEqual(len(self.http.requests), 1)
        confirmed = deepcopy(operation(self.sim))
        execution = deepcopy(self.sim.runtime['executions'][confirmed['execution_id']])
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'output_accepted'))
        self.assertEqual(execution['submission_receipt']['kind'], 'machine_output')
        self.assertEqual(self.sim.runtime['activities'][execution['owner_activity_id']]['status'], 'finished')
        self.sim.restart()
        self.assertEqual(operation(self.sim), confirmed)
        self.assertEqual(self.sim.runtime['executions'][execution['id']], execution)

    def test_real_loopback_unknown_reconcile_and_retry_share_activity(self):
        self.http.table['/effect'] = (503, b'uncertain', None)
        http_grant(self.e, 'GR-http', prefixes=('/',))
        extended(self.e, 'external', {'operation': 'prepare', 'id': 'EO-test', 'grant_id': 'GR-http',
                                      'request': {'method': 'POST', 'url': ORIGIN + '/effect', 'body': 'test'}})
        run_machine(self.sim, 'external_action')
        op = operation(self.sim, 'EO-test')
        self.assertEqual(op['http_status'], 503)
        self.assertEqual(op['status'], 'unknown')
        self.assertIsNone(op['succeeded'])
        first = deepcopy(self.sim.runtime['executions'][op['execution_id']])
        owner = first['owner_activity_id']
        activity = deepcopy(self.sim.runtime['activities'][owner])
        self.assertEqual(activity['waiting']['kind'], 'external_reconciliation')
        assert_activity_wait_row(self, self.e.status(), owner, activity)
        self.assertEqual(self.sim.runtime['activities'][owner], activity)
        with self.assertRaisesRegex(ValueError, 'retry requires request-bound effect or idempotency evidence'):
            extended(self.e, 'external', {'operation': 'retry', 'id': op['id'], 'grant_id': 'GR-http'})
        with self.assertRaisesRegex(ValueError, 'reconciliation requires structured operation evidence'):
            extended(self.e, 'external', {'operation': 'reconcile', 'id': op['id'], 'result': 'failed', 'evidence': 'string'})
        applied(self.sim, 'external', config={'operation': 'reconcile', 'id': op['id'], 'result': 'failed', 'evidence': {
            'evidence_ref': 'remote-admin-log', 'operation_id': op['id'], 'request_sha256': op['request_sha256'],
            'idempotency_key': op['idempotency_key'], 'fact': 'effect_absent',
            'observed_at': self.sim.clock.now()}})
        failed = deepcopy(operation(self.sim, 'EO-test'))
        self.assertIs(failed['effect_absent'], True)
        activity = deepcopy(self.sim.runtime['activities'][owner])
        self.assertEqual(activity['waiting'], {**activity['waiting'], 'kind': 'external_followup',
            'condition': {'operation_id': op['id'], 'status': 'failed'}, 'next_owner': 'user'})
        assert_activity_wait_row(self, self.e.status(), owner, activity)
        self.assertEqual(len(self.http.requests), 1)
        retry = {'operation': 'retry', 'id': op['id'], 'grant_id': 'GR-http'}
        applied(self.sim, 'external', config=retry, request_id='UC-external-retry-once')
        successor, = [row for row in self.sim.runtime['queue'] if row.get('target') == op['id']]
        self.assertEqual((successor['owner_activity_id'], successor['continuation_of']), (owner, first['id']))
        self.assertEqual(self.sim.runtime['activities'][owner]['status'], 'ready')
        before_replay = deepcopy(self.sim.runtime)
        applied(self.sim, 'external', config=retry, request_id='UC-external-retry-once')
        self.assertEqual(self.sim.runtime, before_replay)
        self.assertEqual(len(self.http.requests), 1)
        # The new attempt is not the reconciled one: its handling goes with its reconciliation.
        retried = operation(self.sim, 'EO-test')
        self.assertEqual(retried['status'], 'prepared')
        self.assertNotIn('handling', retried)
        self.assertNotIn('reconciliation', retried)
        RECORD_RULES['external_operations'](retried)  # the storage rules of one operation record
        self.http.table['/effect'] = (201, b'created', None)
        run_machine(self.sim, 'external_action')
        self.assertEqual(len(self.http.requests), 2)
        attempts = executions(self.sim, 'external_action')
        self.assertEqual(attempts[0]['owner_activity_id'], attempts[1]['owner_activity_id'])
        self.assertEqual(attempts[1]['continuation_of'], attempts[0]['id'])
        self.assertEqual(self.sim.runtime['executions'][first['id']], first)
        self.assertEqual(self.sim.runtime['activities'][owner]['status'], 'finished')
        self.assertEqual(operation(self.sim, 'EO-test')['request'], failed['request'])
        self.sim.restart()
        self.assertEqual(self.sim.runtime['executions'][first['id']], first)
        self.assertNotIn(owner, self.sim.engine.status()['waiting_activities'])

    def test_public_success_reconciliation_finishes_only_the_exact_unknown_owner(self):
        self.http.table['/effect'] = (503, b'uncertain', None)
        config = self.prepare()
        run_machine(self.sim, 'external_action')
        first = deepcopy(operation(self.sim))
        first_execution = deepcopy(self.sim.runtime['executions'][first['execution_id']])
        owner = first_execution['owner_activity_id']
        extended(self.e, 'external', {**config, 'id': 'OP-other'})
        run_machine(self.sim, 'external_action')
        other = deepcopy(operation(self.sim, 'OP-other'))
        other_owner = self.sim.runtime['executions'][other['execution_id']]['owner_activity_id']
        other_activity = deepcopy(self.sim.runtime['activities'][other_owner])
        self.sim.restart()
        self.e = self.sim.engine
        # A redelivered preparation and an owner retry without evidence cannot send again.
        applied(self.sim, 'external', config=config)
        self.e._run_external_action(first_execution['action'])
        self.assertEqual(operation(self.sim), first)
        self.assertEqual(len(self.http.requests), 2)
        activity = deepcopy(self.sim.runtime['activities'][owner])
        assert_activity_wait_row(self, self.e.status(), owner, activity)
        proof = {'operation': 'reconcile', 'id': first['id'], 'result': 'confirmed', 'evidence': {
            'operation_id': first['id'], 'request_sha256': first['request_sha256'],
            'idempotency_key': first['idempotency_key'], 'fact': 'succeeded',
            'evidence_ref': 'remote:exact-receipt', 'observed_at': self.sim.clock.now()}}
        applied(self.sim, 'external', config=proof, request_id='UC-exact-reconcile')
        self.assertEqual(self.sim.runtime['activities'][owner]['status'], 'finished')
        self.assertEqual(self.sim.runtime['activities'][other_owner], other_activity)
        self.assertEqual(operation(self.sim, 'OP-other'), other)
        self.assertEqual(self.sim.runtime['executions'][first_execution['id']], first_execution)
        current = deepcopy(self.sim.runtime)
        applied(self.sim, 'external', config=proof, request_id='UC-exact-reconcile')
        self.assertEqual(self.sim.runtime, current)
        self.assertEqual(len(self.http.requests), 2)
        self.assertNotIn(owner, self.e.status()['waiting_activities'])

    def test_scoped_http_control_preserves_exact_envelope(self):
        self.http.table['/effect'] = (201, b'ok', None)
        scope = {'included_targets': ['TARGET'], 'purposes': ['publish'], 'subjects': ['publisher'],
                 'execution_kinds': ['machine']}
        config = http_grant(self.e, scope=scope)
        fields = {'target_id': 'TARGET', 'purpose': 'publish', 'subject': 'publisher', 'actor_kind': 'machine'}
        extended(self.e, 'external', {**config, **fields})
        op = operation(self.sim)
        self.assertEqual({k: op[k] for k in fields}, fields)
        run_machine(self.sim, 'external_action')
        self.assertEqual(len(self.http.requests), 1)
        with self.assertRaisesRegex(ValueError, 'purpose outside grant'):
            extended(self.e, 'external', {**config, **fields, 'purpose': 'different'})

    def test_once_http_first_send_and_distinct_request(self):
        self.http.table['/effect'] = (201, b'ok', None)
        config = self.prepare(once=True)
        run_machine(self.sim, 'external_action')
        self.assertEqual(len(self.http.requests), 1)
        self.assertEqual(operation(self.sim)['status'], 'confirmed')
        with self.assertRaisesRegex(ValueError, 'one-case grant already reserved or consumed'):
            extended(self.e, 'external', {**config, 'id': 'OP-other'})

    def test_once_unknown_send_cannot_be_replayed_without_evidence(self):
        config = self.prepare(once=True)
        action = next(a for a in self.sim.runtime['queue'] if a['role'] == 'external_action')
        http_fails(self.sim, TimeoutError('no answer'))
        run_machine(self.sim, 'external_action')
        self.assertEqual(len(self.http.requests), 1)
        before = deepcopy(operation(self.sim))
        self.assertEqual(before['status'], 'unknown')
        with self.assertRaisesRegex(ValueError, 'retry requires request-bound effect or idempotency evidence'):
            extended(self.e, 'external', {'operation': 'retry', 'id': config['id'], 'grant_id': config['grant_id']})
        self.e._run_external_action(action)
        self.assertEqual(len(self.http.requests), 1)
        self.assertEqual(operation(self.sim)['execution_id'], before['execution_id'])

    def test_credential_resume_has_new_attempt_receipt_and_cleared_wait(self):
        sim, http = self.sim, self.http
        http.table['/effect'] = (201, b'ok', None)
        config = self.prepare(credentials=True)
        ticking_clock(sim)  # no frozen time: every sample the attempts record differs, as on the host clock
        with patch.dict(self.e.environment):
            self.e.environment.pop(CREDENTIAL, None)
            run_machine(sim, 'external_action')
        self.assertEqual(http.requests, [])
        before = deepcopy(operation(sim))
        first = deepcopy(sim.runtime['executions'][before['execution_id']])
        self.assertEqual(first['status'], 'ended')
        extended(self.e, 'external', config)
        with patch.dict(self.e.environment, {CREDENTIAL: 'synthetic-local-token'}):
            run_machine(sim, 'external_action')
        self.assertEqual(len(http.requests), 1)
        self.assertEqual(http.requests[0][1], [('X-Test', 'synthetic-local-token')])
        op = operation(sim)
        self.assertNotEqual(op['execution_id'], first['id'])
        self.assertEqual(sim.runtime['executions'][first['id']], first)
        current = sim.runtime['executions'][op['execution_id']]
        self.assertEqual(current['continuation_of'], first['id'])
        self.assertEqual(current['owner_activity_id'], first['owner_activity_id'])
        self.assertEqual(current['outcome'], 'output_accepted')
        self.assertEqual(current['submission_receipt']['kind'], 'machine_output')
        self.assertNotIn('waiting_reason', op)
        for key in ('id', 'request_sha256', 'idempotency_key'):
            self.assertEqual(op[key], before[key])
        for execution in (first, current):
            transitions = execution['transitions']
            # The preserved transition sequence records causal state order.
            self.assertEqual(transitions[0]['from'], 'queued')
            self.assertEqual(transitions[-1]['to'], 'ended')
            for previous, following in zip(transitions, transitions[1:]):
                self.assertEqual(previous['to'], following['from'])
            self.assertTrue(all(datetime.fromisoformat(row['at']).utcoffset() == timedelta(0) for row in transitions))
            assert_times_ordered(self, transitions)
            self.assertEqual(execution['ended_at'], transitions[-1]['at'])
        self.assertLess(datetime.fromisoformat(first['ended_at']), datetime.fromisoformat(current['transitions'][0]['at']))


class PublicCredentialResumeTests(unittest.TestCase):
    def test_public_external_once_credential_resume_persists_attempts(self):
        # The subject is how public controls and restarts record the two attempts, not activation.
        sim = external_sim()
        http = sim.ports.http
        http.table['/effect'] = (201, b'ok', None)
        applied(sim, 'decision', config={'change': {'kind': 'grant', 'grant': {
            'id': 'GR-public-http', 'kind': 'http', 'reuse': 'once', 'allowed_origins': [ORIGIN],
            'allowed_methods': ['POST'], 'allowed_path_prefixes': ['/effect'], 'credential_env': {'X-Test': CREDENTIAL}}}})
        config = {'operation': 'prepare', 'id': 'OP-public', 'grant_id': 'GR-public-http',
                  'request': {'method': 'POST', 'url': ORIGIN + '/effect', 'body': 'synthetic local request'}}
        applied(sim, 'external', config=config)
        ticking_clock(sim)  # a flowing clock, as the host's: the recorded times can be out of order
        with patch.dict(sim.environment):
            sim.environment.pop(CREDENTIAL, None)
            run_machine(sim, 'external_action')
        before = deepcopy(operation(sim, 'OP-public'))
        first = deepcopy(sim.runtime['executions'][before['execution_id']])
        self.assertEqual(first['status'], 'ended')
        self.assertEqual(http.requests, [])
        sim.restart()
        applied(sim, 'external', config=config, request_id='UC-public-external-credential-resume')
        with patch.dict(sim.environment, {CREDENTIAL: 'synthetic-local-token'}):
            run_machine(sim, 'external_action')
        sim.restart()
        op = operation(sim, 'OP-public')
        current = sim.runtime['executions'][op['execution_id']]
        self.assertEqual(len(http.requests), 1)
        self.assertEqual(op['status'], 'confirmed')
        self.assertNotIn('waiting_reason', op)
        for key in ('id', 'request_sha256', 'idempotency_key'):
            self.assertEqual(op[key], before[key])
        self.assertEqual(sim.runtime['executions'][first['id']], first)
        self.assertEqual(current['continuation_of'], first['id'])
        self.assertEqual(current['owner_activity_id'], first['owner_activity_id'])
        self.assertEqual(current['submission_receipt']['kind'], 'machine_output')
        self.assertEqual(current['outcome'], 'output_accepted')
        for execution in (first, current):
            assert_times_ordered(self, execution['transitions'])
        self.assertLess(datetime.fromisoformat(first['transitions'][-1]['at']),
                        datetime.fromisoformat(current['transitions'][0]['at']), 'the second attempt follows the first')


class RecordTests(unittest.TestCase):
    """HTTP effects and a trust transition on the instance with the reviewed theorems."""

    def test_machine_records_use_registered_schema_and_existing_source_provenance(self):
        """About 3 s, over the 2 s Sim budget: the start state holds two reviewed theorems whose review cycles (3.2 MB) every save copies and checks."""
        sim = lifecycle_sim()
        e = sim.engine
        sim.ports.http.table['/effect'] = (201, b'ok', None)
        config = http_grant(e)
        extended(e, 'external', config)
        op = operation(sim)

        def validate(record, family):
            self.assertEqual([error.message for error in
                              jsonschema.Draft202012Validator(RECORDS[family]).iter_errors(record)], [])
        validate(op, 'external_operations')
        event = next(row for row in e.runtime['events']
                     if row['kind'] == 'external_operation_prepared' and row['target'] == op['id'])
        self.assertIn(event['source_ref'], e.instance['governance_sources'])
        run_machine(sim, 'external_action')
        validate(operation(sim), 'external_operations')
        # The trust activation of the instance's public activation was queued by the user's transition control.
        transition(sim, prepared_environment(sim))
        only(sim, 'trust_check', 'trust_activate')
        run_machine(sim, 'trust_check')
        run_machine(sim, 'trust_check')
        roles = [row['role'] for row in e.runtime['executions'].values()]
        self.assertTrue({'external_action', 'trust_activate', 'trust_check'} <= set(roles))
        for execution in e.runtime['executions'].values():
            if execution['role'] in {'external_action', 'trust_activate', 'trust_check'}:
                validate(execution, 'executions')
                self.assertTrue(execution['action']['source_ref'])
                if execution['role'].startswith('trust_'):
                    self.assertEqual(execution['result_ref'], execution['submission_receipt']['evidence_ref'])


if __name__ == '__main__':
    unittest.main()


class AcademicPrerequisiteTests(unittest.TestCase):
    """Layer-2 preparation and send recheck, including the separate public completed-state gate."""
    def test_academic_control_binds_current_real_prerequisite(self):
        from do_math.academic import current_requirements
        from do_math.execution_profiles import match_profile_ref, profile_ref
        from do_math.knowledge import plan_impact
        from support.engine_lifecycle import solve_goal, THEOREMS
        from support.provider_probes import ObservedCalls
        sim = lifecycle_sim()
        e = sim.engine
        config = http_grant(e, scope={'requires_academic': True})
        with self.assertRaisesRegex(ValueError, 'no current solution for this request'):
            e._external_control(config, 'UC-before-solution')
        kid = next(k for k, row in e.instance['knowledge'].items() if row['title'] == THEOREMS[0])
        solve_goal(e, kid)
        basis = e._solution_basis()
        self.assertIsNotNone(basis)
        self.assertEqual(e.runtime['status'], 'completed')
        e._save()
        # The layer-2 consumer can bind valid producer state; this does not claim
        # the closed-instance public control dispatcher permits the request.
        e._external_control(config, 'UC-after-solution')
        e._save()
        op = e.runtime['external_operations'][config['id']]
        self.assertEqual(op['academic_basis'], {'solution_basis': basis,
                         'requirements_sha256': current_requirements(e.instance)['sha256']})
        self.assertNotIn('academic_binding', op)
        action = deepcopy(next(row for row in e.runtime['queue']
                               if row['role'] == 'external_action' and row['target'] == config['id']))
        profile = e._execution_profile(action)
        self.assertEqual(action['profile_ref'], profile_ref(profile))
        self.assertIn(action['profile_ref'], e.instance['role_profile_refs']['external_action'])
        self.assertEqual(match_profile_ref(e.instance['execution_profiles'], action['profile_ref']), profile)
        self.assertEqual((action['actor_kind'], op['actor_kind']), ('machine', 'machine'))
        self.assertEqual(action['grant_id'], config['grant_id'])
        grant = e.instance['grants'][config['grant_id']]
        e._validate_external(op, grant)  # the unchanged request and grant pass before evidence withdrawal
        impact = plan_impact(e.instance, e.runtime, [kid], [])
        e._knowledge_control({'operation': 'invalidate', 'id': kid, 'reason': 'Evidence was withdrawn',
                              'declared_impact': impact['computed_impact']}, 'UC-evidence-withdrawal')
        e._invalidate_goal_currentness()
        self.assertEqual(e.instance['goal_status'], 'unsolved')
        self.assertIsNone(e._solution_basis())
        e._save()
        before = len(sim.ports.http.requests)
        self.assertEqual(e.runtime['external_operations'][config['id']], op)
        self.assertEqual(e.instance['grants'][config['grant_id']], grant)
        expected_operation, expected_grant = deepcopy(op), deepcopy(grant)
        with ObservedCalls(send=sim.ports.http.request, check=e._validate_external,
                           prerequisite=e._external_prerequisite,
                           capture={'prerequisite': lambda args: deepcopy({key: args[key]
                                    for key in ('operation', 'grant')})}) as calls:
            e._run_external_action(action)
        self.assertEqual(calls.count('send'), 0)
        self.assertEqual(calls.count('check'), 1)
        self.assertEqual(calls.count('prerequisite'), 1)
        observed = calls.captured('prerequisite')[0]
        # The execution ID is allocated on entry, before the prerequisite check.
        expected_operation['execution_id'] = e.runtime['external_operations'][config['id']]['execution_id']
        self.assertEqual(observed, {'operation': expected_operation, 'grant': expected_grant})
        self.assertEqual(len(sim.ports.http.requests), before)
        rejected = e.runtime['external_operations'][config['id']]
        reason = 'current academic prerequisite is not established'
        self.assertEqual(rejected['status'], 'cancelled')
        self.assertIs(rejected['transmitted'], False)
        self.assertEqual(rejected['error'], reason)
        events = [row for row in e.runtime['events']
                  if row['kind'] == 'external_operation_not_authorized' and row['target'] == config['id']]
        self.assertEqual([row['reason'] for row in events], [reason])
        e._save()
        stored = e.store.load()[2]
        self.assertEqual(stored['external_operations'][config['id']], rejected)
        # Storage assigns event_seq; preserve the event identity and exact
        # rejection reason across that real publication.
        self.assertEqual([(row['id'], row['reason']) for row in stored['events']
                          if row['kind'] == 'external_operation_not_authorized' and row['target'] == config['id']],
                         [(events[0]['id'], reason)])

    def test_completed_solution_blocks_generic_academic_request_at_public_control(self):
        from support.engine_lifecycle import solve_goal, THEOREMS
        sim = lifecycle_sim()
        config = http_grant(sim.engine, scope={'requires_academic': True})
        kid = next(k for k, row in sim.instance['knowledge'].items() if row['title'] == THEOREMS[0])
        solve_goal(sim.engine, kid)
        self.assertIsNotNone(sim.engine._solution_basis())
        self.assertEqual(sim.engine._academic_status()['status'], 'not_applicable')
        self.assertEqual(sim.runtime['status'], 'completed')
        sim.engine._save()
        request = sim.control('external', config=config)
        sim.engine.process_controls()
        result = sim.engine.control_result(request['request_id'])
        self.assertEqual(result['effect'], 'rejected')
        self.assertIn('closed/completed', result['reason'])
        self.assertNotIn(config['id'], sim.runtime['external_operations'])
        self.assertEqual(sim.ports.http.requests, [])
