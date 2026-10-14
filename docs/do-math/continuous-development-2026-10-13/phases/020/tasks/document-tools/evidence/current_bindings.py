from work import *
import re
sys.path.insert(0,str(REPO/'.claude/skills/do-math/scripts'))
sys.path.insert(0,str(REPO/'.claude/skills/do-math/scripts/tests'))
from support.doc_code import documents, SPAN
owners={'record_map','execution_window','scholarly','formal_verifier','preview','submission_contract'}
rows=[]
for path in documents(REPO/'.claude/skills/do-math'):
    title=''
    for i,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
        if line.startswith('#'):title=line
        tokens=[s for s in SPAN.findall(line) if s.split('.')[0].split('=')[0] in owners]
        if tokens:rows.append({'path':path.relative_to(REPO).as_posix(),'line':i,'heading':title,'tokens':tokens,'text':line})
save('current-bindings.json',{'owners':sorted(owners),'document_locations':rows,
 'production':['CoreEngineMixin._context','context_store.record_map','context_store.prepare_role_input','submission.install_tools'],
 'actual_check':'sim.test_role_input_context.PreparedInputTests.test_installed_tools_match_the_final_role_input_and_reject_damage',
 'preview_source':'same formal_verifier.preview child, not a separately produced result',
 'execution_window':'path guidance, not evidence that dynamic notification files occurred',
 'scholarly':'pinned configuration, not live exposure/call success'})
print('Current P03 locations',len(rows))
