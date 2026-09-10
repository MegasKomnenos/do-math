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
            fetched = await call("fetch", {"source": args.source, "target": "MR2733384", "parts": ["metadata", "supplementary"]})
            assert fetched["status"] == "ok", fetched.get("code")
            pdf = fetched["components"]["supplementary"]["artifact"]
            page = await call("extract", {"ref": pdf["ref"], "count": 1})
            assert "2733384" in page["items"][0]["text"]
        elif args.source == "wos":
            search = await call("search", {"source": "wos", "query": 'TI=("P versus NP")', "limit": 5, "export": "plain"})
            assert search["status"] == "ok", search.get("code")
            records = await call("extract", {"ref": search["records"]["ref"], "count": 5})
            assert records["returned"] == 5
            assert len(records["items"][0]["fields"]["cr"]) == 47
        elif args.source == "eccc":
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
        elif args.source == "drops":
            search = await call("search", {"source": "drops", "query": "P versus NP", "limit": 2})
            assert search["status"] == "ok", search.get("code")
            fetched = await call("fetch", {"source": "drops", "target": "10.4230/LIPIcs.CSL.2020.5", "parts": ["metadata", "abstract", "fulltext"]})
            assert fetched["status"] == "ok", fetched.get("code")
            assert fetched["components"]["fulltext"]["artifact"]["pages"] == 2
        elif args.source == 'jstor':
            fetched=await call('fetch',{'source':'jstor','target':'10.2307/345683','parts':['metadata','abstract','export']})
            assert fetched['status']=='ok',fetched.get('code')
            citation=await call('extract',{'ref':fetched['components']['export']['artifact']['ref'],'count':2})
            assert citation['returned']==1
            assert citation['items'][0]['fields']['do']==['10.2307/345683']
            assert 'Provider: JSTOR' in citation['items'][0]['source_preamble']
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
