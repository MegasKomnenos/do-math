"""Task contracts: their shape and review currentness, obligation dispositions, derived readiness, plan
submission checks and prepared dependencies (``task_contracts``, ``planning``, ``contracts``,
``revisions``, ``task_scope``, ``submission``; layer 2), moved from ``test_task_contracts``.

The tests call the product's pure functions on the plain records of
``record_fixtures`` (``approved_task``: task ``TK-1`` reading source ``SO-1``
under grant ``GR-1``, with an approved contract review; ``transfer_assessment``:
``TK-1`` returned and ``OB-2`` transferred to ``TK-2`` by the user decision
``DC-1``). Nothing of the product is replaced. Rejections the legacy tests
checked by exception type alone now pin the product's message.
"""
from copy import deepcopy
import hashlib
import re
import unittest

from jsonschema import Draft202012Validator

from do_math import contracts, planning, submission, task_contracts
from do_math.execution_profiles import profile_ref
from support.record_builders import apply_assessment, approve_task, approved_task, task_contract, task_disposition, transfer_assessment
from support.role_answers import candidate


class TaskContractReviewTests(unittest.TestCase):
    def test_preparation_allowlist_uses_both_fixed_fields_and_same_response_ids_over_the_finite_population(self):
        from itertools import product
        refs = ('KN-input', 'TK-input', 'source:input.txt')
        populations = [tuple(ref for n, ref in enumerate(refs) if mask & (1 << n)) for mask in range(8)]
        self.assertEqual(task_contracts.PREPARATION_INPUT_BASIS_FIELDS,
                         ('available_input_refs', 'supplied_record_ids'))
        for available, records, prepared in product(populations, repeat=3):
            context = {'available_input_refs': list(available), 'supplied_record_ids': list(records),
                       'history': ['KN-never-issued'], 'accepted': ['TK-never-issued']}
            before = deepcopy(context)
            actual = task_contracts.preparation_input_refs(context, prepared)
            with self.subTest(available=available, records=records, prepared=prepared):
                self.assertEqual(actual, set(available) | set(records) | set(prepared))
                self.assertEqual(context, before)
                self.assertEqual(task_contracts.preparation_input_refs(
                    {**context, 'available_input_refs': list(reversed(available)) * 2}, prepared), actual)
        for missing in task_contracts.PREPARATION_INPUT_BASIS_FIELDS:
            context = {'available_input_refs': [], 'supplied_record_ids': []}
            context.pop(missing)
            with self.subTest(missing=missing), self.assertRaisesRegex(ValueError,
                    '^preparation input basis is absent: ' + missing + '$'):
                task_contracts.preparation_input_refs(context, [])

    def test_input_classification_agrees_for_every_small_reference_population(self):
        """Separate input-supply rule: future sources may be authored but never counted as arrived."""
        refs = ('KN-present', 'TK-present', 'source:arrived.txt', 'source:future.txt',
                'tool:lean', 'unknown-record')
        checked = 0
        for supplied_mask in range(1 << len(refs)):
            supplied = {ref for index, ref in enumerate(refs) if supplied_mask & (1 << index)}
            for requested_mask in range(1 << len(refs)):
                requested = [ref for index, ref in enumerate(refs) if requested_mask & (1 << index)]
                strict = task_contracts.unsupplied_task_inputs(requested, supplied, admit_named_sources=False)
                authoring = task_contracts.unsupplied_task_inputs(requested, supplied, admit_named_sources=True)
                expected_strict = sorted(set(requested) - supplied)
                expected_authoring = [ref for ref in expected_strict if not ref.startswith('source:')]
                with self.subTest(supplied_mask=supplied_mask, requested_mask=requested_mask):
                    self.assertEqual(strict, expected_strict)
                    self.assertEqual(authoring, expected_authoring)
                    self.assertLessEqual(set(authoring), set(strict))
                    self.assertEqual(task_contracts.unsupplied_task_inputs(requested * 2, supplied,
                        admit_named_sources=False), strict)
                    if not strict:
                        self.assertEqual(authoring, [])
                checked += 1
        self.assertEqual(checked, 2 ** (2 * len(refs)))

    def test_readiness_and_work_profile_selection_agree_over_the_finite_requirement_space(self):
        """3-C/B-16: both work roles, every rating/floor/allowlist/pinned-tier combination.

        Domain producers seal every profile and contract review. No owner run,
        external process or model is needed; expected eligibility is computed
        from the contract's tier order and explicitly supplied allowlist.
        """
        from itertools import product
        from do_math import model_policy
        from do_math.execution_profiles import RESEARCH_PRODUCER_ROLES, build_profiles
        from support.entry import entry
        checked = 0
        tiers = model_policy.TIERS
        for role in sorted(RESEARCH_PRODUCER_ROLES):
            task, instance, runtime = approved_task()
            produced = build_profiles(instance['config'], host=entry().ports.host)
            profiles = {p['ai']['tier']: p for p in produced['execution_profiles'].values()
                        if p['role'] == role}
            self.assertEqual(set(profiles), set(tiers))
            instance['execution_profiles'] = {p['id']: p for p in profiles.values()}
            instance['grants']['GR-1']['roles'] = [role]
            for difficulty, importance, floor, mask in product(tiers, tiers, tiers, range(1 << len(tiers))):
                instance['config']['role_tiers'][role] = floor
                task['model_assessment'] = {'difficulty': difficulty, 'importance': importance,
                                            'reason': 'Explicit finite model requirement'}
                allowed = [tier for index, tier in enumerate(tiers) if mask & (1 << index)]
                task['profile_refs'] = [profile_ref(profiles[tier]) for tier in allowed]
                approve_task(task, instance, runtime)
                required = max((difficulty, importance, floor), key=tiers.index)
                for pinned in (None, *tiers):
                    action = {'id': 'AC-finite-profile', 'role': role, 'target': task['id']}
                    if pinned is not None:
                        action['profile_ref'] = profile_ref(profiles[pinned])
                    eligible = (required in allowed if pinned is None else
                                pinned in allowed and tiers.index(pinned) >= tiers.index(required))
                    with self.subTest(role=role, difficulty=difficulty, importance=importance,
                                      floor=floor, allowed=allowed, pinned=pinned):
                        selected = None
                        try:
                            selected = model_policy.work_profile_selection(instance['config'], task, instance, action=action)
                        except ValueError:
                            self.assertFalse(eligible, 'an eligible profile was rejected')
                        self.assertEqual(selected is not None, eligible)
                        if selected is not None:
                            self.assertEqual(selected['profile_ref'], profile_ref(profiles[pinned or required]))
                        ready = planning.task_ready(task, instance, runtime, include_scheduling_waits=False,
                            action=action, evaluation_context={'now': entry().ports.clock.now(), 'host_id': entry().host_id})
                        self.assertEqual(ready['state'], 'ready' if eligible else 'not_ready', ready)
                        checked += 1
        self.assertEqual(checked, len(RESEARCH_PRODUCER_ROLES) * len(tiers) ** 3 * 2 ** len(tiers) * (len(tiers) + 1))

    def test_wire_profile_reference_remains_identical_in_stored_contract(self):
        _, instance, _ = approved_task()
        wire = candidate()
        wire['profile_refs'] = [profile_ref(next(iter(instance['execution_profiles'].values())))]
        Draft202012Validator(contracts.TASK_CANDIDATE).validate(wire)
        # Allocation belongs to the engine, not the wire producer.
        stored = {k: deepcopy(v) for k, v in wire.items() if k != 'revises_task_id'}
        stored.update(id='TK-wire', revision=1)
        task_contracts.validate_task_contract(stored)
        self.assertEqual(stored['profile_refs'], wire['profile_refs'])
        for illegal in ({**wire, 'id': 'TK-wire'}, {**wire, 'revision': 1}):
            self.assertTrue(list(Draft202012Validator(contracts.TASK_CANDIDATE).iter_errors(illegal)))
        with self.assertRaisesRegex(ValueError, "^task/: 'id' is a required property$"):
            task_contracts.validate_task_contract(wire)

    def test_raw_governance_review_is_current_in_raw_and_projected_consumers(self):
        from support.entry import entry
        _entry = entry()
        from do_math.governance import governance_view
        value, instance, runtime = approved_task()
        approve_task(value, instance, runtime)
        review = value['reviews'][-1]
        expected = governance_view(instance)
        self.assertEqual(review['goal_revision'], expected['goal_revision'])
        self.assertEqual(review['policy_revision'], expected['policy_revision'])
        for view in (instance, {**instance, **expected}):
            self.assertTrue(planning.contract_review_current(review, value, view, runtime)['valid'])
            self.assertEqual(planning.task_ready(value, view, runtime, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'ready')
        self.assertNotIn('goal_revision', instance)

    def test_transfer_cannot_complete_original_obligations(self):
        instance, runtime, assessment = transfer_assessment()
        assessment['decision'] = 'completed'
        before = deepcopy((instance, runtime))
        with self.assertRaisesRegex(ValueError, 'completed.*transferred'):
            apply_assessment(instance, runtime, assessment)
        self.assertEqual((instance, runtime), before)
        with self.assertRaisesRegex(ValueError, 'completed.*transferred'):
            planning.validate_plan_submission({'dispositions': [], 'task_assessments': [assessment]}, runtime['tasks'], [])

    def test_review_ignores_flat_projection_and_rejects_real_governance_changes(self):
        from support.entry import entry
        _entry = entry()
        from do_math import governance
        value, instance, runtime = approved_task()
        review = deepcopy(value['reviews'][-1])
        stale_projection = {**instance, 'goal_revision': 999, 'policy_revision': 'fake'}
        self.assertTrue(planning.contract_review_current(review, value, stale_projection, runtime)['valid'])
        before = planning.review_basis_key(value, instance, runtime)
        policy = {'id': 'POL-new', 'kind': 'policy', 'revision': 1, 'supersedes': [],
                  'content': {'rule_id': 'rule-new', 'scope': ['P'], 'text': 'Require an explicit domain',
                              'reason_refs': ['D'], 'audit_refs': []}}
        updated, runtime, _ = governance.apply_decision(instance, runtime, {'kind': 'policy', 'record': policy}, source_ref='S', clock=_entry.ports.clock)
        self.assertFalse(planning.contract_review_current(review, value, updated, runtime)['valid'])
        self.assertNotEqual(planning.review_basis_key(value, updated, runtime), before)

    def test_actual_charter_replacement_invalidates_review_without_top_level_fields(self):
        from support.entry import entry
        _entry = entry()
        from do_math import governance
        from support.state_builders import charter
        value, instance, runtime = approved_task()
        review = deepcopy(value['reviews'][-1])
        replacement = charter('CH2', 'Prove the stronger Q')
        replacement.update(revision=2, supersedes=['CH1'])
        updated, runtime, _ = governance.apply_decision(instance, runtime, {'kind': 'charter', 'record': replacement},
                                                        source_ref='S', clock=_entry.ports.clock)
        self.assertNotIn('goal_revision', updated)
        self.assertFalse(planning.contract_review_current(review, value, updated, runtime)['valid'])
        self.assertEqual(planning.task_ready(value, updated, runtime, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'not_ready')

    def test_closed_transfer_never_satisfies_a_completion_dependency(self):
        from support.entry import entry
        _entry = entry()
        instance, runtime, assessment = transfer_assessment()
        instance, runtime = apply_assessment(instance, runtime, assessment)
        source = runtime['tasks']['TK-1']
        consumer = deepcopy(runtime['tasks']['TK-2'])
        consumer.update(id='TK-consumer', dependencies=[source['id']], results=[], reviews=[])
        runtime['tasks'][consumer['id']] = consumer
        instance['grants']['GR-1']['task_ids'].append(consumer['id'])
        approve_task(consumer, instance, runtime)
        state = planning.task_ready(consumer, instance, runtime, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})
        self.assertEqual(state['state'], 'not_ready')
        self.assertIn('blocked dependencies', state['errors'][0])

    def test_terminal_disposition_consistency_is_checked_by_shared_validator(self):
        from do_math.task_scope import assessment_current
        instance, runtime, assessment = transfer_assessment()
        task = runtime['tasks']['TK-1']
        opened = deepcopy(assessment)
        opened['item_dispositions'][0]['kind'] = 'open'
        with self.assertRaisesRegex(ValueError, 'open obligations'):
            task_contracts.validate_item_dispositions(task, opened)
        _, runtime = apply_assessment(instance, runtime, assessment)
        runtime['tasks']['TK-1']['status'] = 'completed'
        self.assertFalse(assessment_current(runtime['tasks']['TK-1'], instance, runtime))

    def test_profile_ref_shape_and_exact_resolution_are_both_required(self):
        from support.entry import entry
        _entry = entry()
        value, instance, runtime = approved_task()
        for replacement, reason in (
                (value['profile_refs'][0]['id'], "^task/profile_refs/0: '[^']+' is not of type 'object'$"),
                ({**value['profile_refs'][0], 'revision': True}, "^task/profile_refs/0/revision: True is not of type 'integer'$"),
                ({**value['profile_refs'][0], 'sha256': 'invalid'},
                 r"^task/profile_refs/0/sha256: 'invalid' does not match '\^\[0-9a-f\]\{64\}\$'$")):
            bad = deepcopy(value)
            bad['profile_refs'] = [replacement]
            with self.assertRaisesRegex(ValueError, reason):
                task_contracts.validate_task_contract(bad)
        bad = deepcopy(value)
        bad['profile_refs'] *= 2
        with self.assertRaisesRegex(ValueError, '^task/profile_refs: .* has non-unique elements$'):
            task_contracts.validate_task_contract(bad)
        for field, invalid in (('revision', 2), ('sha256', 'b' * 64)):
            stale = deepcopy(value)
            stale['profile_refs'][0][field] = invalid
            runtime['tasks'][stale['id']] = stale
            approve_task(stale, instance, runtime)
            result = planning.task_ready(stale, instance, runtime, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})
            self.assertEqual((result['state'], result['errors']), ('not_ready', ['no current approved execution profile']))

    def test_repetition_basis_changes_with_actual_policy_not_flat_projection(self):
        from support.entry import entry
        _entry = entry()
        from do_math import governance, revisions
        _, instance, runtime = approved_task()
        action = {'role': 'research_preparation'}
        revisions.bind_repetition_bases(instance, runtime, action)
        policy = {'id': 'POL-new', 'kind': 'policy', 'revision': 1, 'supersedes': [],
                  'content': {'rule_id': 'new', 'scope': ['P'], 'text': 'A new requirement', 'reason_refs': ['D'],
                              'audit_refs': []}}
        changed, runtime, _ = governance.apply_decision(instance, runtime, {'kind': 'policy', 'record': policy}, source_ref='S', clock=_entry.ports.clock)
        next_action = {'role': 'research_preparation'}
        revisions.bind_repetition_bases(changed, runtime, next_action)
        self.assertNotEqual(action['repetition_bases'], next_action['repetition_bases'])

    def test_common_reference_closure_does_not_split_grant_reuse_string(self):
        value, instance, runtime = approved_task()
        basis = planning.capture_task_basis(value, instance, runtime)
        self.assertNotIn('r', basis['common'])
        self.assertIn(value['profile_refs'][0]['id'], planning.action_read_ids({'target': value['id']}, instance, runtime))


