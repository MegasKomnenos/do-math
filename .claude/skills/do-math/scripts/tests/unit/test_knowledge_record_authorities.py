"""Knowledge record families (layer 2): formal, exposition and identity authorities kept apart, kind definitions,
relations, dependency body evidence, trust-transition evidence, publication barriers, impact plans on small
states, and a storage round trip.

Most tests start from ``knowledge_fixtures.verified_knowledge``: the candidate
"Truth" (``theorem truth : True := True.intro``) verified with the fixture's
synthetic formal evidence in the active environment ``TE-test`` and sealed by a
``policy:1`` match judgment.
"""
import copy
from pathlib import Path
import re
import tempfile
import unittest

from do_math import activities, execution_lifecycle, knowledge, knowledge_io, knowledge_records as kr
from do_math.canonical import exact_content_hash
from do_math.configuration import DEFAULT_CONFIG
from do_math.execution_profiles import build_profiles, profile_ref
from do_math.local_host import LocalHost
from do_math.repository import ResearchRepository
from do_math.review_cycle import accept_result, identity_assessment, next_actions
from do_math.state_contract import default_state_contract, validate_record
from do_math.system_clock import new_id
from do_math.trust_validation import check_environment, environment_errors
from support.knowledge_builders import knowledge_candidate, verified_knowledge
from support.state_builders import current_state
from support.trust_inputs import trust_environment, trust_fixture
from support.review_inputs import scoped_start
from support.fakes.git_backend import make_fake, make_repository

REFERENCES = Path(__file__).resolve().parents[3] / 'references'


def next_environment(state):
    state['trust_environments']['TE-next'] = {'id': 'TE-next', 'status': 'registered', 'toolchain': {'version': 'next'},
                                              'allowed_axioms': []}


