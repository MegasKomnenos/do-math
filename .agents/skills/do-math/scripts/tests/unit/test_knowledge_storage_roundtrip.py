"""Knowledge records stored and reloaded through the real ``ResearchRepository`` (layer 2): shared formal results,
exact source and compiler text, and revision round trips.

Every test starts from ``support.knowledge_roundtrip.KnowledgeRoundtripHarness``:
a verified, not yet reviewed theorem "Truth" in the active environment
``TE-test``, with synthetic sealed reviews recorded through the pure review
cycle, and a repository on the Git port's fake whose storage contract
validates every publication. Unicode that normalization would change is
written as escapes, so no editor can rewrite a test input.
"""
import copy
import hashlib
import json
import unittest

from do_math import knowledge, knowledge_io, knowledge_records as kr
from do_math.canonical import exact_content_hash
from support.knowledge_builders import knowledge_candidate
from support.knowledge_roundtrip import KnowledgeRoundtripHarness


class KnowledgeRoundtripTests(KnowledgeRoundtripHarness):
    def test_shared_formal_result_continuity_round_trips_for_each_exposition(self):
        """About 0.35 s, over the 0.2 s unit budget: the split state is published and reloaded through the storage contract five times."""
        from support.entry import entry
        _entry = entry()
        first = self.kid
        first_assessment = self.assessment()
        shared = self.state['knowledge'][first]['formal_result_id']
        proposed = knowledge_candidate(formal_result_ref=shared)
        proposed.update(title='Second explanation', explanation='An independent account of True')
        self.state, self.runtime, second = knowledge_io.import_candidate(
            self.state, self.runtime, proposed, source_ref='second-source', actor_ref='second-author', clock=_entry.ports.clock)
        self.kid = second
        second_assessment = self.assessment()
        self.roundtrip()
        self.assertEqual(self.state['knowledge'][second]['formal_result_id'], shared)
        previous_assessments = {first: first_assessment, second: second_assessment}
        for environment_id in ('TE-next', 'TE-third'):
            current_environment = self.state['active_trust_environment']
            self.state['trust_environments'][environment_id] = {
                **copy.deepcopy(self.state['trust_environments'][current_environment]),
                'id': environment_id, 'status': 'registered'}
            # Registering the same shared toolchain record again binds the same baseline.
            self.runtime['trust_bindings'][environment_id] = copy.deepcopy(self.runtime['trust_bindings'][current_environment])
            transition = knowledge.begin_transition(self.state, environment_id, clock=_entry.ports.clock)
            self.assertEqual({target['id'] for target in transition['targets']}, {first, second})
            for target in transition['targets']:
                self.assertEqual(target['exposition_id'],
                                 self.state['knowledge'][target['id']]['exposition_id'])
                result = copy.deepcopy(self.state['formal_results'][target['formal_result_id']]['verification'])
                result.update(id=target['id'], toolchain=copy.deepcopy(
                    self.state['trust_environments'][environment_id]['toolchain']))
                transition = knowledge.record_transition_result(self.state, transition, result)
            self.runtime.setdefault('trust_transitions', {})[transition['id']] = transition
            self.roundtrip()
            transition = self.runtime['trust_transitions'][transition['id']]
            self.state = knowledge.activate_transition(self.state, transition, at=_entry.ports.clock.now(), clock=_entry.ports.clock)
            transition['status'] = 'active'
            self.roundtrip()
            for kid, old_assessment in list(previous_assessments.items()):
                inherited = next(row for row in self.state['identity_assessments'].values()
                                 if row.get('previous_assessment_id') == old_assessment)
                self.assertEqual(self.state['expositions'][inherited['exposition_id']]['supersedes'],
                                 self.state['identity_assessments'][old_assessment]['exposition_id'])
                self.assertTrue(kr.usable_links(self.state, kid))
                previous_assessments[kid] = inherited['id']
            broken = copy.deepcopy(self.runtime)
            targets = broken['trust_transitions'][transition['id']]['targets']
            targets[0]['exposition_id'] = targets[1]['exposition_id']
            with self.assertRaisesRegex(ValueError, '^identity continuity requires the actual activated transition$'):
                self.repo.validate_candidate(self.state, broken)
            missing = copy.deepcopy(self.runtime)
            del missing['trust_transitions'][transition['id']]['targets'][0]['exposition_id']
            with self.assertRaisesRegex(ValueError, 'exposition_id'):
                self.repo.validate_candidate(self.state, missing)

    def test_unicode_currentness_and_impact_survive_actual_storage(self):
        self.assessment()
        self.state['knowledge'][self.kid]['title'] = 'Cafe\u0301'
        basis = knowledge.capture_basis(self.state, self.runtime, [self.kid])
        plan = knowledge.plan_impact(self.state, self.runtime, [self.kid], [])
        self.roundtrip()
        self.assertEqual(self.state['knowledge'][self.kid]['title'], 'Cafe\u0301')
        self.assertTrue(knowledge.validate_basis(basis, self.state, self.runtime)['valid'])
        self.assertEqual(plan, knowledge.plan_impact(self.state, self.runtime, [self.kid], []))
        self.assertNotEqual(knowledge.content_hash({'title': 'Cafe\u0301'}), knowledge.content_hash({'title': 'Caf\u00e9'}))
        self.state['knowledge'][self.kid]['title'] = 'Changed meaning'
        self.assertFalse(knowledge.validate_basis(basis, self.state, self.runtime)['valid'])

    def test_raw_lean_source_hash_and_record_basis_preserve_unicode_distinctions(self):
        formal = self.state['formal_results'][self.state['knowledge'][self.kid]['formal_result_id']]
        formal['lean_code'] = '-- Cafe\u0301\n' + formal['lean_code']
        formal['verification']['source_sha256'] = hashlib.sha256(formal['lean_code'].encode()).hexdigest()
        self.assertTrue(kr.formal_usable(self.state, formal))
        basis = knowledge.capture_basis(self.state, self.runtime, [formal['id']])
        formal['lean_code'] = formal['lean_code'].replace('Cafe\u0301', 'Caf\u00e9')
        self.assertFalse(knowledge.validate_basis(basis, self.state, self.runtime)['valid'])
        self.assertFalse(kr.formal_usable(self.state, formal))

    def test_current_mismatch_has_active_effect_without_positive_knowledge(self):
        aid = self.assessment('mismatch')
        self.roundtrip()  # Baseline must pass sealed-review and storage validation.
        sealed = copy.deepcopy(self.state['identity_assessments'][aid])
        self.state = kr.set_assessment_use(self.state, aid, 'suspended', 'formal objection', 'reviewer')
        self.state = kr.set_assessment_use(self.state, aid, 'active', 'reconfirmed exact mismatch', 'reviewer')
        self.roundtrip()
        self.assertEqual(self.state['identity_assessments'][aid], sealed)
        self.assertTrue(knowledge.assess_use(self.state['identity_assessments'][aid], self.state)['valid'])
        self.assertEqual(kr.usable_links(self.state, self.kid), [])

    def test_central_explanation_revision_reuses_formal_and_schedules_only_replacement(self):
        """About 0.2 s, over the 0.2 s unit budget: every round trip publishes and reloads the split state through the storage contract.

        The engine's candidate application (``_apply_bundle_candidate``) on the product engine loaded from the
        repository; its planner wake-up and goal currentness are real, where the legacy test replaced both."""
        from support.entry import entry
        _entry = entry()
        from do_math.configuration import DEFAULT_CONFIG
        from do_math import activities, execution_lifecycle
        from do_math.execution_profiles import build_profiles, profile_ref
        self.assessment()
        self.roundtrip()
        original_fid = self.state['knowledge'][self.kid]['formal_result_id']
        original_formal = copy.deepcopy(self.state['formal_results'][original_fid])
        changes = {'summary': 'Clearer summary of the unchanged formal proposition'}
        roots = knowledge.revision_roots(self.state, self.kid)
        impact = knowledge.plan_impact(self.state, self.runtime, roots, [])['computed_impact']
        profiles = build_profiles({**DEFAULT_CONFIG, 'lean_command': ['synthetic-lean']}, host=_entry.ports.host)
        profile = next(p for p in profiles['execution_profiles'].values() if p['role'] == 'research_work')
        self.state['execution_profiles'][profile['id']] = profile
        activity = activities.open_activity(self.runtime, activity_id=self.clock.new_id('AT'), activity_kind='research_work',
            owner_ref=self.kid, input_refs=[self.kid], opened_at='2026-09-20T00:00:00Z')
        eid, action_id = self.clock.new_id('EX'), self.clock.new_id('AC')
        action = {'id': action_id, 'lineage_id': action_id, 'role': 'research_work', 'target': self.kid}
        execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=activity['id'],
            actor_kind='ai', input_manifest={'source': self.kid}, profile_ref=profile_ref(profile), created_at='2026-09-20T00:00:00Z')
        execution.update(role='research_work', action=action, extensions={'knowledge_changes': [
            {'id': self.kid, 'changes': changes, 'impact_set': impact, 'reason': 'Explain the same result'}]})
        activities.assign_execution(self.runtime, activity['id'], execution)
        for status in ('starting', 'running'):
            execution_lifecycle.transition_execution(execution, status, at='2026-09-20T00:00:00Z')
        stale_id = self.clock.new_id('AC')
        self.runtime['queue'].append({'id': stale_id, 'lineage_id': stale_id, 'role': 'formal_check', 'target': self.kid})
        retained_id = self.clock.new_id('AC')
        retained = {'id': retained_id, 'lineage_id': retained_id, 'role': 'research_work', 'target': self.kid}
        self.runtime['queue'].append(retained)
        execution['input_snapshot'] = self.head
        self.roundtrip()
        prior_history = copy.deepcopy(self.runtime.get('history', []))
        engine = self.engine()
        # Candidate application now owns knowledge revisions; extension-only
        # bundles do not own the separate research response/task disposition.
        extensions = engine.runtime['executions'][eid]['extensions']
        bundle = {'integration_id': self.clock.new_id('IN'), 'payload_sha256': exact_content_hash(extensions),
            'members': ['activity-extensions.json/knowledge_changes/0'], 'extensions': extensions,
            'output': {}, 'owns_response': False, 'impact_set': impact,
            'previous_hashes': {self.kid: knowledge.content_hash(engine.instance['knowledge'][self.kid])}}
        engine._apply_bundle_candidate(engine.instance, engine.runtime, bundle, action=action, execution_id=eid,
            extensions=extensions)
        self.state, self.runtime = engine.instance, engine.runtime
        replacements = [k for k in self.state['knowledge'].values() if k.get('supersedes') == self.kid]
        self.assertEqual(len(replacements), 1)
        replacement = replacements[0]
        self.assertEqual(replacement['formal_result_id'], original_fid)
        self.assertEqual(self.state['formal_results'][original_fid], original_formal)
        self.assertFalse(any(a.get('target') == self.kid and a['role'] in {'formal_check', 'identity_review'} for a in self.runtime['queue']))
        self.assertIn(retained, self.runtime['queue'])
        self.assertEqual(self.runtime.get('history', [])[:len(prior_history)], prior_history)
        self.assertEqual([a['role'] for a in self.runtime['queue'] if a.get('target') == replacement['id']], ['identity_review'])
        self.roundtrip()


