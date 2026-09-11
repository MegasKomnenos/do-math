"""Native formats and selected windows through one actual stdio session."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]
async def main():
    report={'source':'ieee-xplore','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-ieee-exports-mcp.json'
    def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        async def call(tool,args):
            result=(await session.call_tool(tool,args)).structuredContent
            report['calls'].append({'tool':tool,'arguments':args,'result':result});save()
            print(json.dumps({'tool':tool,'status':result['status'],'code':result.get('code'),'received':result.get('received')}),flush=True)
            return result
        for format in ('bibtex','ris','plain','csv'):
            found=await call('search',{'source':'ieee-xplore','query':'"Article Number":10488889','limit':1,'export':format})
            if found['status']!='ok':return
            extracted=await call('extract',{'ref':found['export']['ref'],'count':10})
            assert '10.1109/MC.2024.3358928' in json.dumps(extracted['items'])
            if format!='plain':assert extracted['total']==1
        for start,count in ((0,1),(1,2)):
            found=await call('search',{'source':'ieee-xplore','query':'"Document Title":complexity','start':start,'limit':count,'export':'csv'})
            if found['status']!='ok':return
            extracted=await call('extract',{'ref':found['export']['ref'],'count':count})
            records=await call('extract',{'ref':found['records']['ref'],'count':count})
            assert extracted['total']==count and [r['DOI'].casefold() for r in extracted['items']]==[r['doi'].casefold() for r in records['items']]
        report['completed']=True;save();print(json.dumps({'completed':True}),flush=True)
asyncio.run(main())
