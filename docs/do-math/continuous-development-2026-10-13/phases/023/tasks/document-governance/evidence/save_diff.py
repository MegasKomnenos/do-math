from work import *
import difflib,ast
start=json.loads((E/'start.json').read_text(encoding='utf-8-sig'))
final=snapshot('diff-current')
allowed=json.loads((RUN/'phases/023/phase.json').read_text(encoding='utf-8-sig'))['tasks'][0]['writes']
changes=[p for p in sorted(set(start)|set(final)) if start.get(p)!=final.get(p)]
assert set(changes)<=set(allowed),set(changes)-set(allowed)
diffs=[]; rows=[]
for path in changes:
    original=E/'original'/path
    assert digest(original)==start[path]
    before=original.read_text(encoding='utf-8').splitlines(keepends=True)
    after=(REPO/path).read_text(encoding='utf-8').splitlines(keepends=True)
    if Path(path).name not in ('.timings.json','.timings-t3.json'):
        diffs.extend(difflib.unified_diff(before,after,fromfile='start/'+path,tofile='final/'+path))
    rows.append({'path':path,'start':start[path],'final':final[path]})
(E/'task-changes.diff').write_text(''.join(diffs),encoding='utf-8')
helpers=[]
for name,changed_functions,new_functions in [('doc_code.py',{'field_schemas','scoped_field_issues'},{'governance_field_issues'}),
    ('engine_context.py',set(),{'assert_governance_documents'})]:
    path='.claude/skills/do-math/scripts/tests/support/'+name
    def functions(source):
        return {n.name:ast.get_source_segment(source,n) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)}
    old=functions((E/'original'/path).read_text(encoding='utf-8'))
    new=functions((REPO/path).read_text(encoding='utf-8'))
    delta={key for key in old if old[key]!=new.get(key)}
    assert delta==changed_functions,(name,delta)
    assert set(new)-set(old)==new_functions
    helpers.append({'path':path,'changed_existing_functions':sorted(delta),'added_functions':sorted(set(new)-set(old)),
        'unchanged_existing_functions':sorted(set(old)-delta)})
save('change-coordinates.json',{'changes':rows,'helper_functions':helpers,'outside_writes':[],
    'runtime_unchanged':all(start[p]==final[p] for p in start if '/scripts/do_math/' in p),
    'product_documents_unchanged':all(start[p]==final[p] for p in start if '/do-math/' in p and Path(p).suffix=='.md')})
print('Changes',len(changes),'authorized; exact existing helper behavior preserved outside the four-owner delegation')
