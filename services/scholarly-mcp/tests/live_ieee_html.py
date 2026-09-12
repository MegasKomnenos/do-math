"""Verify IEEE native HTML full text, negative layout, and existing PDF through SDK."""
import argparse,asyncio,json,sys
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1]
async def main(credential_root):
 report={'source':'ieee-xplore','completed':False};path=ROOT/'data/access-research/ieee-html-sdk.json'
 def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 try:
  async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'server.py'),'--credential-root',str(credential_root)])) as (read,write),ClientSession(read,write) as session:
   await session.initialize()
   html=(await session.call_tool('fetch',{'source':'ieee-xplore','target':'10488889','parts':['metadata','fulltext_html']})).structuredContent
   body=html['components']['fulltext_html'];headings=(await session.call_tool('extract',{'ref':body['artifact']['ref'],'selection':'h2,h3,h4','count':100})).structuredContent
   pdf=(await session.call_tool('fetch',{'source':'ieee-xplore','target':'10488889','parts':['fulltext']})).structuredContent
   negative=(await session.call_tool('fetch',{'source':'ieee-xplore','target':'825845','parts':['metadata','fulltext_html']})).structuredContent
   report={'html_status':html['status'],'body_status':body['status'],'body_chars':body['body_text_chars'],'heading_count':body['heading_count'],
           'extracted_headings':headings['returned'],'doi':body['doi'],'title':body['title'],
           'pdf_status':pdf['components']['fulltext']['status'],'pdf_pages':pdf['components']['fulltext']['artifact']['pages'],
           'negative_status':negative['components']['fulltext_html']['status'],'negative_code':negative['components']['fulltext_html'].get('code'),
           'completed':html['status']=='ok' and body['status']=='available' and body['body_text_chars']>40000 and headings['returned']>=12
           and pdf['components']['fulltext']['status']=='available' and negative['components']['fulltext_html']['status']=='not_offered'}
 except Exception as error:
  report.update(error_type=type(error).__name__)
  if 'html' in locals():report['html_call']={'status':html.get('status'),'body':{k:body[k] for k in ('status','code','error_type') if k in body},'body_keys':sorted(body)}
 finally:save();print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--credential-root',type=Path,required=True);args=parser.parse_args();asyncio.run(main(args.credential_root))
