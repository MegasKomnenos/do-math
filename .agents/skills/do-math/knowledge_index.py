"""Render a navigation index from published records, without rewriting summaries."""

from collections import Counter, defaultdict
import re


def plain(value):
    """Author text stays readable as raw text; escape only what could hide or relink it when rendered."""
    return re.sub(r'([\\`<\[\]])', r'\\\1', ' '.join(value.split()))


def record_link(record, label=None):
    return f'[{label or record}]({record}/output.json)'


def render_index(records, status=None):
    """records are (id, manifest) pairs in publication order; status is the latest plan id with research-status.md."""
    by_id = dict(records)
    replaced = defaultdict(list)
    reviews = defaultdict(list)
    for rid, data in records:
        for old in data['supersedes']:
            replaced[old].append(rid)
        if data['category'] == 'review' and data['target']['kind'] == 'research':
            reviews[data['target']['record']].append(rid)
    labels = {'research': '연구', 'review': '검토', 'plan': '계획'}
    lines = ['# 공개 지식 색인', '',
             '실행기가 공개 기록에서 생성한 탐색용 목록이다. 제목·요약은 작성자의 원문이며, '
             '판정은 검토 기록의 명시 범위를 보여 준다. 요약 판정은 각 검토 기록의 `overview_assessment` 값이며 '
             '그 근거와 작성 경위는 해당 검토 기록에서 읽는다. 실제 근거로 사용할 때에는 원문과 현재 검토를 읽는다.', '']
    if status:
        lines += [f'현재 연구 상태와 주요 정의: [{status}/research-status.md]({status}/research-status.md)'
                  ' (마지막 계획의 연구 현황)', '']
    lines += [f'기록 {len(records)}개 · 공개 순서 · 각 기록의 `output.json`에서 해설·증명·계산 자료로 이동한다.', '']
    for rid, data in records:
        overview = data['overview']
        lines += [f"## {plain(overview['title'])}", '',
                  f"{labels[data['category']]} · {record_link(rid)}", '', plain(overview['summary']), '']
        if rid in replaced:
            lines += ['대체됨: ' + ', '.join(record_link(x) for x in replaced[rid]) + '.', '']
        if data['supersedes']:
            lines += ['대체한 기록: ' + ', '.join(record_link(x) for x in data['supersedes']) + '.', '']
        if data['category'] == 'research':
            active = [r for r in reviews[rid] if r not in replaced]
            if not active:
                lines += ['검토 전: 현재 유효한 독립 검토 기록이 없다.', '']
            judgments = defaultdict(set)
            for review_id in active:
                review = by_id[review_id]
                ov = review['overview_assessment']
                lines.append(f"- {record_link(review_id, '현재 검토 ' + review_id)} · 요약: {ov['verdict']}")
                judgments['overview'].add(ov['verdict'])
                for key in ('assessment', 'lean', 'alignment'):
                    counts = Counter(r[key]['verdict'] for r in review['results'])
                    values = ', '.join(f'{v} {n}' for v, n in sorted(counts.items())) or '결과 없음'
                    lines.append(f'  {key}: {values}.')
                    for result in review['results']:
                        judgments[result['result'] + '/' + key].add(result[key]['verdict'])
            conflicts = []
            for key, values in judgments.items():
                if any({a, b} <= values for a, b in [('supported', 'not_supported'),
                                                    ('accepted', 'rejected'), ('matches', 'differs')]):
                    conflicts.append(key)
            if conflicts:
                lines += ['', '상충: ' + ', '.join(plain(x) for x in sorted(conflicts)) + '. 현재 검토 원문을 함께 확인한다.']
            if active:
                lines.append('')
        elif data['category'] == 'review':
            target = data['target']
            lines += [('대상: ' + record_link(target['record']) if target['kind'] == 'research'
                       else '목표 검토: ' + data['goal']['verdict']), '']
    return '\n'.join(lines).rstrip() + '\n'
