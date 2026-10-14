from work import *
rows=[]
for phase in ('012','016','018','024'):
    earlier=json.loads((RUN/f'phases/{phase}/manager-evidence/source-inspected.json').read_text(encoding='utf-8-sig'))
    for name in ('formal.py','trust_validation.py','trust_inventory.py','formal_engine.py','lean_evidence.py'):
        relative='.claude/skills/do-math/scripts/do_math/'+name
        sha=digest(REPO/relative)['sha256']
        assert earlier[relative]==sha,(phase,name)
        rows.append({'phase':phase,'path':relative,'sha256':sha,'unchanged':True})
history=json.loads((E/'history-verification.json').read_text())
save('reuse-verification.json',{'unchanged_runtime_functions':rows,
    'B38':'Use only the formal/project Git port slice retained at 012. Same runtime source bytes, new actual read-only Git and dedicated Lake observation plus current project scene tests. 012 missing raw reports/counts remain missing.',
    '012':'Retain Mathlib full evidence/representative compile and installed lower-boundary properties with their original scope. This narrow task adds current P08 inspection/positive null samples and does not approve shared trust.',
    '016':'Retain the actual compiler/storage/currentness slice and correction to installed fixture content population; no installed-request producer change here.',
    '018':'Retain Job cleanup/stop contracts on unchanged fixture/runtime; this is not a new complete T4 claim.',
    '024':'Retain P09/P11 exact condition/wait/retry properties and helper bytes. Other policy/N/L01 meaning and all final gates remain outside this task.'})
print('Matched',len(rows),'unchanged runtime coordinates to 012/016/018/024')
