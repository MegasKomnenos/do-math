"""Exercise all native formats and title candidates through the public MCP API."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[2]
async def main():
    report={'source':'dblp','calls':[],'completed':False};path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-dblp-documents-mcp.json'
    def save():path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        async def call(tool,args):
            result=(await session.call_tool(tool,args)).structuredContent;report['calls'].append({'tool':tool,'arguments':args,'result':result});save()
            print(json.dumps({'tool':tool,'status':result['status'],'code':result.get('code'),'received':result.get('received')}),flush=True);return result
        fetched=await call('fetch',{'source':'dblp','target':'conf/stoc/Cook71','parts':['metadata','export']})
        if fetched['status']!='ok':return
        files=fetched['components']['export']['artifacts'];assert len(files)==7
        for file in files:
            found=await call('extract',{'ref':file['artifact']['ref'],'count':2})
            assert found['status']=='ok' and found['returned']>0
        named=await call('fetch',{'source':'dblp','target':'The Complexity of Theorem-Proving Procedures','parts':['metadata']})
        assert named['status']=='selection_required'
        exported=await call('search',{'source':'dblp','query':'P versus NP','start':1,'limit':2,'export':'ris'})
        if exported['status']!='ok':return
        assert len(exported['export']['artifacts'])==2
        report['completed']=True;save();print(json.dumps({'completed':True}),flush=True)
asyncio.run(main())
