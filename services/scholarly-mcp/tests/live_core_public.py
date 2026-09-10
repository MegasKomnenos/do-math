"""Verify credential-free CORE name selection and its full-text access state."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]
async def main():
    report={'source':'core','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-core-public-mcp.json'
    def preserve():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    preserve();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        names=(await session.call_tool('fetch',{'source':'core','target':'Deriving Safety Cases from Automatically Constructed Proofs','parts':['metadata']})).structuredContent
        report['calls'].append(names);preserve()
        print(json.dumps({'name_status':names['status'],'code':names.get('code')}),flush=True)
        assert names['status']=='selection_required'
        found=(await session.call_tool('fetch',{'source':'core','target':'https://core.ac.uk/works/340524929','parts':['metadata','abstract','fulltext']})).structuredContent
        report['calls'].append(found);preserve()
        print(json.dumps({'fetch_status':found['status'],'code':found.get('code')}),flush=True)
        assert found['components']['metadata']['status']=='available'
        assert found['components']['fulltext']['status']=='restricted'
        report['completed']=True;preserve();print(json.dumps({'completed':True}),flush=True)
asyncio.run(main())
