"""Local stdio MCP. Run with the dedicated environment's Python executable."""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
from concurrent.futures import ThreadPoolExecutor
import logging
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, ImageContent, TextContent
from pydantic import BaseModel, ConfigDict

from registry import SOURCES, source_info
from scholarly import ArtifactStore, ServiceError, extract_artifact
from scholarly import Sanitizer
from api_adapters import make_adapters
from browser_adapters import KudosGateway, MathSciNet, WebOfScience, ECCC, ACM
from drops import DROPS
from scopus import Scopus
from pqdt import PQDT
from ieee import IEEE
from afp import AFP
from toc import TheoryOfComputing
from eudml import EuDML
from aps import APS
from dataclasses import replace
from publishers import PROFILES, Publisher

ROOT = Path(__file__).resolve().parent
STORE = ArtifactStore(ROOT / "data")
# ponytail: one worker owns browser sessions; use one server per independent research execution.
WORKER = ThreadPoolExecutor(max_workers=1, thread_name_prefix="scholarly")
ADAPTERS = {}


class ToolResult(BaseModel):
    model_config = ConfigDict(extra="allow")
    status: Literal["ok", "partial", "not_found", "restricted", "error", "not_implemented", "unsupported", "selection_required"]

mcp = FastMCP("scholarly", instructions="자료원 목록 → describe_source → 자료원 문법으로 search → extract로 선별 → fetch. 한 호출은 지정 자료원에서 끝난다. 큰 결과는 artifact ref로 보존되며 extract로 다시 읽는다. 미구현·미검증 표지를 확인한다.", log_level="WARNING")


def run_call(function, *args, **kwargs):
    try:
        result = function(*args, **kwargs)
    except ServiceError as error:
        result = error.result
    except Exception as error:
        # Library exception messages may contain authenticated URLs or request values.
        logging.getLogger("scholarly").error("operation failed: %s", type(error).__name__)
        result = {"status": "error", "code": "execution_error", "message": "Server execution failed", "error_type": type(error).__name__}
    return ToolResult.model_validate(result)


@mcp.tool()
def list_sources() -> ToolResult:
    """지원·구현 중인 자료원과 기능 상태를 조회한다. 상세 사용법은 describe_source로 읽는다."""
    return ToolResult(status="ok", sources=[s.summary() for s in SOURCES.values()])


@mcp.tool()
def describe_source(source: str) -> ToolResult:
    """자료원별 검색 문법·필드·필터·export·확보 범위와 예제를 반환한다."""
    def describe():
        item = source_info(source)
        return {"status": "ok", **item.summary(), "home": item.home, "usage": item.usage,
            "scope": "한 호출은 이 자료원에 한정된다. pending은 개발이 남았다는 뜻이며 자료원 자체의 기능 부재를 뜻하지 않는다."}
    return run_call(describe)


def operation(source, name, *args, **kwargs):
    info = source_info(source)
    if info.implementation == "deferred":
        raise ServiceError("source_deferred", "This source is deferred by the user's access requirements", status="unsupported", source=source)
    if source not in ADAPTERS:
        raise ServiceError("adapter_not_implemented", "This source adapter is still being implemented", status="not_implemented", source=source, transport=info.transport)
    return getattr(ADAPTERS[source], name)(*args, **kwargs)


@mcp.tool()
async def search(source: str, query: str, options: dict | None = None, start: int = 0, limit: int = 20, cursor: str | None = None, export: str | None = None) -> ToolResult:
    """지정 자료원에서 검색한다. query·options는 describe_source 문법을 따른다. start는 0부터, limit는 요청 건수다. 결과 전건을 보존하고 건수·자료 참조·다음 범위를 반환한다. 검색식을 만들거나 자료원을 바꾸지 않는다."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(WORKER, lambda: run_call(operation, source, "search", query, options=options or {}, start=start, limit=limit, cursor=cursor, export=export))


@mcp.tool()
async def fetch(source: str, target: str, parts: list[str] | None = None) -> ToolResult:
    """지정 자료원의 식별자·링크·이름으로 자료를 확보한다. parts는 metadata, abstract, fulltext, supplementary, export 중 필요한 항목이다. 모호한 이름은 후보를 반환한다. 다른 자료원의 링크는 자동 방문하지 않는다."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(WORKER, lambda: run_call(operation, source, "fetch", target, parts=parts or ["metadata", "abstract", "fulltext"]))


