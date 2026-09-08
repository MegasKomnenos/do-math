"""Narrow negative-scope rule: no supplied links, no MR Article, zero complete UI queries."""
import hashlib
import json
from pathlib import Path
import recover as r
import content_review as content
from work_queue import component_basis

def assess_absence(record,paper):
    if record['identity']['status']!='confirmed' or 'identity' not in content.assess(record,paper):
        return {}
    if paper.get('source_urls') or record.get('mathscinet_article_link_enabled') is not False or record.get('mr_link_scope_version')!='per-record/1':
        return {}
    if any(record.get(flag) for flag in ('unvisited_link','unvisited_search_pages','collection_error','needs_mathscinet_revisit')):
        return {}
    tasks=record.get('work_state',{}).get('tasks',[])
    public=[t for t in tasks if t['kind']=='search' and t.get('engine')=='public_web']
    if {t.get('public_search_kind') for t in public}!={'title_author','publication'} or any(t['status']!='done' or not t.get('evidence_paths') for t in public):
        return {}
    searches=[t for t in tasks if t['kind']=='search' and t.get('engine')!='public_web']
    if not searches or any(t['status']!='done' or t.get('remaining')!=0 for t in searches):
        return {}
    if any(t['status'] not in {'done','not_needed'} for t in tasks if t['kind'] in {'source','pdf','repair'}):
        return {}
    evidence={a['path']:a for a in record['evidence']}
    paths=[p for t in public for p in t['evidence_paths']]
    if any(p not in evidence for p in paths):return {}
    for t in searches:
        captured=[evidence[p] for p in t.get('evidence_paths',[]) if p in evidence and evidence[p].get('kind')=='ui-search-response']
        if not captured:return {}
        payload=json.loads(content.text(captured[-1]))
        if payload.get('original_query')!=t['target'] or payload.get('holdings_only') is not False or payload.get('record_count')!=0 or payload.get('documents')!=[]:
            return {}
        paths.append(captured[-1]['path'])
    details=[a for a in record['evidence'] if 'mathscinet-detail' in a['path']]
    if not details:return {}
    body=content.text(details[-1])
    if 'Summary:' in body or 'Summary (' in body or 'Abstract' in body:
        return {}
    paths.append(details[-1]['path'])
    reviews={}
    for component in ('abstract','fulltext'):
        if record[component]['status']=='not_found':
            reviews[component]={'basis_sha256':component_basis(record,component),'scope_complete':True,'reason':'Current scoped MR identity is verified; per-record Article control has no link; input supplies no source URL; every required saved ho=f UI query is verified zero-results with no omitted pages; retained MR detail has no explicit Summary/Abstract boundary. Absence is confined to this contract scope.','evidence_paths':paths,'rule_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'test':'kudos-recovery/g08/test_scope_review.py'}
    return reviews
