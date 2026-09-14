"""Fresh stdio verification for ACM's native Edit Query Boolean syntax."""
from pathlib import Path
from datetime import datetime,timezone
import asyncio,json,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

SERVICE=Path(__file__).resolve().parents[2];ROOT=SERVICE.parents[1]
PRIVATE=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260912/acm-boolean-recheck/sdk'
CREDENTIALS=ROOT/'.credentials/scholarly-mcp/probes/access-research-20260912/acm-advanced-agent/edit-search/credentials'
REPORT=SERVICE/'data/access-research/acm-boolean-recheck/live-sdk.json'

def now():return datetime.now(timezone.utc).isoformat()
def safe(label,value):
    return {key:item for key,item in {
        'label':label,'status':value.get('status'),'code':value.get('code'),'source':value.get('source'),
        'received':value.get('received'),'total':value.get('total'),'native_expression':value.get('native_expression'),
        'native_constraint':value.get('native_constraint'),'facet':value.get('facet'),
    }.items() if item is not None}

async def main():
    REPORT.parent.mkdir(parents=True,exist_ok=True);PRIVATE.mkdir(parents=True,exist_ok=True)
    report={'started_at':now(),'transport':'fresh_sdk_stdio','calls':[],'completed':False}
    def save():REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    save();server=StdioServerParameters(command=sys.executable,args=[str(SERVICE/'server.py'),'--data-dir',str(PRIVATE/'artifacts'),
        '--credential-root',str(CREDENTIALS)])
    try:
        async with stdio_client(server) as (read,write),ClientSession(read,write) as session:
            await session.initialize();report['protocol_initialized']=True
            expression='(Title:(algebra) OR Abstract:(complexity))'
            basic=(await session.call_tool('search',{'source':'acm-dl','query':'','options':{'expression':expression},
                'limit':1,'export':'bibtex'})).structuredContent
            report['calls'].append(safe('cross_field_or',basic));save()
            combined_expression='Title:(algebra OR complexity)'
            combined=(await session.call_tool('search',{'source':'acm-dl','query':'','options':{
                'expression':combined_expression,'from_year':2024,'to_year':2026,'sort':'cited',
                'constraint':{'field':'SeriesKey','operator':'Or','values':['Journal of the ACM','Communications of the ACM']},
                'facet':{'field':'ContentItemType','value':'research-article'}},'limit':1,'export':'bibtex'})).structuredContent
            report['calls'].append(safe('expression_with_existing_controls',combined));save()
            report['checks']={
                'cross_field_or':basic.get('status') in ('ok','partial') and basic.get('received')==1
                    and basic.get('total')==95534 and basic.get('native_expression')==expression,
                'combined':combined.get('status') in ('ok','partial') and combined.get('received')==1
                    and combined.get('native_expression')==combined_expression
                    and combined.get('native_constraint',{}).get('native_key')=='SeriesKeyOr'
                    and combined.get('facet',{}).get('value')=='research-article',
            }
            report['completed']=all(report['checks'].values());save()
    except Exception as error:
        report['error_type']=type(error).__name__;report['error_code']=getattr(error,'result',{}).get('code')
    finally:
        report['finished_at']=now();save()
    print(json.dumps({'completed':report['completed'],'calls':report['calls'],'checks':report.get('checks'),
        'error_type':report.get('error_type'),'error_code':report.get('error_code')},ensure_ascii=False))

if __name__=='__main__':asyncio.run(main())