class TransferredContractRevisionTests(unittest.TestCase):
    def test_replacement_preserves_inherited_obligation_and_machine_provenance(self):
        from do_math.contracts import task_candidate_record
        from do_math.task_scope import validate_withdrawal_scope
        instance, runtime, assessment = transfer_assessment()
        instance, runtime = apply_assessment(instance, runtime, assessment)
        recipient = runtime['tasks']['TK-2']
        proposal = candidate('Revised recipient', revises=recipient['id'])
        proposal['completion_obligations'] = deepcopy(recipient['completion_obligations'])
        proposal['completion_obligations'][0]['claim'] = 'Refine the independently authored obligation'
        revised = task_candidate_record(proposal, task_id=recipient['id'], previous=recipient)
        self.assertEqual(revised['transferred_obligations'], recipient['transferred_obligations'])
        self.assertIsNot(revised['transferred_obligations'], recipient['transferred_obligations'])
        self.assertEqual(revised['completion_obligations'][-1], recipient['completion_obligations'][-1])
        with self.assertRaisesRegex(ValueError, 'protected obligations'):
            validate_withdrawal_scope({**revised, 'status': 'planned'}, revised)
        for field in ('remove', 'id', 'claim', 'judges', 'evidence_required'):
            with self.subTest(field=field):
                bad = deepcopy(proposal)
                if field == 'remove':
                    bad['completion_obligations'].pop()
                else:
                    bad['completion_obligations'][-1][field] = (
                        ['changed'] if field in {'judges', 'evidence_required'} else 'changed')
                before = deepcopy(recipient)
                with self.assertRaisesRegex(ValueError, 'preserve transferred obligations'):
                    task_candidate_record(bad, task_id=recipient['id'], previous=recipient)
                self.assertEqual(recipient, before)


