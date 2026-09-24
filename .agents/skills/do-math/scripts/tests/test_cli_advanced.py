from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from do_math import cli as cli_module
from do_math.engine import _repository as ResearchRepository

ENTRY = SCRIPTS / "do_math.py"


class AdvancedCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo, self.workspace = self.root / "repo", self.root / "workspace"
        configuration = self.root / "config.json"
        configuration.write_text(json.dumps({"operator_enabled": False}), encoding="utf-8")
        init = self.cli("init", "--create-repository", "--repository", str(self.repo),
                        "--workspace", str(self.workspace), "--goal", "Original goal",
                        "--config-file", str(configuration))
        self.assertEqual(init[0], 0, init)
        self.instance_id = init[1]["instance_id"]

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, *arguments):
        result = subprocess.run([sys.executable, str(ENTRY), *arguments], cwd=self.root,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        text = result.stdout.decode("utf-8", errors="replace").strip()
        envelope = json.loads(text) if text else None
        if envelope is not None:
            self.assertEqual(envelope['schema_version'], 5)
            self.assertEqual(envelope['exit_code'], result.returncode)
            self.assertNotEqual('result' in envelope, 'error' in envelope)
        return result.returncode, (envelope.get('result', envelope.get('error')) if envelope else None), result.stderr.decode("utf-8", errors="replace")

    def control(self, command, payload):
        path = self.root / f"{command}-{len(list(self.root.glob(command + '-*.json')))}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        result = self.cli(command, "--repository", str(self.repo), "--instance", self.instance_id,
                          "--file", str(path))
        self.assertEqual(result[0], 0, result)
        return result

    def load(self):
        return ResearchRepository(self.repo, self.instance_id).load()

    def charter(self, identifier='CH-1', supersedes=(), goal='New goal'):
        from test_redesign_SURFACE import surface_state
        instance, _ = surface_state()
        record = instance['governance']['CH-1']
        record = {k: record[k] for k in ('id', 'kind', 'revision', 'supersedes', 'content')}
        record.update(id=identifier, supersedes=list(supersedes), revision=1 if not supersedes else 2)
        record['content']['goal'] = goal
        return {'kind': 'charter', 'record': record}

    def test_goal_policy_grant_query_and_revoke(self):
        code, result, _ = self.control("decision", {'kind':'initialization','operation':'governance',
                                                   'records':[self.charter()['record']]})
        self.assertEqual((code, result["effect"]), (0, "applied"))
        code, result, _ = self.control("decision", {'kind': 'policy', 'record': {'id': 'PO-1', 'kind': 'policy',
            'revision': 1, 'supersedes': [], 'content': {'rule_id': 'no_publish', 'scope': ['P'],
            'text': 'New policy', 'reason_refs': ['CH-1'], 'audit_refs': []}}})
        self.assertEqual((code, result["effect"]), (0, "applied"))
        grant = {"kind": "grant", "grant": {"id": "HTTP", "kind": "http",
                 "allowed_origins": ["https://example.com"], "allowed_methods": ["GET"],
                 "allowed_path_prefixes": ["/"], "credential_env": {}}}
        self.assertEqual(self.control("decision", grant)[1]["effect"], "applied")
        query = self.cli("query", "--repository", str(self.repo), "--instance", self.instance_id, "--kind", "grant")
        self.assertEqual(query[0], 0); self.assertTrue(any(item["record"]["id"] == "HTTP" for item in query[1]["items"]))
        self.assertEqual(self.control("decision", {"kind": "revoke", "grant_id": "HTTP"})[1]["effect"], "applied")
        from do_math.governance import governance_view
        _, instance, _ = self.load(); self.assertEqual(governance_view(instance)['goal'], 'New goal'); self.assertEqual(governance_view(instance)['policy_records'][0]['content']['text'], 'New policy'); self.assertEqual(instance["grants"]["HTTP"]["status"], "revoked")

    def test_changed_decision_precondition_is_a_consumed_rejection(self):
        initial={'kind':'initialization','operation':'governance','records':[self.charter()['record']]}
        self.assertEqual(self.control('decision', initial)[1]['effect'], 'applied')
        self.assertEqual(self.control('decision', self.charter('CH-2', ['CH-1']))[1]['effect'], 'applied')
        code, result, _ = self.control('decision', self.charter('CH-stale', ['CH-1']))
        self.assertEqual(code, 0); self.assertEqual(result['effect'], 'rejected'); self.assertIn('active', result['reason'])

    def test_knowledge_invalidation_and_trust_registration(self):
        from do_math.knowledge_records import create_candidate
        from do_math.knowledge import plan_impact
        store = ResearchRepository(self.repo, self.instance_id); head, instance, runtime = store.load()
        base = {"kind": "conjecture", "title": "K", "statement": "s", "explanation": "e", "summary": "s",
                "lean_code": "", "declaration_names": [], "dependencies": []}
        instance, kid = create_candidate(instance, {**base, "id": "KN-1"}, source_ref="input-source", actor_ref="EX-author")
        instance, child = create_candidate(instance, {**base, "id": "KN-2", "dependencies": [kid]}, source_ref="input-source", actor_ref="EX-author")
        store.save_with_state(head, instance, runtime)[0]
        plan = plan_impact(instance, runtime, [kid], [])
        confirmation = {"plan_digest": plan["digest"], "decision": "approve", "review_ref": "review",
            "reviewer_ref": "reviewer", "producer_ref": "producer",
            "affected_ids": sorted(set(plan["computed_impact"]) | set(plan["declared_impact"]))}
        invalid = self.control("knowledge", {"operation": "invalidate", "id": kid, "reason": "withdrawn",
                                             "independent_confirmation": confirmation})
        self.assertEqual((invalid[0], invalid[1]["effect"]), (0, "applied"), invalid)
        _, instance, runtime = self.load()
        self.assertEqual(instance["knowledge"][kid]["lifecycle"], "withdrawn")
        self.assertIn(child, plan["computed_impact"])
        self.assertNotIn("formal", instance["knowledge"][kid])
        trust = self.control("trust", {"operation": "register", "toolchain": {"executable": "lean", "sha256": "abc"}, "allowed_axioms": []})
        self.assertEqual((trust[0], trust[1]["effect"]), (0, "rejected"), trust)
        self.assertIsNone(self.load()[1].get("active_trust_environment"))

    def test_external_prepare_is_model_free_and_conversation_lifecycle(self):
        policy=self.control('decision',{'kind':'initialization','operation':'adopt','external_policy':'explicit_grants'})
        self.assertEqual(policy[1]['effect'],'applied',policy)
        grant = {"kind": "grant", "grant": {"id": "HTTP", "kind": "http",
                 "allowed_origins": ["https://example.com"], "allowed_methods": ["GET"],
                 "allowed_path_prefixes": ["/"], "credential_env": {}}}
        self.control("decision", grant)
        prepared = self.control("external", {"operation": "prepare", "grant_id": "HTTP", "id": "OP",
            "request": {"method": "GET", "url": "https://example.com/read"}})
        self.assertEqual((prepared[0], prepared[1]["effect"]), (0, "applied")); self.assertEqual(self.load()[2]["external_operations"]["OP"]["status"], "prepared")
        attach = {"operation": "attach", "id": "C", "generation": 1, "disconnect_policy": "pause", "lease_seconds": 30}
        self.assertEqual(self.control("conversation", attach)[1]["effect"], "applied")
        self.assertEqual(self.control("conversation", {"operation": "heartbeat", "id": "C", "generation": 1})[1]["effect"], "applied")
        self.assertEqual(self.control("conversation", {"operation": "detach", "id": "C", "generation": 1})[1]["effect"], "applied")
        _, instance, runtime = self.load(); self.assertEqual(instance["conversation_loss_policy"], "pause"); self.assertEqual(runtime["conversations"]["C"]["status"], "lost")

    def test_source_import_preserves_raw_bytes_and_name(self):
        raw = b"\xff\x00source\r\n"; source = self.root / "raw.bin"; source.write_bytes(raw)
        code, result, _ = self.cli("source", "--repository", str(self.repo), "--instance", self.instance_id,
                                   "--file", str(source), "--name", "evidence.bin")
        self.assertEqual((code, result["effect"]), (0, "applied"))
        head, instance, _ = self.load(); record = instance["sources"][-1]
        self.assertEqual(record["name"], "evidence.bin"); self.assertEqual(record["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(ResearchRepository(self.repo, self.instance_id).read(record["path"], head), raw)
        repeated = self.cli("source", "--repository", str(self.repo), "--instance", self.instance_id,
                            "--file", str(source), "--name", "evidence.bin")
        self.assertEqual((repeated[0], repeated[1]["effect"]), (0, "applied"))

    def test_invalid_json_shape_and_missing_source_are_input_errors(self):
        path = self.root / "array.json"; path.write_text("[]", encoding="utf-8")
        bad = self.cli("decision", "--repository", str(self.repo), "--instance", self.instance_id, "--file", str(path))
        self.assertEqual(bad[0], 2); self.assertEqual(bad[1]["kind"], "input_error")
        missing = self.cli("source", "--repository", str(self.repo), "--instance", self.instance_id, "--file", str(self.root / "missing"))
        self.assertEqual(missing[0], 2); self.assertEqual(missing[1]["kind"], "input_error")

    def test_run_watch_is_forwarded_without_running_a_model(self):
        parser = cli_module.build_parser(); args = parser.parse_args(["run", "--repository", str(self.repo), "--instance", self.instance_id, "--watch"])
        engine = Mock(); engine.run.return_value = {"status": "waiting"}
        with patch.object(cli_module, "ResearchEngine", return_value=engine):
            value, code = cli_module.execute(args)
        self.assertEqual(code, 0); self.assertEqual(value["status"], "waiting"); engine.run.assert_called_once_with(max_steps=None, watch=True)

if __name__ == "__main__":
    unittest.main(verbosity=2)
