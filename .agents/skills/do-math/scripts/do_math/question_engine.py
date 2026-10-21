"""Question text stays in its original result; links own routing and resolution."""
from copy import deepcopy
import hashlib
import json

from . import academic, questions, planning, submission, activities
from .canonical import exact_content_hash
from .input_basis import CurrentnessChanged
from .session_slots import held_reservations
from .state_contract import ARTIFACT_ROOT


def resolve_pointer(value, pointer):
    for token in pointer.strip("/").split("/"):
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def question_view(instance, runtime, read_many):
    """Question links with the text each resolves to in its original source.

    ``read_many(paths)`` reads the source artifacts of one snapshot. A source
    that no longer resolves leaves the text None and marks it unavailable.
    """
    rows = deepcopy(runtime.get("question_links", []))
    refs = list(dict.fromkeys([*(row['source_ref'] for row in rows if row.get('source_ref')),
        *(o['source_ref'] for row in rows for o in row['origins'] if o.get('source_ref'))]))
    sources = {ref: json.loads(raw) for ref, raw in read_many(refs).items()} if refs else {}
    for row in rows:
        decision = instance.get('decisions', {}).get(row.get('resolution_ref'))
        if decision:
            row['resolution'] = {key: deepcopy(decision[key]) for key in ('id', 'kind', 'change', 'source_ref', 'created_at') if key in decision}
        try:
            source = (sources[row["source_ref"]] if row.get("source_ref") else
                      runtime["intent_imports"][row["source_id"]] if row.get("source_kind") == "intent_import" else
                      runtime["review_cycles"][row["source_id"]] if row.get("source_kind") == "review_cycle" else
                      runtime["history"] if row.get("source_kind") == "history" else
                      runtime["executions"][row["origin_execution_id"]])
            field = row["origin_field"]
            row["text"] = resolve_pointer(source, field)
            if row.get("question_kind") == "grant":
                row["text"] = "External action requires a user grant: " + row["text"]
        except (KeyError, IndexError, ValueError, TypeError):
            row["text"] = None
            row["source_status"] = "unavailable"
        row['reports'] = []
        for origin in row['origins']:
            report = deepcopy(origin)
            try:
                if origin.get('source_ref'):
                    source = sources[origin['source_ref']]
                elif origin.get('source_kind') == 'intent_import':
                    source = runtime['intent_imports'][origin['source_id']]
                elif origin.get('source_kind') == 'review_cycle':
                    source = runtime['review_cycles'][origin['source_id']]
                elif origin.get('source_kind') == 'history':
                    source = runtime['history']
                elif (origin['execution_id'], origin['field']) == (row['origin_execution_id'], row['origin_field']):
                    report['text'] = deepcopy(row['text'])
                    row['reports'].append(report)
                    continue
                else:
                    source = runtime['executions'][origin['execution_id']]
                report['text'] = resolve_pointer(source, origin['field'])
            except (KeyError, IndexError, ValueError, TypeError):
                report.update(text=None, source_status='unavailable')
            row['reports'].append(report)
    return rows


def user_questions(view):
    """The texts of the open questions a user owns, from a ``question_view``."""
    return [row["text"] for row in view if row["owner"] == "user" and row["status"] == "open" and row.get("text")]


