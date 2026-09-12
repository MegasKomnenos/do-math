"""ScienceDirect native title search, window and zero case through stdio."""
import argparse,asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]

async def main(credential_root=None):
    report={'source':'science-direct','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-science-direct-search-mcp.json'
    def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    server_args=[str(root/'server.py')]
    if credential_root:server_args+=['--credential-root',str(credential_root)]
    save();print(json.dumps({'report':str(path)}),flush=True)
    try:
        async with stdio_client(StdioServerParameters(command=sys.executable,args=server_args)) as (read,write),ClientSession(read,write) as session:
            await session.initialize()
            async def call(tool,args):
                result=(await session.call_tool(tool,args)).structuredContent
                report['calls'].append({'tool':tool,'arguments':args,'result':result});save()
                print(json.dumps({'tool':tool,'status':result['status'],'code':result.get('code'),'received':result.get('received'),'total':result.get('total')}),flush=True)
                return result
            await call('describe_source',{'source':'science-direct'})
            found=await call('search',{'source':'science-direct','query':'"Natural Proofs"','options':{'field':'Title'},'limit':2,'export':'csv'})
            if found['status']!='ok':return
            rows=await call('extract',{'ref':found['records']['ref'],'count':2})
            csv=await call('extract',{'ref':found['export']['ref'],'count':2})
            assert [row['pii'] for row in rows['items']]==[row['pii'] for row in csv['items']]
            boundary=await call('search',{'source':'science-direct','query':'algebra','start':24,'limit':2,'export':'ris'})
            if boundary['status']!='ok':return
            window=await call('extract',{'ref':boundary['records']['ref'],'count':2})
            assert len({row['pii'] for row in window['items']})==2
            assert len(boundary['export']['artifacts'])==2
            for row,item in zip(window['items'],boundary['export']['artifacts']):
                citation=await call('extract',{'ref':item['artifact']['ref'],'count':1})
                assert row['pii'].casefold() in json.dumps(citation).casefold()
            zero=await call('search',{'source':'science-direct','query':'zz_no_such_sci_title_20260912','options':{'field':'Title'},'limit':1})
            assert zero['status']=='not_found' and zero['total']==0
            report['completed']=True
    finally:
        report['finished']=datetime.now(timezone.utc).isoformat();save()
        print(json.dumps({'completed':report['completed']}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--credential-root',type=Path)
    asyncio.run(main(parser.parse_args().credential_root))
