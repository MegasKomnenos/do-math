"""Preserve failed submissions and route accepted installation repairs."""
from __future__ import annotations

from .wait_rules import waiting_action
from .wait_rules import FAILED_ACTION_WAITS
import hashlib
import json
from copy import deepcopy
from pathlib import Path, PurePosixPath

from . import activities, operational_dispositions
from .git_store import GitStateStoreError
from .canonical import exact_content_hash


def installation_sha256(root):
    """Identity of the whole installed skill; unchanged files reuse their digests."""
    from .file_io import cached_sha256, installation_files
    return exact_content_hash({name: cached_sha256(path) for name, path in installation_files(root).items()})


def pending_installation_repair(runtime):
    rows = runtime.get('operational_dispositions', {}).values()
    for status in ('installation_repair_pending', 'installation_repair_waiting'):
        found = next((row for row in rows if row.get('status') == status), None)
        if found is not None:
            return found
    return None


def installation_failure(runtime, record):
    """Resolve a published independent diagnosis; a caller label is not authority."""
    current = runtime.get('operational_dispositions', {}).get(record.get('id'))
    reviewer = runtime.get('executions', {}).get(record.get('execution_id'), {})
    target = runtime.get('executions', {}).get(record.get('target_execution_id'), {})
    disposition = record.get('disposition', {})
    binding = record.get('result', {}).get('installation_repair', {})
    if (current != record or record.get('status') not in {'installation_repair_pending', 'installation_repair_waiting'}
            or reviewer.get('role') != 'operational_review' or reviewer.get('outcome') != 'output_accepted'
            or reviewer.get('status') != 'ended' or reviewer.get('action', {}).get('target') != target.get('id')
            or target.get('status') != 'ended' or not target.get('error')
            or disposition.get('kind') != 'repair' or disposition.get('meaning_preserving') is not True
            or not disposition.get('repair_target', '').startswith('installation:')
            or not binding.get('installation_sha256') or not binding.get('evidence_refs')):
        raise ValueError('installation repair requires a preserved accepted diagnosis of an ended failure')
    return {'kind': 'installation_defect', 'diagnosis_id': record['id'],
        'error': disposition['reason'], 'repair_target': disposition['repair_target'],
        'verification': disposition['verification'], 'target_execution_id': target['id'],
        'failure_sha256': exact_content_hash({'role': target.get('role'),
            'lineage': target.get('action', {}).get('lineage_id') or target.get('action', {}).get('id'),
            'target': target.get('action', {}).get('target'),
            'contract_sha256': target.get('contract_sha256'),
            'goal_revision': target.get('goal_revision'), 'policy_revision': target.get('policy_revision'),
            'decision_basis': target.get('decision_basis'),
            'issues': target.get('integration_result', {}).get('issues') or target['error']}),
        **{key: deepcopy(binding[key]) for key in ('installation_sha256', 'evidence_refs')}}


def validate_installation_target(disposition, target, root):
    if disposition.get('meaning_preserving') is not True:
        raise ValueError('installation repair cannot change research meaning or authority')
    root = Path(root)
    relative = disposition['repair_target'].removeprefix('installation:')
    path = PurePosixPath(relative)
    if (not relative or path.is_absolute() or path.as_posix() != relative
            or any(p in {'.', '..'} or ':' in p or '\\' in p for p in path.parts)
            or not (root / relative).is_file() or not (root / relative).resolve().is_relative_to(root.resolve())):
        raise ValueError('installation repair target must name an existing file inside the installed skill')
    if target.get('status') != 'ended' or not target.get('error'):
        raise ValueError('installation repair requires a preserved ended failure')
    refs = [target[key] for key in ('result_ref', 'submission_check_ref', 'submitted_output_ref') if target.get(key)]
    if not refs:
        raise ValueError('installation defect has no preserved failure artifacts')
    return refs


def resume_installation_repair(runtime, record, *, repaired_by, at):
    """Resume the preserved rejected response, retaining its repair lineage."""
    target_id = record['target_execution_id']
    successor=activities.successor_state(runtime,target_id)
    if successor is not None:
        record['status']='applied'
        record.setdefault('result',{}).setdefault('installation_repair',{}).update(
            status='repaired',repaired_by=repaired_by,successor=successor)
        runtime['executions'][target_id].pop('pending_operational_disposition',None)
        runtime['status']='ready'
        return None
    target = runtime['executions'][target_id]
    previous = runtime.get('waiting_actions', {}).get(target['action']['id'])
    action = activities.continue_activity(runtime, target_id, at=at,
        reason='verified_installation_repair:' + record['id'])
    if previous and previous.get('execution_id') == target_id:
        # The waiting request owns the latest returned bundles and error report.
        action.update(deepcopy(previous['action']), continuation_of=target_id,
                      owner_activity_id=target['owner_activity_id'])
        runtime['waiting_actions'].pop(target['action']['id'], None)
    record['status'] = 'applied'
    record.setdefault('result', {})['installation_repair'].update(
        status='repaired', repaired_by=repaired_by, continuation_action_id=action['id'])
    target.pop('pending_operational_disposition', None)
    runtime['status'] = 'ready'
    return action


