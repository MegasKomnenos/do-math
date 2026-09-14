"""Exercise JSTOR query fields, page marks, filters and exports through stdio."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[2]
async def main():
    report={'source':'jstor','calls':[],'completed':False};path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-jstor-search-mcp.json'
    def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        async def call(tool,args):
            result=(await session.call_tool(tool,args)).structuredContent;report['calls'].append({'tool':tool,'arguments':args,'result':result});save()
            print(json.dumps({'tool':tool,'status':result['status'],'code':result.get('code'),'received':result.get('received'),'total':result.get('total')}),flush=True)
            return result
        found=await call('search',{'source':'jstor','query':'algebra','start':24,'limit':2,'export':'csv'})
        if found['status']!='ok':return
        assert found['received']==2 and len(found['evidence'])==2
        native=await call('extract',{'ref':found['records']['ref'],'count':2});csv=await call('extract',{'ref':found['export']['ref'],'count':2})
        assert [r['id'] for r in native['items']]==[r['id'] for r in csv['items']]
        assert native['items'][1]['id']=='43303777'
        filtered=await call('search',{'source':'jstor','query':'algebra','limit':2,'options':{'content_types':['journal'],'start_date':'2020','end_date':'2025'}})
        if filtered['status']!='ok':return
        assert filtered['total']==7837
        selected=await call('search',{'source':'jstor','query':'ti:algebra AND au:Sawyer','limit':2,'export':'ris'})
        if selected['status']!='ok':return
        assert selected['total']==9 and len(selected['export']['artifacts'])==2
        citation=await call('extract',{'ref':selected['export']['artifacts'][1]['artifact']['ref'],'count':1})
        assert citation['status']=='ok' and '24931626' in json.dumps(citation)
        all_content=await call('search',{'source':'jstor','query':'algebra','limit':1,'options':{'access':'all'}})
        if all_content['status']!='ok':return
        assert all_content['source_total']>found['source_total']
        empty=await call('search',{'source':'jstor','query':'"zzzxqvnevermatching987654321"','limit':2})
        assert empty['status']=='not_found' and empty['received']==empty['total']==0
        images=await call('search',{'source':'jstor','query':'algebra','start':24,'limit':2,'options':{'content_types':['contributed_images']}})
        if images['status']!='ok':return
        assert images['received']==2 and images['total']==images['source_total']==242 and images['result_group']=='image-results-matrix'
        facets=await call('search',{'source':'jstor','query':'algebra','limit':2,'options':{'sort':'oldest','content_types':['journal'],'subjects':['mathematics-discipline'],'languages':['eng OR en OR EN']}})
        if facets['status']!='ok':return
        named=await call('fetch',{'source':'jstor','target':'The Fundamental Theorem of Algebra and Linear Algebra','parts':['metadata']})
        assert named['status']=='selection_required' and named['received']>0
        assert any(item['id']=='3647746' for item in named['preview'])
        other_doi=await call('fetch',{'source':'jstor','target':'10.5951/mathteacher.108.9.0696','parts':['metadata','export']})
        assert other_doi['status']=='ok'
        report['completed']=True;save();print(json.dumps({'completed':True}),flush=True)
asyncio.run(main())
