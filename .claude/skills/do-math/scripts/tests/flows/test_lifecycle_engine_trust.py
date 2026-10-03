"""Trust transitions on the real engine: re-checks through the Lean worker, activation and their records (``formal_engine``).

A transition re-checks every formal target in the new environment. Here the
re-check is the product's ``verify_formal`` and ``verify_lean`` on the Job port
fake, whose program runs ``formal._worker`` with the Lean double at its spawn
seam; the transition's knowledge was verified the same way and reviewed by the
model double (``engine_lifecycle.lifecycle_sim``). The new toolchain is
registered and configured by control, as a user moving to it does. One owner
start of a queued machine action is ``engine_lifecycle.run_machine``.

The verifier arguments are observed through ``sys.monitoring``
(``recorded_verifier``); a case needing
another Lean answer declares it on the Lean double or makes Lean fail.
"""
from copy import deepcopy
import os
from pathlib import Path
import unittest

import jsonschema

from do_math import trust_inventory as records
from do_math.execution_profiles import profile_ref
from do_math.knowledge import plan_impact, revision_roots
from do_math.record_schemas import RECORDS
from support.trust_inputs import trust_fixture, validation_fixture
from support.engine_lifecycle import (THEOREMS, applied, executions, extended, failing_lean, file_access, invalidate,
                                      lifecycle_sim, next_environment, only, prepared_environment, recorded_verifier,
                                      run_machine, solve_goal, transition, warm_lifecycle)
from support.known_defects import known_defect
from support.sim import Sim, warm_template


def setUpModule():
    warm_template()
    warm_lifecycle()
OLEAN = 'lib/lean/Init/Prelude.olean'


def olean(sim, environment):
    return Path(sim.instance['trust_environments'][environment]['toolchain']['executable']).parents[1] / OLEAN


def lean_jobs(sim):
    return [job for job in sim.jobs.launched if job.argv[1:3] == ['-B', '-c']]


class EmptyTransitionTests(unittest.TestCase):
    """A transition with no formal target, on the default activation (it holds no knowledge)."""

    def test_empty_trust_activation_records_profile_bound_machine_execution(self):
        sim = Sim.activated()
        before = {row['id'] for row in executions(sim, 'trust_activate')}
        environment = next_environment(sim, 'empty-transition')
        tid = transition(sim, environment)
        self.assertEqual(sim.runtime['trust_transitions'][tid]['targets'], [])
        run_machine(sim, 'trust_activate')
        attempts = [row for row in executions(sim, 'trust_activate') if row['id'] not in before]
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0]['status'], 'ended')
        self.assertEqual(attempts[0]['outcome'], 'output_accepted')
        self.assertEqual(attempts[0]['submission_receipt']['kind'], 'machine_output')
        self.assertIn('execution_profile_ref', attempts[0])
        self.assertEqual(sim.runtime['activities'][attempts[0]['owner_activity_id']]['status'], 'finished')
        self.assertEqual(sim.instance['active_trust_environment'], environment)

    def test_trust_transition_uses_current_storage_contract(self):
        sim = Sim.activated()
        tid = transition(sim, next_environment(sim, 'schema-transition'))
        jsonschema.validate(sim.runtime['trust_transitions'][tid], RECORDS['trust_transitions'])
        sim.engine._save()
        _, _, stored = sim.engine.store.load()
        self.assertEqual(stored['trust_transitions'][tid], sim.runtime['trust_transitions'][tid])


