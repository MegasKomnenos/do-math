from work import *
import ast
allowed=json.loads((RUN/'phases/021/phase.json').read_text(encoding='utf-8-sig'))['tasks'][0]['writes']
owners="('role_review', 'pending_findings', 'review_research', 'review_sources')"
for rel in allowed:
    if not rel.startswith('.claude/') or not rel.endswith('.py') or rel.endswith(('/support/doc_code.py','/support/engine_context.py')):
        continue
    path=REPO/rel
    source=path.read_text(encoding='utf-8')
    lines=source.splitlines(keepends=True); offsets=[0]
    for line in lines: offsets.append(offsets[-1]+len(line))
    edits=[]
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node,ast.Call) or not isinstance(node.func,ast.Name) or node.func.id!='scoped_field_issues':continue
        keys={k.arg for k in node.keywords}
        if 'defer_tool_inputs' in keys and 'defer_review_inputs' not in keys:
            edits.append((offsets[node.end_lineno-1]+node.end_col_offset-1,', defer_review_inputs='+owners))
    for pos,value in sorted(edits,reverse=True):source=source[:pos]+value+source[pos:]
    if edits:path.write_text(source,encoding='utf-8',newline='');print(rel,len(edits))
path=REPO/'.claude/skills/do-math/scripts/tests/structure/test_doc_code.py'
text=path.read_text(encoding='utf-8')
text=text.replace("'`change.value` `review_research.question` '","'`change.value` '")
text=text.replace("'`toolchain.project.search_paths` `environment_check.changed_files` `role_review.proposal`'", "'`toolchain.project.search_paths` `environment_check.changed_files`'")
path.write_text(text,encoding='utf-8',newline='')
