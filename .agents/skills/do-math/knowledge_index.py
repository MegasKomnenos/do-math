"""Render a navigation index from published records, without rewriting summaries."""

from collections import defaultdict
import json
import re


def plain(value):
    """Author text stays readable as raw text; escape only what could hide or relink it when rendered."""
    return re.sub(r'([\\`<\[\]])', r'\\\1', ' '.join(value.split()))


def record_link(record, label=None):
    return f'[{label or record}]({record}/output.json)'


def render_index(records, status=None, glossary=None):
    """records are (id, manifest) pairs in publication order; status and glossary are
    the latest plan id when that plan has research-status.md or glossary.md."""
    by_id = dict(records)
    replaced = defaultdict(list)
    reviews = defaultdict(list)
    peers = defaultdict(list)
    bundles = defaultdict(list)
    for rid, data in records:
        for old in data['supersedes']:
            replaced[old].append(rid)
        if data['category'] == 'review' and data['target']['kind'] == 'research':
            reviews[data['target']['record']].append(rid)
        elif data['category'] == 'peer':
            peers[data['target']['record']].append(rid)
        elif data['category'] == 'review' and data['target']['kind'] == 'bundle':
            bundles[data['target']['work']].append(rid)
    labels = {'research': '연구', 'explore': '탐구', 'review': '검토', 'plan': '계획'}
    lines = ['# 공개 지식 색인', '',
             '실행기가 공개 기록에서 생성한 탐색용 목록이다. 제목·요약은 작성자의 원문이며, '
             '요약 판정은 각 검토 기록의 `overview_assessment` 값으로, 연구의 소개가 검토된 결과 범위에 부합하는지를 나타낸다. '
             '`supported`가 연구 목표 전체의 해결이나 모든 결과의 Lean 인증을 뜻하지는 않는다. '
             '결과별 수학적 판정·Lean 판정·해설과의 정합성 및 그 근거는 연결된 검토 원문에서 확인한다.', '']
    lines += ['동료는 산출물을 독립적으로 읽고 수학을 다룬 응답이다. 동료의 새 주장도 뒤의 검토 전에는 미인증이다. '
              '묶음 검토는 작업과 동료를 함께 판정하며, 탐구의 관측·추측 전체를 일괄 인증하지 않는다.', '']
    if status:
        lines += [f'현재 연구 상태: [{status}/research-status.md]({status}/research-status.md)'
                  ' (마지막 계획의 연구 현황)', '']
    if glossary:
        lines += [f'용어 정본: [{glossary}/glossary.md]({glossary}/glossary.md)'
                  ' (마지막 계획이 갱신한 수학적 대상·기호의 정의)', '']
    entries = [(rid, data) for rid, data in records if data['category'] not in ('review', 'peer')]
    lines += [f'공개 기록 {len(records)}개 · 색인 항목 {len(entries)}개 (동료·검토 독립 항목 제외) · 공개 순서 · '
              '각 기록의 `output.json`에서 해설·증명·계산 자료로 이동한다.', '']
    goal_reviews = [rid for rid, data in records
                    if data['category'] == 'review' and data['target']['kind'] == 'goal'
                    and rid not in replaced]
    if goal_reviews:
        lines += ['목표 검토: ' + ', '.join(
            record_link(rid) + ' · ' + by_id[rid]['goal']['verdict'] for rid in goal_reviews), '']
    for rid, data in entries:
        overview = data['overview']
        lines += [f"## {plain(overview['title'])}", '',
                  f"{labels[data['category']]} · {record_link(rid)}", '', plain(overview['summary']), '']
        if rid in replaced:
            lines += ['대체됨: ' + ', '.join(record_link(x) for x in replaced[rid]) + '.', '']
        if data['supersedes']:
            lines += ['대체한 기록: ' + ', '.join(record_link(x) for x in data['supersedes']) + '.', '']
        if data['category'] in ('research', 'explore'):
            for peer_id in peers[rid]:
                lines += ['- ' + record_link(peer_id, '동료 ' + peer_id) + ' · '
                          + plain(by_id[peer_id]['overview']['title'])]
            active = [r for r in reviews[rid] if r not in replaced]
            active_bundles = [r for r in bundles[rid] if r not in replaced]
            if not active and not active_bundles:
                lines += ['검토 전: 현재 유효한 독립 검토 기록이 없다.', '']
            judgments = defaultdict(set)
            for review_id in active:
                review = by_id[review_id]
                ov = review['overview_assessment']
                lines.append(f"- {record_link(review_id, '현재 검토 ' + review_id)} · 요약 판정: {ov['verdict']}")
                judgments['overview'].add(ov['verdict'])
                # Keep result-level conflict detection without displaying verdict counts.
                for key in ('assessment', 'lean', 'alignment', 'terminology'):
                    for result in review['results']:
                        judgments[result['result'] + '/' + key].add(result[key]['verdict'])
            for review_id in active_bundles:
                review = by_id[review_id]
                scopes = []
                for row in review['overview_assessments']:
                    source = row['record']
                    verdict = row['assessment']['verdict']
                    scopes.append(('작업' if source == rid else '동료') + ' 소개 ' + verdict)
                    judgments['overview' if source == rid else source + '/overview'].add(verdict)
                lines += ['- ' + record_link(review_id, '현재 검토 ' + review_id) + ' · ' + ', '.join(scopes)]
                for row in review['results']:
                    source = row['source']
                    name = source.get('result') or json.dumps(source, ensure_ascii=False, sort_keys=True)
                    if source['record'] != rid:
                        name = source['record'] + '/' + name
                    for key in ('assessment', 'lean', 'alignment'):
                        judgments[name + '/' + key].add(row[key]['verdict'])
            conflicts = []
            for key, values in judgments.items():
                if any({a, b} <= values for a, b in [('supported', 'not_supported'),
                                                    ('accepted', 'rejected'), ('matches', 'differs')]):
                    conflicts.append(key)
            if conflicts:
                lines += ['', '상충: ' + ', '.join(plain(x) for x in sorted(conflicts)) + '. 현재 검토 원문을 함께 확인한다.']
            if active or active_bundles or peers[rid]:
                lines.append('')
        if data['category'] == 'explore':
            lines += ['탐구 기록: 관측·추측과 검토된 명제를 구분한다. 검토의 수용은 명시된 주장과 범위에만 적용된다.', '']
    return '\n'.join(lines).rstrip() + '\n'
