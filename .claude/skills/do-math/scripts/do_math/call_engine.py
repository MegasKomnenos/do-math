"""Engine integration for one model call: its preparation, the runner's start and stop callbacks and the result.

``ResearchEngine._call_steps`` wires these to the runner, the clock and the tracker (설계 2.3).
"""
from __future__ import annotations

from .wait_rules import waiting_action
from copy import deepcopy
import json
import traceback
from pathlib import Path
from .contracts import prompt_metrics
from . import governance, knowledge, planning, academic
from .input_basis import capture_sources, sources_current, capture_decision_basis, decision_basis_changes
from .context_store import prepare_role_input, defer_input_overflow
from .observations import ObservationTracker, request_checkpoint, tracker_config, observation_settings_errors, bind_task_rules
from .canonical import canonical_json
from .state_contract import ARTIFACT_ROOT
from . import questions
from . import submission, execution_window
from . import activities, execution_lifecycle, execution_profiles, launch
from .provider_engine import record_model_policy_violation
from .payloads import json_safe
from .git_store import GitStateStoreError
from .wait_rules import review_preparation_wait, observation_preparation_wait, action_authority_wait


class InputPreparationInterrupted(Exception):
    """An unpublished input was abandoned before any model execution."""


class ReviewPreparationDeferred(Exception):
    def __init__(self, outcome):
        self.outcome = outcome
        super().__init__("review input restoration requires its recorded recovery")


