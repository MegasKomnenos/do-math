"""Fresh SDK checks for ACM extra CSL items and 10.5555 Guide keys."""
from pathlib import Path
from datetime import datetime,timezone
import asyncio,json,shutil,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[2];ROOT=SERVICE.parents[1]
PRIVATE=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260912/acm-advanced-agent/sdk-boundaries'
REPORT=SERVICE/'data/access-research/acm-advanced/live-sdk-boundaries.json'

def credentials(run):
    target=run/'credentials';(target/'scholarly-mcp').mkdir(parents=True)
    shutil.copy2(ROOT/'.credentials/kudos.md',target/'kudos.md')
    shutil.copy2(ROOT/'.credentials/scholarly-mcp/kudos-firefox.json',target/'scholarly-mcp/kudos-firefox.json')
    return target

async def case(name,arguments,follow_fetch=False):
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');run=PRIVATE/(name+'-'+stamp);credential_root=credentials(run)
    server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(run/'artifacts'),'--credential-root',str(credential_root)])
    async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
        await session.initialize();found=(await session.call_tool('search',arguments)).structuredContent
        row={'status':found.get('status'),'code':found.get('code'),'received':found.get('received'),'total':found.get('total')}
        if found.get('records'):
            extracted=(await session.call_tool('extract',{'ref':found['records']['ref'],'count':1})).structuredContent
            items=extracted.get('items',[]);row['records']={'status':extracted.get('status'),'returned':extracted.get('returned'),
                'id':items[0].get('id') if items else None,'title':items[0].get('title') if items else None}
        scopes=found.get('export_scopes',[])
        row['export']={'status':found.get('export',{}).get('status') if isinstance(found.get('export'),dict) else None,
            'source_export':bool(found.get('source_export')),
            'scopes':[{key:scope.get(key) for key in ('requested_identifiers','included_identifiers','additional_identifiers','selection_status')} for scope in scopes]}
        if follow_fetch and row.get('records',{}).get('id'):
            fetched=(await session.call_tool('fetch',{'source':'acm-dl','target':row['records']['id'],'parts':['metadata','export']})).structuredContent
            row['fetch']={'status':fetched.get('status'),'target':fetched.get('target'),
                'components':{key:value.get('status') for key,value in fetched.get('components',{}).items()},
                'source_export':bool(fetched.get('source_export')),'export_scope':{key:fetched.get('export_scope',{}).get(key)
                    for key in ('requested_identifiers','included_identifiers','additional_identifiers','selection_status','rendered_count')}}
        return row

async def main():
    PRIVATE.mkdir(parents=True,exist_ok=True);REPORT.parent.mkdir(parents=True,exist_ok=True)
    report={'started_at':datetime.now(timezone.utc).isoformat(),'completed':False}
    common={'source':'acm-dl','query':'algebra','limit':1,'export':'bibtex'}
    try:
        report['extra']=await case('extra',{**common,'options':{'sort':'cited','facets':[
            {'field':'SeriesKey','value':'sigplan','panel':'Journal/MagazineNames'},
            {'field':'ContentItemType','value':'research-article','panel':'ContentType'}]}})
        report['guide']=await case('guide',{**common,'options':{'sort':'EpubDate_desc','facets':[
            {'field':'SeriesKey','value':'jmlr','panel':'Journal/MagazineNames'},
            {'field':'ContentItemType','value':'research-article','panel':'ContentType'}]}},True)
        scopes=report['extra'].get('export',{}).get('scopes',[]);scope=scopes[0] if scopes else {}
        report['completed']=report['extra'].get('status')=='partial' and len(scope.get('included_identifiers',[]))==2 \
            and len(scope.get('additional_identifiers',[]))==1 and report['guide'].get('status')=='ok' \
            and str(report['guide'].get('records',{}).get('id','')).startswith('10.5555/') \
            and report['guide'].get('fetch',{}).get('components')=={'metadata':'available','export':'available'}
    except Exception as error:report['error_type']=type(error).__name__
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat();REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'completed':report['completed'],'extra':report.get('extra'),'guide':report.get('guide'),'error_type':report.get('error_type')},ensure_ascii=False))

if __name__=='__main__':asyncio.run(main())
