"""Explicit v5 inputs; all authority and persistence still pass through the engine.

The adapter/Lean facts below are synthetic test evidence. They do not establish
host capabilities, a real compiler result, or approval by the actual user.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from functools import wraps
import hashlib
import json
from pathlib import Path
import sys
import uuid
from unittest.mock import patch

from do_math.contracts import CONTRACT_REVIEW_ITEMS, ROLES
from do_math.control_transport import ControlTransport
from do_math.execution_profiles import profile_ref
from do_math.repository import canonical_json

IDENTITY = {"host": "CORE_TESTS synthetic host", "implementation": "CORE_TESTS synthetic adapter"}
AXIOMS = sorted(["propext", "Classical.choice", "Quot.sound"])


def read_fixture_context(prompt, workspace):
    """Read the same exact local sources exposed to the scripted role."""
    from do_math.context_store import read_source
    value = json.loads(prompt.split('--- CANONICAL INPUT CONTEXT ---\n', 1)[1].split('\n--- OUTPUT JSON SCHEMA ---', 1)[0])
    def read(reference):
        result = read_source(workspace, reference, limit=max(1, reference['bytes']))
        if result['status'] != 'ok' or result['truncated']:
            raise AssertionError('Supplied context source could not be read exactly: ' + repr(result))
        contents = json.loads(result['bytes'])
        for token in reference.get('json_pointer', '').strip('/').split('/') if reference.get('json_pointer') else []:
            contents = contents[int(token)] if isinstance(contents, list) else contents[token]
        return contents
    for key, entry in list(value.items()):
        if isinstance(entry, dict) and isinstance(entry.get('source_ref'), dict) and entry['source_ref'].get('path'):
            value[key] = read(entry['source_ref'])
    for index, task in enumerate(value.get('tasks', []) if isinstance(value.get('tasks'), list) else []):
        if isinstance(task.get('source_ref'), dict):
            task = value['tasks'][index] = {**task, **read(task['source_ref'])}
        for field in ('results', 'reviews', 'revision_history', 'assessment_history'):
            if task.get(field + '_source'):
                task[field] = read(task[field + '_source'])
    return value


def candidate(title="task", *, formal=False, revises=None, refs=None):
    return {"revises_task_id": revises, "title": title,
        "question": "Can the stated natural-number identity be established?",
        "scope": {"included": ["Natural numbers and addition of zero"], "excluded": ["Other domains"]},
        "expected": {"outputs": ["An argument or an explicit remaining obstacle"],
                     "research_change": "Resolve the stated zero-addition identity"},
        "progress_criteria": [{"id": "PC-argument", "claim": "Identify the argument and domain", "evidence_required": []}],
        "completion_obligations": [{"id": "OB-argument", "claim": "Report the exact argument and its domain",
                                     "judges": ["research_plan"], "evidence_required": []}],
        "inputs": list(refs or []), "reuse": list(refs or []), "dependencies": [],
        "profile_refs": [], "authority_refs": [], "basis_refs": [],
        "work_class": "formal" if formal else "nonformal"}


def bind_candidates(output, context):
    """Select only work profiles and current grants actually supplied to the author."""
    current = context.get("role_profile_refs", {}).get("research_work")
    for row in output.get("candidates", []):
        row["profile_refs"] = [profile_ref(p) for p in context["execution_profiles"]
                               if p["role"] == "research_work"
                               and (current is None or profile_ref(p) in current)]
        row["authority_refs"] = [g["id"] for g in context["grants"]
                                 if g["status"] == "active" and "research_work" in g.get("roles", [])]


def contract_review(context, *, decision="approved", findings=()):
    task = context["task"]
    if not task.get("completion_obligations") or not task.get("scope"):
        raise AssertionError("The review fixture requires the actual structured contract")
    return {"item_reviews": [{"item_id": item, "decision": decision,
        "evidence_refs": [task["id"]], "findings": list(findings),
        "missing_inputs": ["Contract clarification"] if decision == "unresolved" else [],
        "next_owner": "research_preparation"} for item in CONTRACT_REVIEW_ITEMS]}


def scope_response(context):
    review = context["role_review"]
    policy = review["review_policy"]
    perspectives = list(policy["required_perspectives"])
    for value in ("Statement and proof", "Explanation and domain"):
        if len(perspectives) < policy["minimum_initial_slots"]:
            perspectives.append(value)
    if len(perspectives) < policy["minimum_initial_slots"]:
        raise AssertionError("The explicit fixture only defines two independent perspectives")
    return {"proposal_digest": review["proposal_digest"], "scope_complete": True,
        "scope_assessment": {"assessment_id": "fixture-full-scope", "policy_id": policy["id"],
            "policy_version": policy["version"], "required_perspectives": list(policy["required_perspectives"]),
            "initial_slots": [{"id": "initial-" + str(i), "perspective": perspective,
                               "required_source_refs": ["proposal"]} for i, perspective in enumerate(perspectives)],
            "selected_profile_ref": profile_ref(context["execution_profile"]),
            "activity_execution_limit": policy["activity_execution_limit"],
            "overflow_disposition": policy["overflow_disposition"]}}


def disposition(task_id, *, kind="selected"):
    return {"task_id": task_id, "kind": kind, "reason": "Select the current independently approved contract",
        "uncertainty": "Completion of the contracted argument remains to be tested.",
        "parallel_task_ids": [], "expected_research_change": "Obtain the contracted argument",
        "revisit": {"event_refs": [], "at": None}, "missing_inputs": [], "next_owner": "research_work"}


def planning_model_assessments(output, context):
    tasks = {task['id']: task for task in context.get('tasks', [])}
    selected = [row['task_id'] for row in output.get('dispositions', []) if row.get('kind') == 'selected']
    assessments = []
    for task_id in selected:
        task = tasks.get(task_id)
        prior = task.get('model_assessment') if task else None
        if not prior:
            raise AssertionError('The planning fixture cannot assess a selected task without its supplied model assessment')
        assessments.append({'task_id': task_id, 'difficulty': prior['difficulty'],
            'importance': prior['importance'],
            'reason': 'The planner explicitly re-assesses the supplied bounded contract'})
    return assessments


def supply_observation_rules(candidates, extensions):
    """Declare an explicit checkpoint-counter policy for the scripted short task."""
    if not candidates:
        return
    conditions = extensions.setdefault('task_conditions', [])
    for candidate in candidates:
        row = next((item for item in conditions if item.get('task_title') == candidate['title']), None)
        if row is None:
            row = {'task_title': candidate['title']}
            conditions.append(row)
        row.setdefault('observation_rules', [{
            'id': 'fixture-attempts', 'operator': 'counter_gte',
            'subject': {'kind': 'counter', 'id': 'attempts'},
            'basis': {'source': 'checkpoint', 'unit': 'count'}, 'threshold': 10,
            'required_evidence': ['checkpoint.json']}])


def prepared_rule_conditions(task_ids):
    """Explicit response fixture for assigned existing-task rule preparation."""
    extensions = {}
    supply_observation_rules([{'title': tid} for tid in task_ids], extensions)
    return [{'task_id': row['task_title'], 'observation_rules': row['observation_rules']}
            for row in extensions.get('task_conditions', [])]


def assessment(task):
    reports = task.get("results", [])
    if not reports or not all(row.get("report") for row in reports):
        raise AssertionError("Completion fixture requires a supplied nonempty report")
    return {"task_id": task["id"], "decision": "completed", "reason": "The supplied report states the argument and domain",
        "item_dispositions": [{"obligation_id": row["id"], "kind": "fulfilled",
                               "evidence_refs": [r["execution_id"] for r in reports]}
                              for row in task["completion_obligations"]], "unresolved": []}


def intent_response(context):
    if context["action"].get("stage", "interpret") == "interpret":
        source = context["user_request"]
        return {"summary": "Preserve the supplied input verbatim for independent inspection",
            "used_sources": [], "questions": [], "needs_clarification": False, "question_details": [],
            "import_units": [{"unit_id": "IU-original", "source_range": {"start": 0, "end": len(source["text"])},
                "interpretation": source["text"], "owner_kind": "charter",
                "owner_ref": context["governance"]["charter"]["id"],
                "payload": {}, "decision_refs": [], "question_refs": []}]}
    bundle = context["interpretation_to_check"]
    source = bundle["source"]["text"]
    units = bundle["output"]["import_units"]
    if "".join(u["interpretation"] for u in units) != source:
        raise AssertionError("This fixture only approves verbatim, complete interpretation")
    return {"summary": "Independently compare supplied units with the exact original input",
        "used_sources": [], "questions": [], "decision": "approved", "scope_complete": True,
        "bundle_sha256": bundle["sha256"], "unit_ids": [u["unit_id"] for u in units],
        "question_ids": [q["id"] for q in bundle["output"]["question_details"]], "findings": []}


def seal_response(output, context, workspace):
    """Producer declares its real output/extension coordinates as one coupled unit."""
    from do_math.integration import mutation_members
    members = ["output"]
    role = context["action"]["role"]
    if role == 'research_preparation':
        from do_math.model_policy import preparation_only
        if not preparation_only(context['action']) and context.get('observed_at'):
            from datetime import datetime, timedelta
            output.setdefault('regenerate_after', (datetime.fromisoformat(context['observed_at'].replace('Z', '+00:00'))
                                                  + timedelta(hours=1)).isoformat())
    if role in {"research_work", "supplemental_research"} and not context["action"].get("review_cycle_id"):
        members += [f"output/{key}/{i}" for key in ("knowledge", "relations") for i, _ in enumerate(output.get(key, []))]
    path = workspace / "activity-extensions.json"
    extensions = json.loads(path.read_bytes()) if path.exists() else {}
    members += [f"activity-extensions.json/{family}/{i}" for family, rows in extensions.items() for i, _ in enumerate(rows)]
    identifier = "IN-" + hashlib.sha256(canonical_json({"action": context["action"], "output": output,
                                                       "extensions": extensions})).hexdigest()[:24]
    visible = {row["id"]: row for family in ("tasks", "knowledge_catalog")
               for row in context.get(family, []) if row.get("id")}
    mutation_ids = {target for _, _, target, _ in mutation_members(output, extensions)}
    previous_hashes = {}
    for target in mutation_ids:
        record = visible.get(target)
        if record is None or not record.get("content_sha256"):
            raise AssertionError("The fixture cannot revise a record absent from its fixed input: " + str(target))
        previous_hashes[target] = record["content_sha256"]
    output["integration_bundles"] = [{"integration_id": identifier, "members": members,
                                      "impact_set": [], "authority_refs": [],
                                      "previous_hashes": previous_hashes}]
    return output


def local_job_runner(method):
    """Give scripted model calls a real, bounded local process lifetime."""
    @wraps(method)
    def run(self, **arguments):
        callback = arguments["on_started"]
        if getattr(callback, "fixture_job", False):
            return method(self, **arguments)
        from do_math.windows_job import WindowsJob, process_identity
        job = None

        def started(_reported_identity=None):
            nonlocal job
            if job is not None:
                raise AssertionError("A scripted call must start exactly once")
            job = WindowsJob([sys.executable, "-c", "import time; time.sleep(600)"],
                             cwd=arguments.get("workspace"), name=arguments['launch_ticket']['job_name'])
            callback({**process_identity(job), "job_name": job.name})
            job.resume()

        started.fixture_job = True
        try:
            return method(self, **{**arguments, "on_started": started})
        finally:
            if job is not None:
                try:
                    job.terminate()
                    if not job.wait(10) or job.inspect().active_processes:
                        raise AssertionError("The fixture child did not terminate")
                finally:
                    job.close()
    return run


def dispatched_launch(execution_id, profile):
    """The current explicit runner contract used by native boundary fixtures."""
    from do_math.launch import ticket
    value = ticket(execution_id, profile)
    value['phase'] = 'dispatched'
    return value


def submit_intent(binding, should_stop, workspace, output):
    if binding is None:
        raise AssertionError("The engine must supply its real control transport")
    from do_math.submission import request_control
    (workspace / "output.json").write_bytes(canonical_json(output))
    delivery = request_control(workspace, "output.json", kind="submit_intent", wait_seconds=0, binding=binding)
    request_id = delivery["request_id"]
    should_stop()  # Pumps the actual engine receiver; does not create a receipt in the fixture.
    receipt = ControlTransport.worker_receipt(binding, request_id)
    if not receipt or receipt["state"] != "accepted":
        raise AssertionError("Submission intent did not receive engine acceptance: " + repr(receipt))


def producer_result(result, arguments):
    """Add only producer transport/envelope facts to a scenario's explicit response."""
    if result.get("status") == "completed" and isinstance(result.get("output"), dict):
        context = read_fixture_context(arguments["prompt"], arguments["workspace"])
        bind_candidates(result["output"], context)
        seal_response(result["output"], context, arguments["workspace"])
        submit_intent(arguments.get("control_binding"), arguments["should_stop"],
                      arguments["workspace"], result["output"])
    return result