class CallEngineMixin:
    def _fail_input_preparation(self, base, execution_id, error):
        """Park this unadmitted attempt; its snapshot and full diagnostic stay durable."""
        self._reload()  # Discard only unpublished preparation changes.
        execution = self.runtime['executions'][execution_id]
        if execution['status'] != 'queued' or execution.get('capacity') or execution.get('input_bundle'):
            raise error  # This boundary owns only private input before admission.
        action = deepcopy(execution['action'])
        reason = f'{type(error).__name__}: {error}'
        self._remove_action(action)
        self.runtime.setdefault('waiting_actions', {})[action['id']] = waiting_action({
            'action': action, 'kind': 'execution_failure', 'failure_kind': 'input_preparation',
            'execution_id': execution_id, 'input_snapshot': execution['input_snapshot'], 'reason': reason})
        self.runtime['history'].append({'kind': 'input_preparation_failed', 'execution_id': execution_id,
            'action': deepcopy(action), 'input_snapshot': execution['input_snapshot'],
            'error_type': type(error).__name__, 'reason': str(error),
            'traceback': ''.join(traceback.format_exception(error))})
        self.route_failed_action(action, execution_id, reason='Diagnose the preserved input preparation failure')
        self._discard_prepared_input(base, execution_id, reason=reason, cancelled=False)
        return True

    def _prepare_call(self, action: dict):
        """Everything before the runner call: gates, input, execution record, tracker and deadline.

        Returns the early-exit value of ``_call_steps`` or the ``prepared`` record the rest reads;
        ``stop_started`` in it is the owner's first stop observation.
        """
        if not self._check_installation(force=True):
            return False
        if not self._clock_guard()["usable"]:
            self.runtime["availability"] = {"state": "blocked", "reason": "clock_regression", "next_owner": "operator"}
            self._save()
            return False
        if action["role"] == "identity_review" and not action.get("review_cycle_id"):
            item = self.instance["knowledge"][action["target"]]
            predecessor = self.instance["knowledge"].get(item.get("supersedes"), {})
            self._start_identity_review(action["target"], previous_cycle_id=predecessor.get("review_cycle_id"))
            self._remove_action(action)
            self._save()
            return True
        action.setdefault("id", self.ports.clock.new_id("AC"))
        action.setdefault("lineage_id", action["id"])
        self._bind_revision_action(action)
        waits = self._revision_dispatch_waits(action)
        if waits:
            action["dispatch_wait"] = {"kind": "contract_revision", "blockers": waits}
            return False
        if not self._selected_action_current(action, evaluation_context=self._evaluation_context()):
            return True
        action = deepcopy(action)
        role = action["role"]
        obsolete = self._obsolete_action_reason(action)
        if obsolete:
            self._remove_action(action)
            self.runtime["history"].append({"kind": "obsolete_action", "action": action, "reason": obsolete})
            self._save()
            return True
        if role == "goal_audit" and action.get("basis") != self._goal_basis_key():
            for judgment in self.instance["goal_judgments"]:
                if judgment["basis"] == action.get("basis"): judgment["current"] = False
            self.runtime["queue"] = [a for a in self.runtime["queue"] if not (a["role"] == "goal_audit" and a.get("basis") == action.get("basis"))]
            self._enqueue("research_plan", reason="Goal audit inputs changed before the complete independent group finished")
            self._save()
            return True
        profile = self._execution_profile(action)
        activity = self._activity_for_action(action)
        config = {**self.instance["config"], **execution_profiles.runtime_config(profile)}
        task = self.runtime["tasks"].get(action.get("target"), {})
        rules = (self.runtime.get("task_observation_rules", {}).get(
            action.get("target"), task.get("initial_observation_rules", []))
            if role == "research_work" and not action.get("review_cycle_id") else [])
        execution_id = self.ports.clock.new_id('EX')
        settings_errors = observation_settings_errors(profile)
        try:
            if settings_errors:
                raise ValueError(json.dumps(settings_errors, ensure_ascii=False))
            if role == 'research_work':
                rules = bind_task_rules(rules, execution_id)
            observation_config = tracker_config(profile, initial_self_check_rules=rules,
                                              no_progress_limit=config.get("no_progress_limit"))
        except ValueError as error:
            waiting = observation_preparation_wait(action, str(error), task_rules=role == 'research_work' and not settings_errors)
            kind, next_owner = waiting['kind'], waiting['next_owner']
            activities.wait_for(self.runtime, activity["id"], kind=kind, reason=str(error),
                condition={"kind": kind, "task_id": action.get("target")}, next_owner=next_owner, at=self.ports.clock.now())
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = waiting
            if settings_errors:
                self.runtime['waiting_actions'][action['id']]['observation_errors'] = settings_errors
            self._remove_action(action)
            if next_owner == "research_preparation":
                self._enqueue("research_preparation", action.get("target"), reason="Supply valid observation rules before research starts")
            self._save()
            return True
        authority = governance.authorize(self.instance, action, runtime=self.runtime, at=self.ports.clock.now())
        if not authority["allowed"]:
            waiting = action_authority_wait(action, authority)
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = waiting
            activities.wait_for(self.runtime, activity['id'], kind=waiting['kind'], reason=waiting['reason'],
                condition={'kind': waiting['kind'], 'action_id': action['id']},
                next_owner=waiting['next_owner'], at=self.ports.clock.now())
            self._remove_action(action)
            if action.get("target") in self.runtime["tasks"]:
                self.runtime["tasks"][action["target"]]["status"] = "waiting"
            if self.runtime["status"] != "paused":
                self.runtime["status"] = "ready" if self.runtime["queue"] else "waiting"
            self._save()
            return bool(self.runtime["queue"])
        # _selected_action_current checked task readiness on this owner state;
        # profile/activity/observation setup above changes none of its premises.
        activity_id = activity["id"]
        queued = self._register_execution(action, {"id": execution_id, "role": role, "status": "queued",
            "created_at": self.ports.clock.now(), "input_snapshot": self.head, "grant_id": authority["grant_id"]}, profile=profile)
        if queued is None:
            self._save()
            return True
        execution_lifecycle.begin_preparation(queued, at=self.ports.clock.now())
        self._save()
        base = Path(self.instance["workspace"]) / "runs" / execution_id
        workspace = base / "workspace"
        workspace.mkdir(parents=True)
        preparation_started = self.ports.clock.monotonic()
        input_head = self.head
        self._preparing_input = True
        try:
            context = self._context(action, workspace, execution_id=execution_id)
        except ReviewPreparationDeferred as error:
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = review_preparation_wait(action, error.outcome)
            self._remove_action(action)
            self._discard_prepared_input(base, execution_id,
                reason="review input or authority requires resolution", cancelled=False)
            return True
        except InputPreparationInterrupted:
            self._apply_inbox(pump=False)
            self._discard_prepared_input(base, execution_id)
            return self.runtime["status"] != "paused" and not self._instance_closed()
        except submission.SealedSubmissionError as error:
            producer_id = action.get('input_basis', {}).get('impact_review', {}).get('producer_execution_id')
            waiting = next((row for row in self.runtime.get('waiting_actions', {}).values()
                if action.get('stage') == 'impact_review' and row.get('kind') == 'impact_review'
                and row.get('execution_id') == producer_id), None)
            if waiting is not None:
                self._hold_unreadable_impact_submission(waiting, error, preparation=(base, execution_id))
                return True
            return self._fail_input_preparation(base, execution_id, error)
        except GitStateStoreError:
            # Repository-wide read/publication failure cannot be isolated here.
            raise
        except Exception as error:
            return self._fail_input_preparation(base, execution_id, error)
        finally:
            self._preparing_input = False
        # Only an execution the tracker opens self checks for is offered the self-check tool.
        binding = self._transport.issue(execution_id, authority["grant_id"], workspace=workspace,
                                        self_check=observation_config["research_self_checks"])
        self._transport_bindings[execution_id] = binding
        context["control_binding"] = deepcopy(binding)
        schema = self._response_schema(action)
        if role == "intent_interpretation":
            context.setdefault("interpretation_to_check", None)
        # The execution's one input archive; the role input manifest names its files.
        input_bundle = self.ports.clock.new_id("BA")
        try:
            fitted = prepare_role_input(context, instance=self.instance, runtime=self.runtime, role=role, profile=profile,
                snapshot=input_head, workspace=workspace, activity_id=activity_id, output_schema=schema,
                documents=self._documents[role], artifact_prefix=f"{ARTIFACT_ROOT}{input_bundle}",
                install_submission_tools=True, max_artifact_bytes=config["max_artifact_bytes"], clock=self.ports.clock)
            context = submission.load_json((workspace / "input/submission/context.json").read_bytes())
        except Exception as error:
            return self._fail_input_preparation(base, execution_id, error)
        prompt = fitted["prompt"]
        self._apply_inbox(pump=False)
        if (self._execution_stop_requested(action)
                or not self._check_installation(force=True)):
            self._discard_prepared_input(base, execution_id)
            return False
        if self.head != input_head:
            # A user control changed the input while it was materialized.
            # Keep its obligations queued and prepare a new immutable input.
            self._discard_prepared_input(base, execution_id)
            return True
        if fitted["overflow"]:
            detail = deepcopy(fitted["overflow"])
            from .input_recovery import input_overflow_disposition
            if (role == 'identity_review' and action.get('review_cycle_id')
                    and detail.get('cause') == 'current_proposal_or_required_sources'
                    and detail.get('suggested_disposition') == input_overflow_disposition(
                        detail['cause'], detail['allowed_profile_candidates'])):
                overflow_ref = f"{ARTIFACT_ROOT}{self.ports.clock.new_id('BA')}/input-overflow.json"
                self.runtime.setdefault('input_overflows', []).append({
                    'action': deepcopy(action), 'detail': deepcopy(detail), 'source_catalog': deepcopy(fitted['manifest'])})
                self.runtime['executions'][execution_id]['input_manifest'] = deepcopy(fitted['manifest'])
                execution_lifecycle.end_preparation(self.runtime['executions'][execution_id], at=self.ports.clock.now(),
                    stage='packing', reason='review proposal input overflow', cancelled=True)
                self._transport.close(binding, reason='review proposal input overflow')
                self._transport_bindings.pop(execution_id, None)
                self._request_review_resource_disposition(action, 'review_input_overflow', {
                    'execution_id': execution_id, 'action': deepcopy(action), 'overflow': detail, 'overflow_ref': overflow_ref})
                self._save({**fitted['artifacts'], overflow_ref: canonical_json(detail)})
                return True
            resolution = detail.setdefault("resolution_question", {"question": "Which authorized profile or scope change should resolve this input overflow?", "next_owner": "user"})
            overflow_ref = f"{ARTIFACT_ROOT}{self.ports.clock.new_id('BA')}/input-overflow.json"
            question = questions.link(self.runtime, execution_id=execution_id, field="resolution_question/question",
                owner="research" if resolution["next_owner"] == "research_plan" else "user",
                targets=[action.get("target") or action["id"]], source_ref=overflow_ref,
                reason=resolution["question"], blocks=resolution["next_owner"] == "user", clock=self.ports.clock)
            retry = self._pending_input_overflow_retry(action)
            if retry:
                question_disposition = self._resolve_input_overflow_question(
                    retry["question_id"], execution_id=execution_id,
                    kind="input_overflow_retry_replaced", evidence={
                        "action_id": action["id"], "request_id": retry["request_id"],
                        "replacement_question_id": question["id"], "overflow_ref": overflow_ref})
                self._set_input_overflow_retry_state(action, "failed",
                    failure_execution_id=execution_id, question_disposition=question_disposition)
                self.runtime.setdefault("history", []).append({"kind": "input_overflow_retry_failed",
                    "action_id": action["id"], "activity_id": activity_id, "request_id": retry["request_id"],
                    "prior_question_id": retry["question_id"], "question_id": question["id"],
                    "execution_id": execution_id, "profile_ref": deepcopy(action.get("profile_ref")),
                    "overflow_ref": overflow_ref, "question_disposition": question_disposition,
                    "failed_at": self.ports.clock.now()})
            self.runtime.setdefault("input_overflows", []).append(deepcopy({"action": action, "detail": detail, "source_catalog": fitted["manifest"]}))
            self._remove_action(action)
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = waiting_action({"action": action,
                "kind": "input_overflow", "reason": "input_overflow", "detail": detail, "question_id": question["id"],
                "next_owner": resolution["next_owner"]})
            defer_input_overflow(self.runtime, detail, at=self.ports.clock.now(), question_ref=question["id"])
            if self.runtime["status"] != "paused":
                self.runtime["status"] = "ready" if self.runtime["queue"] else "waiting"
            if resolution["next_owner"] == "research_plan":
                self._enqueue("research_plan", reason="Select an already authorized profile for the preserved input overflow",
                              input_overflow=deepcopy(detail), overflow_activity_id=activity_id)
            execution_lifecycle.end_preparation(self.runtime["executions"][execution_id], at=self.ports.clock.now(),
                stage="packing", reason="input overflow", cancelled=True)
            self._continue_prepared_action(self.runtime["executions"][execution_id])
            self._transport.close(binding, reason="input overflow")
            self._transport_bindings.pop(execution_id, None)
            self._settle_activity(execution_id)
            self._save({overflow_ref: canonical_json(detail)})
            return self.runtime["status"] == "ready"
        basis_ids = []
        source_refs = []
        if action.get("target") in self.runtime["tasks"]:
            task = self.runtime["tasks"][action["target"]]
            source_refs = task.get("inputs", [])
            basis_ids = [k for k in {*task.get("dependencies", []), *task.get("reuse", []), *task.get("inputs", [])}
                         if k in self.instance["knowledge"] or k in self.runtime["tasks"]]
        elif action.get("target") in self.instance["knowledge"]:
            proposal = self.instance["knowledge"][action["target"]]
            basis_ids = [k for k in proposal.get("dependencies", []) if k in self.instance["knowledge"]]
            source_refs = [row["name"] for row in proposal.get("source_basis", [])]
        elif role == "goal_audit":
            # The group basis was checked before packing; the input_head
            # comparison above already discards any intervening publication.
            basis_ids = [k["id"] for k in self.instance["knowledge"].values() if knowledge.assess_use(k, self.instance)["valid"]]
        chosen_model = action["model_selection"]
        retry = self._pending_input_overflow_retry(action)
        if retry:
            evidence = {"action_id": action["id"], "request_id": retry["request_id"],
                "profile_ref": deepcopy(action.get("profile_ref")),
                "prompt_bytes": fitted["actual_bytes"],
                "limit_bytes": profile["input"]["max_input_bytes"],
                "prompt_sha256": fitted["manifest"]["prompt"]["sha256"]}
            question_disposition = self._resolve_input_overflow_question(
                retry["question_id"], execution_id=execution_id,
                kind="input_overflow_retry_resolved", evidence=evidence)
            self._set_input_overflow_retry_state(action, "resolved",
                resolved_execution_id=execution_id, question_disposition=question_disposition)
            self.runtime.setdefault("history", []).append({"kind": "input_overflow_retry_resolved",
                "activity_id": activity_id, "execution_id": execution_id,
                "question_disposition": question_disposition, "resolved_at": self.ports.clock.now(), **deepcopy(evidence)})
        execution = {"id": execution_id, "role": role, "action": action,
                     "status": "queued", "created_at": self.ports.clock.now(), "input_snapshot": self.head,
                     "input_bundle": input_bundle,
                     "model": chosen_model["model"],
                     "model_selection": chosen_model,
                     "grant_id": authority["grant_id"], "observed_at": context["observed_at"],
                     **self._governance_revisions(),
                     "validity_basis": knowledge.capture_basis(self.instance, self.runtime, basis_ids),
                     "decision_basis": capture_decision_basis(self.instance, self.runtime, self._decision_references(action)),
                     "source_basis": capture_sources(self.instance, source_refs),
                     "input_preparation_milliseconds": int((self.ports.clock.monotonic() - preparation_started) * 1000),
                     "input_manifest": deepcopy(fitted["manifest"]),
                     "input_reductions": fitted["reductions"],
                     "input_metrics": prompt_metrics(prompt, fitted["context"], schema, self._documents[role])}
        if action.get("target") in self.runtime["tasks"]:
            execution["contract_sha256"] = planning.contract_hash(self.runtime["tasks"][action["target"]])
            if self.runtime["tasks"][action["target"]].get("academic_requirement_id"):
                execution["academic_requirements_sha256"] = academic.current_requirements(self.instance)["sha256"]
        if role == "research_plan":
            solution_basis = self._solution_basis()
            if solution_basis is not None:
                execution["input_solution_basis"] = solution_basis
        if action.get("delegation_application_id"):
            execution["delegation_input_sha256"] = context["delegation_case"]["input_sha256"]
        if action.get("kind_definition_id"):
            execution["input_basis"] = {"kind_definition": {"id": action["kind_definition_id"],
                                                           "sha256": action["kind_definition_sha256"]}}
        self._bind_governance_input(action, execution, fitted["context"])
        self.runtime["executions"][execution_id].update(execution)
        execution = self.runtime["executions"][execution_id]
        tracker = ObservationTracker(execution_id, workspace, observation_config, time_port=self.ports.clock)
        if observation_config['observation_rules']:
            execution['observation_rules'] = deepcopy(observation_config['observation_rules'])
        admitted = self._provider_admit(action, execution_id, profile=profile, execution=execution)
        if not admitted:
            self._transport.close(binding, reason="execution was not admitted")
            self._transport_bindings.pop(execution_id, None)
            execution_lifecycle.transition_execution(execution, "ended", at=self.ports.clock.now(), outcome="start_failed",
                reason="provider admission deferred", disposition=deepcopy(action.get("dispatch_wait")))
            self._continue_prepared_action(execution)
            for queued in self.runtime['queue']:
                if queued.get('id') == action['id']:
                    queued['dispatch_wait'] = deepcopy(action['dispatch_wait'])
            activities.wait_for(self.runtime, activity_id, kind='provider_admission', reason="provider admission deferred",
                condition=deepcopy(action["dispatch_wait"]), next_owner=action["dispatch_wait"]["next_owner"], at=self.ports.clock.now())
            self._save(self._input_artifacts(input_bundle, schema, fitted, workspace))
            return False
        # Successful SessionSlots.acquire has already transitioned to starting.
        self._live_execution_ids.add(execution_id)
        if self.runtime["status"] != "paused":
            self.runtime["status"] = "running"
        if execution_profiles.task_research(action):
            self.runtime["tasks"][action["target"]]["status"] = "active"
        execution["control_transport"] = {key: value for key, value in binding.items() if key != "capability"}
        launch.mark_dispatched(execution['launch_ticket'])
        if role == "identity_review" and action.get("review_cycle_id"):
            self._record_review_input(action, execution_id)
            self._record_review_prompt(execution_id, prompt, artifact_ref=fitted["manifest"]["prompt"]["artifact_ref"])
        self._save(self._input_artifacts(input_bundle, schema, fitted, workspace))
        execution = self.runtime["executions"][execution_id]
        execution["input_published_at"] = self.ports.clock.now()
        self._trackers[execution_id] = tracker
        call_deadline = execution_window.call_deadline(role, config, clock=self.ports.clock.monotonic)
        return {'action': action, 'base': base, 'binding': binding, 'call_deadline': call_deadline,
                'config': config, 'context': context, 'execution': execution, 'execution_id': execution_id,
                'fitted': fitted, 'profile': profile, 'prompt': prompt, 'role': role, 'schema': schema,
                'tracker': tracker, 'workspace': workspace, 'stop_started': None}

    def _call_started(self, prepared, identity):
        """The runner started the execution: record the start and publish its execution window."""
        call_deadline = prepared['call_deadline']
        config = prepared['config']
        execution_id = prepared['execution_id']
        workspace = prepared['workspace']
        current = self._session_slots().started(execution_id, identity, at=self.ports.clock.now())
        current["execution_window"] = execution_window.publish(workspace, execution_id, call_deadline, config,
                                                               clock=self.ports.clock.monotonic, wall_clock=self.ports.clock.wall())
        self._save()

    def _call_stop_requested(self, prepared):
        """Owner-thread stop judgment for one running call; records a stop transition once."""
        action = prepared['action']
        call_deadline = prepared['call_deadline']
        config = prepared['config']
        execution_id = prepared['execution_id']
        role = prepared['role']
        tracker = prepared['tracker']
        workspace = prepared['workspace']
        # Owner-thread judgment. The owner loop applies controls and conversation
        # leases; this reads the published state and records a stop transition once.
        current = self.runtime["executions"][execution_id]
        if role == "operational_review" and action.get("live") and self._obsolete_action_reason(action):
            current["stop_requested"] = "observation_target_ended"
        allowed = governance.authorize(self.instance, action, runtime=self.runtime, at=self.ports.clock.now())["allowed"]
        changed = any(current[key] != value for key, value in self._governance_revisions().items())
        premise_changes = decision_basis_changes(current.get("decision_basis"), self.instance, self.runtime)
        premise_changes.extend(self._execution_requirement_changes(action, evaluation_context=self._evaluation_context()))
        if role == "goal_audit" and action.get("basis") != self._goal_basis_key_at_head():
            premise_changes.append({"field": "goal_audit_basis", "reason": "complete goal judgment basis changed"})
        if premise_changes:
            changed = True
        if not sources_current(current.get("source_basis", []), self.instance): changed = True
        if current.get("academic_requirements_sha256") and current["academic_requirements_sha256"] != academic.current_requirements(self.instance).get("sha256"):
            changed = True
        if current.get("contract_sha256") and action.get("target") in self.runtime["tasks"]:
            target_task = self.runtime["tasks"][action["target"]]
            changed = changed or planning.contract_hash(target_task) != current["contract_sha256"] or target_task["status"] == "closed"
        if changed:
            current["currentness_changes"] = premise_changes or [{"field": "action_contract_or_authority", "reason": "execution input changed"}]
        requested = (current.get("submission_intent") or self._execution_stop_requested(action, current)
                     or not allowed or changed
                     or execution_window.deadline_passed(call_deadline, clock=self.ports.clock.monotonic))
        if not requested:
            # The notice compares the same clock as the deadline above.
            execution_window.request_finish(workspace, call_deadline, config, clock=self.ports.clock.monotonic,
                                            now_iso=self.ports.clock.now())
            return False
        reason = current.get("stop_requested") or ("authority_changed" if not allowed or changed else
            "submission_intent" if current.get("submission_intent") else "user_or_deadline_stop")
        # Instruction boundaries cannot enforce checkpoint-only research after stop.
        if prepared['stop_started'] is None:
            prepared['stop_started'] = self.ports.clock.monotonic()
            current["stop_reason"] = reason
            current["stop_observed_at"] = self.ports.clock.now()
            tracker.set_execution_status("stopping")
            execution_lifecycle.transition_execution(current, "stopping", at=self.ports.clock.now(), reason=str(reason))
            self._save()
            request_checkpoint(workspace / ".control", str(reason), immediate=True, deadline=self.ports.clock.now())
        return True

    def _receive_call(self, prepared, result):
        """Everything after the runner returned: collect, preserve, judge and route the result."""
        action = prepared['action']
        base = prepared['base']
        binding = prepared['binding']
        config = prepared['config']
        context = prepared['context']
        execution = prepared['execution']
        execution_id = prepared['execution_id']
        profile = prepared['profile']
        role = prepared['role']
        schema = prepared['schema']
        tracker = prepared['tracker']
        workspace = prepared['workspace']
        tracker.set_execution_status("stopping")
        self._transport.pump(self._publish_control_request)
        self._transport.close(binding, reason="execution process ended")
        tracker.set_execution_status("ended")
        self._trackers.pop(execution_id, None)
        self._check_installation(force=True)
        self._live_execution_ids.discard(execution_id)
        provider_state = self._provider_outcome(execution_id, result)
        observation = execution_profiles.execution_observation(result)
        if observation is not None:
            self.runtime["executions"][execution_id]["provider_observation"] = observation
        if result.get("capability_evidence"):
            evidence = result["capability_evidence"]
            if evidence["execution_profile_ref"] != execution_profiles.profile_ref(profile):
                raise ValueError("capability evidence differs from the attempted profile")
            self.instance.setdefault("capability_evidence", {})[evidence["id"]] = deepcopy(evidence)
        pending = self.runtime["executions"][execution_id]
        if not execution_lifecycle.release_or_hold(pending, self._session_slots(), at=self.ports.clock.now()):
            result_ref = f"{ARTIFACT_ROOT}{self.ports.clock.new_id('BA')}/result.json"
            pending['result_ref'] = result_ref
            preserved = json_safe(result)
            for key in ('error_kind', 'failure'):
                if key in preserved:
                    pending[key] = deepcopy(preserved[key])
            self._publish_provider_result({result_ref: canonical_json(preserved)})
            return True
        result = self._collect_submitted_result(self.runtime["executions"][execution_id], result, context, schema, workspace)
        result = json_safe(result)
        if result.get('status') == 'failed':
            result.setdefault('error_kind', 'execution_failure')
        stopped_execution = self.runtime["executions"][execution_id]
        if result.get("error_kind") == "model_policy":
            record_model_policy_violation(self.instance, self.runtime, execution_id, execution["model"], result)
        if result["status"] == "completed" and (
                stopped_execution.get("after_stop")
                or self._execution_stop_requested(action, stopped_execution)):
            # The stop request already revoked general authority; keep the late output only as preserved evidence.
            result = {**result, "status": "stopped",
                      "error": "final output was collected after " + str(stopped_execution.get("stop_requested")
                          or "a pause or operational stop request") + "; preserved without acceptance"}
        bundle = self.ports.clock.new_id("BA")
        artifacts, output_files, _, outputs_complete = self._preserve_outputs(
            execution_id, workspace, bundle, max_bytes=config["max_artifact_bytes"], evidence_dir=base / "evidence")
        artifacts[f"{ARTIFACT_ROOT}{bundle}/result.json"] = canonical_json(result)
        if result.get("output") is not None:
            artifacts[f"{ARTIFACT_ROOT}{bundle}/output.json"] = canonical_json(result["output"])
        execution = self.runtime["executions"][execution_id]
        if execution["status"] != "stopping":
            execution_lifecycle.transition_execution(execution, "stopping", at=self.ports.clock.now())
        obsolete = self._obsolete_action_reason(action, execution_id=execution_id)
        accepting = ((result["status"] == "completed" or result.get("error_kind") == "output_validation")
            and not self._instance_closed() and not obsolete
            and not execution.get("currentness_changes"))
        if not accepting:
            cancelled = result["status"] == "stopped" and (self.runtime["status"] in {"paused", "closed"}
                or self.runtime.get("stop_requested"))
            execution_lifecycle.transition_execution(execution, "ended", at=self.ports.clock.now(), outcome="cancelled" if cancelled else "execution_incomplete",
                disposition={"kind": "preserved_for_followup", "artifact_ref": f"{ARTIFACT_ROOT}{bundle}/result.json"})
            if cancelled:
                self._continue_prepared_action(execution)
        execution.update(usage=result.get("usage", {}), artifact_bundle=bundle,
                          output_files=output_files, outputs_complete=outputs_complete,
                          result_ref=f"{ARTIFACT_ROOT}{bundle}/result.json", error=result.get("error"))
        for key in ("usage_segments", "model_usage_reported", "usage_scope", "reported_models", "error_kind", "failure"):
            if key in result:
                execution[key] = deepcopy(result[key])
        # Raw evidence is durable before any domain bundle is attempted.
        self._save(artifacts)
        artifacts = {}
        obsolete = self._obsolete_action_reason(action, execution_id=execution_id)
        if self.runtime["status"] == "closed":
            self.runtime["executions"][execution_id]["result_disposition"] = {"kind": "preserved_after_close"}
            self.runtime["queue"] = []
        elif self.runtime["status"] == "completed":
            self.runtime["executions"][execution_id]["result_disposition"] = {"kind": "preserved_after_goal_completion"}
            self._remove_action(action)
        elif obsolete:
            self.runtime["executions"][execution_id].update(result_disposition={"kind": "preserved_after_target_change"}, preserved_reason=obsolete)
            self._remove_action(action)
            if self.runtime["status"] == "running":
                self.runtime["status"] = "ready"
        elif execution.get("currentness_changes") and self.runtime["status"] != "paused":
            self._refresh_changed_decision(action, execution_id, execution["currentness_changes"])
        elif result.get("error_kind") == "provider_limit":
            self._requeue_provider_action(action, execution_id, provider_state)
        elif result.get("error_kind") == "model_policy":
            self._remove_action(action)
            self.runtime["status"] = "paused"
            self.runtime["questions"].append("A reported model differed from the locked assignment; inspect " + execution_id)
        elif result["status"] == "completed" or result.get("error_kind") == "output_validation":
            try:
                if not outputs_complete:
                    raise ValueError("required execution artifacts could not be preserved")
                self._receive_submission(action, result, execution_id, context, schema, workspace)
            except Exception as error:
                # Never restore an execution-wide copy: earlier bundles may have committed.
                current = self.runtime["executions"][execution_id]
                execution_lifecycle.transition_execution(current, "ended", at=self.ports.clock.now(), outcome="execution_incomplete",
                    disposition={"kind": "submission_failure"})
                current.update(error=str(error), error_kind="submission_failure")
                self._remove_action(action)
                self.runtime.setdefault("waiting_actions", {})[action["id"]] = waiting_action({
                    "action": deepcopy(action), "kind": "submission_failure", "reason": str(error),
                    "execution_id": execution_id, "next_owner": "engine"})
                self.route_failed_action(action, execution_id,
                    reason="Resolve the preserved submission or publication failure")
                if self.runtime["status"] != "paused" and not self._instance_closed():
                    self.runtime["status"] = "ready"
        else:
            pending_disposition = execution.get("pending_operational_disposition")
            if pending_disposition:
                self._remove_action(action)
                self._complete_operational_disposition(self.runtime["operational_dispositions"][pending_disposition])
            elif (role == "operational_review") and (action.get("live")):
                self._remove_action(action)
                self._failed_live_review(action, "Live operational review did not finish: " + str(result.get("error")))
                if self.runtime["status"] not in {"closed", "paused"}:
                    self.runtime["status"] = "ready" if self.runtime["queue"] else "waiting"
            elif result["status"] == "failed" or (result["status"] == "stopped"
                    and self.runtime["status"] not in {"paused", "closed"}
                    and not self.runtime.get("stop_requested")):
                self._remove_action(action)
                self.runtime.setdefault("waiting_actions", {})[action["id"]] = waiting_action({
                    "action": action, "kind": "execution_failure", "reason": result.get("error"),
                    "failure_kind": result.get("error_kind", "execution_failure"),
                    "execution_id": execution_id, "input_snapshot": execution["input_snapshot"]})
                returned = (result['status'] == 'stopped' and role == 'supplemental_research'
                            and action.get('research_request_id')
                            and self._finish_failed_investigation(action, execution_id, result.get('error')))
                if not returned:
                    self.route_failed_action(action, execution_id,
                        reason="Diagnose the preserved failure before selecting recovery")
                if self.runtime["status"] not in {"paused", "closed"}:
                    self.runtime["status"] = "ready" if self.runtime["queue"] else "waiting"
            # model_call.classify_run and the submission collector return only
            # completed/failed/stopped. A stopped paused/closed request needs
            # no extra status change here.
        self._settle_activity(execution_id)
        self._publish_provider_result(artifacts)
        self._controls()
        if self.runtime["status"] != "paused" and not self._instance_closed():
            self._refresh_readiness()
            self._save()
        return self.runtime["status"] in {"ready", "running"}
