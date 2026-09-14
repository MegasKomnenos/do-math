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
from do_math.repository import ResearchRepository

ENTRY = SCRIPTS / "do_math.py"


class AdvancedCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo, self.workspace = self.root / "repo", self.root / "workspace"
        init = self.cli("init", "--create-repository", "--repository", str(self.repo),
                        "--workspace", str(self.workspace), "--goal", "Original goal",
                        "--goal-kind", "research")
        self.assertEqual(init[0], 0, init)
        self.instance_id = init[1]["instance_id"]

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, *arguments):
        result = subprocess.run([sys.executable, str(ENTRY), *arguments], cwd=self.root,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        text = result.stdout.decode("utf-8", errors="replace").strip()
        return result.returncode, json.loads(text) if text else None, result.stderr.decode("utf-8", errors="replace")

    def control(self, command, payload):
        path = self.root / f"{command}-{len(list(self.root.glob(command + '-*.json')))}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return self.cli(command, "--repository", str(self.repo), "--instance", self.instance_id,
                        "--file", str(path))

    def load(self):
        return ResearchRepository(self.repo, self.instance_id).load()

    def test_goal_policy_grant_query_and_revoke(self):
        code, result, _ = self.control("decision", {"kind": "goal", "goal": "New goal", "expected_revision": 1})
        self.assertEqual((code, result["effect"]), (0, "applied"))
        code, result, _ = self.control("decision", {"kind": "policy", "text": "New policy", "expected_revision": 1})
        self.assertEqual((code, result["effect"]), (0, "applied"))
        grant = {"kind": "grant", "grant": {"id": "HTTP", "kind": "http",
                 "allowed_origins": ["https://example.com"], "allowed_methods": ["GET"],
                 "allowed_path_prefixes": ["/"], "credential_env": {}}}
        self.assertEqual(self.control("decision", grant)[1]["effect"], "applied")
        query = self.cli("query", "--repository", str(self.repo), "--instance", self.instance_id, "--kind", "grant")
        self.assertEqual(query[0], 0); self.assertTrue(any(item["record"]["id"] == "HTTP" for item in query[1]["items"]))
        self.assertEqual(self.control("decision", {"kind": "revoke", "grant_id": "HTTP"})[1]["effect"], "applied")
        _, instance, _ = self.load(); self.assertEqual(instance["goal_revision"], 2); self.assertEqual(instance["policy_revision"], 2); self.assertEqual(instance["grants"]["HTTP"]["status"], "revoked")

    def test_changed_decision_precondition_is_a_consumed_rejection(self):
        self.assertEqual(self.control("decision", {"kind": "goal", "goal": "First", "expected_revision": 1})[1]["effect"], "applied")
        code, result, _ = self.control("decision", {"kind": "goal", "goal": "Stale", "expected_revision": 1})
        self.assertEqual(code, 0); self.assertEqual(result["effect"], "rejected"); self.assertIn("revision", result["reason"])

    def test_knowledge_invalidation_and_trust_registration(self):
        store = ResearchRepository(self.repo, self.instance_id); head, instance, runtime = store.load()
        base = {"kind": "theorem", "title": "K", "statement": "s", "explanation": "e", "summary": "s",
                "lean_code": "", "declaration_names": [], "reviews": [], "formal": {}, "status": "verified"}
        instance["knowledge"] = {"KN-1": {**base, "id": "KN-1", "dependencies": []},
                                 "KN-2": {**base, "id": "KN-2", "dependencies": ["KN-1"]}}
        runtime["tasks"]["TK-1"] = {"id": "TK-1", "title": "t", "status": "completed",
            "dependencies": ["KN-2"], "inputs": [], "reuse": [], "results": [],
            "assessment": {"decision": "completed", "current": True}, "revision": 1, "completion_criteria": []}
        store.save(head, instance, runtime)
        invalid = self.control("knowledge", {"operation": "invalidate", "id": "KN-1", "reason": "withdrawn"})
        self.assertEqual((invalid[0], invalid[1]["effect"]), (0, "applied"))
        _, instance, runtime = self.load(); self.assertEqual(instance["knowledge"]["KN-1"]["status"], "withdrawn"); self.assertTrue(instance["knowledge"]["KN-2"]["use_suspended"])
        self.assertEqual(runtime["tasks"]["TK-1"]["status"], "completed"); self.assertFalse(runtime["tasks"]["TK-1"]["assessment"]["current"]); self.assertEqual(runtime["tasks"]["TK-1"]["assessment"]["invalidated_reason"], "withdrawn")
        trust = self.control("trust", {"operation": "register", "toolchain": {"executable": "lean", "sha256": "abc"}, "allowed_axioms": []})
        self.assertEqual((trust[0], trust[1]["effect"]), (0, "applied")); self.assertTrue(self.load()[1]["trust_environments"])

    def test_external_prepare_is_model_free_and_conversation_lifecycle(self):
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
