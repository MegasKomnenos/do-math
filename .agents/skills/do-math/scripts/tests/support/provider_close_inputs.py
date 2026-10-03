"""2-A 입력 표와 작업자 요청 씨앗. 원 외곽은 유지하고 목표 좌표만 바꾼다.

native 목록은 review_engine._record_review_observation의 분기 대응표다.
자동 발견 목록이 아니므로 새 제품 분기는 별도 코드 검토가 필요하다.
mode는 execution_profiles.OBSERVATION_MODES 정본을 사용한다.
"""
from copy import deepcopy

from do_math.claude_adapter import ADAPTERS
from do_math.execution_profiles import OBSERVATION_MODES
from do_math.model_call import worker_request_fields
from support.ingress import malformed
from support.provider_native_inputs import NATIVE_ROWS




def ingress_contracts():
    """입구별 현재 명세·전제·반려·소비 좌표. 원 반려 누락은 B35에서 수리했다.

NATIVE_ROWS는 공개 텍스트 네 외곽의 표다. command/mcp/tool 블록은
native_storage에서 별도 순회한다. 종결·개정·충돌과 원시 JSON은 resume 시험에서 별도 검산한다.
공개 삭제 전이가 없는 대상과 명시 null seam은 인계 보고서에 남긴다.
"""
    rows = []
    for name, seed, field, handler in NATIVE_ROWS:
        rows.append({'name': name, 'format': {'type': seed['type'], field: 'object'},
            'handler': handler, 'prerequisite': 'identity_review + review_cycle_id + 유효 slot',
            'coordinate': field, 'rejection': 'ValueError',
            'reason': {'public': 'invalid normalized public message', 'codex': 'invalid provider item',
                       'assistant': 'invalid provider public message', 'user': 'invalid provider public message'}[name],
            'consumption': 'source.event_index/message_id와 raw artifact_ref, 다음 빈 batch의 head 불변',
            'limitation': '중첩 잘못된 입력은 B35의 실제 owner 반려/다음 정상/빈 재순회 검증에 연결; 단위 표를 소비 증거로 대신하지 않음'})
    for mode in sorted(OBSERVATION_MODES):
        rows.append({'name': 'observation:' + mode,
            'format': {'type': 'turn.started', 'execution_id': '다른 실행 ID'},
            'handler': 'ObservationTracker.observe -> core_engine._observe_running',
            'prerequisite': '실제 running execution; 신뢰 batch source; research_self_checks=False',
            'coordinate': 'execution_id / stdout.jsonl start_offset,end_offset',
            'rejection': 'observation_input_rejected',
            'reason': 'observation belongs to a different execution',
            'consumption': '반려 1 + 원 사건 fact 1 + 후속 정상 fact 1; 빈 재순회 head/runtime 불변',
            'limitation': 'resume owner 시험은 live scheduling과 ended replay도 순회; 삭제 전이는 정적 상신'})
    return rows






def control_event(provider, call_id, tool, arguments):
    """실제 두 공급자의 제어 호출 외곽. 공급자 모집단은 ADAPTERS다."""
    from do_math.control_protocol import CONTROL_SERVER
    if provider == 'codex':
        return {'type': 'item.started', 'item': {'type': 'mcp_tool_call', 'id': call_id,
            'server': CONTROL_SERVER, 'tool': tool, 'arguments': deepcopy(arguments)}}
    if provider == 'claude':
        return {'type': 'assistant', 'message': {'content': [{'type': 'tool_use',
            'id': call_id, 'name': 'mcp__' + CONTROL_SERVER + '__' + tool, 'input': deepcopy(arguments)}]}}
    raise ValueError('provider 입력 표에 외곽 등록이 필요하다: ' + provider)


def request_seed(provider, root, *, jobs, clock):
    """실제 adapter options와 생산자를 사용한 비결속 정상 요청."""
    evidence, workspace = root / 'evidence', root / 'workspace'
    options = ADAPTERS[provider](str(root / (provider + '.exe')), jobs=jobs, clock=clock).worker_options(evidence)
    return worker_request_fields(options, prompt_path=evidence / 'input.txt', workspace=workspace,
        evidence_dir=evidence, cli_model='claude-sonnet-5' if provider == 'claude' else 'test-model',
        effort='high', timeout_seconds=10, schema_path=evidence / 'schema.json', execution_id=None,
        reference=None, resource_limits=None, control_binding=None, scholarly_server=None,
        claude_only_assigned_model=False)


def claude_rejections(seed):
    """서로 독립된 네 고유 guard. 다른 필드는 정상인 채 둔다."""
    missing = deepcopy(seed)
    del missing['output_schema_path']
    yield 'schema', missing, 'an unbound Claude worker requires its structured final schema'
    yield 'effort', {**seed, 'effort': 'ultra'}, 'Claude effort must be low, medium, high, xhigh or max'
    for value in ('true', 0, 1, None, [], {}):
        yield 'lock:' + repr(value), {**seed, 'claude_only_assigned_model': value}, 'claude_only_assigned_model must be a boolean'
    yield 'model', {**seed, 'model': 'haiku', 'claude_only_assigned_model': True}, 'claude_only_assigned_model requires a full Claude model ID'
