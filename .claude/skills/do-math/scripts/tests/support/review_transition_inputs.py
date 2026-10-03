"""실제 순수 전이로 만드는 정상 단계 입력. 제품 함수를 대체하지 않는다."""
from copy import deepcopy

from do_math import review_cycle as rc
from support.review_inputs import scoped_start, review_stage_output


def cycle_at(stage='initial'):
    cycle = scoped_start({'revision': 1, 'statement': '합성 명제'}, reviewers=2, max_rounds=2)
    cycle['id'] = 'RC-review-input'
    if stage == 'initial':
        return cycle
    for index in range(2):
        action = rc.next_actions(cycle)[0]
        output = review_stage_output(cycle, 'initial', decision='mismatch', findings=[
            {'id': 'finding-' + str(index), 'statement': '범위 반례', 'evidence': ['proposal']}])
        cycle = rc.accept_result(cycle, action, output, 'initial-ex-' + str(index))
    if stage == 'organize':
        return cycle
    action = rc.next_actions(cycle)[0]
    cycle = rc.accept_result(cycle, action, review_stage_output(cycle, 'organize'), 'organize-ex')
    if stage == 'judge':
        return cycle
    for index in range(3):
        action = rc.next_actions(cycle)[0]
        output = review_stage_output(cycle, 'judge', decision='match', issue_verdicts=[
            {'issue_id': key, 'decision': 'rejected', 'reason': '원문이 반례를 반박', 'evidence': ['proposal']}
            for key in cycle['issues']])
        cycle = rc.accept_result(cycle, action, output, 'judge-ex-' + str(index))
    if stage != 'answer':
        raise ValueError('지원하지 않는 정상 입력 단계: ' + stage)
    return cycle


def stage_input(stage):
    cycle = cycle_at(stage)
    action = rc.next_actions(cycle)[0]
    return cycle, action, review_stage_output(cycle, stage)


def replace_path(value, path, replacement):
    """정상 생산물 사본의 한 좌표만 바꾼다."""
    changed = deepcopy(value)
    parent = changed
    for key in path[:-1]:
        parent = parent[key]
    parent[path[-1]] = deepcopy(replacement)
    return changed
