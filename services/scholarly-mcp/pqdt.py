"""ProQuest dissertations through its institutional browser UI and native RIS export."""
import json
import re
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from browser_adapters import browser_download, clean_html, goto_source, require_source_url
from scholarly import ServiceError, encoded, extract_artifact


def pqdt_records(raw, base):
    soup = BeautifulSoup(raw, "html.parser")
    heading = soup.select_one("#pqResultsCount")
    match = re.search(r"([\d,]+)\s+results?", heading.get_text(" ", strip=True) if heading else "", re.I)
    if not match:
        raise ServiceError("invalid_response", "PQDT page contains no recognized result count")
    rows = []
    for item in soup.select("li.resultItem"):
        title = next((a for a in item.select("a.previewTitle") if a.get_text(strip=True)), None)
        found = re.search(r"/docview/(\d+)", title.get("href", "") if title else "")
        if not found:
            raise ServiceError("invalid_response", "PQDT result contains no document-bound title link")
        links = [urljoin(base, e["href"]) for e in item.select('a[href*="/fulltextPDF/"]') if "/docview/" + found[1] + "/" in e["href"]]
        rows.append({"id": found[1], "title": title.get_text(" ", strip=True), "url": urljoin(base, title["href"]),
            "pdf_page": links[0] if links else None, "listing": item.get_text("\n", strip=True)})
    return rows, int(match[1].replace(",", ""))


