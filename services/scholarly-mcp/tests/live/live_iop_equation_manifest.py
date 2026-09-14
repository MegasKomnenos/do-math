"""Re-run IOP serialization with already verified native files, then SDK-read its compact manifest."""
import asyncio,json,sys,tempfile
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from bs4 import BeautifulSoup
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[2];ROOT=SERVICE.parents[1];sys.path.insert(0,str(SERVICE))
from publisher_html import fetch_html
from scholarly import ArtifactStore

OLD_DATA=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260913/iop-equation-live/data'
SOURCE_REPORT=SERVICE/'data/validation/20260912T201746Z-iop-content-mcp.json';DOI='10.1088/1367-2630/add557'

async def extract(ref,data_dir,**args):
    server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(data_dir)])
    async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
        await session.initialize();return await session.call_tool('extract',{'ref':ref,**args})

def main():
    stamp=f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}';new_data=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260913/iop-equation-manifest'/stamp
    report={'source':'iop','started_at':datetime.now(timezone.utc).isoformat(),'basis':'previously verified actual files; no remote download','completed':False}
    try:
        old=ArtifactStore(OLD_DATA);result=json.loads(SOURCE_REPORT.read_text(encoding='utf-8'))['calls'][0]['result'];component=result['components']['fulltext_html']
        _,body=old.read(component['artifact']['ref']);soup=BeautifulSoup(body,'html.parser');downloads={}
        for img,item in zip(soup.select('figure img.panzoom'),component['figures']):
            img['src']=item['url'];downloads[item['url']]=old.read(item['artifact']['ref'])[1]
        for item in component['math_images']['files']:
            ref=item['artifact']['ref'];url=item['url'];downloads[url]=old.read(ref)[1]
            for img in soup.select('span.texImage > img[src="'+ref+'"]'):img['src']=url
        raw=str(soup);store=ArtifactStore(new_data);source=store.put(raw,'text/html','iop',component['artifact']['url'],role='source_page',doi=DOI)
        page=SimpleNamespace(url=component['artifact']['url'],content=lambda:raw)
        adapter=SimpleNamespace(store=store,source='iop',profile=SimpleNamespace(download_hosts={'content-cld-iop-org.libproxy.knu.ac.kr'}),gateway=SimpleNamespace(context=None))
        def downloaded(context,url,hosts,headers=None):
            data=downloads[url];media='image/gif' if data.startswith((b'GIF87a',b'GIF89a')) else 'image/png' if data.startswith(b'\x89PNG') else 'image/jpeg'
            return data,media,url
        with patch('publisher_html.browser_download',side_effect=downloaded):compact=fetch_html(adapter,page,DOI,source)
        math=compact['math_images'];manifest=math['manifest'];first=asyncio.run(extract(manifest['ref'],new_data,start=0,count=1)).structuredContent
        last=asyncio.run(extract(manifest['ref'],new_data,start=153,count=1)).structuredContent
        image=asyncio.run(extract(math['artifact']['ref'],new_data))
        html_meta=store.read(compact['artifact']['ref'])[0]
        report.update(component_json_bytes=len(json.dumps(compact,ensure_ascii=False).encode()),requested=math['requested'],received=math['received'],
            manifest_total=first['total'],first_number=first['items'][0]['number'],last_number=last['items'][0]['number'],
            first_status=first['items'][0]['status'],last_status=last['items'][0]['status'],first_image_blocks=sum(x.type=='image' for x in image.content),
            html_manifest_ref_matches=html_meta.get('equation_image_manifest_ref')==manifest['ref'],
            inline_files_key='files' in math,inline_artifacts_key='artifacts' in math,inline_equation_refs='equation_image_refs' in html_meta)
        report['completed']=compact['status']=='available' and report['requested']==report['received']==report['manifest_total']==154 \
            and (report['first_number'],report['last_number'])==(1,154) and report['first_image_blocks']==1 and report['html_manifest_ref_matches'] \
            and not report['inline_files_key'] and not report['inline_artifacts_key'] and not report['inline_equation_refs']
    except Exception as error:report['error_type']=type(error).__name__
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat();path=SERVICE/'data/validation'/(stamp+'-iop-equation-manifest-mcp.json');path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False));return report['completed']
if __name__=='__main__':sys.exit(0 if main() else 1)
