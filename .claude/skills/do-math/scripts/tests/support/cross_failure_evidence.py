"""Strict historical failure-evidence classifier; it never captures or permits exploratory failures."""
import json
from pathlib import Path

def matches_recorded_failure(error, kind):
    if kind == 'closed_initialization':
        from do_math.lifecycle_engine import LifecycleEngineMixin
        if not isinstance(error, ValueError) or str(error) != 'closed/completed instance cannot activate':
            return False
        origin = error.__traceback__
        while origin is not None and origin.tb_next is not None:
            origin = origin.tb_next
        if origin is None or origin.tb_frame.f_code is not LifecycleEngineMixin._activate_initialization.__code__:
            return False
        witness = getattr(error, 'initialization_witness', {})
        lifecycle, receipt = witness.get('lifecycle', {}), witness.get('receipt') or {}
        return bool(witness.get('before_status') == witness.get('after_status') == 'closed'
                    and witness.get('other_invariants_checked')
                    and witness.get('last_event') == ('step',)
                    and lifecycle.get('state') == 'initializing' and lifecycle.get('permanently_closed')
                    and witness.get('source_ref') and receipt.get('effect') == 'applied'
                    and receipt.get('status') == 'closed' and receipt.get('snapshot')
                    and any(row.get('kind') == 'closed' and row.get('source_ref') == witness['source_ref']
                            for row in lifecycle.get('history', [])))
    if not isinstance(error, AssertionError) or not error.args or not isinstance(error.args[0], tuple):
        return False
    detail = error.args[0]
    if kind == 'closed_reasons':
        from support.cross_obligations import RequestReasonLoss, reasons
        if (not isinstance(error, RequestReasonLoss)
                or len(detail) != 2 or detail[0] != 'lost request reasons' or detail[1] != error.lost
                or not getattr(error, 'other_invariants_checked', False)
                or getattr(error, 'previous_status', None) in {None, 'closed', 'completed'}
                or error.runtime_status != 'closed'):
            return False
        witness = getattr(error, 'closure_witness', {})
        event, control = witness.get('last_event'), witness.get('control')
        if not event or event[0] != 'close' or not control or control['action'] != 'close':
            return False
        result = control['result'] or {}
        lifecycle = witness.get('lifecycle', {})
        if (result.get('effect') != 'applied' or result.get('status') != 'closed'
                or not result.get('snapshot') or not lifecycle.get('permanently_closed')
                or not any(row.get('kind') == 'closed' and row.get('source_ref') == control['request_id']
                           for row in lifecycle.get('history', []))):
            return False
        required = [row for row in error.requests if isinstance(row.get('id'), str) and row['id']
                    and (row.get('revision_of') or len(reasons(row)) > 1)]
        return bool(error.lost and error.lost == reasons(error.requests) - reasons(error.preserved)
                    and error.lost <= reasons(required))
    if kind == 'operational_question' and len(detail) == 5 and detail[:3] == (
            'event not accepted', 'operation', 'user_decision'):
        if not detail[4]:
            return False
        failed_execution = detail[4][-1][0]
        path = Path(detail[3]) / 'evidence.json'
        if not path.is_file():
            return False
        evidence = json.loads(path.read_text(encoding='utf-8'))
        execution = evidence['runtime'].get('executions', {}).get(failed_execution, {})
        action = execution.get('action', {})
        target = evidence['runtime'].get('executions', {}).get(action.get('target'), {})
        if (execution.get('status') != 'ended' or execution.get('outcome') != 'execution_incomplete'
                or execution.get('outcome') != detail[4][-1][1] or execution.get('error_kind') != 'output_contract'
                or action.get('role') != 'operational_review' or target.get('status') != 'ended'):
            return False
        observed = [row for row in evidence.get('observed', [])
                    if row.get('action', {}).get('id') == action.get('id')
                    and row.get('event') == 'operation' and row.get('value') == 'user_decision'
                    and row.get('output', {}).get('disposition', {}).get('kind') == 'user_decision']
        if len(observed) != 1:
            return False
        repairs = [wait.get('action', {}).get('repair', {})
                   for wait in evidence['runtime'].get('waiting_actions', {}).values()]
        issues = [issue for repair in repairs if repair.get('execution_id') == failed_execution
                  for issue in repair.get('issues', [])]
        return bool(issues) and all(issue.get('rule_id') == 'integration.candidate'
                   and 'runtime/operational_dispositions/' in issue.get('message', '')
                   and "Additional properties are not allowed ('question_id' was unexpected)" in issue['message']
                   for issue in issues)
    return False
