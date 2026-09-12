"""Verify that SIAM's 52nd advanced row changes the native result set."""
import json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT.parents[1];sys.path.insert(0,str(ROOT))
from native_browser import NativeChromeGateway
from publishers import PROFILES
from siam import SIAM
from scholarly import ArtifactStore,Sanitizer,ServiceError

STAMP=f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}';PRIVATE=WORK/'.credentials/scholarly-mcp/probes/access-research-20260913/siam-semantic-52'/STAMP
CREDENTIALS=WORK/'.credentials/scholarly-mcp/probes/access-research-20260913/semantic-cap-live/credentials';PUBLIC=ROOT/'data/access-research/siam-semantic-52.json'
def now():return datetime.now(timezone.utc).isoformat()
def shot(page,name):
    png=PRIVATE/(name+'.png');html=PRIVATE/(name+'.html');page.screenshot(path=str(png),full_page=False);html.write_text(page.content(),encoding='utf-8');return {'screenshot':str(png),'private_html':str(html)}
def brief(value):return {k:value.get(k) for k in ('status','code','total','received')}
def main():
    PRIVATE.mkdir(parents=True,exist_ok=True);report={'source':'siam','started_at':now(),'credential_root':'explicit_private','data_root':'explicit_private','completed':False}
    gateway=NativeChromeGateway(CREDENTIALS,Sanitizer());page=None
    try:
        store=ArtifactStore(PRIVATE/'data',gateway.sanitizer);adapter=SIAM(store,gateway,next(p for p in PROFILES if p.source=='siam'))
        gateway.start();page=gateway.public_page('siam');page.goto('https://epubs.siam.org/search/advanced',wait_until='domcontentloaded',timeout=45000);page.wait_for_timeout(5000)
        report['before']=shot(page,'01-before')
        terms=[{'field':'Author','query':'Stetter'} for _ in range(51)]
        positive=adapter.search('algebra',options={'field':'Title','terms':terms},limit=1);report['positive']=brief(positive)
        report['positive']['preserved_terms']=len(positive.get('options',{}).get('terms',[]))+1;report['positive']['native_last']='field52=Contrib,text52=Stetter'
        report['positive_after']=shot(page,'02-positive')
        if positive.get('status')=='ok':
            terms=[{'field':'Author','query':'Stetter'} for _ in range(50)]+[{'field':'Author','query':'zzqv_no_such_author_52'}]
            negative=adapter.search('algebra',options={'field':'Title','terms':terms},limit=1);report['negative']=brief(negative)
            report['negative']['preserved_terms']=len(negative.get('options',{}).get('terms',[]))+1;report['negative']['native_last']='field52=Contrib,text52=zzqv_no_such_author_52'
            report['negative_after']=shot(page,'03-negative')
        report['completed']=(report.get('positive',{}).get('total') or 0)>0 and report.get('negative',{}).get('total')==0 \
            and report['positive']['preserved_terms']==report['negative']['preserved_terms']==52
    except Exception as error:
        report['error_type']=type(error).__name__;report['error_code']=error.result.get('code') if isinstance(error,ServiceError) else None
        report['error_status']=error.result.get('status') if isinstance(error,ServiceError) else None
        if page is not None and not page.is_closed():
            try:report['failure']=shot(page,'99-failure')
            except Exception as capture:report['capture_error_type']=type(capture).__name__
    finally:
        try:gateway.close()
        except Exception as error:report['close_error_type']=type(error).__name__
        report['finished_at']=now();(PRIVATE/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        public={k:report[k] for k in ('source','started_at','completed','positive','negative','error_type','error_code','error_status','capture_error_type','close_error_type','finished_at') if k in report}
        for key in ('before','positive_after','negative_after','failure'):
            if key in report:public[key]={'screenshot':report[key].get('screenshot')}
        PUBLIC.write_text(json.dumps(public,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:public.get(k) for k in ('completed','positive','negative','error_type','error_code','error_status','failure')},ensure_ascii=False));return report['completed']
if __name__=='__main__':sys.exit(0 if main() else 1)