class AuthorityTests(unittest.TestCase):
    def test_import_separates_formal_and_exposition_authority(self):
        from support.entry import entry
        _entry = entry()
        state, runtime, kid = knowledge_io.import_candidate({}, {}, knowledge_candidate(), source_ref='source',
                                                            actor_ref='producer', clock=_entry.ports.clock)
        record = state['knowledge'][kid]
        self.assertNotIn('lean_code', record)
        self.assertNotIn('formal', record)
        self.assertIn(record['formal_result_id'], state['formal_results'])
        self.assertIn(record['exposition_id'], state['expositions'])

    def test_explanation_revision_preserves_formal_evidence_and_old_judgment(self):
        from support.entry import entry
        _entry = entry()
        state, runtime, kid, aid = verified_knowledge()
        formal = copy.deepcopy(state['formal_results'])
        assessment = copy.deepcopy(state['identity_assessments'][aid])
        declared = [aid, next(u['id'] for u in state['assessment_uses'].values() if u['assessment_id'] == aid)]
        revised, _ = knowledge.revise_knowledge(state, runtime, kid, {'summary': 'Revised summary'},
                                                reason='clarify', actor_ref='author', declared_impact=declared, clock=_entry.ports.clock)
        self.assertEqual(revised['formal_results'], formal)
        self.assertEqual(revised['identity_assessments'][aid], assessment)
        self.assertEqual(revised['knowledge'][kid]['lifecycle'], 'superseded')
        replacements = [r for r in revised['knowledge'].values() if r.get('supersedes') == kid]
        self.assertEqual(len(replacements), 1)
        self.assertFalse(knowledge.assess_use(replacements[0], revised)['valid'])
        old_use = next(u for u in revised['assessment_uses'].values() if u['assessment_id'] == aid)
        self.assertEqual(old_use['status'], 'suspended')
        self.assertEqual(revised['expositions'][state['knowledge'][kid]['exposition_id']]['lifecycle'], 'superseded')

    def test_decision_reference_reports_actual_split_environment(self):
        state, runtime, kid, aid = verified_knowledge()
        self.assertEqual(knowledge.decision_reference(state['knowledge'][kid], state)['trust_environment_id'], 'TE-test')

    def test_revision_reuses_candidate_kind_and_dependency_validation(self):
        from support.entry import entry
        _entry = entry()
        state, runtime, kid, aid = verified_knowledge()
        declared = [aid, next(u['id'] for u in state['assessment_uses'].values() if u['assessment_id'] == aid)]
        for changes, reason in (({'kind': 'unregistered_kind'}, 'unknown knowledge kind: unregistered_kind'),
                                ({'dependencies': ['KN-missing']}, 'candidate dependencies do not exist: KN-missing')):
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, re.escape(reason)):
                knowledge.revise_knowledge(state, runtime, kid, changes, reason='revision', actor_ref='author',
                                           declared_impact=declared, clock=_entry.ports.clock)

    def test_revision_changes_name_only_authored_fields(self):
        # The producer check and the application share this one rule.
        for field in sorted(knowledge.AUTHORED_FIELDS):
            with self.subTest(field=field):
                knowledge.validate_changes({field: 'value'})
        for field in ('id', 'status', 'formal', 'verified_at', 'identity_assessment', 'producer_execution_ids',
                      'unknown_field'):
            with self.subTest(field=field), self.assertRaisesRegex(
                    ValueError, '^changes name fields a revision cannot author: ' + field + '$'):
                knowledge.validate_changes({field: 'value'})

    def test_common_execution_names_exactly_the_authored_fields(self):
        """「공통 실행」 gives revision authors the closed field set that validate_changes accepts."""
        text = (REFERENCES / '공통-실행.md').read_text(encoding='utf-8')
        match = re.search(r'`changes`의 키는 저작 필드 (.+?) 가운데서만 고른다', text)
        self.assertIsNotNone(match)
        self.assertEqual(set(re.findall(r'`(\w+)`', match.group(1))), knowledge.AUTHORED_FIELDS)

    def test_import_captures_required_source_and_rejects_unknown_source(self):
        from support.entry import entry
        _entry = entry()
        state = {'sources': [{'name': 'paper', 'path': 'research/sources/paper.txt', 'sha256': 'original'}]}
        with self.assertRaisesRegex(ValueError, 'required source does not exist'):
            knowledge_io.import_candidate(state, {}, knowledge_candidate(source_refs=['absent']), source_ref='submission',
                                          actor_ref='author', clock=_entry.ports.clock)
        changed, _, kid = knowledge_io.import_candidate(state, {}, knowledge_candidate(source_refs=['paper']),
                                                        source_ref='submission', actor_ref='author', clock=_entry.ports.clock)
        self.assertEqual(changed['knowledge'][kid]['source_basis'][0]['sha256'], 'original')

    def test_assessment_suspension_is_local_and_reversible(self):
        state, runtime, kid, aid = verified_knowledge()
        before = copy.deepcopy(state['identity_assessments'])
        suspended = kr.set_assessment_use(state, aid, 'suspended', 'review defect', 'reviewer')
        self.assertEqual(suspended['identity_assessments'], before)
        self.assertFalse(knowledge.assess_use(suspended['knowledge'][kid], suspended)['valid'])
        self.assertTrue(kr.knowledge_view(suspended)[0]['formal_valid'])
        restored = kr.set_assessment_use(suspended, aid, 'active', 'defect resolved', 'reviewer')
        self.assertTrue(knowledge.assess_use(restored['knowledge'][kid], restored)['valid'])

    def test_independent_expositions_share_one_formal_result(self):
        from support.entry import entry
        _entry = entry()
        state, runtime, kid, aid = verified_knowledge()
        fid = state['knowledge'][kid]['formal_result_id']
        data = knowledge_candidate(formal_result_ref=fid)
        data['explanation'] = 'A second explanation'
        state, runtime, other = knowledge_io.import_candidate(state, runtime, data, source_ref='second-source',
                                                              actor_ref='other-author', clock=_entry.ports.clock)
        self.assertEqual(len(state['formal_results']), 1)
        self.assertEqual(runtime['queue'][-1]['role'], 'identity_review')
        state, second_assessment = kr.record_identity_assessment(
            state, other, {'decision': 'match', 'basis': kr.identity_basis(state, other)}, 'policy:1', runtime=runtime, clock=_entry.ports.clock)
        state = kr.set_assessment_use(state, aid, 'suspended', 'first explanation defect', 'reviewer')
        self.assertFalse(knowledge.assess_use(state['knowledge'][kid], state)['valid'])
        self.assertTrue(knowledge.assess_use(state['knowledge'][other], state)['valid'])

    def test_import_rejects_malformed_registry_id(self):
        from support.entry import entry
        _entry = entry()
        with self.assertRaisesRegex(ValueError, 'knowledge ID must be a canonical KN-prefixed ULID'):
            knowledge_io.import_candidate({}, {}, knowledge_candidate(id='KN-not-a-ulid'), source_ref='source',
                                          actor_ref='author', clock=_entry.ports.clock)

    def test_rejects_unapproved_environment_and_replayed_identity_basis(self):
        from support.entry import entry
        _entry = entry()
        state, runtime, kid, aid = verified_knowledge()
        assessment = {'decision': 'match', 'basis': {'formal': 'old', 'exposition': 'old'}}
        with self.assertRaisesRegex(ValueError, 'identity assessment must name the exact current formal and exposition basis'):
            kr.record_identity_assessment(state, kid, assessment, 'policy:1', runtime=runtime, clock=_entry.ports.clock)
        result = state['formal_results'][state['knowledge'][kid]['formal_result_id']]['verification']
        state['trust_environments']['TE-test']['status'] = 'registered'
        with self.assertRaisesRegex(ValueError, 'formal verification requires a preapproved active environment'):
            kr.record_formal_result(state, kid, result, 'TE-test', runtime=runtime)

    def test_publication_reads_runtime_transition_barrier(self):
        from support.entry import entry
        _entry = entry()
        state, runtime, kid, aid = verified_knowledge()
        runtime['trust_transitions'] = {'TR-test': {'status': 'checking'}}
        result = state['formal_results'][state['knowledge'][kid]['formal_result_id']]['verification']
        with self.assertRaisesRegex(ValueError, 'formal publication waits for the trust transition'):
            kr.record_formal_result(state, kid, result, 'TE-test', runtime=runtime)
        with self.assertRaisesRegex(ValueError, 'identity publication waits for the trust transition'):
            kr.record_identity_assessment(state, kid, {'decision': 'match', 'basis': kr.identity_basis(state, kid)},
                                          'policy:1', runtime=runtime, clock=_entry.ports.clock)


