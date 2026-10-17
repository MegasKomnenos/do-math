"""The worker checkpoint (``observations``, layer 2): the read, its evidence, its preservation and its notices.

A checkpoint is ``checkpoint.json`` in the execution workspace. It is read
with the one checkpoint format rule (strict JSON in the storage value domain
that matches ``CHECKPOINT_SCHEMA``) and every evidence path it names must be a
preserved workspace file. The workspace is a real temporary folder; reads are
counted with a profile hook, so no product name is replaced.
"""
from support.observation_clock import scripted_clock
import json
from pathlib import Path
import tempfile
import unittest

import jsonschema

from do_math import observations
from do_math.canonical import canonical_json
from do_math.submission import _captured_checkpoint
from support.observation_inputs import Clock, observation_rule
from support.provider_probes import ObservedCalls, junction, settle

FIELDS = {"current_claim": "c", "evidence_paths": [], "attempts": [], "remaining_work": [], "next_step": "n",
          "progress_state": "working"}
MISSING_EVIDENCE = "ValueError: checkpoint evidence is unavailable or excluded from preservation: "


class CheckpointCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.ws = Path(temporary.name)

    def write(self, **changes):
        (self.ws / "checkpoint.json").write_text(json.dumps({**FIELDS, **changes}), encoding="utf-8")

    def read(self):
        from support.entry import entry
        _entry = entry()
        return observations.read_checkpoint(self.ws, clock=_entry.ports.clock)


