"""Final source-owned semantic checks for the last SIAM and Numdam advanced row."""
import json,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT.parents[1]
sys.path.insert(0,str(ROOT))
from browser_adapters import KudosGateway,is_access_challenge
from native_browser import NativeChromeGateway
from numdam import Numdam
from publishers import PROFILES
from siam import SIAM
from scholarly import ArtifactStore,Sanitizer,ServiceError

STAMP=f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}';PRIVATE=WORK/'.credentials/scholarly-mcp/probes/access-research-20260913/semantic-cap-final'/STAMP
CREDENTIALS=WORK/'.credentials/scholarly-mcp/probes/access-research-20260913/semantic-cap-live/credentials';PUBLIC=ROOT/'data/access-research/semantic-cap-final.json'
def now():return datetime.now(timezone.utc).isoformat()
def shot(page,name):
    png=PRIVATE/(name+'.png');html=PRIVATE/(name+'.html');page.screenshot(path=str(png),full_page=False);html.write_text(page.content(),encoding='utf-8');return {'screenshot':str(png),'private_html':str(html)}
def result(value):return {k:value.get(k) for k in ('status','code','total','received')}
def cases(adapter,source):
    positive_terms=[{'field':'Author','query':'Stetter'} for _ in range(51)] if source=='siam' else [{'field':'all','query':'algebra'} for _ in range(10)]
    field='Title' if source=='siam' else 'all';positive=adapter.search('algebra',options={'field':field,'terms':positive_terms},limit=1)
    negative_terms=([{'field':'Author','query':'Stetter'} for _ in range(50)]+[{'field':'Author','query':'zzqv_no_such_author_52'}]) if source=='siam' else ([{'field':'all','query':'algebra'} for _ in range(9)]+[{'field':'all','query':'zzqv_no_such_term_11'}])
    negative=adapter.search('algebra',options={'field':field,'terms':negative_terms},limit=1)
    return positive,negative
def main():
    PRIVATE.mkdir(parents=True,exist_ok=True);report={'started_at':now(),'credential_root':'explicit_private','data_root':'explicit_private','sources':{},'completed':False}
    for source in ('siam','numdam'):
        gateway=NativeChromeGateway(CREDENTIALS,Sanitizer()) if source=='siam' else KudosGateway(CREDENTIALS,Sanitizer());page=None;entry={};report['sources'][source]=entry
        try:
            store=ArtifactStore(PRIVATE/(source+'-data'),gateway.sanitizer);adapter=SIAM(store,gateway,next(p for p in PROFILES if p.source=='siam')) if source=='siam' else Numdam(store,gateway)
            gateway.start();page=gateway.public_page(source);page.goto('https://epubs.siam.org/search/advanced' if source=='siam' else 'https://www.numdam.org/',wait_until='domcontentloaded',timeout=45000);page.wait_for_timeout(5000)
            entry['before']=shot(page,source+'-01-before')
            try:positive,negative=cases(adapter,source)
            except ServiceError as error:
                if source!='siam' or error.result.get('code')!='provider_error' or not is_access_challenge(page.content()):raise
                entry['challenge']=shot(page,'siam-02-challenge');deadline=time.monotonic()+75
                while time.monotonic()<deadline and is_access_challenge(page.content()):page.wait_for_timeout(5000)
                entry['challenge_cleared']=not is_access_challenge(page.content());entry['after_settle']=shot(page,'siam-03-after-settle')
                if not entry['challenge_cleared']:raise ServiceError('publisher_access_challenge','SIAM verification did not settle',status='restricted')
                entry['retry']='one_after_observed_challenge_settled';positive,negative=cases(adapter,source)
            entry['positive']=result(positive);entry['negative']=result(negative)
            entry['positive_requested_terms']=52 if source=='siam' else 11;entry['negative_requested_terms']=entry['positive_requested_terms']
            entry['positive_preserved_terms']=len(positive.get('options',{}).get('terms',[]))+1
            entry['negative_preserved_terms']=len(negative.get('options',{}).get('terms',[]))+1
            entry['native_last_positive']='field52=Contrib,text52=Stetter' if source=='siam' else 'q10=all:algebra'
            entry['native_last_negative']='field52=Contrib,text52=zzqv_no_such_author_52' if source=='siam' else 'q10=all:zzqv_no_such_term_11'
            entry['after']=shot(page,source+'-04-after-negative')
        except Exception as error:
            entry['error_type']=type(error).__name__;entry['error_code']=error.result.get('code') if isinstance(error,ServiceError) else None
            if page is not None and not page.is_closed():
                try:entry['failure']=shot(page,source+'-99-failure')
                except Exception as capture:entry['capture_error_type']=type(capture).__name__
        finally:
            try:gateway.close()
            except Exception as error:entry['close_error_type']=type(error).__name__
    s=report['sources'];report['completed']=(s['siam'].get('positive',{}).get('total') or 0)>0 and s['siam'].get('negative',{}).get('total')==0 \
        and (s['numdam'].get('positive',{}).get('total') or 0)>0 and s['numdam'].get('negative',{}).get('total')==0 \
        and all(e.get('positive_preserved_terms')==e.get('negative_preserved_terms')==(52 if name=='siam' else 11) for name,e in s.items())
    report['finished_at']=now();(PRIVATE/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    public={'started_at':report['started_at'],'completed':report['completed'],'sources':{},'finished_at':report['finished_at']}
    for name,entry in s.items():
        safe={key:entry[key] for key in ('positive','negative','challenge_cleared','retry','error_type','error_code','capture_error_type','close_error_type','positive_requested_terms','negative_requested_terms','positive_preserved_terms','negative_preserved_terms','native_last_positive','native_last_negative') if key in entry}
        for key in ('before','after','failure'):
            if key in entry:safe[key]={'screenshot':entry[key].get('screenshot')}
        public['sources'][name]=safe
    PUBLIC.write_text(json.dumps(public,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'completed':report['completed'],'sources':{name:{k:entry.get(k) for k in ('positive','negative','challenge_cleared','retry','error_type','error_code')} for name,entry in s.items()}},ensure_ascii=False));return report['completed']
if __name__=='__main__':sys.exit(0 if main() else 1)
