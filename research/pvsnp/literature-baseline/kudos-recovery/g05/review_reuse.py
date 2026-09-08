"""Reuse explicit prior visual PDF decisions bound to the same accepted artifact."""
import hashlib,json,sys
from urllib.parse import unquote,urlsplit
from collect import BASE,WORK,artifact,save_json
sys.path.insert(0,str(WORK.parent))
from work_queue import component_basis

def matching_review(record,entries):
    full=record.get('fulltext',{})
    if full.get('status')!='found':return None
    for entry in entries:
        reviewed=entry.get('artifact',{})
        if entry.get('paper_id')!=record['paper_id'] or entry.get('review_status')!='verified' or not entry.get('review_note'):continue
        observed=unquote(urlsplit(reviewed.get('url','')).path).casefold()
        dois=record.get('metadata',{}).get('identifiers',{}).get('doi',[])
        if not dois or not any(observed.rstrip('/').endswith('/'+doi.casefold()) for doi in dois):continue
        if not any(a.get('sha256')==reviewed.get('sha256') and a.get('path')==reviewed.get('path') for a in full.get('artifacts',[])):continue
        source=BASE/reviewed['path'];image=BASE/entry.get('image','')
        if not source.is_file() or not image.is_file() or hashlib.sha256(source.read_bytes()).hexdigest()!=reviewed['sha256']:continue
        if full.get('validation')!=entry['review_note']:continue
        return entry
    return None

def main():
    entries=[]
    for name in ['pending-pdf-review.json','root-pdf-review.json','book-review-pending.json']:
        data=json.loads((WORK/name).read_text())
        if isinstance(data,list):entries.extend(data)
    active=set(json.loads((WORK/'html-work-list.json').read_text()))
    count=0
    for path in (WORK/'results').glob('*.json'):
        record=json.loads(path.read_text())
        if record['paper_id'] in active:continue
        entry=matching_review(record,entries)
        if entry is None:continue
        prior=record['work_state']['reviews'].get('fulltext',{})
        if prior.get('basis_sha256')==component_basis(record,'fulltext'):continue
        note=artifact(record['paper_id'],'reused-visual-pdf-review.json',json.dumps(entry,ensure_ascii=False,indent=2),'operator:g05-prior-visual-review','application/json','reused-direct-content-review')
        image=artifact(record['paper_id'],'reused-visual-pdf-page.png',(BASE/entry['image']).read_bytes(),'operator:g05-prior-visual-review','image/png','reused-direct-page-image')
        record['evidence'].extend([note,image]);paths=[entry['artifact']['path'],note['path'],image['path']]
        reason='Reuse the prior explicit visual review, unchanged accepted PDF hash and the inspected page image: '+entry['review_note']
        record['work_state']['reviews']['fulltext']={'method':'manual','basis_sha256':component_basis(record,'fulltext'),'reason':reason,'evidence_paths':paths,'prior_review_note':entry['review_note']}
        for task in record['work_state']['tasks']:
            if task['key']=='review:fulltext' or task.get('target')==entry['artifact']['path']:
                task.update(status='done',reason=reason,evidence_paths=paths)
        save_json(path,record);count+=1
    print(json.dumps({'reused_explicit_pdf_reviews':count}))
if __name__=='__main__':main()
