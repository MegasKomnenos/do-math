"""Checks of the do-math command surface without model execution.

Commands run in this process through ``research_fixtures.run_cli``; the
help and input-error exit codes are also checked as a child process sees them.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1]
ENTRYPOINT = SCRIPTS / "do_math.py"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
from research_fixtures import git_init, restore_template, run_cli


def response_body(response):
    envelope = json.loads(response.stdout)
    assert envelope['schema_version'] == 5
    assert envelope['exit_code'] == response.returncode
    assert ('result' in envelope) != ('error' in envelope)
    return envelope.get('result', envelope.get('error'))


def cli_instance(root, shared):
    """``restore_template`` build: one instance the CLI's ``init`` created; returns its result.

    The repository is ``root / 'repository'``, the workspace ``root / 'workspace'``,
    and ``root / 'operator-disabled.json'`` the configuration file ``init`` read.
    """
    repository = git_init(root / "repository")
    configuration = root / "operator-disabled.json"
    configuration.write_text(json.dumps({"operator_enabled": False}), encoding="utf-8")
    initialized = run_cli(
        "init", "--repository", str(repository), "--workspace", str(root / "workspace"),
        "--goal", "Prove a small theorem", "--title", "Small theorem", "--config-file", str(configuration),
        cwd=root)
    if initialized.returncode != 0:
        raise AssertionError(initialized.stdout + initialized.stderr)
    return response_body(initialized)


class CliTests(unittest.TestCase):
    def test_original_request_is_preserved_separately_from_the_mathematical_goal(self):
        from do_math.repository import ResearchRepository
        original='증명: n+0=n. 모델은 gpt-6-sol까지. 새 인스턴스.\n'
        path=self.root/'original.txt';path.write_bytes(original.encode('utf-8'))
        response=self.run_cli('init','--repository',str(self.repository),'--workspace',str(self.root/'second'),
            '--goal','n+0=n','--request-text-file',str(path),'--config-file',str(self.operator_disabled))
        self.assertEqual(response.returncode,0,response.stdout)
        _,instance,runtime=ResearchRepository(self.repository,response_body(response)['instance_id']).load()
        self.assertEqual(instance['lifecycle']['immutable_input']['text'],original)
        self.assertEqual(runtime['inputs'][0]['config']['goal'],'n+0=n')
        self.assertEqual(instance['lifecycle']['immutable_input']['sha256'],hashlib.sha256(original.encode()).hexdigest())

    def test_profile_selection_respects_the_role_floor_without_model_execution(self):
        response=self.run_cli('select-profile',*self.instance_args(),'--role','intent_interpretation')
        self.assertEqual(response.returncode,0,response.stdout)
        result=response_body(response)
        self.assertEqual(result['selection']['tier'],'high')
        self.assertEqual(result['profile']['id'],result['selection']['profile_ref']['id'])

    def test_resend_replays_its_receipt_until_an_opposite_control_intervenes(self):
        from do_math.engine import control
        args=['pause',*self.instance_args(),'--reason','audit2 pause']
        first=self.run_cli(*args)
        self.assertEqual(first.returncode,0,first.stdout)
        original=response_body(first)
        # The same command with no state change between replays the first receipt.
        again=self.run_cli(*args)
        self.assertEqual(again.returncode,0,again.stdout)
        self.assertEqual(json.loads(again.stdout)['request_id'],json.loads(first.stdout)['request_id'])
        self.assertEqual(response_body(again)['request_id'],original['request_id'])
        resumed=self.run_cli('resume',*self.instance_args(),'--reason','audit2 resume')
        self.assertEqual(resumed.returncode,0,resumed.stdout)
        self.assertNotEqual(original['snapshot'],response_body(resumed)['snapshot'])
        # After the resume the same pause is a new request that pauses again.
        repeated=self.run_cli(*args)
        self.assertEqual(repeated.returncode,0,repeated.stdout)
        result=response_body(repeated)
        self.assertNotEqual(result['request_id'],original['request_id'])
        self.assertEqual((result['effect'],result['status']),('applied','paused'))
        # Its resend, with no resume between, replays its receipt.
        direct=control(self.repository,self.instance,'pause',text='audit2 pause')
        self.assertEqual(direct['request_id'],result['request_id'])
        self.assertTrue(direct['replayed'])
        for field in ('effect','reason','status','snapshot','config'):
            self.assertEqual(direct[field],result[field],field)
        reapplied=self.run_cli(*args,'--idempotency-key','audit2 intentional reapply')
        receipt=response_body(reapplied)
        direct=control(self.repository,self.instance,'pause',text='audit2 pause',idempotency_key='audit2 intentional reapply')
        self.assertNotEqual(receipt['request_id'],original['request_id'])
        self.assertEqual(receipt['request_id'],direct['request_id'])
        self.assertEqual(receipt['snapshot'],direct['snapshot'])

    def test_source_identity_and_effect_use_one_read(self):
        from do_math import cli
        from do_math.engine import control
        from do_math.repository import ResearchRepository
        path=self.root/'raw-source.bin'; original=b'\xff\x00original\r\n'; changed=b'changed after read'
        path.write_bytes(original)
        read=Path.read_bytes; reads=[]
        def read_then_change(value):
            data=read(value)
            if value==path:
                reads.append(data)
                path.write_bytes(changed)
            return data
        output=io.StringIO()
        with patch.object(Path,'read_bytes',read_then_change),redirect_stdout(output):
            code=cli.main(['source',*self.instance_args(),'--file',str(path),'--name','raw.bin'])
        envelope=json.loads(output.getvalue())
        self.assertEqual(code,0,envelope)
        self.assertEqual(reads,[original])
        store=ResearchRepository(self.repository,self.instance);head,instance,_=store.load()
        entry=instance['sources'][-1]
        self.assertEqual(entry['name'],'raw.bin')
        self.assertEqual(entry['sha256'],hashlib.sha256(original).hexdigest())
        self.assertEqual(store.read(entry['path'],head),original)
        normalized={'name':'raw.bin','body_base64':base64.b64encode(original).decode('ascii'),
                    'sha256':hashlib.sha256(original).hexdigest(),'bytes':len(original)}
        direct=control(self.repository,self.instance,'source',config=normalized)
        self.assertEqual(direct['request_id'],envelope['request_id'])
        self.assertEqual(direct['snapshot'],envelope['result']['snapshot'])
        alternate=self.root/'same-bytes.bin';alternate.write_bytes(original)
        direct_file=control(self.repository,self.instance,'source',config={'path':str(alternate),'name':'raw.bin'})
        self.assertEqual(direct_file['request_id'],envelope['request_id'])
        repeated=self.run_cli('source',*self.instance_args(),'--file',str(alternate),'--name','raw.bin')
        self.assertEqual(repeated.returncode,0,repeated.stdout)
        self.assertEqual(response_body(repeated)['effect'],'applied')

    def test_pending_and_rejected_receipts_keep_their_meaning(self):
        from do_math.repository import ResearchRepository
        store=ResearchRepository(self.repository,self.instance)
        args=['pause',*self.instance_args(),'--reason','wait for writer']
        with store.writer_lock():
            pending=self.run_cli(*args)
        self.assertEqual(pending.returncode,0,pending.stdout)
        queued=response_body(pending)
        self.assertTrue(queued['accepted'])
        self.assertEqual(queued['effect'],'pending engine processing')
        self.assertNotIn('snapshot',queued)
        done=self.run_cli(*args)
        self.assertEqual(done.returncode,0,done.stdout)
        self.assertEqual(response_body(done)['request_id'],queued['request_id'])
        self.assertEqual(response_body(done)['effect'],'applied')
        # A well-formed request the engine refuses: the named environment does not exist.
        path=self.root/'rejected.json';path.write_text(json.dumps({'operation':'invalidate','env_id':'TE-missing'}),encoding='utf-8')
        rejected=self.run_cli('trust',*self.instance_args(),'--file',str(path))
        self.assertEqual(rejected.returncode,0,rejected.stdout)
        original=response_body(rejected)
        self.assertTrue(original['accepted'])
        self.assertEqual(original['effect'],'rejected')
        self.assertTrue(original['reason'])
        later=self.run_cli('resume',*self.instance_args(),'--reason','after rejected request')
        self.assertEqual(later.returncode,0,later.stdout)
        repeated=self.run_cli('trust',*self.instance_args(),'--file',str(path))
        self.assertEqual(repeated.returncode,0,repeated.stdout)
        for key in ('effect','reason','status','snapshot'):
            self.assertEqual(response_body(repeated)[key],original[key],key)

    def test_public_check_json_discovery_and_fixed_snapshot(self):
        result = self.run_cli('check', '--repository', str(self.repository), '--instance', self.instance)
        self.assertEqual(result.returncode, 0, result.stdout)
        value = json.loads(result.stdout)
        self.assertEqual(value['schema_version'], 5)
        self.assertEqual(value['command'], 'check')
        self.assertEqual(value['exit_code'], 0)
        self.assertEqual(value['result']['inspection']['status'], 'healthy')
        discovery = self.run_cli('--describe')
        self.assertEqual(discovery.returncode, 0, discovery.stdout)
        described = json.loads(discovery.stdout)['result']
        self.assertIn('check', described['commands'])
        # The discovery contract names the fields every actual envelope carries.
        self.assertEqual(set(described['response_fields'][:-1]), set(value) - {'result'})
        self.assertEqual(described['inspection_exit_codes'],
                         {'healthy': 0, 'degraded': 1, 'blocked': 1, 'incomplete': 1})
        request = self.root / 'command.json'
        request.write_text(json.dumps({'schema_version':5,'command':'check','payload':{
            'repository':str(self.repository),'instance':self.instance,'snapshot':self.initial['snapshot'],
            'kinds':['record_storage']}}),encoding='utf-8')
        response = self.run_cli('--request-file',str(request))
        self.assertEqual(response.returncode,0,response.stdout)
        data = json.loads(response.stdout)['result']
        self.assertEqual(data['snapshot'],self.initial['snapshot'])
        self.assertEqual(data['inspection']['requested_areas'],['record_storage'])
        unknown = self.run_cli('check',*self.instance_args(),'--snapshot',self.initial['snapshot'],'--kinds','not_registered')
        self.assertEqual(unknown.returncode,1,unknown.stdout)
        self.assertEqual(response_body(unknown)['inspection']['status'],'incomplete')
        historical = self.run_cli('status',*self.instance_args(),'--snapshot',self.initial['snapshot'],'--json')
        self.assertEqual(historical.returncode,0,historical.stdout)
        self.assertEqual(response_body(historical)['snapshot'],self.initial['snapshot'])
        # Before charter adoption the snapshot view shows the original input's goal, as live status does.
        self.assertEqual(response_body(historical)['goal'],'Prove a small theorem')
        # One projection: a stored snapshot has the live fields, and nothing observed on this host.
        from do_math.reporting import OBSERVED_FIELDS
        body = response_body(historical)
        self.assertEqual({field: body[field] for field in OBSERVED_FIELDS}, dict.fromkeys(OBSERVED_FIELDS))
        live = self.run_cli('status',*self.instance_args(),'--json')
        self.assertEqual(set(response_body(live)), set(body))

    def setUp(self) -> None:
        self.root, self.initial = restore_template(cli_instance)
        self.repository = self.root / "repository"
        self.workspace = self.root / "workspace"
        self.operator_disabled = self.root / "operator-disabled.json"
        self.instance = self.initial["instance_id"]

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return run_cli(*arguments, cwd=self.root)

    def instance_args(self) -> tuple[str, ...]:
        return ("--repository", str(self.repository), "--instance", self.instance)

    def test_help_and_input_error_exit_codes_are_structured(self) -> None:
        # Exit codes as the shell sees them: this test keeps the child process.
        def process(*arguments):
            return subprocess.run([sys.executable, str(ENTRYPOINT), *arguments], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, cwd=self.root)
        help_result = process("--help")
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("init", help_result.stdout)
        self.assertIn("request", help_result.stdout)
        invalid = process("init", "--repository", str(self.repository), "--workspace", str(self.workspace))
        self.assertEqual(invalid.returncode, 2)
        self.assertEqual(response_body(invalid)["kind"], "input_error")
        # The discovery contract publishes the exit code the shell actually saw.
        from do_math import cli
        described = cli.describe_commands(cli.build_parser())
        self.assertEqual(described["error_exit_codes"]["input_error"], invalid.returncode)
        self.assertEqual(described["request_fields"], list(described["request_schema"]["properties"]))

    def test_explicit_request_identity_replays_once_and_rejects_changed_payload(self):
        first = self.run_cli('input', *self.instance_args(), '--text', 'One request', '--request-id', 'UC-repeat')
        self.assertEqual(first.returncode, 0, first.stdout)
        second = self.run_cli('input', *self.instance_args(), '--text', 'One request', '--request-id', 'UC-repeat')
        self.assertEqual(second.returncode, 0, second.stdout)
        self.assertTrue(response_body(second)['replayed'])
        from do_math.repository import ResearchRepository
        _, _, runtime = ResearchRepository(self.repository, self.instance).load()
        self.assertEqual(runtime['processed_controls'].count('UC-repeat'), 1)
        conflict = self.run_cli('input', *self.instance_args(), '--text', 'Changed request', '--request-id', 'UC-repeat')
        self.assertEqual(conflict.returncode, 2, conflict.stdout)
        self.assertIn('different payload', response_body(conflict)['message'])

    def test_status_input_pause_and_configure_apply_without_running_model(self) -> None:
        status = self.run_cli("status", *self.instance_args(), "--json")
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        self.assertEqual(response_body(status)["status"], "initializing")

        incoming = self.run_cli("input", *self.instance_args(), "--text", "Use induction")
        self.assertEqual(incoming.returncode, 0, incoming.stdout + incoming.stderr)
        self.assertTrue(response_body(incoming)["accepted"])
        paused = self.run_cli("pause", *self.instance_args(), "--reason", "review inputs")
        self.assertEqual(paused.returncode, 0, paused.stdout + paused.stderr)
        self.assertEqual(response_body(paused)["status"], "paused")

        config_path = self.root / "config.json"
        config_path.write_text(json.dumps({"call_timeout_seconds": 4}), encoding="utf-8")
        configured = self.run_cli("configure", *self.instance_args(), "--config-file", str(config_path))
        self.assertEqual(configured.returncode, 0, configured.stdout + configured.stderr)
        self.assertEqual(response_body(configured)["config"]["call_timeout_seconds"], 4)


    def test_request_applies_a_maintenance_queue_entry_without_model_execution(self) -> None:
        requested = self.run_cli("request", *self.instance_args(), "--role", "maintenance", "--reason", "inspect state")
        self.assertEqual(requested.returncode, 0, requested.stdout + requested.stderr)
        result = response_body(requested)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["effect"], "applied")
        status = self.run_cli("status", *self.instance_args(), "--json")
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        self.assertGreaterEqual(response_body(status)["pending_actions"], 1)
        from do_math.repository import ResearchRepository
        _, _, runtime = ResearchRepository(self.repository, self.instance).load()
        self.assertIn('maintenance', [a['role'] for a in runtime['queue']])
        self.assertNotIn('research_preparation', [a['role'] for a in runtime['queue']])
        self.assertFalse(runtime["executions"], "request must not start a model execution")

    def test_retry_action_reaches_the_public_control_inbox_idempotently(self) -> None:
        first = self.run_cli("request", *self.instance_args(), "--retry-action", "AC-held",
                             "--request-id", "UC-retry-held")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertTrue(response_body(first)["accepted"])
        second = self.run_cli("request", *self.instance_args(), "--retry-action", "AC-held",
                              "--request-id", "UC-retry-held")
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertTrue(response_body(second)["replayed"])

    def test_query_read_export_and_check_use_a_fixed_repository_snapshot(self) -> None:
        records = self.run_cli("query", *self.instance_args(), "--limit", "1")
        self.assertEqual(records.returncode, 0, records.stdout + records.stderr)
        record_page = response_body(records)
        self.assertEqual(record_page['loaded'], len(record_page['items']))
        self.assertGreaterEqual(record_page['total'], record_page['loaded'])
        queried = self.run_cli("query", *self.instance_args(), "--files", "--prefix", "research/", "--text", "small", "--limit", "1")
        self.assertEqual(queried.returncode, 0, queried.stdout + queried.stderr)
        query = response_body(queried)
        self.assertGreaterEqual(query["total"], 1)
        from do_math.repository import ResearchRepository
        store = ResearchRepository(self.repository, self.instance)
        head, _, _ = store.load()
        path = store.list_files('research/', head)[0]
        read = self.run_cli("read", *self.instance_args(), "--path", path, '--snapshot', head)
        self.assertEqual(read.returncode, 0, read.stdout + read.stderr)
        self.assertEqual(response_body(read)["path"], path)
        self.assertEqual(response_body(read)['snapshot'], head)
        destination = self.root / "export"
        exported = self.run_cli("export", *self.instance_args(), "--destination", str(destination))
        self.assertEqual(exported.returncode, 0, exported.stdout + exported.stderr)
        self.assertEqual((destination / path).read_bytes(), store.read(path, head))
        self.assertFalse((destination / 'research/instance.json').exists())
        checked = self.run_cli("check", *self.instance_args())
        report = response_body(checked)
        self.assertEqual(checked.returncode, 0 if report['passed'] else 1, report)
        self.assertIn('areas', report.get('inspection', report))

    def test_create_repository_is_explicit_and_only_accepts_empty_directory(self) -> None:
        created = self.root / "created"
        result = self.run_cli(
            "init", "--create-repository", "--repository", str(created), "--workspace", str(self.root / "other-workspace"),
            "--goal", "A research goal", "--config-file", str(self.operator_disabled),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((created / ".git").exists())
        nonempty = self.root / "nonempty"
        nonempty.mkdir()
        (nonempty / "file.txt").write_text("x", encoding="utf-8")
        refused = self.run_cli(
            "init", "--create-repository", "--repository", str(nonempty), "--workspace", str(self.root / "third-workspace"),
            "--goal", "A research goal", "--config-file", str(self.operator_disabled),
        )
        self.assertEqual(refused.returncode, 2)


class CliBoundaryTests(unittest.TestCase):
    def test_retry_action_is_a_distinct_request_mode(self) -> None:
        from do_math import cli
        parser = cli.build_parser()
        instance_args = ("--repository", ".", "--instance", "RI-test")
        retry = parser.parse_args(("request", *instance_args, "--retry-action", "AC-held"))
        self.assertEqual(retry.retry_action, "AC-held")
        self.assertIsNone(retry.role)
        with self.assertRaises(cli.CliInputError):
            parser.parse_args(("request", *instance_args, "--role", "maintenance",
                               "--retry-action", "AC-held"))
        with self.assertRaises(cli.CliInputError):
            parser.parse_args(("request", *instance_args, "--role", "maintenance",
                               "--text", "inspect state"))
        schema = cli.describe_commands(parser, 'request')['commands']['request']['payload_schema']
        self.assertIn('reason', schema['properties'])
        self.assertNotIn('text', schema['properties'])
        with self.assertRaises(cli.CliInputError):
            cli._json_arguments(parser, {'schema_version': 5, 'command': 'request',
                'payload': {'repository': '.', 'instance': 'RI-test',
                            'role': 'maintenance', 'text': 'inspect state'}})

    def test_query_rejects_unused_filters_before_reading_in_both_interfaces(self):
        from do_math import cli
        base = ['query', '--repository', '.', '--instance', 'RI-test']
        cases = [
            (['--prefix', 'runtime/'], {'prefix': 'runtime/'}),
            (['--direction', 'incoming'], {'direction': 'incoming'}),
            (['--files', '--kind', 'grant'], {'files': True, 'kind': 'grant'}),
            (['--files', '--related-to', 'KN-one'], {'files': True, 'related_to': 'KN-one'}),
            (['--files', '--direction', 'both'], {'files': True, 'direction': 'both'}),
        ]
        for options, payload in cases:
            with self.subTest(options=options), patch.object(cli, 'ResearchRepository') as files, \
                    patch('do_math.cli.query_records') as records:
                with self.assertRaises(cli.CliInputError):
                    cli.execute(cli.build_parser().parse_args(base + options))
                with self.assertRaises(cli.CliInputError):
                    cli._json_arguments(cli.build_parser(), {
                        'schema_version': 5, 'command': 'query',
                        'payload': {'repository': '.', 'instance': 'RI-test', **payload}})
                files.assert_not_called()
                records.assert_not_called()

    def test_query_defaults_and_explicit_filters_reach_consumers_in_both_interfaces(self):
        from do_math import cli
        parser = cli.build_parser()
        base = ['query', '--repository', '.', '--instance', 'RI-test']
        for interface in ('cli', 'json'):
            def arguments(options, payload):
                if interface == 'cli':
                    return parser.parse_args(base + options)
                return cli._json_arguments(parser, {'schema_version': 5, 'command': 'query',
                    'payload': {'repository': '.', 'instance': 'RI-test', **payload}})
            with self.subTest(interface=interface), patch.object(cli, 'ResearchRepository') as files:
                files.return_value.query.return_value = {
                    'snapshot': 'fixed', 'items': [], 'total': 0, 'next_cursor': None, 'truncated': False}
                cli.execute(arguments(['--files'], {'files': True}))
                self.assertEqual(files.return_value.query.call_args.kwargs['prefix'], 'research/')
                cli.execute(arguments(['--files', '--prefix', 'runtime/'], {'files': True, 'prefix': 'runtime/'}))
                self.assertEqual(files.return_value.query.call_args.kwargs['prefix'], 'runtime/')
            with self.subTest(interface=interface), patch('do_math.cli.query_records', return_value={}) as records:
                cli.execute(arguments([], {}))
                self.assertEqual(records.call_args.kwargs['direction'], 'both')
                cli.execute(arguments(['--kind', 'knowledge', '--related-to', 'KN-one', '--direction', 'incoming'],
                    {'kind': 'knowledge', 'related_to': 'KN-one', 'direction': 'incoming'}))
                self.assertEqual(records.call_args.kwargs['kind'], 'knowledge')
                self.assertEqual(records.call_args.kwargs['related_to'], 'KN-one')
                self.assertEqual(records.call_args.kwargs['direction'], 'incoming')

    def test_json_string_values_preserve_leading_hyphens(self):
        from do_math import cli
        parser = cli.build_parser()
        for command, field in (('input', 'text'), ('pause', 'reason'), ('init', 'goal')):
            for value in ('--literal-user-text', '-P', '--', ''):
                with self.subTest(command=command, value=value):
                    payload = {'repository': '.', field: value}
                    payload.update({'workspace': '.'} if command == 'init' else {'instance': 'RI-test'})
                    args = cli._json_arguments(parser, {
                        'schema_version': 5, 'command': command, 'payload': payload})
                    self.assertEqual(getattr(args, field), value)
        args = cli._json_arguments(parser, {
            'schema_version': 5, 'command': 'init',
            'payload': {'repository': '.', 'workspace': '.', 'goal': 'P',
                        'source': ['--first.txt', '-second.txt']}})
        self.assertEqual(args.source, [Path('--first.txt'), Path('-second.txt')])

    def test_record_output_path_is_rejected_before_reading(self):
        from do_math import cli
        output = io.StringIO()
        with patch('do_math.cli.read_record') as read, redirect_stdout(output):
            code = cli.main(['read', '--repository', '.', '--instance', 'RI-test',
                             '--id', 'KN-test', '--output', 'unused.json'])
        self.assertEqual(code, 2)
        read.assert_not_called()
        self.assertEqual(json.loads(output.getvalue())['error']['message'],
                         '--output requires --path')
    def test_configure_receipt_does_not_reapply_scheduler(self):
        from do_math import cli
        with tempfile.TemporaryDirectory() as directory:
            configuration=Path(directory)/'configuration.json'
            configuration.write_text(json.dumps({'operator_enabled':False}),encoding='utf-8')
            for effect,replayed,expected in [('applied',True,'not_reapplied'),('rejected',False,'not_applied')]:
                with self.subTest(effect=effect):
                    receipt={'accepted':True,'request_id':'UC-test','effect':effect,'replayed':replayed,
                        'snapshot':'a'*40,'config':{'operator_enabled':False},'reason':'original receipt'}
                    output=io.StringIO()
                    with patch.object(cli,'_control',return_value=receipt),patch.object(cli,'_reconcile_operator',return_value={'status':'installed'}) as schedule,redirect_stdout(output):
                        code=cli.main(['configure','--repository','.','--instance','RI-test','--config-file',str(configuration)])
                    self.assertEqual(code,0,output.getvalue())
                    schedule.assert_not_called()
                    envelope=json.loads(output.getvalue())
                    self.assertEqual(envelope['result']['effect'],effect)
                    self.assertEqual(envelope['result']['operator_schedule']['status'],expected)

    def test_operator_effort_alone_leaves_the_schedule_untouched(self):
        # The recovery AI reads operator_effort from the recovery profile that configure rebuilds.
        from do_math import cli
        with tempfile.TemporaryDirectory() as directory:
            configuration=Path(directory)/'configuration.json'
            configuration.write_text(json.dumps({'operator_effort':'max'}),encoding='utf-8')
            receipt={'accepted':True,'request_id':'UC-test','effect':'applied','snapshot':'a'*40,
                     'config':{'operator_enabled':True,'operator_interval_seconds':7200,'operator_timeout_seconds':5400}}
            output=io.StringIO()
            with patch.object(cli,'_control',return_value=receipt),patch.object(cli,'_reconcile_operator',return_value={'status':'installed'}) as schedule,redirect_stdout(output):
                code=cli.main(['configure','--repository','.','--instance','RI-test','--config-file',str(configuration)])
            self.assertEqual(code,0,output.getvalue())
            schedule.assert_not_called()
            self.assertNotIn('operator_schedule',json.loads(output.getvalue())['result'])

    def test_common_request_rejects_malformed_identity_before_dispatch(self):
        from do_math import cli
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'request.json'
            base={'schema_version':5,'command':'pause','payload':{'repository':'.','instance':'RI-test'}}
            for changes in ({'request_id':False},{'request_id':''},{'idempotency_key':7},{'command':['pause']}):
                path.write_text(json.dumps({**base,**changes}),encoding='utf-8')
                output=io.StringIO()
                with patch.object(cli,'execute',return_value=({},0)) as dispatch, redirect_stdout(output):
                    code=cli.main(['--request-file',str(path)])
                self.assertEqual(code,2,output.getvalue())
                dispatch.assert_not_called()
                self.assertEqual(json.loads(output.getvalue())['error']['kind'],'input_error')

    def test_operator_origin_is_offered_only_where_control_admission_accepts_it(self):
        from do_math import cli
        from do_math.control_contracts import OPERATOR_ACTIONS
        parser = cli.build_parser()
        offered = {}
        for name, command in cli._command_parsers(parser).items():
            origin = next((action for action in command._actions if action.dest == 'origin'), None)
            if origin is not None:
                offered[name.replace('-', '_')] = 'operator' in origin.choices
        self.assertIn('decision', offered)
        self.assertEqual({name for name, operator in offered.items() if operator}, set(OPERATOR_ACTIONS))
        with self.assertRaises(cli.CliInputError):
            parser.parse_args(['decision', '--repository', '.', '--instance', 'RI-test',
                               '--file', 'unused.json', '--origin', 'operator'])

    def test_json_request_validates_types_and_preserves_common_error(self):
        from do_math import cli
        with tempfile.TemporaryDirectory() as directory:
            request=Path(directory)/'request.json'
            request.write_text(json.dumps({'schema_version':5,'command':'query','caller':'user',
                'payload':{'repository':'.','instance':'RI-test','limit':True}}),encoding='utf-8')
            output=io.StringIO()
            with redirect_stdout(output):
                code=cli.main(['--request-file',str(request)])
            result=json.loads(output.getvalue())
            self.assertEqual(code,2)
            self.assertEqual(result['command'],'query')
            self.assertIn('error',result)
            self.assertNotIn('result',result)
            self.assertEqual(result['error']['next_owner'],'user')

    def test_check_exit_uses_actual_inspection_status(self):
        from do_math import cli
        for status, expected in [('healthy',0),('incomplete',1),('blocked',1),('degraded',1)]:
            output = io.StringIO()
            with patch.object(cli, 'ResearchEngine') as engine, redirect_stdout(output):
                engine.return_value.check.return_value = {'inspection':{'status':status},
                    'passed':status != 'healthy','submission_checks':{'evidence':'preserved'}}
                code = cli.main(['check','--repository','.','--instance','RI-test',
                                 '--snapshot','a'*40,'--kinds','repair_iteration'])
                engine.return_value.check.assert_called_once_with(snapshot='a'*40,requested_areas=['repair_iteration'])
            self.assertEqual(code,expected)
            self.assertEqual(json.loads(output.getvalue())['result']['submission_checks'],{'evidence':'preserved'})

    def test_normalized_control_identity_at_public_boundary(self):
        # The CLI passes the command's identity inputs to ENGINE's control, which
        # derives the request ID (control_contracts.control_request_id), and reports
        # the ID control returns: the same command repeats one ID, a new key makes another.
        from do_math import cli
        from do_math.control_contracts import control_request_id
        forwarded, ids = [], []
        def admit(repository, instance, action, **kwargs):
            forwarded.append(kwargs)
            ids.append(kwargs['request_id'] or control_request_id(instance, action, text=kwargs['text'],
                config=kwargs['config'], origin=kwargs['origin'], idempotency_key=kwargs['idempotency_key']))
            return {'request_id': ids[-1], 'accepted': True}
        reported = []
        with patch.object(cli,'control',side_effect=admit), patch.object(cli,'ResearchEngine') as engine:
            engine.return_value.process_controls.return_value={'status':'paused','snapshot':'a'*40}
            engine.return_value.control_result.return_value=None
            engine.return_value.runtime={'history':[]}
            for extra in ([], [], ['--idempotency-key','again']):
                output = io.StringIO()
                with redirect_stdout(output):
                    code=cli.main(['pause','--repository','.','--instance','RI-test','--reason','P',*extra])
                self.assertEqual(code,0)
                reported.append(json.loads(output.getvalue())['request_id'])
        self.assertEqual([row['request_id'] for row in forwarded], [None, None, None])
        self.assertEqual([row['idempotency_key'] for row in forwarded], [None, None, 'again'])
        self.assertEqual(reported, ids)
        self.assertEqual(ids[0],ids[1])
        self.assertNotEqual(ids[0],ids[2])

    def test_runtime_failure_is_a_structured_internal_error(self):
        from do_math import cli
        output = io.StringIO()
        with patch.object(cli, 'execute', side_effect=RuntimeError('clock guard blocks new actions')), redirect_stdout(output):
            code = cli.main(['status', '--repository', '.', '--instance', 'RI-test'])
        result = json.loads(output.getvalue())
        self.assertEqual(code, 5)
        self.assertEqual(result['error']['kind'], 'contract_error')
        self.assertEqual(result['error']['next_owner'], 'maintenance')
        self.assertFalse(result['error']['retryable'])
        self.assertEqual(result['response_contract'], 'do-math-cli/5')

    def test_accepted_control_processing_failure_is_not_a_user_input_error(self):
        from do_math import cli
        from argparse import Namespace
        with patch.object(cli, 'control', return_value={'request_id': 'R-1'}), patch.object(cli, 'ResearchEngine') as engine:
            engine.return_value.process_controls.side_effect = ValueError('stale derived view: role_profile_refs')
            with self.assertRaisesRegex(RuntimeError, 'R-1.*stale derived view'):
                cli._control(Namespace(repository=Path('.'), instance='RI-test'), 'configure')


if __name__ == "__main__":
    unittest.main(verbosity=2)
