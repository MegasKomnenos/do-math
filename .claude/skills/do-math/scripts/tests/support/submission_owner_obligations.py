"""실제 owner의 정상 준비·반려·재전달 단언. 제품 수신과 저장은 대체하지 않는다."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import traceback
import jsonschema

from do_math import integration, submission
from do_math.canonical import canonical_json
from do_math.control_transport import ControlTransport, FINAL_RECEIPTS
from support.fakes.calls import owner_turn
from support.submission_calls import submission_model
from support.submission_obligations import (
    item_shapes, maintenance_output, mutation_target_inputs, required_and_enum_inputs,
)


def receipt(binding, request_id):
    for _ in range(100):
        value = ControlTransport.worker_receipt(binding, request_id)
        if value and value['state'] in FINAL_RECEIPTS:
            return value
        owner_turn()
    raise AssertionError('100 owner 차례 안에 제출 영수증 없음: ' + request_id)


class OwnerIngressAssertions:
    def install_family_probe(self, sim, roles):
        """실제 모델 호출의 정상 응답을 보존하여 같은 실행에 오입력을 전달한다."""
        model = submission_model(sim, responder=sim.model.responder)
        seen = {}
        failures = []

        def probe(context, workspace):
            workspace = Path(workspace)
            fixed = json.loads((workspace / 'input/submission/context.json').read_bytes())
            action = fixed['action']
            key = (action['role'], action.get('stage'), bool(action.get('review_cycle_id')),
                   'assessment_targets' in action, 'observation_rule_targets' in action)
            if key in seen:
                return
            good, contract = model.output(action['role'], context, workspace)
            self.assertEqual((contract.mode, contract.expected_receipt), ('bound', 'accepted'))
            sidecar = workspace / 'activity-extensions.json'
            original = sidecar.read_bytes() if sidecar.exists() else b'{}'
            baseline = json.loads(original)
            draft = workspace / 'normal-family-draft.json'
            draft.write_bytes(canonical_json(good))
            normal = submission.producer_check(workspace, draft, clock=sim.clock)
            self.assertEqual((normal['passed'], normal['issues']), (True, []), key)
            if action['role'] == 'operational_review':
                basis = fixed['admissible_basis_refs']
                self.assertIn(action['target'], basis)
                self.assertEqual(len(basis), len(set(basis)))
                readable = next(row['value'] for row in fixed['reference_catalog'] if row['value'] not in basis)
                bad = deepcopy(good)
                bad['disposition']['basis_refs'] = [readable]
                reason = ('operational disposition cites evidence outside its current input; '
                    'invalid_basis_refs=' + repr([readable]) + '; admissible_basis_refs=' + repr(sorted(basis)))
                self.reject_and_replay(sim, workspace, fixed['control_binding'], bad, baseline,
                    [('submission.output.disposition.basis_refs', 'output/disposition/basis_refs', reason)], 'basis-outside')
                sidecar.write_bytes(original)
                for reference in basis:
                    candidate = deepcopy(good)
                    candidate['disposition']['basis_refs'] = [reference]
                    draft.write_bytes(canonical_json(candidate))
                    self.assert_candidate_admitted(sim, workspace, fixed['control_binding'],
                        candidate, baseline, 'basis-' + str(basis.index(reference)))
                good['disposition']['basis_refs'] = list(basis)
                draft.write_bytes(canonical_json(good))
                normal = submission.producer_check(workspace, draft, clock=sim.clock)
                self.assertEqual((normal['passed'], normal['issues']), (True, []), key)
            families = submission.extension_schema(action)['properties']
            seen[key] = {'execution_id': fixed['execution_id'], 'families': list(families),
                         'output': deepcopy(good), 'extensions': deepcopy(baseline)}
            cases = []
            for family, schema in families.items():
                for _, value in item_shapes():
                    error, = jsonschema.Draft202012Validator(schema['items']).iter_errors(value)
                    cases.append((family, [value], 'schema.type', '0', error.message))
                for label, value in [*required_and_enum_inputs(schema), *mutation_target_inputs(family, schema)]:
                    errors = list(jsonschema.Draft202012Validator(schema).iter_errors(value))
                    self.assertEqual(len(errors), 1, (family, label, errors))
                    error, = errors
                    path = '/'.join(map(str, error.absolute_path))
                    if error.validator == 'required':
                        missing = [key for key in error.validator_value if key not in error.instance]
                        self.assertEqual(len(missing), 1, (family, label))
                        path += '/' + missing[0]
                        message = 'required property is missing'
                    else:
                        message = error.message
                    cases.append((family, value, 'schema.' + error.validator, path, message))
            for index, (family, value, rule, path, message) in enumerate(cases):
                extensions = {**baseline, family: value}
                output = deepcopy(good)
                if 'integration_bundles' in output:
                    self.assertEqual(len(output['integration_bundles']), 1)
                    output['integration_bundles'][0]['members'] = sorted(
                        integration.member_values(output, extensions, fixed))
                self.reject_and_replay(sim, workspace, fixed['control_binding'], output, extensions,
                    [(rule, 'activity-extensions.json/' + family + '/' + path, message)], index)
            sidecar.write_bytes(original)
            # 상태를 가진 정상 응답 생산자도 한 번만 호출한다. 실제 worker가
            # 뒤에 제출할 답은 방금 정상 검사를 통과한 바로 그 출력이다.
            model.preserve_reply(action['role'], fixed['execution_id'], good, baseline)

        def observed(context, workspace):
            try:
                probe(context, workspace)
            except Exception:
                failures.append(traceback.format_exc())
                raise

        for role in roles:
            model.before(role, observed)
        return seen, failures


    def await_family_probes(self, sim, roles, seen, failures, *, max_steps=16):
        """worker 내부 단언 오류를 원래 traceback으로 드러내며 종료까지 기다린다."""
        def finished(state):
            self.assertEqual(failures, [], '\n'.join(failures))
            return roles <= {key[0] for key in seen} and all(
                state.runtime['executions'][row['execution_id']]['status'] == 'ended'
                for row in seen.values())
        from support.role_input_requirements import observe_judgment_inputs
        with observe_judgment_inputs(self):
            sim.run_until(finished, max_steps=max_steps)

    def assert_family_accepted(self, sim, seen):
        """중앙 봉인 뒤 실제 적용까지 원래 수락 계약을 확인한다."""
        for key, row in seen.items():
            execution = sim.runtime['executions'][row['execution_id']]
            self.assertEqual(execution['outcome'], 'output_accepted', (key, execution.get('error'), execution.get('integration_result')))
            sealed = submission.read_sealed_submission(execution, sim.engine.head,
                sim.engine.store.read, git_dir=sim.engine.store.git_dir)
            self.assertEqual(sealed['output'], row['output'], key)
            self.assertEqual(sealed['extensions'], submission.load_extensions(canonical_json(row['extensions'])), key)

    def assert_candidate_admitted(self, sim, workspace, binding, output, extensions, index):
        """Check identical bytes locally and with the owner's real candidate callbacks.

        Preview runs currentness/application/storage validation on disposable
        state. Its receipt is not an authoritative submission or publication.
        The enclosing flow separately submits and applies its preserved reply.
        """
        workspace = Path(workspace)
        draft = workspace / '.scratch/advertised-draft.json'
        draft.parent.mkdir(exist_ok=True)
        draft.write_bytes(canonical_json(output))
        (workspace / 'activity-extensions.json').write_bytes(canonical_json(extensions))
        checked = submission.producer_check(workspace, draft, clock=sim.clock)
        self.assertEqual((checked['passed'], checked['issues']), (True, []), index)
        before = deepcopy((sim.instance, sim.runtime))
        request_id = 'advertised-' + binding['execution_id'] + '-' + str(index)
        delivery = ControlTransport.worker_submit(binding, request_id=request_id,
            kind='submission_preview', payload={'draft_path': draft.relative_to(workspace).as_posix()})
        self.assertEqual(delivery, {'request_id': request_id, 'state': 'submitted'})
        preview = receipt(binding, request_id)
        self.assertEqual(preview['state'], 'previewed', preview)
        result = preview['result']
        self.assertEqual((result['passed'], result['issues'], result['authoritative']), (True, [], False), index)
        self.assertEqual(result['input_hashes'], checked['input_hashes'], index)
        self.assertNotIn('candidate_application', result['not_checked'])
        self.assertEqual((sim.instance, sim.runtime), before)


    def reject_and_replay(self, sim, workspace, binding, output, extensions, expected, index):
        """expected는 모든 (rule, path, message)의 순서 있는 목록이다."""
        workspace = Path(workspace)
        draft = workspace / 'obligation-draft.json'
        draft.write_bytes(canonical_json(output))
        sidecar = workspace / 'activity-extensions.json'
        sidecar.write_bytes(canonical_json(extensions))
        raw = draft.read_bytes()
        raw_extensions = sidecar.read_bytes()
        producer = submission.producer_check(workspace, draft, clock=sim.clock)
        self.assertEqual((producer['passed'], [(i['rule_id'], i['path'], i['message'])
            for i in producer['issues']]), (False, expected))
        before_receipts = deepcopy(sim.runtime.get('control_receipts', {}))
        before_events = deepcopy(sim.runtime.get('events', []))
        before_domains = deepcopy((sim.instance.get('knowledge', {}), sim.runtime['tasks'],
                                   sim.runtime.get('integrations', {})))
        request_id = 'submission-malformed-' + binding['execution_id'] + '-' + str(index)
        payload = {'draft_path': draft.name}
        delivery = ControlTransport.worker_submit(binding, request_id=request_id,
                                                   kind='submit_intent', payload=payload)
        self.assertEqual(delivery, {'request_id': request_id, 'state': 'submitted'})
        rejected = receipt(binding, request_id)
        self.assertEqual((rejected['state'], rejected['reason']), ('rejected', 'candidate validation failed'))
        added = {key: row for key, row in sim.runtime['control_receipts'].items() if key not in before_receipts}
        self.assertEqual(len(added), 1)
        stored, = added.values()
        self.assertEqual(stored['request_id'], request_id)
        check_ref = stored['payload']['submission_check']['check_ref']
        check_raw = sim.engine.store.read(check_ref, sim.engine.head)
        check = json.loads(check_raw)
        self.assertEqual([(i['rule_id'], i['path'], i['message']) for i in check['issues']], expected)
        self.assertEqual((check['mode'], check['passed']), ('receiver', False))
        normalized_extensions = {key: value for key, value in extensions.items()
                                 if key not in submission.EXTENSION_ROLES or value != []}
        for name, value in [('output', output), ('extensions', normalized_extensions)]:
            encoded = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                                  allow_nan=False) + '\n').encode('utf-8')
            self.assertEqual(check['input_hashes'][name], hashlib.sha256(encoded).hexdigest())
        if any(rule.startswith('schema.') for rule, _, _ in expected):
            self.assertIn('payload_semantics', check['not_checked'])
            self.assertIn('integration_structure', check['not_checked'])
        prior_ids = {e['id'] for e in before_events}
        events = [e for e in sim.runtime['events'] if e['id'] not in prior_ids]
        self.assertEqual([(e['kind'], e['source_ref']) for e in events], [('submission_checked', stored['id'])])
        self.assertEqual((sim.instance.get('knowledge', {}), sim.runtime['tasks'],
                          sim.runtime.get('integrations', {})), before_domains)
        prefix = check_ref.removesuffix('check.json')
        self.assertEqual(sim.engine.store.read(prefix + 'output.json', sim.engine.head), raw)
        self.assertEqual(sim.engine.store.read(prefix + 'extensions.json', sim.engine.head), raw_extensions)
        for artifact in stored['payload']['submission_check']['artifacts']:
            preserved = sim.engine.store.read(artifact['path'], sim.engine.head)
            self.assertEqual(artifact['sha256'], hashlib.sha256(preserved).hexdigest())
        self.assertEqual(sim.runtime['executions'][binding['execution_id']]['status'], 'running')
        after = deepcopy((sim.runtime['control_receipts'], sim.runtime['events'],
                          sim.instance.get('knowledge', {}), sim.runtime['tasks'],
                          sim.runtime.get('integrations', {})))
        # 동일 locator의 바이트가 바뀌어도 동일 요청의 영수증은 다시 검사하지 않는다.
        draft.write_bytes(canonical_json(maintenance_output()))
        sidecar.write_bytes(b'{"research_insights":null}')
        self.assertEqual(ControlTransport.worker_submit(binding, request_id=request_id,
            kind='submit_intent', payload=payload), {'request_id': request_id, 'state': 'already_received'})
        for _ in range(2):
            owner_turn()
        self.assertEqual(receipt(binding, request_id), rejected)
        self.assertEqual((sim.runtime['control_receipts'], sim.runtime['events'],
                          sim.instance.get('knowledge', {}), sim.runtime['tasks'],
                          sim.runtime.get('integrations', {})), after)
        self.assertEqual(sim.engine.store.read(check_ref, sim.engine.head), check_raw)
        with self.assertRaisesRegex(ValueError, '^request_id was already received with different content$'):
            ControlTransport.worker_submit(binding, request_id=request_id, kind='submit_intent',
                                           payload={'draft_path': 'different.json'})
        self.assertEqual((sim.runtime['control_receipts'], sim.runtime['events'],
                          sim.instance.get('knowledge', {}), sim.runtime['tasks'],
                          sim.runtime.get('integrations', {})), after)
        self.assertEqual(sim.engine.store.read(prefix + 'output.json', sim.engine.head), raw)
        self.assertEqual(sim.engine.store.read(prefix + 'extensions.json', sim.engine.head), raw_extensions)
        sidecar.write_bytes(raw_extensions)
