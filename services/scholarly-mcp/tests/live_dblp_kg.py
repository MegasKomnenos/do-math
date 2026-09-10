"""Exercise the explicitly selected public DBLP knowledge graph through stdio."""
import asyncio,json,sys
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]

async def main():
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-dblp-kg-mcp.json'
    report={'source':'dblp-kg','calls':[],'completed':False}
    def preserve():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    preserve();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        async def call(tool,arguments):
            data=(await session.call_tool(tool,arguments)).structuredContent
            report['calls'].append({'tool':tool,'arguments':arguments,'result':data});preserve()
            print(json.dumps({'tool':tool,'status':data['status'],'code':data.get('code'),'received':data.get('received')}),flush=True)
            return data
        guide=await call('describe_source',{'source':'dblp-kg'})
        assert guide['status']=='ok' and guide['usage']['examples']
        query=guide['usage']['examples'][0]['arguments']['query']
        first=await call('search',{'source':'dblp-kg','query':query,'limit':4})
        assert first['status']=='ok' and first['received']==4 and first['total'] is None
        rows=await call('extract',{'ref':first['records']['ref'],'count':4})
        for format in ('native','csv','tsv'):
            found=await call('search',{'source':'dblp-kg','query':query,'start':1,'limit':2,'export':format})
            assert found['status']=='ok' and found['received']==2
            window=await call('extract',{'ref':found['records']['ref'],'count':2})
            assert window['items']==rows['items'][1:3]
            exported=await call('extract',{'ref':found['export']['ref'],'count':3})
            assert exported['status']=='ok'
        for target in ('journals/jcss/RazborovR97','10.1006/jcss.1997.1494'):
            document=await call('fetch',{'source':'dblp-kg','target':target,'parts':['metadata','supplementary']})
            assert document['status']=='ok' and document['subjects']==['https://dblp.org/rec/journals/jcss/RazborovR97']
            assert document['statement_count']>10
        named=await call('fetch',{'source':'dblp-kg','target':'Natural Proofs','parts':['metadata']})
        assert named['status']=='selection_required'
        boundary=await call('search',{'source':'dblp-kg','query':'SELECT * WHERE { SERVICE <https://example.org/> {?s ?p ?o} }','limit':2})
        assert boundary['status']=='error' and boundary['code']=='source_boundary'
        report['completed']=True;preserve();print(json.dumps({'completed':True}),flush=True)

asyncio.run(main())