class CheckpointReadTests(CheckpointCase):
    def test_repeated_checkpoint_reads_reuse_schema_but_recheck_value_and_evidence(self):
        self.write()
        validator = jsonschema.validators.validator_for(observations.CHECKPOINT_SCHEMA)
        with ObservedCalls(check_schema=validator.check_schema) as calls:
            for _ in range(20):
                self.assertEqual(self.read()["status"], "valid")
            self.write(progress_state="invented")
            invented = self.read()
            self.assertEqual(invented["status"], "invalid")
            self.assertIn("'invented' is not one of ['working', 'blocked', 'no_progress', 'ready_to_submit']",
                          invented["error"])
            self.write(evidence_paths=["proof.txt"])
            self.assertEqual(self.read(), {"status": "invalid", "error": MISSING_EVIDENCE + "proof.txt"})
            proof = self.ws / "proof.txt"
            proof.write_bytes(b"current evidence")
            self.assertEqual(self.read()["status"], "valid")
            proof.unlink()
            self.assertEqual(self.read(), {"status": "invalid", "error": MISSING_EVIDENCE + "proof.txt"})
        self.assertLessEqual(calls.count("check_schema"), 1)

    def test_live_polling_rereads_the_checkpoint_only_after_a_change(self):
        """The tracker skips a read only on a settled fingerprint of a valid read; an invalid read is read again."""
        from support.entry import entry
        _entry = entry()
        import os
        tracker = observations.ObservationTracker("E", self.ws, {"observation_rules": [observation_rule()],
            "self_check_response_window_seconds": 5, "tool_review_window_seconds": 60},  time_port=scripted_clock(Clock()))
        checkpoint = self.ws / "checkpoint.json"
        self.write(evidence_paths=["proof.txt"])
        # Fresh files are inside the racy window; age this one's times instead of shortening the window.
        settle(checkpoint)
        with ObservedCalls(read=observations.read_checkpoint) as reads:
            self.assertEqual(tracker._changed_checkpoint()["status"], "invalid")
            # An invalid read is not remembered: its named evidence may appear later.
            (self.ws / "proof.txt").write_bytes(b"evidence")
            self.assertEqual(tracker._changed_checkpoint()["status"], "valid")
            self.assertEqual(tracker._changed_checkpoint()["status"], "unchanged")
            self.assertEqual(reads.count("read"), 2)
            self.write(evidence_paths=["proof.txt"], next_step="later")
            later = checkpoint.stat().st_mtime_ns + 10 ** 9
            os.utime(checkpoint, ns=(later, later))
            self.assertEqual(tracker._changed_checkpoint()["status"], "valid")
            self.assertEqual(reads.count("read"), 3)

    def test_duplicate_checkpoint_keys_are_invalid_live_and_at_final_capture(self):
        from support.entry import entry
        _entry = entry()
        self.write(current_claim="last valid", counters={"attempts": 1})
        prior, _ = observations.preserve_checkpoint(self.ws, artifact_prefix="runtime/artifacts/prior", max_bytes=100000, clock=_entry.ports.clock)
        raw = (self.ws / "checkpoint.json").read_bytes()
        variants = [("current_claim", raw.replace(b'"current_claim": "last valid"',
                                                  b'"current_claim": "first", "current_claim": "last valid"')),
                    ("attempts", raw.replace(b'"attempts": 1', b'"attempts": 0, "attempts": 1'))]
        for key, malformed in variants:
            with self.subTest(key=key):
                reason = "ValueError: duplicate JSON key: " + key
                (self.ws / "checkpoint.json").write_bytes(malformed)
                self.assertEqual(self.read(), {"status": "invalid", "error": reason})
                self.assertEqual(_captured_checkpoint({"checkpoint.json": malformed}),
                                 {"status": "invalid", "error": reason})
                preserved, artifacts = observations.preserve_checkpoint(self.ws, previous=prior,
                    artifact_prefix="runtime/artifacts/final", max_bytes=100000, clock=_entry.ports.clock)
                self.assertEqual(preserved["sha256"], prior["sha256"])
                self.assertEqual(preserved["final_observation"]["checkpoint_status"], "invalid")
                self.assertEqual(artifacts, {})

    def test_checkpoint_rejects_numbers_outside_the_storage_value_domain(self):
        for changes, reason in (({"iteration": 1.0}, "JSON floating-point numbers are not permitted"),
                                ({"counters": {"attempts": 2.0}}, "JSON floating-point numbers are not permitted"),
                                ({"iteration": 2 ** 53}, "JSON integers must be safe integers")):
            with self.subTest(changes=changes):
                self.write(**changes)
                self.assertEqual(self.read(), {"status": "invalid", "error": "ValueError: " + reason})
        self.write(iteration=1, counters={"attempts": 2})
        checkpoint = self.read()
        self.assertEqual(checkpoint["status"], "valid")
        stored = observations.persistent_record(checkpoint, artifact_ref="runtime/artifacts/fixture/checkpoint.json")
        self.assertEqual(stored["value"]["iteration"], 1)
        self.assertEqual(stored["value"]["counters"], {"attempts": 2})

    def test_checkpoint_requires_available_preserved_evidence_paths(self):
        self.write(evidence_paths=["proof.txt"])
        self.assertEqual(self.read(), {"status": "invalid", "error": MISSING_EVIDENCE + "proof.txt"})
        (self.ws / "proof.txt").write_text("actual evidence", encoding="utf-8")
        self.assertEqual(self.read()["status"], "valid")
        (self.ws / ".scratch").mkdir()
        (self.ws / ".scratch/proof.txt").write_text("disposable", encoding="utf-8")
        self.write(evidence_paths=[".scratch/proof.txt"])
        self.assertEqual(self.read(), {"status": "invalid", "error": MISSING_EVIDENCE + ".scratch/proof.txt"})

    def test_checkpoint_is_refused_through_a_workspace_reparse_point(self):
        # The checkpoint obeys the workspace path rule (context_store.safe_path) like every other
        # workspace file: a junction on the path is refused even when it resolves back inside.
        from support.entry import entry
        _entry = entry()
        import os
        real, link = self.ws / "real", self.ws / "link"
        real.mkdir()
        (real / "checkpoint.json").write_text(json.dumps(FIELDS), encoding="utf-8")
        junction(link, real)
        self.assertTrue(os.path.isjunction(link) if os.name == "nt" else link.is_symlink())
        try:
            self.assertEqual(observations.read_checkpoint(real, clock=_entry.ports.clock)["status"], "valid")
            refused = observations.read_checkpoint(link, clock=_entry.ports.clock)
            self.assertEqual(refused["status"], "invalid")
            self.assertRegex(refused["error"], "reparse|symlink")
        finally:
            os.rmdir(link) if os.name == "nt" else link.unlink()  # Only the link, not its target.

    def test_invalid_partial_missing_checkpoint_and_stop_request(self):
        self.assertEqual(self.read(), {"status": "missing"})
        for raw, reason in ((b'\xff', "UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff"),
                            (b'{"current_claim":"partial"}', "ValidationError: 'evidence_paths' is a required property")):
            with self.subTest(raw=raw):
                (self.ws / "checkpoint.json").write_bytes(raw)
                refused = self.read()
                self.assertEqual(refused["status"], "invalid")
                self.assertTrue(refused["error"].startswith(reason), refused["error"])
        request = observations.request_checkpoint(self.ws, "stop", immediate=True, deadline="2026-01-01T00:00:00Z")
        self.assertIn("Do not start new research", request["instruction"])
        self.assertTrue((self.ws / ".control/stop-request.json").is_file())

    def test_checkpoint_record_requires_preserved_original_artifact(self):
        self.write()
        checkpoint = {"kind": "checkpoint", **self.read()}
        with self.assertRaisesRegex(ValueError, "artifact"):
            observations.persistent_record(checkpoint)
        preserved = observations.persistent_record(checkpoint, artifact_ref="ART-1")
        self.assertNotIn("raw", preserved)
        self.assertEqual(preserved["artifact_ref"], "ART-1")
        canonical_json(preserved)

    def test_oversized_live_checkpoint_is_refused_before_replacing_preserved_evidence(self):
        from support.entry import entry
        clock = entry().ports.clock
        self.write()
        previous, artifacts = observations.preserve_checkpoint(self.ws,
            artifact_prefix='runtime/artifacts/checkpoint-before', max_bytes=100000, clock=clock)
        raw = (self.ws / 'checkpoint.json').read_bytes()
        oversized = raw + b' ' * (observations.CHECKPOINT_MAX_BYTES + 1 - len(raw))
        (self.ws / 'checkpoint.json').write_bytes(oversized)
        self.assertEqual(self.read(), {
            'status': 'invalid', 'error': 'ValueError: checkpoint exceeds the 4 MiB record limit'})
        retained, added = observations.preserve_checkpoint(self.ws, previous=previous,
            artifact_prefix='runtime/artifacts/checkpoint-after', max_bytes=len(oversized), clock=clock)
        self.assertEqual(retained['sha256'], previous['sha256'])
        self.assertEqual(retained['artifact_ref'], previous['artifact_ref'])
        self.assertEqual(artifacts[previous['artifact_ref']], raw)
        self.assertEqual(added, {})
        self.assertEqual(retained['final_observation']['checkpoint_status'], 'invalid')
        self.assertEqual((self.ws / 'checkpoint.json').read_bytes(), oversized)


