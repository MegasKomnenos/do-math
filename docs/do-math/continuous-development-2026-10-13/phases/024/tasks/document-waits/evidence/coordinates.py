from work import *
import ast,re,zipfile
archive=json.loads((RUN/'phases/023/manager-evidence/preservation.json').read_text(encoding='utf-8-sig'))
start=json.loads((E/'start.json').read_text(encoding='utf-8'))
checks=[]
with zipfile.ZipFile(REPO/archive['archive']) as z:
    for rel,mutable in [('.claude/skills/do-math/scripts/tests/support/doc_code.py',{'field_schemas','scoped_field_issues'}),
                        ('.claude/skills/do-math/scripts/tests/support/engine_context.py',set())]:
        raw=z.read(rel); assert hashlib.sha256(raw).hexdigest()==start[rel]['sha256']
        def functions(raw):
            text=raw.decode('utf-8'); lines=text.splitlines(keepends=True)
            return {n.name:''.join(lines[n.lineno-1:n.end_lineno]) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
        before=functions(raw); after=functions((REPO/rel).read_bytes())
        changed=sorted(n for n in before if before[n]!=after.get(n))
        assert set(changed)==mutable,(rel,changed)
        checks.append({'path':rel,'changed_existing_functions':changed,'unchanged_existing_functions':sorted(set(before)-mutable),
                       'added_functions':sorted(set(after)-set(before))})
packets=json.loads((E/'followup-packets-input.json').read_text(encoding='utf-8'))['packets']
coordinates=[]
for packet in packets:
    if packet['id'] not in ('P09','P11'):continue
    for old in packet['original_document_locations']:
        path=REPO/old['path'].split(':',1)[1]; lines=path.read_text(encoding='utf-8').splitlines()
        needle='| `decision_value_is` |' if packet['id']=='P09' else '- 계획과 착수:'
        n,line=next((n,line) for n,line in enumerate(lines,1) if line.startswith(needle))
        title=next((line for line in reversed(lines[:n-1]) if line.startswith('#')),None)
        coordinates.append({'packet':packet['id'],'historical':old,'current_line':n,'current_heading':title,'current_text':line,
            'path_sha256':digest(path)['sha256']})
save('change-coordinates.json',{'helper_preservation':checks,'packet_coordinates':coordinates})
temp=Path('C:/t/p024')
p=subprocess.run(['git','rev-parse','--show-toplevel'],cwd=temp,capture_output=True)
assert p.returncode!=0
save('temp-parent-git.json',{'argv':['git','rev-parse','--show-toplevel'],'cwd':str(temp),'exit_code':p.returncode,
    'stdout':p.stdout.decode(),'stderr':p.stderr.decode()})
print('Existing helper functions preserved; exact P09/P11 text coordinates; outside-repo parent TEMP confirmed')
