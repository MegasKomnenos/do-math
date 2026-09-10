"""Run Semantic Scholar's public paper, citation and graph routes through stdio."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]
async def main():
    report={'source':'semantic-scholar','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-semantic-scholar-mcp.json'
    def preserve():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    preserve();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        async def call(name,args):
            value=(await session.call_tool(name,args)).structuredContent
            report['calls'].append({'tool':name,'arguments':args,'result':value});preserve()
            print(json.dumps({'tool':name,'status':value['status'],'code':value.get('code'),'received':value.get('received')}),flush=True)
            return value
        await call('describe_source',{'source':'semantic-scholar'})
        found=await call('search',{'source':'semantic-scholar','query':'Construction of the Literature Graph in Semantic Scholar','limit':1,'export':'bibtex'})
        assert found['status']=='ok'
        record=await call('extract',{'ref':found['records']['ref'],'count':1})
        identifier=record['items'][0]['paperId']
        fetched=await call('fetch',{'source':'semantic-scholar','target':record['items'][0]['url'],'parts':['metadata','abstract','export','supplementary']})
        assert fetched['status']=='ok'
        graph=await call('search',{'source':'semantic-scholar','query':identifier,'options':{'kind':'citations'},'limit':2})
        assert graph['status']=='ok'
        named=await call('fetch',{'source':'semantic-scholar','target':record['items'][0]['title'],'parts':['metadata']})
        assert named['status']=='selection_required'
        report['completed']=True;preserve()
asyncio.run(main())
