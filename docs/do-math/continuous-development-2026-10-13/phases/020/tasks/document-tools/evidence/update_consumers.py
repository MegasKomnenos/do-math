from work import *
import ast
phase=json.loads((RUN/'phases/020/phase.json').read_text(encoding='utf-8-sig'))
owners="('execution_window', 'scholarly', 'formal_verifier', 'preview', 'record_map.read_tool', 'submission_contract')"
for rel in phase['tasks'][0]['writes']:
    if not rel.startswith('.claude/') or not rel.endswith('.py') or rel.endswith(('doc_code.py','engine_context.py')):
        continue
    path=REPO/rel
    text=path.read_text(encoding='utf-8')
    tree=ast.parse(text); edits=[]
    lines=text.splitlines(keepends=True)
    offsets=[0]
    for line in lines:offsets.append(offsets[-1]+len(line))
    for node in ast.walk(tree):
        if not isinstance(node,ast.Call) or not isinstance(node.func,ast.Name) or node.func.id!='scoped_field_issues':continue
        kws={k.arg for k in node.keywords}
        if 'defer_tool_inputs' in kws:continue
        # Existing full-document sweeps already declare the P02 delegation.
        if 'defer_result_inputs' in kws:
            pos=offsets[node.end_lineno-1]+node.end_col_offset-1
            edits.append((pos,', defer_tool_inputs='+owners))
    for pos,value in sorted(edits,reverse=True):text=text[:pos]+value+text[pos:]
    if edits:
        path.write_text(text,encoding='utf-8',newline='')
        print(rel,len(edits))
