"""Verify one substantive non-Nature Springer HTML article through fresh stdio."""
from pathlib import Path
from datetime import datetime,timezone
import asyncio,json,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[2];ROOT=SERVICE.parents[1]
PRIVATE=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260912/limitations-audit/springer-live'
CREDENTIALS=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260912/limitations-audit/springer/credentials'
REPORT=SERVICE/'data/access-research/limitations-audit/independent-springer-sdk.json'

async def main():
    PRIVATE.mkdir(parents=True,exist_ok=True);report={'started_at':datetime.now(timezone.utc).isoformat(),'completed':False}
    server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(PRIVATE/'data'),'--credential-root',str(CREDENTIALS)])
    try:
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize();value=(await session.call_tool('fetch',{'source':'springer','target':'https://link.springer.com/article/10.1016/S1018-3639(18)30727-X','parts':['metadata','fulltext_html']})).structuredContent
            body=value.get('components',{}).get('fulltext_html',{});headings=(await session.call_tool('extract',{'ref':body['artifact']['ref'],'selection':'[id^="Sec"][id$="-section"] > h2','count':30})).structuredContent if body.get('artifact') else {}
            math=(await session.call_tool('extract',{'ref':body['artifact']['ref'],'selection':'span.mathjax-tex','count':100})).structuredContent if body.get('artifact') else {}
            from bs4 import BeautifulSoup
            labels=[item.get('text','') if isinstance(item,dict) else BeautifulSoup(str(item),'html.parser').get_text(' ',strip=True) for item in headings.get('items',[])]
            report.update({'status':value.get('status'),'target':value.get('target'),'body_status':body.get('status'),'html_bytes':body.get('artifact',{}).get('bytes'),
                'headings':labels,'heading_total':headings.get('total'),'math_total':math.get('total'),'figures':len(body.get('figures',[]))})
            report['completed']=value.get('target','').casefold().rstrip('/').endswith('10.1016/s1018-3639(18)30727-x') and body.get('status') in ('available','partial') \
                and headings.get('total')==7 and any('Introduction' in label for label in labels) and any('Conclusion' in label for label in labels)
    except Exception as error:report['error_type']=type(error).__name__
    finally:report['finished_at']=datetime.now(timezone.utc).isoformat();REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'completed':report['completed'],'status':report.get('status'),'body_status':report.get('body_status'),'html_bytes':report.get('html_bytes'),'heading_total':report.get('heading_total'),'math_total':report.get('math_total'),'figures':report.get('figures'),'error_type':report.get('error_type')},ensure_ascii=False))

if __name__=='__main__':asyncio.run(main())
