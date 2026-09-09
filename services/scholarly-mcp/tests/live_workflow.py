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
