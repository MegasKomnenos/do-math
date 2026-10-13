"""Check inventory coordinates, coverage and editions, without importing the product."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

REPO=Path('C:/math')
OUT=Path(__file__).resolve().parent


def read_json(name):
    return json.loads((OUT/name).read_text(encoding='utf-8'))


def main():
    inv=read_json('binding-inventory.json'); census=read_json('source-census.json')
    packets=read_json('followup-packets.json')['packets']
    hashes=read_json('reviewed-source-hashes.json')['source_hashes']
    owners=[r['owner'] for r in inv['bindings']]
    assert len(owners)==len(set(owners))==84
    def occurrence(r): return r['document'],r['line'],r['token']
    actual=Counter(occurrence(r) for r in census['field_occurrences'] if r['category']=='field')
    indexed=Counter(occurrence(d) for row in inv['bindings'] for d in row['documents'])
    assert actual==indexed, (actual-indexed,indexed-actual)
    assert len({r['path'] for r in inv['documents']})==24
    text=(REPO/'.claude/skills/do-math/scripts/tests/support/doc_code.py').read_text(encoding='utf-8-sig')
    tree=ast.parse(text)
    field=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='field_schemas')
    declared=set()
    for node in ast.walk(field):
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id=='schemas':
                    declared.update(ast.literal_eval(k) for k in node.value.keys)
                if isinstance(target,ast.Subscript):
                    chain=target
                    while isinstance(chain.value,ast.Subscript): chain=chain.value
                    if isinstance(chain.value,ast.Name) and chain.value.id=='schemas' and isinstance(chain.slice,ast.Constant):
                        declared.add(chain.slice.value)
        if isinstance(node,ast.For) and isinstance(node.iter,ast.Tuple):
            if any(isinstance(n,ast.Assign) and any(isinstance(t,ast.Subscript) and isinstance(t.value,ast.Name) and t.value.id=='schemas' for t in n.targets) for n in ast.walk(node)):
                values=ast.literal_eval(node.iter)
                declared.update(v[0] if isinstance(v,tuple) else v for v in values)
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in
            ('CLI_RESULT_BOUNDARIES','ROLE_INPUT_BOUNDARIES','CONTINUATION_BOUNDARIES') for t in node.targets):
            declared.update(ast.literal_eval(node.value.generators[0].iter))
    assert set(owners)==declared,(set(owners)-declared,declared-set(owners))
    sites={n.lineno for n in ast.walk(field) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in
           ('produced_object_schema','written_object_schema','consumed_object_schema')}
    listed={n for row in inv['bindings'] for n in row['ast_sites']}
    assert listed==sites and len(sites)==34
    packet_sites=Counter(n for p in packets for n in p.get('ast_sites',[]))
    assert set(packet_sites)==sites and set(packet_sites.values())=={1}
    closed={'status','operation_progress','query_record','query_result','init_result','scheduling_result',
            'selection_result','input_manifest','prompt','documents','result_source','rejected_response',
            'previous_output_files','profile_selection','operating_summary'}
    assigned={o for p in packets for o in p.get('owners',[])}
    assert not closed & assigned,closed & assigned
    partitions=Counter(path for p in packets for path in p.get('document_partition',[]))
    assert set(partitions)=={r['path'] for r in inv['documents']} and set(partitions.values())=={1}
    for p in packets:
        for path in p.get('document_partition',[]):
            sections=sorted((s for s in p['required_slices'] if s['document']==path), key=lambda x:x['start_line'])
            total=len((REPO/path.removeprefix('repo:')).read_text(encoding='utf-8-sig').splitlines())
            assert sections[0]['start_line']==1 and sections[-1]['end_line']==total
            assert all(a['end_line']+1==b['start_line'] for a,b in zip(sections,sections[1:]))
    checked_paths=set(); checked_symbols=set()
    def inspect(value):
        if isinstance(value,dict):
            path=value.get('path')
            if isinstance(path,str) and path.startswith('repo:'):
                filename=REPO/path.removeprefix('repo:'); assert filename.is_file(),path
                checked_paths.add(path)
                if 'symbol' in value:
                    current=filename.read_text(encoding='utf-8-sig').splitlines()
                    leaf=value['symbol'].split('.')[-1]
                    assert re.search(r'\b(def|class) '+re.escape(leaf)+r'\b',current[value['line']-1]),value
                    assert value['end_line']<=len(current)
                    checked_symbols.add((path,value['symbol']))
            if 'document' in value and 'line' in value and 'token' in value:
                filename=REPO/value['document'].removeprefix('repo:')
                line=filename.read_text(encoding='utf-8-sig').splitlines()[value['line']-1]
                assert value['token'] in line,value
            for v in value.values(): inspect(v)
        elif isinstance(value,list):
            for v in value:inspect(v)
    inspect(inv); inspect(packets)
    changed=[p for p,h in hashes.items() if hashlib.sha256((REPO/p).read_bytes()).hexdigest()!=h]
    assert not changed,changed
    baseline=json.loads((REPO/'docs/do-math/continuous-development-2026-10-13/sources/baseline.json').read_text(encoding='utf-8-sig'))
    changed_baseline=[x['path'] for x in baseline['source_files']+baseline['product_files']+baseline['engine_files']
                      if hashlib.sha256((REPO/x['path']).read_bytes()).hexdigest()!=x['sha256']]
    assert not changed_baseline,changed_baseline
    # Record the actual importer population; no import/pytest/unittest discovery.
    consumer_files=[]
    for path in (REPO/'.claude/skills/do-math/scripts/tests').rglob('*.py'):
        body=path.read_text(encoding='utf-8-sig')
        if 'field_schemas' in body: consumer_files.append(path.relative_to(REPO).as_posix())
    legacy=inv['legacy_17_lexical_candidates']
    assert len(legacy)==len({c['token'] for c in legacy})==17
    bootstrap=(REPO/'.claude/skills/do-math/scripts/operator_bootstrap.py').read_text(encoding='utf-8-sig')
    assert 'LIVE_INSTALLATION_ROOT' not in bootstrap
    assert 'installation_root=installation_root' in bootstrap
    summary={'result':'pass','declared_owners':len(owners),'documents':24,'field_occurrences':sum(actual.values()),
             'ast_sites':len(sites),'ast_site_packets_disjoint':True,'closed_owners_redispatched':[],
             'document_partitions_disjoint_complete':True,'referenced_paths_checked':len(checked_paths),
             'referenced_symbols_checked':len(checked_symbols),'reviewed_file_hashes_checked':len(hashes),
             'baseline_files_checked':len(baseline['source_files'])+len(baseline['product_files'])+len(baseline['engine_files']),
             'changed_sources':changed,'changed_baseline_files':changed_baseline,
             'legacy_candidates':17,'field_schemas_consumer_files':consumer_files,
             'limits':'Only inventory format/coordinates/population/edition checks. No product tests, helper imports or semantic conformance execution.'}
    (OUT/'inventory-validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__': main()
