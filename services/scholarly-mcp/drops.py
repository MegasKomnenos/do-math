"""DROPS: public metadata exports; fixed UI search and document-link discovery."""
import json
import re
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from api_adapters import APIAdapter, doi
from browser_adapters import browser_download, clean_html, goto_source, require_source_url
from scholarly import ServiceError, encoded


class DROPS(APIAdapter):
    source = "drops"
    hosts = ("drops.dagstuhl.de",)
    max_limit = 1000

    def __init__(self, store, gateway, client=None):
        super().__init__(store, client=client)
        self.gateway = gateway

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if cursor or export not in (None, "json", "html"):
            raise ServiceError("invalid_options", "DROPS search uses start/limit and json/html export")
        page = self.gateway.public_page(self.source)
        goto_source(page, "https://drops.dagstuhl.de/", self.hosts, wait_until="domcontentloaded", timeout=45000)
        page.locator('input[name="term"]').fill(query)
        with page.expect_navigation(wait_until="domcontentloaded"):
            page.locator('input[name="term"]').press("Enter")
        heading = page.get_by_role("heading", level=1)
        heading.wait_for()
        match = re.fullmatch(r'([0-9,]+) Search Results? for\s+"(.*)"', heading.inner_text().strip(), re.S)
        if not match or match.group(2) != query:
            raise ServiceError("query_mismatch", "DROPS did not display the requested query and result count")
        total = int(match.group(1).replace(",", ""))
        first_size = page.locator(".entity-list-item").count()
        if total and not first_size:
            raise ServiceError("invalid_response", "DROPS reported results without entity cards")
        size = first_size or 1
        rows, observations = [], []
        for number in range(start // size + 1, (min(start + limit, total) - 1) // size + 2):
            if number > 1:
                page.get_by_role("button", name=str(number), exact=True).first.click()
                page.wait_for_function("n => [...document.querySelectorAll('.page-item.active')].some(e => e.textContent.trim() === String(n))", arg=number)
            require_source_url(page.url, self.hosts)
            raw = page.content()
            soup = BeautifulSoup(raw, "html.parser")
            native = []
            for card in soup.select(".entity-list-item"):
                title = card.select_one(".card-title a")
                if title is None:
                    raise ServiceError("invalid_response", "DROPS entity card has no title link")
                native.append({"id": title["href"], "url": urljoin(page.url, title["href"]),
                    "title": title.get_text(" ", strip=True), "listing": card.get_text("\n", strip=True)})
            observations.append(self.store.put(clean_html(raw, self.store.sanitizer), "text/html", self.source, page.url, query=query, page=number, role="search_page"))
            offset = (number - 1) * size
            rows.extend(row for i, row in enumerate(native, offset) if start <= i < start + limit)
        artifact = self.store.put(encoded(rows), "application/json", self.source, page.url, role="records", query=query, start=start, requested=limit, total=total)
        return {"status": "ok" if rows else "not_found", "source": self.source, "query": query, "start": start,
            "requested": limit, "received": len(rows), "total": total, "has_more": start + len(rows) < total,
            "next": {"start": start + len(rows)} if start + len(rows) < total else None,
            "records": artifact, "export": {"artifacts": observations} if export == "html" else artifact, "evidence": observations,
            "preview": [{k: row[k] for k in ("id", "title", "url")} for row in rows[:3]]}

    def fetch(self, target, *, parts):
        if target.startswith(("10.", "doi:", "https://doi.org/")):
            identifier = doi(target)
            if not identifier.lower().startswith("10.4230/"):
                raise ServiceError("source_boundary", "This DOI is not a DROPS identifier")
            entity = "https://drops.dagstuhl.de/entities/document/" + identifier
        elif target.startswith("https://"):
            parsed = urlsplit(target)
            if parsed.hostname not in self.hosts or not parsed.path.startswith("/entities/"):
                raise ServiceError("source_boundary", "Use a DROPS entity URL")
            entity = target.split("/metadata/")[0].rstrip("/")
        else:
            result = self.search(target, options={}, limit=20)
            result["status"] = "selection_required" if result["received"] else "not_found"
            return result
        raw, evidence = self.request(entity + "/metadata/schema-org")
        if not isinstance(raw, dict) or raw.get("url", "").rstrip("/").lower() != entity.lower():
            raise ServiceError("identity_mismatch", "DROPS metadata does not match the requested entity", evidence=evidence)
        result = self.fetched([raw], evidence, parts, ("metadata", "export") + (("abstract",) if raw.get("abstract") else ()))
        if "fulltext" in parts or "supplementary" in parts:
            page = self.gateway.public_page(self.source)
            goto_source(page, entity, self.hosts, wait_until="domcontentloaded", timeout=45000)
            source_page = self.store.put(clean_html(page.content(), self.store.sanitizer), "text/html", self.source, page.url, role="source_page", entity=entity)
            if "fulltext" in parts:
                links = page.locator('a[href$=".pdf"]').evaluate_all("es => es.map(e => e.href)")
                expected = entity.rsplit("/", 1)[-1] + ".pdf"
                links = list(dict.fromkeys(u for u in links if urlsplit(u).hostname in self.hosts and urlsplit(u).path.endswith("/" + expected)))
                if len(links) == 1:
                    data, media, url = browser_download(self.gateway.context, links[0], self.hosts)
                    if not data.startswith(b"%PDF-"):
                        raise ServiceError("unexpected_content", "DROPS returned no PDF", evidence=source_page)
                    import pymupdf
                    with pymupdf.open(stream=data, filetype="pdf") as doc:
                        pages = len(doc)
                    artifact = self.store.put(data, "application/pdf", self.source, url, role="fulltext", pages=pages, entity=entity)
                    result["components"]["fulltext"] = {"status": "available", "artifact": artifact}
                else:
                    result["components"]["fulltext"] = {"status": "not_implemented", "reason": "No unique entity-bound PDF link was found", "artifact": source_page}
            if "supplementary" in parts:
                result["components"]["supplementary"] = {"status": "source_page", "artifact": source_page, "reason": "Supplementary links are preserved; automatic attachment selection is pending"}
            result["source_page"] = source_page
        result["status"] = "ok" if all(c["status"] == "available" for c in result["components"].values()) else "partial"
        return result
