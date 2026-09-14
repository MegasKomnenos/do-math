"""Export the selected IOP search records through the native citation controls."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[2]
async def main():
    report={'source':'iop','calls':[],'completed':False};path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-iop-search-citations-mcp.json'
    def save():path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        for format,options in [('bibtex',{}),('ris',{'sort':'relevance'})]:
            result=(await session.call_tool('search',{'source':'iop','query':'"Mastering data complexity"','limit':1,'options':options,'export':format})).structuredContent
            report['calls'].append(result);save();print(json.dumps({'format':format,'status':result['status'],'code':result.get('code'),'received':result.get('received')}),flush=True)
            if result['status']!='ok':return
            exported=result['export']['artifacts'];assert len(exported)==1
            extracted=(await session.call_tool('extract',{'ref':exported[0]['artifact']['ref'],'count':1})).structuredContent
            report['calls'].append(extracted);save();assert extracted['status']=='ok'
            assert 'add557' in json.dumps(extracted)
        report['completed']=True;save();print(json.dumps({'completed':True}),flush=True)
asyncio.run(main())