class TaskContractsTest(unittest.TestCase):
    def test_missing_returned_assessment_identifies_the_missing_task(self):
        _, runtime, assessment = transfer_assessment()
        self.assertIsNone(planning.validate_plan_submission(
            {'dispositions': [], 'task_assessments': [assessment]}, runtime['tasks'], []))
        unknown = {**assessment, 'task_id': 'TK-outside'}
        for rows, missing, unexpected, duplicate in (
                ([], ['TK-1'], [], []),
                ([assessment, unknown], [], ['TK-outside'], []),
                ([assessment, assessment], [], [], ['TK-1']),
                ([unknown, unknown], ['TK-1'], ['TK-outside'], ['TK-outside'])):
            reason = ('plan must assess every returned task exactly once: '
                      f'missing={missing}; unexpected={unexpected}; duplicate={duplicate}')
            with self.subTest(missing=missing, unexpected=unexpected, duplicate=duplicate), \
                    self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                planning.validate_plan_submission({'dispositions': [], 'task_assessments': rows}, runtime['tasks'], [])

    def test_contract_has_stable_obligations_and_completion_requires_every_disposition(self):
        value = task_contract()
        task_contracts.validate_task_contract(value)
        assessment = {'item_dispositions': [
            {'obligation_id': 'OB-1', 'kind': 'fulfilled', 'evidence_refs': ['EV-1']},
            {'obligation_id': 'OB-2', 'kind': 'transferred', 'evidence_refs': [], 'target_task_id': 'TK-2',
             'target_obligation_id': 'OB-9', 'authority_ref': 'GR-1'},
        ]}
        task_contracts.validate_item_dispositions(value, assessment)
        self.assertEqual(task_contracts.remaining_obligations(value, assessment), [])

    def test_unresolved_inspection_is_not_a_false_or_open_disposition(self):
        value = task_contract()
        assessment = {'unresolved': [{'obligation_id': 'OB-1', 'missing_inputs': ['EV-1'], 'next_owner': 'AC-recover'}],
                      'item_dispositions': [{'obligation_id': 'OB-2', 'kind': 'fulfilled', 'evidence_refs': []}]}
        with self.assertRaisesRegex(ValueError, 'unresolved'):
            task_contracts.validate_item_dispositions(value, assessment, require_complete=True)
        self.assertEqual(task_contracts.remaining_obligations(value, assessment), ['OB-1'])

    def test_waiver_and_transfer_need_authoritative_links(self):
        # Each input pins the check that rejects it: a waiver without authority, a transfer row
        # without evidence_refs (rejected before its target check), and a single waived row that
        # leaves OB-2 undisposed (the pure validator does not resolve authority_ref; assessment
        # application does, in unit.test_planning_assessments).
        value = task_contract()
        for row, reason in (
                ({'obligation_id': 'OB-1', 'kind': 'waived', 'evidence_refs': ['EV-1']},
                 '^waived obligation needs authority_ref$'),
                ({'obligation_id': 'OB-1', 'kind': 'transferred', 'target_task_id': 'TK-2', 'authority_ref': 'GR-1'},
                 '^item disposition requires evidence_refs$')):
            with self.subTest(row=row), self.assertRaisesRegex(ValueError, reason):
                task_contracts.validate_item_dispositions(value, {'item_dispositions': [row]})
        with self.assertRaisesRegex(ValueError, '^every obligation requires a disposition or unresolved inspection$'):
            task_contracts.validate_item_dispositions(value, {'item_dispositions': [{
                'obligation_id': 'OB-1', 'kind': 'waived', 'evidence_refs': ['EV-1'], 'authority_ref': 'GR-unrelated',
            }]})

    def test_readiness_is_derived_not_a_saved_task_state(self):
        from support.entry import entry
        _entry = entry()
        value, instance, runtime = approved_task()
        before = deepcopy(runtime)
        result = planning.task_ready(value, instance, runtime, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})
        self.assertEqual(result['state'], 'ready')
        self.assertEqual(runtime, before)

    def test_repetition_lineages_keep_ai_repair_distinct_from_user_authority(self):
        runtime = {'history': [{'kind': 'task_repetition', 'lineage': name, 'lineage_id': 'TK-1',
                                'outcome': 'revised', 'owner': 'ai'} for name in task_contracts.REPEAT_LINEAGES]}
        lineages = task_contracts.repetition_lineages(runtime, 'TK-1')
        self.assertEqual(set(lineages), {'import_rework', 'selection_failure', 'exhaustion_empty', 'proposal_version',
                                         'contract_revision'})
        self.assertTrue(all(row['owner'] == 'ai' for row in lineages.values()))
        self.assertTrue(all(row['count'] == 1 for row in lineages.values()))

    def test_planning_routes_tasks_to_derived_readiness_and_item_plan_checks(self):
        from support.entry import entry
        _entry = entry()
        value, instance, runtime = approved_task()
        self.assertEqual(planning.task_ready(value, instance, runtime, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'ready')
        self.assertEqual(planning.ready_task_ids(runtime, instance, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id}), ['TK-1'])
        plan = {'dispositions': [task_disposition('TK-1', 'not_selected')], 'task_assessments': []}
        planning.validate_plan_submission(plan, {'TK-1': value}, ['TK-1'])
        invalid = {'dispositions': [task_disposition('TK-absent'), task_disposition('TK-absent')], 'task_assessments': []}
        with self.assertRaises(ValueError) as rejected:
            planning.validate_plan_submission(invalid, {'TK-1': value}, ['TK-1'])
        for detail in ("missing=['TK-1']", "unexpected=['TK-absent']", "duplicate=['TK-absent']"):
            self.assertIn(detail, str(rejected.exception))

    def test_family_qualified_condition_does_not_read_a_same_id_from_another_family(self):
        instance = {'knowledge': {'X': {'id': 'X', 'status': 'verified'}}}
        runtime = {'tasks': {'X': {'id': 'X', 'status': 'completed'}}}
        result = planning.evaluate_condition({'op': 'record_lifecycle_is', 'space': 'research', 'family': 'knowledge',
                                              'record_id': 'X', 'value': 'active'}, instance, runtime)
        self.assertEqual(result['state'], 'evaluation_error')
        self.assertIn('duplicate', result['errors'][0])

    def test_decision_and_artifact_conditions_preserve_effect_and_validity(self):
        _, instance, runtime = approved_task()
        instance['decisions'] = {'DC-1': {'id': 'DC-1', 'actor': 'user', 'source_ref': 'SO-1',
                                          'source_sha256': 'a' * 64, 'change': {'value': 'continue'}}}
        decision = {'op': 'decision_value_is', 'decision_id': 'DC-1', 'value': 'continue'}
        self.assertEqual(planning.evaluate_condition(decision, instance, {})['state'], 'ready')
        instance['decisions']['DC-1']['source_sha256'] = 'b' * 64
        self.assertEqual(planning.evaluate_condition(decision, instance, runtime)['state'], 'not_ready')
        data = b'valid proof output'
        condition = {'op': 'artifact_valid', 'artifact_ref': {'snapshot': 'SN-1', 'path': 'runtime/artifacts/BA-1/proof.txt',
                                                              'sha256': hashlib.sha256(data).hexdigest()}}
        context = {'snapshot': 'SN-1', 'read_artifact': lambda p, s: data, 'validate_artifact': lambda r, b: b == data}
        self.assertEqual(planning.evaluate_condition(condition, instance, runtime, evaluation_context=context)['state'], 'ready')
        context['snapshot'] = 'SN-later-evaluation'
        self.assertEqual(planning.evaluate_condition(condition, instance, runtime, evaluation_context=context)['state'], 'ready')
        context['read_artifact'] = lambda p, s: b'corrupt'
        self.assertEqual(planning.evaluate_condition(condition, instance, runtime, evaluation_context=context)['state'],
                         'evaluation_error')

    def test_prose_requirement_does_not_require_a_future_id_equal_to_the_description(self):
        wire = candidate()
        wire['completion_obligations'][0]['evidence_requirements'] = ['Code and exact output for the full stated range']
        task = contracts.task_candidate_record(wire, task_id='TK-new')
        # The engine stores the contract without the wire-only revision pointer.
        del task['revises_task_id']
        assessment = {'decision': 'completed', 'item_dispositions': [
            {'obligation_id': 'OB-argument', 'kind': 'fulfilled', 'evidence_refs': ['EX-newly-created']}], 'unresolved': []}
        task_contracts.validate_item_dispositions(task, assessment)
        task['completion_obligations'][0]['evidence_required'] = ['KN-required-existing']
        with self.assertRaisesRegex(ValueError, 'required evidence'):
            task_contracts.validate_item_dispositions(task, assessment)
        assessment['item_dispositions'][0]['evidence_refs'].append('KN-required-existing')
        task_contracts.validate_item_dispositions(task, assessment)
        fields = list(submission._explicit_reference_fields(wire))
        self.assertFalse(any('evidence_requirements' in path for path, _ in fields))