class RepairExecutionMixin:
    """Engine methods that route failed submissions and installation repairs."""

    def route_failed_action(self, action, execution_id, *, reason):
        """Choose a diagnosis allowed in the current lifecycle, without recursion."""
        wait = self.runtime['waiting_actions'][action['id']]
        if self.instance.get('lifecycle', {}).get('state') == 'initializing':
            wait['next_owner'] = 'maintenance'
            if action['role'] == 'intent_interpretation' and not action.get('diagnosis_attempt'):
                self._enqueue('maintenance', execution_id, initial_submission_diagnosis=True, reason=reason)
            return
        wait['next_owner'] = 'operational_review'
        if action['role'] != 'operational_review':
            self._enqueue('operational_review', execution_id, reason=reason)

    def route_submission_return(self, action, received, execution_id, output, *, rejected_submission=None):
        """Keep a bounded producer repair, then diagnose the preserved actual error."""
        retry = {**deepcopy(action), 'continuation_of': execution_id,
            'repair_attempt': action.get('repair_attempt', 0) + 1,
            'repair': {'execution_id': execution_id, 'previous_output': output,
                'retry_bundle_ids': received['retry_bundle_ids'],
                'bundle_results': received['bundles'], 'issues': received['issues']}}
        if rejected_submission:
            retry['repair'].update(deepcopy(rejected_submission))
        if retry['repair_attempt'] <= self.instance['config']['max_output_repairs'] and not action.get('diagnosis_attempt'):
            self.runtime.get('waiting_actions', {}).pop(action['id'], None)
            self.runtime['queue'].append(retry)
            return
        self.runtime.setdefault('waiting_actions', {})[action['id']] = waiting_action({
            'action': retry, 'kind': 'output_validation', 'execution_id': execution_id,
            'reason': 'Producer repair was rejected again; diagnose the preserved contract and receiver errors',
            'detail': {'issues': deepcopy(received['issues'])}})
        self.route_failed_action(action, execution_id,
            reason='Bounded submission repair exhausted; distinguish producer, input, contract and installation defects')

    def initial_diagnosis_input(self, action):
        if self.instance['lifecycle']['state'] != 'initializing':
            raise ValueError('initial submission diagnosis requires initialization')
        execution = self.runtime['executions'].get(action.get('target'), {})
        if execution.get('role') != 'intent_interpretation' or execution.get('status') != 'ended':
            raise ValueError('initial diagnosis must identify an ended interpretation')
        wait = self.runtime.get('waiting_actions', {}).get(execution['action']['id'])
        if not wait or wait.get('kind') not in FAILED_ACTION_WAITS or wait.get('execution_id') != execution['id']:
            raise ValueError('initial diagnosis no longer owns this failure')
        self._validate_initial_retry(wait, diagnostic_action_id=action.get('id'))
        return execution, wait

    def apply_initial_diagnosis(self, action, output, execution_id):
        failed, wait = self.initial_diagnosis_input(action)
        decision = output['initial_submission_diagnosis']
        if not decision['guidance'].strip():
            raise ValueError('initial diagnosis requires concrete repair or waiting guidance')
        wait['diagnosis'] = {'execution_id': execution_id, **deepcopy(decision)}
        if decision['decision'] == 'wait':
            wait.update(reason=decision['guidance'], next_owner='maintenance')
            return
        if decision['decision'] != 'retry' or wait['action'].get('diagnosis_attempt'):
            raise ValueError('initial diagnosis allows one bounded follow-up, not repeated automatic diagnosis')
        # This runs inside an integration candidate. Native-final recovery publishes
        # evidence, so only the owner may continue after this diagnosis is committed.
        wait['next_owner'] = 'engine'

    def continue_initial_retries(self):
        if (self.instance.get('lifecycle', {}).get('state') != 'initializing'
                or self.runtime.get('status') == 'paused' or self._instance_closed()
                or self.runtime.get('user_pause')):
            return
        for identifier in list(self.runtime.get('waiting_actions', {})):
            wait = self.runtime['waiting_actions'].get(identifier)
            if not wait:
                continue
            diagnosis = wait.get('diagnosis', {})
            reviewer = self.runtime['executions'].get(diagnosis.get('execution_id'), {})
            if (diagnosis.get('decision') != 'retry' or diagnosis.get('retry_error')
                    or reviewer.get('role') != 'maintenance' or reviewer.get('status') != 'ended'
                    or reviewer.get('outcome') != 'output_accepted'
                    or reviewer.get('action', {}).get('target') != wait.get('execution_id')
                    or not reviewer.get('action', {}).get('initial_submission_diagnosis')):
                continue
            try:
                self._continue_initial_execution(wait, request_id=reviewer['id'], diagnosis=diagnosis)
            except (ValueError, OSError, GitStateStoreError) as error:
                current = self.runtime.get('waiting_actions', {}).get(identifier)
                if current:
                    current['diagnosis']['retry_error'] = str(error)
                    current.update(next_owner='maintenance', reason=str(error))
            self._save()

    def request_installation_repair(self, record):
        disposition = record['disposition']
        root = Path(__file__).resolve().parents[2]
        target = self.runtime['executions'][record['target_execution_id']]
        refs = validate_installation_target(disposition, target, root)
        record['status'] = 'installation_repair_pending'
        record.setdefault('result', {})['installation_repair'] = {
            'installation_sha256': installation_sha256(root), 'evidence_refs': refs}
        self.runtime['operational_dispositions'][record['id']] = record
        self._save()
        return deepcopy(self.runtime['operational_dispositions'][record['id']])

    def complete_repair(self, record):
        """Hand the current installation diagnosis to the existing recovery owner."""
        identifier = record["id"]
        current = self.runtime.get("operational_dispositions", {}).get(identifier)
        if current is None or current != record:
            raise ValueError("repair must consume the current authoritative OD record")
        record = deepcopy(current)
        disposition = operational_dispositions.validate_disposition(record["disposition"])
        if disposition["kind"] != "repair":
            raise ValueError("complete_repair only consumes repair dispositions")
        if record['status'] in {'installation_repair_pending', 'installation_repair_waiting', 'applied'}:
            return record
        return self.request_installation_repair(record)


