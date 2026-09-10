"""IEEE Xplore Command Search and native exports through KUDOS."""
import json
import re
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from browser_adapters import browser_download, dismiss_cookies, goto_source
from scholarly import ServiceError, encoded


def ieee_records(raw):
    rows, total, offset = raw.get("records"), raw.get("totalRecords"), raw.get("startRecord")
    if not isinstance(rows, list) or type(total) is not int or type(offset) is not int:
        raise ServiceError("invalid_response", "IEEE response has no document range")
    if not all(isinstance(row, dict) and row.get("articleNumber") for row in rows) or raw.get("endRecord") != offset + len(rows):
        raise ServiceError("invalid_response", "IEEE document identities or range do not match the response")
    return rows, total, offset


def reference_records(payload,identifier):
    rows=payload.get('references')
    if str(payload.get('articleNumber'))!=identifier:
        raise ServiceError('identity_mismatch','IEEE reference response belongs to a different document')
    if not isinstance(rows,list) or any(not isinstance(row,dict) for row in rows):
        raise ServiceError('invalid_response','IEEE returned no native reference array')
    return rows


class IEEE:
    source = "ieee-xplore"
    hosts = ("ieeexplore.ieee.org", "ieeexplore-ieee-org.libproxy.knu.ac.kr")
    formats = {"bibtex": ("bibtex", "application/x-bibtex"), "ris": ("ris", "application/x-research-info-systems"), "plain": ("ascii", "text/plain"), "csv": (None, "text/csv")}

    def __init__(self, store, gateway):
        self.store, self.gateway = store, gateway
        self.known = {}

    def page(self):
        return self.gateway.open(self.source, "IEEE", self.hosts, "body")

    def references(self,identifier,base):
        page=self.page()
        goto_source(page,urljoin(base,'/document/'+identifier+'/'),self.hosts,wait_until='domcontentloaded',timeout=45000)
        page.locator('h1.document-title').wait_for(timeout=30000)
        dismiss_cookies(page)
        path='/rest/document/'+identifier+'/references'
        with page.expect_response(lambda r:urlsplit(r.url).hostname in self.hosts and urlsplit(r.url).path==path,timeout=45000) as pending:
            page.locator('a.document-tab-link').filter(has_text=re.compile(r'^References$')).filter(visible=True).first.click()
        response=pending.value
        if response.status in (401,403):
            raise ServiceError('access_restricted','IEEE restricted the reference request',status='restricted')
        if response.status!=200:
            raise ServiceError('provider_error','IEEE reference request failed',http_status=response.status)
        payload=response.json()
        rows=reference_records(payload,identifier)
        document={key:payload[key] for key in ('articleNumber','title','publicationNumber','publisher','contentType','references') if key in payload}
        proof=self.store.put(encoded(document),'application/json',self.source,response.url,role='native_reference_response',article_number=identifier)
        artifact=self.store.put(encoded(rows),'application/json',self.source,response.url,role='reference_records',article_number=identifier,evidence_ref=proof['ref'])
        return {'status':'available' if rows else 'not_found','artifact':artifact,'count':len(rows),'evidence':proof,
                'scope':'Native reference array for this article; citation links are preserved and not followed'}

    def citation(self, page, indices, format):
        controls = page.get_by_role("checkbox", name="Select search result", exact=True)
        for i in range(controls.count()):
            controls.nth(i).set_checked(i in indices)
        page.get_by_role("button", name="Export", exact=True).click()
        native, media = self.formats[format]
        if native:
            page.get_by_role("tab", name="Citations", exact=True).click()
            page.locator('label[for="download-' + native + '"] input').check()
            page.locator('label[for="citation-abstract"] input').check()
        with page.expect_download(timeout=45000) as pending:
            page.get_by_role("button", name="Download", exact=True).click()
        download = pending.value
        from pathlib import Path
        data = Path(download.path()).read_bytes()
        if not data or data.lstrip().lower().startswith((b"<!doctype", b"<html")):
            raise ServiceError("unexpected_content", "IEEE native citation export returned no bibliographic file")
        return self.store.put(data, media, self.source, page.url, role="native_citation_export", format=format, count=len(indices))

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ServiceError("invalid_range", "IEEE requires start >= 0 and limit 1..1000")
        if options or cursor or export not in (None, "json", *self.formats):
            raise ServiceError("invalid_options", "Use Command Search syntax; options must be empty; export supports json/bibtex/ris/plain/csv")
        page = self.page()
        dismiss_cookies(page)
        goto_source(page, "https://" + urlsplit(page.url).hostname + "/search/advanced/command", self.hosts, wait_until="domcontentloaded", timeout=45000)
        page.locator("#cmdTextArea").wait_for(timeout=45000)
        dismiss_cookies(page)
        page.locator("#cmdTextArea").fill(query)

        def matches(response):
            if urlsplit(response.url).hostname not in self.hosts or urlsplit(response.url).path != "/rest/search" or response.request.method != "POST":
                return False
            try:
                return response.request.post_data_json.get("queryText") in (query, "(" + query + ")")
            except Exception:
                return False

        with page.expect_response(matches, timeout=60000) as pending:
            page.locator(".stats-Adv_Command_search").click()
        response = pending.value
        rows, evidence, exports, total, offset = [], [], [], None, 0
        while True:
            if response.status in (401, 403):
                raise ServiceError("access_restricted", "IEEE restricted this institutional search", status="restricted")
            if response.status != 200:
                raise ServiceError("provider_error", "IEEE search failed", http_status=response.status)
            raw = response.json()
            native, observed, position = ieee_records(raw)
            if position != offset or total is not None and observed != total:
                raise ServiceError("range_mismatch", "IEEE returned a different document range")
            total = observed
            # Session/account information is not bibliographic evidence. Preserve all search data.
            raw.pop("userInfo", None)
            evidence.append(self.store.put(encoded(raw), "application/json", self.source, response.url, role="search_response", query=query, offset=offset, total=total))
            indices = [i for i in range(len(native)) if start <= offset + i < start + limit]
            selected = [native[i] for i in indices]
            rows.extend(selected)
            self.known.update({row["articleNumber"]: (row, page.url) for row in selected})
            if indices and export in self.formats:
                page.get_by_role("checkbox", name="Select search result", exact=True).first.wait_for(timeout=30000)
                exports.append(self.citation(page, indices, export))
            offset += len(native)
            if offset >= min(total, start + limit) or not native:
                break
            next_page = page.locator('a[aria-label="Next Page"],button[aria-label="Next Page"],a[title="Next Page"],button[aria-label="Next page"],a[aria-label="Next page"]')
            if not next_page.count():
                raise ServiceError("pagination_control_missing", "IEEE next-page control could not be identified", evidence=evidence)
            with page.expect_response(matches, timeout=60000) as pending:
                next_page.filter(visible=True).first.click()
            response = pending.value
        artifact = self.store.put(encoded(rows), "application/json", self.source, page.url, role="records", query=query, start=start, requested=limit, total=total)
        more = start + len(rows) < total
        return {"status": "ok" if rows else "not_found", "source": self.source, "query": query, "start": start,
            "requested": limit, "received": len(rows), "total": total, "has_more": more,
            "next": {"start": start + len(rows)} if more else None, "records": artifact,
            "export": exports[0] if len(exports) == 1 else {"artifacts": exports} if exports else artifact,
            "evidence": evidence, "preview": [{k: row.get(k) for k in ("articleNumber", "articleTitle", "publicationYear", "doi")} for row in rows[:3]]}

    def fetch(self, target, *, parts):
        from api_adapters import doi
        if set(parts) - {"metadata", "abstract", "fulltext", "supplementary", "export"}:
            raise ServiceError("invalid_parts", "Unknown requested content")
        value = target
        if target.startswith(("http://", "https://")) and urlsplit(target).hostname not in (*self.hosts, "doi.org", "dx.doi.org"):
            raise ServiceError("source_boundary", "Use an IEEE document URL or DOI")
        if target.startswith(("http://", "https://")) and urlsplit(target).hostname in self.hosts:
            found = re.fullmatch(r"/document/(\d+)/?", urlsplit(target).path)
            if not found:
                raise ServiceError("invalid_target", "Use an IEEE document URL")
            value = found[1]
        if value.isdigit():
            identifier, query = value, '"Article Number":' + value
        else:
            identifier = None
            try:
                query = '"DOI":"' + doi(value) + '"'
            except ServiceError:
                result = self.search('"Document Title":"' + value.replace('"', " ") + '"', options={}, limit=20)
                result["status"] = "selection_required" if result["received"] else "not_found"
                return result
        if identifier not in self.known:
            result = self.search(query, options={}, limit=2)
            if result["total"] != 1:
                result["status"] = "selection_required" if result["received"] else "not_found"
                return result
            identifier = json.loads(self.store.read(result["records"]["ref"])[1])[0]["articleNumber"]
        row, base = self.known[identifier]
        artifact = self.store.put(encoded([row]), "application/json", self.source, urljoin(base, row["documentLink"]), role="records", target=identifier)
        components = {}
        for part in parts:
            if part in ("metadata", "export"):
                components[part] = {"status": "available", "artifact": artifact, "format": "json"}
            elif part == "abstract":
                components[part] = {"status": "available", "artifact": artifact} if row.get("abstract") else {"status": "not_found", "reason": "IEEE record has no abstract"}
            elif part == "fulltext":
                if not row.get("pdfLink"):
                    components[part] = {"status": "not_implemented", "reason": "This record has no PDF link; HTML-only retrieval is pending"}
                    continue
                try:
                    data, media, url = browser_download(self.gateway.context, urljoin(base, row["pdfLink"]), self.hosts)
                    if not data.startswith(b"%PDF-"):
                        soup = BeautifulSoup(data, "html.parser")
                        frames = soup.select('iframe[src*="/stampPDF/getPDF.jsp"]')
                        if len(frames) != 1:
                            raise ServiceError("unexpected_content", "IEEE PDF viewer did not identify its document file")
                        data, media, url = browser_download(self.gateway.context, urljoin(url, frames[0]["src"]), self.hosts)
                    if not data.startswith(b"%PDF-"):
                        raise ServiceError("unexpected_content", "IEEE document endpoint returned no PDF")
                    import pymupdf
                    with pymupdf.open(stream=data, filetype="pdf") as pdf:
                        pages = len(pdf)
                    fulltext = self.store.put(data, "application/pdf", self.source, url, role="fulltext", target=identifier, pages=pages)
                    components[part] = {"status": "available", "artifact": fulltext}
                except ServiceError as error:
                    components[part] = error.result
            else:
                from ieee_media import fetch_media
                details={}
                for name,operation in [('references',lambda:self.references(identifier,base)),('attachments',lambda:fetch_media(self,identifier,base))]:
                    try: details[name]=operation()
                    except ServiceError as error: details[name]=error.result
                    except Exception as error: details[name]={'status':'error','code':name+'_retrieval_failed','error_type':type(error).__name__}
                clean=all(item['status'] in ('available','not_found','not_offered') for item in details.values())
                components[part]={'status':'available' if clean and any(item['status']=='available' for item in details.values()) else 'not_found' if clean else 'partial',**details}
                if details['references'].get('artifact'): components[part]['artifact']=details['references']['artifact']
        return {"status": "ok" if all(v["status"] == "available" for v in components.values()) else "partial", "source": self.source,
            "target": identifier, "records": artifact, "components": components}