class TransitionTests(unittest.TestCase):
    """The reviewed theorems ``k1`` and ``k2`` move to the prepared environment."""

    def setUp(self):
        self.sim = lifecycle_sim()
        self.old = self.sim.instance['active_trust_environment']
        self.kids = [next(k for k, row in self.sim.instance['knowledge'].items() if row['title'] == name)
                     for name in THEOREMS]

    def start(self, environment=None):
        self.new = environment or prepared_environment(self.sim)
        self.tid = transition(self.sim, self.new)
        only(self.sim, 'trust_check', 'trust_activate')
        return self.tid

    def results(self):
        return self.sim.runtime['trust_transitions'][self.tid]['results']

    def test_full_transition_preserves_old_formal_records_and_full_command(self):
        """About 3 s, over the 2 s Sim budget: the start state holds two reviewed theorems whose review cycles (3.2 MB) every save copies and checks."""
        sim = self.sim
        calls = self.enterContext(recorded_verifier())
        self.start()
        prior = deepcopy(sim.instance['formal_results'])
        with self.assertRaisesRegex(ValueError, 'formal admission is blocked during a trust transition'):
            sim.engine._formal_environment()
        run_machine(sim, 'trust_check')
        self.assertEqual(sim.instance['active_trust_environment'], self.old)
        run_machine(sim, 'trust_check')
        run_machine(sim, 'trust_activate')
        self.assertEqual(sim.instance['active_trust_environment'], self.new)
        for fid, row in prior.items():
            self.assertEqual(sim.instance['formal_results'][fid], row)
        self.assertEqual(len(calls), 2)
        for arguments in calls:
            self.assertEqual(arguments['lean_command'], arguments['expected_toolchain']['configured_command'])
            self.assertEqual(arguments['expected_toolchain'], sim.instance['trust_environments'][self.new]['toolchain'])
        # The command the verifier received is the one the Lean worker ran.
        self.assertEqual([check['declarations'] for check in sim.lean.checks], [[name] for name in THEOREMS])
        for row in sim.runtime['executions'].values():
            self.assertIn('execution_profile_ref', row)
            self.assertIn('owner_activity_id', row)
            if row['role'] == 'trust_check':
                self.assertEqual(row['outcome'], 'output_accepted')
                self.assertEqual(row['submission_receipt']['kind'], 'machine_output')

    def test_the_activation_a_finished_recheck_queues_names_its_source(self):
        """About 3 s, over the 2 s Sim budget: the start state holds two reviewed theorems whose review cycles (3.2 MB) every save copies and checks."""
        sim = self.sim
        self.start()
        source = sim.runtime['trust_transitions'][self.tid]['source_ref']
        run_machine(sim, 'trust_check')
        run_machine(sim, 'trust_check')
        run_machine(sim, 'trust_activate')
        self.assertEqual(sim.instance['active_trust_environment'], self.new)
        execution = executions(sim, 'trust_activate')[-1]
        self.assertEqual(execution['action'].get('source_ref'), source,
                         'the activation keeps the provenance of the transition control, as an empty transition\'s does')

    def test_trust_recheck_needs_no_grant_naming_the_trust_roles(self):
        """About 3.5 s, over the 2 s Sim budget: the start state holds two reviewed theorems whose review cycles (3.2 MB) every save copies and checks."""
        # The documented research grant names research roles and formal_check (초기화-운전 3절); the dispatch
        # gate admits the trust roles on the user's transition control, and the re-check keeps that authority.
        sim = self.sim
        self.assertFalse([gid for gid, row in sim.instance['grants'].items()
                          if {'trust_check', 'trust_activate'} & set(row.get('roles', []))])
        self.start()
        run_machine(sim, 'trust_check')
        run_machine(sim, 'trust_check')
        run_machine(sim, 'trust_activate')
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        self.assertEqual(sim.instance['active_trust_environment'], self.new)

    def test_partial_failure_cannot_activate(self):
        """About 3 s, over the 2 s Sim budget: the start state holds two reviewed theorems whose review cycles (3.2 MB) every save copies and checks."""
        sim = self.sim
        self.start()
        failing_lean(sim)
        run_machine(sim, 'trust_check')
        run_machine(sim, 'trust_check')
        run_machine(sim, 'trust_activate')
        self.assertEqual(sim.instance['active_trust_environment'], self.old)
        self.assertEqual(sim.runtime['trust_transitions'][self.tid]['status'], 'failed')
        self.assertEqual({row['status'] for row in self.results().values()}, {'failed'})

    def test_changed_semantics_requires_independent_review(self):
        """About 3 s, over the 2 s Sim budget: the start state holds two reviewed theorems whose review cycles (3.2 MB) every save copies and checks."""
        sim = self.sim
        self.start()
        for name in THEOREMS:  # Lean now reports another proposition for each declaration
            sim.lean.allow(f'theorem {name} : 1 = 1 := rfl', [name],
                           signatures={name: name + ' : Changed proposition'})
        run_machine(sim, 'trust_check')
        run_machine(sim, 'trust_check')
        run_machine(sim, 'trust_activate')
        self.assertEqual(sim.instance['active_trust_environment'], self.old)
        self.assertEqual(sim.runtime['trust_transitions'][self.tid]['status'], 'ready')
        self.assertEqual(len([c for c in sim.runtime['review_cycles'].values() if c.get('transition_id') == self.tid]),
                         len(THEOREMS))

    def test_completed_target_not_repeated_on_recovery(self):
        """About 3 s, over the 2 s Sim budget: the start state holds two reviewed theorems whose review cycles (3.2 MB) every save copies and checks."""
        sim = self.sim
        self.start()
        action = run_machine(sim, 'trust_check')
        checks, jobs = len(sim.lean.checks), len(sim.jobs.launched)
        self.assertEqual(checks, 1)
        sim.engine._run_trust_check(action)
        self.assertEqual((len(sim.lean.checks), len(sim.jobs.launched)), (checks, jobs))
        run_machine(sim, 'trust_check')
        run_machine(sim, 'trust_activate')
        self.assertEqual(sim.instance['active_trust_environment'], self.new)

    def test_changed_olean_blocks_trust_check_before_compiling(self):
        """About 2.5 s, over the 2 s Sim budget: the start state holds two reviewed theorems whose review cycles (3.2 MB) every save copies and checks."""
        sim = self.sim
        self.start(next_environment(sim, 'changed-olean'))  # its own toolchain, since this test changes a file
        olean(sim, self.new).write_bytes(b'changed module bytes')
        run_machine(sim, 'trust_check')
        result = self.results()[self.kids[0]]
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['error_kind'], 'trust_environment')
        self.assertIn('olean fingerprint differs', result['reason'])
        self.assertEqual(result['environment_check']['changed_files'], ['toolchain/' + OLEAN])
        self.assertEqual((sim.lean.checks, lean_jobs(sim)), ([], []))

    def test_changed_fixed_source_never_activates_transition(self):
        """About 2.5 s, over the 2 s Sim budget: the start state holds two reviewed theorems whose review cycles (3.2 MB) every save copies and checks."""
        sim = self.sim
        e = sim.engine
        self.start()
        kid = self.kids[0]
        formal = e.instance['formal_results'][e.instance['knowledge'][kid]['formal_result_id']]
        # A published formal result is sealed (a save refuses an edited one), so the fixed source
        # changes the way the product changes it: the user revises the record's source.
        impact = plan_impact(e.instance, e.runtime, revision_roots(e.instance, kid), [])
        extended(e, 'knowledge', {'operation': 'revise', 'id': kid, 'changes': {'lean_code': formal['lean_code'] + '\n-- changed'},
                                  'declared_impact': impact['computed_impact'], 'reason': 'The fixed source changed.'})
        only(sim, 'trust_check', 'trust_activate')
        run_machine(sim, 'trust_check')
        run_machine(sim, 'trust_check')
        self.assertEqual(sim.instance['active_trust_environment'], self.old)
        self.assertEqual(self.results()[kid]['status'], 'failed')
        self.assertIn('trust transition basis changed', self.results()[kid]['reason'])

    def test_stop_and_resume_trust_check_preserves_attempt_lineage(self):
        """About 3.5 s, over the 2 s Sim budget: the start state holds two reviewed theorems whose review cycles (3.2 MB) every save copies and checks."""
        sim = self.sim
        self.start()
        spawn = sim.lean.spawn
        paused = []

        def pause_during_the_check(command, **options):
            if not paused:  # the user's pause arrives while the first re-check compiles
                paused.append(sim.control('pause', text='pause during the trust re-check'))
            return spawn(command, **options)
        sim.lean.spawn = pause_during_the_check
        sim.engine._save()
        sim.step()  # the owner starts the re-check, applies the pause before its result, and stops it
        first = next(row for row in executions(sim, 'trust_check'))
        self.assertTrue(paused)
        self.assertEqual(first['status'], 'ended')
        self.assertNotIn(self.kids[0], self.results())
        self.assertEqual(sim.instance['lifecycle']['state'], 'paused')
        sim.lean.spawn = spawn
        applied(sim, 'resume')
        only(sim, 'trust_check', 'trust_activate')
        sim.engine._save()
        sim.step()
        attempts = executions(sim, 'trust_check')
        self.assertEqual(len(attempts), 2)
        self.assertEqual(attempts[1]['owner_activity_id'], first['owner_activity_id'])
        self.assertEqual(attempts[1]['continuation_of'], first['id'])

    def test_rerecorded_baseline_is_followed_once_with_an_event(self):
        """About 2.5 s, over the 2 s Sim budget: the start state holds two reviewed theorems whose review cycles (3.2 MB) every save copies and checks."""
        sim = self.sim
        self.start(next_environment(sim, 'rerecorded'))  # its own toolchain, since this test re-records it
        environment = deepcopy(sim.instance['trust_environments'][self.new])
        before = deepcopy(sim.runtime['trust_bindings'][self.new])
        path = olean(sim, self.new)
        info = os.stat(path)
        os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns + 10**9))
        # What setup_lean.rerecord records after a metadata-only change (its host observation and
        # representative compile are the toolchain tools' own; sim.test_toolchain_tools covers them).
        record_path = Path(environment['toolchain_record']['path'])
        record = records.read_record(record_path)
        fingerprint = records.observe_fingerprint(environment['toolchain'])
        content = records.content_hashes(environment['toolchain'], fingerprint['files'])
        record['baselines'].append(records.new_baseline(fingerprint, content, validation_fixture(
            environment['toolchain'], record_path.parent / 'smoke.lean'), clock=sim.clock))
        records.write_record(record_path, record)
        rebound = records.binding(record)
        run_machine(sim, 'trust_check')
        run_machine(sim, 'trust_check')
        run_machine(sim, 'trust_activate')
        self.assertEqual(sim.instance['active_trust_environment'], self.new)
        self.assertEqual(sim.runtime['trust_bindings'][self.new], rebound)
        events = [row for row in sim.runtime['events'] if row['kind'] == 'trust_environment_rebound']
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['basis'], {'previous': before, 'current': rebound,
            'toolchain_record': environment['toolchain_record'], 'recorded_at': record['baselines'][-1]['recorded_at']})
        # Rebinding changed only the runtime binding; activation adds its status and receipt.
        activated = sim.instance['trust_environments'][self.new]
        self.assertEqual(environment, {**{k: v for k, v in activated.items() if k != 'validation_receipt'},
                                       'status': 'registered'})
        self.assertEqual(activated['validation_receipt']['binding'], rebound)

    @known_defect('KD-0801')
    def test_wrong_pinned_trust_command_ends_attempt_without_verifier(self):
        """About 4 s, over the 2 s Sim budget: the start state holds two reviewed theorems whose review cycles (3.2 MB) every save copies and checks; the pass also dispatches the research the owner queues."""
        sim = self.sim
        old_command = sim.instance['trust_environments'][self.old]['toolchain']['configured_command']
        old_ref = profile_ref([p for p in sim.instance['execution_profiles'].values()
                               if p['role'] == 'trust_check' and p['machine']['lean_command'] == old_command][-1])
        self.start()
        action = next(a for a in sim.runtime['queue'] if a['role'] == 'trust_check')
        action['profile_ref'] = old_ref  # an attempt pinned to the edition of the old command, as a requeued one is
        sim.runtime['queue'][:] = [action]
        sim.engine._save()
        sim.step()  # the owner's pass starts the one queued action: the pinned re-check
        self.assertEqual((sim.lean.checks, lean_jobs(sim)), ([], []))
        attempts = executions(sim, 'trust_check')
        self.assertEqual(len(attempts), 1, 'the pinned attempt ends instead of waiting in the queue')
        self.assertEqual(attempts[0]['status'], 'ended')
        self.assertEqual(attempts[0]['outcome'], 'execution_incomplete')
        self.assertEqual([row['id'] for row in sim.runtime['executions'].values() if row['status'] != 'ended'], [])

    def test_changed_transition_opens_real_review_without_live_publication(self):
        """About 3 s, over the 2 s Sim budget: the start state holds two reviewed theorems whose review cycles (3.2 MB) every save copies and checks."""
        sim = self.sim
        before = deepcopy(sim.instance)
        self.start()
        sim.lean.allow(f'theorem {THEOREMS[0]} : 1 = 1 := rfl', [THEOREMS[0]],
                       signatures={THEOREMS[0]: THEOREMS[0] + ' : Changed proposition'})
        run_machine(sim, 'trust_check')
        run_machine(sim, 'trust_check')
        run_machine(sim, 'trust_activate')
        transition_row = sim.runtime['trust_transitions'][self.tid]
        self.assertEqual(transition_row['status'], 'ready')
        cycles = [row for row in sim.runtime['review_cycles'].values() if row.get('transition_id') == self.tid]
        self.assertEqual(len(cycles), 1)
        self.assertTrue(any(a.get('review_cycle_id') == cycles[0]['id'] for a in sim.runtime['queue']))
        for family in ('knowledge', 'formal_results', 'identity_assessments', 'assessment_uses'):
            self.assertEqual(sim.instance.get(family), before.get(family))

    def test_trust_verifier_uses_registered_command_without_deadline(self):
        """About 2.5 s, over the 2 s Sim budget: the start state holds two reviewed theorems whose review cycles (3.2 MB) every save copies and checks."""
        sim = self.sim
        calls = self.enterContext(recorded_verifier())
        self.start()
        command = sim.instance['trust_environments'][self.new]['toolchain']['configured_command']
        run_machine(sim, 'trust_check')
        self.assertEqual(len(calls), 1)
        self.assertNotIn('timeout_seconds', calls[0])
        self.assertEqual(calls[0]['lean_command'], command)
        self.assertEqual(lean_jobs(sim)[-1].argv[1:3], ['-B', '-c'])