class KindTests(unittest.TestCase):
    def test_installed_relation_kinds_are_active_from_installation(self):
        from support.entry import entry
        _entry = entry()
        state = knowledge_io.ensure_ontology({})
        installed = {row['token'] for row in knowledge_io.BUILTIN_DEFINITIONS if row['family'] == 'relation'}
        catalog = knowledge_io.catalog_definitions(state)['relations']
        self.assertEqual({row['token'] for row in catalog}, installed)
        self.assertTrue(all(row['status'] == 'active' and row['builtin'] for row in catalog))
        supports = next(row for row in catalog if row['token'] == 'supports')
        with self.assertRaisesRegex(ValueError, 'already defined'):
            knowledge_io.register_kind_definition(state, {key: supports[key] for key in
                                                          ('family', 'token', 'meaning', 'constraints')},
                                                  source_ref='source', actor_ref='producer', clock=_entry.ports.clock)

    def test_kind_registration_requires_explicit_check_and_activation(self):
        from support.entry import entry
        _entry = entry()
        definition = dict(family='knowledge', token='bounded_result', meaning='A bounded result', constraints={})
        state, token = knowledge_io.register_kind_definition({}, definition, source_ref='source', actor_ref='producer', clock=_entry.ports.clock)
        definition = next(r for r in state['kind_definitions'].values() if r['token'] == token)
        self.assertEqual(definition['status'], 'candidate')

    def test_kind_definitions_use_record_ids_and_allow_explicit_replacement(self):
        from support.entry import entry
        _entry = entry()
        state = knowledge_io.ensure_ontology({})
        self.assertTrue(all(key == value['id'] for key, value in state['kind_definitions'].items()))
        state, runtime = knowledge_io.withdraw_kind_definition(state, {}, 'knowledge', 'theorem', reason='replacement',
                                                               actor_ref='review', clock=_entry.ports.clock)
        state, token = knowledge_io.register_kind_definition(
            state, {'family': 'knowledge', 'token': 'theorem', 'meaning': 'Revised theorem kind', 'constraints': {}},
            source_ref='revision', actor_ref='author', clock=_entry.ports.clock)
        replacement = next(d for d in state['kind_definitions'].values() if d['token'] == token and d['status'] == 'candidate')
        self.assertIn(replacement['supersedes'], state['kind_definitions'])

    def test_kind_constraints_and_withdrawal(self):
        from support.entry import entry
        _entry = entry()
        definition = dict(family='knowledge', token='bounded_result', meaning='A bounded result',
                          constraints={'allowed_epistemic_statuses': ['tentative'], 'required_fields': ['confirmed_scope']})
        state, token = knowledge_io.register_kind_definition({}, definition, source_ref='source', actor_ref='author', clock=_entry.ports.clock)
        with self.assertRaisesRegex(ValueError, 'kind definition must be checked before activation'):
            knowledge_io.activate_kind_definition(state, 'knowledge', token, approval_ref='review', actor_ref='reviewer')
        state = knowledge_io.check_kind_definition(state, 'knowledge', token, check_ref='check', actor_ref='checker')
        state = knowledge_io.activate_kind_definition(state, 'knowledge', token, approval_ref='review', actor_ref='reviewer')
        data = knowledge_candidate()
        data['kind'] = token
        with self.assertRaisesRegex(ValueError, 'epistemic_status is not allowed by the kind definition'):
            knowledge_io.import_candidate(state, {}, data, source_ref='source', actor_ref='author', clock=_entry.ports.clock)
        data.update(epistemic_status='tentative', confirmed_scope='finite case')
        state, runtime, kid = knowledge_io.import_candidate(state, {}, data, source_ref='source', actor_ref='author', clock=_entry.ports.clock)
        state, runtime = knowledge_io.withdraw_kind_definition(state, runtime, 'knowledge', token, reason='bad semantics',
                                                               actor_ref='reviewer', clock=_entry.ports.clock)
        self.assertTrue(state['knowledge'][kid]['kind_use_suspended'])


