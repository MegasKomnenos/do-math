"""Verify an actual public script-rendered preprint through author-repository."""
from pathlib import Path
from datetime import datetime,timezone
import asyncio,json,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[2];ROOT=SERVICE.parents[1]
PRIVATE=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260912/limitations-audit/osf-live'
CREDENTIALS=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260912/limitations-audit/osf/credentials'
REPORT=SERVICE/'data/access-research/limitations-audit/independent-webdocuments-osf-sdk.json'
TARGET='https://osf.io/preprints/socarxiv/9apsq_v1/'
TITLE='Start-up certification and prices: Evidence from markups and a statutory expiry in Italy'

async def main():
    PRIVATE.mkdir(parents=True,exist_ok=True);report={'started_at':datetime.now(timezone.utc).isoformat(),'completed':False}
    server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(PRIVATE/'data'),'--credential-root',str(CREDENTIALS)])
    try:
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize();value=(await session.call_tool('fetch',{'source':'author-repository','target':TARGET,'parts':['metadata']})).structuredContent
            extracted=(await session.call_tool('extract',{'ref':value['records']['ref'],'count':1})).structuredContent if value.get('records') else {}
            item=extracted.get('items',[{}])[0] if extracted.get('items') else {}
            report.update({'status':value.get('status'),'target':value.get('target'),'media_type':value.get('source_document',{}).get('media_type'),
                'bytes':value.get('source_document',{}).get('bytes'),'record_type':item.get('type'),'title':item.get('title'),'extract_status':extracted.get('status')})
            report['completed']=value.get('status')=='ok' and str(item.get('title','')).casefold()==TITLE.casefold() and item.get('type')=='web_document'
    except Exception as error:report['error_type']=type(error).__name__
    finally:report['finished_at']=datetime.now(timezone.utc).isoformat();REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'completed':report['completed'],'status':report.get('status'),'media_type':report.get('media_type'),'bytes':report.get('bytes'),'record_type':report.get('record_type'),'title_match':str(report.get('title','')).casefold()==TITLE.casefold(),'error_type':report.get('error_type')},ensure_ascii=False))

if __name__=='__main__':asyncio.run(main())
