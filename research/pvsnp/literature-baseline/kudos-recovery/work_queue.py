"""Derive resumable work from results; legacy pass markers never imply completion.

This checks declared work and review bindings, not the semantic truth of a review.
Workers inspect the cited evidence before recording a review.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

VERSION = 'remaining-work/1'
COMPONENTS = ('identity', 'abstract', 'fulltext')
KINDS = {'search', 'source', 'pdf', 'review', 'repair'}
OPEN = {'pending', 'retry', 'needs_review'}
CLOSED = {'done', 'not_needed'}


def component_basis(record, component):
    keys = ['paper_id', 'version_sha256', 'identity', component]
    value = {key: record.get(key) for key in keys}
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def known_paths(record):
    artifacts = list(record.get('evidence', []))
    for component in ('abstract', 'fulltext'):
        artifacts.extend(record.get(component, {}).get('artifacts', []))
    return {a.get('path') for a in artifacts if isinstance(a, dict) and a.get('path')}


def pending_work(record):
    if not record:
        return [{'key': 'collect', 'kind': 'search', 'reason': 'No result exists.'}]
    pending = []

    def add(key, kind, reason):
        pending.append({'key': key, 'kind': kind, 'reason': reason})

    state = record.get('work_state') or {}
    if not isinstance(state, dict) or state.get('version') != VERSION:
        add('assess_saved_evidence', 'review', 'Assess saved evidence and build current tasks before any browser replay.')
        state = {}
    paths = known_paths(record)
    tasks = state.get('tasks')
    if not isinstance(tasks, list):
        tasks = []
        add('task_inventory', 'review', 'Inventory required queries, pages, sources, PDF candidates and content reviews.')
    seen = set()
    for task in tasks:
        if not isinstance(task, dict):
            add('invalid_task', 'repair', 'Task must be an object.'); continue
        key, kind, status = task.get('key'), task.get('kind'), task.get('status')
        if not key or key in seen or kind not in KINDS or status not in OPEN | CLOSED or not task.get('target'):
            add(str(key or 'invalid_task'), 'repair', 'Task key, kind, status or target is invalid.'); continue
        seen.add(key)
        if status in OPEN:
            add(key, kind, task.get('reason') or 'Task remains open.')
        elif not task.get('reason') or not task.get('evidence_paths') or not set(task['evidence_paths']) <= paths:
            add(key, 'review', 'Closing a task requires a reason and references to preserved evidence.')
        count_keys = ('discovered', 'attempted', 'remaining')
        if any(k in task for k in count_keys):
            counts = [task.get(k) for k in count_keys]
            if not all(type(n) is int and n >= 0 for n in counts) or counts[0] != counts[1] + counts[2]:
                add(key + ':counts', 'repair', 'discovered = attempted + remaining must hold for the same unit.')
            elif status == 'done' and counts[2]:
                add(key + ':remaining', kind, 'Unvisited candidates/pages cannot be marked done.')
    reviews = state.get('reviews') or {}
    if not isinstance(reviews, dict):
        reviews = {}
    for component in COMPONENTS:
        status = record.get(component, {}).get('status')
        allowed = {'confirmed', 'not_found'} if component == 'identity' else {'found', 'not_found', 'unavailable'}
        if status not in allowed:
            add(component, 'review' if component == 'identity' else 'source', component + ' is unresolved.')
        review = reviews.get(component) or {}
        if not isinstance(review, dict) or review.get('basis_sha256') != component_basis(record, component):
            add('review:' + component, 'review', 'Review the current component and identity; previous conclusion is absent or stale.')
        elif not review.get('reason') or not review.get('evidence_paths') or not set(review['evidence_paths']) <= paths:
            add('review:' + component, 'review', 'Component review needs a reason and preserved evidence references.')
        elif status in {'not_found', 'unavailable'} and review.get('scope_complete') is not True:
            add('scope:' + component, 'search', 'A negative conclusion requires completed required source scope.')
    if any(record.get(c, {}).get('status') in {'not_found', 'unavailable'} for c in COMPONENTS):
        if not {'search', 'source'} <= {t.get('kind') for t in tasks if isinstance(t, dict)}:
            add('negative_scope_inventory', 'review', 'Record actual search scope and source/link assessment for negative conclusions.')
    for flag in ('unvisited_link', 'unvisited_search_pages', 'collection_error', 'needs_mathscinet_revisit'):
        if record.get(flag):
            add('legacy:' + flag, 'review', 'Resolve or evidence-back supersession of the retained ' + flag + ' before completion.')
    return pending


def build_queue(assignment_path):
    assignment_path = Path(assignment_path).resolve()
    assignment = json.loads(assignment_path.read_text(encoding='utf-8-sig'))
    base = next(p for p in assignment_path.parents if (p / 'catalog/abstract-format-partition/input.jsonl').exists())
    result_dir = base / assignment['worker_root'] / 'results'
    entries, totals = [], Counter()
    for line in (base / assignment['members_path']).read_text(encoding='utf-8-sig').splitlines():
        if not line.strip():
            continue
        paper = json.loads(line)
        path = result_dir / (paper['paper_id'] + '.json')
        try:
            record = json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else None
            work = pending_work(record)
        except (OSError, ValueError, TypeError, AttributeError):
            work = [{'key': 'repair_result', 'kind': 'repair', 'reason': 'Result is malformed; preserve and repair it.'}]
        totals['assigned'] += 1
        totals['with_result'] += int(path.exists())
        if work:
            entries.append({'paper_id': paper['paper_id'], 'tasks': work})
        else:
            totals['completion_candidates'] += 1
    totals['papers_with_remaining_work'] = len(entries)
    return {'version': VERSION, 'group_id': assignment['group_id'], 'counts': dict(totals), 'entries': entries}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assignment', required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = build_queue(args.assignment)
    if args.output:
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(report['counts']))
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
