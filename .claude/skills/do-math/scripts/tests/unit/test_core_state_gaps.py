"""Persisted review, delegation and held-request semantic bindings on existing producers."""
from copy import deepcopy
from pathlib import Path
import re
import tempfile
import unittest

from do_math.canonical import exact_content_hash
from support.core_state_gaps import staged_states


class StateBindingTests(unittest.TestCase):
    def assertRejected(self, store, instance, runtime, reason):
        before = deepcopy((instance, runtime))
        with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
            store.validate_candidate(instance, runtime)
        self.assertEqual((instance, runtime), before)

    def test_staged_current_candidate_activation_and_review_input_are_bound(self):
        """T3 about 1.7 s: stored ReviewScene and three real registrations, needed for sealed transition bindings."""
        with tempfile.TemporaryDirectory() as directory:
            store, pending, activated, cid, tid = staged_states(Path(directory))
            store.validate_candidate(*pending)
            store.validate_candidate(*activated)
            instance, runtime = deepcopy(pending)
            staged = runtime['review_cycles'][cid]['staged_candidate']
            staged['target_environment']['source_ref'] = 'GS-other-environment-source'
            transition = runtime['trust_transitions'][tid]
            target = next(row for row in transition['targets'] if row['id'] == 'K1')
            verification = {key: value for key, value in transition['results']['K1'].items()
                            if key not in {'id', 'identity_review'}}
            staged['transition_basis'] = exact_content_hash({'transition_id': tid, 'target': target,
                'verification': verification, 'target_environment': staged['target_environment'],
                'from_environment': transition['from_environment']})
            self.assertRejected(store, instance, runtime, 'staged review differs from current transition evidence')
            instance, runtime = deepcopy(pending)
            binding = next(iter(runtime['review_cycles'][cid]['input_bindings'].values()))
            binding['profile_ref'] = deepcopy(instance['role_profile_refs']['maintenance'][0])
            self.assertRejected(store, instance, runtime, 'review input binding differs from its execution')
            instance, runtime = deepcopy(activated)
            runtime['trust_transitions'][tid]['status'] = 'failed'
            self.assertRejected(store, instance, runtime, 'staged identity assessment differs from its activated transition')
            # Unassigned reviewer seats are explicitly nullable, not stale profiles.
            instance, runtime = deepcopy(pending)
            runtime['review_cycles'][cid]['slot_profiles']['unassigned'] = None
            store.validate_candidate(instance, runtime)
            self.assertIsNone(runtime['review_cycles'][cid]['slot_profiles']['unassigned'])

    def test_delegation_frozen_rows_typed_namespaces_and_judgments_resolve(self):
        """T3 about 15.7 s including the existing delegated Sim template and its two independent judgments."""
        from support.governance_cases import delegated_sim
        sim = delegated_sim()
        instance, runtime = deepcopy((sim.instance, sim.runtime))
        sim.engine.store.validate_candidate(instance, runtime)
        application_id = next(iter(runtime['delegation_applications']))
        for damage, reason in (
                ('row', 'delegation frozen reference identity does not resolve'),
                ('namespace', 'delegation reference is not an independently typed record'),
                ('judgment', 'delegation judgment provenance mismatch')):
            with self.subTest(damage=damage):
                broken = deepcopy(runtime)
                application = broken['delegation_applications'][application_id]
                if damage == 'row':
                    next(iter(application['basis']['references'].values()))['id'] = 'absent-frozen-row'
                elif damage == 'namespace':
                    identifier = instance['id']
                    application['basis']['case']['basis_refs'].append(identifier)
                    application['basis']['references'][identifier] = {'id': identifier}
                else:
                    application['judgments']['interpret']['execution_id'] = 'EX-unissued'
                application['input_sha256'] = exact_content_hash(application['basis'])
                self.assertRejected(sim.engine.store, instance, broken, reason)

    def test_held_impact_requests_keep_the_original_bundle_and_assigned_input(self):
        """T3 about 22.2 s: existing impact Sim must produce a held bundle and its independent request."""
        from support.review_sim import held_impact, impact_sim
        sim = impact_sim()
        wait, _, identifier, _ = held_impact(sim)
        action_id = wait['action']['id']
        instance, runtime = deepcopy((sim.instance, sim.runtime))
        sim.engine.store.validate_candidate(instance, runtime)
        for damage, reason in (
                ('request', 'held impact request does not bind its original bundle/execution'),
                ('execution', 'held impact review execution differs from its assigned request')):
            with self.subTest(damage=damage):
                broken = deepcopy(runtime)
                held = broken['waiting_actions'][action_id]
                if damage == 'request':
                    held['review_requests'][identifier]['integration_id'] = 'IB-other'
                else:
                    held['review_execution_ids'] = {identifier: wait['execution_id']}
                self.assertRejected(sim.engine.store, instance, broken, reason)
