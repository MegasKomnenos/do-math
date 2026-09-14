"""Verify the native PQDT supplemental PNG action and MCP image extraction."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[2]
async def main():
    report={'source':'pqdt','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-pqdt-supplement-mcp.json'
    def preserve():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        found=(await session.call_tool('fetch',{'source':'pqdt','target':'2485541561','parts':['metadata','supplementary']})).structuredContent
        report['calls'].append(found);preserve()
        print(json.dumps({'status':found['status'],'code':found.get('code'),'report':str(path)}),flush=True)
        assert found['status']=='ok'
        files=found['components']['supplementary']['files']
        assert len(files)==1 and files[0]['artifact']['bytes']==529775
        result=await session.call_tool('extract',{'ref':files[0]['artifact']['ref']})
        extracted=result.structuredContent;report['calls'].append(extracted)
        assert extracted['status']=='ok' and extracted['unit']=='image'
        assert any(item.type=='image' for item in result.content)
        report['completed']=True;preserve();print(json.dumps({'completed':True,'bytes':extracted['bytes']}),flush=True)
asyncio.run(main())
