"""Run production IOP HTML/image extraction in an owned headed Chromium session."""
import asyncio,json,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[1];ROOT=SERVICE.parents[1];sys.path.insert(0,str(SERVICE))
from browser_adapters import KudosGateway,clean_html,is_access_challenge
from publisher_html import fetch_html
from publishers import PROFILES,Publisher,publication_metadata,publication_dois
from scholarly import ArtifactStore,Sanitizer

PRIVATE=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260913/iop-equation-headed'
CREDENTIALS=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260913/iop-equation-live/credentials'
TARGET='https://iopscience.iop.org/article/10.1088/1367-2630/add557';DOI='10.1088/1367-2630/add557'
def now():return datetime.now(timezone.utc).isoformat()
def loc(url):
    p=urlsplit(url);return {'host':p.hostname,'path':p.path,'query_present':bool(p.query)}
def public_event(value):
    host,path=value.get('host'),value.get('path')
    allowed=(host=='kudos.knu.ac.kr' and path in ('/pages/index.htm','/pages/sub.htm','/include/proxyGo.php')) \
        or (host=='libproxy.knu.ac.kr' and path=='/lp1129_login~req.do') \
        or (host in ('iopscience.iop.org','iopscience-iop-org.libproxy.knu.ac.kr') and path in ('/', '/article/'+DOI, '/article/'+DOI+'/meta', '/article/'+DOI+'/pdf'))
    return {'at':value.get('at'),'status':value.get('status'),'host':host if allowed else 'other','path':path if allowed else '[redacted]'}
async def image_content(ref,data_dir):
    server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(data_dir)])
    async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
        await session.initialize();response=await session.call_tool('extract',{'ref':ref})
        return response.structuredContent,sum(block.type=='image' for block in response.content)
def main():
    stamp=f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}';run_dir=PRIVATE/stamp;run_dir.mkdir(parents=True,exist_ok=True);data_dir=run_dir/'data'
    def shot(page,name):
        png=run_dir/(name+'.png');html=run_dir/(name+'.html');page.screenshot(path=str(png),full_page=False);html.write_text(page.content(),encoding='utf-8');return {'screenshot':str(png),'private_html':str(html)}
    report={'source':'iop','started_at':now(),'browser_mode':'owned headed Playwright Chromium with copied production Chromium state','completed':False};timeline=[]
    gateway=KudosGateway(CREDENTIALS,Sanitizer(),engine='chromium');page=None
    try:
        from playwright.sync_api import sync_playwright
        gateway.playwright=sync_playwright().start();gateway.browser=gateway.playwright.chromium.launch(headless=False,channel='chrome')
        gateway.context=gateway.browser.new_context(storage_state=str(gateway.state_path()),accept_downloads=True);gateway.context.set_default_timeout(25000)
        def seen(response):
            try:
                if response.request.is_navigation_request():timeline.append({'at':now(),'status':response.status,**loc(response.url)})
            except Exception:pass
        gateway.context.on('response',seen)
        store=ArtifactStore(data_dir,gateway.sanitizer);profile=next(p for p in PROFILES if p.source=='iop');adapter=Publisher(store,gateway,profile)
        page=adapter.document(TARGET);page.wait_for_timeout(5000)
        raw=page.content();metadata=publication_metadata(raw)
        if publication_dois(metadata)!=[DOI] or is_access_challenge(raw):raise RuntimeError('article identity not ready')
        report['article_before']={**loc(page.url),'title':page.title(),**shot(page,'01-article-before-equations')}
        source=store.put(clean_html(raw,gateway.sanitizer),'text/html','iop',page.url,role='source_page',doi=DOI)
        component=fetch_html(adapter,page,DOI,source)
        report['article_after']={**loc(page.url),'title':page.title(),**shot(page,'02-article-after-equations')}
        math=component['math_images'];first=math.get('artifact')
        report.update(component_status=component['status'],html_bytes=component['artifact']['bytes'],figures=len(component['figures']),
            equation_requested=math['requested'],equation_received=math['received'],equation_status=math['status'],
            first_equation_media=first.get('media_type') if first else None,first_equation_bytes=first.get('bytes') if first else None)
        if first:
            extracted,blocks=asyncio.run(image_content(first['ref'],data_dir));report.update(first_extract_status=extracted.get('status'),first_image_blocks=blocks)
        report['completed']=component['status']=='available' and math['requested']==math['received']==154 and report.get('first_image_blocks')==1
    except Exception as error:
        report['error_type']=type(error).__name__
        if page is not None and not page.is_closed():
            try:report['error_capture']={**loc(page.url),**shot(page,'99-error')}
            except Exception as capture:report['capture_error_type']=type(capture).__name__
    finally:
        report['timeline']=timeline
        if page is not None and not page.is_closed():page.close()
        gateway.close();report['finished_at']=now()
        (run_dir/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        public={key:report.get(key) for key in ('source','started_at','browser_mode','completed','component_status','html_bytes','figures',
            'equation_requested','equation_received','equation_status','first_equation_media','first_equation_bytes','first_extract_status',
            'first_image_blocks','error_type','capture_error_type','finished_at') if key in report}
        public['timeline']=[public_event(value) for value in timeline]
        for key in ('article_before','article_after','error_capture'):
            if key in report:
                value=public_event(report[key]);value['screenshot']=report[key].get('screenshot');public[key]=value
        path=SERVICE/'data/validation'/(stamp+'-iop-equation-headed-mcp.json');path.write_text(json.dumps(public,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:report.get(k) for k in ('completed','component_status','figures','equation_requested','equation_received','equation_status','first_equation_media','first_equation_bytes','first_extract_status','first_image_blocks','error_type')},ensure_ascii=False))
    print(json.dumps({'screenshots':[report.get(k,{}).get('screenshot') for k in ('article_before','article_after','error_capture')],'timeline_count':len(timeline)},ensure_ascii=False))
if __name__=='__main__':main()
