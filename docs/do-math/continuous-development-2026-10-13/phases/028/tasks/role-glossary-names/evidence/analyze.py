import ast
import hashlib
import json
import re
from pathlib import Path

ROOT = Path('C:/math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = RUN / 'phases/028/tasks/role-glossary-names/evidence'
SKILL = ROOT / '.claude/skills/do-math'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def snapshot():
    prior = read(RUN / 'phases/027/manager-evidence/source-inspected.json')
    return {p: sha(ROOT / p) if (ROOT / p).is_file() else None for p in prior}

def setup():
    start = snapshot()
    save('source-start.json', start)
    prior = read(RUN / 'phases/027/manager-evidence/source-inspected.json')
    save('source-comparison.json', {'files':len(start),'differences': [p for p in prior if prior[p] != start[p]]})
    phase = read(RUN / 'phases/028/phase.json')
    task = next(t for t in phase['tasks'] if t['id']=='role-glossary-names')
    save('input-profiles.json', [{'reference':ref,'sha256':sha((ROOT if ref.startswith('repo:') else RUN)/ref.split(':',1)[1]),'bytes':((ROOT if ref.startswith('repo:') else RUN)/ref.split(':',1)[1]).stat().st_size} for ref in task['inputs']])
    a = next(t for t in read(RUN/'phases/028/assignments.json')['tasks'] if t['task']=='role-glossary-names')
    packet = next(p for p in read(RUN/'phases/001/tasks/document-closeout/evidence/followup-packets.json')['packets'] if p['id']=='N01')
    originals = {s['id']:s for s in packet['required_slices']}
    mapped = []
    for s in a['slices']:
        p = ROOT/s['document'].split(':',1)[1]
        lines = p.read_text(encoding='utf-8-sig').splitlines()
        heads=[i for i,line in enumerate(lines) if re.match(r'^#{1,6} ',line)]
        if s['heading']=='도입':
            i=0
        else:
            hits=[i for i in heads if lines[i]==s['heading']]
            assert len(hits)==1,(s,hits)
            i=hits[0]
        end=next((n for n in heads if n>i),len(lines))
        body=lines[i:end]
        occurrences=[]
        fence=False
        for ln,line in enumerate(body,i+1):
            if line.lstrip().startswith('```'): fence=not fence
            if not fence:
                occurrences.extend({'line':ln,'name':m.group(1)} for m in re.finditer(r'(?<!`)`([^`\n]+)`(?!`)',line))
        mapped.append({**s,'current_start':i+1,'current_end':end,'sha256':sha(p),'body_sha256':hashlib.sha256('\n'.join(body).encode()).hexdigest(),'historical_tokens':originals[s['id']]['distinct_tokens'],'inline_occurrences':occurrences,'text':'\n'.join(body)})
    assert len(mapped)==195 and len({s['id'] for s in mapped})==195
    save('slice-map.json',mapped)
    c3=read(RUN/'phases/027/tasks/doc-policy/evidence/c3/report.json')
    hashes=c3['source_sha256']
    diffs=[p for p,h in hashes.items() if sha(SKILL/'scripts'/p)!=h]
    rows=[row for g in c3['reports'] for row in g['rows'] if row['id'].startswith('structure.test_doc_code.')]
    assert len(rows)==38 and all(row['outcome']=='passed' for row in rows) and len(hashes)==875 and not diffs
    save('reused-rows.json',{'reference':'run:phases/027/tasks/doc-policy/evidence/c3/report.json','sha256':sha(RUN/'phases/027/tasks/doc-policy/evidence/c3/report.json'),'python_files':len(hashes),'python_differences':diffs,'changed_during_run':c3['changed_during_run'],'rows':rows,'meaning':'Historical execution only. Current Python hashes match all 875 files; new names are not thereby automatically tested.'})
    print(json.dumps({'source_files':len(start),'source_differences':sum(prior[p]!=start[p] for p in prior),'slices':len(mapped),'inline_occurrences':sum(len(s['inline_occurrences']) for s in mapped),'reused_rows':len(rows),'python_files':len(hashes)},ensure_ascii=False))

if __name__=='__main__':
    setup()
