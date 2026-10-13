"""Trace original requirement locators and historical report availability."""
import json
import re
from pathlib import Path
from investigate import REPO, RUN, OUT, PREFIX, sha, write, git


req = json.loads((RUN/'phases/001/tasks/closure-map/evidence/requirement-state.json').read_text(encoding='utf-8-sig'))
rows = []
for i, row in enumerate(req['rows']):
    text = json.dumps(row, ensure_ascii=False)
    if any(term in text for term in ('측정', '선택 색인', '함수 진입', 'P10', 'P11')):
        rows.append(dict(selector='/rows/'+str(i), id=row['id'], group=row['group'],
                         original=row['original'], sources=row['sources'], question=row['question'],
                         next_action=row['next_action']))
write('requirement-trace.json', dict(
    p10_p11_literal_occurrences=len(re.findall(r'P10|P11', json.dumps(req, ensure_ascii=False))),
    interpretation='P10/P11 are the exact-baseline test/history labels, not IDs in the 103-row requirement-state population. Do not invent matching requirement IDs.',
    related_rows=rows))
print(json.dumps([{'id': r['id'], 'original':r['original'], 'sources':r['sources']} for r in rows], ensure_ascii=False, indent=2))
integration=json.loads((OUT/'b56-original-record.json').read_text(encoding='utf-8'))
reports=[]
for key in ('changed_area','structure','timing_red','exact_baseline_comparison'):
    record=integration[key]
    p=Path(record['path'])
    reports.append(dict(selector='/current_work/measurement_integration/'+key,
                        path=str(p), exists=p.is_file(), expected_sha256=record['sha256'],
                        actual_sha256=sha(p.read_bytes()) if p.is_file() else None,
                        historical_counts=record['counts'], historical_seconds=record['total_seconds']))
write('historical-report-availability.json', reports)
fix='bbe64043f49d46fb7c3b6e768b99a8acbaa125cf'
git('fix-memory', 'show', fix+':기억/layer1/M-0472.md')
git('fix-board-md', 'show', fix, '--', 'docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.md')
print(json.dumps(reports,ensure_ascii=False,indent=2))
