"""Re-evaluate retained evidence with the tested identity and access rules."""
from pathlib import Path
import json
import re
import recover

def reconcile(record,paper,base):
    fixed=json.loads(json.dumps(record))
    def scrub(value):
        if isinstance(value,dict):
            return {k:(recover.public_url(v) if k=='url' and isinstance(v,str) else scrub(v)) for k,v in value.items()}
        if isinstance(value,list):
            return [scrub(v) for v in value]
        return value
    fixed=scrub(fixed)
    if fixed['abstract']['status']=='found':
        for asset in fixed['abstract'].get('artifacts',[]):
            if asset.get('media_type','text/plain')!='text/plain':continue
            issue=recover.abstract_quality_issue((base/asset['path']).read_text(encoding='utf-8'))
            if issue:
                fixed.setdefault('withdrawn_abstracts',[]).append({'reason':issue,'component':fixed['abstract']})
                fixed['evidence'].extend(a for a in fixed['abstract']['artifacts'] if a['path'] not in {e['path'] for e in fixed['evidence']})
                fixed['abstract']={'status':'unresolved','reason':'Retained text fails content review: '+issue+'. Recover a complete abstract from another actual source or PDF region.'}
                fixed.get('work_state',{}).get('reviews',{}).pop('abstract',None)
                break
    if fixed.get('unvisited_link') or fixed.get('collection_error') or fixed.get('unvisited_search_pages'):
        for component in ('abstract','fulltext'):
            if fixed[component]['status']=='not_found':
                fixed.setdefault('superseded_conclusions',[]).append({'component':component,'conclusion':fixed[component]})
                fixed[component]={'status':'unresolved','reason':'Retained incomplete source/search or collection failure must be resolved before absence can be concluded.'}
        fixed['required_sources_complete']=False
    if fixed['identity']['status']=='unresolved':
        captures=[a for a in fixed['evidence'] if 'mathscinet-detail' in a['path']]
        if captures:
            text=(base/captures[-1]['path']).read_text(encoding='utf-8')
            heading=text.splitlines()[0]
            bibliography=fixed['identity'].get('observed_bibliography','')
            if recover.bind_mr(paper,heading,bibliography):
                fixed['identity']={'status':'confirmed','reason':'Retained MR heading and bibliographic title/all named authors/year pass the revised tested script/TeX normalization. Source retrieval will be repeated with the corrected binding.','observed_bibliography':bibliography}
                fixed['required_sources_complete']=False
                fixed['identity_repaired_needs_source_recheck']=True
    if fixed['fulltext']['status']=='not_found':
        urls={b['url'] for b in fixed.get('publisher_bindings',[]) if b.get('target_match')}
        for capture in fixed['evidence']:
            if 'publisher' in capture['path'] and capture['url'] in urls:
                text=(base/capture['path']).read_text(encoding='utf-8')
                if recover.publisher_restriction(text):
                    fixed['fulltext']={'status':'unavailable','reason':'The identity-confirmed publisher page explicitly restricts this content to subscription/institutional access or preview; no complete original was acquired.','evidence_path':capture['path']}
                    break
    if fixed['identity']['status']=='confirmed':
        for source in ([] if fixed.get('review',{}).get('grouped') else fixed.get('review',{}).get('artifacts',[])):
            text=(base/source['path']).read_text(encoding='utf-8')
            summary=recover.abstract_from_review(text)
            if summary:
                label=next((line for line in text.splitlines() if line.startswith('Summary') and ':' in line),'Summary')
                label=label.split(':',1)[0]
                asset=recover.artifact(fixed['paper_id'],'mathscinet-summary.txt',summary,source['url'],'explicit-source-summary','text/plain')
                recovered={'status':'found','source_kind':label,'artifacts':[asset],'source_evidence':source['path']}
                fixed['mathscinet_summary']=recovered
                component='description' if paper.get('record_type') in {'book','proceedings'} else 'abstract'
                if fixed.get(component,{}).get('status')!='found':
                    fixed[component]=recovered
                break
    return fixed

if __name__=='__main__':
    papers={p['paper_id']:p for p in (json.loads(x) for x in (recover.BASE/recover.ASSIGNMENT['members_path']).read_text(encoding='utf-8').splitlines())}
    changed=[]
    for path in sorted((recover.ROOT/'results').glob('*.json')):
        record=json.loads(path.read_text(encoding='utf-8'))
        fixed=reconcile(record,papers[record['paper_id']],recover.BASE)
        if fixed!=record:
            recover.save_json(path,fixed)
            changed.append(record['paper_id'])
    recover.save_json(recover.ROOT/'reconciliation.json',{'changed':changed,'count':len(changed)})
    print(json.dumps({'changed':len(changed),'paper_ids':changed},ensure_ascii=False))