class PQDT:
    source = "pqdt"
    hosts = ("www.proquest.com", "www-proquest-com.libproxy.knu.ac.kr")
    media_hosts = hosts + ("media.proquest.com", "media-proquest-com.libproxy.knu.ac.kr")

    def __init__(self, store, gateway):
        self.store, self.gateway = store, gateway
        self.known = {}

    def page(self):
        page = self.gateway.open(self.source, "PQDT", self.hosts, "#searchTerm, #pqResultsCount")
        page.wait_for_load_state("load", timeout=45000)
        page.wait_for_function("typeof OneTrust !== 'undefined' && typeof OneTrust.RejectAll === 'function'", timeout=30000)
        if not page.evaluate("document.cookie.includes('OptanonAlertBoxClosed=')"):
            page.locator("#onetrust-banner-sdk").wait_for(timeout=30000)
            page.evaluate("OneTrust.RejectAll()")
            page.locator(".onetrust-pc-dark-filter").wait_for(state="hidden", timeout=20000)
        return page

    def citation(self, page):
        previous = set(self.gateway.context.pages)
        page.locator("#allSaveOptionsLink").click()
        page.locator("#allSaveOptionsOverlay").wait_for()
        page.locator('a[href*="selectformat/ProEndRefMgr"]').filter(visible=True).first.click()
        button = page.locator('#saveasExportLayerOverlay a[id^="submitButton_"]')
        button.wait_for(timeout=30000)
        with self.gateway.context.expect_event("response", predicate=lambda r: "research-info-systems" in r.headers.get("content-type", "").lower(), timeout=60000) as pending:
            button.click()
        response = pending.value
        if urlsplit(response.url).hostname not in self.hosts or response.status != 200:
            raise ServiceError("export_source_mismatch", "PQDT export did not return a successful response from its own service")
        data = response.body()
        if not data.lstrip().startswith(b"TY  -"):
            raise ServiceError("unexpected_content", "PQDT export response is not RIS")
        native = self.store.put(data, "application/x-research-info-systems", self.source, response.url, role="native_citation_export")
        for popup in set(self.gateway.context.pages) - previous:
            popup.close()
        rows = extract_artifact(self.store, native["ref"], count=1000)["items"]
        for row in rows:
            fields = row["fields"]
            row.update(id=(fields.get("an") or [None])[0], title=(fields.get("t1") or [None])[0])
        return rows, native

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ServiceError("invalid_range", "PQDT requires start >= 0 and limit 1..1000")
        if options or cursor or export not in (None, "json", "ris", "html"):
            raise ServiceError("invalid_options", "Use the native query and start/limit; export is json/ris/html")
        page = self.page()
        # Marked items persist across searches. Clear only this server's browser selection.
        clear = page.locator("#selecteditemsclear_link")
        if clear.count() and clear.is_visible():
            clear.click()
            dialog = page.locator("#selecteditemsclear_confirm_clear_overlay")
            if dialog.is_visible():
                dialog.get_by_role("button", name="Yes", exact=True).click()
        if not page.locator("#searchTerm").count():
            goto_source(page, "https://" + urlsplit(page.url).hostname + "/pqdtglobal", self.hosts, wait_until="load", timeout=45000)
        page.locator("#searchTerm").fill(query)
        page.locator("#searchTerm").press("Tab")
        with page.expect_navigation(wait_until="load", timeout=60000):
            page.locator("#expandedSearch").click()
        page.locator("#pqResultsCount").wait_for(timeout=60000)
        rows, evidence, offset, total = [], [], 0, None
        while True:
            require_source_url(page.url, self.hosts)
            raw = page.content()
            native, observed = pqdt_records(raw, page.url)
            if total is not None and observed != total:
                raise ServiceError("range_mismatch", "PQDT result count changed during pagination")
            total = observed
            evidence.append(self.store.put(clean_html(raw, self.store.sanitizer), "text/html", self.source, page.url, role="search_page", query=query, offset=offset, total=total))
            for i, row in enumerate(native):
                if start <= offset + i < start + limit:
                    control = page.locator("li.resultItem").nth(i).locator('input.marked_list_checkbox')
                    if not control.is_checked():
                        control.focus()
                        control.press("Space")
                        page.wait_for_function("e => e.checked", arg=control.element_handle())
                    rows.append(row)
            offset += len(native)
            if offset >= min(total, start + limit) or not native:
                break
            next_page = page.locator('a[title="Next page"],a[aria-label="Next page"],a[title="Next"],a[rel="next"]').filter(visible=True)
            if not next_page.count():
                raise ServiceError("pagination_control_missing", "PQDT next-page control could not be identified", evidence=evidence)
            with page.expect_navigation(wait_until="load", timeout=60000):
                next_page.first.click()
        citations, exported = ([], None)
        if rows:
            citations, exported = self.citation(page)
            if {row["id"] for row in rows} != {row["id"] for row in citations} or len(rows) != len(citations):
                raise ServiceError("export_identity_mismatch", "PQDT RIS records do not match the selected documents", evidence=exported)
            by_id = {row["id"]: row for row in citations}
            for row in rows:
                row.update(bibliography=by_id[row["id"]])
                self.known[row["id"]] = (row, exported)
        artifact = self.store.put(encoded(rows), "application/json", self.source, page.url, role="records", query=query, start=start, requested=limit, total=total)
        more = start + len(rows) < total
        return {"status": "ok" if rows else "not_found", "source": self.source, "query": query, "start": start,
            "requested": limit, "received": len(rows), "total": total, "has_more": more,
            "next": {"start": start + len(rows)} if more else None, "records": artifact,
            "export": exported if export == "ris" else {"artifacts": evidence} if export == "html" else artifact,
            "native_citation": exported, "evidence": evidence, "preview": [{k: r[k] for k in ("id", "title")} for r in rows[:3]]}

    def fetch(self, target, *, parts):
        if set(parts) - {"metadata", "abstract", "fulltext", "supplementary", "export"}:
            raise ServiceError("invalid_parts", "Unknown requested content")
        if target.isdigit():
            identifier = target
        elif target.startswith(("http://", "https://")):
            parsed = urlsplit(target)
            found = re.search(r"/docview/(\d+)", parsed.path)
            if parsed.hostname not in self.hosts or not found:
                raise ServiceError("source_boundary", "Use a PQDT docview identifier or document URL")
            identifier = found[1]
        else:
            result = self.search('TI("' + target.replace('"', " ") + '")', options={}, limit=20)
            result["status"] = "selection_required" if result["received"] else "not_found"
            return result
        page = self.page()
        if identifier not in self.known:
            goto_source(page, "https://" + urlsplit(page.url).hostname + "/pqdtglobal/docview/" + identifier, self.hosts, wait_until="domcontentloaded", timeout=45000)
            records, native = self.citation(page)
            if len(records) != 1 or records[0]["id"] != identifier:
                raise ServiceError("identity_mismatch", "PQDT document export did not match the target", evidence=native)
            record = {"id": identifier, "title": records[0]["title"], "bibliography": records[0], "url": page.url}
            self.known[identifier] = (record, native)
        record, native = self.known[identifier]
        artifact = self.store.put(encoded([record]), "application/json", self.source, record["url"], role="records", target=identifier)
        components = {}
        for part in parts:
            if part in ("metadata", "export"):
                components[part] = {"status": "available", "artifact": native if part == "export" else artifact}
            elif part == "abstract":
                components[part] = {"status": "available", "artifact": artifact} if record["bibliography"]["fields"].get("ab") else {"status": "not_found", "reason": "Native RIS has no abstract"}
            elif part == "fulltext":
                goto_source(page, "https://" + urlsplit(page.url).hostname + "/pqdtglobal/docview/" + identifier + "/fulltextPDF", self.hosts, wait_until="domcontentloaded", timeout=45000)
                download = page.locator("#downloadPDFLink_MSTAR_" + identifier)
                try:
                    download.wait_for(timeout=30000)
                    url = urljoin(page.url, download.get_attribute("href"))
                    data, _, obtained = browser_download(self.gateway.context, url, self.media_hosts)
                    if not data.startswith(b"%PDF-"):
                        raise ServiceError("unexpected_content", "PQDT document control did not return a PDF")
                    import pymupdf
                    with pymupdf.open(stream=data, filetype="pdf") as pdf:
                        pages = len(pdf)
                    fulltext = self.store.put(data, "application/pdf", self.source, obtained, role="fulltext", pages=pages, target=identifier)
                    components[part] = {"status": "available", "artifact": fulltext}
                except ServiceError as error:
                    components[part] = error.result
            else:
                components[part] = {"status": "not_implemented", "reason": "Separate supplementary file retrieval is pending"}
        return {"status": "ok" if all(v["status"] == "available" for v in components.values()) else "partial", "source": self.source,
            "target": identifier, "records": artifact, "native_citation": native, "components": components}
