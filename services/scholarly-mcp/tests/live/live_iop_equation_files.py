"""Verify actual IOP equation GIF controls preserved by an earlier DOI-bound HTML fetch."""
import asyncio,json,sys
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[2];ROOT=SERVICE.parents[1]
sys.path.insert(0,str(SERVICE))
from browser_adapters import KudosGateway,browser_download
from scholarly import ArtifactStore,Sanitizer

PRIVATE=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260913/iop-equation-files'
CREDENTIALS=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260913/iop-equation-live/credentials'
SOURCE_REPORT=SERVICE/'data/validation/20260912T033324Z-iop-content-mcp.json'
HOST='content-cld-iop-org.libproxy.knu.ac.kr';DOI='10.1088/1367-2630/add557'
def loc(url):
    parts=urlsplit(url);return {'host':parts.hostname,'path':parts.path,'query_present':bool(parts.query)}

def source_html():
    report=json.loads(SOURCE_REPORT.read_text(encoding='utf-8'));artifact=None
    def walk(value):
        nonlocal artifact
        if isinstance(value,dict):
            if value.get('role')=='fulltext_html':artifact=value
            for item in value.values():walk(item)
        elif isinstance(value,list):
            for item in value:walk(item)
    walk(report)
    return (SERVICE/'data/blobs'/artifact['sha256']).read_bytes(),artifact['url']

async def image_content(ref,data_dir):
    server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(data_dir)])
    async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
        await session.initialize();response=await session.call_tool('extract',{'ref':ref})
        return response.structuredContent,sum(block.type=='image' for block in response.content)

def main():
    stamp=f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}';PRIVATE.mkdir(parents=True,exist_ok=True);data_dir=PRIVATE/stamp
    report={'source':'iop','started_at':datetime.now(timezone.utc).isoformat(),'completed':False,'basis':'previously preserved DOI-bound native HTML controls'}
    gateway=KudosGateway(CREDENTIALS,Sanitizer(),engine='firefox');files=[]
    try:
        report['stage']='parse_controls'
        html,article_url=source_html();soup=BeautifulSoup(html,'html.parser');occurrences=soup.select('span.texImage > img[src]')
        images=list({img['src']:img for img in occurrences}.values())
        parents={str(PurePosixPath(unquote(urlsplit(img['src']).path)).parent) for img in images}
        report['occurrences']=len(occurrences)
        if len(images)!=154 or len(parents)!=1:raise RuntimeError('unexpected equation control set')
        report['stage']='start_private_browser'
        store=ArtifactStore(data_dir,gateway.sanitizer);gateway.start()
        for number,img in enumerate(images,1):
            report['stage']='download_equation';report['current_number']=number
            url=img['src'];parts=urlsplit(url);path=unquote(parts.path);name=PurePosixPath(path).name
            if parts.hostname!=HOST or str(PurePosixPath(path).parent) not in parents or not name:
                raise RuntimeError('equation identity mismatch')
            data,media,actual=browser_download(gateway.context,url,{HOST},headers={'Referer':article_url})
            if unquote(urlsplit(actual).path)!=path or not data.startswith((b'GIF87a',b'GIF89a')):
                report['file_mismatch']={'requested':loc(url),'actual':loc(actual),'media':media,'bytes':len(data),'magic':data[:8].hex()}
                raise RuntimeError('equation file mismatch')
            artifact=store.put(data,'image/gif','iop',actual,preserve_bytes=True,role='equation_image',doi=DOI,equation_number=number,source_control_path=path)
            files.append(artifact)
        report['stage']='sdk_extract'
        extracted,blocks=asyncio.run(image_content(files[0]['ref'],data_dir))
        report.update(files=len(files),unique_sha256=len({f['sha256'] for f in files}),bytes=sum(f['bytes'] for f in files),
            first_extract_status=extracted.get('status'),first_extract_media=extracted.get('media_type'),first_image_blocks=blocks,
            all_gif=all(f['media_type']=='image/gif' for f in files))
        report['completed']=len(files)==154 and report['all_gif'] and blocks==1 and extracted.get('media_type')=='image/gif'
    except Exception as error:report['error_type']=type(error).__name__
    finally:
        gateway.close();report['finished_at']=datetime.now(timezone.utc).isoformat()
        path=SERVICE/'data/validation'/(stamp+'-iop-equation-files-mcp.json');path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
    return report['completed']
if __name__=='__main__':sys.exit(0 if main() else 1)
