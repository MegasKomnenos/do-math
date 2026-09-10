"""Verify that an AIP supplement remains an explicit Figshare selection."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]
async def main():
    report={'source':'aip','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-aip-supplement-mcp.json'
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        found=(await session.call_tool('fetch',{'source':'aip','target':'https://pubs.aip.org/aip/apq/article/2/3/036104/3358451/On-demand-single-photon-generation-and-coherent','parts':['metadata','supplementary']})).structuredContent
        report['calls'].append(found)
        path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({'status':found['status'],'code':found.get('code'),'report':str(path)}),flush=True)
        component=found['components']['supplementary']
        assert component['status']=='selection_required' and component['received']==0
        extracted=(await session.call_tool('extract',{'ref':component['artifact']['ref'],'count':2})).structuredContent
        report['calls'].append(extracted)
        assert extracted['returned']==1 and extracted['items'][0]['target']=='10.60893/figshare.aip.c.7956296'
        assert extracted['items'][0]['source']=='figshare'
        report['completed']=True
        path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({'completed':True,'references':extracted['returned']}),flush=True)
asyncio.run(main())
