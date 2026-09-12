"""Download the selected image and distinguish native restricted permissions."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]
async def main():
    report={'source':'jstor','calls':[],'completed':False};path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-jstor-image-mcp.json'
    def save():path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        for target,expected in [('community.13581670','available'),('community.39607963','restricted')]:
            found=(await session.call_tool('fetch',{'source':'jstor','target':target,'parts':['metadata','fulltext']})).structuredContent
            report['calls'].append(found);save();component=found.get('components',{}).get('fulltext',found)
            print(json.dumps({'target':target,'status':component['status'],'code':component.get('code'),'stage':component.get('stage')}),flush=True)
            if component['status']!=expected:return
            if expected=='available':
                assert component['artifact']['media_type']=='image/jpeg'
                extracted=await session.call_tool('extract',{'ref':component['artifact']['ref']})
                report['calls'].append({'tool':'extract','structured':extracted.structuredContent,'image_blocks':sum(x.type=='image' for x in extracted.content)});save()
                assert any(x.type=='image' for x in extracted.content)
        report['completed']=True;save();print(json.dumps({'completed':True}),flush=True)
asyncio.run(main())
