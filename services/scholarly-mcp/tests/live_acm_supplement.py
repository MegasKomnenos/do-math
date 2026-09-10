"""Verify an ACM supplemental archive through the actual stdio tools."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]
async def main():
    report={'source':'acm-dl','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-acm-supplement-mcp.json'
    def preserve():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    preserve();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        found=(await session.call_tool('fetch',{'source':'acm-dl','target':'10.1145/3425501','parts':['metadata','abstract','export','supplementary']})).structuredContent
        report['calls'].append(found);preserve()
        print(json.dumps({'status':found['status'],'code':found.get('code')}),flush=True)
        assert found['status']=='ok'
        files=found['components']['supplementary']['files'];assert len(files)==1
        file=files[0]['artifact'];assert file['media_type']=='application/zip'
        extracted=(await session.call_tool('extract',{'ref':file['ref'],'count':20})).structuredContent
        report['calls'].append(extracted);preserve()
        assert extracted['status']=='ok' and extracted['returned']>0
        report['completed']=True;preserve();print(json.dumps({'completed':True,'bytes':file['bytes'],'members':extracted['total']}),flush=True)
asyncio.run(main())
