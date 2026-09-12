"""Fresh stdio verification for ACM advanced search and HTML full text."""
from pathlib import Path
from datetime import datetime,timezone
import asyncio,json,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[1];ROOT=SERVICE.parents[1]
PRIVATE=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260912/acm-advanced-agent/sdk'
CREDENTIALS=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260912/acm-advanced-agent/edit-search/credentials'
REPORT=SERVICE/'data/access-research/acm-advanced/live-sdk.json'

def now():return datetime.now(timezone.utc).isoformat()
def safe(label,value):
    row={'label':label,'status':value.get('status'),'code':value.get('code')}
    for key in ('source','received','total','start','has_more','target','native_constraint','facet'):
        if key in value:row[key]=value[key]
    if 'components' in value:
        row['components']={key:{'status':item.get('status'),'code':item.get('code'),'media_type':item.get('artifact',{}).get('media_type'),
            'bytes':item.get('artifact',{}).get('bytes'),'pages':item.get('artifact',{}).get('pages'),
            'math_count':item.get('math',{}).get('count')} for key,item in value['components'].items()}
    return row

async def extract(session,artifact,count):
    value=(await session.call_tool('extract',{'ref':artifact['ref'],'count':count})).structuredContent
    return {'status':value.get('status'),'returned':value.get('returned'),'total':value.get('total')}

async def main():
    REPORT.parent.mkdir(parents=True,exist_ok=True);PRIVATE.mkdir(parents=True,exist_ok=True)
    report={'started_at':now(),'transport':'fresh_sdk_stdio','calls':[],'completed':False}
    def save():REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    save();server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(PRIVATE/'artifacts'),
        '--credential-root',str(CREDENTIALS)])
    try:
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize();report['protocol_initialized']=True
            combined=(await session.call_tool('search',{'source':'acm-dl','query':'algebra','options':{'field':'Title',
                'fields':[{'field':'Abstract','value':'complexity'}]},'limit':1,'export':'bibtex'})).structuredContent
            report['calls'].append(safe('two_fields_native_and',combined));save()
            constrained=(await session.call_tool('search',{'source':'acm-dl','query':'algebra','options':{'field':'Title',
                'constraint':{'field':'SeriesKey','operator':'Or','values':['Journal of the ACM','Communications of the ACM']}},'limit':1,'export':'bibtex'})).structuredContent
            report['calls'].append(safe('category_or',constrained));save()
            faceted=(await session.call_tool('search',{'source':'acm-dl','query':'algebra','options':{'field':'Title','from_year':2024,
                'to_year':2026,'sort':'cited','facet':{'field':'ContentItemType','value':'research-article'}},'limit':1,'export':'endnote'})).structuredContent
            report['calls'].append(safe('facet_date_sort',faceted));save()
            fetched=(await session.call_tool('fetch',{'source':'acm-dl','target':'10.1145/3831699',
                'parts':['metadata','export','fulltext','fulltext_html']})).structuredContent
            report['calls'].append(safe('html_and_pdf',fetched));save()
            html=fetched.get('components',{}).get('fulltext_html',{});math=html.get('math',{})
            if html.get('status')=='available':report['html_extract']=await extract(session,html['artifact'],3)
            if math.get('status')=='available':report['math_extract']=await extract(session,math['artifact'],100)
            report['checks']={
                'two_fields':combined.get('status')=='ok' and combined.get('received')==1,
                'category_or':constrained.get('status')=='ok' and constrained.get('native_constraint',{}).get('native_key')=='SeriesKeyOr'
                    and constrained.get('native_constraint',{}).get('native_values')==['jacm','cacm'] and constrained.get('total')==93,
                'facet_date_sort':faceted.get('status')=='ok' and faceted.get('facet',{}).get('value')=='research-article',
                'pdf':fetched.get('components',{}).get('fulltext',{}).get('status')=='available',
                'html':html.get('status')=='available' and html.get('artifact',{}).get('document_doi')=='10.1145/3831699',
                'math':math.get('count')==30 and report.get('math_extract',{}).get('returned')==30,
            }
            report['completed']=all(report['checks'].values());save()
    except Exception as error:report['error_type']=type(error).__name__
    finally:report['finished_at']=now();save()
    print(json.dumps({'completed':report['completed'],'calls':report['calls'],'checks':report.get('checks'),'error_type':report.get('error_type')},ensure_ascii=False))

if __name__=='__main__':asyncio.run(main())
