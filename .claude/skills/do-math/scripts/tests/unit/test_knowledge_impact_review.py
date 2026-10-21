"""Knowledge-impact review (``integration``, layer 2): the designated review of a held change, its sealed evidence
and the single application of the reviewed bundle.

Every test starts from ``review_fixtures.ImpactReviewHarness``'s state (its
``setUp`` builds it; its ``seal_review_fixture`` is not used): research work
``EX-producer`` revises observations ``A`` and ``C`` and declares ``B`` in the
impact of its bundle ``IN-held``. A review is sealed by
``support.knowledge_impact.seal_review`` (the product's central capture on a
real engine) and published to a ``GitStateStore`` or a ``ResearchRepository``
on the Git port's fake; the review consumer reads those bytes back.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import jsonschema

from do_math import contracts, integration, knowledge_io, submission
from do_math.canonical import canonical_json, exact_content_hash
from do_math.knowledge import content_hash
from support.record_builders import research_work_context
from support.knowledge_impact import ImpactCase
from support.knowledge_impact import fixture_store, seal_review
from support.storage_records import record_store


class ImpactReviewCase(ImpactCase):
    def seal(self, execution, output, fixed, workspace):
        return seal_review(execution, output, fixed, workspace)


class ImpactBundleTests(ImpactReviewCase):
    def test_duplicate_historical_assignments_do_not_hide_the_new_impact_request(self):
        original = self._request()
        # Two retries can read the same assignment. A later ordinary consumer
        # changes its closure, so neither preserved review is a fixed point.
        for identifier in ('EX-review-a', 'EX-review-b'):
            self.runtime['executions'][identifier] = {'id': identifier, 'role': 'maintenance',
                'status': 'ended', 'action': {'role': 'maintenance', 'stage': 'impact_review',
                    'input_basis': {'impact_review': deepcopy(original)}}}
        self.assertEqual(self._request(), original)
        self.runtime['executions']['EX-new-consumer'] = {'id': 'EX-new-consumer',
            'role': 'research_work', 'status': 'ended',
            'output': {'used_sources': [self.ids[0]], 'report': 'Read the changed premise'}}
        before = deepcopy((self.instance, self.runtime))
        current = self._request()
        self.assertNotEqual(current, original)
        self.assertIn('EX-new-consumer', current['plans']['bundle']['computed_impact'])
        self.assertEqual({key: current[key] for key in original if key != 'plans'},
                         {key: original[key] for key in original if key != 'plans'})
        self.assertEqual((self.instance, self.runtime), before)

    def test_impact_requires_original_execution_and_exact_change_coordinates(self):
        for fault, reason in (
                ('execution', 'impact request needs its original execution and fixed input snapshot'),
                ('snapshot', 'impact request needs its original execution and fixed input snapshot'),
                ('coordinates', 'impact changes need distinct targets and exact member coordinates'),
                ('duplicate', 'impact changes need distinct targets and exact member coordinates'),
                ('root', 'bundle declares impact without an existing mutation root')):
            bundle = deepcopy(self.bundle)
            producer, snapshot = 'EX-producer', 'fixed-input'
            if fault == 'execution': producer = 'EX-missing'
            elif fault == 'snapshot': snapshot = None
            elif fault == 'coordinates': bundle['members'].pop()
            elif fault == 'duplicate': bundle['extensions']['knowledge_changes'][1]['id'] = self.ids[0]
            else:
                bundle['extensions'] = {}
                bundle['members'] = ['output']
                bundle['previous_hashes'] = {}
            before = deepcopy((self.instance, self.runtime, bundle))
            with self.subTest(fault=fault), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                integration.bundle_impact_request(self.instance, self.runtime, bundle,
                    producer_execution_id=producer, input_snapshot=snapshot)
            self.assertEqual((self.instance, self.runtime, bundle), before)

    def test_approved_impact_must_cover_both_computed_and_declared_records(self):
        request = self._request()
        output = self.review_output(request)
        output['impact_review']['plan_decisions'][0]['affected_ids'] = []
        with self.assertRaisesRegex(ValueError, '^approved impact scope must cover the computed and declared union$'):
            integration.validate_impact_review_response(request, output)
        output['impact_review']['plan_decisions'][0]['decision'] = 'unresolved'
        rows = integration.validate_impact_review_response(request, output)
        self.assertEqual(rows[output['impact_review']['plan_decisions'][0]['scope']]['decision'], 'unresolved')

    def test_designated_review_requires_both_sealed_artifact_coordinates(self):
        request = self._request()
        output = self.review_output(request)
        action = {'id': 'AC-review', 'role': 'maintenance', 'stage': 'impact_review',
                  'input_basis': {'impact_review': request}}
        self.runtime['executions']['EX-review'] = {'id': 'EX-review', 'role': 'maintenance',
            'actor_kind': 'ai', 'status': 'ended', 'outcome': 'output_accepted', 'action': action}
        before = deepcopy(self.runtime)
        with self.assertRaisesRegex(ValueError, '^impact review requires sealed input and output artifacts$'):
            integration.require_bundle_impact_review(self.instance, self.runtime, self.bundle,
                producer_execution_id='EX-producer', input_snapshot='fixed-input', review_execution_id='EX-review')
        self.assertEqual(self.runtime, before)

    def test_previous_hashes_cover_the_exact_current_mutation_targets(self):
        original = deepcopy(self.bundle)
        before = deepcopy((self.instance, self.runtime))
        self.assertTrue(self._request()['plans'])
        for target in original['previous_hashes']:
            for fault in ('missing', 'changed'):
                self.bundle = deepcopy(original)
                if fault == 'missing':
                    del self.bundle['previous_hashes'][target]
                    reason = '^bundle previous hashes missing for mutation targets$'
                    with self.subTest(target=target, fault=fault), self.assertRaisesRegex(ValueError, reason):
                        self._request()
                else:
                    from do_math.input_basis import CurrentnessChanged
                    record = self.instance['knowledge'][target]
                    previous = deepcopy(record)
                    record['summary'] = 'A live change after the fixed declaration'
                    with self.subTest(target=target, fault=fault), self.assertRaises(CurrentnessChanged) as caught:
                        self._request()
                    self.assertEqual(caught.exception.changes, [{'id': target, 'field': 'content_sha256',
                        'before': original['previous_hashes'][target], 'after': content_hash(record)}])
                    record.clear()
                    record.update(previous)
                self.assertEqual((self.instance, self.runtime), before)
        self.bundle = original

    def test_impact_followup_requires_affected_records_and_coalesces_the_same_request(self):
        from do_math import knowledge
        from support.entry import entry
        first, dependent, _ = self.ids
        for affected in (set(), {dependent}):
            with self.subTest(affected=sorted(affected)):
                runtime = deepcopy(self.runtime)
                runtime['queue'] = []
                before = deepcopy((self.instance, runtime))
                instance, changed = knowledge._apply_impact_effects(self.instance, runtime, affected, [first],
                    reason='Reviewed knowledge impact', impact_digest='checked-impact', clock=entry().ports.clock)
                self.assertEqual((self.instance, runtime), before)
                plans = [a for a in changed['queue'] if a['role'] == 'research_plan']
                self.assertEqual(len(plans), int(bool(affected)))
                if plans:
                    self.assertEqual(plans[0]['affected_ids'], [dependent])
                _, repeated = knowledge._apply_impact_effects(instance, changed, affected, [first],
                    reason='Reviewed knowledge impact', impact_digest='checked-impact', clock=entry().ports.clock)
                self.assertEqual(repeated['queue'], changed['queue'])

    def _request(self):
        return integration.bundle_impact_request(self.instance, self.runtime, self.bundle,
                                                 producer_execution_id='EX-producer', input_snapshot='fixed-input')

    def _seal_review(self, request, *, fixed_changes=None):
        """Seal an approving review of ``request`` through the central capture and publish it.

        Returns the review consumers' keyword arguments for that snapshot.
        """
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        output = self.review_output(request)
        action = {'id': 'AC-review', 'role': 'maintenance', 'stage': 'impact_review',
                  'input_basis': {'impact_review': request}}
        fixed = {'action': action, 'execution_id': 'EX-review', **(fixed_changes or {})}
        review_bundle = next(integration.split_bundles(output, {}, fixed))
        self.runtime['executions']['EX-review'] = {'id': 'EX-review', 'role': 'maintenance', 'actor_kind': 'ai',
            'status': 'running', 'action': action, 'input_bundle': 'BA-review-input'}
        self.runtime['integrations'] = {'IN-review': {'id': 'IN-review', 'execution_id': 'EX-review',
            'payload_sha256': review_bundle['payload_sha256'],
            'response_sha256': exact_content_hash(integration.member_values(output, {}, fixed)['output'])}}
        workspace = root / 'review-workspace'
        workspace.mkdir()
        artifacts = self.seal(self.runtime['executions']['EX-review'], output, fixed, workspace)
        store = fixture_store(root / 'repository')
        head = store.publish(None, {'research/fixture.json': b'{}',
            'runtime/artifacts/BA-review-input/input/submission/context.json': canonical_json(fixed),
            **artifacts}).head
        return {'producer_execution_id': 'EX-producer', 'input_snapshot': 'fixed-input',
                'review_execution_id': 'EX-review', 'snapshot': head,
                'read_artifact': lambda path, snapshot: store.read_bytes(snapshot, path)}

    def test_impact_receiving_execution_must_match_the_sealed_designated_input(self):
        request = self._request()
        fixed_action = {'id': 'AC-another-assignment', 'role': 'maintenance', 'stage': 'impact_review',
                        'input_basis': {'impact_review': request}}
        args = self._seal_review(request, fixed_changes={'action': fixed_action})
        before = deepcopy((self.instance, self.runtime))
        with self.assertRaisesRegex(ValueError, '^impact review input is not the sealed designated assignment$'):
            integration.require_bundle_impact_review(self.instance, self.runtime, self.bundle, **args)
        self.assertEqual((self.instance, self.runtime), before)

    def test_impact_review_response_cannot_bundle_an_unrelated_insight(self):
        extensions = {'research_insights': [{'kind': 'observation', 'title': 'Unrelated insight',
                        'statement': 'Independent observation', 'summary': 'Not part of the impact judgment'}]}
        request = self._request()
        output = self.review_output(request)
        output['integration_bundles'][0]['members'].append('activity-extensions.json/research_insights/0')
        fixed = {'execution_id': 'EX-review', 'action': {'id': 'AC-review', 'role': 'maintenance',
            'stage': 'impact_review', 'input_basis': {'impact_review': request}},
            'kind_definitions': knowledge_io.catalog_definitions(self.instance)}
        workspace = Path(self.enterContext(tempfile.TemporaryDirectory()))
        schema = contracts.action_schema(fixed['action'])
        submission.install_tools(workspace, fixed, schema, None, clock=self.clock)
        (workspace / 'activity-extensions.json').write_bytes(canonical_json(extensions))
        sealed = submission.seal_submission(workspace, execution_id='EX-review', context=fixed,
            schema=schema, max_artifact_bytes=1024 * 1024, raw_output=canonical_json(output), clock=self.clock)
        self.assertFalse(sealed['passed'])
        self.assertFalse(sealed['capture_eligible'])
        self.assertEqual([(r['rule_id'], r['path'], r['message']) for r in sealed['check']['issues']],
            [('submission.impact_review', 'activity-extensions.json',
              'a designated impact judgment cannot also author research mutations')])

    def test_coupled_changes_use_the_single_reviewed_s0_plan(self):
        """About 0.25 s, over the 0.2 s unit budget: the review is sealed by the product's central capture on a real engine and published to a repository."""
        from support.entry import entry
        _entry = entry()
        first, dependent, second = self.ids
        self.instance['knowledge'][dependent]['dependencies'] = [first]
        self.instance = knowledge_io.ensure_ontology(self.instance)
        self.runtime['queue'] = []
        self.extensions['knowledge_changes'] = [
            {'id': dependent, 'changes': {'summary': 'Revised dependent'},
             'reason': 'Correct dependent explanation', 'impact_set': []},
            {'id': first, 'changes': {'summary': 'Revised premise'},
             'reason': 'Correct premise explanation', 'impact_set': [dependent]}]
        self.output['integration_bundles'][0]['impact_set'] = [dependent]
        self.output['integration_bundles'][0]['previous_hashes'] = {
            identifier: content_hash(self.instance['knowledge'][identifier]) for identifier in (dependent, first)}
        self.bundle = next(integration.split_bundles(self.output, self.extensions, research_work_context()))
        before_instance = canonical_json(self.instance)
        before_runtime = canonical_json(self.runtime)
        request = self._request()
        args = self._seal_review(request)
        changed, running = integration.apply_reviewed_knowledge_changes(
            self.instance, self.runtime, self.bundle, actor_ref='EX-producer', **args, clock=_entry.ports.clock)
        self.assertEqual(before_instance, canonical_json(self.instance))
        self.assertNotEqual(before_runtime, canonical_json(running))
        self.assertEqual({dependent, first},
                         {row['supersedes'] for row in changed['knowledge'].values() if row.get('supersedes')})
        reassessments = [row for row in running['history'] if row.get('kind') == 'knowledge_reassessment_required']
        self.assertEqual(1, len(reassessments))
        followups = [row for row in running['queue'] if row.get('role') == 'research_plan' and row.get('affected_ids')]
        self.assertEqual(1, len(followups))
        self.assertIn(dependent, followups[0]['affected_ids'])

    def test_bundle_level_reviewed_effect_is_applied_once(self):
        """About 0.5 s, over the 0.2 s unit budget: the review is sealed by the product's central capture on a real engine and published to a repository."""
        from support.entry import entry
        _entry = entry()
        target = self.ids[0]
        task_id = 'TK-external-premise'
        self.runtime['tasks'] = {task_id: {'id': task_id, 'status': 'open', 'assessment': {'current': True, 'basis': []}}}
        self.runtime['queue'] = []
        self.extensions = {'knowledge_changes': [{'id': target, 'changes': {'summary': 'Revised once'},
                                                  'reason': 'Correct explanation', 'impact_set': []}]}
        self.output['integration_bundles'] = [{'integration_id': 'IN-whole-only',
            'members': ['output', 'activity-extensions.json/knowledge_changes/0'], 'impact_set': [task_id],
            'authority_refs': [], 'previous_hashes': {target: content_hash(self.instance['knowledge'][target])}}]
        self.bundle = next(integration.split_bundles(self.output, self.extensions, research_work_context()))
        request = self._request()
        args = self._seal_review(request)
        changed, running = integration.apply_reviewed_knowledge_changes(
            self.instance, self.runtime, self.bundle, actor_ref='EX-producer', **args, clock=_entry.ports.clock)
        self.assertFalse(running['tasks'][task_id]['assessment']['current'])
        self.assertEqual(1, len([row for row in running['history'] if row.get('kind') == 'knowledge_reassessment_required']))

    def test_ordinary_execution_source_dependency_still_propagates(self):
        from do_math import knowledge
        root = self.ids[0]
        self.runtime['executions']['EX-consumer'] = {'id': 'EX-consumer', 'role': 'research_work', 'status': 'ended',
            'output': {'used_sources': [root], 'report': 'Consumed the premise.'}}
        self.runtime['executions']['EX-other-review'] = {'id': 'EX-other-review', 'role': 'maintenance', 'status': 'ended',
            'action': {'role': 'maintenance', 'stage': 'impact_review',
                       'input_basis': {'impact_review': {'integration_id': 'IN-other'}}},
            'output': {'used_sources': [root], 'report': 'Reviewed a different assignment.'}}
        plan = knowledge.plan_impact(self.instance, self.runtime, [root], [])
        self.assertIn('EX-consumer', plan['computed_impact'])
        self.assertIn('EX-other-review', plan['computed_impact'])

    def test_only_an_impact_beyond_the_computed_closure_needs_independent_review(self):
        from do_math import knowledge
        root, unrelated = self.ids[0], self.ids[1]
        self.runtime['executions']['EX-consumer'] = {'id': 'EX-consumer', 'role': 'research_work', 'status': 'ended',
            'output': {'used_sources': [root], 'report': 'Consumed the premise.'}}
        # The machine applies its computed closure, and an approval must cover it,
        # so a declaration that misses part of it changes nothing.
        undeclared = knowledge.plan_impact(self.instance, self.runtime, [root], [])
        self.assertIn('EX-consumer', undeclared['missing_declarations'])
        self.assertFalse(undeclared['requires_independent_review'])
        # Suspending a record the closure does not reach is the producer's own judgment.
        extra = knowledge.plan_impact(self.instance, self.runtime, [root], [unrelated])
        self.assertIn(unrelated, extra['extra_declarations'])
        self.assertTrue(extra['requires_independent_review'])

    def test_explicit_replacement_ids_support_forward_sibling_dependencies(self):
        from support.entry import entry
        _entry = entry()
        first, dependent = self.ids[:2]
        new_first = 'KN-01ARZ3NDEKTSV4RRFFQ69G5FAA'
        new_dependent = 'KN-01ARZ3NDEKTSV4RRFFQ69G5FAB'
        changes = [
            {'id': dependent, 'replacement_id': new_dependent, 'changes': {'dependencies': [new_first]},
             'reason': 'Use the replacement premise', 'impact_set': []},
            {'id': first, 'replacement_id': new_first, 'changes': {'summary': 'Stable replacement premise'},
             'reason': 'Correct the premise', 'impact_set': []}]
        self.extensions = {'knowledge_changes': changes}
        self.output['integration_bundles'] = [{'integration_id': 'IN-explicit-ids',
            'members': ['output', 'activity-extensions.json/knowledge_changes/0', 'activity-extensions.json/knowledge_changes/1'],
            'impact_set': [], 'authority_refs': [],
            'previous_hashes': {identifier: content_hash(self.instance['knowledge'][identifier]) for identifier in (dependent, first)}}]
        self.bundle = next(integration.split_bundles(self.output, self.extensions, research_work_context()))
        before_instance = canonical_json(self.instance)
        before_runtime = canonical_json(self.runtime)
        changed, running = integration.apply_reviewed_knowledge_changes(self.instance, self.runtime, self.bundle,
            actor_ref='EX-producer', producer_execution_id='EX-producer', input_snapshot='fixed-input', clock=_entry.ports.clock)
        self.assertEqual([new_first], changed['knowledge'][new_dependent]['dependencies'])
        self.assertEqual(first, changed['knowledge'][new_first]['supersedes'])
        self.assertEqual(dependent, changed['knowledge'][new_dependent]['supersedes'])
        self.assertEqual(before_instance, canonical_json(self.instance))
        self.assertEqual(before_runtime, canonical_json(self.runtime))
        self.assertNotEqual(before_runtime, canonical_json(running))

    def test_replacement_id_schema_and_global_uniqueness_are_enforced(self):
        from support.entry import entry
        _entry = entry()
        replacement_id = 'KN-01ARZ3NDEKTSV4RRFFQ69G5FAC'
        row = {'id': self.ids[0], 'replacement_id': replacement_id, 'changes': {'summary': 'Revised'},
               'reason': 'Correct the record', 'impact_set': []}
        schema = submission.extension_schema({'role': 'research_work'})
        self.assertEqual([], list(jsonschema.Draft202012Validator(schema).iter_errors({'knowledge_changes': [row]})))
        sibling = {'id': self.ids[1], 'replacement_id': 'KN-01ARZ3NDEKTSV4RRFFQ69G5FAD',
                   'changes': {'dependencies': [replacement_id]}, 'reason': 'Use the explicit sibling', 'impact_set': []}
        producer_output = deepcopy(self.output)
        producer_output['integration_bundles'] = [{'integration_id': 'IN-producer-explicit-ids',
            'members': ['output', 'activity-extensions.json/knowledge_changes/0', 'activity-extensions.json/knowledge_changes/1',
                        'activity-extensions.json/revision_resolutions/0', 'activity-extensions.json/revision_resolutions/1'],
            'impact_set': [], 'authority_refs': [], 'previous_hashes': {
                identifier: content_hash(self.instance['knowledge'][identifier]) for identifier in (self.ids[1], self.ids[0])}}]
        producer_extensions = {'knowledge_changes': [sibling, row], 'revision_resolutions': [
            {'record_id': identifier, 'disposition': 'revised', 'reason': 'Apply the declared revision'}
            for identifier in (self.ids[1], self.ids[0])]}
        producer_action = {**research_work_context()['action'],
                           'revision_targets': {identifier: {} for identifier in (self.ids[1], self.ids[0])}}
        producer_context = {**research_work_context(), 'action': producer_action, 'execution_id': 'EX-producer',
                            'knowledge_catalog': deepcopy(self.fixed_context['knowledge_catalog'])}
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            response_schema = contracts.schema_for('research_work')
            submission.install_tools(workspace, producer_context, response_schema, None, clock=_entry.ports.clock)
            draft = workspace / '.scratch/draft.json'
            draft.parent.mkdir()
            draft.write_bytes(canonical_json(producer_output))
            (workspace / 'activity-extensions.json').write_bytes(canonical_json(producer_extensions))
            producer_check = submission.producer_check(workspace, draft, clock=_entry.ports.clock)
            self.assertTrue(producer_check['passed'], producer_check['issues'])

        def bundle_for(rows):
            extensions = {'knowledge_changes': rows}
            self.output['integration_bundles'] = [{'integration_id': 'IN-id-rejection',
                'members': ['output'] + [f'activity-extensions.json/knowledge_changes/{index}' for index in range(len(rows))],
                'impact_set': [], 'authority_refs': [],
                'previous_hashes': {entry['id']: content_hash(self.instance['knowledge'][entry['id']]) for entry in rows}}]
            return next(integration.split_bundles(self.output, extensions, research_work_context()))

        original_instance = canonical_json(self.instance)
        original_runtime = canonical_json(self.runtime)
        duplicate = [row, {**row, 'id': self.ids[1], 'changes': {'summary': 'Also revised'}}]
        # import_candidate rejects the second use of one replacement ID.
        with self.assertRaisesRegex(ValueError, 'already exists'):
            integration.apply_reviewed_knowledge_changes(self.instance, self.runtime, bundle_for(duplicate),
                actor_ref='EX-producer', producer_execution_id='EX-producer', input_snapshot='fixed-input', clock=_entry.ports.clock)
        reused = [{**row, 'replacement_id': self.ids[2]}]
        with self.assertRaisesRegex(ValueError, 'already exists'):
            integration.apply_reviewed_knowledge_changes(self.instance, self.runtime, bundle_for(reused),
                actor_ref='EX-producer', producer_execution_id='EX-producer', input_snapshot='fixed-input', clock=_entry.ports.clock)
        self.assertEqual(original_instance, canonical_json(self.instance))
        self.assertEqual(original_runtime, canonical_json(self.runtime))


