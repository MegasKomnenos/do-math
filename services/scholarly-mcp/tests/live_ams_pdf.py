"""Verify an explicit AMS PDF through a real stdio MCP client."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]
async def main():
    report={'source':'ams','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-ams-pdf-mcp.json'
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        found=(await session.call_tool('fetch',{'source':'ams','target':'https://www.ams.org/books/gsm/128/gsm128-endmatter.pdf','parts':['metadata','fulltext','export']})).structuredContent
        report['calls'].append(found)
        path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({'status':found['status'],'code':found.get('code'),'report':str(path)}),flush=True)
        assert found['status']=='ok',found.get('code')
        if found['status']=='ok':
            extracted=(await session.call_tool('extract',{'ref':found['components']['fulltext']['artifact']['ref'],'count':1})).structuredContent
            report['calls'].append(extracted)
            assert extracted['total']==51
            assert found['components']['metadata']['kind']=='embedded_pdf_metadata'
            report['completed']=True
            path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps({'completed':True,'pages':extracted['total']}),flush=True)
asyncio.run(main())
