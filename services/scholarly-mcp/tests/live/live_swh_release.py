"""Follow actual directory/revision release targets through stdio."""
import asyncio,json,sys,argparse
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[2]
async def main():
    parser=argparse.ArgumentParser();parser.add_argument('--kind',choices=('directory','revision','all'),default='all');args=parser.parse_args()
    report={'source':'software-heritage','target_kind':args.kind,'calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-swh-release-mcp.json'
    def save():path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        cases=[('directory','fc8e44c5bb3fabe81e5ebe46ac013a2510271616','7057a716afab8ca80728aa7c6c2cc4bd03b0f45b'),('revision','22ece559cc7cc2364edc5e5593d63ae8bd229f9f','a8eded6a2d062c998ba2dcc3dcb0ce68a4e15a58')]
        for kind,key,directory in cases:
            if args.kind not in ('all',kind):continue
            target='swh:1:rel:'+key
            for attempt in range(20):
                found=(await session.call_tool('fetch',{'source':'software-heritage','target':target,'parts':['metadata','fulltext']})).structuredContent
                report['calls'].append(found);save();component=found.get('components',{}).get('fulltext',{})
                print(json.dumps({'target':target,'status':found['status'],'content_status':component.get('status'),'code':component.get('code'),'attempt':attempt}),flush=True)
                if component.get('status')!='pending':break
                await asyncio.sleep(component['retry_after_seconds'])
            if component.get('status')!='available':return
            assert found['archive_selection']['directory_swhid']=='swh:1:dir:'+directory
            assert component['integrity']['verified'] and component['integrity']['digest']==directory
            selected=(await session.call_tool('extract',{'ref':component['artifact']['ref'],'count':1})).structuredContent
            report['calls'].append(selected);save()
            assert selected['status']=='ok' and selected['returned']==1
        report['completed']=True;save();print(json.dumps({'completed':True}),flush=True)
asyncio.run(main())
