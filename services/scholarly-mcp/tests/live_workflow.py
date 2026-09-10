"""Run the same source-guide → search → export → extract → fetch flow as a caller."""
import argparse
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="mathscinet")
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    report = {"started_at": now.isoformat(), "source": args.source, "transport": "stdio", "calls": [], "completed": False}
    path = ROOT / "data" / "validation" / (now.strftime("%Y%m%dT%H%M%S%fZ-") + args.source + "-workflow.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    def preserve():
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    preserve()
    print(json.dumps({"report": str(path)}), flush=True)
    params = StdioServerParameters(command=sys.executable, args=[str(ROOT / "server.py")])
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        async def call(name, arguments):
            result = await session.call_tool(name, arguments)
            data = result.structuredContent
            if not isinstance(data, dict):
                raise AssertionError("Missing structured result")
            report["calls"].append({"tool": name, "arguments": arguments, "result": data})
            preserve()
            print(json.dumps({"tool": name, "source": args.source, "status": data.get("status"), "code": data.get("code"), "received": data.get("received"), "total": data.get("total")}), flush=True)
            return data
        await call("describe_source", {"source": args.source})
        if args.source == "mathscinet":
            search = await call("search", {"source": args.source, "query": 'ti:("P versus NP")', "limit": 5, "export": "bibtex"})
            assert search["status"] == "ok", search.get("code")
            extracted = await call("extract", {"ref": search["records"]["ref"], "fields": ["mrnumber", "titles"], "count": 5})
            assert extracted["returned"] == 5
            fetched = await call("fetch", {"source": args.source, "target": "MR2733384", "parts": ["metadata", "supplementary", "export"]})
            assert fetched["status"] == "ok", fetched.get("code")
            pdf = fetched["components"]["supplementary"]["artifact"]
            page = await call("extract", {"ref": pdf["ref"], "count": 1})
            assert "2733384" in page["items"][0]["text"]
            assert {x['format'] for x in fetched['components']['export']['artifacts']}=={'bibtex','endnote','amsref','tex'}
            for item in fetched['components']['export']['artifacts']:
                exported=await call('extract',{'ref':item['artifact']['ref'],'count':1})
                assert exported['status']=='ok' and exported['returned']==1
            exact=await call('search',{'source':'mathscinet','query':'mr:(2733384)','limit':2,'export':'bibtex'})
            assert exact['status']=='ok' and exact['received']==1
            named=await call('fetch',{'source':'mathscinet','target':'P versus NP','parts':['metadata']})
            assert named['status']=='selection_required'
            identified=await call('fetch',{'source':'mathscinet','target':'10.1006/jcss.1997.1494','parts':['metadata','export']})
            assert identified['status']=='ok' and identified['target']=='MR1473047'
        elif args.source == "wos":
            search = await call("search", {"source": "wos", "query": 'TI=("P versus NP")', "limit": 5, "export": "plain"})
            assert search["status"] == "ok", search.get("code")
            records = await call("extract", {"ref": search["records"]["ref"], "count": 5})
            assert records["returned"] == 5
            assert len(records["items"][0]["fields"]["cr"]) == 47
            candidates = await call('fetch', {'source': 'wos', 'target': 'The status of the P versus NP problem', 'parts': ['metadata']})
            assert candidates['status'] == 'selection_required'
            chosen = await call('extract', {'ref': candidates['records']['ref'], 'count': 1})
            identifier = chosen['items'][0]['id']
            linked = await call('fetch', {'source': 'wos', 'target': 'https://www.webofscience.com/wos/woscc/full-record/' + identifier, 'parts': ['metadata', 'abstract', 'supplementary']})
            assert linked['components']['metadata']['status'] == 'available'
            assert linked['components']['supplementary']['status'] == 'available'
            assert linked['components']['abstract']['status'] in ('available', 'not_found')
            excel = await call('search', {'source':'wos','query':'UT=('+identifier+')','limit':1,'export':'excel'})
            assert excel['status']=='ok'
            sheet = await call('extract', {'ref':excel['export']['ref'],'count':2})
            assert sheet['status']=='ok' and sheet['returned']==2
        elif args.source == "eccc":
            named=await call('fetch',{'source':'eccc','target':'natural proofs','parts':['metadata']})
            assert named['status']=='selection_required' and named['received']>0
            search = await call("search", {"source": "eccc", "query": "natural proofs", "limit": 2})
            assert search["status"] == "ok", search.get("code")
            records = await call("extract", {"ref": search["records"]["ref"], "count": 2})
            assert records["returned"] == 2
            fetched = await call("fetch", {"source": "eccc", "target": "TR26-008r1", "parts": ["metadata", "abstract", "fulltext"]})
            assert fetched["status"] == "ok", fetched.get("code")
            assert fetched["revision"] == 1
        elif args.source == "acm-dl":
            search = await call("search", {"source": "acm-dl", "query": '"The complexity of theorem-proving procedures"', "options": {"field": "Title", "collection": "fulltext"}, "limit": 2, "export": "bibtex"})
            assert search["status"] == "ok", search.get("code")
            records = await call("extract", {"ref": search["records"]["ref"], "fields": ["id", "title", "year"], "count": 2})
            assert {r["year"] for r in records["items"]} == {"1971", "2023"}
            fetched = await call("fetch", {"source": "acm-dl", "target": "10.1145/800157.805047", "parts": ["metadata", "abstract", "fulltext"]})
            assert fetched["status"] == "ok", fetched.get("code")
            assert fetched["components"]["fulltext"]["artifact"]["pages"] == 8
        elif args.source == 'openalex':
            wide=await call('search',{'source':'openalex','query':'"natural proofs"','limit':4,'options':{'select':'id,title'}})
            assert wide['status']=='ok'
            rows=await call('extract',{'ref':wide['records']['ref'],'count':4})
            small=await call('search',{'source':'openalex','query':'"natural proofs"','start':1,'limit':2,'options':{'select':'id,title'}})
            portion=await call('extract',{'ref':small['records']['ref'],'count':2})
            assert portion['items']==rows['items'][1:3]
            groups=await call('search',{'source':'openalex','query':'natural proofs','options':{'group_by':'publication_year'},'limit':2})
            assert groups['status']=='ok' and groups['records_kind']=='groups' and groups['total'] is None
            following=await call('search',{'source':'openalex','query':'natural proofs','options':{'group_by':'publication_year'},'limit':2,**groups['next']})
            assert following['status']=='ok'
            one=await call('fetch',{'source':'openalex','target':'https://openalex.org/works/W2741809807','parts':['metadata','abstract','supplementary']})
            assert one['status']=='ok'
            abstract=await call('extract',{'ref':one['components']['abstract']['artifact']['ref'],'count':1})
            assert abstract['unit']=='lines' and len(abstract['items'][0])>500
            relations=await call('extract',{'ref':one['components']['supplementary']['artifact']['ref'],'count':1})
            assert len(relations['items'][0]['referenced_works'])==one['components']['supplementary']['reference_count']
            named=await call('fetch',{'source':'openalex','target':'The state of OA: a large-scale analysis of the prevalence and impact of Open Access articles','parts':['metadata']})
            assert named['status']=='selection_required'
            empty=await call('fetch',{'source':'openalex','target':'10.1006/jcss.1997.1494','parts':['metadata','abstract','supplementary']})
            assert empty['components']['abstract']['status']=='not_found'
            assert empty['components']['supplementary']['reference_count']==36
        elif args.source == 'figshare':
            found=await call('search',{'source':'figshare','query':'quantum','limit':3,'export':'native'})
            assert found['status']=='ok' and found['received']==3 and found['total'] is None
            first=await call('extract',{'ref':found['records']['ref'],'count':3,'fields':['id']})
            window=await call('search',{'source':'figshare','query':'quantum','start':1,'limit':2})
            second=await call('extract',{'ref':window['records']['ref'],'count':2,'fields':['id']})
            assert second['items']==first['items'][1:]
            collection=await call('fetch',{'source':'figshare','target':'10.60893/figshare.aip.c.7956296','parts':['metadata','supplementary']})
            assert collection['status']=='ok'
            members=await call('extract',{'ref':collection['components']['supplementary']['artifact']['ref'],'count':2})
            assert members['returned']==1
            item=await call('fetch',{'source':'figshare','target':members['items'][0]['doi'],'parts':['metadata','supplementary']})
            assert item['status']=='ok' and item['version']==1
            file=item['components']['supplementary']['files'][0]['artifact']
            assert file['checksum_verified'] and file['provider_md5']=='bdfa565f42075d264cf31684d21d7635'
            extracted=await call('extract',{'ref':file['ref'],'count':1})
            assert extracted['status']=='ok' and extracted['returned']==1
        elif args.source == 'general-web':
            found=await call('search',{'source':'general-web','query':'natural proofs','limit':2,'export':'csv'})
            assert found['status']=='ok' and found['received']==2
            assert found['total'] is None
            rows=await call('extract',{'ref':found['records']['ref'],'count':2})
            assert any('natural' in x['title'].lower() for x in rows['items'])
            empty=await call('search',{'source':'general-web','query':'qzjxwv947231','limit':2})
            assert empty['status']=='not_found' and empty['returned_set_size']==0
        elif args.source == 'siam':
            found=await call('fetch',{'source':args.source,'target':'https://epubs.siam.org/doi/pdf/10.1137/1.9781611974997.fm','parts':['metadata','fulltext','export']})
            assert found['status']=='ok'
            assert found['components']['metadata']['kind']=='embedded_pdf_metadata'
            pages=await call('extract',{'ref':found['components']['fulltext']['artifact']['ref'],'count':1})
            assert pages['total']==10 and 'First-Order' in pages['items'][0]['text']
        elif args.source == 'ams':
            found=await call('search',{'source':args.source,'query':'algebra','start':11,'limit':2,'export':'csv'})
            assert found['status']=='ok' and found['received']==2
            rows=await call('extract',{'ref':found['records']['ref'],'count':2,'fields':['Title','ProductCode','ContentType','DOI','target']})
            assert rows['returned']==2
            book=await call('fetch',{'source':args.source,'target':'SURV/168','parts':['metadata','abstract','export']})
            assert book['status']=='ok'
            row=await call('extract',{'ref':book['records']['ref'],'count':1,'fields':['ProductCode','Title','Subtitle']})
            assert row['items'][0]['ProductCode']=='SURV/168'
            empty=await call('search',{'source':args.source,'query':'qzjxwv947231','limit':2})
            assert empty['status']=='not_found' and empty['total']==0
        elif args.source == 'project-euclid':
            found=await call('search',{'source':args.source,'query':'Sure independence screening in generalized linear models','options':{'field':'TITLE','year_from':2010,'year_to':2010,'terms':[{'query':'Fan','field':'AUTHORNAME'},{'query':'Song','field':'AUTHORNAME'},{'query':'qzjxwv947231','field':'TITLE','operator':'NOT'}],'publication_titles':['The Annals of Statistics']},'limit':2,'export':'endnote'})
            assert found['status']=='ok' and found['received']==1
            native=await call('extract',{'ref':found['export']['artifacts'][0]['artifact']['ref'],'count':1})
            assert native['items'][0]['fields']['DOI']==['10.1214/10-AOS798']
            found=await call('search',{'source':args.source,'query':'complexity','options':{'field':'TITLE','sort':'PubDateDesc','page_size':100},'start':99,'limit':2,'export':'csv'})
            assert found['status']=='ok' and found['received']==2
            chosen=await call('extract',{'ref':found['records']['ref'],'count':2})
            assert chosen['returned']==2
            fetched=await call('fetch',{'source':args.source,'target':'10.1214/10-AOS798','parts':['metadata','abstract','fulltext','export']})
            assert fetched['status']=='ok'
            assert {x['format'] for x in fetched['components']['export']['artifacts']}=={'bibtex','ris','endnote','citation-pdf'}
            first=await call('extract',{'ref':fetched['components']['fulltext']['artifact']['ref'],'count':1})
            assert '10.1214/10-AOS798'.casefold() in first['items'][0]['text'].casefold()
            empty=await call('search',{'source':args.source,'query':'qzjxwv947231','limit':2})
            assert empty['status']=='not_found' and empty['total']==0
        elif args.source == 'iop':
            fetched = await call('fetch', {'source':'iop','target':'https://iopscience.iop.org/article/10.1088/0022-3727/34/10/311/meta','parts':['metadata','abstract','fulltext','export']})
            assert fetched['status']=='ok'
            assert fetched['components']['fulltext']['artifact']['pages']==16
            native = await call('extract', {'ref':fetched['components']['export']['artifact']['ref'],'count':1})
            assert native['items'][0]['doi']=='10.1088/0022-3727/34/10/311'
        elif args.source == 'science-direct':
            fetched = await call('fetch', {'source':args.source,'target':'10.1006/jcss.1997.1494','parts':['metadata','abstract','export']})
            assert fetched['status'] == 'ok'
            assert fetched['pii'] == 'S002200009791494X'
            native = await call('extract', {'ref':fetched['components']['export']['artifact']['ref'],'count':1})
            assert native['items'][0]['fields']['t1'] == ['Natural Proofs']
            assert len(native['items'][0]['fields']['ab'][0]) > 900
        elif args.source == 'society-journal':
            fetched = await call('fetch', {'source':args.source,'target':'https://www.combinatorics.org/ojs/index.php/eljc/article/view/v1i1r1','parts':['metadata','abstract','fulltext','export']})
            assert fetched['status'] == 'ok' and fetched['components']['fulltext']['artifact']['pages'] == 10
            assert {x['format'] for x in fetched['components']['export']['artifacts']} == {'ris','bibtex'}
            native = await call('extract', {'ref':next(a['artifact']['ref'] for a in fetched['components']['export']['artifacts'] if a['format']=='ris'),'count':1})
            assert native['items'][0]['fields']['do'] == ['10.37236/1181']
        elif args.source == 'author-repository':
            fetched = await call('fetch', {'source':args.source,'target':'https://www.cs.toronto.edu/~sacook/homepage/ptime.pdf','parts':['metadata','fulltext']})
            assert fetched['status'] == 'ok' and fetched['components']['fulltext']['artifact']['pages'] == 14
            page = await call('extract', {'ref':fetched['components']['fulltext']['artifact']['ref'],'count':1})
            assert 'RECURSION' in page['items'][0]['text']
            site = await call('fetch', {'source':args.source,'target':'https://www.cs.toronto.edu/~sacook/','parts':['metadata','fulltext','supplementary']})
            assert site['status'] == 'ok'
            links = await call('extract', {'ref':site['components']['supplementary']['artifact']['ref'],'count':200})
            assert any(x['url'].endswith('/ptime.pdf') for x in links['items'])
        elif args.source == 'knu-fric':
            found = await call('search', {'source':'knu-fric','query':'computer','start':9,'limit':2,'export':'csv'})
            assert found['status'] == 'ok' and found['received'] == 2 and found['total'] > 10
            records = await call('extract', {'ref':found['records']['ref'],'count':2})
            assert records['returned'] == 2
            fetched = await call('fetch', {'source':'knu-fric','target':'issn:2263-8733','parts':['metadata','export']})
            assert fetched['status'] == 'ok'
            zero = await call('search', {'source':'knu-fric','query':'codexnomatchxqz947231','limit':2})
            assert zero['status'] == 'not_found' and zero['total'] == 0
        elif args.source == "numdam":
            search = await call("search", {"source": "numdam", "query": "complexity", "start": 19, "limit": 2, "export": "ris"})
            assert search['status'] == 'ok', search.get('code')
            assert search['received'] == 2 and search['total'] > 20
            citations = await call('extract', {'ref': search['export']['ref'], 'count': 2})
            assert citations['returned'] == 2
            fetched = await call('fetch', {'source': 'numdam', 'target': '10.1051/ita/2011126', 'parts': ['metadata', 'abstract', 'fulltext', 'export', 'supplementary']})
            assert fetched['status'] == 'ok', fetched.get('code')
            assert fetched['native_id'] == 'ITA_2012__46_1_67_0'
            page = await call('extract', {'ref': fetched['components']['fulltext']['artifact']['ref'], 'count': 1})
            assert 'THREE COMPLEXITY FUNCTIONS' in page['items'][0]['text'].upper()
            filtered = await call('search', {'source': 'numdam', 'query': '"Three complexity functions"', 'options': {'field': 'title', 'terms': [{'field': 'date', 'from': '2012', 'until': '2012'}]}, 'limit': 2, 'export': 'bibtex'})
            assert filtered['status'] == 'ok' and filtered['received'] == 1
            empty = await call('search', {'source': 'numdam', 'query': 'codexnomatchxqz947231', 'limit': 2})
            assert empty['status'] == 'not_found' and empty['total'] == 0
            fetched = await call("fetch", {"source": "numdam", "target": "AIF_1956__6__1_0", "parts": ["metadata", "fulltext"]})
            assert fetched["status"] == "ok", fetched.get("code")
            page = await call("extract", {"ref": fetched["components"]["fulltext"]["artifact"]["ref"], "count": 1})
            assert page["returned"] == 1
        elif args.source == "aps":
            search = await call("search", {"source": "aps", "query": "", "options": {"from": "2026-09-01", "until": "2026-09-02", "date": "published"}, "limit": 2})
            assert search["status"] == "ok", search.get("code")
            assert search["received"] == 2
            fetched = await call("fetch", {"source": "aps", "target": "10.1103/PhysRevLett.116.061102", "parts": ["metadata", "abstract", "fulltext"]})
            assert fetched["status"] == "ok", fetched.get("code")
            first_page = await call("extract", {"ref": fetched["components"]["fulltext"]["artifact"]["ref"], "count": 1})
            assert "Gravitational" in first_page["items"][0]["text"]
        elif args.source == "eudml":
            search = await call("search", {"source": "eudml", "query": 'all="P versus NP"', "start": 1, "limit": 2, "export": "rss"})
            assert search["status"] == "ok", search.get("code")
            assert search["received"] == 2
            xml = await call("extract", {"ref": search["export"]["ref"], "selection": "./channel/item", "count": 2})
            assert xml["returned"] == 2
            fetched = await call("fetch", {"source": "eudml", "target": "196516", "parts": ["metadata"]})
            assert fetched["status"] == "ok", fetched.get("code")
            native = await call("extract", {"ref": fetched["components"]["metadata"]["artifact"]["ref"], "selection": "./front/article-meta/article-id", "count": 10})
            assert any("urn:eudml:doc:196516" in item for item in native["items"])
        elif args.source == 'arxiv':
            found = await call('search', {'source': 'arxiv', 'query': 'ti:"The OpenCitations Index"', 'limit': 2, 'export': 'native'})
            assert found['status'] == 'ok' and found['received'] >= 1
            fetched = await call('fetch', {'source': 'arxiv', 'target': 'https://arxiv.org/html/2408.02321v1', 'parts': ['metadata', 'fulltext', 'supplementary']})
            assert fetched['status'] == 'ok' and fetched['version'] == '2408.02321v1'
            assert fetched['components']['fulltext']['artifact']['media_type'] == 'text/html'
            heading = await call('extract', {'ref': fetched['components']['fulltext']['artifact']['ref'], 'selection': 'h1.ltx_title_document', 'count':1})
            assert 'OpenCitations' in str(heading['items'][0])
            archive = await call('extract', {'ref': fetched['components']['supplementary']['artifact']['ref'], 'count': 20})
            assert archive['total'] == 11
            source = await call('extract', {'ref': fetched['components']['supplementary']['artifact']['ref'], 'selection': 'main.tex', 'count': 1})
            lines = await call('extract', {'ref': source['items'][0]['artifact']['ref'], 'count': 3})
            assert lines['status'] == 'ok' and lines['returned'] == 3
        elif args.source=='zbmath':
            window=await call('search',{'source':'zbmath','query':'','options':{'Title':'Natural proofs'},'start':1,'limit':2,'export':'native'})
            assert window['status']=='ok' and window['received']==2
            chosen=await call('extract',{'ref':window['records']['ref'],'count':2,'fields':['id','title']})
            baseline=await call('search',{'source':'zbmath','query':'','options':{'Title':'Natural proofs'},'limit':4})
            first=await call('extract',{'ref':baseline['records']['ref'],'count':4,'fields':['id']})
            assert [row['id'] for row in chosen['items']]==[row['id'] for row in first['items'][1:3]]
            found=await call('fetch',{'source':'zbmath','target':'10.1006/jcss.1997.1494','parts':['metadata','abstract','supplementary','export']})
            assert found['status']=='partial' and found['identity']['zbmath_id']==1079979
            assert found['components']['abstract']['status']=='restricted'
            references=found['components']['supplementary']
            rows=await call('extract',{'ref':references['artifact']['ref'],'selection':references['selection'],'count':40})
            assert rows['returned']==40
            linked=await call('fetch',{'source':'zbmath','target':'https://zbmath.org/?q=an:0884.68055','parts':['metadata']})
            assert linked['status']=='ok' and linked['identity']['zbmath_id']==1079979
            candidates=await call('fetch',{'source':'zbmath','target':'Natural proofs','parts':['metadata']})
            assert candidates['status']=='selection_required'
        elif args.source in ('crossref', 'crossmark'):
            found = await call('search', {'source': args.source, 'query': '', 'options': {'filter': 'doi:10.1145/321250.321251'}, 'limit': 1, 'export': 'bibtex'})
            assert found['status'] == 'ok' and found['received'] == 1
            native = await call('extract', {'ref': found['export']['ref'], 'count': 1})
            assert native['items'][0]['doi'] == '10.1145/321250.321251'
            fetched = await call('fetch', {'source': args.source, 'target': '10.1145/321250.321251', 'parts': ['metadata','export']})
            assert fetched['status'] == 'ok'
            assert len(fetched['components']['export']['artifacts']) == 8
            csl = next(a['artifact'] for a in fetched['components']['export']['artifacts'] if a['format']=='csl-json')
            parsed = await call('extract', {'ref': csl['ref'], 'fields': ['DOI', 'title'], 'count':1})
            assert parsed['items'][0]['DOI'] == '10.1145/321250.321251'
        elif args.source == 'opencitations':
            found = await call('search', {'source': args.source, 'query': 'doi:10.1186/1756-8722-6-59', 'start': 1, 'limit': 2, 'export': 'csv'})
            assert found['status'] == 'ok' and found['received'] == 2
            rows = await call('extract', {'ref': found['export']['ref'], 'count': 2})
            assert rows['returned'] == 2
            first = rows['items'][0]
            fetched = await call('fetch', {'source': args.source, 'target': 'oci:' + first['oci'], 'parts': ['metadata', 'export']})
            assert fetched['status'] == 'ok' and fetched['received'] == 1
            count = await call('search', {'source': args.source, 'query': 'doi:10.1186/1756-8722-6-59', 'options': {'direction': 'reference-count'}, 'limit': 1})
            value = await call('extract', {'ref': count['records']['ref'], 'count': 1})
            assert int(value['items'][0]['count']) == found['total']
        elif args.source == "zenodo":
            search = await call("search", {"source": "zenodo", "query": '"P versus NP"', "limit": 1})
            assert search["status"] == "ok", search.get("code")
            fetched = await call("fetch", {"source": "zenodo", "target": "822080", "parts": ["metadata", "fulltext"]})
            assert fetched["status"] == "ok", fetched.get("code")
            file = fetched["components"]["fulltext"]["artifacts"][0]["artifact"]
            assert file["checksum_verified"] is True
            assert file["provider_checksum"] == "md5:e2c576e39d4d885b7383cc3509eab9bf"
            result = await call("extract", {"ref": file["ref"], "count": 1})
            assert result["returned"] == 1
        elif args.source == "theory-of-computing":
            search = await call("search", {"source": args.source, "query": "geometric complexity theory", "options": {"field": "category"}, "limit": 2, "export": "bibtex"})
            assert search["status"] == "ok", search.get("code")
            rows = await call("extract", {"ref": search["records"]["ref"], "count": 2})
            assert rows["items"][0]["id"] == "gs010"
            fetched = await call("fetch", {"source": args.source, "target": "gs010", "parts": ["metadata", "abstract", "fulltext", "supplementary"]})
            assert fetched["status"] == "ok", fetched.get("code")
            assert fetched["components"]["fulltext"]["artifact"]["pages"] == 166
            source = next(item["artifact"] for item in fetched["components"]["supplementary"]["artifacts"] if item["format"] == "source_zip")
            archive = await call("extract", {"ref": source["ref"], "count": 10})
            assert archive["returned"] > 0
            web = await call("search", {"source": args.source, "query": '"geometric complexity"', "start": 10, "limit": 2})
            assert web["status"] == "ok", web.get("code")
            assert web["received"] == 2
        elif args.source in ('mathlib', 'math-comp'):
            path_prefix = 'Mathlib/Computability/' if args.source == 'mathlib' else 'algebra/'
            query = 'theorem' if args.source == 'mathlib' else 'Lemma'
            found = await call('search', {'source': args.source, 'query': query, 'options': {'path': path_prefix}, 'limit': 2})
            assert found['status'] == 'ok' and found['received'] == 2
            rows = await call('extract', {'ref': found['records']['ref'], 'count': 2})
            first = rows['items'][0]
            fetched = await call('fetch', {'source': args.source, 'target': found['revision'] + ':' + first['path'], 'parts': ['metadata', 'fulltext']})
            assert fetched['status'] == 'ok' and fetched['revision'] == found['revision']
            lines = await call('extract', {'ref': fetched['components']['fulltext']['artifact']['ref'], 'start': first['line'] - 1, 'count': 1})
            assert lines['items'][0] == first['text']
        elif args.source == "afp":
            search = await call("search", {"source": "afp", "query": "Cook-Levin", "limit": 10})
            assert search["status"] == "ok", search.get("code")
            records = await call("extract", {"ref": search["records"]["ref"], "count": 10})
            entry = next(row for row in records["items"] if row["id"] == "Cook_Levin")
            fetched = await call("fetch", {"source": "afp", "target": entry["target"], "parts": ["metadata", "abstract", "fulltext"]})
            assert fetched["status"] == "ok", fetched.get("code")
            assert fetched["commit"] == search["commit"]
            archive = await call("extract", {"ref": fetched["components"]["fulltext"]["artifact"]["ref"], "count": 1000})
            assert archive["returned"] > 1
        elif args.source == "ieee-xplore":
            search = await call("search", {"source": "ieee-xplore", "query": '"Document Title":"P versus NP"', "limit": 1, "export": "bibtex"})
            assert search["status"] == "ok", search.get("code")
            records = await call("extract", {"ref": search["records"]["ref"], "count": 1})
            assert records["items"][0]["articleNumber"] == "10488889"
            bib = await call("extract", {"ref": search["export"]["ref"], "count": 1})
            assert bib["items"][0]["doi"] == "10.1109/MC.2024.3358928"
            fetched = await call("fetch", {"source": "ieee-xplore", "target": "10488889", "parts": ["metadata", "abstract", "fulltext"]})
            assert fetched["status"] == "ok", fetched.get("code")
            assert fetched["components"]["fulltext"]["artifact"]["pages"] >= 2
            details=await call('fetch',{'source':'ieee-xplore','target':'10488889','parts':['metadata','supplementary']})
            references=details['components']['supplementary']['references']
            assert references['status']=='available' and references['count']==22
            rows=await call('extract',{'ref':references['artifact']['ref'],'count':22,'fields':['id','order','title','text','links']})
            assert rows['returned']==22 and rows['items'][0]['title']=='PRIMES is in P'
        elif args.source == "pqdt":
            search = await call("search", {"source": "pqdt", "query": 'TI("P versus NP")', "limit": 1, "export": "ris"})
            assert search["status"] == "ok", search.get("code")
            records = await call("extract", {"ref": search["records"]["ref"], "count": 1})
            assert records["items"][0]["id"] == "2618193239"
            fetched = await call("fetch", {"source": "pqdt", "target": "2618193239", "parts": ["metadata", "abstract", "fulltext"]})
            assert fetched["status"] == "ok", fetched.get("code")
            assert fetched["components"]["fulltext"]["artifact"]["pages"] >= 40
            following = await call("search", {"source": "pqdt", "query": "TI(complexity)", "start": 20, "limit": 1, "export": "ris"})
            assert following["status"] == "ok", following.get("code")
            assert following["received"] == 1
        elif args.source == "scopus":
            search = await call("search", {"source": "scopus", "query": 'TITLE("P versus NP")', "start": 9, "limit": 2, "export": "csv"})
            assert search["status"] == "ok", search.get("code")
            assert search["received"] == 2
            records = await call("extract", {"ref": search["records"]["ref"], "count": 2})
            assert records["items"][0]["title"] == "P versus NP and geometry"
            assert records["items"][0]["eid"] != records["items"][1]["eid"]
            fetched = await call("fetch", {"source": "scopus", "target": records["items"][0]["eid"], "parts": ["metadata", "abstract"]})
            assert fetched["status"] == "ok", fetched.get("code")
            related=await call('fetch',{'source':'scopus','target':'2-s2.0-77957268169','parts':['metadata','supplementary']})
            assert related['status']=='ok'
            relation=related['components']['supplementary']
            assert relation['references']['received']==relation['references']['total']
            assert relation['citations']['received']==relation['citations']['total']
        elif args.source == "drops":
            search = await call("search", {"source": "drops", "query": "P versus NP", "limit": 2, "export": "bibtex"})
            assert search["status"] == "ok", search.get("code")
            cited = await call('extract', {'ref': search['export']['ref'], 'count': 2})
            assert cited['returned'] == 2
            fetched = await call("fetch", {"source": "drops", "target": "10.4230/LIPIcs.CSL.2020.5", "parts": ["metadata", "abstract", "fulltext", "export"]})
            assert fetched["status"] == "ok", fetched.get("code")
            assert fetched["components"]["fulltext"]["artifact"]["pages"] == 2
            assert len(fetched['components']['export']['artifacts']) == 5
            html = await call('fetch', {'source': 'drops', 'target': 'https://drops.dagstuhl.de/storage/00lipics/lipics-vol347-dna31/html/LIPIcs.DNA.31.9/LIPIcs.DNA.31.9.html', 'parts': ['metadata', 'fulltext', 'supplementary']})
            assert html['status'] == 'ok', html.get('code')
            assert html['components']['fulltext']['artifact']['media_type'] == 'text/html'
            extracted = await call('extract', {'ref': html['components']['fulltext']['artifact']['ref'], 'selection': 'article', 'count': 1})
            assert extracted['returned'] == 1
            artifact = await call('fetch', {'source': 'drops', 'target': '10.4230/artifacts.27685', 'parts': ['metadata', 'export']})
            assert artifact['status'] == 'ok'
            assert {x['format'] for x in artifact['components']['export']['artifacts']} == {'schema-org', 'bibtex', 'xml', 'codemeta-json'}
        elif args.source == 'jstor':
            fetched=await call('fetch',{'source':'jstor','target':'10.2307/345683','parts':['metadata','abstract','export']})
            assert fetched['status']=='ok',fetched.get('code')
            citation=await call('extract',{'ref':fetched['components']['export']['artifact']['ref'],'count':2})
            assert citation['returned']==1
            assert citation['items'][0]['fields']['do']==['10.2307/345683']
            assert 'Provider: JSTOR' in citation['items'][0]['source_preamble']
            formats={item['format']:item['artifact'] for item in fetched['components']['export']['artifacts']}
            assert set(formats)=={'ris','bibtex'}
            bib=await call('extract',{'ref':formats['bibtex']['ref'],'count':1})
            assert bib['items'][0]['url'].endswith('/stable/345683')
            book=await call('fetch',{'source':'jstor','target':'https://www.jstor.org/stable/jj.8306294','parts':['metadata','export']})
            assert book['status']=='ok'
            metadata=await call('extract',{'ref':book['records']['ref'],'count':1})
            assert metadata['items'][0]['fields']['ty']==['BOOK']
            assert len(book['components']['export']['artifacts'])==2
        elif args.source == 'de-gruyter':
            search=await call('search', {'source':'de-gruyter','query':'title:(complexity)','options':{'visibility':'available'},'limit':2,'export':'ris'})
            assert search['status']=='ok', search.get('export')
            assert search['received']==2
            for item in search['export']['artifacts']:
                citation=await call('extract',{'ref':item['ref'],'count':2})
                assert citation['returned']==1
            records=await call('extract',{'ref':search['records']['ref'],'count':2})
            fetched=await call('fetch',{'source':'de-gruyter','target':records['items'][0]['url'],'parts':['metadata','abstract','fulltext','export']})
            assert fetched['status']=='ok', {k:v.get('status') for k,v in fetched.get('components',{}).items()}
            assert fetched['components']['fulltext']['artifact']['pages']>=1
            following=await call('search',{'source':'de-gruyter','query':'title:(complexity)','options':{'visibility':'available'},'start':9,'limit':2,'export':'csv'})
            assert following['status']=='ok',following.get('code')
            assert following['received']==2
        elif args.source == 'taylor-francis':
            search = await call('search', {'source':'taylor-francis','query':'complexity','options':{'field':'Title'},'start':19,'limit':2,'export':'bibtex'})
            assert search['status']=='ok', search.get('export')
            assert search['received']==2
            for item in search['export']['artifacts']:
                exported=await call('extract', {'ref':item['ref'],'count':2})
                assert exported['returned']==1
            fetched=await call('fetch', {'source':'taylor-francis','target':'10.1080/09557571.2011.558053','parts':['metadata','abstract','fulltext','export']})
            assert fetched['status']=='ok', {k:v.get('status') for k,v in fetched.get('components',{}).items()}
            assert fetched['components']['fulltext']['artifact']['pages']==23
        elif args.source == 'cambridge':
            search = await call('search', {'source':'cambridge','query':'"P versus NP"','options':{'content_type':'Articles','available':True},'limit':2,'export':'ris'})
            assert search['status']=='ok', search.get('code')
            assert search['received']==2
            records = await call('extract', {'ref':search['records']['ref'],'count':2})
            citation = await call('extract', {'ref':search['export']['artifacts'][0]['ref'],'count':2})
            assert citation['returned']==2
            fetched = await call('fetch', {'source':'cambridge','target':records['items'][0]['url'],'parts':['metadata','abstract','fulltext','export']})
            assert fetched['status']=='ok', {k:v.get('status') for k,v in fetched.get('components',{}).items()}
            assert fetched['components']['fulltext']['artifact']['pages']>=2
            following = await call('search', {'source':'cambridge','query':'complexity','start':19,'limit':2,'export':'ris'})
            assert following['status']=='ok', following.get('code')
            assert following['received']==2
        elif args.source == 'aip':
            search = await call('search', {'source':'aip','query':'quantum computation','options':{'field':'Title','exact':True},'limit':1})
            assert search['status']=='ok', search.get('code')
            assert search['received']==1
            records = await call('extract', {'ref':search['records']['ref'],'count':1})
            fetched = await call('fetch', {'source':'aip','target':records['items'][0]['url'],'parts':['metadata','abstract','export']})
            assert fetched['status']=='ok', {k:v.get('status') for k,v in fetched.get('components',{}).items()}
            citation = await call('extract', {'ref':fetched['components']['export']['artifact']['ref'],'count':1})
            assert citation['returned']==1
            following = await call('search', {'source':'aip','query':'quantum computation','options':{'field':'Title','exact':True},'start':19,'limit':2,'export':'csv'})
            assert following['status']=='ok', following.get('code')
            assert following['received']==2
            oa = await call('fetch', {'source':'aip','target':'10.1063/5.0281142','parts':['metadata','abstract','fulltext','export']})
            assert oa['status']=='ok' and oa['components']['fulltext']['artifact']['pages']==16
            first_page = await call('extract', {'ref':oa['components']['fulltext']['artifact']['ref'],'count':1})
            assert '10.1063/5.0281142' in first_page['items'][0]['text']
        elif args.source == 'oxford':
            search = await call('search', {'source':'oxford','query':'P versus NP','options':{'field':'Title','exact':True},'limit':2,'export':'bibtex'})
            assert search['status']=='ok', search.get('export')
            assert search['received']==1
            records = await call('extract', {'ref':search['records']['ref'],'count':2})
            assert records['items'][0]['title']=='The Prehistory of P versus NP'
            citation = await call('extract', {'ref':search['export']['artifacts'][0]['ref'],'count':2})
            assert citation['items'][0]['doi']=='10.23943/princeton/9780691175782.003.0005'
            fetched = await call('fetch', {'source':'oxford','target':records['items'][0]['url'],'parts':['metadata','abstract','export']})
            assert fetched['status']=='ok', {k:v.get('status') for k,v in fetched.get('components',{}).items()}
            following = await call('search', {'source':'oxford','query':'complexity','options':{'field':'Title'},'start':19,'limit':2,'export':'csv'})
            assert following['status']=='ok', following.get('code')
            assert following['received']==2
        elif args.source == "springer":
            search = await call('search', {'source': 'springer', 'query': 'P versus NP', 'options': {'field': 'Title'}, 'limit': 2, 'export': 'bibtex'})
            assert search['status'] == 'ok', search.get('export')
            assert search['received'] == 2
            for citation in search['export']['artifacts']:
                extracted = await call('extract', {'ref': citation['ref'], 'count': 2})
                assert extracted['returned'] == 1
            fetched = await call('fetch', {'source': 'springer', 'target': '10.1007/s00037-008-0249-x', 'parts': ['metadata','abstract','fulltext','export']})
            assert fetched['status'] == 'ok', {k:v.get('status') for k,v in fetched.get('components',{}).items()}
            assert fetched['components']['fulltext']['artifact']['pages'] == 28
            following = await call('search', {'source': 'springer', 'query': '"P versus NP"', 'start': 19, 'limit': 2, 'export': 'csv'})
            assert following['status'] == 'ok', following.get('code')
            assert following['received'] == 2
            attached=await call('fetch',{'source':'springer','target':'https://www.nature.com/articles/s41467-023-41217-6','parts':['metadata','supplementary']})
            files=attached['components']['supplementary']['files']
            assert attached['status']=='ok' and len(files)==2
            assert [file['artifact']['pages'] for file in files]==[42,19]
            for file in files:
                pages=await call('extract',{'ref':file['artifact']['ref'],'count':1})
                assert pages['status']=='ok' and pages['returned']==1
        elif args.source == "wiley":
            search = await call("search", {"source": "wiley", "query": "random graphs", "options": {"field": "Title"}, "start": 19, "limit": 2, "export": "bibtex"})
            assert search["status"] == "ok", search.get("export")
            assert search["received"] == 2
            records = await call("extract", {"ref": search["records"]["ref"], "count": 2})
            assert len({row["doi"] for row in records["items"]}) == 2
            citations = await call("extract", {"ref": search["export"]["artifact"]["ref"], "count": 2})
            assert citations["returned"] == 2
            fetched = await call("fetch", {"source": "wiley", "target": "10.1002/rsa.21210", "parts": ["metadata", "abstract", "fulltext"]})
            assert fetched["status"] == "ok", {k:v.get("status") for k,v in fetched.get("components", {}).items()}
            assert fetched["components"]["fulltext"]["artifact"]["pages"] > 1
            pdf_page = await call('extract', {'ref': fetched['components']['fulltext']['artifact']['ref'], 'count': 1})
            assert 'Weakly saturated random graphs' in ' '.join(pdf_page['items'][0]['text'].split())
            empty = await call("search", {"source": "wiley", "query": "zzzzscholarlyabsent998314", "options": {"field": "Title"}, "limit": 2})
            assert empty["status"] == "not_found"
            attached=await call('fetch',{'source':'wiley','target':'10.1002/rsa.70063','parts':['metadata','supplementary']})
            files=attached['components']['supplementary']['files']
            assert attached['status']=='ok' and len(files)==1
            archive=await call('extract',{'ref':files[0]['artifact']['ref'],'count':20})
            assert {item['path'] for item in archive['items']}=={'anc/','anc/dimension_bounds.py','anc/internal_external.py'}
            for member in ('anc/dimension_bounds.py','anc/internal_external.py'):
                selected=await call('extract',{'ref':files[0]['artifact']['ref'],'selection':member})
                text=await call('extract',{'ref':selected['items'][0]['artifact']['ref'],'count':3})
                assert text['status']=='ok' and text['unit']=='lines' and text['returned']==3
        else:
            query = 'ti:"P versus NP"' if args.source == "arxiv" else "P versus NP"
            options = {"Title": "P versus NP"} if args.source == "zbmath" else {}
            search = await call("search", {"source": args.source, "query": "" if options else query, "options": options, "limit": 2})
            assert search["status"] == "ok", search.get("code")
            extracted = await call("extract", {"ref": search["records"]["ref"], "count": 2})
            assert extracted["returned"] == search["received"]
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        report["completed"] = True
    preserve()
    print(json.dumps({"report": str(path), "workflow_completed": report["completed"]}), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