class TaskReadinessTests(unittest.TestCase):
    def test_explicit_query_time_controls_grant_window_and_exhaustion(self):
        t, i, r = approved_task()
        start, end = '2041-03-02T12:00:00Z', '2041-03-02T12:01:00Z'
        i['grants']['GR-1'].update(valid_from=start, expires_at=end)
        approve_task(t, i, r)
        context = {'now': end, 'lean_available': False}
        before = deepcopy((t, i, r, context))
        for at, state in (('2041-03-02T11:59:59Z', 'not_ready'),
                          (start, 'ready'), (end, 'not_ready')):
            with self.subTest(at=at):
                self.assertEqual(planning.task_ready(t, i, r, evaluation_context={'now': at})['state'], state)
                exhausted = planning.exhaustion_state(i, r, now=at, evaluation_context=context)
                self.assertEqual('ready_contracts' in exhausted['reasons'], state == 'ready')
        self.assertEqual((t, i, r, context), before)

    def test_authority_evaluation_requires_explicit_time(self):
        t, i, r = approved_task()
        for context in (None, {}, {'now': None}, {'now': ''}):
            with self.subTest(context=context), self.assertRaisesRegex(
                    ValueError, '^time must be a nonempty ISO timestamp string$'):
                planning.task_ready(t, i, r, evaluation_context=context)

    def test_review_cannot_be_replaced_by_an_unsubstantiated_summary(self):
        from support.entry import entry
        _entry = entry()
        value, i, r = approved_task()
        value['reviews'][0]['item_reviews'] = []
        self.assertNotEqual(planning.task_ready(value, i, r, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'ready')

    def test_each_actual_premise_change_blocks_an_otherwise_ready_task(self):
        from support.entry import entry
        _entry = entry()
        mutations = [lambda t, i, r: t['reviews'][0].update(inputs_current=False),
                     lambda t, i, r: i['sources'].clear(),
                     lambda t, i, r: i['sources'][0].update(sha256='b' * 64),
                     lambda t, i, r: i['grants']['GR-1'].update(status='revoked'),
                     lambda t, i, r: i['execution_profiles'].clear(),
                     lambda t, i, r: t.update(revision_requested={'revision': 1, 'source': 'EX-repair'}),
                     lambda t, i, r: r['question_links'].append({'id': 'Q-1', 'owner': 'user', 'status': 'open', 'blocks': True,
                                                                 'target_ids': ['TK-1'], 'unresolved_target_ids': ['TK-1']}),
                     lambda t, i, r: r['queue'].append({'id': 'AC-revise', 'role': 'research_preparation',
                                                        'revision_targets': {'TK-1': {}}})]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                t, i, r = approved_task()
                self.assertEqual(planning.task_ready(t, i, r, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'ready')
                mutate(t, i, r)
                self.assertEqual(planning.task_ready(t, i, r, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'not_ready')

    def test_missing_input_cannot_be_approved_into_existence(self):
        from support.entry import entry
        _entry = entry()
        t, i, r = approved_task()
        t['inputs'].append('SO-absent')
        approve_task(t, i, r)
        self.assertIn('missing inputs', planning.task_ready(t, i, r, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['errors'][0])

    def test_profile_edition_and_fixed_trust_must_still_apply(self):
        from support.entry import entry
        _entry = entry()
        t, i, r = approved_task()
        t.update(work_class='formal', trust_environment_id='TE-1')
        i.update(active_trust_environment='TE-1', trust_environments={'TE-1': {'id': 'TE-1', 'status': 'active'}})
        approve_task(t, i, r)
        action = {'id': 'AC-work', 'role': 'research_work', 'target': t['id'],
                  'profile_ref': profile_ref(next(iter(i['execution_profiles'].values())))}
        self.assertEqual(planning.task_ready(t, i, r, action=action, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'ready')
        action['profile_ref']['revision'] += 1
        self.assertEqual(planning.task_ready(t, i, r, action=action, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'not_ready')
        i['active_trust_environment'] = 'TE-2'
        self.assertEqual(planning.task_ready(t, i, r, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'not_ready')

    def test_split_knowledge_evidence_is_part_of_review_currentness(self):
        from support.entry import entry
        _entry = entry()
        t, i, r = approved_task()
        i['knowledge'] = {'KN-1': {'id': 'KN-1', 'exposition_id': 'XP-1', 'formal_result_id': 'FR-1'}}
        i['expositions'] = {'XP-1': {'id': 'XP-1', 'items': ['old']}}
        i['formal_results'] = {'FR-1': {'id': 'FR-1', 'verification': {'status': 'verified'}}}
        t['inputs'].append('KN-1')
        approve_task(t, i, r)
        self.assertEqual(planning.task_ready(t, i, r, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'ready')
        i['expositions']['XP-1']['items'] = ['changed']
        self.assertEqual(planning.task_ready(t, i, r, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'not_ready')

    def test_external_wait_and_formal_work_are_not_research_exhaustion(self):
        from support.entry import entry
        _entry = entry()
        t, i, r = approved_task()
        t['waiting'] = {'kind': 'external_event', 'next_owner': 'external_action'}
        t['status'] = 'waiting'
        self.assertFalse(planning.exhaustion_state(i, r, now=_entry.ports.clock.now())['exhausted'])
        r['tasks'] = {}
        r['queue'] = [{'id': 'AC-formal', 'role': 'formal_check', 'target': 'FR-1'}]
        self.assertFalse(planning.exhaustion_state(i, r, now=_entry.ports.clock.now())['exhausted'])

    def test_empty_queue_is_not_exhaustion_when_work_is_running(self):
        from support.entry import entry
        _entry = entry()
        runtime = {'status': 'active', 'tasks': {}, 'queue': [], 'executions': {
            'EX-live': {'id': 'EX-live', 'role': 'research_work', 'status': 'running', 'action': {'target': 'TK'}}}}
        self.assertFalse(planning.exhaustion_state({'goal_status': 'unresolved'}, runtime, now=_entry.ports.clock.now())['exhausted'])

    def test_stale_approval_and_absent_input(self):
        from support.entry import entry
        _entry = entry()
        value = task_contract()
        value['inputs'] = ['missing-input']
        value['reviews'] = [{'revision': 1, 'decision': 'approved', 'inputs_current': False}]
        result = planning.task_ready(value, {}, {'tasks': {value['id']: value}}, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})
        self.assertNotEqual(result['state'], 'ready')

    def test_missing_returned_work_cannot_be_silently_omitted(self):
        value = task_contract()
        value.update(status='waiting', results=[{'id': 'EV-return'}])
        reason = f"plan must assess every returned task exactly once: missing={[value['id']]}; unexpected=[]; duplicate=[]"
        with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
            planning.validate_plan_submission({'dispositions': [], 'task_assessments': []}, {value['id']: value}, [])

    def test_open_obligation_does_not_require_evidence_of_fulfilment(self):
        value = task_contract()
        assessment = {'item_dispositions': [{'obligation_id': 'OB-1', 'kind': 'open', 'evidence_refs': []},
                                            {'obligation_id': 'OB-2', 'kind': 'open', 'evidence_refs': []}]}
        # The legacy test passed by not raising; the validator's result and the open obligations are now asserted.
        self.assertIsNone(task_contracts.validate_item_dispositions(value, assessment))
        self.assertEqual(task_contracts.remaining_obligations(value, assessment), ['OB-1', 'OB-2'])

    def test_new_contract_fields_are_in_approval_digest(self):
        value = task_contract()
        changed = deepcopy(value)
        changed['completion_obligations'][0]['claim'] = 'A different requirement'
        self.assertNotEqual(planning.contract_hash(value), planning.contract_hash(changed))

    def test_artifact_metadata_is_not_evidence_of_readable_bytes(self):
        result = planning.evaluate_condition({'op': 'artifact_valid', 'artifact_ref': 'AR-1'},
                                             {'artifacts': {'AR-1': {'id': 'AR-1', 'valid': True, 'sha256': 'a' * 64}}}, {})
        self.assertEqual(result['state'], 'evaluation_error')


class TaskDependencyTests(unittest.TestCase):
    def test_primary_and_extension_dependencies_are_preserved(self):
        candidate_record = {'dependencies': ['TK-existing']}
        self.assertEqual(task_contracts.prepared_dependencies(candidate_record, {'observation_rules': []}), ['TK-existing'])
        self.assertEqual(task_contracts.prepared_dependencies(candidate_record,
                                                              {'dependencies': ['new task', 'TK-existing']},
                                                              {'new task': 'TK-new'}), ['TK-existing', 'TK-new'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
