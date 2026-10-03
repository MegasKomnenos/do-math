"""The do-math command surface on a real Git repository, without model execution (``cli.main``, layer 3).

Commands run in this process through ``research_fixtures.run_cli`` on a copy of
one instance the CLI's ``init`` created (``support.engine_cli``); the help and
the input-error exit codes are also checked as a child process sees them.
These callers supply real Ports, so their repository and engine use the real
Git process, which places these tests with the boundary tests (1f seam ledger 6).
The legacy boundary tests replaced ``cli`` names (``control``, ``_control``,
``ResearchEngine``, ``ResearchRepository``, ``query_records``,
``_reconcile_operator``, ``execute``); here the product runs unchanged,
``sys.monitoring`` records the calls it makes and the arguments they received
(``support.provider_probes.ObservedCalls``), and a failure is a real one: damage
from outside do-math that the owner refuses to publish over.
"""
from argparse import Namespace
import base64
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from do_math import cli, scheduled_operator
from do_math.cli_contract import _json_arguments, build_parser
from do_math.control_contracts import control_request_id
from do_math.core_engine import query_records
from do_math.engine import ResearchEngine, control
from do_math.reporting import OBSERVED_FIELDS
from do_math.repository import ResearchRepository
from support.cli_images import initialized_cli
from support.engine_cli import CliInstanceTest, body, cli_instance
from support.engine_context import damage
from support.provider_probes import ObservedCalls
from test_categories import test_group

ENTRYPOINT = Path(__file__).resolve().parents[2] / 'do_math.py'
CLOSED_LIFECYCLE = 'closed/completed instance cannot apply lifecycle controls'
REFUSED_PUBLICATION = 'current state evidence must be repaired before publication: '


class ControlCliTests(CliInstanceTest):
    def test_resume_of_a_publicly_closed_instance_reports_its_rejection(self):
        closed = self.cli('close', *self.instance_args(), '--reason', 'close the research')
        self.assertEqual(closed.returncode, 0, closed.stdout + closed.stderr)
        self.assertEqual(body(closed)['effect'], 'applied')
        resumed = self.cli('resume', *self.instance_args())
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        rejected = body(resumed)
        self.assertEqual((rejected['effect'], rejected['reason']), ('rejected', CLOSED_LIFECYCLE))
        status = self.cli('status', *self.instance_args(), '--json')
        self.assertEqual(body(status)['status'], 'closed')

    def test_maintenance_fence_commands_reach_the_owner_and_keep_the_user_pause(self):
        args = self.instance_args()
        quiesced = self.cli('quiesce', *args, '--origin', 'operator', '--reason', 'fixture installation maintenance')
        self.assertEqual(quiesced.returncode, 0, quiesced.stdout + quiesced.stderr)
        request = body(quiesced)
        fence = self.store().load()[2]['maintenance_fence']
        self.assertEqual((fence['state'], fence['request_id'], fence['origin']),
                         ('quiescent', request['request_id'], 'operator'))
        paused = self.cli('pause', *args, '--origin', 'user', '--reason', 'separate user pause')
        self.assertEqual(paused.returncode, 0, paused.stdout + paused.stderr)
        released = self.cli('release-quiesce', *args, '--origin', 'operator', '--fence', fence['request_id'],
                            '--reason', 'fixture complete')
        self.assertEqual(released.returncode, 0, released.stdout + released.stderr)
        self.assertEqual(body(released)['effect'], 'applied')
        _, _, runtime = self.store().load()
        self.assertNotIn('maintenance_fence', runtime)
        self.assertEqual(runtime['status'], 'paused')
        self.assertEqual(runtime['user_pause']['reason'], 'separate user pause')


