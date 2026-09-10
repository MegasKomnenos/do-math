"""Read observed publisher attachments through the actual stdio tools."""
import asyncio,json,sys,argparse
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]
targets={
 'cambridge':'https://www.cambridge.org/core/journals/psychometrika/article/abs/exponentialfamily-random-graph-models-for-multilayer-networks/2BE58EAFDEB0C29909BE36E08FD83CE4',
 'oxford':'https://academic.oup.com/restud/advance-article/doi/10.1093/restud/rdag022/8528932',
 'taylor-francis':'https://www.tandfonline.com/doi/abs/10.1080/10618600.2017.1349663',
 'de-gruyter':'https://www.degruyterbrill.com/document/doi/10.1524/zkri.2013.1610/html'}
async def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--source',choices=list(targets),required=True); args=parser.parse_args()
    report={'source':args.source,'calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{args.source}-supplements-mcp.json'
    def preserve(): path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        parts=['metadata','supplementary']+(['abstract','export'] if args.source=='taylor-francis' else [])
        found=(await session.call_tool('fetch',{'source':args.source,'target':targets[args.source],'parts':parts})).structuredContent
        report['calls'].append(found); preserve()
        print(json.dumps({'status':found['status'],'code':found.get('code'),'report':str(path)}),flush=True)
        assert found['status']=='ok',found.get('code')
        files=found['components']['supplementary']['files']
        assert len(files)=={'cambridge':2,'oxford':1,'taylor-francis':3,'de-gruyter':1}[args.source]
        for file in files:
            extracted=(await session.call_tool('extract',{'ref':file['artifact']['ref'],'count':1})).structuredContent
            report['calls'].append(extracted); preserve()
            print(json.dumps({'filename':file['filename'],'media':file['artifact']['media_type'],'total':extracted.get('total')}),flush=True)
            assert extracted['status']=='ok' and extracted['returned']==1
            if file['artifact']['media_type']=='text/csv':
                assert extracted['total']==3 and len(extracted['items'][0])==4
        if args.source=='taylor-francis':
            assert found['components']['export']['status']=='available'
            assert found['components']['abstract']['status']=='available'
            assert files[0]['artifact']['doi']=='10.1080/10618600.2017.1349663'
        report['completed']=True; preserve()
        print(json.dumps({'completed':True}),flush=True)
asyncio.run(main())
