"""Verify revision history and snapshot bundles through fresh MCP stdio."""
import asyncio,json,sys,argparse
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]
async def main():
    parser=argparse.ArgumentParser();parser.add_argument('--target',action='append');args=parser.parse_args()
    targets=args.target or ['swh:1:rev:2db189928c94d62a3b4757b3eec68f0a4d4113f0','swh:1:snp:2611ba3c6ee63b2078ac02e597ee0e40df930a66']
    report={'source':'software-heritage','targets':targets,'calls':[],'completed':False};path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-swh-git-mcp.json'
    def save():path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        for target in targets:
            for attempt in range(12):
                found=(await session.call_tool('fetch',{'source':'software-heritage','target':target,'parts':['metadata','history']})).structuredContent
                report['calls'].append(found);save();component=found.get('components',{}).get('history',found)
                print(json.dumps({'target':target,'status':component.get('status'),'code':component.get('code'),'attempt':attempt}),flush=True)
                if component.get('status')!='pending':break
                await asyncio.sleep(component['retry_after_seconds'])
            if component.get('status')!='available':return
            assert component['integrity']['verified'] and component['integrity']['swhid']==target
            selected=(await session.call_tool('extract',{'ref':component['artifact']['ref'],'count':3})).structuredContent
            report['calls'].append(selected);save();assert selected['status']=='ok' and selected['returned']==3
        report['completed']=True;save();print(json.dumps({'completed':True}),flush=True)
asyncio.run(main())