class FixtureAdapter:
    def __init__(self, capabilities):
        self.capabilities = capabilities

    def capability_identity(self):
        return deepcopy(IDENTITY)

    def observation_key(self): return ('fixture',)

    def describe(self):
        return {"identity": deepcopy(IDENTITY), "verified": True,
            "scope": "synthetic_test_evidence_not_host_verification",
            "supported": dict(self.capabilities), "unknown": [],
            "version_sha256": "a" * 64, "exec_help_sha256": "b" * 64}


def install_adapter_fixture(test_case):
    """Replace only external observation; retain evidence hashing and capability gates."""
    def adapter(profile):
        return FixtureAdapter({"jsonl": True, "model": True, "structured_output": True})
    mocked = patch("do_math.initialization.adapter_for", side_effect=adapter)
    mocked.start()
    test_case.addCleanup(mocked.stop)


def validation_fixture(toolchain, inventory, source):
    """Explicit compiler double; never present this record as native validation."""
    from do_math.trust_inventory import validation_program
    from do_math.repository import exact_content_hash
    text,scope=validation_program(toolchain)
    return {'status':'verified','scope':scope,'source':str(source.resolve()),'source_text':text,
        'source_sha256':hashlib.sha256(text.encode()).hexdigest(),
        'command':[*toolchain['configured_command'],str(source.resolve())],
        'exit_code':0,'stdout':'synthetic external compiler result','stderr':'',
        'toolchain':deepcopy(toolchain),'toolchain_after':deepcopy(toolchain),
        'inventory_sha256':exact_content_hash(inventory),
        'started_at':'2026-09-20T00:00:00Z','finished_at':'2026-09-20T00:00:01Z'}