@mcp.tool()
def extract(ref: str, fields: list[str] | None = None, start: int = 0, count: int = 20, selection: str = "", render: bool = False) -> ToolResult:
    """보존 자료를 기계적으로 읽는다. start는 0부터, count는 레코드·줄·쪽의 수다. JSON selection은 /경로 형식, HTML은 CSS 선택자, XML은 ElementTree XPath 부분집합이다. BibTeX·RIS·WOS·CSV의 selection=raw는 원 줄을 읽는다. JSON fields는 원 필드 이름이다. PDF는 쪽별 텍스트와 선택적 이미지 ref를 반환한다. 이미지 ref를 extract에 주면 이미지를 그대로 전달하며 판독은 호출 AI가 한다."""
    result = run_call(extract_artifact, STORE, ref, fields=fields, start=start, count=count, selection=selection, render=render)
    payload = result.model_dump(mode="json")
    if payload.get("image_ref"):
        meta, data = STORE.read(payload["image_ref"])
        # SDK validates this transport container's structuredContent against ToolResult.
        return CallToolResult(structuredContent=payload, content=[TextContent(type="text", text=json.dumps(payload, ensure_ascii=False)),
            ImageContent(type="image", data=base64.b64encode(data).decode("ascii"), mimeType=meta["media_type"])])
    return result


@mcp.resource("scholarly://artifact/{artifact_id}", mime_type="application/octet-stream")
def read_artifact(artifact_id: str) -> bytes:
    """보존 파일의 정확한 바이트. 자료의 실제 MIME·해시·크기는 도구가 반환한 artifact 설명에 있다."""
    return STORE.read("scholarly://artifact/" + artifact_id)[1]


def main():
    global STORE
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    STORE = ArtifactStore(args.data_dir)
    ADAPTERS.update(make_adapters(STORE))
    ADAPTERS["afp"] = AFP(STORE)
    ADAPTERS["eudml"] = EuDML(STORE)
    ADAPTERS["aps"] = APS(STORE)
    gateway = KudosGateway(ROOT.parents[1] / ".credentials", STORE.sanitizer)
    firefox_gateway = KudosGateway(ROOT.parents[1] / ".credentials", STORE.sanitizer, engine="firefox")
    ADAPTERS["mathscinet"] = MathSciNet(STORE, gateway)
    ADAPTERS["wos"] = WebOfScience(STORE, gateway)
    ADAPTERS["eccc"] = ECCC(STORE, gateway)
    ADAPTERS["acm-dl"] = ACM(STORE, firefox_gateway)
    ADAPTERS["drops"] = DROPS(STORE, gateway)
    ADAPTERS["theory-of-computing"] = TheoryOfComputing(STORE, gateway)
    ADAPTERS["scopus"] = Scopus(STORE, firefox_gateway)
    ADAPTERS["pqdt"] = PQDT(STORE, firefox_gateway)
    ADAPTERS["ieee-xplore"] = IEEE(STORE, firefox_gateway)
    ADAPTERS["springer"] = Publisher(STORE, firefox_gateway, next(p for p in PROFILES if p.source == "springer"))
    for identifier in ("project-euclid", "cambridge", "oxford", "aip", "wiley"):
        ADAPTERS[identifier] = Publisher(STORE, firefox_gateway, next(p for p in PROFILES if p.source == identifier))
    ADAPTERS["aps-institutional"] = Publisher(STORE, firefox_gateway, replace(next(p for p in PROFILES if p.source == "aps"), source="aps-institutional"))
    try:
        mcp.run(transport="stdio")
    finally:
        WORKER.submit(gateway.close).result()
        WORKER.submit(firefox_gateway.close).result()
        WORKER.shutdown(wait=True, cancel_futures=True)


if __name__ == "__main__":
    main()
