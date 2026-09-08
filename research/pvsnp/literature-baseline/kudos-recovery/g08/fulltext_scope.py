"""Narrow fulltext dispositions from actual closed source inventories."""
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit
import recover as r
import content_review
sys.path.insert(0,str(r.ROOT.parent))
import work_queue

def classify(payload):
    text=payload.get('text','')
    host=urlsplit(payload.get('url','')).netloc.lower()
    if 'Download audio CAPTCHA' in text and 'Submit' in text:
        return ('unavailable','Publisher human-verification CAPTCHA blocks content inspection.')
    if 'Cloudflare' in text and ('보안 확인 수행 중' in text or 'Verify you are human' in text):
        return ('unavailable','Observed Cloudflare human-verification page blocks content inspection.')
    if host.endswith('search.serialssolutions.com') and '이용가능한 전자자료가 없습니다' in text:
        return ('not_found','Institutional resolver explicitly reports no electronic resource for its displayed citation.')
    if host.startswith('books.google.') and '사용 가능한 eBook 없음' in text:
        return ('not_found','Observed Google Books catalogue reports no eBook; catalogue descriptions/snippets are not complete originals.')
    return None

def assess(record,paper=None):
    if record['fulltext']['status']=='found':return None
    identity=record.get('work_state',{}).get('reviews',{}).get('identity',{})
    if record['identity']['status']!='confirmed' or identity.get('basis_sha256')!=work_queue.component_basis(record,'identity'):return None
    tasks=record.get('work_state',{}).get('tasks',[])
    if any(t['status'] in work_queue.OPEN for t in tasks if t['kind']!='review'):return None
    searches=[t for t in tasks if t['kind']=='search']
    if not searches or any(t['status']=='done' and t.get('engine')!='public_web' and t.get('remaining')!=0 for t in searches):return None
    if paper and not paper.get('source_urls') and record.get('mathscinet_article_link_enabled') is False and all(t.get('discovered')==0 for t in searches if t.get('engine')!='public_web'):
        public=[t for t in searches if t.get('engine')=='public_web']
        if {t.get('public_search_kind') for t in public}!={'title_author','publication'}:return None
    evidence={a['path']:a for a in record['evidence']}
    dispositions=[]
    paths=list(identity.get('evidence_paths',[]))
    for t in tasks:
        if t['kind'] not in {'search','source','pdf','repair'}:continue
        if not t.get('evidence_paths') or any(p not in evidence and p not in {a['path'] for c in ('abstract','fulltext') for a in record[c].get('artifacts',[])} for p in t['evidence_paths']):return None
        paths.extend(t['evidence_paths'])
        if t['kind']!='source' or t['target']=='MathSciNet detail' or t['status']=='not_needed':continue
        captures=[evidence[p] for p in t['evidence_paths'] if p in evidence and evidence[p].get('kind')=='source-link-inventory']
        if not captures:return None
        disposition=classify(json.loads(content_review.text(captures[-1])))
        if not disposition:return None
        dispositions.append(disposition)
    if not dispositions:return None
    status='unavailable' if any(d[0]=='unavailable' for d in dispositions) else 'not_found'
    return {'status':status,'reason':'Completed required search/source scope. '+' '.join(dict.fromkeys(d[1] for d in dispositions))+' This conclusion is limited to the inspected sources.','evidence_paths':list(dict.fromkeys(paths)),'rule_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'test':'kudos-recovery/g08/test_fulltext_scope.py'}