class RelationTests(unittest.TestCase):
    def test_mathematical_relation_consumes_separate_result_and_assessment(self):
        state, runtime, kid, aid = verified_knowledge()
        token = 'formally_implies'
        fid = state['knowledge'][kid]['formal_result_id']
        claim = {'kind': token, 'source': kid, 'target': kid, 'confirmed_scope': 'reflexive implication'}
        state['formal_results'][fid]['relation_claim'] = claim
        state['identity_assessments'][aid]['relation_claim'] = claim
        relation = {**claim, 'formal_result_refs': [fid], 'assessment_refs': [aid], 'evidence_refs': [kid]}
        self.assertTrue(knowledge_io.validate_relation(state, relation)['valid'])
        stopped = kr.set_assessment_use(state, aid, 'suspended', 'recheck', 'reviewer')
        self.assertFalse(knowledge_io.validate_relation(stopped, relation)['valid'])

    def test_relation_claim_is_bound_through_import_and_identity(self):
        from support.entry import entry
        _entry = entry()
        state, runtime, kid, aid = verified_knowledge()
        token = 'formally_implies'
        claim = {'kind': token, 'source': kid, 'target': kid, 'confirmed_scope': 'reflexive'}
        state, runtime, proof = knowledge_io.import_candidate(state, runtime, knowledge_candidate(relation_claim=claim),
                                                              source_ref='source', actor_ref='author', clock=_entry.ports.clock)
        verification = copy.deepcopy(state['formal_results'][state['knowledge'][kid]['formal_result_id']]['verification'])
        state = kr.record_formal_result(state, proof, verification, 'TE-test', runtime=runtime)
        state, identity = kr.record_identity_assessment(
            state, proof, {'decision': 'match', 'basis': kr.identity_basis(state, proof)}, 'policy:1', runtime=runtime, clock=_entry.ports.clock)
        relation = {**claim, 'formal_result_refs': [state['knowledge'][proof]['formal_result_id']],
                    'assessment_refs': [identity], 'evidence_refs': [kid]}
        self.assertTrue(knowledge_io.validate_relation(state, relation)['valid'])
        state['knowledge'][kid]['title'] = 'changed endpoint'
        self.assertFalse(knowledge_io.validate_relation(state, relation)['valid'])