class QuestionEngineMixin:
    def _question_view(self):
        return question_view(self.instance, self.runtime, lambda refs: self.store.read_many(refs, self.head))

    def _record_output_questions(self, action, output, execution_id, *, public=False, source_ref=None,
                                 read_artifact=None, output_files=None):
        # v5 intent questions are published only by governance.apply_import after check.
        if action.get("role") == "intent_interpretation":
            return
        if (not public and action.get('role') == 'operational_review'
                and self.runtime['executions'].get(action.get('target'), {}).get('action', {}).get('review_cycle_id')):
            return
        if not output.get("questions") or (action.get("review_cycle_id") and not public):
            return
        execution = self.runtime["executions"][execution_id]
        source = None
        review_source = None
        if public and action.get("review_cycle_id"):
            cycle = self.runtime["review_cycles"][action["review_cycle_id"]]
            review_source = next(key for key, row in cycle["results"].items() if row["execution_id"] == execution_id)
        else:
            source = source_ref or (execution.get("submission_intent", {}).get("output_ref") or
                      f"{ARTIFACT_ROOT}{execution['artifact_bundle']}/output.json")
        routes = {row["question_index"]: row for row in execution.get("extensions", {}).get("question_routes", [])}
        default_owner = "operations" if action["role"] in questions.OPERATIONS_ROLES else "research"
        for index, text in enumerate(output.get("questions", [])):
            route = routes.get(index, {})
            owner = route.get("owner", default_owner)
            targets = route.get("target_ids", [self.instance["id"]] if owner == "user" else [action["target"]] if action.get("target") else [])
            field = ("results/" + review_source + "/output/" if review_source else "") + "questions/" + str(index)
            row = questions.link(self.runtime, execution_id=execution_id, field=field,
                owner=owner, targets=targets, source_ref=source, reason=route.get("reason"), blocks=route.get("blocks", False),
                obligation=route.get('obligation'), existing_question_id=route.get('existing_question_id'),
                handler_role=route.get('handler_role'), reopen_reason=route.get('reopen_reason'),
                source_kind='review_cycle' if review_source else None,
                source_id=action['review_cycle_id'] if review_source else None,
                observation_basis=([self._resolve_execution_evidence(execution_id, ref,
                    read_artifact=read_artifact, output_files=output_files) for ref in route['reopen_basis_refs']]
                    if route.get('reopen_basis_refs') else None), clock=self.ports.clock)

    def _resolve_execution_evidence(self, execution_id, ref, *, read_artifact=None, output_files=None):
        execution = self.runtime['executions'][execution_id]
        reader = read_artifact or (lambda path: self.store.read(path, self.head))
        files = output_files if output_files is not None else execution.get('submission_intent', {}).get('file_refs', execution.get('output_files', []))
        def record(reference):
            found = planning.record_index(self.instance, self.runtime, source_aliases=True).get(reference)
            if found:
                family, value = found
                # Preserve the exact checked content, not a mutable workspace locator.
                return {'record_id': reference, 'family': family, 'sha256': exact_content_hash(value)}
            value = academic.evidence_record(self.instance, self.runtime, reference, reader)
            return {'artifact_ref': reference, 'sha256': exact_content_hash(value) if not isinstance(value, bytes)
                    else hashlib.sha256(value).hexdigest(),
                    **({'bytes': len(value)} if isinstance(value, bytes) else {})}
        return submission.resolve_output_evidence(ref, output_files=files, read_artifact=reader, resolve_record=record)

    def _apply_question_resolutions(self, execution_id, *, read_artifact=None, output_files=None):
        if not self.runtime['executions'][execution_id].get('extensions', {}).get('question_resolutions'):
            return
        # A caller may use this receiver directly as well as inside a bundle candidate.
        original = self.runtime
        self.runtime = deepcopy(original)
        try:
            self._apply_question_resolution_candidate(execution_id, read_artifact=read_artifact, output_files=output_files)
            original.clear()
            original.update(self.runtime)
        finally:
            self.runtime = original

    def _apply_question_resolution_candidate(self, execution_id, *, read_artifact=None, output_files=None):
        execution = self.runtime['executions'][execution_id]
        extension = execution.get('extensions', {})
        by_id = {row['id']: row for row in self.runtime.get('question_links', [])}
        action, role = execution['action'], execution['role']
        checked = set()
        for resolution in extension.get('question_resolutions', []):
            identifier = resolution['question_id']
            error = questions.resolution_error(None if identifier in checked else by_id.get(identifier), role)
            if error:
                raise ValueError(error)
            checked.add(identifier)
        seen = set()
        for resolution in extension.get("question_resolutions", []):
            identifier = resolution["question_id"]
            # The receiver's schema already fixed disposition, reason and evidence.
            error = questions.resolution_error(None if identifier in seen else by_id.get(identifier), role)
            if error:
                raise ValueError(error)
            seen.add(identifier)
            row = by_id[identifier]
            evidence = {'evidence_refs': list(resolution['evidence_refs']), 'reason': resolution['reason'],
                'resolved_evidence': [self._resolve_execution_evidence(execution_id, ref,
                    read_artifact=read_artifact, output_files=output_files) for ref in resolution['evidence_refs']]}
            disposition = resolution['disposition']
            affected = list(action['question_target_ids']) if row['owner'] == 'operations' else list(questions.open_targets(row))
            later_observations = set()
            if row['owner'] == 'operations':
                handling = row['handling']
                if (resolution.get('generation') != action.get('question_generation')
                        or set(resolution.get('affected_ids', [])) != set(affected)):
                    raise ValueError('operations resolution differs from its fixed assignment')
                if handling['generation'] != action['question_generation']:
                    raise CurrentnessChanged([{'id': identifier, 'field': 'question_generation',
                        'before': action['question_generation'], 'after': handling['generation']}])
                fixed, _ = self._issued_input(execution, with_schema=False)
                assigned = next(q for q in fixed['operations_questions'] if q['id'] == identifier)
                read_origins = {(o['execution_id'], o['field']) for o in assigned['origins']}
                for origin in row['origins']:
                    if ((origin['execution_id'], origin['field']) not in read_origins and origin.get('observation_basis')
                            and origin['observation_basis'] != assigned['handling']['observation_basis']):
                        later_observations.update(set(origin['target_ids']) & set(affected))
                handling['last_resolution_ref'] = execution_id
            if disposition == 'superseded':
                replacement = by_id.get(resolution.get('replacement_question_id'))
                if not replacement or replacement['status'] != 'open' or replacement['owner'] != row['owner'] or replacement is row:
                    raise ValueError('superseded requires a distinct open recipient of the same owner')
                replacement['target_ids'] = list(dict.fromkeys([*replacement['target_ids'], *affected]))
                replacement['unresolved_target_ids'] = list(dict.fromkeys([*questions.open_targets(replacement), *affected]))
                replacement['origins'].extend(o for o in deepcopy(row['origins']) if o not in replacement['origins'])
                evidence['replacement_question_id'] = replacement['id']
                questions.close(row, kind='ai_resolution', status='superseded', resolution_ref=execution_id,
                                affected_ids=affected, evidence=evidence)
            elif disposition == 'resolved':
                questions.close(row, kind='ai_resolution', resolution_ref=execution_id, affected_ids=affected,
                    evidence=evidence, preserve_ids=later_observations)
            else:
                if row['owner'] != 'operations':
                    raise ValueError('only operations handlers may wait or transfer')
                handling = row['handling']
                if disposition == 'waiting':
                    wait = deepcopy(resolution['wait_for'])
                    if wait['kind'] == 'question':
                        child = next(q for q in fixed['question_links'] if q['id'] == wait['question_id'])
                        wait = questions.question_wait(child, affected)
                    handling.update(state='waiting', waiting=wait)
                elif resolution.get('recipient_ref') == 'current:operational_disposition':
                    od = next((r for r in self.runtime.get('operational_dispositions', {}).values()
                               if r['execution_id'] == execution_id and r['disposition']['kind'] == 'repair'), None)
                    if not od:
                        raise ValueError('repair recipient must have an actual operational disposition')
                    handling.update(state='waiting', waiting={'kind': 'operational_disposition', 'disposition_id': od['id']})
                elif resolution['next_owner'] in questions.OPERATIONS_ROLES:
                    if resolution['next_owner'] == role:
                        raise ValueError('transfer must change the actual handler')
                    handling.update(state='pending', role=resolution['next_owner'], waiting=None,
                        generation=handling['generation'] + 1, action_id=None)
                else:
                    index = questions.output_question_index(resolution['recipient_ref'])
                    child = next((q for q in by_id.values() if any(o['execution_id'] == execution_id
                                 and o['field'] == 'questions/' + str(index) for o in q['origins'])), None)
                    if not child or child['owner'] != resolution['next_owner'] or child is row:
                        raise ValueError('transfer must bind its actual routed child question')
                    handling.update(state='waiting', waiting=questions.question_wait(child, affected))
                    evidence['recipient_question_id'] = child['id']
                    if child['owner'] == 'research':
                        self._lifecycle_event('question_research_followup', target=child['id'], source_ref=execution_id,
                            next_owner='research_plan', reason='Prepare or assess research for the transferred question')
                row.setdefault('resolution_history', []).append({'kind': disposition, 'resolution_ref': execution_id,
                    'affected_ids': affected, 'evidence': evidence, 'wait_for': deepcopy(handling['waiting'])})
            self._advance_question_dependents(identifier, execution_id)

    def _advance_question_dependents(self, question_id, resolution_ref):
        history = self.runtime.setdefault('history', [])
        if any(r.get('kind') == 'question_followup' and (r.get('question_id'), r.get('resolution_ref')) ==
               (question_id, resolution_ref) for r in history):
            return False
        row = next(q for q in self.runtime['question_links'] if q['id'] == question_id)
        if row['status'] == 'open' and not any(r['resolution_ref'] == resolution_ref and r['kind'] == 'ai_resolution'
                                              for r in row.get('resolution_history', [])):
            return False
        history.append({'kind': 'question_followup', 'question_id': question_id, 'resolution_ref': resolution_ref})
        self._resume_contract_review_waits()
        for entry in list(self.runtime.get('waiting_actions', {}).values()):
            if entry.get('kind') != 'revision_dependency':
                continue
            targets = {}
            for identifier, deferred in entry.get('deferrals', {}).items():
                states = [questions.question_scope_state(self.runtime, qid, scope)
                    for qid, scope in deferred.get('question_scopes', {}).items()]
                if states and all(s['resolved'] for s in states) and any(resolution_ref in s['resolution_refs'] for s in states):
                    targets[identifier] = entry['action']['revision_targets'][identifier]
            if targets:
                self._enqueue('research_preparation', revision_targets=targets, revision_parent_ids=[entry['action']['id']],
                    receipt_refs=[resolution_ref], reason='Question evidence released the deferred revision preparation')
                for identifier in targets:
                    del entry['deferrals'][identifier]
        if not self._instance_closed():
            self._lifecycle_event('question_resolved', target=question_id, source_ref=resolution_ref,
                next_owner='research_plan', reason='Reconsider affected work with the accepted question evidence')
        return True

    def _resume_contract_review_waits(self):
        changed = False
        links = {q['id']: q for q in self.runtime.get('question_links', [])}
        for task in self.runtime.get('tasks', {}).values():
            wait = task.get('waiting', {})
            if wait.get('kind') != 'contract_review_input' or wait.get('contract_sha256') != planning.contract_hash(task):
                continue
            basis = planning.review_basis_key(task, self.instance, self.runtime)
            relevant = {qid: questions.question_scope_state(self.runtime, qid, scope)
                        for qid, scope in wait['question_scopes'].items()}
            closed = all(q['resolved'] for q in relevant.values())
            fresh_receipt = relevant != wait['question_resolution_basis']
            if not (closed and fresh_receipt) and basis == wait['review_basis_key']:
                continue
            receipt_refs = list(dict.fromkeys(ref for q in relevant.values() for ref in q['resolution_refs']))
            live = any(e['status'] != 'ended' and e.get('action', {}).get('role') == 'task_contract_review'
                and e['action'].get('target') == task['id'] for e in self.runtime['executions'].values())
            if live:
                continue
            task.pop('waiting')
            task['status'] = 'planned'
            for r in task.get('contract_review_reconsiderations', []):
                if r['status'] == 'conflict':
                    r['status'] = 'reviewed'
            self._enqueue('task_contract_review', task['id'],
                contract_basis={'revision': task['revision'], 'contract_sha256': planning.contract_hash(task), **self._governance_revisions()},
                review_basis_key=basis, receipt_refs=receipt_refs,
                reason='Missing contract judgment evidence changed or was resolved')
            changed = True
        return changed

    def _reconcile_question_actions(self):
        """Bind QU and real handler requests in the same candidate, including cold owners."""
        changed = self._resume_contract_review_waits()
        links = {q['id']: q for q in self.runtime.get('question_links', [])}
        for row in list(links.values()):
            if row['owner'] != 'operations':
                if row.get('resolution_ref'):
                    changed |= self._advance_question_dependents(row['id'], row['resolution_ref'])
                continue
            handling = row['handling']
            executions = [self.runtime['executions'][eid] for eid in handling['execution_ids']]
            if any(e['status'] != 'ended' for e in executions) or held_reservations(self.runtime, handling['execution_ids']):
                continue
            for action in list(self.runtime.get('queue', [])):
                if (action.get('question_ids') == [row['id']] and (row['status'] != 'open'
                        or action['question_generation'] != handling['generation'])):
                    self._remove_action(action)
                    self.runtime['history'].append({'kind': 'question_action_retired', 'action': deepcopy(action),
                        'resolution_ref': handling['last_resolution_ref']})
                    if handling['action_id'] == action['id']:
                        handling['action_id'] = None
            if row['status'] != 'open':
                if row.get('resolution_ref'):
                    changed |= self._advance_question_dependents(row['id'], row['resolution_ref'])
                continue
            if handling['state'] == 'waiting':
                wake = questions.handling_wait_ready(row, self.instance, self.runtime, now=self.ports.clock.now())
                if not wake:
                    continue
                handling.update(state='pending', generation=handling['generation'] + 1,
                    action_id=None, waiting=None)
                changed = True
            active = [a for a in self.runtime.get('queue', []) if a.get('question_ids') == [row['id']]
                      and a.get('question_generation') == handling['generation']]
            blocked = [entry for entry in self.runtime.get('waiting_actions', {}).values()
                       if entry['action'].get('question_ids') == [row['id']]
                       and entry['action'].get('question_generation') == handling['generation']]
            if active or blocked:
                handling['action_id'] = (active[0] if active else blocked[0]['action'])['id']
                continue
            if handling['state'] == 'assigned':
                # Failure/rejection keeps the original bounded repair/diagnosis owner.
                continue
            if self._instance_closed() or self.runtime.get('user_pause') or self.runtime.get('status') in {'paused', 'closed'} or self.runtime.get('maintenance_fence'):
                continue
            if (handling['owner_activity_id'] and
                    self.runtime['activities'][handling['owner_activity_id']]['status'] == 'finished'):
                handling['owner_activity_id'] = None
            subject = row['obligation']['subject_ref']
            if handling['role'] == 'operational_review' and subject not in self.runtime['executions']:
                raise ValueError('operational question handler requires an execution subject')
            self._enqueue(handling['role'], subject, stage='question', question_ids=[row['id']],
                question_generation=handling['generation'], question_target_ids=list(questions.open_targets(row)),
                **({'owner_activity_id': handling['owner_activity_id']} if handling['owner_activity_id'] else {}),
                reason='Investigate the operations obligation and return its evidence-backed disposition')
            action = next(a for a in self.runtime['queue'] if a.get('question_ids') == [row['id']]
                          and a['question_generation'] == handling['generation'])
            handling.update(action_id=action['id'], state='pending')
            changed = True
        return changed

    def _record_review_questions(self, cycle, execution_id):
        fields = ["research/" + key + "/question" for key, request in cycle.get("research", {}).items()
                  if request.get("status") in {"pending", "unresolved"}]
        fields.extend(f"research/{key}/result/output/questions/{index}"
                      for key, request in cycle.get("research", {}).items()
                      for index, _ in enumerate((request.get("result") or {}).get("output", {}).get("questions", [])))
        fields.extend(f"followup/{index}/research_requests/{number}/question"
                      for index, entry in enumerate(cycle.get("followup", []))
                      for number, _ in enumerate(entry.get("research_requests", [])))
        for field in fields:
            row = questions.link(self.runtime, execution_id=execution_id, field=field, owner="research",
                                 targets=[cycle.get("knowledge_id")] if cycle.get("knowledge_id") else [],
                                 source_kind='review_cycle', source_id=cycle['id'], clock=self.ports.clock)

    def _user_questions(self):
        return user_questions(self._question_view())
