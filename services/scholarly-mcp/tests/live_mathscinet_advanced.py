"""Fresh stdio checks for MathSciNet publication sorts and exact-label facets."""
from pathlib import Path
from datetime import datetime,timezone
import asyncio,json,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
SERVICE=Path(__file__).resolve().parents[1];ROOT=SERVICE.parents[1]
CREDENTIALS=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260913/mathscinet-prefix/credentials'
PRIVATE=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260913/limitations-audit-mathscinet/sdk'
REPORT=SERVICE/'data/access-research/limitations-audit/institutional-mathscinet-sdk.json';QUERY='ti:(algebra)'
def now():return datetime.now(timezone.utc).isoformat()
def safe(label,value):return {key:item for key,item in {'label':label,'status':value.get('status'),'code':value.get('code'),'total':value.get('total'),
    'received':value.get('received'),'sort':value.get('sort'),'facet_groups':value.get('facet_groups'),
    'filter_evidence_count':len(value.get('filter_evidence') or []),'facet_candidates':value.get('facet_candidates'),'field':value.get('field'),
    'candidate_group_count':value.get('candidate_group_count'),'stage':value.get('stage'),'error_type':value.get('error_type'),'observed_host':value.get('observed_host'),
    'attached_group_count':value.get('attached_group_count'),'panel_display':value.get('panel_display'),
    'filter_button_count':value.get('filter_button_count'),
    'page_path':value.get('page_path'),'page_title':value.get('page_title'),'main_text':value.get('main_text'),
    'query_keys':value.get('query_keys'),'facets_present':value.get('facets_present'),'selected':value.get('selected'),
    'query_matches':value.get('query_matches'),'query_length':value.get('query_length'),
    'observed_query':value.get('observed_query'),'native_query':value.get('native_query'),'filter_state':value.get('filter_state'),
    'candidate_labels':[item.get('label') for item in value.get('candidates',[])[:12]] if isinstance(value.get('candidates'),list) else None}.items() if item is not None}
async def main():
    PRIVATE.mkdir(parents=True,exist_ok=True);report={'source':'mathscinet','started_at':now(),'calls':[],'completed':False}
    server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(PRIVATE/'artifacts'),'--credential-root',str(CREDENTIALS)])
    try:
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize()
            if '--preview' in sys.argv:
                preview=(await session.call_tool('search',{'source':'mathscinet','query':QUERY,'options':{'facet_group':'journals','facet_query':'J. Algebra'},'limit':1})).structuredContent
                report['calls'].append(safe('candidate_search',preview));report['checks']={'preview':preview.get('status')=='ok' and bool(preview.get('facet_candidates'))}
                report['completed']=all(report['checks'].values());return
            if '--sorts' in sys.argv:
                for sort in ('author-count','paging'):
                    value=(await session.call_tool('search',{'source':'mathscinet','query':QUERY,'options':{'sort':sort},'limit':1})).structuredContent
                    report['calls'].append(safe(sort,value))
                report['checks']={'sorts':all(item.get('status')=='ok' and item.get('total')==144101 for item in report['calls'])}
                report['completed']=all(report['checks'].values());return
            if '--zero' in sys.argv:
                zero=(await session.call_tool('search',{'source':'mathscinet','query':'ti:(zxqvnomatchmathscinetzero)','options':{
                    'facet_filters':{'publication_type':{'include':['Journal Article']}}},'limit':1})).structuredContent
                report['calls'].append(safe('base_zero_with_filter',zero));report['checks']={'zero':zero.get('status')=='not_found' and zero.get('total')==0
                    and zero.get('filter_state',{}).get('status')=='not_applicable' and not zero.get('filter_evidence')}
                report['completed']=all(report['checks'].values());return
            if '--exclude' in sys.argv:
                excluded=(await session.call_tool('search',{'source':'mathscinet','query':QUERY,'options':{'facet_filters':{
                    'review_status':{'exclude':['Pending']}}},'limit':1})).structuredContent
                report['calls'].append(safe('exclude',excluded));report['checks']={'exclude':excluded.get('status')=='ok' and type(excluded.get('total')) is int and 0<excluded['total']<144101
                    and len(excluded.get('filter_evidence') or [])==1 and excluded.get('native_query')=='ti:(algebra) NOT frs:"Pending"'}
                report['completed']=all(report['checks'].values());return
            if '--outside' in sys.argv:
                label=sys.argv[sys.argv.index('--outside')+1]
                outside=(await session.call_tool('search',{'source':'mathscinet','query':QUERY,'options':{'facet_filters':{
                    'journals':{'include':[label]}}},'limit':1})).structuredContent
                report['calls'].append(safe('searched_outside_candidate',outside));native=outside.get('native_query','')
                report['checks']={'outside':outside.get('status')=='ok' and outside.get('received')==1 and len(outside.get('filter_evidence') or [])==1
                    and native.startswith(QUERY+' ji:')}
                report['completed']=all(report['checks'].values());return
            combined=(await session.call_tool('search',{'source':'mathscinet','query':QUERY,'options':{'sort':'citations','facet_filters':{
                'publication_type':{'include':['Journal Article','Book']},'publication_years':{'include':['2025','2026']}}},'limit':2})).structuredContent
            report['calls'].append(safe('sort_same_group_or_different_group_and_preview',combined))
            plain=(await session.call_tool('search',{'source':'mathscinet','query':QUERY,'options':{},'limit':1})).structuredContent
            report['calls'].append(safe('plain_after_filtered',plain))
            excluded={} if '--one' in sys.argv else (await session.call_tool('search',{'source':'mathscinet','query':QUERY,'options':{'facet_filters':{
                'review_status':{'exclude':['Pending']}}},'limit':1})).structuredContent
            if excluded:report['calls'].append(safe('exclude',excluded))
            report['checks']={'combined':combined.get('status') in ('ok','partial') and combined.get('received')==2 and combined.get('sort')=='citations'
                and len(combined.get('filter_evidence') or [])==2,
                'plain_reset':plain.get('status')=='ok' and plain.get('native_query')==QUERY and not plain.get('filter_evidence'),
                'exclude':not excluded or excluded.get('status')=='ok' and len(excluded.get('filter_evidence') or [])==1}
            report['completed']=all(report['checks'].values())
    except Exception as error:report['error_type']=type(error).__name__
    finally:report['finished_at']=now();REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':asyncio.run(main())
