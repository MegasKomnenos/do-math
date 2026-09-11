"""Exercise documented nested criteria and a result window across native pages."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]
async def main():
    expression={'condition':'AND','terms':[{'field':'Title','operator':'contains','value':'algebra'},
        {'condition':'OR','terms':[{'field':'PublicationYear','operator':'equals','value':'2000'},
                                 {'field':'PublicationYear','operator':'equals','value':'2001'}]}]}
    report={'source':'ams','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-ams-expression-mcp.json'
    def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        async def call(tool,args):
            result=(await session.call_tool(tool,args)).structuredContent
            report['calls'].append({'tool':tool,'arguments':args,'result':result});save()
            print(json.dumps({'tool':tool,'status':result['status'],'code':result.get('code')}),flush=True)
            return result
        await call('describe_source',{'source':'ams'})
        found=await call('search',{'source':'ams','query':'','options':{'expression':expression},'limit':13,'export':'csv'})
        if found['status']!='ok':return
        assert found['received']==min(13,found['total'])
        extracted=await call('extract',{'ref':found['records']['ref'],'count':13})
        assert extracted['returned']==found['received']
        if found['total']>12:
            next_window=await call('search',{'source':'ams','query':'','options':{'expression':expression},'start':11,'limit':2})
            if next_window['status']!='ok':return
            rows=await call('extract',{'ref':next_window['records']['ref'],'count':2})
            assert rows['items']==extracted['items'][11:13]
        report['completed']=True;save();print(json.dumps({'completed':True}),flush=True)
asyncio.run(main())