class CliTests(CliInstanceTest):
    def test_original_request_is_preserved_separately_from_the_mathematical_goal(self):
        original = '증명: n+0=n. 모델은 gpt-6-sol까지. 새 인스턴스.\n'
        path = self.root / 'original.txt'
        path.write_bytes(original.encode('utf-8'))
        response = self.cli('init', '--repository', str(self.repository), '--workspace', str(self.root / 'second'),
                            '--goal', 'n+0=n', '--request-text-file', str(path), '--config-file', str(self.operator_disabled))
        self.assertEqual(response.returncode, 0, response.stdout)
        _, instance, runtime = self.store(body(response)['instance_id']).load()
        self.assertEqual(instance['lifecycle']['immutable_input']['text'], original)
        self.assertEqual(runtime['inputs'][0]['config']['goal'], 'n+0=n')
        self.assertEqual(instance['lifecycle']['immutable_input']['sha256'], hashlib.sha256(original.encode()).hexdigest())

    def test_profile_selection_respects_the_role_floor_without_model_execution(self):
        response = self.cli('select-profile', *self.instance_args(), '--role', 'intent_interpretation')
        self.assertEqual(response.returncode, 0, response.stdout)
        result = body(response)
        self.assertEqual(result['selection']['tier'], 'high')
        self.assertEqual(result['profile']['id'], result['selection']['profile_ref']['id'])
        self.assertEqual(self.store().load()[2]['executions'], {})

    def test_resend_replays_its_receipt_until_an_opposite_control_intervenes(self):
        args = ['pause', *self.instance_args(), '--reason', 'audit2 pause']
        first = self.cli(*args)
        self.assertEqual(first.returncode, 0, first.stdout)
        original = body(first)
        # The same command with no state change between replays the first receipt.
        again = self.cli(*args)
        self.assertEqual(again.returncode, 0, again.stdout)
        self.assertEqual(json.loads(again.stdout)['request_id'], json.loads(first.stdout)['request_id'])
        self.assertEqual(body(again)['request_id'], original['request_id'])
        resumed = self.cli('resume', *self.instance_args(), '--reason', 'audit2 resume')
        self.assertEqual(resumed.returncode, 0, resumed.stdout)
        self.assertNotEqual(original['snapshot'], body(resumed)['snapshot'])
        # After the resume the same pause is a new request that pauses again.
        repeated = self.cli(*args)
        self.assertEqual(repeated.returncode, 0, repeated.stdout)
        result = body(repeated)
        self.assertNotEqual(result['request_id'], original['request_id'])
        self.assertEqual((result['effect'], result['status']), ('applied', 'paused'))
        # Its resend, with no resume between, replays its receipt.
        direct = self.control('pause', text='audit2 pause')
        self.assertEqual(direct['request_id'], result['request_id'])
        self.assertTrue(direct['replayed'])
        for field in ('effect', 'reason', 'status', 'snapshot', 'config'):
            self.assertEqual(direct[field], result[field], field)
        reapplied = self.cli(*args, '--idempotency-key', 'audit2 intentional reapply')
        receipt = body(reapplied)
        direct = self.control('pause', text='audit2 pause', idempotency_key='audit2 intentional reapply')
        self.assertNotEqual(receipt['request_id'], original['request_id'])
        self.assertEqual(receipt['request_id'], direct['request_id'])
        self.assertEqual(receipt['snapshot'], direct['snapshot'])

    def test_source_identity_and_effect_use_one_read(self):
        path = self.root / 'raw-source.bin'
        original, changed = b'\xff\x00original\r\n', b'changed after read'
        path.write_bytes(original)
        read, reads = Path.read_bytes, []

        def read_then_change(value):
            # Another writer replaces the file right after do-math reads it (a standard-library read, not do-math).
            data = read(value)
            if value == path:
                reads.append(data)
                path.write_bytes(changed)
            return data
        output = io.StringIO()
        with patch.object(Path, 'read_bytes', read_then_change), redirect_stdout(output):
            code = cli.main(['source', *self.instance_args(), '--file', str(path), '--name', 'raw.bin'])
        envelope = json.loads(output.getvalue())
        self.assertEqual(code, 0, envelope)
        self.assertEqual(reads, [original])
        store = self.store()
        head, instance, _ = store.load()
        entry = instance['sources'][-1]
        self.assertEqual(entry['name'], 'raw.bin')
        self.assertEqual(entry['sha256'], hashlib.sha256(original).hexdigest())
        self.assertEqual(store.read(entry['path'], head), original)
        normalized = {'name': 'raw.bin', 'body_base64': base64.b64encode(original).decode('ascii'),
                      'sha256': hashlib.sha256(original).hexdigest(), 'bytes': len(original)}
        direct = self.control('source', config=normalized)
        self.assertEqual(direct['request_id'], envelope['request_id'])
        self.assertEqual(direct['snapshot'], envelope['result']['snapshot'])
        alternate = self.root / 'same-bytes.bin'
        alternate.write_bytes(original)
        direct_file = self.control('source', config={'path': str(alternate), 'name': 'raw.bin'})
        self.assertEqual(direct_file['request_id'], envelope['request_id'])
        repeated = self.cli('source', *self.instance_args(), '--file', str(alternate), '--name', 'raw.bin')
        self.assertEqual(repeated.returncode, 0, repeated.stdout)
        self.assertEqual(body(repeated)['effect'], 'applied')

    def test_pending_and_rejected_receipts_keep_their_meaning(self):
        args = ['pause', *self.instance_args(), '--reason', 'wait for writer']
        with self.store().writer_lock():
            pending = self.cli(*args)
        self.assertEqual(pending.returncode, 0, pending.stdout)
        queued = body(pending)
        self.assertTrue(queued['accepted'])
        self.assertEqual(queued['effect'], 'pending engine processing')
        self.assertNotIn('snapshot', queued)
        done = self.cli(*args)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertEqual(body(done)['request_id'], queued['request_id'])
        self.assertEqual(body(done)['effect'], 'applied')
        # A well-formed request the engine refuses: the named environment does not exist.
        path = self.root / 'rejected.json'
        path.write_text(json.dumps({'operation': 'invalidate', 'env_id': 'TE-missing'}), encoding='utf-8')
        rejected = self.cli('trust', *self.instance_args(), '--file', str(path))
        self.assertEqual(rejected.returncode, 0, rejected.stdout)
        original = body(rejected)
        self.assertTrue(original['accepted'])
        self.assertEqual((original['effect'], original['reason']), ('rejected', 'unknown trust environment: TE-missing'))
        later = self.cli('resume', *self.instance_args(), '--reason', 'after rejected request')
        self.assertEqual(later.returncode, 0, later.stdout)
        repeated = self.cli('trust', *self.instance_args(), '--file', str(path))
        self.assertEqual(repeated.returncode, 0, repeated.stdout)
        for key in ('effect', 'reason', 'status', 'snapshot'):
            self.assertEqual(body(repeated)[key], original[key], key)

    def test_public_check_json_discovery_and_fixed_snapshot(self):
        result = self.cli('check', *self.instance_args())
        self.assertEqual(result.returncode, 0, result.stdout)
        value = json.loads(result.stdout)
        self.assertEqual(value['schema_version'], 5)
        self.assertEqual(value['command'], 'check')
        self.assertEqual(value['exit_code'], 0)
        self.assertEqual(value['result']['inspection']['status'], 'healthy')
        discovery = self.cli('--describe')
        self.assertEqual(discovery.returncode, 0, discovery.stdout)
        described = json.loads(discovery.stdout)['result']
        self.assertIn('check', described['commands'])
        # The discovery contract names the fields every actual envelope carries.
        self.assertEqual(set(described['response_fields'][:-1]), set(value) - {'result'})
        self.assertEqual(described['inspection_exit_codes'], {'healthy': 0, 'degraded': 1, 'blocked': 1, 'incomplete': 1})
        request = self.root / 'command.json'
        request.write_text(json.dumps({'schema_version': 5, 'command': 'check', 'payload': {
            'repository': str(self.repository), 'instance': self.instance, 'snapshot': self.initial['snapshot'],
            'kinds': ['record_storage']}}), encoding='utf-8')
        response = self.cli('--request-file', str(request))
        self.assertEqual(response.returncode, 0, response.stdout)
        data = json.loads(response.stdout)['result']
        self.assertEqual(data['snapshot'], self.initial['snapshot'])
        self.assertEqual(data['inspection']['requested_areas'], ['record_storage'])
        unknown = self.cli('check', *self.instance_args(), '--snapshot', self.initial['snapshot'], '--kinds', 'not_registered')
        self.assertEqual(unknown.returncode, 1, unknown.stdout)
        self.assertEqual(body(unknown)['inspection']['status'], 'incomplete')
        historical = self.cli('status', *self.instance_args(), '--snapshot', self.initial['snapshot'], '--json')
        self.assertEqual(historical.returncode, 0, historical.stdout)
        self.assertEqual(body(historical)['snapshot'], self.initial['snapshot'])
        # Before charter adoption the snapshot view shows the original input's goal, as live status does.
        self.assertEqual(body(historical)['goal'], 'Prove a small theorem')
        # One projection: a stored snapshot has the live fields, and nothing observed on this host.
        stored = body(historical)
        self.assertEqual({field: stored[field] for field in OBSERVED_FIELDS}, dict.fromkeys(OBSERVED_FIELDS))
        live = self.cli('status', *self.instance_args(), '--json')
        self.assertEqual(set(body(live)), set(stored))


    def test_explicit_request_identity_replays_once_and_rejects_changed_payload(self):
        first = self.cli('input', *self.instance_args(), '--text', 'One request', '--request-id', 'UC-repeat')
        self.assertEqual(first.returncode, 0, first.stdout)
        second = self.cli('input', *self.instance_args(), '--text', 'One request', '--request-id', 'UC-repeat')
        self.assertEqual(second.returncode, 0, second.stdout)
        self.assertTrue(body(second)['replayed'])
        _, _, runtime = self.store().load()
        self.assertEqual(runtime['processed_controls'].count('UC-repeat'), 1)
        conflict = self.cli('input', *self.instance_args(), '--text', 'Changed request', '--request-id', 'UC-repeat')
        self.assertEqual(conflict.returncode, 2, conflict.stdout)
        self.assertEqual(body(conflict)['message'], 'request_id reused with different payload')

    def test_status_input_pause_and_configure_apply_without_running_model(self):
        status = self.cli('status', *self.instance_args(), '--json')
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        self.assertEqual(body(status)['status'], 'initializing')
        incoming = self.cli('input', *self.instance_args(), '--text', 'Use induction')
        self.assertEqual(incoming.returncode, 0, incoming.stdout + incoming.stderr)
        self.assertTrue(body(incoming)['accepted'])
        paused = self.cli('pause', *self.instance_args(), '--reason', 'review inputs')
        self.assertEqual(paused.returncode, 0, paused.stdout + paused.stderr)
        self.assertEqual(body(paused)['status'], 'paused')
        config_path = self.root / 'config.json'
        config_path.write_text(json.dumps({'call_timeout_seconds': 4}), encoding='utf-8')
        configured = self.cli('configure', *self.instance_args(), '--config-file', str(config_path))
        self.assertEqual(configured.returncode, 0, configured.stdout + configured.stderr)
        self.assertEqual(body(configured)['config']['call_timeout_seconds'], 4)
        self.assertEqual(self.store().load()[2]['executions'], {})

    def test_request_applies_a_maintenance_queue_entry_without_model_execution(self):
        requested = self.cli('request', *self.instance_args(), '--role', 'maintenance', '--reason', 'inspect state')
        self.assertEqual(requested.returncode, 0, requested.stdout + requested.stderr)
        result = body(requested)
        self.assertTrue(result['accepted'])
        self.assertEqual(result['effect'], 'applied')
        status = self.cli('status', *self.instance_args(), '--json')
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        self.assertGreaterEqual(body(status)['pending_actions'], 1)
        _, _, runtime = self.store().load()
        self.assertIn('maintenance', [row['role'] for row in runtime['queue']])
        self.assertNotIn('research_preparation', [row['role'] for row in runtime['queue']])
        self.assertFalse(runtime['executions'], 'request must not start a model execution')

    def test_retry_action_reaches_the_public_control_inbox_idempotently(self):
        first = self.cli('request', *self.instance_args(), '--retry-action', 'AC-held', '--request-id', 'UC-retry-held')
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertTrue(body(first)['accepted'])
        second = self.cli('request', *self.instance_args(), '--retry-action', 'AC-held', '--request-id', 'UC-retry-held')
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertTrue(body(second)['replayed'])
        self.assertEqual(body(second)['request_id'], 'UC-retry-held')

    def test_query_read_export_and_check_use_a_fixed_repository_snapshot(self):
        records = self.cli('query', *self.instance_args(), '--limit', '1')
        self.assertEqual(records.returncode, 0, records.stdout + records.stderr)
        record_page = body(records)
        self.assertEqual(record_page['loaded'], len(record_page['items']))
        self.assertGreaterEqual(record_page['total'], record_page['loaded'])
        queried = self.cli('query', *self.instance_args(), '--files', '--prefix', 'research/', '--text', 'small', '--limit', '1')
        self.assertEqual(queried.returncode, 0, queried.stdout + queried.stderr)
        self.assertGreaterEqual(body(queried)['total'], 1)
        store = self.store()
        head, _, _ = store.load()
        path = store.list_files('research/', head)[0]
        read = self.cli('read', *self.instance_args(), '--path', path, '--snapshot', head)
        self.assertEqual(read.returncode, 0, read.stdout + read.stderr)
        self.assertEqual(body(read)['path'], path)
        self.assertEqual(body(read)['snapshot'], head)
        destination = self.root / 'export'
        exported = self.cli('export', *self.instance_args(), '--destination', str(destination))
        self.assertEqual(exported.returncode, 0, exported.stdout + exported.stderr)
        self.assertEqual((destination / path).read_bytes(), store.read(path, head))
        self.assertFalse((destination / 'research/instance.json').exists())
        checked = self.cli('check', *self.instance_args())
        report = body(checked)
        self.assertEqual(checked.returncode, 0 if report['passed'] else 1, report)
        self.assertIn('areas', report.get('inspection', report))

    def test_create_repository_is_explicit_and_only_accepts_empty_directory(self):
        created = self.root / 'created'
        implicit = self.cli('init', '--repository', str(created), '--workspace', str(self.root / 'implicit-workspace'),
                            '--goal', 'A research goal', '--config-file', str(self.operator_disabled))
        self.assertEqual(implicit.returncode, 2, implicit.stdout)
        self.assertEqual(body(implicit)['message'],
                         '--repository must name an existing Git repository; use init --create-repository explicitly')
        self.assertFalse((created / '.git').exists())
        result = self.cli('init', '--create-repository', '--repository', str(created), '--workspace',
                          str(self.root / 'other-workspace'), '--goal', 'A research goal',
                          '--config-file', str(self.operator_disabled))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((created / '.git').exists())
        nonempty = self.root / 'nonempty'
        nonempty.mkdir()
        (nonempty / 'file.txt').write_text('x', encoding='utf-8')
        refused = self.cli('init', '--create-repository', '--repository', str(nonempty), '--workspace',
                           str(self.root / 'third-workspace'), '--goal', 'A research goal',
                           '--config-file', str(self.operator_disabled))
        self.assertEqual(refused.returncode, 2)
        self.assertEqual(body(refused)['message'], '--create-repository accepts only a missing or empty directory')


