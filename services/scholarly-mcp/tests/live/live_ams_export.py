"""AMS selected-product XLSX through a fresh stdio server and extraction."""
import argparse,asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[2]

async def main(credential_root=None):
    report={'source':'ams','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-ams-export-mcp.json'
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
            await call('describe_source',{'source':'ams'})
            found=await call('search',{'source':'ams','query':'algebra','limit':1,'export':'xlsx'})
            if found['status']!='ok':return
            assert found['received']==1 and found['total']>1000 and found['next']['start']==1
            selected=await call('extract',{'ref':found['records']['ref'],'count':1})
            exported=found['export']['artifacts']
            assert len(exported)==1 and exported[0]['product_code']==selected['items'][0]['ProductCode']
            rows=await call('extract',{'ref':exported[0]['artifact']['ref'],'selection':'Products','count':10})
            assert rows['status']=='ok'
            assert rows['total']==exported[0]['physical_rows']+1
            book=await call('fetch',{'source':'ams','target':selected['items'][0]['ProductCode'],'parts':['metadata','abstract']})
            assert book['components']['metadata']['status']=='available'
            report['completed']=True
    finally:
        report['finished']=datetime.now(timezone.utc).isoformat();save()
        print(json.dumps({'completed':report['completed']}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--credential-root',type=Path)
    asyncio.run(main(parser.parse_args().credential_root))
