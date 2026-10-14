import ast
import hashlib
import json
from pathlib import Path

REPO=Path('C:/math')
RUN=REPO/'docs/do-math/continuous-development-2026-10-13'
OUT=RUN/'phases/026/tasks/role-contract-names/evidence'
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name,value): (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

population=read(OUT/'population.json'); slices=read(OUT/'slice-map.json'); decisions=read(OUT/'decisions.json')
assert len(population)==11 and sum(d['lines'] for d in population)==1299
assert {s['id'] for s in slices}=={d['id'] for d in decisions} and len(decisions)==144
expected={(p['ref'],o['line'],o['text']) for p in population for o in p['occurrences']}
actual={(d['document'],n,b['name']) for d in decisions for b in d['bindings'] for n in b['lines']}
assert expected==actual, (expected-actual,actual-expected)
profiles=read(OUT/'source-profiles.json')
citations=[]
for profile in profiles.values():
    for kind in ('definitions','consumers','tests'):
        for row in profile[kind]:
            path=REPO/row['path'][5:]
            assert digest(path)==row['sha256']
            assert row['excerpt']
            citations.append((row['path'],row['symbol']))
for d in decisions:
    assert set(d['profiles'])<=set(profiles)
    for b in d['bindings']:
        assert b['owner'] and b['reason'] and b['source_profiles']
for item in read(OUT/'inputs.json'):
    root,relative=item['ref'].split(':',1)
    assert digest((REPO if root=='repo' else RUN)/relative)==item['sha256']

history=[]
for item in read(RUN/'phases/025/manager-evidence/history-check.json'):
    assert digest(REPO/item['path'])==item['sha256']
    history.append(item)
save('history-reuse.json',{'reports':history,'decision':'B110~B114의 명시 소유자/별칭/진단/배열 분리 성질과 019~025의 실제 반환 교체 slice만 재사용. PR24 전체 및 다른 N01/N02를 완료로 판정하지 않는다.',
    'preserved':'7개 원보고 SHA 대조; 역사 counts를 새 실행에 더하지 않음'})

reuse=[]
report_specs=[
 ('025','phases/025/tasks/document-trust/evidence/c2/report.json',('structure.test_doc_code.',)),
 ('023','phases/023/tasks/document-governance/evidence/c2/report.json',('structure.test_doc_code.',)),
 ('008','phases/008/tasks/document-recovery/evidence/canonical-joined-final/results/report.json',('boundary.test_operator_bootstrap_info.',)),
]
for phase,relative,prefixes in report_specs:
    path=RUN/relative
    report=read(path)
    rows=[row for group in report['reports'] for row in group['rows'] if row['id'].startswith(prefixes)]
    assert rows and all(row['outcome']=='passed' for row in rows)
    current_differences=[p for p,sha in report['source_sha256'].items()
        if digest(REPO/'.claude/skills/do-math/scripts'/p)!=sha]
    reuse.append({'phase':phase,'report':'run:'+relative,'sha256':digest(path),'rows':rows,
        'python_source_count':len(report['source_sha256']),'current_python_differences':current_differences,
        'scope':'025 문서 검사 rows는 현재875 Python 전건 동등성 확인. 008/023의 옛 전체 판본은 다르며 각 manager 검수/현재 불변 하위 경계와 지정 함수 성질만 재사용. 새 실행 아님.'})
save('reused-rows.json',reuse)
assert reuse[0]['current_python_differences']==[]

evidence={
 'documents':11,'slices':144,'inline_occurrences':sum(len(d['occurrences']) for d in population),
 'unique_document_line_token_coordinates':len(expected),'missing_coordinates':0,'extra_coordinates':0,
 'json_examples':len(read(OUT/'fence-decisions.json')),'source_profiles':len(profiles),
 'distinct_source_symbol_citations':len(set(citations)),
 'required_inputs_unchanged':len(read(OUT/'inputs.json')),'historical_reports_unchanged':len(history),
 'current_025_python_source_differences':0,
 'status':'pass',
 'limit':'This verifies evidence coverage, exact sources and existing report rows. It neither runs product modules nor validates mathematical meaning, actual reading compliance or new tests.'}
save('verification.json',evidence)
print(json.dumps(evidence,ensure_ascii=False))
