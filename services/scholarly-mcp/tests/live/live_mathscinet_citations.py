"""One bounded SDK verification of MathSciNet incoming and outgoing relations."""
from __future__ import annotations

import asyncio
from datetime import datetime,timezone
import json
from pathlib import Path
import sys

from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[2]
ROOT=SERVICE.parents[1]
PRIVATE=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260912/mathscinet-citations'
REPORT=SERVICE/'data/access-research/mathscinet-citations/live-sdk.json'

def now():return datetime.now(timezone.utc).isoformat()

def safe_result(label,value):
    row={'label':label,'status':value.get('status'),'code':value.get('code')}
    for key in ('source','kind','target','start','requested','received','total','has_more','native_query'):
        if key in value:row[key]=value[key]
    relation=value.get('relation')
    if isinstance(relation,dict):
        row['relation']={key:relation.get(key) for key in ('direction','basis','scope','total','from_references','from_reviews','control_total','result_total','count_difference','source_reference_items',
            'searchable_mr_occurrences','searchable_unique_mrs','duplicate_mr_occurrences') if key in relation}
        if isinstance(relation.get('source_page'),dict):row['relation']['source_page_ref']=relation['source_page'].get('ref')
    return row

async def extracted(session,result):
    value=(await session.call_tool('extract',{'ref':result['records']['ref'],'count':result['received']})).structuredContent
    return {'status':value.get('status'),'returned':value.get('returned'),
            'ids':['MR'+str(item.get('mrnumber')) for item in value.get('items',[])]}

async def extracted_export(session,result):
    artifact=result.get('export',{})
    value=(await session.call_tool('extract',{'ref':artifact['ref'],'count':result['received']})).structuredContent
    return {'status':value.get('status'),'returned':value.get('returned'),'ref':artifact.get('ref'),
            'media_type':artifact.get('media_type')}

async def main():
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    report={'started_at':now(),'transport':'fresh_sdk_stdio','calls':[],'completed':False}
    def save():REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    save()
    server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(PRIVATE/'sdk-artifacts'),
        '--credential-root',str(PRIVATE/'credentials')])
    try:
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize();report['protocol_initialized']=True
            incoming=(await session.call_tool('search',{'source':'mathscinet','query':'MR2733384','options':{'kind':'citations'},
                'start':1,'limit':2,'export':'bibtex'})).structuredContent
            report['calls'].append(safe_result('incoming_mr_range',incoming))
            if incoming.get('status')!='ok':return
            report['incoming_records']=await extracted(session,incoming)
            report['incoming_export']=await extracted_export(session,incoming)
            outgoing=(await session.call_tool('search',{'source':'mathscinet','query':'MR2733384','options':{'kind':'references'},
                'start':4,'limit':2,'export':'endnote'})).structuredContent
            report['calls'].append(safe_result('outgoing_mr_cross_page',outgoing))
            if outgoing.get('status')!='ok':return
            report['outgoing_records']=await extracted(session,outgoing)
            report['outgoing_export']=await extracted_export(session,outgoing)
            doi_incoming=(await session.call_tool('search',{'source':'mathscinet','query':'10.1016/j.jsc.2010.06.015',
                'options':{'kind':'citations'},'limit':1})).structuredContent
            report['calls'].append(safe_result('incoming_doi_identity',doi_incoming))
            if doi_incoming.get('status')!='ok':return
            report['doi_records']=await extracted(session,doi_incoming)
            reviews=(await session.call_tool('search',{'source':'mathscinet','query':'MR0463157',
                'options':{'kind':'citations','citation_basis':'reviews'},'limit':1,'export':'bibtex'})).structuredContent
            report['calls'].append(safe_result('incoming_from_reviews',reviews))
            if reviews.get('status')!='ok':return
            report['review_records']=await extracted(session,reviews)
            report['review_export']=await extracted_export(session,reviews)
            report['checks']={
                'incoming_control':incoming.get('total')==3 and incoming.get('relation',{}).get('from_reviews')==0,
                'incoming_range':incoming.get('start')==1 and incoming.get('received')==2,
                'incoming_native_export':report['incoming_export'].get('status')=='ok' and report['incoming_export'].get('returned')==2,
                'outgoing_subset':outgoing.get('total')==42 and outgoing.get('relation',{}).get('source_reference_items')==48
                    and outgoing.get('relation',{}).get('searchable_mr_occurrences')==44
                    and outgoing.get('relation',{}).get('duplicate_mr_occurrences')==2,
                'outgoing_cross_page':outgoing.get('start')==4 and outgoing.get('received')==2,
                'outgoing_native_export':report['outgoing_export'].get('status')=='ok' and report['outgoing_export'].get('returned')==2,
                'doi_identity':doi_incoming.get('target')=='MR2733384' and bool(doi_incoming.get('lookup')),
                'review_basis':reviews.get('target')=='MR0463157' and reviews.get('total')==72
                    and reviews.get('relation',{}).get('basis')=='From Reviews'
                    and reviews.get('relation',{}).get('from_references')==7912
                    and reviews.get('relation',{}).get('control_total')==76
                    and reviews.get('relation',{}).get('result_total')==72,
                'review_native_export':report['review_export'].get('status')=='ok' and report['review_export'].get('returned')==1,
            }
            report['completed']=all(report['checks'].values())
    except Exception as error:
        report['error_type']=type(error).__name__
    finally:
        report['finished_at']=now();save()
    print(json.dumps({'completed':report['completed'],'calls':report['calls'],'error_type':report.get('error_type')},ensure_ascii=False))

if __name__=='__main__':asyncio.run(main())
