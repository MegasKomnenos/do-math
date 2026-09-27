"""Cross-owner response/dispatch tests; never invoke providers or real research."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import jsonschema

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from do_math.repository import exact_content_hash
import check_coverage
from do_math import contracts, execution_profiles, governance, knowledge, knowledge_io, knowledge_records as kr, planning
from do_math.engine import DEFAULT_CONFIG
from do_math.task_scope import apply_task_dispositions
from research_fixtures import bare_engine, review_items


def repository_root(start=Path(__file__).resolve()):
    for root in start.parents:
        if ((root / '.agents/skills/do-math/scripts/check_coverage.py').is_file()
                and (root / 'docs/do-math/통합-설계-명세-v9/source-vector-map.json').is_file()):
            return root
    raise RuntimeError('freeze both repository/.agents/skills/do-math and necessary docs')


ROOT = repository_root()
TRACE = ROOT / 'docs/do-math/implementation-v5/traceability.json'
SOURCE = ROOT / 'docs/do-math/통합-설계-명세-v9/source-vector-map.json'
TIME = '2026-09-20T00:00:00+00:00'


class InputSnapshot:
    """Storage-boundary fixture, not a replacement for any domain transition."""
    git_dir = None  # No repository: issued inputs are read, never cached across fixtures.
    def __init__(self, instance, runtime): self.snapshot = deepcopy((instance, runtime))
    def load(self, snapshot):
        if snapshot != 'input-snapshot': raise ValueError('unexpected snapshot')
        return snapshot, *deepcopy(self.snapshot)

    def view(self, snapshot):
        # The repository's read-only fixed-input read; callers never mutate it.
        return self.load(snapshot)

    def read(self, path, snapshot):
        if path.endswith('/input/submission/context.json'):
            instance, runtime = self.snapshot
            return json.dumps({'snapshot': snapshot, 'tasks': list(runtime['tasks'].values()),
                'ready_task_ids': planning.ready_task_ids(runtime, instance)}).encode()
        raise ValueError('fixture has no archived artifact: ' + path)


def engine_fixture(goal='Establish P', *, academic_requirements=None):
    e = bare_engine()
    e.instance = {'id': 'RI-evidence', 'feature_version': 5, 'lifecycle': {'state': 'active'},
        'goal_status': 'unresolved', 'goal_judgments': [],
        'sources': [], 'knowledge': {}, 'relations': [], 'decisions': {}, 'config': deepcopy(DEFAULT_CONFIG),
        'workspace': str(SCRIPTS),
        'grants': {'GR-evidence': {'id': 'GR-evidence', 'kind': 'local', 'status': 'active',
            'roles': ['research_work', 'supplemental_research'], 'task_ids': [],
            'expires_at': None, 'checkpoint_allowed': True, 'reuse': 'reusable'}}}
    charter = {'id': 'CH-fixture', 'kind': 'charter', 'revision': 1, 'supersedes': [], 'content': {
        'rationale': 'Research the stated goal', 'goal': goal, 'desired_result': goal,
        'success_criteria': [goal], 'partial_success_criteria': ['Cases settled'],
        'included_scope': ['P'], 'excluded_scope': [], 'priorities': ['P'], 'preferences': [],
        'evidence_boundary': 'Proof not preference', 'academic_requirements': academic_requirements or [],
        'decision_authority': 'user', 'stop_conditions': []}}
    source = governance.preserve_source('US-fixture', 'User approves: ' + goal, origin='user', revision=1)
    e.instance = governance.initialize_governance(e.instance, source, {'id': 'DC-fixture', 'actor': 'user',
        'source_ref': source['id'], 'source_sha256': source['sha256'],
        'record_hashes': {charter['id']: exact_content_hash(charter)}}, [charter])
    # ENGINE currently consumes this read projection. It is never persisted.
    from do_math.initialization import governance_working_view
    e.instance = governance_working_view(e.instance)
    e.instance['goal_status'] = 'unresolved'
    e.instance.update(execution_profiles.build_profiles(e.instance['config']))
    e.runtime = {'feature_version': 5, 'last_observed_utc': TIME, 'tasks': {}, 'activities': {}, 'executions': {}, 'queue': [],
        'waiting_actions': {}, 'history': [], 'inputs': [], 'questions': [], 'question_links': [],
        'interpretations': {}, 'events': [], 'pending_events': [], 'status': 'ready'}
    e.head = 'input-snapshot'
    e.lifecycle_clock = lambda: TIME
    e.lifecycle_monotonic = lambda: 0
    e._documents = contracts.all_prompt_documents()
    e.store = InputSnapshot(e.instance, e.runtime)
    return e


def task_fixture(identifier='TK-1'):
    return {'id': identifier, 'revision': 1, 'status': 'planned', 'title': 'Bounded result',
        'question': 'Does P hold?', 'scope': {'included': ['P'], 'excluded': ['publication']},
        'expected': {'outputs': ['report'], 'research_change': 'resolve one case'},
        'progress_criteria': [{'id': 'PC-1', 'claim': 'inspect a case', 'evidence_required': []}],
        'completion_obligations': [
            {'id': 'OB-proof', 'claim': 'provide result', 'judges': ['research_plan'], 'evidence_required': ['EV-proof']},
            {'id': 'OB-scope', 'claim': 'account for scope', 'judges': ['research_plan'], 'evidence_required': ['EV-scope']}],
        'inputs': [], 'reuse': [], 'dependencies': [], 'profile_refs': [], 'authority_refs': ['GR-evidence'],
        'basis_refs': [], 'occurrence_condition': {'op': 'always'}, 'producer_execution': 'EX-preparation',
        'reviews': [], 'results': []}


def reviewed_task(e, identifier='TK-1', **changes):
    task = task_fixture(identifier); task.update(changes)
    task['profile_refs'] = [execution_profiles.profile_ref(p) for p in e.instance['execution_profiles'].values()
                            if p['role'] in {'research_work', 'supplemental_research'}]
    e.runtime['tasks'][identifier] = task
    output = review_items([identifier])
    task['reviews'] = [planning.seal_contract_review(task, output, e.instance, e.runtime, execution_id='EX-review-' + identifier)]
    return task


def plan_fixture(**changes):
    return dict({'dispositions': [], 'task_assessments': [], 'goal_audit': False, 'preparation_requests': []}, **changes)


def apply_plan(e, plan, execution_id='EX-plan'):
    e.store = InputSnapshot(e.instance, e.runtime)
    e.runtime['executions'][execution_id] = {'id': execution_id, 'role': 'research_plan', 'status': 'ended',
                                          'input_snapshot': 'input-snapshot', 'input_bundle': 'BA-plan', 'extensions': {}}
    e._apply({'id': 'AC-' + execution_id, 'role': 'research_plan'}, plan, execution_id)


def candidate(statement='True', source='theorem truth : True := True.intro', **changes):
    return dict(kind='theorem', title=statement, statement=statement, explanation=statement, summary=statement,
                lean_code=source, declaration_names=['truth'], dependencies=[], **changes)


def accept_knowledge(e, proposed=None):
    """Only Lean/identity responses are fixtures; import/binding/use gates run."""
    proposed = proposed or candidate()
    e.instance, e.runtime, kid = knowledge_io.import_candidate(e.instance, e.runtime, proposed,
        source_ref='fixture:source', actor_ref='EX-producer')
    from research_fixtures import trust_environment, trust_fixture
    if not hasattr(e, '_trust_fixture_directory'):
        e._trust_fixture_directory = tempfile.TemporaryDirectory()
    trust, binding = trust_environment(trust_fixture(Path(e._trust_fixture_directory.name), ['synthetic-lean']))
    e.instance.update(active_trust_environment='TE-fixture', trust_environments={'TE-fixture': trust})
    e.runtime['trust_bindings'] = {'TE-fixture': binding}
    response = {'status': 'verified', 'source_sha256': hashlib.sha256(proposed['lean_code'].encode()).hexdigest(),
        'declarations': ['truth'], 'toolchain': deepcopy(trust['toolchain']), 'allowed_axioms': deepcopy(trust['allowed_axioms']), 'axioms': {'truth': []},
        'dependency_closure': {'truth': ['True', 'True.intro']},
        'dependency_evidence': {'truth': {'True': 'fixture-type', 'True.intro': 'fixture-constructor'}},
        'declaration_evidence': {'truth': {'type': proposed['statement'], 'value': 'fixture-proof'}}}
    e.instance = kr.record_formal_result(e.instance, kid, response, 'TE-fixture', runtime=e.runtime)
    e.instance, aid = kr.record_identity_assessment(e.instance, kid, {'decision': 'match',
        'basis': kr.identity_basis(e.instance, kid)}, 'policy:fixture', runtime=e.runtime)
    return kid, aid


def audit_goal(e, kid, decision='satisfied'):
    basis = e._goal_basis_key()
    for slot in range(2):
        eid = 'EX-goal-' + str(slot) + '-' + str(len(e.instance['goal_judgments']))
        e.runtime['executions'][eid] = {'id': eid, 'role': 'goal_audit', 'status': 'ended'}
        e._bind_governance_input({'role': 'goal_audit'}, e.runtime['executions'][eid],
                                e._governance_context({'role': 'goal_audit'}, {}))
        e._apply({'role': 'goal_audit', 'slot': slot, 'basis': basis, 'required': 2},
            {'decision': decision, 'scope_complete': True, 'used_sources': [kid],
             'summary': 'Fixture auditor response for the stated charter', 'questions': []}, eid)


class PriorityVectorTests(unittest.TestCase):
    def test_v45_scheduler_blocks_other_activity_and_allows_ended_retry(self):
        e = engine_fixture(); task = reviewed_task(e)
        from do_math.initialization import adapter_for
        # Fixture behavioral capability observations are bound to actual local
        # adapter/worker identity. Reading hashes does not execute the CLI.
        e.instance['capability_evidence'] = {}
        for profile in e.instance['execution_profiles'].values():
            if profile['role'] not in {'research_work', 'supplemental_research'}: continue
            observation = {'execution_profile_ref': execution_profiles.profile_ref(profile),
                'identity': adapter_for(profile).capability_identity(), 'observed_at': TIME,
                'capabilities': {key: {'status': 'supported', 'evidence': 'fixture only'}
                                 for key in profile['required_capabilities']}}
            observation['id'] = 'CE-' + exact_content_hash(observation)
            e.instance['capability_evidence'][observation['id']] = observation
        # No difficulty/importance judgment is authored in this fixture;
        # the current admission rule therefore requires the high profile.
        model = e.instance['config']['tier_models']['high']
        first = {'id': 'AC-first', 'role': 'research_work', 'target': task['id'], 'grant_id': 'GR-evidence',
                 'owner_activity_id': 'AY-first', 'model_selection': {'model': model}}
        other = {**first, 'id': 'AC-other', 'owner_activity_id': 'AY-other', 'role': 'supplemental_research'}
        same_role = {**first, 'id': 'AC-other-work', 'owner_activity_id': 'AY-other'}
        self.assertTrue(e._dispatchable(other), repr(other))
        self.assertTrue(e._dispatchable(same_role), 'different work request is valid before occupancy')
        self.assertTrue(e._dispatchable(first), 'reviewed unoccupied task must be dispatchable')
        e.runtime['executions']['EX-first'] = {'id': 'EX-first', 'status': 'running',
            'role': first['role'], 'action': deepcopy(first), 'owner_activity_id': 'AY-first'}
        self.assertFalse(e._dispatchable(other))
        self.assertFalse(e._dispatchable(same_role))
        e.runtime['executions']['EX-first'].update(status='ended', outcome='execution_incomplete')
        self.assertTrue(e._dispatchable({**first, 'id': 'AC-retry', 'continuation_of': 'EX-first'}),
                        'ended attempt must not consume a lifetime task slot')
        self.assertTrue(e._dispatchable(other), 'ended work releases the task for the other role')

    def test_v112_engine_completion_rejects_open_then_applies_fulfilled_obligations(self):
        e = engine_fixture(); task = task_fixture()
        task.update(status='waiting', results=[{'id': 'EV-proof', 'execution_id': 'EX-work', 'report': 'bounded result'},
                                              {'id': 'EV-scope', 'execution_id': 'EX-work', 'report': 'scope disposition'}])
        e.runtime['tasks'][task['id']] = task
        assessment = {'task_id': task['id'], 'decision': 'completed', 'item_dispositions': [
            {'obligation_id': 'OB-proof', 'kind': 'fulfilled', 'evidence_refs': ['EV-proof']},
            {'obligation_id': 'OB-scope', 'kind': 'open', 'evidence_refs': []}]}
        before = deepcopy(task)
        for decision in ('completed', 'closed'):
            assessment['decision'] = decision
            with self.assertRaises(ValueError): apply_plan(e, plan_fixture(task_assessments=[assessment]))
        self.assertEqual(e.runtime['tasks'][task['id']], before)
        assessment['item_dispositions'][1].update(kind='fulfilled', evidence_refs=['EV-scope'])
        assessment['decision'] = 'completed'
        apply_plan(e, plan_fixture(task_assessments=[assessment]), 'EX-plan-retry')
        task = e.runtime['tasks'][task['id']]
        self.assertEqual(task['status'], 'completed')
        self.assertEqual(task['assessment']['execution_id'], 'EX-plan-retry')
        self.assertEqual(task['assessment']['item_dispositions'], assessment['item_dispositions'])

    def test_v82_withdrawal_preserves_separate_formal_assessment_and_use(self):
        e = engine_fixture(); kid, aid = accept_knowledge(e); task = task_fixture()
        e.runtime['tasks'][task['id']] = task
        e.runtime['executions']['EX-preparation'] = {'id': 'EX-preparation', 'role': 'research_preparation', 'status': 'ended'}
        e.runtime['queue'] = [{'id': 'AC-cancel', 'role': 'research_work', 'target': task['id']}]
        families = {name: deepcopy(e.instance[name]) for name in
                    ('knowledge', 'formal_results', 'expositions', 'identity_assessments', 'assessment_uses')}
        request = [{'task_id': task['id'], 'disposition': 'withdraw', 'reason': 'Different direction'}]
        changed, runtime = apply_task_dispositions(e.instance, e.runtime, request,
            execution_id='EX-planner', input_tasks=deepcopy(e.runtime['tasks']))
        self.assertEqual(runtime['tasks'][task['id']]['status'], 'closed')
        self.assertEqual(runtime['queue'], [])
        self.assertEqual({name: changed[name] for name in families}, families)
        self.assertTrue(knowledge.assess_use(changed['knowledge'][kid], changed)['valid'])
        e.instance = kr.set_assessment_use(e.instance, aid, 'suspended', 'check objection', 'reviewer')
        changed, _ = apply_task_dispositions(e.instance, e.runtime, request,
            execution_id='EX-planner', input_tasks=deepcopy(e.runtime['tasks']))
        self.assertFalse(knowledge.assess_use(changed['knowledge'][kid], changed)['valid'])
        self.assertEqual(changed['formal_results'], families['formal_results'])


class ProducerStorageContractTests(unittest.TestCase):
    def test_accepted_uncertainty_metadata_matches_registered_storage_shape(self):
        from do_math import submission
        from do_math.state_contract import default_state_contract
        from test_redesign_CONTRACTS import response, context
        wire = submission.extension_schema({'role': 'research_work'})
        registered = default_state_contract().family('research', 'knowledge').schema
        output = response()
        output['integration_bundles'][0]['members'].append('activity-extensions.json/knowledge_metadata/0')
        workspace = Path(self.enterContext(tempfile.TemporaryDirectory()))
        for value in ('Not a proof', {'claim': 'Not a proof', 'scope': 'finite search only'},
                      None, [], 7, False):
            with self.subTest(value=value):
                extension = {'knowledge_metadata': [{'title': 'A', 'uncertainty_assessment': value}]}
                valid = isinstance(value, (str, dict))
                errors = list(jsonschema.Draft202012Validator(wire).iter_errors(extension))
                self.assertEqual(not errors, valid)
                issues = submission.payload_issues(output, contracts.schema_for('research_work'),
                    context(), extension, workspace)
                self.assertEqual(not issues, valid, issues)
                proposed = {**output['knowledge'][0], 'uncertainty_assessment': value}
                if not valid:
                    self.assertTrue(any(row['rule_id'] == 'schema.type' and
                        row['path'].endswith('/uncertainty_assessment') for row in issues), issues)
                    with self.assertRaisesRegex(ValueError, 'uncertainty_assessment'):
                        knowledge_io.import_candidate({}, {}, proposed,
                            source_ref='fixture:submission', actor_ref='fixture:author')
                    continue
                state, _, kid = knowledge_io.import_candidate({}, {}, proposed,
                    source_ref='fixture:submission', actor_ref='fixture:author')
                jsonschema.Draft202012Validator(registered).validate(state['knowledge'][kid])
                self.assertEqual(state['knowledge'][kid]['uncertainty_assessment'], value)


class TraceabilityCheckerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(SOURCE.read_text(encoding='utf-8'))
        cls.structural_trace = json.loads(TRACE.read_text(encoding='utf-8'))
        # Structural mutations do not change archived execution evidence. Check
        # the complete archive once in the integration test below; these copies
        # make no execution claim and never rewrite the real trace.
        cls.structural_trace['runs'] = {}
        cls.structural_trace['observed_runs'] = {}
        rows = [*cls.structural_trace['vectors'].values(),
                *cls.structural_trace['quality_contracts'].values(),
                *cls.structural_trace['walkthroughs']]
        for row in rows:
            row['execution'] = {'state': 'not_run', 'run_ids': []}
            for evidence in row.get('evidence', []):
                evidence.pop('observations', None)
        errors = check_coverage.validate_data(cls.structural_trace, cls.source, ROOT, SOURCE)
        if errors:
            raise AssertionError('negative samples require a valid baseline: ' + repr(errors))

    def check_mutation(self, mutate, expected):
        trace = deepcopy(self.structural_trace)
        mutate(trace)
        errors = check_coverage.validate_data(trace, self.source, ROOT, SOURCE)
        self.assertTrue(any(expected in error for error in errors), errors)

    def test_full_trace_is_structurally_valid_not_an_execution_pass(self):
        self.assertEqual(check_coverage.validate(TRACE, SOURCE, ROOT), [])

    def test_missing_vector_cannot_hide_in_defaults(self):
        self.check_mutation(lambda t: t['vectors'].pop('V01'), 'missing source IDs')

    def test_symbol_names_in_wrong_class_are_not_coordinates(self):
        self.check_mutation(lambda t: t['vectors']['V45']['evidence'][0].update(coordinate=
            '.agents/skills/do-math/scripts/tests/test_redesign_EVIDENCE.py::TraceabilityCheckerTests.test_v45_scheduler_blocks_other_activity_and_allows_ended_retry'), 'nonexistent evidence coordinate')

    def test_missing_file_and_path_escape_are_rejected(self):
        for c in ('missing.py::test_nothing', '../outside.py::test_nothing'):
            self.check_mutation(lambda t: t['vectors']['V45']['evidence'][0].update(coordinate=c), 'nonexistent evidence coordinate')

    def test_execution_pass_without_fixed_run_is_rejected(self):
        self.check_mutation(lambda t: t['vectors']['V45'].update(execution={'state': 'passed', 'run_ids': []}), 'fixed run')

    def test_semantic_coverage_needs_actual_assertion_scope(self):
        self.check_mutation(lambda t: t['vectors']['V45']['evidence'][0].update(asserts=''), 'asserts')

    def test_duplicate_walkthrough_is_not_set_equality(self):
        self.check_mutation(lambda t: t['walkthroughs'].append(deepcopy(t['walkthroughs'][0])), 'exactly once')

    def test_quality_source_vectors_may_not_silently_drift(self):
        self.check_mutation(lambda t: t['quality_contracts']['Q01'].update(source_vectors=[]), 'source_vectors')

    def test_source_requirement_may_not_be_reworded_as_a_pass(self):
        self.check_mutation(lambda t: t['vectors']['V45'].update(expected='A file exists'), 'source requirement')

    def test_test_pass_without_implementation_edition_is_rejected(self):
        trace = json.loads(TRACE.read_text(encoding='utf-8'))
        row = trace['vectors']['V45']
        # Synthetic complete mapping isolates the missing-edition invariant.
        row.update(mapping='mapped', gaps=[])
        row['execution'] = {'state': 'passed', 'run_ids': ['RUN-fixture']}
        outcomes = {e['coordinate']: 'passed' for e in row['evidence']}
        manifest = {c.partition('::')[0]: 'fixture' for c in outcomes}
        run = {'tests': outcomes, 'file_sha256': manifest}
        errors = []
        check_coverage._item(ROOT, 'V45', row, trace['semantic_groups'], {'RUN-fixture': run}, errors)
        self.assertEqual(errors, ['V45: fixed run omits implementation edition'])

    def test_failed_state_cannot_be_inferred_from_unrelated_failure(self):
        trace = json.loads(TRACE.read_text(encoding='utf-8'))
        row = trace['vectors']['V45']
        row['execution'] = {'state': 'failed', 'run_ids': ['RUN-fixture']}
        run = {'tests': {e['coordinate']: 'passed' for e in row['evidence']}}
        run['tests']['unrelated.py::test_other'] = 'failed'
        errors = []
        check_coverage._item(ROOT, 'V45', row, trace['semantic_groups'], {'RUN-fixture': run}, errors)
        self.assertEqual(errors, ['V45: failed state requires a cited failing test'])

    def test_fixed_run_rejects_changed_code_log_and_reported_outcome(self):
        # Synthetic files test the checker, never attest to an actual run.
        for changed, expected in [('implementation', 'run edition differs'),
                                  ('log', 'run log missing or changed'),
                                  ('outcome', 'machine report differs')]:
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / 'impl.py').write_text('def apply(): return 1\n', encoding='utf-8')
                (root / 'test_sample.py').write_text('\n'.join(
                    f'def test_w{i:02}(): pass' for i in range(1, 13)), encoding='utf-8')
                source = {'vectors': [{'id': 'V01', 'input': 'x', 'expected': 'y', 'source_row_sha256': 'fixture'}],
                          'quality_contracts': []}
                source_path = root / 'source.json'
                source_path.write_text(json.dumps(source), encoding='utf-8')
                digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
                row = {'mapping': 'mapped', 'groups': ['sample'], 'rationale': 'Synthetic checker input',
                    'scope': 'Structure only', 'gaps': [], 'implementation': ['impl.py::apply'],
                    'evidence': [{'coordinate': 'test_sample.py::test_w01', 'asserts': 'synthetic assertion',
                                  'boundary': ['synthetic report; no actual execution']}],
                    'execution': {'state': 'passed', 'run_ids': ['RUN']}}
                manifest = {p: digest(root / p) for p in ('impl.py', 'test_sample.py')}
                outcomes = {f'test_sample.py::test_w{i:02}': 'passed' for i in range(1, 13)}
                (root / 'run.log').write_text('synthetic checker fixture', encoding='utf-8')
                report = {'tests': outcomes, 'file_sha256': manifest}
                (root / 'report.json').write_text(json.dumps(report), encoding='utf-8')
                run = {'command': 'synthetic fixture only', 'tests': outcomes, 'file_sha256': manifest,
                    'log_path': 'run.log', 'log_sha256': digest(root / 'run.log'),
                    'report_path': 'report.json', 'report_sha256': digest(root / 'report.json')}
                walks = []
                for i in range(1, 13):
                    walk = deepcopy(row)
                    walk.update(id=i, input='synthetic input', transitions=['synthetic transition'],
                                real=['checker only'], stubbed=['everything else'])
                    walk['evidence'][0]['coordinate'] = f'test_sample.py::test_w{i:02}'
                    walks.append(walk)
                trace = {'schema_version': 2, 'source_vector_map': {'path': 'source.json', 'sha256': digest(source_path)},
                    'semantic_groups': {'sample': {'requirement': 'x', 'observed': 'y', 'limit': 'z'}},
                    'vectors': {'V01': {**row, **source['vectors'][0]}}, 'quality_contracts': {},
                    'runs': {'RUN': run}, 'walkthroughs': walks}
                self.assertEqual(check_coverage.validate_data(trace, source, root, source_path), [])
                if changed == 'implementation':
                    (root / 'impl.py').write_text('def apply(): return 2\n', encoding='utf-8')
                elif changed == 'log':
                    (root / 'run.log').write_text('changed log', encoding='utf-8')
                else:
                    report = deepcopy(report); report['tests']['test_sample.py::test_w01'] = 'failed'
                    (root / 'report.json').write_text(json.dumps(report), encoding='utf-8')
                    run['report_sha256'] = digest(root / 'report.json')
                errors = check_coverage.validate_data(trace, source, root, source_path)
                self.assertTrue(any(expected in error for error in errors), errors)


if __name__ == '__main__': unittest.main(verbosity=2)