class FormalEvidenceTests(unittest.TestCase):
    def imported(self):
        """A fresh candidate in a state whose active environment is the fixture's, and the fixture's verification."""
        from support.entry import entry
        _entry = entry()
        state, runtime, kid = knowledge_io.import_candidate({}, {}, knowledge_candidate(), source_ref='source',
                                                            actor_ref='producer', clock=_entry.ports.clock)
        fixture, _, _, _ = verified_knowledge()
        state.update(active_trust_environment='TE-test', trust_environments=fixture['trust_environments'])
        return state, runtime, kid, copy.deepcopy(next(iter(fixture['formal_results'].values()))['verification'])

    def test_formal_verification_requires_dependency_body_evidence(self):
        state, runtime, kid, verification = self.imported()
        verification.pop('dependency_evidence')
        with self.assertRaisesRegex(ValueError, 'dependency body evidence differs from the closure'):
            kr.record_formal_result(state, kid, verification, 'TE-test', runtime=runtime)

    def test_dependency_body_evidence_is_one_hash_table_over_the_declared_closures(self):
        state, runtime, kid, verification = self.imported()
        closure = verification['dependency_closure']['truth']
        table = {name: exact_content_hash(name) for name in closure}
        accepted = kr.record_formal_result(state, kid, {**verification, 'dependency_evidence': table}, 'TE-test',
                                           runtime=runtime)
        fid = accepted['knowledge'][kid]['formal_result_id']
        self.assertEqual(accepted['formal_results'][fid]['verification']['dependency_evidence'], table)
        for invalid in ({'truth': table}, {name: table[name] for name in closure[:-1]},
                        {**table, closure[0]: 'not-a-hash'}):
            with self.subTest(invalid=invalid), \
                    self.assertRaisesRegex(ValueError, 'dependency body evidence differs from the closure'):
                kr.record_formal_result(state, kid, {**verification, 'dependency_evidence': invalid}, 'TE-test',
                                        runtime=runtime)


