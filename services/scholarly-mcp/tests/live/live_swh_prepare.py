"""Observe preparation and eventual download of a small archived Tools directory."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[2]
async def main():
    target='swh:1:dir:93ea4d40f1ace5b45af5a4a65993a87ad6e900d1'
    report={'source':'software-heritage','target':target,'calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-swh-prepare-mcp.json'
    def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        for attempt in range(12):
            result=(await session.call_tool('fetch',{'source':'software-heritage','target':target,'parts':['metadata','fulltext']})).structuredContent
            report['calls'].append(result);save()
            component=result.get('components',{}).get('fulltext',result)
            print(json.dumps({'attempt':attempt+1,'status':component['status'],'code':component.get('code')}),flush=True)
            if component['status']=='available':
                assert component['integrity']['verified'];report['completed']=True;save();break
            assert component['status']=='pending'
            await asyncio.sleep(component['retry_after_seconds'])
        print(json.dumps({'completed':report['completed']}),flush=True)
asyncio.run(main())
