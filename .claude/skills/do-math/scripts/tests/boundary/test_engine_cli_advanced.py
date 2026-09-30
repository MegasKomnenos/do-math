"""The advanced command surface on an instance ``init --create-repository`` made, without model execution (``cli.main``).

Commands run in this process through ``research_fixtures.run_cli`` on a copy of
one CLI-created instance (``support.engine_cli_created``). ``cli.main`` and
``cli.execute`` take no Ports, so the repository and the engine run on the real
Git process (1f seam ledger 6), which places these tests with the boundary tests.
Every control is sent as a JSON file and its receipt and the published state are
both checked. The legacy ``run --watch`` test replaced ``cli.ResearchEngine``
with a mock; here the product runs, ``sys.monitoring`` records the arguments of
the engine's ``run`` and the object it returned, and no model call starts.
"""
import unittest

from do_math.cli_contract import build_parser
from do_math import cli
from do_math.engine import ResearchEngine, control
from do_math.governance import governance_view
from do_math.knowledge import plan_impact
from do_math.knowledge_records import create_candidate
from do_math.model_runner import ModelRunner
from do_math.repository import ResearchRepository
from do_math.scheduler import OWNER_POLL_SECONDS
from do_math.wiring import real_ports
from support.engine_cli_created import CreatedCliTest, ReturnedValues, control_at_first_sleep
from support.provider_probes import ObservedCalls

GRANT = {'kind': 'grant', 'grant': {'id': 'HTTP', 'kind': 'http', 'allowed_origins': ['https://example.com'],
                                    'allowed_methods': ['GET'], 'allowed_path_prefixes': ['/'], 'credential_env': {}}}


def charter(identifier='CH-1', supersedes=(), goal='New goal'):
    from record_fixtures import surface_state
    instance, _ = surface_state()
    record = instance['governance']['CH-1']
    record = {k: record[k] for k in ('id', 'kind', 'revision', 'supersedes', 'content')}
    record.update(id=identifier, supersedes=list(supersedes), revision=1 if not supersedes else 2)
    record['content']['goal'] = goal
    return {'kind': 'charter', 'record': record}


