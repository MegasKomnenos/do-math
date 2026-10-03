"""4-B: every admission wait enters, stays and leaves through the real ledger."""
from copy import deepcopy
import unittest

from do_math import execution_profiles, reporting
from do_math.session_slots import SessionSlots
from do_math.wait_rules import ADMISSION_WAIT_RULES
from support.entry import entry
from support.fakes.clock import FakeClock
from support.fakes.jobs import FakeJobs
from support.provider_inputs import PROFILE_CONFIG, host_capacity_fixture


def queued(identifier, profile):
    return {'id': identifier, 'role': profile['role'], 'status': 'queued'}


def wait_case(kind):
    values = entry()
    clock, jobs = FakeClock(), FakeJobs()
    config = deepcopy(PROFILE_CONFIG)
    if kind == 'host_capacity':
        instance, selected, _ = host_capacity_fixture()
        profile = selected['recovery']
    else:
        if kind == 'capacity':
            config['session_limits']['work'] = {model: 1 for model in config['session_limits']['work']}
        instance = {**execution_profiles.build_profiles(config, host=values.ports.host), 'config': config}
        profile = next(row for row in instance['execution_profiles'].values() if row['role'] == 'research_work')
    runtime = {'executions': {}, 'reservations': {}, 'provider_waits': {}}
    slots = SessionSlots(runtime, instance, clock=clock, jobs=jobs, host_id=values.host_id)
    if kind in {'capacity', 'host_capacity'}:
        for number in range(3 if kind == 'host_capacity' else 1):
            identifier = 'EX-held-' + str(number)
            if not slots.acquire(identifier, profile=profile, execution=queued(identifier, profile), current_time=100):
                raise AssertionError('valid admission setup was refused')
        release = lambda: slots.release('EX-held-0')
        current = 100
    elif kind == 'provider_limit':
        slots.acquire('EX-limited', profile=profile, execution=queued('EX-limited', profile), current_time=100)
        slots.provider_result_from_run('EX-limited', {'status': 'failed', 'error_kind': 'provider_limit',
            'failure': {'kind': 'provider_limit', 'provider': profile['ai']['provider'],
                        'retry_at': '1970-01-01T00:01:55+00:00', 'evidence_ref': 'stdout.jsonl'}},
            config, current_time=100)
        slots.release('EX-limited')
        gate = next(iter(runtime['provider_waits'].values()))
        current = gate['retry_at'] - 1
        release = lambda: gate['retry_at']
    else:
        raise AssertionError('admission wait has no entry/negative/release scenario: ' + kind)
    return runtime, slots, profile, current, release, config


class AdmissionWaitContractTests(unittest.TestCase):
    def test_every_declared_wait_is_read_only_until_its_release_and_admits_once(self):
        for kind, rule in ADMISSION_WAIT_RULES.items():
            with self.subTest(kind=kind):
                runtime, slots, profile, current, release, config = wait_case(kind)
                before = deepcopy(runtime)
                for _ in range(2):
                    denied = slots.admission_check(profile, current_time=current)
                    self.assertFalse(denied['allowed'])
                    self.assertEqual(denied['wait']['kind'], kind)
                    self.assertLessEqual(set(rule['fields']), set(denied['wait']))
                    self.assertEqual(runtime, before)
                    projection = {'executions': {}, 'queue': [{'id': 'AC-no-task', 'role': profile['role'],
                        'dispatch_wait': deepcopy(denied['wait'])}]}
                    rows = reporting.dispatch_waits(projection)
                    self.assertEqual(rows, [{'action_id': 'AC-no-task', 'role': profile['role'], 'target': None,
                        'model_selection': None, 'wait': denied['wait']}])
                    text = reporting.render_dispatch_waits({'tasks': [], 'dispatch_waits': rows})
                    coordinate = denied['wait'].get('constraint_id') or denied['wait'].get('provider') or 'none'
                    self.assertEqual(text, [f"action AC-no-task: {profile['role']} wait={kind} constraint={coordinate} "
                        f"next={denied['wait']['next_owner']} reason={denied['wait']['reason']}"])
                    rows[0]['wait']['reason'] = 'changed observer copy'
                    self.assertEqual(projection['queue'][0]['dispatch_wait'], denied['wait'])
                    self.assertFalse(slots.acquire('EX-early', profile=profile,
                        execution=queued('EX-early', profile), current_time=current))
                    self.assertEqual(runtime, before)
                released = release()
                if kind == 'provider_limit':
                    current = released
                else:
                    self.assertTrue(released)
                self.assertTrue(slots.admission_check(profile, current_time=current)['allowed'])
                self.assertTrue(slots.acquire('EX-next', profile=profile, execution=queued('EX-next', profile), current_time=current))
                admitted = deepcopy(runtime)
                with self.assertRaisesRegex(ValueError,
                        '^execution IDs are single-use; only the registered unreserved execution can be admitted$'):
                    slots.acquire('EX-next', profile=profile, execution=runtime['executions']['EX-next'], current_time=current)
                self.assertEqual(runtime, admitted)
                if kind == 'provider_limit':
                    self.assertEqual(slots.admission_check(profile, current_time=current)['wait']['kind'], kind)
                    slots.provider_result_from_run('EX-next', {'status': 'completed'}, config, current_time=current + 1)
                    self.assertTrue(slots.release('EX-next'))
                    self.assertTrue(slots.admission_check(profile, current_time=current + 1)['allowed'])