class ImpactReviewTests(ImpactReviewCase):
    def test_request_cannot_relabel_the_original_producer_snapshot(self):
        with self.assertRaisesRegex(ValueError, '^impact request snapshot differs from its original producer input$'):
            self.api.bundle_impact_request(self.instance, self.runtime, self.bundle,
                producer_execution_id='EX-producer', input_snapshot='other-input')

    def test_designated_review_has_producible_closed_schema_and_exact_scope(self):
        """About 0.25 s, over the 0.2 s unit budget: the installed producer check runs twice on a real workspace."""
        from support.entry import entry
        _entry = entry()
        request = self.request()
        action = {'role': 'maintenance', 'stage': 'impact_review', 'input_basis': {'impact_review': request}}
        output = self.review_output(request)
        schema = contracts.action_schema(action)
        self.assertEqual([], list(jsonschema.Draft202012Validator(schema).iter_errors(output)))
        self.api.validate_impact_review_response(request, output)
        self.assertEqual(3, len(request['plans']))
        self.assertNotEqual(request['plans']['bundle']['digest'],
                            request['plans']['activity-extensions.json/knowledge_changes/0']['digest'])
        altered = deepcopy(output)
        altered['impact_review']['plan_decisions'].pop()
        with self.assertRaisesRegex(ValueError, r'^impact review response differs from its assignment: .* is too short$'):
            self.api.validate_impact_review_response(request, altered)
        altered = deepcopy(output)
        altered['impact_review']['plan_decisions'][1]['plan_digest'] = request['plans']['bundle']['digest']
        with self.assertRaisesRegex(ValueError, r'^impact review response differs from its assignment: .* is not valid under any of the given schemas$'):
            self.api.validate_impact_review_response(request, altered)
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            ctx = {'action': action, 'execution_id': 'EX-review', 'snapshot': 'review-input', 'kind_definitions': {}}
            submission.install_tools(workspace, ctx, schema, None, clock=_entry.ports.clock)
            draft = workspace / '.scratch/draft.json'
            draft.parent.mkdir()
            draft.write_text(json.dumps(output), encoding='utf-8')
            self.assertTrue(submission.producer_check(workspace, draft, clock=_entry.ports.clock)['passed'])
            bad = deepcopy(output)
            bad['impact_review']['plan_decisions'] = [bad['impact_review']['plan_decisions'][0]] * 3
            draft.write_text(json.dumps(bad), encoding='utf-8')
            self.assertFalse(submission.producer_check(workspace, draft, clock=_entry.ports.clock)['passed'],
                             'Installed producer must reject duplicate scope judgments')

    def test_review_required_is_a_waiting_disposition_not_a_producer_retry(self):
        result = self.api.apply_bundles(self.instance, self.runtime, self.output, self.extensions, self.fixed_context,
            execution_id='EX-producer', apply_bundle=lambda *args: self.fail('unreviewed mutation'),
            validate_current=lambda i, r, b: self.api.require_bundle_impact_review(i, r, b,
                producer_execution_id='EX-producer', input_snapshot='fixed-input'),
            validate_candidate=lambda *args: self.fail('unreviewed candidate'), publish=lambda *args: self.fail('unreviewed publication'))
        self.assertEqual('impact_review', result['bundles'][0]['next_owner'])
        self.assertEqual(self.request(), result['bundles'][0]['impact_review_request'])

    def test_review_evidence_does_not_change_the_mathematical_impact_plan(self):
        before = self.request()
        output = self.review_output(before)
        output['used_sources'] = [self.ids[0]]
        self.runtime['executions']['EX-review'] = {'id': 'EX-review', 'role': 'maintenance', 'status': 'ended',
            'action': {'role': 'maintenance', 'stage': 'impact_review', 'input_basis': {'impact_review': before}}, 'output': output}
        self.assertEqual(before, self.request(), 'Recording the review must not invalidate its own assigned impact plan')
        # A changed dependency makes the first assignment historical. Its
        # execution remains in the new impact; only the new exact review is
        # excluded. Both requests come from the real dependency planner.
        from support.record_builders import observation_knowledge
        candidate = observation_knowledge('Later dependent')
        candidate['dependencies'] = [self.ids[0]]
        self.instance, self.runtime, _ = knowledge_io.import_candidate(
            self.instance, self.runtime, candidate, source_ref='UC-dependent',
            actor_ref='UC-dependent', clock=self.clock)
        changed = self.request()
        self.assertNotEqual(before, changed)
        self.assertIn('EX-review', changed['plans']['bundle']['computed_impact'])
        new_output = self.review_output(changed)
        new_output['used_sources'] = [self.ids[0]]
        self.runtime['executions']['EX-current-review'] = {
            'id': 'EX-current-review', 'role': 'maintenance', 'status': 'ended',
            'action': {'role': 'maintenance', 'stage': 'impact_review',
                       'input_basis': {'impact_review': changed}}, 'output': new_output}
        self.assertEqual(changed, self.request(),
            'A stale review must not prevent exclusion of the exact current assignment')

    def test_review_resolver_uses_actual_git_bytes_and_scoped_receipt(self):
        """About 0.7 s, over the 0.2 s unit budget: three reviews are sealed by the central capture and published."""
        request = self.request()
        action = {'id': 'AC-review', 'role': 'maintenance', 'stage': 'impact_review', 'input_basis': {'impact_review': request}}
        output = self.review_output(request)
        fixed = {'action': action, 'execution_id': 'EX-review'}
        review_bundle = next(self.api.split_bundles(output, {}, fixed))
        self.runtime['executions']['EX-review'] = {'id': 'EX-review', 'role': 'maintenance', 'actor_kind': 'ai', 'status': 'running',
            'action': action, 'output': output, 'input_bundle': 'BA-review-input'}
        self.runtime['integrations'] = {'IN-review': {'id': 'IN-review', 'execution_id': 'EX-review',
            'payload_sha256': review_bundle['payload_sha256'],
            'response_sha256': exact_content_hash(self.api.member_values(output, {}, fixed)['output'])}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = fixture_store(root)
            workspace = root / 'review-workspace'
            workspace.mkdir()
            artifacts = self.seal(self.runtime['executions']['EX-review'], output, fixed, workspace)
            head = store.publish(None, {'research/fixture.json': b'{}',
                'runtime/artifacts/BA-review-input/input/submission/context.json': canonical_json(fixed),
                **artifacts}).head
            args = {'producer_execution_id': 'EX-producer', 'input_snapshot': 'fixed-input',
                'review_execution_id': 'EX-review', 'snapshot': head,
                'read_artifact': lambda path, snapshot: store.read_bytes(snapshot, path)}
            confirmations = self.api.require_bundle_impact_review(self.instance, self.runtime, self.bundle, **args)
            self.assertEqual(set(request['plans']), set(confirmations))
            changed, running = self.api.apply_reviewed_knowledge_changes(self.instance, self.runtime, self.bundle,
                actor_ref='EX-producer', **args, clock=self.clock)
            self.assertEqual({self.ids[0], self.ids[2]},
                {row['supersedes'] for row in changed['knowledge'].values() if row.get('supersedes')})
            saved = store.publish(head, {'research/domain-result.json': canonical_json(changed),
                                        'runtime/domain-result.json': canonical_json(running)}).head
            self.assertEqual(changed, json.loads(store.read_bytes(saved, 'research/domain-result.json')))
            retry_runtime = deepcopy(self.runtime)
            retry_runtime['executions']['EX-retry'] = {'id': 'EX-retry', 'continuation_of': 'EX-producer'}
            self.assertEqual(confirmations, self.api.require_bundle_impact_review(self.instance, retry_runtime,
                self.bundle, receiving_execution_id='EX-retry', **args))
            retry_runtime['executions']['EX-retry'].pop('continuation_of')
            with self.assertRaisesRegex(ValueError, '^impact approval cannot transfer to an unrelated receiving execution$'):
                self.api.require_bundle_impact_review(self.instance, retry_runtime, self.bundle,
                    receiving_execution_id='EX-retry', **args)
            cached = deepcopy(self.runtime)
            cached['executions']['EX-review']['output']['summary'] = 'Untrusted cached projection'
            self.assertEqual(confirmations, self.api.require_bundle_impact_review(self.instance, cached, self.bundle, **args))
            reasons = {'same_producer': '^independent checker execution required$', 'other_bundle': '^impact review is not the accepted designated current assignment$', 'stale': 'current assignment',
                       'unsealed': '^impact review has no matching published response receipt$', 'tampered_output': 'sealed output_ref hash differs',
                       'author_continuation': '^checker resumes an author lineage$', 'machine': '^impact review is not the accepted designated current assignment$'}
            for case, reason in reasons.items():
                with self.subTest(case=case):
                    i, r, b, a = deepcopy(self.instance), deepcopy(self.runtime), deepcopy(self.bundle), dict(args)
                    if case == 'same_producer': a['review_execution_id'] = 'EX-producer'
                    if case == 'other_bundle': b['integration_id'] = 'IN-other'
                    if case == 'stale': i['knowledge'][self.ids[1]]['summary'] = 'Changed premise'
                    if case == 'unsealed': r['integrations'].clear()
                    if case == 'tampered_output':
                        output_ref = r['executions']['EX-review']['submission_intent']['output_ref']
                        a['read_artifact'] = lambda path, selected, output_ref=output_ref: (
                            canonical_json({**output, 'summary': 'Altered'}) if path == output_ref else store.read_bytes(selected, path))
                    if case == 'machine': r['executions']['EX-review']['actor_kind'] = 'machine'
                    if case == 'author_continuation':
                        r['executions']['EX-review']['continuation_of'] = 'EX-producer'
                    before = canonical_json(r)
                    with self.assertRaisesRegex(ValueError, reason):
                        self.api.require_bundle_impact_review(i, r, b, **a)
                    # A rejected review leaves the runtime it was checked against unchanged.
                    self.assertEqual(before, canonical_json(r))

            # A legally submitted negative judgment is evidence, never mutation permission.
            for decision in ('reject', 'unresolved'):
                negative = deepcopy(output)
                negative['impact_review']['plan_decisions'][0]['decision'] = decision
                self.api.validate_impact_review_response(request, negative)
                rejected_runtime = deepcopy(self.runtime)
                negative_id = 'EX-review-' + decision
                negative_input = 'BA-review-input-' + decision
                negative_fixed = {**deepcopy(fixed), 'execution_id': negative_id}
                negative_execution = {'id': negative_id, 'role': 'maintenance', 'actor_kind': 'ai',
                    'status': 'running', 'action': deepcopy(action), 'output': negative, 'input_bundle': negative_input}
                rejected_runtime['executions'][negative_id] = negative_execution
                negative_workspace = root / decision
                negative_workspace.mkdir()
                negative_artifacts = self.seal(negative_execution, negative, negative_fixed, negative_workspace)
                rejected_bundle = next(self.api.split_bundles(negative, {}, negative_fixed))
                rejected_runtime['integrations']['IN-review'].update(
                    execution_id=negative_id, payload_sha256=rejected_bundle['payload_sha256'],
                    response_sha256=exact_content_hash(self.api.member_values(negative, {}, negative_fixed)['output']))
                negative_head = store.publish(saved, {**negative_artifacts,
                    'runtime/artifacts/' + negative_input + '/input/submission/context.json': canonical_json(negative_fixed)}).head
                with self.subTest(decision=decision), self.assertRaisesRegex(ValueError, 'did not approve'):
                    self.api.require_bundle_impact_review(self.instance, rejected_runtime, self.bundle,
                        **{**args, 'snapshot': negative_head, 'review_execution_id': negative_id})
                saved = negative_head

    def test_sealed_review_allows_real_domain_git_retry_and_rejects_wrong_evidence(self):
        """About 0.7 s, over the 0.2 s unit budget: the review and the producer bundle are published through the storage contract."""
        from support.entry import entry
        _entry = entry()
        from do_math import activities, execution_profiles, model_policy
        from support.state_builders import current_state
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profiles = execution_profiles.build_profiles({'session_limits': model_policy.LIMITS,
                'tier_models': model_policy.MODELS, 'observation_mode': 'event_driven', 'max_input_bytes': 500000,
                'effort': 'medium', 'operator_effort': 'high', 'operator_timeout_seconds': 600,
                'scholarly_enabled': True, 'scholarly_server': None, 'claude_only_assigned_model': False}, host=_entry.ports.host)
            self.instance.update({k: v for k, v in profiles.items() if k != 'role_profile_refs'})
            self.runtime['queue'] = []

            def execution(identifier, role, action):
                aid = 'AT-' + identifier.removeprefix('EX-')
                at = activities.open_activity(self.runtime, activity_id=aid, activity_kind=role,
                    owner_ref='task', input_refs=[], opened_at='2026-09-20T00:00:00Z')
                row = {'id': identifier, 'role': role, 'action': action, 'actor_kind': 'ai', 'owner_activity_id': aid,
                    'created_at': '2026-09-20T00:00:00Z', 'status': 'running', 'input_manifest': [], 'context_origin': []}
                profile = next(p for p in profiles['execution_profiles'].values() if p['role'] == role)
                execution_profiles.bind_execution(row, profile)
                self.runtime['executions'][identifier] = row
                at['assigned_execution_ids'] = [identifier]
                return row
            execution('EX-producer', 'research_work', {'id': 'AC-producer', 'role': 'research_work', 'target': None})
            # Every stored state passes the current lifecycle gate.
            self.instance, self.runtime = current_state(self.instance, self.runtime)
            repo = record_store(root, clock=self.clock)
            head = repo.initialize(self.instance, self.runtime)
            self.runtime['executions']['EX-producer']['input_snapshot'] = head
            request = self.request()
            action = {'id': 'AC-review', 'role': 'maintenance', 'stage': 'impact_review', 'input_basis': {'impact_review': request}}
            reviewer = execution('EX-review', 'maintenance', action)
            fixed = {'action': action, 'execution_id': 'EX-review', 'snapshot': head,
                     'knowledge_catalog': [self.instance['knowledge'][kid] for kid in self.ids], 'kind_definitions': {}}
            output = self.review_output(request)
            output['used_sources'] = [self.ids[0], self.ids[2]]
            workspace = root / 'review-workspace'
            workspace.mkdir()
            schema = contracts.schema_for('maintenance')
            schema['properties']['impact_review'] = self.api.impact_review_response_schema(request)
            schema['required'].append('impact_review')
            submission.install_tools(workspace, fixed, schema, None, clock=_entry.ports.clock)
            (workspace / 'draft.json').write_bytes(canonical_json(output))
            sealed = submission.seal_submission(workspace, 'draft.json', execution_id='EX-review',
                context=fixed, schema=schema, max_artifact_bytes=1024 * 1024, clock=_entry.ports.clock)
            self.assertTrue(sealed['passed'], sealed['check']['issues'])
            reviewer.update(input_bundle='BA-review-input', submitted_output_ref='runtime/artifacts/BA-review-output/output.json',
                            output=output, input_snapshot=head)
            artifacts = {'runtime/artifacts/BA-review-input/input/submission/context.json': canonical_json(fixed),
                         **{'runtime/artifacts/BA-review-output/' + path: raw for path, raw in sealed['artifacts'].items()}}
            head = repo.save_with_state(head, self.instance, self.runtime, artifacts=artifacts)[0]

            def publish(i, r, bundle, validated):
                nonlocal head
                head = repo.save_validated(head, validated)[0]

            def validate(i, r, bundle):
                return repo.validate_candidate(i, r, head)

            def accept_review(i, r, bundle):
                from do_math.execution_lifecycle import record_submission_intent, transition_execution
                self.api.validate_impact_review_response(request, bundle['output'])
                record_submission_intent(r['executions']['EX-review'],
                    {**sealed['intent'], 'output_ref': reviewer['submitted_output_ref'],
                     'extensions_ref': 'runtime/artifacts/BA-review-output/extensions.json',
                     'check_ref': 'runtime/artifacts/BA-review-output/check.json'},
                    {'id': 'CT-review', 'kind': 'submit_intent', 'state': 'accepted', 'execution_id': 'EX-review',
                     'payload': {'submission_check': {'artifacts': [
                         {'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
                         for path, raw in artifacts.items()]}}},
                    at='2026-09-20T00:00:01Z')
                transition_execution(r['executions']['EX-review'], 'ended', at='2026-09-20T00:00:02Z',
                    outcome='output_accepted', disposition={'kind': 'submission_integrated'})
            review_result = self.api.apply_bundles(self.instance, self.runtime, output, {}, fixed,
                execution_id='EX-review', apply_bundle=accept_review,
                validate_current=lambda i, r, b: self.api.validate_impact_review_response(request, b['output']),
                validate_candidate=validate, publish=publish)
            self.assertEqual('accepted', review_result['status'], review_result['bundles'])
            _, self.instance, self.runtime = repo.load(head)
            args = {'producer_execution_id': 'EX-producer', 'input_snapshot': request['input_snapshot'],
                    'review_execution_id': 'EX-review', 'snapshot': head, 'read_artifact': repo.read}
            confirmations = self.api.require_bundle_impact_review(self.instance, self.runtime, self.bundle, **args)
            self.assertEqual(set(request['plans']), set(confirmations))
            reasons = {'same_producer': '^independent checker execution required$', 'other_bundle': '^impact review is not the accepted designated current assignment$', 'stale': 'current assignment',
                       'unsealed': '^impact review has no matching published response receipt$'}
            for case, reason in reasons.items():
                with self.subTest(case=case), self.assertRaisesRegex(ValueError, reason):
                    i, r, b, a = deepcopy(self.instance), deepcopy(self.runtime), deepcopy(self.bundle), dict(args)
                    if case == 'same_producer': a['review_execution_id'] = 'EX-producer'
                    if case == 'other_bundle': b['integration_id'] = 'IN-other'
                    if case == 'stale': i['knowledge'][self.ids[1]]['summary'] = 'Changed premise'
                    if case == 'unsealed': r['integrations'].clear()
                    self.api.require_bundle_impact_review(i, r, b, **a)

            def apply_changes(i, r, b):
                updated, running = self.api.apply_reviewed_knowledge_changes(i, r, b, actor_ref='EX-producer', **args, clock=self.clock)
                i.clear(); i.update(updated)
                r.clear(); r.update(running)
            result = self.api.apply_bundles(self.instance, self.runtime, self.output, self.extensions, self.fixed_context,
                execution_id='EX-producer', apply_bundle=apply_changes,
                validate_current=lambda i, r, b: self.api.require_bundle_impact_review(i, r, b, **args),
                validate_candidate=validate, publish=publish)
            self.assertEqual('accepted', result['status'], result)
            saved, i, r = repo.load(head)
            self.assertEqual({self.ids[0], self.ids[2]}, {v['supersedes'] for v in i['knowledge'].values() if v.get('supersedes')})
            replay = self.api.apply_bundles(i, r, self.output, self.extensions, self.fixed_context, execution_id='EX-producer',
                apply_bundle=lambda *a: self.fail('accepted bundle applied twice'),
                validate_current=lambda *a: self.fail('accepted bundle revalidated'),
                validate_candidate=validate, publish=lambda *a: self.fail('accepted bundle republished'))
            self.assertEqual('already_accepted', replay['bundles'][0]['status'])
            self.assertEqual(saved, head)


if __name__ == '__main__':
    unittest.main()
