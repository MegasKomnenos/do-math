from work import *
import ast

def edit(relative, transform):
    p = REPO / relative
    text = p.read_bytes().decode('utf-8')
    updated = transform(text)
    p.write_bytes(updated.encode('utf-8'))

base = '.claude/skills/do-math/scripts/tests/'
# The last product consumers of these AST helpers were P08. Tests of the
# removed inference machinery are removed; unrelated assertions are retained.
edit(base+'support/doc_code.py', lambda t: t[:t.index('def producer_nodes(')] +
     t[t.index('def field_schemas():'):])
edit(base+'support/doc_code.py', lambda t: t.replace('import inspect\n','').replace('import textwrap\n',''))
p=REPO/base/'structure/test_doc_code.py'
t=p.read_text(encoding='utf-8')
tree=ast.parse(t)
methods={n.name:n for c in tree.body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef)}
remove=methods['test_producer_fields_do_not_come_from_nested_scopes_or_unknown_spreads']
lines=t.splitlines(keepends=True)
del lines[remove.lineno-1:remove.end_lineno]
t=''.join(lines)
start=t.index('        def result(extra):',t.index('    def test_explicit_producer_composition'))
end=t.index('        schemas = field_schemas()',start)
t=t[:start]+t[end:]
t=t.replace('test_explicit_producer_composition_keeps_owners_and_rejects_stale_bindings',
            'test_operating_summary_and_operational_input_keep_their_owners')
start=t.index('        def producer(command):',t.index('    def test_cli_result_branches'))
end=t.index('        schemas = field_schemas()',start)
t=t[:start]+t[end:]
start=t.index('        def consumer(payload, other, field):',t.index('    def test_optional_reads'))
end=t.index('        schemas = field_schemas()',start)
t=t[:start]+t[end:]
for name in ('consumed_object_schema, ', 'produced_object_schema, ', ', written_object_schema'):
    t=t.replace(name,'')
p.write_bytes(t.encode('utf-8'))

phase=json.loads((RUN/'phases/025/phase.json').read_text(encoding='utf-8-sig'))
walks=[]
for relative in phase['tasks'][0]['writes']:
    if relative.startswith('.claude/') and relative.endswith('.py'):
        p=REPO/relative
        t=p.read_bytes().decode('utf-8')
        old="defer_waits=('change', 'plan_settle_wait')"
        if old in t:
            walks.append({'path':relative,'calls':t.count(old)})
            p.write_bytes(t.replace(old,old+", defer_trust=('project', 'toolchain', 'environment_check')").encode('utf-8'))
save('walk-updates.json',walks)
print('Updated',len(walks),'document-walk consumers; removed unused AST inference helpers')