class ExactSourceTests(KnowledgeRoundtripHarness):
    def test_actual_git_candidate_preserves_exact_source_and_declaration_names(self):
        from support.entry import entry
        _entry = entry()
        source = 'theorem \u212a : True := True.intro\n-- e\u0301\r\n'
        data = knowledge_candidate()
        data.update(lean_code=source, declaration_names=['\u212a'])
        self.state, self.runtime, kid = knowledge_io.import_candidate(self.state, self.runtime, data,
            source_ref='raw-source-fixture', actor_ref='raw-source-author', clock=_entry.ports.clock)
        record = self.state['knowledge'][kid]
        basis = knowledge.capture_basis(self.state, self.runtime, [record['formal_result_id'], record['exposition_id']])
        impact = knowledge.plan_impact(self.state, self.runtime, [record['formal_result_id']], [])['computed_impact']
        self.roundtrip()
        proposal = kr.proposal_view(self.state, kid)
        self.assertEqual(proposal['lean_code'].encode(), source.encode())
        self.assertEqual(proposal['declaration_names'], ['\u212a'])
        self.assertTrue(knowledge.validate_basis(basis, self.state, self.runtime)['valid'])
        self.assertEqual(knowledge.plan_impact(self.state, self.runtime, [record['formal_result_id']], [])['computed_impact'], impact)
        persisted = self.repo.read_record(record['formal_result_id'], self.head)
        self.assertEqual(persisted['record']['lean_code'].encode(), source.encode())
        physical = self.repo.read(persisted['path'], self.head)
        self.assertEqual(hashlib.sha256(physical).hexdigest(), persisted['sha256'])

    def test_identity_basis_distinguishes_exact_exposition_and_compiler_expressions(self):
        formal = self.state['formal_results'][self.state['knowledge'][self.kid]['formal_result_id']]
        exposition = self.state['expositions'][self.state['knowledge'][self.kid]['exposition_id']]
        exposition['items'][0]['text'] = 'Expression e\u0301'
        first = kr.identity_basis(self.state, self.kid)
        exposition['items'][0]['text'] = 'Expression \u00e9'
        self.assertNotEqual(first, kr.identity_basis(self.state, self.kid))
        formal['verification']['declaration_evidence']['truth']['type'] = 'Expression e\u0301'
        first = kr.identity_basis(self.state, self.kid)
        formal['verification']['declaration_evidence']['truth']['type'] = 'Expression \u00e9'
        self.assertNotEqual(first, kr.identity_basis(self.state, self.kid))

    def test_synthetic_transition_review_cannot_cover_a_changed_unicode_expression(self):
        from support.entry import entry
        _entry = entry()
        self.state['trust_environments']['TE-next'] = {**copy.deepcopy(self.state['trust_environments']['TE-test']),
            'id': 'TE-next', 'status': 'registered'}
        transition = knowledge.begin_transition(self.state, 'TE-next', clock=_entry.ports.clock)
        result = copy.deepcopy(self.state['formal_results'][self.state['knowledge'][self.kid]['formal_result_id']]['verification'])
        result['id'] = self.kid
        result['declaration_evidence']['truth']['type'] = 'Exact expression \u212a'
        result['identity_review'] = {'decision': 'match', 'result_digest': exact_content_hash(result),
            'review_ref': 'synthetic:eligible-review', 'policy_ref': 'synthetic:frozen-policy'}
        before = copy.deepcopy(self.state)
        synthetic = knowledge.record_transition_result(self.state, transition, result)
        with self.assertRaisesRegex(ValueError, 'sealed staged identity review runtime'):
            knowledge.activate_transition(self.state, synthetic, at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        self.assertEqual(self.state, before)
        result['declaration_evidence']['truth']['type'] = 'Exact expression K'
        invalid = knowledge.record_transition_result(self.state, transition, result)
        with self.assertRaisesRegex(ValueError, 'sealed staged identity review runtime'):
            knowledge.activate_transition(self.state, invalid, at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        self.assertEqual(self.state, before)

    def test_actual_git_preserves_exact_compiler_result_and_mathematical_exposition(self):
        formal = self.state['formal_results'][self.state['knowledge'][self.kid]['formal_result_id']]
        formal['lean_code'] += '\n-- e\u0301\r\n'
        formal['verification']['source_sha256'] = hashlib.sha256(formal['lean_code'].encode()).hexdigest()
        formal['verification']['declaration_evidence']['truth']['type'] = 'String.literal "e\u0301"'
        formal['verification']['declaration_signatures'] = {'truth': 'String.literal "e\u0301"'}
        exposition = self.state['expositions'][self.state['knowledge'][self.kid]['exposition_id']]
        exposition['items'][0]['text'] = 'Exact mathematical expression e\u0301'
        expected_formal, expected_exposition = copy.deepcopy(formal), copy.deepcopy(exposition)
        self.roundtrip()
        self.assertEqual(self.state['formal_results'][formal['id']], expected_formal)
        self.assertEqual(self.state['expositions'][exposition['id']], expected_exposition)
        self.assertTrue(kr.formal_usable(self.state, self.state['formal_results'][formal['id']]))

    def test_source_catalog_delivers_exact_proposal_text_and_compiler_keys(self):
        from do_math.context_store import write_source_catalog
        formal = self.state['formal_results'][self.state['knowledge'][self.kid]['formal_result_id']]
        formal['lean_code'] += '\n-- e\u0301\r\n'
        formal['verification']['declaration_signatures'] = {'\u212a': 'first', 'K': 'second'}
        proposal = kr.proposal_view(self.state, self.kid)
        catalog = write_source_catalog({'proposal': proposal}, self.root)
        row = catalog['entries']['proposal']
        raw = (self.root / row['path']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
        self.assertEqual(json.loads(raw), proposal)


if __name__ == '__main__':
    unittest.main()
