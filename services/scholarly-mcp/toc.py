"""Theory of Computing's native indexes, public search widget and document formats."""
import json
import re
from urllib.parse import quote, urljoin, urlsplit
from waits import SOURCE_WAIT_MS

from bs4 import BeautifulSoup

from browser_adapters import browser_download, clean_html, goto_source, require_source_url
from publishers import PROFILES, Publisher, publication_metadata
from scholarly import ServiceError, encoded, bibliography

ARTICLE = re.compile(r"/articles/((?:v\d+a\d+|gs\d+))/(?:index\.html)?$")
FORMATS = {"pdf": "application/pdf", "postscript": "application/postscript", "source_zip": "application/zip",
    "bibtex": "application/x-bibtex", "abstract_text": "text/plain", "references_html": "text/html", "authors_html": "text/html"}


def catalog_records(raw, base):
    soup = BeautifulSoup(raw, "html.parser")
    rows = []
    for link in soup.select(".tocline2 a[href]"):
        url = urljoin(base, link["href"])
        match = ARTICLE.fullmatch(urlsplit(url).path)
        if not match:
            continue
        cell = link.find_parent("td")
        listing = cell.get_text(" ", strip=True)
        year = re.search(r"\b(?:19|20)\d{2}\b", listing)
        rows.append({"id": match[1], "title": re.sub(r"\s+", " ", link.get_text("", strip=False)).strip(), "url": url,
            "year": year[0] if year else None, "authors": [a.get_text(" ", strip=True) for a in cell.select('a[href^="/authors/"]')], "listing": listing})
    return rows


def document_formats(raw, base):
    soup = BeautifulSoup(raw, "html.parser")
    result = {}
    directory = urljoin(base, "./")
    for link in soup.select("a[href]"):
        url = urljoin(base, link["href"])
        if not url.startswith(directory):
            continue
        path = urlsplit(url).path
        name = path.rsplit("/", 1)[-1]
        kind = {"bibtex.txt": "bibtex", "abstract.txt": "abstract_text", "bibliography.html": "references_html", "about.html": "authors_html", "source.zip": "source_zip"}.get(name)
        if kind is None:
            kind = "pdf" if path.endswith(".pdf") else "postscript" if path.endswith(".ps") else None
        if kind:
            result[kind] = {"url": url, "media_type": FORMATS[kind], "label": link.get_text(" ", strip=True)}
    return result