class CliConsumerTests(CliInstanceTest):
    """What the CLI hands the engine and the repository, and how it reports what they answer."""

    def test_query_defaults_and_explicit_filters_reach_consumers_in_both_interfaces(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        parser = build_parser()
        base = ['query', *self.instance_args()]
        payload = {'repository': str(self.repository), 'instance': self.instance}
        for interface in ('cli', 'json'):
            def arguments(options, fields):
                if interface == 'cli':
                    return parser.parse_args(base + options)
                return _json_arguments(parser, {'schema_version': 5, 'command': 'query', 'payload': {**payload, **fields}})
            with self.subTest(interface=interface):
                with ObservedCalls(files=ResearchRepository.query, records=query_records) as calls:
                    cli.execute(arguments(['--files'], {'files': True}), codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id, ports=_entry.ports)
                    cli.execute(arguments(['--files', '--prefix', 'runtime/'], {'files': True, 'prefix': 'runtime/'}), codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id, ports=_entry.ports)
                    cli.execute(arguments([], {}), codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id, ports=_entry.ports)
                    cli.execute(arguments(['--kind', 'knowledge', '--related-to', 'KN-one', '--direction', 'incoming'],
                                          {'kind': 'knowledge', 'related_to': 'KN-one', 'direction': 'incoming'}), codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id, ports=_entry.ports)
                self.assertEqual([call['prefix'] for call in calls.captured('files', caller='do_math.cli')],
                                 ['research/', 'runtime/'])
                self.assertEqual([(call['kind'], call['related_to'], call['direction'])
                                  for call in calls.captured('records', caller='do_math.cli')],
                                 [(None, None, 'both'), ('knowledge', 'KN-one', 'incoming')])

    def test_replayed_configure_receipt_does_not_reapply_scheduler(self):
        requested = {'operator_enabled': False}
        path = self.root / 'configuration.json'
        path.write_text(json.dumps(requested), encoding='utf-8')
        # The same configure applied outside the CLI: the CLI's request replays its receipt.
        first = self.control('configure', config=requested)
        self.engine().process_controls()
        with ObservedCalls(reconcile=cli._reconcile_operator, schedule=scheduled_operator.schedule) as calls:
            response = self.cli('configure', *self.instance_args(), '--config-file', str(path))
        self.assertEqual(response.returncode, 0, response.stdout + response.stderr)
        result = body(response)
        self.assertEqual((result['request_id'], result['replayed'], result['effect']), (first['request_id'], True, 'applied'))
        self.assertEqual(result['operator_schedule']['status'], 'not_reapplied')
        self.assertEqual((calls.count('reconcile'), calls.count('schedule')), (0, 0))

    def test_rejected_configure_receipt_does_not_reapply_scheduler(self):
        # Admission checks a configure against the current configuration and the owner checks it again
        # against the configuration when it applies: an earlier admitted configure raises the initial
        # retry interval above the maximum this one sets, so the owner rejects this one.
        self.control('configure', config={'provider_retry_initial_seconds': 3600})
        path = self.root / 'configuration.json'
        path.write_text(json.dumps({'operator_enabled': False, 'provider_retry_max_seconds': 1800}), encoding='utf-8')
        with ObservedCalls(reconcile=cli._reconcile_operator, schedule=scheduled_operator.schedule) as calls:
            response = self.cli('configure', *self.instance_args(), '--config-file', str(path))
        self.assertEqual(response.returncode, 0, response.stdout + response.stderr)
        result = body(response)
        self.assertEqual((result['effect'], result['reason']),
                         ('rejected', 'provider retry maximum must be at least the initial interval'))
        self.assertEqual(result['operator_schedule'], {'status': 'not_applied', 'reason': 'configuration was rejected'})
        self.assertEqual((calls.count('reconcile'), calls.count('schedule')), (0, 0))

    def test_operator_effort_alone_leaves_the_schedule_untouched(self):
        path = self.root / 'configuration.json'
        path.write_text(json.dumps({'operator_effort': 'max'}), encoding='utf-8')
        with ObservedCalls(reconcile=cli._reconcile_operator, schedule=scheduled_operator.schedule) as calls:
            response = self.cli('configure', *self.instance_args(), '--config-file', str(path))
        self.assertEqual(response.returncode, 0, response.stdout + response.stderr)
        result = body(response)
        self.assertEqual((result['effect'], result['config']['operator_effort']), ('applied', 'max'))
        self.assertNotIn('operator_schedule', result)
        self.assertEqual((calls.count('reconcile'), calls.count('schedule')), (0, 0))

    def test_check_exit_follows_the_engine_inspection_status(self):
        head = self.store().load()[0]
        for kinds, status, code in ((['repair_iteration'], 'healthy', 0), (['not_registered'], 'incomplete', 1)):
            with self.subTest(kinds=kinds):
                with ObservedCalls(check=ResearchEngine.check) as calls:
                    response = self.cli('check', *self.instance_args(), '--snapshot', head, '--kinds', *kinds)
                self.assertEqual(response.returncode, code, response.stdout)
                result = body(response)
                self.assertEqual((result['inspection']['status'], result['exit_code'], result['passed']),
                                 (status, code, code == 0))
                (checked,) = calls.captured('check', caller='do_math.cli')
                self.assertEqual((checked['snapshot'], checked['requested_areas']), (head, kinds))
                # Everything else is the engine's own answer for that snapshot and those areas.
                direct = self.engine().check(snapshot=head, requested_areas=kinds)
                self.assertEqual({key: value for key, value in result.items() if key != 'exit_code'}, direct)

    def test_normalized_control_identity_at_public_boundary(self):
        # The CLI passes the command's identity inputs to ENGINE's control, which derives the
        # request ID (control_contracts.control_request_id), and reports the ID control returns:
        # the same command repeats one ID, a new key makes another.
        reported, history = [], len(self.store().load()[2]['history'])
        with ObservedCalls(admit=control) as calls:
            for extra in ([], [], ['--idempotency-key', 'again']):
                response = self.cli('pause', *self.instance_args(), '--reason', 'P', *extra)
                self.assertEqual(response.returncode, 0, response.stdout)
                reported.append(json.loads(response.stdout)['request_id'])
        forwarded = calls.captured('admit', caller='do_math.cli')
        self.assertEqual([row['request_id'] for row in forwarded], [None, None, None])
        self.assertEqual([row['idempotency_key'] for row in forwarded], [None, None, 'again'])
        ids = [control_request_id(self.instance, 'pause', text='P'),
               control_request_id(self.instance, 'pause', text='P', idempotency_key='again')]
        self.assertEqual(reported, [ids[0], ids[0], ids[1]])
        self.assertNotEqual(ids[0], ids[1])
        # The owner applied the first command and the keyed one; the resend added nothing.
        _, _, runtime = self.store().load()
        self.assertEqual([(row['kind'], row['request']['id']) for row in runtime['history'][history:]],
                         [('user_control', ids[0]), ('user_control', ids[1])])


class CliTemplateTests(CliInstanceTest):
    """``research_fixtures.restore_template``, which every test here starts from (``support.engine_cli.cli_instance``)."""

    def test_restored_template_is_an_independent_copy_of_the_published_state(self):
        head, instance, runtime = self.store().load()
        self.assertEqual(Path(instance['workspace']), self.workspace)
        self.control('pause', text='Change only this copy')
        self.engine().process_controls()
        self.assertNotEqual(self.store().load()[0], head)
        self.assertEqual(initialized_cli('existing'), (self.root, self.initial))
        self.assertEqual(self.store().load(), (head, instance, runtime))
        self.assertEqual(list((self.workspace / 'control' / self.instance).glob('*.json')), [])


class CliFailureTests(CliInstanceTest):
    """A control the owner cannot process: a source artifact was cut short from outside do-math."""

    def setUp(self):
        super().setUp()
        source = self.root / 'basis.txt'
        source.write_text('preserved original', encoding='utf-8')
        imported = self.cli('source', *self.instance_args(), '--file', str(source))
        self.assertEqual(body(imported)['effect'], 'applied')
        store = self.store()
        _, instance, _ = store.load()
        # Damage from outside do-math: the stored source is shorter than its record says.
        damage(store, instance['sources'][0]['path'], b'short')
        self.inbox = Path(instance['workspace']) / 'control' / self.instance

    def test_runtime_failure_is_a_structured_internal_error(self):
        response = self.cli('pause', *self.instance_args(), '--reason', 'P')
        self.assertEqual(response.returncode, 5, response.stdout)
        envelope = json.loads(response.stdout)
        error = body(response)
        self.assertEqual((error['kind'], error['next_owner'], error['retryable']), ('contract_error', 'maintenance', False))
        self.assertEqual(envelope['response_contract'], 'do-math-cli/5')
        self.assertRegex(error['message'], '^accepted request ' + re.escape(envelope['request_id'])
                         + ' could not be processed: ' + re.escape(REFUSED_PUBLICATION))

    def test_accepted_control_processing_failure_is_not_a_user_input_error(self):
        from support.entry import entry
        _entry = entry()
        from support.entry import entry
        _entry = entry()
        args = Namespace(repository=self.repository, instance=self.instance)
        with self.assertRaises(RuntimeError) as failed:
            from do_math.wiring import real_ports
            cli._control(args, 'configure', ports=real_ports(environment=_entry.environment), codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id)
        # Admission produced the request before its processing failed.
        self.assertTrue((self.inbox / (args._resolved_request_id + '.json')).is_file())
        self.assertRegex(str(failed.exception), '^accepted request ' + re.escape(args._resolved_request_id)
                         + ' could not be processed: ' + re.escape(REFUSED_PUBLICATION)
                         + '.*artifact length differs')
        self.assertIsInstance(failed.exception.__cause__, ValueError)




class CliExitTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.repository, self.workspace = self.root / "repository", self.root / "work"

    @test_group('resource')
    def test_help_and_input_error_exit_codes_are_structured(self):
        # Exit codes as the shell sees them: this test keeps the child process.
        def process(*arguments):
            return subprocess.run([sys.executable, str(ENTRYPOINT), *arguments], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, cwd=self.root)
        help_result = process('--help')
        self.assertEqual(help_result.returncode, 0)
        self.assertIn('init', help_result.stdout)
        self.assertIn('request', help_result.stdout)
        invalid = process('init', '--repository', str(self.repository), '--workspace', str(self.workspace))
        self.assertEqual(invalid.returncode, 2)
        error = body(invalid)
        self.assertEqual((error['kind'], error['message']),
                         ('input_error', 'one of the arguments --goal --goal-file is required'))
        # The discovery contract publishes the exit code the shell actually saw.
        described = cli.describe_commands(cli.build_parser())
        self.assertEqual(described['error_exit_codes']['input_error'], invalid.returncode)
        self.assertEqual(described['request_fields'], list(described['request_schema']['properties']))


if __name__ == '__main__':
    unittest.main()
