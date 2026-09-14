"""Verify WOS incoming citing works and the existing outgoing CR through stdio."""
import argparse,asyncio,json,sys
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

root=Path(__file__).resolve().parents[2]
UT='WOS:000269418800023';DOI='10.1145/1562164.1562186'


async def main(credential_root=None):
    report={'source':'wos','scope':'incoming-citations','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-wos-citations-mcp.json'
    def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    args=[str(root/'server.py')]
    if credential_root:args+=['--credential-root',str(credential_root),'--data-dir',str(credential_root.parent/'data')]
    save();print(json.dumps({'report':str(path)}),flush=True)
    try:
        async with stdio_client(StdioServerParameters(command=sys.executable,args=args)) as (read,write),ClientSession(read,write) as session:
            await session.initialize()
            async def call(tool,args):
                result=(await session.call_tool(tool,args)).structuredContent
                report['calls'].append({'tool':tool,'arguments':args,'result':result});save()
                print(json.dumps({'tool':tool,'status':result['status'],'code':result.get('code'),'received':result.get('received'),'total':result.get('total')}),flush=True)
                return result
            await call('describe_source',{'source':'wos'})
            first=await call('search',{'source':'wos','query':UT,'options':{'kind':'citations'},'limit':2,'export':'plain'})
            if first['status']!='ok':return
            assert first['relation']=={'direction':'incoming','control_total':136,'result_total':125}
            assert first['received']==2 and first['next']=={'start':2}
            records=await call('extract',{'ref':first['records']['ref'],'count':2})
            exported=await call('extract',{'ref':first['export']['ref'],'count':2})
            assert records['returned']==exported['returned']==2
            boundary=await call('search',{'source':'wos','query':DOI,'options':{'kind':'citations'},'start':124,'limit':2,'export':'plain'})
            if boundary['status']!='ok':return
            assert boundary['received']==1 and boundary['total']==125 and not boundary['has_more']
            fetched=await call('fetch',{'source':'wos','target':UT,'parts':['supplementary']})
            if fetched['status']!='ok':return
            related=fetched['components']['supplementary']
            assert related['references']['direction']=='outgoing' and related['references']['count']>0
            assert related['citations']['direction']=='incoming' and related['citations']['total']==125
            report['completed']=True
    finally:
        report['finished']=datetime.now(timezone.utc).isoformat();save();print(json.dumps({'completed':report['completed']}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--credential-root',type=Path);args=parser.parse_args()
    asyncio.run(main(args.credential_root))