class TheoryOfComputing(Publisher):
    def __init__(self, store, gateway):
        super().__init__(store, gateway, next(p for p in PROFILES if p.source == "theory-of-computing"))

    def text_search(self, query, start, limit):
        if start + limit > 100:
            raise ServiceError("invalid_range", "The native search widget exposes at most its first 100 result positions")
        page = self.gateway.public_page(self.source)
        goto_source(page, "https://theoryofcomputing.org/search.html", self.profile.hosts, wait_until="domcontentloaded", timeout=SOURCE_WAIT_MS)
        found = re.search(r"CustomSearchControl\s*\(\s*['\"]([^'\"]+)", page.content())
        if not found:
            raise ServiceError("search_configuration_missing", "The journal did not publish its search engine configuration")
        # The journal's legacy HTTP loader is blocked on HTTPS. Reuse its engine with the current public widget.
        page.evaluate("() => { window._scholarlySearchRendered = 0; window.__gcse = {searchCallbacks:{web:{rendered:() => window._scholarlySearchRendered++}}}; const node = document.createElement('div'); node.className = 'gcse-search'; document.body.appendChild(node); }")
        page.add_script_tag(url="https://cse.google.com/cse.js?cx=" + quote(found[1], safe=""))
        field = page.locator("input.gsc-input")
        field.wait_for(timeout=SOURCE_WAIT_MS)
        field.fill(query)
        field.press("Enter")
        page.wait_for_function("window._scholarlySearchRendered > 0", timeout=SOURCE_WAIT_MS)
        if field.input_value() != query:
            raise ServiceError("query_mismatch", "The native search widget changed the submitted query")
        first_html = page.locator(".gsc-resultsbox-visible").inner_html()
        initial = self.store.put(clean_html(first_html, self.store.sanitizer), "text/html", self.source, page.url, role="native_search_page", query=query, page=1)
        rows, evidence, excluded = [], [initial], 0
        reported = page.locator(".gsc-result-info").all_inner_texts()
        first_size = page.locator(".gsc-webResult.gsc-result").count() or 10
        page_numbers = [int(value) for value in page.locator(".gsc-cursor-page").all_inner_texts() if value.isdigit()]
        last_page = max(page_numbers, default=1)
        for number in range(start // first_size + 1, min(last_page, (start + limit - 1) // first_size + 1) + 1):
            if number > 1:
                before = page.evaluate("window._scholarlySearchRendered")
                page.locator(".gsc-cursor-page").filter(has_text=re.compile("^" + str(number) + "$" )).click()
                page.wait_for_function("previous => window._scholarlySearchRendered > previous", arg=before, timeout=SOURCE_WAIT_MS)
                page.wait_for_function("n => [...document.querySelectorAll('.gsc-cursor-current-page')].some(e => e.textContent.trim() === String(n))", arg=number)
            require_source_url(page.url, self.profile.hosts)
            html = page.locator(".gsc-resultsbox-visible").inner_html()
            if number > 1:
                evidence.append(self.store.put(clean_html(html, self.store.sanitizer), "text/html", self.source, page.url, role="native_search_page", query=query, page=number))
            cards = BeautifulSoup(html, "html.parser").select(".gsc-webResult.gsc-result")
            for index, card in enumerate(cards, (number - 1) * first_size):
                if not start <= index < start + limit:
                    continue
                link = card.select_one("a.gs-title")
                if link is None or not link.get("href"):
                    continue
                url = link["href"]
                if urlsplit(url).hostname not in self.profile.hosts:
                    excluded += 1
                    continue
                identifier = re.search(r"/articles/(v\d+a\d+|gs\d+)/", urlsplit(url).path)
                snippet = card.select_one(".gs-snippet")
                rows.append({"id": identifier[1] if identifier else None, "title": link.get_text(" ", strip=True), "url": url,
                    "snippet": snippet.get_text(" ", strip=True) if snippet else None, "result_kind": "source_web_page"})
        more = (start + limit) < last_page * first_size
        return rows, None, evidence, {"reported_total": reported, "reported_total_is_approximate": True,
            "excluded_external_results": excluded, "has_more": more, "native_result_limit": 100}

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ServiceError("invalid_range", "Use start >= 0 and limit 1..1000")
        field = options.get("field", "text")
        if set(options) - {"field"} or field not in ("text", "author", "category") or cursor or export not in (None, "json", "html", "bibtex"):
            raise ServiceError("invalid_options", "field is text/author/category; export is json/html/bibtex; use start/limit")
        details, status = {}, None
        if field == "text":
            rows, total, evidence, details = self.text_search(query, start, limit)
        else:
            page = self.gateway.public_page(self.source)
            section = "authors" if field == "author" else "categories"
            goto_source(page, "https://theoryofcomputing.org/" + section + "/index.html", self.profile.hosts, wait_until="domcontentloaded", timeout=SOURCE_WAIT_MS)
            soup = BeautifulSoup(page.content(), "html.parser")
            choices = [{"label": re.sub(r"\s*\(\d+\)\s*$", "", a.get_text(" ", strip=True)), "url": urljoin(page.url, a["href"])}
                for a in soup.select('a[href^="/' + section + '/"]') if not a["href"].endswith("/index.html")]
            matches = [r for r in choices if r["label"].casefold() == query.casefold()] or [r for r in choices if query.casefold() in r["label"].casefold()]
            if len(matches) != 1:
                rows, total, status = matches[start:start + limit], len(matches), "selection_required" if matches else "not_found"
            else:
                goto_source(page, matches[0]["url"], self.profile.hosts, wait_until="domcontentloaded", timeout=SOURCE_WAIT_MS)
                native = catalog_records(page.content(), page.url)
                rows, total = native[start:start + limit], len(native)
            evidence = [self.store.put(clean_html(page.content(), self.store.sanitizer), "text/html", self.source, page.url, role="native_index", field=field, query=query)]
        artifact = self.store.put(encoded(rows), "application/json", self.source, evidence[0]["url"] if evidence else "https://theoryofcomputing.org/search.html", role="records", query=query, options=options, start=start, requested=limit, total=total)
        exported, missing = artifact, []
        if export == "html":
            exported = {"artifacts": evidence}
        elif export == "bibtex" and rows and status != "selection_required":
            citations = []
            for row in rows:
                if not row.get("id"):
                    missing.append(row.get("url"))
                    continue
                result = self.fetch(row["id"], parts=["export"])
                component = result["components"]["export"]
                if component["status"] == "available":
                    citations.append(component["artifact"])
                else:
                    missing.append(row["id"])
            exported = {"artifacts": citations, "without_native_citation": missing}
        more = details.get("has_more", start + len(rows) < total if total is not None else False)
        return {"status": status or ("partial" if missing or details.get("excluded_external_results") else "ok" if rows else "not_found"),
            "source": self.source, "query": query, "options": options, "start": start, "requested": limit, "received": len(rows),
            "total": total, "has_more": more, "next": {"start": start + limit} if more else None, "records": artifact, "export": exported,
            "evidence": evidence, "preview": [{k: row.get(k) for k in ("id", "title", "label", "url")} for row in rows[:3]], **details}

    def fetch(self, target, *, parts):
        if set(parts) - {"metadata", "abstract", "fulltext", "supplementary", "export"}:
            raise ServiceError("invalid_parts", "Unknown requested content")
        if re.fullmatch(r"v\d+a\d+|gs\d+", target):
            target = "https://theoryofcomputing.org/articles/" + target + "/"
        elif not target.startswith(("http://", "https://", "10.", "doi:")):
            result = self.search(target, options={}, limit=20)
            result["status"] = "selection_required" if result["received"] else "not_found"
            return result
        url, requested_doi = self.resolve_target(target)
        direct_file = re.fullmatch(r"/articles/(v\d+a\d+|gs\d+)/([^/]+)", urlsplit(url).path)
        direct_file = direct_file if direct_file and direct_file[2] != "index.html" else None
        entry_url = urljoin(url, "./") if direct_file else url
        page = self.gateway.public_page(self.source)
        response = goto_source(page, entry_url, self.profile.hosts, wait_until="domcontentloaded", timeout=SOURCE_WAIT_MS)
        if response and response.status >= 400:
            raise ServiceError("not_found_at_source" if response.status == 404 else "provider_error", "Theory of Computing did not return this page", status="not_found" if response.status == 404 else "error", http_status=response.status)
        raw = page.content()
        metadata = publication_metadata(raw)
        source_page = self.store.put(clean_html(raw, self.store.sanitizer), "text/html", self.source, page.url, role="source_page", target=target)
        record = {"title": (metadata.get("citation_title") or [page.title()])[0], "metadata": metadata, "url": page.url,
            "content_kind": "article" if metadata.get("citation_title") else "web_page"}
        if requested_doi and requested_doi.lower() not in {d.lower() for d in metadata.get("citation_doi", [])}:
            raise ServiceError("identity_mismatch", "Theory of Computing page does not match the requested DOI", evidence=source_page)
        artifact = self.store.put(encoded([record]), "application/json", self.source, page.url, role="records", target=target)
        formats = document_formats(raw, page.url)
        selected_format = None
        if direct_file:
            selected_format = next((kind for kind, item in formats.items() if (urlsplit(item["url"]).path, urlsplit(item["url"]).query) == (urlsplit(url).path, urlsplit(url).query)), None)
            if selected_format is None:
                raise ServiceError("file_variant_not_implemented", "This file variant is not linked by the current article page; no other version was substituted", status="not_implemented", evidence=source_page)

        def obtain(kind):
            link = formats[kind]
            data, _, obtained = browser_download(self.gateway.context, link["url"], self.profile.hosts)
            extra = {"role": kind, "target": target}
            if kind == "pdf":
                if not data.startswith(b"%PDF-"):
                    raise ServiceError("unexpected_content", "Theory of Computing PDF link returned no PDF")
                import pymupdf
                with pymupdf.open(stream=data, filetype="pdf") as document:
                    extra["pages"] = len(document)
            elif kind == "bibtex":
                citations = bibliography(data, FORMATS[kind])
                if len(citations) != 1 or citations[0].get("doi", "").lower() not in {d.lower() for d in metadata.get("citation_doi", [])}:
                    raise ServiceError("identity_mismatch", "Native BibTeX does not match the article DOI")
            return self.store.put(data, link["media_type"], self.source, obtained, **extra)

        components = {}
        for part in parts:
            try:
                if part == "metadata":
                    components[part] = {"status": "available", "artifact": artifact}
                elif part == "fulltext" and record["content_kind"] == "web_page":
                    components[part] = {"status": "available", "artifact": source_page, "content_kind": "web_page"}
                elif part == "supplementary":
                    items = [{"format": kind, "artifact": obtain(kind)} for kind in ("source_zip", "postscript", "references_html", "authors_html") if kind in formats]
                    components[part] = {"status": "available" if items else "not_offered", "artifacts": items}
                else:
                    kind = {"abstract": "abstract_text", "fulltext": selected_format or "pdf", "export": "bibtex"}[part]
                    components[part] = {"status": "available", "artifact": obtain(kind), "content_kind": kind} if kind in formats else {"status": "not_offered", "reason": "This source page does not link the requested format", "artifact": source_page}
            except ServiceError as error:
                components[part] = error.result
        return {"status": "ok" if all(c["status"] == "available" for c in components.values()) else "partial", "source": self.source,
            "target": target, "target_kind": selected_format or record["content_kind"], "records": artifact, "source_page": source_page, "components": components, "available_formats": list(formats)}
