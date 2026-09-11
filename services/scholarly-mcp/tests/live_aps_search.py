"""Use native APS institution search, exports and page boundaries through stdio."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]
async def main():
    report={'source':'aps-institutional','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-aps-search-mcp.json'
    def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        async def call(tool,args):
            result=(await session.call_tool(tool,args)).structuredContent
            report['calls'].append({'tool':tool,'arguments':args,'result':result});save()
            print(json.dumps({'tool':tool,'status':result['status'],'code':result.get('code'),'received':result.get('received'),'total':result.get('total')}),flush=True)
            return result
        await call('describe_source',{'source':'aps-institutional'})
        first=await call('search',{'source':'aps-institutional','query':'algebra','limit':2,'export':'csv'})
        if first['status']!='ok':return
        native=await call('extract',{'ref':first['records']['ref'],'count':2})
        csv=await call('extract',{'ref':first['export']['ref'],'count':2})
        assert [x['doi'] for x in native['items']]==[x['doi'] for x in csv['items']]
        page=await call('search',{'source':'aps-institutional','query':'algebra','start':19,'limit':2,'export':'html'})
        report['pagination_verified']=page['status']=='ok' and page['received']==2;save()
        if report['pagination_verified']:
            assert len(page['evidence'])==2
            later=await call('extract',{'ref':page['records']['ref'],'count':2})
            assert len({row['doi'] for row in later['items']})==2
        title=await call('search',{'source':'aps-institutional','query':'algebra','options':{'field':'title'},'limit':2})
        report['title_field_verified']=title['status']=='ok';save()
        record=await call('fetch',{'source':'aps-institutional','target':native['items'][0]['url'],'parts':['metadata','abstract']})
        report['core_workflow_completed']=record['status']=='ok';save()
        if not report['pagination_verified'] or not report['title_field_verified']:return
        if record['status']!='ok':return
        report['completed']=True;save();print(json.dumps({'completed':True}),flush=True)
asyncio.run(main())
