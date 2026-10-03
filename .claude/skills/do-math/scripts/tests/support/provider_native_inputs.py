"""Malformed native message shapes retain each normal provider envelope."""
from copy import deepcopy
from support.ingress import malformed

NATIVE_ROWS = (
    ('public', {'type': 'public_message', 'message': {'role': 'assistant', 'content': '정상'}},
     'message', 'review_engine._record_review_observation:public_message'),
    ('codex', {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': '정상'}},
     'item', 'review_engine._record_review_observation:item.completed'),
    ('assistant', {'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': '정상'}]}},
     'message', 'review_engine._record_review_observation:assistant'),
    ('user', {'type': 'user', 'message': {'content': [{'type': 'text', 'text': '정상'}]}},
     'message', 'review_engine._record_review_observation:user'),
)


def nested_native_rows():
    """각 행의 전제는 identity_review, review_cycle_id, slot이 유효한 실행이다.

비객체 중첩값은 각 공개 외곽의 ValueError 반려 계약을 검사한다.
정상 외곽 보존은 단위 시험, 실제 소유자 전건 반려 계약은 KD-0900에서 검사한다.
경로는 이 형식에 없으므로 경로 이탈 축은 작업 공간/수송 담당이다.
"""
    for name, seed, field, handler in NATIVE_ROWS:
        for label, value in malformed({'type': 'object'}):
            event = deepcopy(seed)
            event[field] = value
            yield name + ':' + label, event, field, handler


def native_rejection_cases():
    """review_engine의 네 외곽과 content/text 하위 좌표의 잘못된 입력 전건.

    비객체 다섯 값은 공통 malformed 정본에서 온다. 빈 content와 비객체
    block은 현재 공개 메시지 추출기가 무시하는 값이므로 정상 대조에서 본다.
    """
    yield from ((label, event) for label, event, _, _ in nested_native_rows())
    for kind in ('assistant', 'user'):
        for label, value in (('null', None), ('zero', 0)):
            yield kind + ':content:' + label, {'type': kind, 'message': {'content': value}}
        yield kind + ':missing-text', {'type': kind, 'message': {'content': [{'type': 'text'}]}}
    yield 'codex:missing-text', {'type': 'item.completed', 'item': {'type': 'agent_message'}}
    for label, role in malformed({'type': 'string'}):
        yield 'public:role:' + label, {'type': 'public_message', 'message': {'role': role, 'content': '내용'}}
    for label, message in (('missing-content', {'role': 'assistant'}),
                           ('invalid-role', {'role': 'outside', 'content': '내용'})):
        yield 'public:' + label, {'type': 'public_message', 'message': message}
