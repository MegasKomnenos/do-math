"""Verify native Vault archives and a revision's directory through stdio."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]
directory='swh:1:dir:01d2169c88d0783182b1b7facffa522ba09b5957'
revision='swh:1:rev:2db189928c94d62a3b4757b3eec68f0a4d4113f0'
async def main():
    report={'source':'software-heritage','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-swh-vault-mcp.json'
    def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        async def call(tool,args):
            data=(await session.call_tool(tool,args)).structuredContent
            report['calls'].append({'tool':tool,'arguments':args,'result':data});save()
            print(json.dumps({'tool':tool,'status':data['status'],'code':data.get('code')}),flush=True)
            return data
        empty=await call('fetch',{'source':'software-heritage','target':'swh:1:dir:4b825dc642cb6eb9a060e54bf8d69288fbee4904','parts':['metadata','fulltext']})
        assert empty['status']=='ok' and empty['components']['fulltext']['integrity']['files']==0
        found=await call('fetch',{'source':'software-heritage','target':directory,'parts':['metadata','fulltext']})
        assert found['status']=='ok'
        component=found['components']['fulltext'];assert component['integrity']['verified'] and component['integrity']['files']==69
        listing=await call('extract',{'ref':component['artifact']['ref'],'count':100})
        names=[item['path'] for item in listing['items'] if item['path'].endswith('/Examples/SimpleFarm/simplefarm.ml')]
        assert len(names)==1 and listing['total']==85
        member=await call('extract',{'ref':component['artifact']['ref'],'selection':names[0]})
        selected=await call('extract',{'ref':member['items'][0]['artifact']['ref'],'count':30})
        assert selected['status']=='ok' and selected['total']==27
        raw=await call('fetch',{'source':'software-heritage','target':'swh:1:cnt:4d99d2d18326621ccdd70f5ea66c2e2ac236ad8b','parts':['fulltext']})
        lines=await call('extract',{'ref':raw['components']['fulltext']['artifact']['ref'],'count':30})
        assert selected['items']==lines['items']
        rev=await call('fetch',{'source':'software-heritage','target':revision,'parts':['metadata','supplementary']})
        assert rev['status']=='ok' and rev['archive_selection']['directory_swhid']==directory
        assert rev['components']['supplementary']['integrity']==component['integrity']
        report['completed']=True;save();print(json.dumps({'completed':True}),flush=True)
asyncio.run(main())