def trust_fixture(root, command):
    directory = root / "synthetic-trust"
    directory.mkdir(parents=True, exist_ok=True)
    from do_math.trust_inventory import SMOKE
    from do_math.repository import exact_content_hash
    files = []
    paths = {'lean_binary':'toolchain/bin/lean.exe', 'lean_source':'toolchain/src/Init/Prelude.lean',
             'lake_binary':'toolchain/bin/lake.exe', 'mathlib_source':'project/Mathlib.lean',
             'mathlib_build':'project/.lake/build/Mathlib.olean', 'checker':'checker/formal.py'}
    for role, relative in paths.items():
        path = directory / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = ("CORE_TESTS synthetic " + role).encode()
        path.write_bytes(raw)
        files.append({"role": role, "path": str(path.resolve()), "sha256": hashlib.sha256(raw).hexdigest()})
    by_role={row['role']:row for row in files}
    toolchain = {"executable": by_role['lean_binary']['path'], "sha256": by_role['lean_binary']['sha256'], "version": "Lean test 4.32.0",
                 "version_exit": 0, "configured_command": list(command),
                 "verifier_sha256": by_role['checker']['sha256'],
                 'verifier_path':by_role['checker']['path'],
                 "executables": {by_role[r]['path']:by_role[r]['sha256'] for r in ('lean_binary','lake_binary')},
                 "project": {'manifest_hashes':{}, 'fingerprint':{'root':str((directory/'project').resolve())},'search_paths':[]}}
    scope={'roots':[{'kind':kind,'path':str((directory/kind).resolve())} for kind in ('toolchain','project','checker')]}
    validation=validation_fixture(toolchain,{'scope':scope,'files':files},directory/'smoke.lean')
    manifest = {"command": list(command), "files": files,
        'scope':scope,
        "foundation_profile": {"allowed_axioms": AXIOMS, "forbidden": ["sorryAx", "Lean.trustCompiler", "additional_axioms"]},
        "validation": {'record':validation,'sha256':exact_content_hash(validation)}}
    return {"operation": "register", "toolchain": toolchain, "allowed_axioms": AXIOMS, "manifest": manifest}


