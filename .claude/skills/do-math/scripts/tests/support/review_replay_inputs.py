"""조사 완료·예산 종료 증거를 실제 엔진·작업자·저장 경로에서 만든다."""
import json
from pathlib import Path
from support.sim import Sim, built
from support.engine_purpose import PURPOSE_CONFIG
from support.engine_lifecycle import clear_work
from support.review_research import InvestigationResponder, research_policy


class SuppliedSourceResponder(InvestigationResponder):
    """모델 응답 경계에서 실제 초기화가 보존한 원천도 조사 대상으로 고른다."""
    def respond(self, role, ctx, workspace):
        output = super().respond(role, ctx, workspace)
        if role == 'identity_review':
            path = workspace / 'activity-extensions.json'
            if path.exists():
                extensions = json.loads(path.read_bytes())
                for request in extensions.get('research_requests', []):
                    request['source_refs'].append('source:review-source.txt')
                path.write_text(json.dumps(extensions, ensure_ascii=False), encoding='utf-8')
        return output


def _build(root, shared, *, closure, budget_only=False):
    limit = 1 if closure and not budget_only else 3
    source = Path(shared) / 'review-source.txt'
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text('공급된 정확 원천: 자연수의 덧셈 항등식.', encoding='utf-8')
    sim = Sim(root, shared=shared, sources=[source], config={**PURPOSE_CONFIG, 'review_research_limit': limit})
    policy = research_policy(2, limit)
    if budget_only:
        policy['activity_execution_limit'] = 15
    sim.activate(review_policy=policy)
    responder = SuppliedSourceResponder(repeat=closure)
    sim.model.responder = responder
    for _ in range(45):
        sim.step()
        if responder.failures:
            raise AssertionError('조사 생산자의 입력 계약 실패: ' + repr(responder.failures))
        cycles = list(sim.runtime['review_cycles'].values())
        if cycles and cycles[0]['status'] != 'working':
            break
        if sim.runtime['status'] in {'paused', 'closed', 'waiting'}:
            raise AssertionError('조사 결말 전에 흐름 정지: ' + repr(sim.waiting()))
    else:
        raise AssertionError('45단계 안에 조사 결말에 도달하지 못함')
    cycle = cycles[0]
    expected = 'unresolved' if closure else 'match'
    if cycle['decision'] != expected or len(cycle['research']) != 1:
        raise AssertionError('조사 생산자의 결말 불일치: ' + repr((cycle['decision'], cycle['research'])))
    clear_work(sim)
    return sim


def replay_sim(*, closure=False, budget_only=False):
    return built('review-replay-evidence', _build, closure=closure, budget_only=budget_only)