class AdvancedCliTests(CreatedCliTest):
    def test_goal_policy_grant_query_and_revoke(self):
        code, result, _ = self.control('decision', {'kind': 'initialization', 'operation': 'governance',
                                                    'records': [charter()['record']]})
        self.assertEqual((code, result['effect']), (0, 'applied'))
        code, result, _ = self.control('decision', {'kind': 'policy', 'record': {'id': 'PO-1', 'kind': 'policy',
            'revision': 1, 'supersedes': [], 'content': {'rule_id': 'no_publish', 'scope': ['P'],
            'text': 'New policy', 'reason_refs': ['CH-1'], 'audit_refs': []}}})
        self.assertEqual((code, result['effect']), (0, 'applied'))
        self.assertEqual(self.control('decision', GRANT)[1]['effect'], 'applied')
        query = self.cli('query', '--repository', str(self.repo), '--instance', self.instance_id, '--kind', 'grant')
        self.assertEqual(query[0], 0)
        self.assertTrue(any(item['record']['id'] == 'HTTP' for item in query[1]['items']))
        self.assertEqual(self.control('decision', {'kind': 'revoke', 'grant_id': 'HTTP'})[1]['effect'], 'applied')
        _, instance, _ = self.load()
        self.assertEqual(governance_view(instance)['goal'], 'New goal')
        self.assertEqual(governance_view(instance)['policy_records'][0]['content']['text'], 'New policy')
        self.assertEqual(instance['grants']['HTTP']['status'], 'revoked')

    def test_changed_decision_precondition_is_a_consumed_rejection(self):
        initial = {'kind': 'initialization', 'operation': 'governance', 'records': [charter()['record']]}
        self.assertEqual(self.control('decision', initial)[1]['effect'], 'applied')
        self.assertEqual(self.control('decision', charter('CH-2', ['CH-1']))[1]['effect'], 'applied')
        code, result, _ = self.control('decision', charter('CH-stale', ['CH-1']))
        self.assertEqual(code, 0)
        self.assertEqual(result['effect'], 'rejected')
        self.assertEqual(result['reason'], 'supersession must name an active same-kind record')

    def test_knowledge_invalidation_and_trust_registration(self):
        store = ResearchRepository(self.repo, self.instance_id)
        head, instance, runtime = store.load()
        base = {'kind': 'conjecture', 'title': 'K', 'statement': 's', 'explanation': 'e', 'summary': 's',
                'lean_code': '', 'declaration_names': [], 'dependencies': []}
        instance, kid = create_candidate(instance, {**base, 'id': 'KN-1'}, source_ref='input-source', actor_ref='EX-author')
        instance, child = create_candidate(instance, {**base, 'id': 'KN-2', 'dependencies': [kid]},
                                           source_ref='input-source', actor_ref='EX-author')
        store.save_with_state(head, instance, runtime)
        plan = plan_impact(instance, runtime, [kid], [])
        confirmation = {'plan_digest': plan['digest'], 'decision': 'approve', 'review_ref': 'review',
                        'reviewer_ref': 'reviewer', 'producer_ref': 'producer',
                        'affected_ids': sorted(set(plan['computed_impact']) | set(plan['declared_impact']))}
        invalid = self.control('knowledge', {'operation': 'invalidate', 'id': kid, 'reason': 'withdrawn',
                                             'independent_confirmation': confirmation})
        self.assertEqual((invalid[0], invalid[1]['effect']), (0, 'applied'), invalid)
        _, instance, runtime = self.load()
        self.assertEqual(instance['knowledge'][kid]['lifecycle'], 'withdrawn')
        self.assertIn(child, plan['computed_impact'])
        self.assertNotIn('formal', instance['knowledge'][kid])
        path = self.root / 'invalid-trust.json'
        path.write_text('{"operation": "register", "toolchain": {"executable": "lean", "sha256": "abc"}, '
                        '"allowed_axioms": []}', encoding='utf-8')
        trust = self.cli('trust', '--repository', str(self.repo), '--instance', self.instance_id, '--file', str(path))
        self.assertEqual((trust[0], trust[1]['kind']), (2, 'input_error'), trust)
        self.assertEqual(trust[1]['message'], TRUST_REFUSAL)
        self.assertIsNone(self.load()[1].get('active_trust_environment'))

    def test_external_prepare_is_model_free_and_conversation_lifecycle(self):
        policy = self.control('decision', {'kind': 'initialization', 'operation': 'adopt', 'external_policy': 'explicit_grants'})
        self.assertEqual(policy[1]['effect'], 'applied', policy)
        self.control('decision', GRANT)
        prepared = self.control('external', {'operation': 'prepare', 'grant_id': 'HTTP', 'id': 'OP',
                                             'request': {'method': 'GET', 'url': 'https://example.com/read'}})
        self.assertEqual((prepared[0], prepared[1]['effect']), (0, 'applied'))
        self.assertEqual(self.load()[2]['external_operations']['OP']['status'], 'prepared')
        attach = {'operation': 'attach', 'id': 'C', 'generation': 1, 'disconnect_policy': 'pause', 'lease_seconds': 30}
        self.assertEqual(self.control('conversation', attach)[1]['effect'], 'applied')
        self.assertEqual(self.control('conversation', {'operation': 'heartbeat', 'id': 'C', 'generation': 1})[1]['effect'],
                         'applied')
        self.assertEqual(self.control('conversation', {'operation': 'detach', 'id': 'C', 'generation': 1})[1]['effect'],
                         'applied')
        _, instance, runtime = self.load()
        self.assertEqual(instance['conversation_loss_policy'], 'pause')
        self.assertEqual(runtime['conversations']['C']['status'], 'lost')

    def test_invalid_json_shape_and_missing_source_are_input_errors(self):
        path = self.root / 'array.json'
        path.write_text('[]', encoding='utf-8')
        bad = self.cli('decision', '--repository', str(self.repo), '--instance', self.instance_id, '--file', str(path))
        self.assertEqual((bad[0], bad[1]['kind']), (2, 'input_error'))
        self.assertEqual(bad[1]['message'], ARRAY_REFUSAL)
        missing = self.cli('source', '--repository', str(self.repo), '--instance', self.instance_id,
                           '--file', str(self.root / 'missing'))
        self.assertEqual((missing[0], missing[1]['kind']), (2, 'input_error'))
        self.assertEqual(missing[1]['message'], '--file is not a file: ' + str(self.root / 'missing'))


class RunForwardingTests(CreatedCliTest):
    def test_run_watch_is_forwarded_without_running_a_model(self):
        """The watching owner waits on its clock after an idle pass; a pause sent while it waits ends the run."""
        args = build_parser().parse_args(['run', '--repository', str(self.repo), '--instance', self.instance_id, '--watch'])
        pause = lambda: control(self.repo, self.instance_id, 'pause', text='stop watching', ports=real_ports())
        with control_at_first_sleep(pause, OWNER_POLL_SECONDS) as arrival, \
                ObservedCalls(run=ResearchEngine.run, model=ModelRunner.run) as calls, \
                ReturnedValues(run=ResearchEngine.run) as returned:
            value, code = cli.execute(args)
        self.assertEqual(code, 0)
        (arguments,) = calls.captured('run')
        self.assertEqual({key: arguments[key] for key in ('max_steps', 'watch', 'until_active')},
                         {'max_steps': None, 'watch': True, 'until_active': False})
        self.assertIsNotNone(arrival['sent'], 'the owner went on watching after its first idle pass')
        self.assertEqual(value['status'], 'paused')
        (result,) = returned.values['run']
        self.assertIs(value, result, 'the command returns the object the engine run returned')
        self.assertEqual(calls.count('model'), 0)


TRUST_REFUSAL = 'config: trust register requires exactly toolchain, allowed_axioms, toolchain_record and binding'
ARRAY_REFUSAL = 'JSON configuration must be an object'


if __name__ == '__main__':
    unittest.main()
