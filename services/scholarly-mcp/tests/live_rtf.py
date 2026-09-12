"""Extract an observed ProQuest RTF export through a fresh local MCP server."""
import argparse,asyncio,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,Sanitizer
from browser_adapters import KudosGateway
from richtext import rtf_text


async def main(input_file,credential_root):
    private=input_file.parent/'rtf-sdk'
    sanitizer=Sanitizer()
    KudosGateway(credential_root,sanitizer)
    store=ArtifactStore(private/'artifacts',sanitizer)
    data=input_file.read_bytes()
    document_ids=set()
    for target in re.findall(rb'HYPERLINK\s+("[^\"]+"|[^\s}]+)',data,re.I):
        parsed=urlsplit(target.strip(b'"').decode('ascii'))
        if parsed.hostname in ('www.proquest.com','www-proquest-com.libproxy.knu.ac.kr'):
            match=re.search(r'/docview/(\d+)(?:/|$)',parsed.path)
            if match:document_ids.add(match[1])
    assert document_ids=={'2618193239'}
    text=rtf_text(data)
    assert sanitizer.text(text)==text and all(value.encode() not in data for value in sanitizer.secrets)
    artifact=store.put(data,'application/rtf','pqdt','https://www.proquest.com/docview/2618193239',preserve_bytes=True,
                       role='observed_citation_export_for_extraction_validation')
    report={'scope':'RTF extraction of an observed source export; fetch is validated separately','completed':False,'calls':[],
            'identity':{'native_hyperlink_docview_ids':sorted(document_ids),'expected_title':'Resource Bounded Measure and P Versus NP Problem-A Critical Study'}}
    path=ROOT/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-rtf-mcp.json'
    def save():path.write_text(json.dumps(sanitizer.value(report),ensure_ascii=False,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    try:
        args=[str(ROOT/'server.py'),'--data-dir',str(private/'artifacts'),'--credential-root',str(credential_root)]
        async with stdio_client(StdioServerParameters(command=sys.executable,args=args)) as (read,write),ClientSession(read,write) as session:
            await session.initialize()
            async def call(arguments):
                result=(await session.call_tool('extract',arguments)).structuredContent
                report['calls'].append({'arguments':arguments,'result':result});save()
                print(json.dumps({'status':result['status'],'total':result.get('total'),'returned':result.get('returned')}),flush=True)
                return result
            first=await call({'ref':artifact['ref'],'count':3})
            assert first['status']=='ok' and first['unit']=='lines' and first['items']==text.splitlines()[:3]
            rest=await call({'ref':artifact['ref'],'start':3,'count':1000})
            assert first['items']+rest['items']==text.splitlines()
            assert 'Resource Bounded Measure and P Versus NP Problem-A Critical Study' in '\n'.join(first['items']+rest['items'])
            assert store.read(artifact['ref'])[1]==data
            report['completed']=True
    finally:
        save();print(json.dumps({'completed':report['completed']}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('input_file',type=Path);parser.add_argument('--credential-root',type=Path,required=True)
    options=parser.parse_args()
    try:asyncio.run(main(options.input_file.resolve(),options.credential_root.resolve()))
    except Exception as error:
        print(json.dumps({'verification_error':type(error).__name__}),flush=True)
        sys.exit(1)
