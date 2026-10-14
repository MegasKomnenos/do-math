import hashlib
import json
from pathlib import Path
import re
import sys

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = RUN / 'phases/026/tasks/reference-names/evidence'
DOCS = ['공통-실행', '과제-착수조건', '모델과-실행예산', '입력-소비자', '자기-점검', '지식-저작과-재사용', '학술자료-활용']

def write(name, data):
    (OUT/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def snapshot(name):
    expected = json.loads((RUN/'phases/025/manager-evidence/source-inspected.json').read_text(encoding='utf-8-sig'))
    current = {p: hashlib.sha256((REPO/p).read_bytes()).hexdigest() if (REPO/p).is_file() else None for p in expected}
    mismatches = {p: {'expected': h, 'actual': current[p]} for p,h in expected.items() if current[p] != h}
    write(name, {'baseline':'run:phases/025/manager-evidence/source-inspected.json', 'count':len(current), 'mismatches':mismatches, 'sha256':current})
    print(name, len(current), 'mismatches', len(mismatches))
    if mismatches: print(json.dumps(mismatches, ensure_ascii=False))
    return not mismatches

if __name__ == '__main__':
    if sys.argv[1] in ('start','end'):
        ok=snapshot('source-'+sys.argv[1]+'.json')
        if sys.argv[1]=='end':
            prior=json.loads((OUT/'inputs-read.json').read_text(encoding='utf-8'))
            errors=[]
            for ref,item in prior.items():
                root=REPO if ref.startswith('repo:') else RUN
                path=root/ref.split(':',1)[1]
                if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
                    errors.append(ref)
            start=json.loads((OUT/'source-start.json').read_text(encoding='utf-8'))
            end=json.loads((OUT/'source-end.json').read_text(encoding='utf-8'))
            equal=start['sha256']==end['sha256']
            write('end-protection.json',{'protected_inputs':len(prior),'mismatches':errors,'start_end_sha_equal':equal})
            print('protected inputs',len(prior),'mismatches',len(errors),'start/end equal',equal)
            ok=ok and not errors and equal
        raise SystemExit(0 if ok else 1)
    if sys.argv[1] == 'inventory':
        rows=[]
        for name in DOCS:
            path=f'.claude/skills/do-math/references/{name}.md'
            lines=(REPO/path).read_text(encoding='utf-8-sig').splitlines()
            section=''; fence=None
            for n,line in enumerate(lines,1):
                if line.startswith('#'): section=line
                if line.lstrip().startswith('```'):
                    if fence is None: fence={'start':n, 'language':line.lstrip()[3:], 'lines':[]}
                    else:
                        rows.append({'path':path,'line':fence['start'],'section':section,'kind':'fence','text':'\n'.join(fence['lines']),'end':n}); fence=None
                elif fence is not None: fence['lines'].append(line)
                for token in re.findall(r'(?<!`)`([^`]+)`(?!`)',line):
                    rows.append({'path':path,'line':n,'section':section,'kind':'inline','text':token})
            print(name,len(lines),'lines')
        write('occurrences.json',rows)
        print('occurrences',len(rows))
