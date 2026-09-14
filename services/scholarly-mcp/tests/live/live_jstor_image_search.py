"""Verify image sorts and native resolution/geography/contributor facets."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[2]
async def main():
    report={'source':'jstor','calls':[],'completed':False};path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-jstor-image-search-mcp.json'
    def save():path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        async def call(tool,args):
            result=(await session.call_tool(tool,args)).structuredContent;report['calls'].append({'tool':tool,'arguments':args,'result':result});save()
            print(json.dumps({'tool':tool,'status':result['status'],'code':result.get('code'),'received':result.get('received'),'total':result.get('total')}),flush=True);return result
        first_ids=[]
        for sort in ['title_asc','title_desc','creator_asc','creator_desc','resolution']:
            result=await call('search',{'source':'jstor','query':'algebra','limit':2,'options':{'content_types':['contributed_images'],'sort':sort}})
            if result['status']!='ok':return
            first_ids.append(result['preview'][0]['id'])
        assert first_ids[0]!=first_ids[1] and first_ids[2]!=first_ids[3]
        raw=await call('extract',{'ref':result['facets']['ref'],'count':30});queue=list(raw['items']);fields={}
        while queue:
            node=queue.pop();queue.extend(node.get('h_values',[]))
            if node.get('field'):fields[node['field']]=node.get('values',[])
        for field,display,total in [('cc_media_resolution','>10 megapixels',47),('geography','Europe',5),('cc_portal_id','Northern State University',26)]:
            value=next(v['label'] for v in fields[field] if v.get('display')==display)
            found=await call('search',{'source':'jstor','query':'algebra','limit':2,'options':{'content_types':['contributed_images'],'facets':{field:[value]}}})
            if found['status']!='ok':return
            assert found['total']==total
        nested=await call('extract',{'ref':found['facets']['ref'],'count':30})
        collection=next(f for f in nested['items'] if f.get('field')=='cc_compilation_ids')
        selected=next(v['label'] for v in collection['values'] if v.get('display')=='NSU Pasque Collection')
        child=await call('search',{'source':'jstor','query':'algebra','limit':2,'options':{'content_types':['contributed_images'],
            'facets':{'cc_portal_id':['100689779'],'cc_compilation_ids':[selected]}}})
        assert child['status']=='ok' and child['total']==22
        report['completed']=True;save();print(json.dumps({'completed':True}),flush=True)
asyncio.run(main())
