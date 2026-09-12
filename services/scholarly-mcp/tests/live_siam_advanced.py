"""Current native SIAM fields, autocomplete, dates, and filtered pagination via MCP."""
import argparse,asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]

async def main(credential_root=None):
    report={'source':'siam','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-siam-advanced-mcp.json'
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
            await call('describe_source',{'source':'siam'})
            cases=[('algebra',{'field':'Title','terms':[{'field':'Author','query':'Stetter'}]},0),
                   ('algebra',{'field':'Title','terms':[{'field':'Author','query':'Stetter'},{'field':'Anywhere','query':'polynomial'}]},0),
                   ('optimization',{'publication':'SIAM Journal on Optimization','published_within':'year'},19),
                   ('linear algebra',{'topic':'Linear Algebra and Matrix Theory','published_after':{'year':2024,'month':1},'published_before':{'year':2026,'month':9}},0)]
            for query,options,start in cases:
                found=await call('search',{'source':'siam','query':query,'options':options,'start':start,'limit':2,'export':'csv'})
                if found['status']!='ok':return
                assert found['received']==2 and found['total']>=2
                rows=await call('extract',{'ref':found['records']['ref'],'count':2})
                csv=await call('extract',{'ref':found['export']['ref'],'count':2})
                assert [row['doi'] for row in rows['items']]==[row['doi'] for row in csv['items']]
                if 'publication' in options:
                    assert len(found['evidence'])==2
                    assert all(row['type']=='article' and row['publication']==options['publication'] for row in rows['items'])
                if 'published_after' in options:
                    assert all(2024<=row['year']<=2026 for row in rows['items'])
            ambiguous=await call('search',{'source':'siam','query':'optimization','options':{'publication':'SIAM'},'limit':1})
            assert ambiguous['status']=='selection_required' and ambiguous.get('candidates')
            report['completed']=True
    finally:
        report['finished']=datetime.now(timezone.utc).isoformat();save()
        print(json.dumps({'completed':report['completed']}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--credential-root',type=Path)
    asyncio.run(main(parser.parse_args().credential_root))