class TrustTransitionEvidenceTests(unittest.TestCase):
    def test_trust_transition_uses_split_results_and_compares_evidence(self):
        from support.entry import entry
        _entry = entry()
        state, runtime, kid, aid = verified_knowledge()
        next_environment(state)
        transition = knowledge.begin_transition(state, 'TE-next', clock=_entry.ports.clock)
        self.assertEqual(len(transition['targets']), 1)
        self.assertIn('dependency_closure', transition['targets'][0])
        self.assertIn('axioms', transition['targets'][0])
        result = copy.deepcopy(state['formal_results'][state['knowledge'][kid]['formal_result_id']]['verification'])
        result.update(id=kid, toolchain={'version': 'next'})
        transition = knowledge.record_transition_result(state, transition, result)
        activated = knowledge.activate_transition(state, transition, at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        self.assertEqual(activated['active_trust_environment'], 'TE-next')
        self.assertTrue(knowledge.assess_use(activated['knowledge'][kid], activated)['valid'])
        self.assertEqual(activated['identity_assessments'][aid], state['identity_assessments'][aid])
        result['dependency_evidence']['True'] = exact_content_hash('changed-type')
        transition = knowledge.record_transition_result(state, knowledge.begin_transition(state, 'TE-next', clock=_entry.ports.clock), result)
        with self.assertRaisesRegex(ValueError, 'transition requires its sealed staged identity review runtime: ' + kid):
            knowledge.activate_transition(state, transition, at=_entry.ports.clock.now(), clock=_entry.ports.clock)

    def test_identity_review_cannot_replace_missing_new_kernel_evidence(self):
        from support.entry import entry
        _entry = entry()
        state, runtime, kid, aid = verified_knowledge()
        next_environment(state)
        transition = knowledge.begin_transition(state, 'TE-next', clock=_entry.ports.clock)
        result = copy.deepcopy(state['formal_results'][state['knowledge'][kid]['formal_result_id']]['verification'])
        result.update(id=kid, toolchain={'version': 'next'})
        result.pop('dependency_closure')
        result['identity_review'] = {'decision': 'match', 'result_digest': exact_content_hash(result),
                                     'review_ref': 'review', 'policy_ref': 'policy:1'}
        transition = knowledge.record_transition_result(state, transition, result)
        with self.assertRaisesRegex(ValueError, 'verification evidence incomplete: dependency_closure'):
            knowledge.activate_transition(state, transition, at=_entry.ports.clock.now(), clock=_entry.ports.clock)

    def test_transition_targets_store_the_dependency_hash_table(self):
        from support.entry import entry
        _entry = entry()
        state, runtime, kid, aid = verified_knowledge()
        next_environment(state)
        transition = knowledge.begin_transition(state, 'TE-next', clock=_entry.ports.clock)
        checker = default_state_contract().family('runtime', 'trust_transitions').checker
        validate_record(checker, transition, 'transition')
        nested = copy.deepcopy(transition)
        nested['targets'][0]['dependency_evidence'] = {'truth': transition['targets'][0]['dependency_evidence']}
        with self.assertRaisesRegex(ValueError, r'^transition/targets/0/dependency_evidence: .* is not valid under any of '
                                                r'the given schemas$'):
            validate_record(checker, nested, 'transition')


class ImpactPlanTests(unittest.TestCase):
    def test_impact_planning_does_not_mutate_and_includes_relations(self):
        state = {'knowledge': {'KN-a': {'id': 'KN-a', 'lifecycle': 'active'}},
                 'relations': [{'id': 'RL-a', 'source': 'KN-a', 'target': 'KN-a', 'status': 'active'}]}
        before = copy.deepcopy(state)
        plan = knowledge.plan_impact(state, {}, ['KN-a'], ['RL-a'])
        self.assertEqual(state, before)
        self.assertIn('RL-a', plan['computed_impact'])

    def test_impact_mismatch_and_staleness_reject_without_mutation(self):
        from support.entry import entry
        _entry = entry()
        state = {'knowledge': {'KN-a': {'id': 'KN-a', 'lifecycle': 'active'},
                               'KN-b': {'id': 'KN-b', 'lifecycle': 'active'}},
                 'relations': [{'id': 'RL-a', 'source': 'KN-a', 'target': 'KN-a', 'status': 'active'}]}
        before = copy.deepcopy(state)
        # A declared record beyond the computed closure needs an independent confirmation.
        mismatch = knowledge.plan_impact(state, {}, ['KN-a'], ['RL-a', 'KN-b'])
        with self.assertRaisesRegex(ValueError, 'impact requires independent scope and disposition confirmation'):
            knowledge.apply_impact(state, {}, mismatch, reason='change', clock=_entry.ports.clock)
        self.assertEqual(state, before)
        plan = knowledge.plan_impact(state, {}, ['KN-a'], ['RL-a'])
        state['relations'][0]['target'] = 'KN-changed'
        with self.assertRaisesRegex(ValueError, 'impact plan is stale or altered'):
            knowledge.apply_impact(state, {}, plan, reason='change', clock=_entry.ports.clock)

    def test_impact_tracks_origin_refs_and_missing_split_refs(self):
        state = {'knowledge': {'KN-a': {'id': 'KN-a', 'lifecycle': 'active'},
                               'KN-b': {'id': 'KN-b', 'lifecycle': 'active', 'origin_refs': ['KN-a'],
                                        'formal_result_refs': ['FR-missing']}}}
        plan = knowledge.plan_impact(state, {}, ['KN-a'], ['KN-b'])
        self.assertIn('KN-b', plan['computed_impact'])
        self.assertIn('FR-missing', plan['unresolved_refs'])

    def test_impact_preserves_terminal_task_and_suspends_its_judgment(self):
        from support.entry import entry
        _entry = entry()
        state = {'knowledge': {'KN-a': {'id': 'KN-a', 'lifecycle': 'active'}},
                 'goal_judgments': [{'id': 'GJ-a', 'used_sources': ['KN-a'], 'current': True}]}
        runtime = {'tasks': {'TK-a': {'id': 'TK-a', 'status': 'completed', 'inputs': ['KN-a'],
                                      'assessment': {'current': True}}}}
        plan = knowledge.plan_impact(state, runtime, ['KN-a'], ['TK-a', 'GJ-a'])
        changed, run = knowledge.apply_impact(state, runtime, plan, reason='premise changed', clock=_entry.ports.clock)
        self.assertEqual(run['tasks']['TK-a']['status'], 'completed')
        self.assertFalse(run['tasks']['TK-a']['assessment']['current'])
        self.assertFalse(changed['goal_judgments'][0]['current'])


class StorageRoundTripTests(unittest.TestCase):
    def test_storage_registration_roundtrip_uses_split_family_files(self):
        """Real ResearchRepository and domain validators over the in-process Git backend; compiler, reviewer and
        approval evidence is synthetic."""
        from support.entry import entry
        _entry = entry()
        contract = default_state_contract()
        with tempfile.TemporaryDirectory() as directory:
            environment, binding = trust_environment(trust_fixture(Path(directory), ['synthetic-lean']),
                                                     environment_id='TE-test', source_ref='synthetic:approval')
            self.assertEqual(environment_errors(environment, binding), [])
            self.assertEqual(check_environment(environment, binding, host=LocalHost(clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs), clock=_entry.ports.clock)['status'], 'verified')
            state, runtime, kid, _ = verified_knowledge(environment, binding=binding, identity=False)
            profiles = build_profiles(DEFAULT_CONFIG, host=_entry.ports.host)
            profile = next(p for p in profiles['execution_profiles'].values() if p['role'] == 'identity_review')
            state.update(execution_profiles={profile['id']: profile}, capacity_constraints=profiles['capacity_constraints'])
            activity = activities.open_activity(runtime, activity_id=new_id('AT'), activity_kind='identity_review',
                                                owner_ref=kid, input_refs=[kid], opened_at='2026-09-20T00:00:00Z')
            cycle = scoped_start({**kr.proposal_view(state, kid), 'revision': 1}, reviewers=2)
            for _ in range(2):
                action = next_actions(cycle)[0]
                eid = new_id('EX')
                output = dict(proposal_digest=cycle['proposal_digest'], summary='Synthetic complete review',
                              used_sources=['proposal'], questions=[], decision='match', scope_complete=True, findings=[])
                cycle = accept_result(cycle, action, output, eid)
                execution = execution_lifecycle.create_execution(
                    execution_id=eid, owner_activity_id=activity['id'], actor_kind='ai',
                    input_manifest={'proposal_digest': cycle['proposal_digest']}, profile_ref=profile_ref(profile),
                    created_at='2026-09-20T00:00:00Z')
                execution.update(role='identity_review')
                activities.assign_execution(runtime, activity['id'], execution)
                for status in ('starting', 'running'):
                    execution_lifecycle.transition_execution(execution, status, at='2026-09-20T00:00:00Z')
                execution['submission_receipt'] = {'state': 'accepted', 'evidence_ref': 'synthetic:review'}
                execution_lifecycle.transition_execution(execution, 'stopping', at='2026-09-20T00:00:00Z')
                execution_lifecycle.transition_execution(execution, 'ended', at='2026-09-20T00:00:00Z',
                                                         outcome='output_accepted')
            self.assertEqual(cycle['status'], 'completed')
            cycle.update(id=new_id('RC'), knowledge_id=kid, identity_basis=kr.identity_basis(state, kid),
                         policy_ref='policy:fixture')
            runtime['review_cycles'] = {cycle['id']: cycle}
            assessment = identity_assessment(cycle, reason='Synthetic sealed review')
            state, aid = kr.record_identity_assessment(state, kid, {**assessment, 'basis': cycle['identity_basis']},
                                                       cycle['policy_ref'], runtime=runtime, clock=_entry.ports.clock)
            repo = ResearchRepository(make_repository(Path(directory) / 'repository'), new_id('RI'), contract=contract,
                                      backend=make_fake(), clock=_entry.ports.clock)
            # Every stored state passes the current lifecycle gate.
            state, runtime = current_state(state, runtime)
            repo.initialize(state, runtime)
            head, loaded, loaded_runtime = repo.load()
            self.assertEqual(loaded['formal_results'], state['formal_results'])
            self.assertEqual(loaded['identity_assessments'], state['identity_assessments'])
            self.assertTrue(knowledge.assess_use(loaded['knowledge'][kid], loaded)['valid'])


if __name__ == '__main__':
    unittest.main()
