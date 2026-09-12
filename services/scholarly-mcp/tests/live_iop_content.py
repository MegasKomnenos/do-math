"""Verify IOP native HTML, TeX, figures and supplementary PDF through stdio."""
import asyncio,json,sys
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
root=Path(__file__).resolve().parents[1]
private=root.parents[1]/'.credentials/scholarly-mcp/probes/access-research-20260913/iop-equation-live'

async def main():
    report={'source':'iop','calls':[],'completed':False}
    path=root/'data/validation'/f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-iop-content-mcp.json'
    def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    save();print(json.dumps({'report':str(path)}),flush=True)
    private.mkdir(parents=True,exist_ok=True)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(root/'server.py'),'--data-dir',str(private/'data'),'--credential-root',str(private/'credentials')])) as (read,write),ClientSession(read,write) as session:
        await session.initialize()
        async def call(tool,args):
            response=await session.call_tool(tool,args);result=response.structuredContent
            report['calls'].append({'tool':tool,'arguments':args,'result':result});save()
            print(json.dumps({'tool':tool,'status':result['status'],'code':result.get('code')}),flush=True)
            return response
        result=(await call('fetch',{'source':'iop','target':'https://iopscience.iop.org/article/10.1088/1367-2630/add557','parts':['metadata','fulltext_html','supplementary']})).structuredContent
        if result['status']!='ok':return
        html=result['components']['fulltext_html'];supp=result['components']['supplementary']
        assert len(html['figures'])==5 and supp['discovered']==supp['received']==1
        math=html['math_images'];assert math['status']=='available' and math['requested']==math['received']==154
        first_math=(await call('extract',{'ref':math['manifest']['ref'],'start':0,'count':1})).structuredContent
        last_math=(await call('extract',{'ref':math['manifest']['ref'],'start':153,'count':1})).structuredContent
        assert first_math['items'][0]['number']==1 and last_math['items'][0]['number']==154
        assert first_math['items'][0]['status']==last_math['items'][0]['status']=='available'
        tex=(await call('extract',{'ref':html['artifact']['ref'],'selection':'script[type^="math/tex"]','count':2})).structuredContent
        assert tex['status']=='ok' and tex['returned']==2 and '\\textbf{s}' in json.dumps(tex)
        image=await call('extract',{'ref':html['figures'][0]['artifact']['ref']})
        assert sum(block.type=='image' for block in image.content)==1
        equation=await call('extract',{'ref':math['artifact']['ref']})
        assert equation.structuredContent['media_type']=='image/gif' and sum(block.type=='image' for block in equation.content)==1
        file=supp['files'][0]
        assert file['filename']=='njpadd557supp1.pdf' and file['artifact']['media_type']=='application/pdf'
        pdf=(await call('extract',{'ref':file['artifact']['ref'],'count':1})).structuredContent
        assert pdf['status']=='ok' and pdf['returned']==1 and pdf['total']>0
        assert 'Mastering data complexity beyond traditional computation: Supplements' in pdf['items'][0]['text']
        report.update(completed=True,figures=5,equation_images=154,equation_image_blocks=1,pdf_pages=pdf['total']);save()
        print(json.dumps({'completed':True,'figures':5,'equation_images':154,'equation_image_blocks':1,'pdf_pages':pdf['total']}),flush=True)

asyncio.run(main())
