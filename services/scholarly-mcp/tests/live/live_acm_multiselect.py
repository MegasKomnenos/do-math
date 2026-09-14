"""Fresh SDK verification of multiple ACM category values and facet groups."""
from pathlib import Path
from datetime import datetime,timezone
import asyncio,json,shutil,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[2];ROOT=SERVICE.parents[1]
PRIVATE=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260912/acm-advanced-agent/sdk-multiselect'
REPORT=SERVICE/'data/access-research/acm-advanced/live-sdk-multiselect.json'

async def main():
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');run=PRIVATE/stamp;credentials=run/'credentials';(credentials/'scholarly-mcp').mkdir(parents=True)
    shutil.copy2(ROOT/'.credentials/kudos.md',credentials/'kudos.md')
    shutil.copy2(ROOT/'.credentials/scholarly-mcp/kudos-firefox.json',credentials/'scholarly-mcp/kudos-firefox.json')
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    report={'started_at':datetime.now(timezone.utc).isoformat(),'transport':'fresh_sdk_stdio','private_run':stamp,'completed':False}
    server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(run/'artifacts'),'--credential-root',str(credentials)])
    try:
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize()
            facets=(await session.call_tool('search',{'source':'acm-dl','query':'algebra','options':{'sort':'EpubDate_desc','facets':[
                {'field':'SeriesKey','value':'cacm','panel':'Journal/MagazineNames'},
                {'field':'ContentItemType','value':'research-article','panel':'ContentType'}]},'limit':1,'export':'bibtex'})).structuredContent
            report['facets']={'status':facets.get('status'),'code':facets.get('code'),'total':facets.get('total'),'received':facets.get('received'),
                'selected':facets.get('facets'),'requested_count':facets.get('requested_count'),'item_count':facets.get('item_count'),
                'exported_doi_length':facets.get('exported_doi_length')}
            report['completed']=facets.get('status')=='ok' and type(facets.get('total')) is int and facets['total']>0 and len(facets.get('facets',[]))==2
    except Exception as error:report['error_type']=type(error).__name__
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat();REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'completed':report['completed'],'facets':report.get('facets'),'error_type':report.get('error_type')},ensure_ascii=False))

if __name__=='__main__':asyncio.run(main())