class CheckpointReminderTests(CheckpointCase):
    def test_reminder_is_once_and_does_not_replace_existing_feedback(self):
        self.assertTrue(observations.write_checkpoint_reminder(self.ws))
        first = (self.ws / ".control/observation-feedback.json").read_bytes()
        self.assertFalse(observations.write_checkpoint_reminder(self.ws))
        self.assertEqual((self.ws / ".control/observation-feedback.json").read_bytes(), first)
        value = json.loads(first)
        self.assertIn("current_claim", value["reason"])



class ConcurrentCheckpointTests(CheckpointCase):
    def test_live_read_reports_replacement_as_being_written(self):
        from support.engine_control import on_audit
        import os
        self.write(current_claim='before')
        path = self.ws / 'checkpoint.json'
        observed = []
        def replace_before_open(arguments):
            if not observed:
                observed.append(True)
                self.write(current_claim='a longer concurrent version')
        with on_audit('msvcrt.open_osfhandle', replace_before_open):
            self.assertEqual(self.read(), {'status': 'being_written'})
        current = self.read()
        self.assertEqual(current['status'], 'valid')
        self.assertEqual(current['value']['current_claim'], 'a longer concurrent version')

    def test_evidence_growth_after_stat_is_omitted_by_actual_bytes(self):
        from support.engine_control import on_audit
        import os
        evidence = self.ws / 'proof.bin'
        evidence.write_bytes(b'x')
        observed = []
        def grow_before_open(arguments):
            if os.path.abspath(arguments[0]) == str(evidence) and not observed:
                observed.append(True)
                evidence.write_bytes(b'grown evidence')
        with on_audit('open', grow_before_open):
            files, omitted = observations.capture_checkpoint_files(self.ws, {'evidence_paths': ['proof.bin']}, max_bytes=2)
        self.assertEqual(files, {})
        self.assertEqual(omitted, [{'path': 'proof.bin', 'reason': 'checkpoint evidence exceeds artifact byte limit'}])
        self.assertEqual(evidence.read_bytes(), b'grown evidence')


if __name__ == "__main__":
    unittest.main()
