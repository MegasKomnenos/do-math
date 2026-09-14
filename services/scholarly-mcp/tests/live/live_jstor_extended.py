"""Verify native snippets, BCE dates and mixed-group windows through MCP."""
import asyncio,json,sys,re
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[2]
async def main():
    report={'source':'jstor','calls':[],'completed':False};path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-jstor-extended-mcp.json'
    def save():path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        async def call(tool,args):
            found=(await session.call_tool(tool,args)).structuredContent;report['calls'].append({'tool':tool,'arguments':args,'result':found});save()
            print(json.dumps({'tool':tool,'status':found['status'],'code':found.get('code'),'received':found.get('received'),'total':found.get('total')}),flush=True);return found
        found=await call('search',{'source':'jstor','query':'algebra','limit':2,'options':{'snippets':True}})
        if found['status']!='ok':return
        rows=await call('extract',{'ref':found['records']['ref'],'count':2})
        assert all(row['snippet']['status']=='available' and 'algebra' in row['snippet']['text'].lower() for row in rows['items'])
        bce=await call('search',{'source':'jstor','query':'vase','limit':2,'options':{'start_date':'-0500','end_date':'-0100'}})
        if bce['status']!='ok':return
        assert bce['total']==14936
        rows=await call('extract',{'ref':bce['records']['ref'],'count':2})
        assert all(re.search(r'B\.?C',row['publication_date_display']) for row in rows['items'])
        mixed=await call('search',{'source':'jstor','query':'algebra','start':24,'limit':2,'options':{'content_types':['journal','contributed_images']},'export':'csv'})
        if mixed['status']!='ok':return
        assert mixed['received']==4 and [g['received'] for g in mixed['result_groups']]==[2,2]
        rows=await call('extract',{'ref':mixed['records']['ref'],'count':4});csv=await call('extract',{'ref':mixed['export']['ref'],'count':4})
        assert [r['id'] for r in rows['items']]==[r['id'] for r in csv['items']]
        assert len({r['result_group'] for r in rows['items']})==2
        report['completed']=True;save();print(json.dumps({'completed':True}),flush=True)
asyncio.run(main())