# Judgments of the failure-only installation recovery (``scheduled_operator.recovery``);
# it holds the locks, runs the recovery AI and writes the evidence.

def check_recovery_failure(failure) -> None:
    """A given failure must be preserved engine-failure or installation-defect evidence with its error."""
    if failure is not None and (failure.get("kind") not in {"engine_unavailable", "installation_defect"}
                                or not failure.get("error")):
        raise ValueError("recovery requires preserved engine failure evidence")


def recovery_block_outcome(block, failure) -> dict | None:
    """The result when supervision blocks a recovery (disabled, or any block but an installation repair), else None."""
    if block == 'disabled':
        return {"outcome": "recovery_disabled", "failure": failure}
    if block not in {None, 'installation_repair'}:
        return {"outcome": "held"}
    return None


def failure_to_repair(runtime: dict, failure):
    """The failure this recovery repairs: the given one, else the pending installation repair's; None when none is pending."""
    if failure is not None:
        return failure
    pending = pending_installation_repair(runtime)
    return None if pending is None else installation_failure(runtime, pending)


def matching_diagnosis(runtime: dict, failure: dict):
    """The published diagnosis of an installation defect; it must describe exactly this failure."""
    diagnosis = None
    if failure['kind'] == 'installation_defect':
        diagnosis = runtime.get('operational_dispositions', {}).get(failure.get('diagnosis_id'))
        if diagnosis is None or installation_failure(runtime, diagnosis) != failure:
            raise ValueError('installation diagnosis is missing or differs from its published record')
    return diagnosis


def unconfirmed_termination(runtime: dict, *, jobs):
    """The first unended execution whose local termination is not confirmed, or None.

    ``jobs`` is the Jobs port; without it the migration default asks the real
    Windows Jobs (the recovery path receives the port in 1d).
    """
    from .launch import termination_confirmed
    for execution in runtime.get("executions", {}).values():
        if execution.get("status") == "ended":
            continue
        if not execution.get('launch_ticket') or not termination_confirmed(execution['launch_ticket'], recovering=True,
                                                                           jobs=jobs):
            return execution["id"]
    return None


RECOVERY_FAILURE_FIELDS = ('kind', 'diagnosis_id', 'error', 'repair_target', 'verification',
                           'target_execution_id', 'evidence_refs', 'installation_sha256', 'evidence_path',
                           'engine_run_directory')


