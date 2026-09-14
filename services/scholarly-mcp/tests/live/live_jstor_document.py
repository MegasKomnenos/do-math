"""Retrieve the selected JSTOR article, native citations and full PDF via stdio."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[2]
async def main():
    report={'source':'jstor','calls':[],'completed':False};path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-jstor-document-mcp.json'
    def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        result=(await session.call_tool('fetch',{'source':'jstor','target':'24931626','parts':['metadata','export','fulltext']})).structuredContent
        report['calls'].append(result);save();pdf=result.get('components',{}).get('fulltext',{})
        print(json.dumps({'status':result['status'],'pdf_status':pdf.get('status'),'code':pdf.get('code')}),flush=True)
        if result['status']!='ok':return
        assert pdf['artifact']['pages']==11 and len(result['components']['export']['artifacts'])==2
        extracted=(await session.call_tool('extract',{'ref':pdf['artifact']['ref'],'count':2})).structuredContent
        report['calls'].append(extracted);save()
        assert extracted['status']=='ok' and extracted['total']==11 and extracted['returned']==2
        assert '24931626' in extracted['items'][0]['text'] and 'ALGEBRA' in extracted['items'][1]['text'].upper()
        report['completed']=True;save();print(json.dumps({'completed':True,'pdf_pages':11}),flush=True)
asyncio.run(main())
