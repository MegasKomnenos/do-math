"""Verify explicit Nature HTML, source TeX and native figure ImageContent."""
import asyncio,json,sys
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[2]

async def main():
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-nature-html-mcp.json'
    report={'source':'springer','calls':[],'completed':False}
    def preserve():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    preserve();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        result=(await session.call_tool('fetch',{'source':'springer','target':'https://www.nature.com/articles/s41467-023-41217-6','parts':['metadata','fulltext_html']})).structuredContent
        report['calls'].append(result);preserve()
        body=result.get('components',{}).get('fulltext_html',{})
        print(json.dumps({'status':result['status'],'code':result.get('code'),'html_status':body.get('status'),'figures':len(body.get('figures',[]))}),flush=True)
        assert result['status']=='ok' and body['status']=='available'
        tex=(await session.call_tool('extract',{'ref':body['artifact']['ref'],'selection':'.main-content .mathjax-tex','count':2})).structuredContent
        report['calls'].append(tex);preserve()
        assert tex['status']=='ok' and tex['returned']==2 and 'NISQ' in json.dumps(tex)
        assert len(body['figures'])==1
        picture=await session.call_tool('extract',{'ref':body['figures'][0]['artifact']['ref']})
        report['calls'].append(picture.structuredContent)
        report['image_blocks']=sum(x.type=='image' for x in picture.content);preserve()
        assert report['image_blocks']==1 and picture.structuredContent['status']=='ok'
        report['completed']=True;preserve();print(json.dumps({'completed':True,'image_blocks':report['image_blocks']}),flush=True)

asyncio.run(main())