def failure_identity(failure: dict, diagnosis) -> str:
    """The identity of an actual failure: a diagnosis's recorded hash, else the hash of the failure's identifying fields."""
    if diagnosis:
        return failure['failure_sha256']
    return hashlib.sha256(json.dumps({key: failure[key] for key in RECOVERY_FAILURE_FIELDS if key in failure},
        ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


def already_attempted(runtime: dict, failure_sha256: str, installation_sha256: str) -> bool:
    """One automatic repair per actual failure and installation edition.

    A call that judged no repair does not count: the provider limit refused it,
    or a HOLD, pause or close held it before its repair report was received. A
    held call with a received report still counts. The provider gate and the
    supervision blocks pace a retry.
    """
    def attempted(execution):
        disposition = execution.get('result_disposition')
        recovery = disposition.get('recovery') if isinstance(disposition, dict) else None
        unjudged = (recovery == 'recovery_provider_limited'
                    or (recovery == 'recovery_held' and not execution.get('submission_receipt')))
        return (execution.get('role') == 'recovery'
                and execution.get('input_manifest', {}).get('repair_identity') == {
                    'failure_sha256': failure_sha256, 'installation_sha256': installation_sha256}
                and not unjudged)
    return any(attempted(e) for e in runtime.get('executions', {}).values())


def repair_prompt(failure: dict, failure_inputs: list, *, diagnosed: bool, installation, repository, instance: str,
                  execution_id: str, reference) -> str:
    """The recovery AI's instruction and its failure record, before the profile's prompt preparation."""
    return (
        ("Repair only the independently diagnosed do-math installation defect that blocks the preserved submission. "
         if diagnosed else "Repair only the do-math installation defect that prevents this engine from starting. ")
        + "Reproduce the recorded failure, make the smallest code repair, and run relevant checks. "
        "Preserve failure evidence, verification commands and changed file paths in your report. "
        "For a diagnosed submission defect, report repair_outcome=repaired only after reproducing and fixing it; "
        "otherwise report unresolved. Write regression logs inside this workspace and list their relative paths in verification_evidence. "
        "Do not change research records, goals, budgets, grants, user configuration or scheduled tasks. "
        "Do not start the engine or wait for research: the launcher owns restart after releasing its lock. "
        "Existing installation-repair approval applies; a new research or external-action authority does not.\n"
        + json.dumps({"failure": failure, "failure_inputs": failure_inputs,
                      "installation": str(installation), "repository": str(repository),
                      "instance": instance, "execution_id": execution_id, "profile_ref": reference}, ensure_ascii=False))


def runner_outcome(result: dict) -> str:
    """The recovery outcome the runner's result gives before verification and holds."""
    outcome = "repaired" if result.get("status") == "completed" else "recovery_failed"
    if result.get("error_kind") == "provider_limit":
        outcome = "recovery_provider_limited"
    return outcome


def recovery_report_receipt(execution_id: str, *, evidence_ref: str, observed_at: str) -> dict:
    """The receipt of a structured recovery report; it is not a research integration."""
    from .execution_lifecycle import RECOVERY_REPORT_RECEIPT
    return {"kind": RECOVERY_REPORT_RECEIPT, "state": "accepted", "execution_id": execution_id,
            "receiver": "recovery_launcher", "observed_at": observed_at,
            "evidence_ref": evidence_ref,
            "scope": "structured_recovery_report_not_research_integration"}


def recovery_held(held: bool, state: dict, runtime: dict) -> bool:
    """A HOLD marker, a pause or an ended instance holds the recovery's outcome."""
    from .planning import instance_ended
    return bool(held or runtime.get('user_pause') or runtime.get('status') == 'paused'
                or instance_ended(state, runtime))


def record_recovery_attempt(runtime: dict, execution: dict, *, activity_id: str, owner: dict, outcome: str,
                            diagnosis, execution_id: str, at: str) -> None:
    """End a released recovery execution, settle its activity and record the attempt on its diagnosis."""
    from . import activities, execution_lifecycle
    execution_lifecycle.transition_execution(execution, "stopping", at=at, reason=outcome)
    execution_lifecycle.transition_execution(execution, "ended", at=at,
        outcome="output_accepted" if execution.get("submission_receipt") else "execution_incomplete",
        disposition={"recovery": outcome})
    if outcome == "repaired":
        activities.finish_activity(runtime, activity_id, result_refs=[execution_id], unresolved=[], followups=[], at=at)
    else:
        activities.wait_for(runtime, activity_id, reason=outcome,
            condition={"kind": "installation_repair_retry", "failure": owner},
            next_owner="recovery", at=at)
    if diagnosis:
        current_diagnosis = runtime['operational_dispositions'][diagnosis['id']]
        if outcome == 'repaired':
            resume_installation_repair(runtime, current_diagnosis, repaired_by=execution_id, at=at)
        else:
            current_diagnosis['status'] = 'installation_repair_waiting'
            current_diagnosis.setdefault('result', {})['installation_repair'].update(
                status=outcome, attempted_by=execution_id)
