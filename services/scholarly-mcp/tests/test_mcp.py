"""Real stdio transport, tool discovery, schemas and local extraction."""
import asyncio
import base64
import json
from pathlib import Path
import sys
import tempfile
import unittest

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scholarly import ArtifactStore


class MCPContract(unittest.IsolatedAsyncioTestCase):
    async def test_stdio_client_can_discover_and_extract_without_internal_knowledge(self):
        self.assertTrue((ROOT / "server.py").exists(), "The five-tool stdio MCP entry point has not been implemented")
        with tempfile.TemporaryDirectory() as tmp:
            artifact = ArtifactStore(tmp).put(b'[{"title":"one"},{"title":"two"}]', "application/json", "crossref", "https://api.crossref.org/works")
            params = StdioServerParameters(command=sys.executable, args=[str(ROOT / "server.py"), "--data-dir", tmp])
            async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
                await session.initialize()
                tools = (await session.list_tools()).tools
                self.assertEqual({tool.name for tool in tools}, {"list_sources", "describe_source", "search", "fetch", "extract"})
                for tool in tools:
                    self.assertTrue(tool.description)
                    self.assertIsNotNone(tool.outputSchema)
                    self.assertIn("status", tool.outputSchema.get("required", []))
                result = await session.call_tool("extract", {"ref": artifact["ref"], "start": 1, "count": 1, "fields": ["title"]})
                self.assertFalse(result.isError)
                self.assertEqual(result.structuredContent["items"], [{"title": "two"}])
                content = (await session.read_resource(artifact["ref"])).contents[0]
                self.assertEqual(json.loads(base64.b64decode(content.blob)), [{"title": "one"}, {"title": "two"}])
                png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jSgAAAABJRU5ErkJggg==")
                picture = ArtifactStore(tmp).put(png, "image/png", "arxiv", "https://arxiv.org/")
                viewed = await session.call_tool("extract", {"ref": picture["ref"]})
                self.assertEqual(viewed.structuredContent["status"], "ok")
                self.assertEqual(base64.b64decode(next(c for c in viewed.content if c.type == "image").data), png)
                bad = await session.call_tool("fetch", {"source": "nonexistent", "target": "anything"})
                self.assertEqual(bad.structuredContent["code"], "unknown_source")
                sources = (await session.call_tool("list_sources", {})).structuredContent
                names = {row["id"] for row in sources["sources"]}
                self.assertTrue({"mathscinet", "wos", "scopus", "acm-dl", "ieee-xplore", "pqdt", "arxiv", "crossref", "numdam", "mathlib", "wiley", "author-repository"} <= names)
                description = (await session.call_tool("describe_source", {"source": "mathscinet"})).structuredContent
                self.assertIn("search", description["usage"])
                self.assertIn("examples", description["usage"])
                deferred = (await session.call_tool("fetch", {"source": "unpaywall", "target": "10.1038/nature12373"})).structuredContent
                self.assertEqual(deferred["code"], "source_deferred")
                self.assertEqual(deferred["status"], "unsupported")
                guide = (await session.call_tool("describe_source", {"source": "unpaywall"})).structuredContent
                self.assertEqual(guide["implementation"], "deferred")
                self.assertEqual(guide["capabilities"], ["source_guide"])


if __name__ == "__main__":
    unittest.main()
