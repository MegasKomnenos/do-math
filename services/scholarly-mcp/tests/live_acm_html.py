"""One fresh stdio retry of the verified ACM HTML full-text document."""
from pathlib import Path
from datetime import datetime,timezone
import asyncio,json,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[1];ROOT=SERVICE.parents[1]
PRIVATE=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260912/acm-advanced-agent/sdk-html'
CREDENTIALS=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260912/acm-advanced-agent/edit-search/credentials'
REPORT=SERVICE/'data/access-research/acm-advanced/live-sdk-html.json'

async def main():
    PRIVATE.mkdir(parents=True,exist_ok=True);REPORT.parent.mkdir(parents=True,exist_ok=True)
    report={'started_at':datetime.now(timezone.utc).isoformat(),'transport':'fresh_sdk_stdio','completed':False}
    server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(PRIVATE/'artifacts'),'--credential-root',str(CREDENTIALS)])
    try:
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize();value=(await session.call_tool('fetch',{'source':'acm-dl','target':'10.1145/3831699',
                'parts':['metadata','fulltext_html']})).structuredContent
            html=value.get('components',{}).get('fulltext_html',{});math=html.get('math',{})
            report['fetch']={'status':value.get('status'),'code':value.get('code'),'metadata_status':value.get('components',{}).get('metadata',{}).get('status'),
                'html_status':html.get('status'),'html_bytes':html.get('artifact',{}).get('bytes'),'document_doi':html.get('artifact',{}).get('document_doi'),
                'math_count':math.get('count')}
            if html.get('status')=='available':
                extracted=(await session.call_tool('extract',{'ref':html['artifact']['ref'],'count':3})).structuredContent
                math_items=(await session.call_tool('extract',{'ref':math['artifact']['ref'],'count':100})).structuredContent
                report['extract']={'html_status':extracted.get('status'),'html_total':extracted.get('total'),
                    'math_status':math_items.get('status'),'math_returned':math_items.get('returned'),'math_total':math_items.get('total')}
                report['completed']=math.get('count')==30 and math_items.get('returned')==30
    except Exception as error:report['error_type']=type(error).__name__
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat();REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'completed':report['completed'],'fetch':report.get('fetch'),'extract':report.get('extract'),'error_type':report.get('error_type')},ensure_ascii=False))

if __name__=='__main__':asyncio.run(main())