def send_control(engine, action, **kwargs):
    from do_math.engine import control
    request = control(engine.store._store.repository, engine.instance["id"], action, **kwargs)
    engine.process_controls()
    rejected = [h for h in engine.runtime["history"] if h.get("kind") == "rejected_user_control"
                and h.get("request", {}).get("id") == request["request_id"]]
    if rejected:
        raise AssertionError("Public fixture control was rejected: " + repr(rejected))
    return request


def charter_change(engine, **content_changes):
    """Propose explicit changes to the actual current charter; approval stays public."""
    from do_math.repository import new_id
    current = engine._governance()["charter"]
    return {"kind": "charter", "record": {"id": new_id("CH"), "kind": "charter",
        "revision": current["revision"] + 1, "supersedes": [current["id"]],
        "content": {**deepcopy(current["content"]), **deepcopy(content_changes)}}}


def policy_change(engine, text):
    from do_math.repository import new_id
    return {"kind": "policy", "record": {"id": new_id("PO"), "kind": "policy", "revision": 1,
        "supersedes": [], "content": {"rule_id": "fixture-domain", "text": text,
            "scope": [engine._governance()["goal"]], "reason_refs": [engine._governance()["charter"]["id"]],
            "audit_refs": []}}}


def charter_record(goal):
    """Author explicit synthetic charter content; this grants no approval."""
    return {"id": "CH-fixture", "kind": "charter", "revision": 1, "supersedes": [],
        "content": {"rationale": "Exercise the explicit synthetic research scenario", "goal": goal,
            "desired_result": "A proof of the supplied mathematical goal", "success_criteria": [goal],
            "partial_success_criteria": ["Record an explicit unresolved obligation"],
            "included_scope": [goal], "excluded_scope": [], "priorities": ["Proof"], "preferences": [],
            "evidence_boundary": "Synthetic model and compiler inputs in a temporary repository",
            "academic_requirements": [], "decision_authority": "user", "stop_conditions": []}}


