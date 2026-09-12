"""AMS basic native page boundaries and zero results through stdio."""
import argparse,asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]

async def main(credential_root=None):
    report={'source':'ams','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-ams-search-mcp.json'
    def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    args=[str(root/'server.py')]
    if credential_root:args+=['--credential-root',str(credential_root)]
    save();print(json.dumps({'report':str(path)}),flush=True)
    try:
        async with stdio_client(StdioServerParameters(command=sys.executable,args=args)) as (read,write),ClientSession(read,write) as session:
            await session.initialize()
            async def call(tool,args):
                result=(await session.call_tool(tool,args)).structuredContent
                report['calls'].append({'tool':tool,'arguments':args,'result':result});save()
                print(json.dumps({'tool':tool,'status':result['status'],'code':result.get('code'),'received':result.get('received'),'total':result.get('total')}),flush=True)
                return result
            first=await call('search',{'source':'ams','query':'algebra','limit':13,'export':'csv'})
            if first['status']!='ok':return
            records=await call('extract',{'ref':first['records']['ref'],'count':13})
            assert len(records['items'])==13
            window=await call('search',{'source':'ams','query':'algebra','start':11,'limit':2,'export':'native'})
            if window['status']!='ok':return
            selected=await call('extract',{'ref':window['records']['ref'],'count':2})
            assert selected['items']==records['items'][11:13]
            assert len(window['export']['artifacts'])==2
            empty=await call('search',{'source':'ams','query':'zz_no_such_ams_title_20260912','limit':1})
            assert empty['status']=='not_found' and empty['total']==0
            report['completed']=True
    finally:
        report['finished']=datetime.now(timezone.utc).isoformat();save()
        print(json.dumps({'completed':report['completed']}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--credential-root',type=Path)
    asyncio.run(main(parser.parse_args().credential_root))
