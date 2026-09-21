"""Run with Python's standard library; live service is checked separately."""
import copy
import importlib.util
import io
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "jev.py"
REQUEST = json.loads((HERE / "examples/request.json").read_text(encoding="utf-8"))
RESPONSE = {
    "model": "jev-test",
    "answers": {
        "refund_requested": {"type": "noul", "noul": 0.99},
        "department": {"type": "choice", "choice": "billing",
                       "probabilities": {"billing": 0.9, "delivery": 0.05, "other": 0.05},
                       "confidence": 0.8},
        "urgency": {"type": "score", "score": 0.2,
                    "legend": {"0": "none", "1": "soon", "2": "now"},
                    "probabilities": {"0": 0.8, "1": 0.2, "2": 0.0}, "confidence": 0.7},
    },
    "usage": {"input_tokens": 120, "output_tokens": 20},
}


class CliTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.exists(), "Jev CLI has not been implemented")

    def run_cli(self, *args, data=None, env=None):
        environment = dict(os.environ)
        environment.pop("TYPESAFE_API_KEY", None)
        environment.pop("TYPESAFE_DEFAULT_MODEL", None)
        environment.update(env or {})
        with tempfile.TemporaryDirectory(prefix="jev unrelated ") as cwd:
            return subprocess.run(
                [sys.executable, str(SCRIPT), *args], input=data, encoding="utf-8",
                capture_output=True, cwd=cwd, env=environment, timeout=15,
            )

    def test_file_and_stdin_preserve_structured_questions_from_other_cwd(self):
        for args, data in [(["--input", str(HERE / "examples/request.json")], None),
                           ([], "\ufeff" + json.dumps(REQUEST, ensure_ascii=False))]:
            with self.subTest(args=args):
                result = self.run_cli(*args, "--dry-run", data=data)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout), dict(REQUEST, model="jev-latest"))
                self.assertEqual(result.stderr, "")

    def test_separate_text_state_and_questions(self):
        with tempfile.TemporaryDirectory(prefix="jev 한글 ") as folder:
            questions = Path(folder) / "questions.json"
            questions.write_text(json.dumps(REQUEST["questions"]), encoding="utf-8-sig")
            result = self.run_cli("--state", "-", "--questions", str(questions),
                                  "--dry-run", data="새로운 문맥\n둘째 줄")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["state"], "새로운 문맥\n둘째 줄")

    def test_separate_json_state_and_model_precedence(self):
        with tempfile.TemporaryDirectory() as folder:
            questions = Path(folder) / "q.json"
            questions.write_text(json.dumps(REQUEST["questions"]), encoding="utf-8")
            result = self.run_cli("--state", "-", "--state-format", "json", "--questions",
                                  str(questions), "--model", "chosen", "--dry-run",
                                  data=json.dumps(REQUEST["state"]),
                                  env={"TYPESAFE_DEFAULT_MODEL": "environment"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["model"], "chosen")
        self.assertEqual(json.loads(result.stdout)["state"], REQUEST["state"])

    def test_invalid_inputs_do_not_emit_success(self):
        inputs = ['{"state":"x","state":"y","questions":{}}',
                  '{"state":NaN,"questions":{}}', '{"state":1e999,"questions":{}}',
                  '{"state":42,"questions":{}}', '{}', 'not json',
                  json.dumps(dict(REQUEST, typo=True))]
        for data in inputs:
            with self.subTest(data=data):
                result = self.run_cli("--dry-run", data=data)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertEqual(json.loads(result.stderr)["error"]["kind"], "input")

    def test_nullable_descriptions_arrays_and_model_defaults(self):
        payload = {"state": [{"text": "한국어"}], "model": "request-model", "questions": {
            "q": {"type": "choice", "instructions": ["고르세요", {"context": "추가"}],
                  "criteria": {"a": None, "b": ["설명", {"example": "나"}]}},
            "s": {"type": "score", "instructions": "정도", "criteria": [None, {"level": "높음"}]},
            "n": {"type": "noul", "instructions": None, "criteria": {"true": {"means": "예"}, "false": None}},
        }}
        result = self.run_cli("--dry-run", data=json.dumps(payload), env={"TYPESAFE_DEFAULT_MODEL": "environment-model"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), payload)
        del payload["model"]
        result = self.run_cli("--dry-run", data=json.dumps(payload), env={"TYPESAFE_DEFAULT_MODEL": "environment-model"})
        self.assertEqual(json.loads(result.stdout)["model"], "environment-model")

    def test_invalid_question_shapes(self):
        for question in [{"type": "score", "instructions": "x", "criteria": ["one"]},
                         {"type": "choice", "instructions": "x", "criteria": {}},
                         {"type": "noul", "instructions": "x", "criteria": {"yes": "x"}},
                         {"type": "unknown", "instructions": "x"},
                         {"type": "noul", "instruction": "typo"}]:
            with self.subTest(question=question):
                result = self.run_cli("--dry-run", data=json.dumps({"state": "x", "questions": {"q": question}}))
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(result.stdout, "")

    def test_missing_key_is_configuration_error(self):
        result = self.run_cli(data=json.dumps(REQUEST))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(json.loads(result.stderr)["error"]["kind"], "configuration")

    def test_conflicting_input_and_invalid_limits(self):
        for args in [["--input", "-", "--state", "-", "--questions", "-"],
                     ["--state", "-", "--questions", "-"],
                     ["--timeout", "nan"], ["--timeout", "0"], ["--retries", "-1"]]:
            with self.subTest(args=args):
                result = self.run_cli(*args, "--dry-run", data=json.dumps(REQUEST))
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertEqual(json.loads(result.stderr)["error"]["kind"], "input")


class TransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SCRIPT.exists():
            return
        spec = importlib.util.spec_from_file_location("jev", SCRIPT)
        cls.jev = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.jev)

    def setUp(self):
        self.assertTrue(SCRIPT.exists(), "Jev CLI has not been implemented")

    def http_error(self, status, headers=None, body=b'{"detail":"test failure"}'):
        return HTTPError("https://api.typesafe.ai/v1/systemone", status, "failure", headers or {}, io.BytesIO(body))

    def call(self, outcomes, retries=2):
        with patch.object(self.jev.urllib.request.OpenerDirector, "open", side_effect=outcomes) as opened, \
                patch.object(self.jev.time, "sleep") as slept:
            result = self.jev.evaluate(dict(REQUEST, model="jev-latest"), "test-secret", timeout=3, retries=retries)
        return result, opened, slept

    def test_wire_request_and_full_response(self):
        result, opened, _ = self.call([io.BytesIO(json.dumps(RESPONSE).encode())])
        self.assertEqual(result, RESPONSE)
        request = opened.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.typesafe.ai/v1/systemone")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-secret")
        self.assertEqual(json.loads(request.data), dict(REQUEST, model="jev-latest"))

    def test_retry_transient_http_failure(self):
        result, opened, slept = self.call([self.http_error(429, {"Retry-After": "0"}),
                                          io.BytesIO(json.dumps(RESPONSE).encode())])
        self.assertEqual(result, RESPONSE)
        self.assertEqual(opened.call_count, 2)
        self.assertEqual(slept.call_args.args[0], 0)

    def test_retries_are_bounded(self):
        with patch.object(self.jev.urllib.request.OpenerDirector, "open", side_effect=lambda *a, **k: self.http_error_raise()) as opened, \
                patch.object(self.jev.time, "sleep"):
            with self.assertRaises(self.jev.JevError) as raised:
                self.jev.evaluate(dict(REQUEST, model="jev-latest"), "test-secret", timeout=3, retries=2)
        self.assertEqual(opened.call_count, 3)
        self.assertEqual(raised.exception.kind, "http")

    def http_error_raise(self):
        raise self.http_error(529)

    def test_permanent_errors_and_connection_failures_are_not_retried(self):
        for error in [self.http_error(401), self.http_error(422), URLError("offline"), TimeoutError("slow")]:
            with self.subTest(error=error), patch.object(self.jev.urllib.request.OpenerDirector, "open", side_effect=error) as opened:
                with self.assertRaises(self.jev.JevError):
                    self.jev.evaluate(dict(REQUEST, model="jev-latest"), "test-secret", timeout=3, retries=2)
                self.assertEqual(opened.call_count, 1)

    def test_malformed_or_incomplete_success_is_failure(self):
        missing = copy.deepcopy(RESPONSE)
        del missing["answers"]["urgency"]
        invalid = copy.deepcopy(RESPONSE)
        invalid["answers"]["refund_requested"]["noul"] = True
        for body in [b"<html>bad gateway</html>", b"{}", json.dumps(missing).encode(), json.dumps(invalid).encode()]:
            with self.subTest(body=body):
                with self.assertRaises(self.jev.JevError) as raised:
                    self.call([io.BytesIO(body)])
                self.assertEqual(raised.exception.kind, "response")

    def test_extreme_service_number_is_a_response_error(self):
        invalid = copy.deepcopy(RESPONSE)
        invalid["answers"]["refund_requested"]["noul"] = 10 ** 400
        with self.assertRaises(self.jev.JevError) as raised:
            self.call([io.BytesIO(json.dumps(invalid).encode())])
        self.assertEqual(raised.exception.kind, "response")

    def test_interrupted_http_error_body_is_a_network_error(self):
        class InterruptedBody(io.BytesIO):
            def read(self, *args):
                raise self_error

        self_error = self.jev.http.client.IncompleteRead(b"partial")
        error = HTTPError("https://api.typesafe.ai/v1/systemone", 422, "failure", {}, InterruptedBody())
        with self.assertRaises(self.jev.JevError) as raised:
            self.call([error])
        self.assertEqual(raised.exception.kind, "network")

    def test_redirect_does_not_forward_credentials(self):
        handler = self.jev.NoRedirect()
        self.assertIsNone(handler.redirect_request(None, None, 307, "redirect", {}, "https://elsewhere.invalid"))

    def test_long_retry_after_stops_instead_of_retrying_early(self):
        with patch.object(self.jev.urllib.request.OpenerDirector, "open", side_effect=self.http_error(429, {"Retry-After": "120"})) as opened, \
                patch.object(self.jev.time, "sleep") as slept:
            with self.assertRaises(self.jev.JevError):
                self.jev.evaluate(dict(REQUEST, model="jev-latest"), "test-secret")
        self.assertEqual(opened.call_count, 1)
        slept.assert_not_called()

    def test_real_http_success_redirect_and_error_redaction(self):
        received = []
        scenario = {"status": 200}

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                received.append((self.path, self.headers.get("Authorization"), self.rfile.read(int(self.headers["Content-Length"]))))
                self.send_response(scenario["status"])
                if scenario["status"] == 307:
                    self.send_header("Location", "/leaked")
                self.end_headers()
                self.wfile.write(json.dumps(RESPONSE).encode() if scenario["status"] == 200 else b'{"detail":"test-secret"}')

        with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with patch.object(self.jev, "ENDPOINT", "http://127.0.0.1:" + str(server.server_port) + "/v1/systemone"):
                    self.assertEqual(self.jev.evaluate(dict(REQUEST, model="jev-latest"), "test-secret"), RESPONSE)
                    self.assertEqual(received[0][1], "Bearer test-secret")
                    self.assertEqual(json.loads(received[0][2])["state"], REQUEST["state"])
                    scenario["status"] = 307
                    with self.assertRaises(self.jev.JevError) as error:
                        self.jev.evaluate(dict(REQUEST, model="jev-latest"), "test-secret")
                    self.assertEqual(error.exception.status, 307)
                    self.assertEqual(len(received), 2)
                    scenario["status"] = 401
                    output, errors = io.StringIO(), io.StringIO()
                    with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-secret"}), \
                            patch.object(sys, "stdin", io.StringIO(json.dumps(REQUEST))), \
                            patch.object(sys, "stdout", output), patch.object(sys, "stderr", errors):
                        code = self.jev.main([])
                    self.assertEqual(code, 1)
                    self.assertEqual(output.getvalue(), "")
                    self.assertEqual(json.loads(errors.getvalue())["error"]["status"], 401)
                    self.assertNotIn("test-secret", errors.getvalue())
            finally:
                server.shutdown()
                thread.join()


if __name__ == "__main__":
    unittest.main()