class GoalJudgmentTests(unittest.TestCase):
    def test_invalidated_split_knowledge_invalidates_dependent_goal(self):
        sim = lifecycle_sim()
        e = sim.engine
        kid = next(k for k, row in e.instance['knowledge'].items() if row['title'] == THEOREMS[0])
        solve_goal(e, kid)  # the goal auditors' judgments depend on the theorem
        self.assertEqual(e.instance['goal_status'], 'mathematically_solved')
        dependent = [j['id'] for j in e.instance['goal_judgments'] if kid in j.get('dependencies', [])]
        self.assertTrue(dependent)
        # A solution completes the research; an external rejection reopens it with the solution still current,
        # so the user can change the knowledge the solution rests on.
        e._save()
        applied(sim, 'decision', config={'change': {'kind': 'academic_rejection', 'actor': 'An external referee',
                                                    'text': 'The referee rejects the published solution.'}})
        e = sim.engine
        self.assertEqual((e.runtime['status'], e.instance['goal_status']), ('ready', 'mathematically_solved'))
        invalidate(e, kid, 'User withdrew this result')
        self.assertEqual(e.instance['goal_status'], 'unsolved')
        for judgment in e.instance['goal_judgments']:
            if judgment['id'] in dependent:
                self.assertFalse(judgment['current'])


