"""Disprove observed UI counts that were encoded as client input or page ceilings."""
import argparse,asyncio,json,sys
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[2]
async def main(credential_root,data_dir):
 report={'completed':False,'calls':[]};path=ROOT/'data/access-research/range-cap-audit-live.json'
 try:
  async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'server.py'),'--credential-root',str(credential_root),'--data-dir',str(data_dir)])) as (read,write),ClientSession(read,write) as session:
   await session.initialize()
   async def call(source,query,options,start=0,limit=1):
    result=(await session.call_tool('search',{'source':source,'query':query,'options':options,'start':start,'limit':limit})).structuredContent
    report['calls'].append({'source':source,'status':result['status'],'code':result.get('code'),'total':result.get('total'),'received':result.get('received'),'start':start});print(json.dumps(report['calls'][-1]),flush=True);return result
   terms=[{'field':'TITLE','query':'complexity','operator':'OR'} for _ in range(20)]
   euclid=await call('project-euclid','complexity',{'terms':terms},0,1)
   if euclid['status']=='ok':
    expression=euclid['native_query']['term'][0]
    report['calls'][-1]['preserved_terms']=expression.count('complexity')
    report['calls'][-1]['native_field_terms']=expression.count('TITLE:')
    report['calls'][-1]['identity_ok']=euclid['preview'][0]['id']=='10.11650/tjm.18.2014.3904'
   nonsense=[{'field':'ALL','query':f'zxqvsdkboundary{i:02d}alpha','operator':'OR'} for i in range(1,20)]
   semantic=await call('project-euclid','zxqvsdkboundary00alpha',{'terms':nonsense+[{'field':'TITLE','query':'complexity','operator':'OR'}]},0,1)
   if semantic['status']=='ok':
    semantic_expression=semantic['native_query']['term'][0]
    report['calls'][-1]['preserved_terms']=sum(value in semantic_expression for value in ['zxqvsdkboundary00alpha',*[x['query'] for x in nonsense],'complexity'])
    report['calls'][-1]['last_title_preserved']='TITLE:(complexity)' in semantic_expression
   ranged=await call('project-euclid','zxqvsdkboundary00alpha',{'terms':nonsense+[{'field':'TITLE','query':'complexity','operator':'OR'}],
                     'year_from':2020,'year_to':2025,'sort':'PubDateDesc','page_size':25},24,2)
   if ranged['status']=='ok':
    native=ranged['native_query'];report['calls'][-1]['native_conditions_ok']=(native.get('startYear')==['2020'] and native.get('endYear')==['2025'] and native.get('sortBy')==['PubDateDesc'] and native.get('pageSize')==['25'])
    report['calls'][-1]['range_ok']=ranged['start']==24 and ranged['received']==2
   report['completed']=(euclid['status']=='ok' and report['calls'][-3].get('preserved_terms')==21 and report['calls'][-3].get('native_field_terms')==20 and report['calls'][-3].get('identity_ok')
                        and semantic['status']=='ok' and semantic['total']>0 and report['calls'][-2].get('preserved_terms')==21 and report['calls'][-2].get('last_title_preserved')
                        and ranged['status']=='ok' and report['calls'][-1].get('native_conditions_ok') and report['calls'][-1].get('range_ok'))
 finally:path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'completed':report['completed']}),flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--credential-root',type=Path,required=True)
 parser.add_argument('--data-dir',type=Path,required=True);args=parser.parse_args()
 asyncio.run(main(args.credential_root,args.data_dir))
