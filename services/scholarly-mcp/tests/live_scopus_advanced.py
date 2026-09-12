"""Fresh stdio checks for Scopus native result sorts and exact-label facets."""
from pathlib import Path
from datetime import datetime,timezone
import asyncio,json,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
SERVICE=Path(__file__).resolve().parents[1];ROOT=SERVICE.parents[1]
CREDENTIALS=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260913/limitations-audit-scopus/credentials'
PRIVATE=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260913/limitations-audit-scopus/sdk'
REPORT=SERVICE/'data/access-research/limitations-audit/institutional-scopus-sdk.json';QUERY='TITLE("P versus NP")'
def now():return datetime.now(timezone.utc).isoformat()
def safe(label,value):return {key:item for key,item in {'label':label,'status':value.get('status'),'code':value.get('code'),
    'total':value.get('total'),'received':value.get('received'),'sort':value.get('sort'),'facet_groups':value.get('facet_groups'),
    'filter_evidence_count':len(value.get('filter_evidence') or []),'sort_evidence':bool(value.get('sort_evidence')),
    'facet_candidates':value.get('facet_candidates'),'export':{key:value.get('export',{}).get(key) for key in ('bytes','media_type','role','facet_groups','candidate_rows','table_header_row')}
        if isinstance(value.get('export'),dict) else None,'export_error':value.get('export_error')}.items() if item is not None}
async def main():
    PRIVATE.mkdir(parents=True,exist_ok=True);report={'source':'scopus','started_at':now(),'calls':[],'completed':False}
    server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(PRIVATE/'artifacts'),'--credential-root',str(CREDENTIALS)])
    try:
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize()
            if '--stale' in sys.argv:
                filtered=(await session.call_tool('search',{'source':'scopus','query':QUERY,'options':{'sort':'cited-highest','facet_filters':{
                    'document_type':{'include':['Article','Review']},'language':{'include':['English']}}},'limit':1})).structuredContent
                plain=(await session.call_tool('search',{'source':'scopus','query':QUERY,'options':{},'limit':1})).structuredContent
                report['calls']+=[safe('filtered',filtered),safe('plain_after_filtered',plain)]
                report['checks']={'filtered':filtered.get('status')=='ok' and filtered.get('total')==16,
                    'plain':plain.get('status')=='ok' and plain.get('total')==21 and not plain.get('filter_evidence') and plain.get('sort') is None}
                report['completed']=all(report['checks'].values());return
            if '--year' in sys.argv:
                value=(await session.call_tool('search',{'source':'scopus','query':QUERY,'options':{'facet_filters':{'year':{'include':['2025']}}},'limit':1})).structuredContent
                report['calls'].append(safe('year',value));report['checks']={'year':value.get('status')=='ok' and value.get('total')==1 and len(value.get('filter_evidence') or [])==1}
                report['completed']=all(report['checks'].values());return
            if '--export-counts' in sys.argv:
                value=(await session.call_tool('search',{'source':'scopus','query':QUERY,'options':{},'limit':1,'export':'facet-counts'})).structuredContent
                report['calls'].append(safe('native_filter_counts',value));export=value.get('export',{})
                extracted=(await session.call_tool('extract',{'ref':export['ref'],'count':1000})).structuredContent if export.get('ref') else {}
                report['extract']={key:extracted.get(key) for key in ('status','total','returned')}
                report['checks']={'export':value.get('status')=='ok' and export.get('media_type')=='text/csv' and export.get('bytes',0)>1000
                    and export.get('candidate_rows',0)>0 and 'FUNDING SPONSOR' in export.get('facet_groups',[]),
                    'extract':extracted.get('status')=='ok' and extracted.get('returned')==extracted.get('total') and extracted.get('total',0)>100}
                report['completed']=all(report['checks'].values());return
            if '--export-filtered' in sys.argv:
                value=(await session.call_tool('search',{'source':'scopus','query':QUERY,'options':{'facet_filters':{
                    'document_type':{'include':['Article']}}},'limit':1,'export':'facet-counts'})).structuredContent
                report['calls'].append(safe('filtered_native_filter_counts',value));error=value.get('export_error',{})
                report['checks']={'filtered_partial':value.get('status')=='partial' and value.get('total')==14 and value.get('received')==1
                    and error.get('code')=='invalid_native_export' and bool(value.get('records'))}
                report['completed']=all(report['checks'].values());return
            if '--subject' in sys.argv:
                preview=(await session.call_tool('search',{'source':'scopus','query':QUERY,'options':{'facet_group':'subject_area'},'limit':1})).structuredContent
                report['calls'].append(safe('expanded_subject_candidates',preview));report['checks']={'preview':preview.get('status')=='ok' and preview.get('facet_candidates',{}).get('bytes',0)>2}
                report['completed']=all(report['checks'].values());return
            if '--source-wide' in sys.argv:
                preview=(await session.call_tool('search',{'source':'scopus','query':'TITLE(complexity)','options':{'facet_group':'source_title'},'limit':1})).structuredContent
                report['calls'].append(safe('expanded_source_title_candidates',preview));report['checks']={'preview':preview.get('status')=='ok' and preview.get('facet_candidates',{}).get('bytes',0)>2}
                report['completed']=all(report['checks'].values());return
            combined=(await session.call_tool('search',{'source':'scopus','query':QUERY,'options':{'sort':'cited-highest','facet_filters':{
                'document_type':{'include':['Article','Review']},'language':{'include':['English']}}},'limit':2})).structuredContent
            report['calls'].append(safe('same_group_or_different_group_and_sort',combined))
            excluded=(await session.call_tool('search',{'source':'scopus','query':QUERY,'options':{'facet_filters':{
                'document_type':{'exclude':['Book chapter']}}},'limit':1})).structuredContent
            report['calls'].append(safe('exclude',excluded))
            preview=(await session.call_tool('search',{'source':'scopus','query':QUERY,'options':{'facet_group':'source_title'},'limit':1})).structuredContent
            report['calls'].append(safe('candidate_preview',preview))
            report['checks']={'combined':combined.get('status')=='ok' and combined.get('received')==2 and combined.get('sort')=='cited-highest'
                and len(combined.get('filter_evidence') or [])==2,
                'exclude':excluded.get('status')=='ok' and excluded.get('total')==20,
                'preview':preview.get('status')=='ok' and preview.get('facet_candidates',{}).get('bytes',0)>2}
            report['completed']=all(report['checks'].values())
    except Exception as error:report['error_type']=type(error).__name__
    finally:report['finished_at']=now();REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':asyncio.run(main())
