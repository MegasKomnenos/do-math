"""Verify newest public API and explicitly ranked institutional IOP searches."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]
async def main():
    report={'source':'iop','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-iop-search-mcp.json'
    def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        async def call(tool,args):
            result=(await session.call_tool(tool,args)).structuredContent
            report['calls'].append({'tool':tool,'arguments':args,'result':result});save()
            print(json.dumps({'tool':tool,'status':result['status'],'code':result.get('code'),'received':result.get('received'),'retrieval':result.get('retrieval')}),flush=True)
            return result
        await call('describe_source',{'source':'iop'})
        newest=await call('search',{'source':'iop','query':'complexity','options':{'page_size':10},'start':9,'limit':2,'export':'rss'})
        report['api_window_verified']=newest['status']=='ok' and newest.get('retrieval')=='rss_api';save()
        if report['api_window_verified']:
            assert newest['received']==2 and len(newest['evidence'])==2
            rows=await call('extract',{'ref':newest['records']['ref'],'count':2})
            assert len({x['doi'] for x in rows['items']})==2
        beyond=await call('search',{'source':'iop','query':'complexity','options':{'page_size':10},'start':500,'limit':2})
        report['api_beyond_500_verified']=beyond['status']=='ok' and beyond.get('received')==2;save()
        ranked=await call('search',{'source':'iop','query':'complexity','options':{'sort':'relevance','page_size':10},'start':9,'limit':2,'export':'csv'})
        report['ranked_window_verified']=ranked['status']=='ok' and ranked.get('received')==2;save()
        if report['ranked_window_verified']:
            assert ranked['total'] is None and ranked['accessible_total']==500
            csv=await call('extract',{'ref':ranked['export']['ref'],'count':2})
            assert csv['returned']==2
        filtered=await call('search',{'source':'iop','query':'complexity','options':{'sort':'oldest','journals':['1742-6596'],'pub_type':['article'],'open_access':True,'page_size':20},'limit':2})
        report['filters_verified']=filtered['status']=='ok' and filtered.get('received')==2;save()
        rejected=await call('search',{'source':'iop','query':'complexity','options':{'sort':'relevance'},'start':500,'limit':1})
        assert rejected['status']=='unsupported' and rejected['code']=='source_window_limit'
        empty=await call('search',{'source':'iop','query':'qzjxwv947231','options':{'sort':'relevance'},'limit':2})
        report['zero_verified']=empty['status']=='not_found' and empty.get('total')==0;save()
        report['completed']=all(report.get(k) for k in ('api_window_verified','api_beyond_500_verified','ranked_window_verified','filters_verified','zero_verified'));save();print(json.dumps({'completed':report['completed']}),flush=True)
asyncio.run(main())
