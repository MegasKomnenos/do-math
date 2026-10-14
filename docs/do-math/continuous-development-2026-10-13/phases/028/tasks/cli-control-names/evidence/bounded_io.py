from pathlib import Path
import sys, json, hashlib, re, ast
REPO=Path('C:/math')
RUN=REPO/'docs/do-math/continuous-development-2026-10-13'
OUT=RUN/'phases/028/tasks/cli-control-names/evidence'
def read(p): return p.read_text(encoding='utf-8-sig')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value): (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def resolve(ref):
    root,rel=ref.split(':',1)
    return (REPO if root=='repo' else RUN)/rel.split('#')[0]
mode=sys.argv[1] if len(sys.argv)>1 else None
if mode=='start':
    previous=json.loads(read(RUN/'phases/027/manager-evidence/source-inspected.json'))
    print('source-inspected shape',type(previous).__name__, list(previous)[:8] if isinstance(previous,dict) else previous[:1])
    save('source-start.json', {str(p.relative_to(REPO)).replace('\\','/'):digest(p) for p in [resolve(k) if ':' in k else REPO/k for k in (previous.get('files',previous) if isinstance(previous,dict) else [])] if p.is_file()})
    phase=json.loads(read(RUN/'phases/028/phase.json'))
    task=next(t for t in phase['tasks'] if t['id']=='cli-control-names')
    refs=task['inputs']+['run:context.md','run:plan.md','run:seams.md','run:phases/028/phase.json','run:phases/028/tasks/cli-control-names/objective.md','repo:services/continuous-development/protocol.md']
    save('input-profile.json',[{'ref':r,'sha256':digest(resolve(r)),'bytes':resolve(r).stat().st_size} for r in refs])
elif mode=='shape':
    for ref in sys.argv[2:]:
        p=resolve(ref); obj=json.loads(read(p))
        print(ref,digest(p),type(obj).__name__)
        if isinstance(obj,dict):
            print({k:(list(v)[:8] if isinstance(v,dict) else {'length':len(v),'first':v[:1]} if isinstance(v,list) else v) for k,v in obj.items()})
elif mode=='read':
    ref=sys.argv[2]; lines=read(resolve(ref)).splitlines(); start=int(sys.argv[3]) if len(sys.argv)>3 else 1; end=int(sys.argv[4]) if len(sys.argv)>4 else len(lines)
    print(ref,'SHA',digest(resolve(ref)))
    for i in range(start-1,min(end,len(lines))): print(f'{i+1}: {lines[i]}')
elif mode=='slices':
    assignment=next(t for t in json.loads(read(RUN/'phases/028/assignments.json'))['tasks'] if t['task']=='cli-control-names')
    doc=resolve(assignment['documents'][0]); lines=read(doc).splitlines(); headings=[]; fence=False
    for i,line in enumerate(lines):
        if line.startswith('```'): fence=not fence
        if not fence and re.match(r'^#{2,3} ',line): headings.append((i+1,line))
    rows=[]
    for s in assignment['slices']:
        start=1 if s['heading']=='도입' else next(i for i,h in headings if h==s['heading'])
        end=next((i-1 for i,h in headings if i>start),len(lines))
        block='\n'.join(lines[start-1:end])
        occurrences=[]; fenced=False; language=None
        for line_no in range(start,end+1):
            line=lines[line_no-1]
            if line.startswith('```'): fenced=not fenced; language=line[3:].strip() if fenced else None; continue
            if fenced:
                tokens=(list(re.finditer(r'"([A-Za-z_][A-Za-z_0-9-]*)"',line)) if language=='json' else list(re.finditer(r'(?:--[a-z][a-z-]*|\b[A-Za-z_][A-Za-z_0-9.:-]*)',line)))
                for m in tokens: occurrences.append({'line':line_no,'column':m.start()+1,'surface':m.group(0),'name':m.group(1) if language=='json' else m.group(0),'form':'fence:'+str(language)})
            else:
                for m in re.finditer(r'`([^`]+)`',line): occurrences.append({'line':line_no,'column':m.start()+1,'surface':m.group(1),'name':m.group(1),'form':'inline/table'})
        rows.append({**s,'current_start':start,'current_end':end,'document_sha256':digest(doc),'section_sha256':hashlib.sha256(block.encode()).hexdigest(),'occurrences':occurrences})
    save('section-inventory.json',rows)
    print(json.dumps([{'id':r['id'],'heading':r['heading'],'lines':[r['current_start'],r['current_end']],'occurrences':len(r['occurrences'])} for r in rows],ensure_ascii=False,indent=2))
