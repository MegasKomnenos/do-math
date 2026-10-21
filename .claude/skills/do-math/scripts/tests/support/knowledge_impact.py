"""Sealed impact reviews for the knowledge-impact tests, captured by the product's central capture on a real engine.

``review_fixtures.ImpactReviewHarness.seal_review_fixture`` captured a review
through ``core_engine._stage_submission_capture`` on a ``bare_engine`` whose
``_lifecycle_event`` was an autospec double, and the tests published the
artifacts to a real ``git`` repository. Here the capture runs on the product's
``ResearchEngine`` loaded from a small valid state on the port fakes, so its
``submission_checked`` event is recorded for real (on that engine, which the
review under test never reads), and the artifacts go to a ``GitStateStore`` on
the Git port's fake.

- ``seal_review(execution, output, fixed, workspace)``: install the submission
  tools for ``fixed``'s action in ``workspace``, seal ``output`` through
  ``submission.seal_submission`` (a failed seal fails at once, as the legacy
  fixture asserted), capture it centrally as an accepted explicit-tool
  submission, end ``execution`` as ``output_accepted`` with its submitted output
  reference, and return the artifacts to publish.
- ``fixture_store(root)``: a ``GitStateStore`` for the fixture instance on a new
  repository at ``root`` over the Git port's fake.
"""
from pathlib import Path

from do_math import contracts, submission
from do_math.canonical import canonical_json
from do_math.execution_lifecycle import transition_execution
from do_math.git_store import GitStateStore
from support.state_builders import current_state
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit, make_repository
from support.storage_records import INSTANCE_ID, engine_on, fake_ports, record_store


def seal_review(execution, output, fixed, workspace):
    from support.entry import entry
    _entry = entry()
    workspace = Path(workspace)
    schema = contracts.action_schema(fixed['action'])
    submission.install_tools(workspace, fixed, schema, None, clock=_entry.ports.clock)
    (workspace / 'draft.json').write_bytes(canonical_json(output))
    sealed = submission.seal_submission(workspace, 'draft.json', execution_id=execution['id'],
        context=fixed, schema=schema, max_artifact_bytes=1024 * 1024, clock=_entry.ports.clock)
    if not sealed['passed']:
        raise AssertionError('the impact review fixture did not seal: ' + repr(sealed['check']['issues']))
    host = _capture_engine(workspace.parent / (workspace.name + '-capture'))
    artifacts = host._stage_submission_capture(execution, sealed,
        {'id': host.ports.clock.new_id('CT'), 'kind': 'submit_intent', 'state': 'accepted', 'execution_id': execution['id'],
         'received_at': '2026-09-20T00:00:01Z'}, origin='explicit_tool')
    transition_execution(execution, 'ended', at='2026-09-20T00:00:02Z', outcome='output_accepted')
    execution['submitted_output_ref'] = execution['submission_intent']['output_ref']
    return artifacts


# One clock for every capture in the process: each capture names a new artifact bundle (``BA-``),
# so two reviews sealed into one repository never collide on an immutable bundle path.
_CAPTURE_CLOCK = FakeClock()


def _capture_engine(root):
    clock, backend = _CAPTURE_CLOCK, InProcessGit()
    instance, runtime = current_state(None, {'events': [], 'pending_events': []})
    engine, _ = engine_on(record_store(root / 'repository', backend=backend, clock=clock), instance, runtime,
                          workspace=root / 'work', ports=fake_ports(clock, backend))
    return engine


def fixture_store(root):
    make_repository(root)
    return GitStateStore(root, INSTANCE_ID, backend=InProcessGit(), clock=FakeClock())


from copy import deepcopy
import unittest
from do_math import knowledge_io


class ImpactCase(unittest.TestCase):
    def setUp(self):
        from support.entry import entry
        _entry = entry()
        from do_math import integration
        from do_math.knowledge import content_hash
        from support.record_builders import observation_knowledge, research_work_context, two_observation_output
        self.clock = _entry.ports.clock
        self.api = integration
        self.instance = knowledge_io.ensure_ontology({"knowledge": {}, "expositions": {}})
        self.runtime = {"executions": {
            "EX-producer": {"id": "EX-producer", "role": "research_work", "status": "running", "input_snapshot": "fixed-input"}}, "queue": []}
        self.ids = []
        for title in ("A", "B", "C"):
            self.instance, self.runtime, kid = knowledge_io.import_candidate(self.instance, self.runtime,
                observation_knowledge(title), source_ref="EX-producer", actor_ref="EX-producer", clock=_entry.ports.clock)
            self.ids.append(kid)
        self.output = two_observation_output()
        self.output["knowledge"] = []
        self.output["integration_bundles"] = [{"integration_id": "IN-held", "members": ["output",
            "activity-extensions.json/knowledge_changes/0", "activity-extensions.json/knowledge_changes/1"],
            "impact_set": [self.ids[1]], "authority_refs": [],
            "previous_hashes": {kid: content_hash(self.instance["knowledge"][kid]) for kid in (self.ids[0], self.ids[2])}}]
        self.extensions = {"knowledge_changes": [{"id": kid, "changes": {"summary": "Revised " + str(n)},
            "reason": "Correct explanation", "impact_set": [self.ids[1]]} for n, kid in enumerate((self.ids[0], self.ids[2]))]}
        self.bundle = next(self.api.split_bundles(self.output, self.extensions, research_work_context()))
        self.fixed_context = {**research_work_context(), 'knowledge_catalog': [
            {**deepcopy(self.instance['knowledge'][kid]), 'content_sha256': content_hash(self.instance['knowledge'][kid])}
            for kid in self.ids]}

    def request(self):
        return self.api.bundle_impact_request(self.instance, self.runtime, self.bundle,
            producer_execution_id="EX-producer", input_snapshot=self.runtime["executions"]["EX-producer"]["input_snapshot"])

    def review_output(self, request):
        return {"summary": "Independent impact assessment", "questions": [], "used_sources": [],
            "report": "Compared each declared scope with its computed dependencies and supplied premises.", "remaining_work": [],
            "impact_review": {key: deepcopy(request[key]) for key in
                ("integration_id", "payload_sha256", "producer_execution_id", "input_snapshot")} | {
                "plan_decisions": [{"scope": scope, "plan_digest": plan["digest"], "decision": "approve",
                    "affected_ids": sorted(set(plan["computed_impact"]) | set(plan["declared_impact"])),
                    "reason": "The declared additional scope must also be reassessed."} for scope, plan in request["plans"].items()]},
            "integration_bundles": [{"integration_id": "IN-review", "members": ["output"],
                                     "impact_set": [], "authority_refs": []}]}