class RegistrationTests(unittest.TestCase):
    def test_registration_reads_the_shared_record_without_scanning_files(self):
        sim = Sim.activated()
        e = sim.engine
        request = trust_fixture(sim.root / 'shared', ['synthetic-lean', 'shared'])
        toolchain = Path(request['toolchain']['executable']).parents[1]
        with file_access(toolchain) as touched:
            e._trust_control(request, 'UI-shared-one')
            e._trust_control(request, 'UI-shared-two')
        self.assertEqual(touched, [], 'registration scanned or hashed toolchain files')
        shared = [eid for eid, row in e.instance['trust_environments'].items() if row['toolchain'] == request['toolchain']]
        self.assertEqual(len(shared), 2)
        for eid in shared:
            self.assertEqual(e.instance['trust_environments'][eid]['toolchain_record'], request['toolchain_record'])
            self.assertEqual(e.runtime['trust_bindings'][eid], request['binding'])
        changed = {**request, 'binding': {**request['binding'], 'fingerprint_sha256': '0' * 64}}
        with self.assertRaisesRegex(ValueError, 'differs from its toolchain record'):
            e._trust_control(changed, 'UI-shared-bad')
        registered = dict(e.instance['trust_environments'])
        duplicated = {**request, 'allowed_axioms': [*request['allowed_axioms'], request['allowed_axioms'][0]]}
        with self.assertRaisesRegex(ValueError, 'foundation axiom profile differs'):
            e._trust_control(duplicated, 'UI-shared-dup')
        self.assertEqual(e.instance['trust_environments'], registered)
        # The same calls observe the toolchain when it is scanned: the check can see what it guards against.
        with file_access(toolchain) as touched:
            records.observe_fingerprint(request['toolchain'])
        self.assertTrue(touched)


if __name__ == '__main__':
    unittest.main()
