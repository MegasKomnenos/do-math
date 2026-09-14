"""Verify WOS sort, current facets and edition selection through stdio."""
import argparse,asyncio,json,sys
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

root=Path(__file__).resolve().parents[2]


async def main(credential_root=None):
    report={'source':'wos','scope':'sort-facets-editions','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-wos-advanced-mcp.json'
    def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    args=[str(root/'server.py')]
    if credential_root:args+=['--credential-root',str(credential_root),'--data-dir',str(credential_root.parent/'data')]
    save();print(json.dumps({'report':str(path)}),flush=True)
    try:
        async with stdio_client(StdioServerParameters(command=sys.executable,args=args)) as (read,write),ClientSession(read,write) as session:
            await session.initialize()
            async def call(tool,args):
                result=(await session.call_tool(tool,args)).structuredContent
                report['calls'].append({'tool':tool,'arguments':args,'result':result});save()
                print(json.dumps({'tool':tool,'status':result['status'],'code':result.get('code'),'received':result.get('received'),'total':result.get('total')}),flush=True)
                return result
            cpc=await call('search',{'source':'wos','query':'TI=("P versus NP")','options':{'editions':['CPCI-S'],'sort':'date-newest'},'limit':2,'export':'plain'})
            if cpc['status']!='ok':return
            assert cpc['total']==cpc['received']==1 and cpc['editions']==['CPCI-S'] and cpc['sort']=='date-newest'
            cpc_rows=await call('extract',{'ref':cpc['records']['ref'],'count':2})
            assert cpc_rows['returned']==1 and cpc_rows['items'][0]['fields']['we']==['Conference Proceedings Citation Index - Science (CPCI-S)']
            filtered=await call('search',{'source':'wos','query':'TI=("P versus NP")',
                'options':{'facets':['OA.OPEN ACCESS','DT.ARTICLE'],'sort':'citations-highest'},'limit':2,'export':'plain'})
            if filtered['status']!='ok':return
            assert filtered['total']==filtered['received']==2 and filtered['sort']=='citations-highest'
            rows=await call('extract',{'ref':filtered['records']['ref'],'count':2});native=await call('extract',{'ref':filtered['export']['ref'],'count':2})
            assert rows['returned']==native['returned']==2
            counts=[int(row['fields']['tc'][0]) for row in rows['items']]
            assert counts==sorted(counts,reverse=True)
            boundary=await call('search',{'source':'wos','query':'TI=("P versus NP")',
                'options':{'facets':['OA.OPEN ACCESS','DT.ARTICLE'],'sort':'citations-highest'},'start':1,'limit':2})
            assert boundary['status']=='ok' and boundary['total']==2 and boundary['received']==1 and not boundary['has_more']
            expanded=await call('search',{'source':'wos','query':'TI=("P versus NP")','options':{'facet_filters':{'publication_years':['2013']}},'limit':2})
            if expanded['status']!='ok':return
            expanded_rows=await call('extract',{'ref':expanded['records']['ref'],'count':2})
            assert expanded['total']==expanded['received']==1 and expanded_rows['items'][0]['fields']['py']==['2013']
            preview=await call('search',{'source':'wos','query':'TI=("P versus NP")',
                'options':{'facet_group':'publication_titles','facet_query':'Computational'},'limit':1})
            candidates=await call('extract',{'ref':preview['facet_candidates'][0]['ref'],'count':10})
            assert any(item['field']=='publication_titles' and item['label']=='COMPUTATIONAL COMPLEXITY' for item in candidates['items'])
            friendly=await call('search',{'source':'wos','query':'TI=("P versus NP")',
                'options':{'facet_filters':{'publication_titles':['COMPUTATIONAL COMPLEXITY'],'languages':['English']}},'limit':2,'export':'plain'})
            if friendly['status']!='ok':return
            friendly_rows=await call('extract',{'ref':friendly['records']['ref'],'count':2})
            assert friendly['total']==friendly['received']==1 and friendly_rows['items'][0]['fields']['so']==['COMPUTATIONAL COMPLEXITY'] and friendly_rows['items'][0]['fields']['la']==['English']
            assert next(item for item in friendly['facets'] if item['value']=='DT.ARTICLE')['count']==1
            same_group=await call('search',{'source':'wos','query':'TI=("P versus NP")',
                'options':{'facet_filters':{'wos_categories':['Computer Science Theory Methods','Mathematics']}},'limit':2})
            assert same_group['status']=='ok' and same_group['total']==9 and same_group['received']==2
            fetched=await call('fetch',{'source':'wos','target':'10.1145/1562164.1562186','parts':['metadata']})
            if fetched['status']!='ok':return
            fetched_rows=await call('extract',{'ref':fetched['records']['ref'],'count':1})
            assert fetched_rows['items'][0]['id']=='WOS:000269418800023' and fetched_rows['items'][0]['fields']['di']==['10.1145/1562164.1562186']
            report['completed']=True
    finally:
        report['finished']=datetime.now(timezone.utc).isoformat();save();print(json.dumps({'completed':report['completed']}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--credential-root',type=Path);args=parser.parse_args();asyncio.run(main(args.credential_root))