def activate(engine, root, *, initialization_runner, external_policy="disabled", review_policy=None):
    """Fill activation through public controls and two actual interpretation executions.

    The fixture supplies synthetic approval, trust, and capability observations.
    The engine applies lifecycle changes and checks the activation gates.
    """
    from do_math.engine import control
    # This fixture explicitly approves observation windows before adopting the
    # resulting profiles. Production deliberately has no implicit defaults.
    windows = {key: value for key, value in {
        "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5}.items()
        if key not in engine.instance["config"]}
    if windows:
        send_control(engine, "configure", config=windows)
    expiry = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    from do_math.execution_profiles import resolve_profile
    profiles = [resolve_profile(engine.instance['execution_profiles'], ref)
                for refs in engine.instance['role_profile_refs'].values() for ref in refs]
    profiles = [p for p in profiles if p['actor_kind'] == 'ai']
    from do_math.model_policy import selection
    initial_ref = selection(engine.instance["config"], {"role": "intent_interpretation"},
        {}, engine.instance["knowledge"],
        profiles=engine.instance["execution_profiles"])["profile_ref"]
    charter = charter_record(engine.instance["lifecycle"]["immutable_input"]["text"])
    controls = [("decision", {"change": {"kind": "initialization", "operation": "governance", "records": [charter]}}),
        ("decision", {"change": {"kind": "grant", "grant": {
        "id": "GR-initial-fixture", "kind": "local", "roles": ["intent_interpretation"],
        "budget_kind": "operations", "reuse": "reusable", "expires_at": expiry}}}),
        ("decision", {"change": {"kind": "grant", "grant": {"id": "GR-research-fixture",
        "kind": "local", "roles": list(ROLES) + ["formal_check"], "reuse": "reusable", "expires_at": expiry}}})]
    controls += [("decision", {"change": {"kind": "initialization", "operation": "probe",
                                         "profile_refs": [profile_ref(p) for p in profiles]}})]
    controls += [("trust", trust_fixture(root, engine.instance["config"]["lean_command"]))]
    for action, config in controls:
        control(engine.store._store.repository, engine.instance["id"], action,
            text="Synthetic CORE_TESTS input; not actual host verification or user approval", config=config)
    engine.process_controls()
    rejected = [h for h in engine.runtime["history"] if h.get("kind") == "rejected_user_control"]
    if rejected:
        raise AssertionError("Initialization controls rejected: " + repr(rejected))
    environment = next(iter(engine.instance["trust_environments"]))
    send_control(engine, "trust", config={"operation": "transition", "env_id": environment})
    send_control(engine, "decision", config={"change": {"kind": "initialization",
        "adopt_current_config": True, "adopt_current_governance": True,
        "conversation_loss_policy": "continue_authorized", "external_policy": external_policy,
        **({"review_policy": review_policy} if review_policy is not None else {"adopt_default_review_policy": True}),
        "profile_refs": [profile_ref(p) for p in profiles],
        "initial_profile_ref": initial_ref, "initial_grant_ids": ["GR-initial-fixture"],
        "research_grant_ids": ["GR-research-fixture"]}})
    previous = engine.runner
    engine.runner = initialization_runner
    try:
        engine.run(until_active=True)
        if engine.instance['lifecycle']['state'] != 'active':
            raise AssertionError("Public initialization did not reach active: " + repr({
                "activation": engine.instance["lifecycle"]["activation"],
                "status": engine.runtime["status"], "history": engine.runtime["history"][-3:]}))
    finally:
        engine.runner = previous
    return engine


def sealed_maintenance_submission(workspace, execution_id):
    """Create real central seal bytes for lifecycle/storage fixture assertions."""
    from do_math import contracts, submission
    workspace = Path(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    context = {'action': {'id': 'AC-fixture', 'role': 'maintenance'},
               'execution_id': execution_id, 'snapshot': 'fixture-input',
               'tasks': [], 'knowledge_catalog': [], 'sources': [], 'kind_definitions': {}}
    schema = contracts.schema_for('maintenance')
    submission.install_tools(workspace, context, schema, None)
    output = {'summary': 'Inspect fixture', 'used_sources': [], 'questions': [],
              'report': 'Explicit synthetic maintenance output.', 'remaining_work': []}
    seal_response(output, context, workspace)
    (workspace / 'draft.json').write_bytes(canonical_json(output))
    sealed = submission.seal_submission(workspace, 'draft.json', execution_id=execution_id,
        context=context, schema=schema, max_artifact_bytes=1024*1024)
    if not sealed['passed']:
        raise AssertionError(sealed['check']['issues'])
    prefix = 'runtime/artifacts/BA-fixture-submission/'
    return ({**sealed['intent'], 'output_ref': prefix + 'output.json'},
            {prefix + path: raw for path, raw in sealed['artifacts'].items()})


def scope_assessment(policy, slots):
    """Explicit synthetic full-proposal scope authored by the fixture reviewer."""
    return {"assessment_id": "fixture-full-proposal-scope", "policy_id": policy["id"],
        "policy_version": policy["version"], "required_perspectives": policy["required_perspectives"],
        "initial_slots": [{"id": slot, "perspective": slot, "required_source_refs": ["proposal"]} for slot in slots],
        "selected_profile_ref": None, "activity_execution_limit": policy["activity_execution_limit"],
        "overflow_disposition": policy["overflow_disposition"]}
