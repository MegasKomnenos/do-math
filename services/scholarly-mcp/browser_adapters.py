"""Observed browser workflows, including KUDOS's academic database gateway."""
from __future__ import annotations

import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit, urlunsplit, quote, unquote

from bs4 import BeautifulSoup

from scholarly import ServiceError, encoded, bibliography

MSC_HOSTS = {"mathscinet.ams.org", "mathscinet-ams-org.libproxy.knu.ac.kr"}


def require_source_url(url, hosts):
    parsed = urlsplit(url)
    if parsed.scheme not in ("https", "http") or parsed.hostname not in hosts or parsed.username or parsed.password or parsed.port not in (None, 80, 443):
        raise ServiceError("source_boundary", "Document navigation left the named source")


def goto_source(page, url, hosts, **kwargs):
    require_source_url(url, hosts)
    response = page.goto(url, **kwargs)
    require_source_url(page.url, hosts)
    return response


def clean_html(raw, sanitizer):
    soup = BeautifulSoup(raw, "html.parser")
    for tag in list(soup.find_all(["script", "input", "form", "iframe", "object", "embed", "button"])):
        if tag.name == "script" and str(tag.get("type", "")).startswith("math/tex") and not tag.has_attr("src"):
            continue
        if tag.name in ("form", "button"):
            tag.unwrap()
        else:
            tag.decompose()
    for tag in soup.find_all(True):
        for key in list(tag.attrs):
            if key.lower().startswith(("on", "data-", "wire:")) or sanitizer.sensitive.search(key):
                del tag.attrs[key]
            elif key in ("href", "src"):
                value = tag.get(key, "")
                if value.lower().startswith(("javascript:", "data:text/html")):
                    del tag.attrs[key]
                elif not value.startswith("data:"):
                    tag[key] = sanitizer.url(value)
    return sanitizer.text(str(soup))


def mathscinet_record(raw, base, sanitizer):
    html = clean_html(raw, sanitizer)
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.select_one('[id^="publication-"]')
    if heading is None:
        raise ServiceError("invalid_response", "MathSciNet result has no publication identity")
    anchors = heading.select('a[href*="article?mr="]')
    if len(anchors) < 2:
        raise ServiceError("invalid_response", "MathSciNet result has no title link")
    mr = re.search(r"mr=([0-9]+)", anchors[0]["href"]).group(1)
    return {"id": "MR" + mr, "title": anchors[1].get_text("", strip=True),
        "url": sanitizer.url(urljoin(base, anchors[0]["href"])), "text": soup.get_text("\n", strip=True),
        "html": html, "links": [{"label": a.get_text(" ", strip=True), "url": sanitizer.url(urljoin(base, a["href"]))} for a in soup.select("a[href]")]}


def mathscinet_target(target):
    if target.startswith(("http://", "https://")):
        parsed = urlsplit(target)
        if parsed.hostname not in MSC_HOSTS:
            raise ServiceError("source_boundary", "The target is outside MathSciNet")
        target = parse_qs(parsed.query).get("mr", [""])[0]
    target = re.sub(r"^MR", "", target, flags=re.I)
    if not re.fullmatch(r"[0-9]{1,8}", target):
        raise ServiceError("invalid_target", "Use an MR number or a MathSciNet article link")
    return target


def wos_events(raw):
    events = [json.loads(line) for line in raw.splitlines() if line.strip()]
    info = next((e["payload"] for e in events if e.get("key") == "searchInfo"), None)
    if info is None or type(info.get("RecordsFound")) is not int:
        raise ServiceError("invalid_response", "WOS search stream has no result count")
    records = {}
    for event in events:
        if event.get("key") == "records":
            records.update(event["payload"])
    return {"total": info["RecordsFound"], "available": info.get("RecordsAvailable"),
        "records": [records[k] for k in sorted(records, key=int)], "events": events}


def eccc_records(raw):
    soup = BeautifulSoup(raw, "html.parser")
    records = []
    for box in soup.select("div#box"):
        title = box.select_one("h4")
        link = title.find_parent("a") if title else None
        if not link or not re.fullmatch(r"/report/[0-9]{4}/[0-9]+/?", link.get("href", "")):
            continue
        identity = re.search(r"TR[0-9]{2}-[0-9]{3}", box.get_text(" "))
        records.append({"id": identity.group() if identity else None, "title": title.get_text(" ", strip=True),
            "url": urljoin("https://eccc.weizmann.ac.il/", link["href"]),
            "listing": box.get_text("\n", strip=True), "snippet": "\n".join(p.get_text(" ", strip=True) for p in box.find_all("p"))})
    return records


def eccc_versions(raw):
    soup = BeautifulSoup(raw, "html.parser")
    versions = []
    for box in soup.select("div#box"):
        heading = box.select_one("h4")
        pdf = box.select_one('a[href$="/download"]')
        if not heading or not pdf:
            continue
        link = urljoin("https://eccc.weizmann.ac.il/", pdf["href"])
        revision = re.search(r"/revision/([0-9]+)/download$", link)
        header = heading.parent.get_text(" ", strip=True)
        report = re.search(r"TR[0-9]{2}-[0-9]{3}", header)
        versions.append({"id": report.group() if report else None, "revision": int(revision.group(1)) if revision else 0,
            "title": heading.get_text(" ", strip=True), "version_label": header, "pdf": link,
            "authors": [a.get_text(" ", strip=True) for a in box.select('a[href^="/author/"]')],
            "abstract": "\n\n".join(p.get_text("", strip=False) for p in box.find_all("p", recursive=False))})
    return versions


def acm_records(raw, base):
    soup = BeautifulSoup(raw, "html.parser")
    rows = []
    for item in soup.select("li.search__item"):
        title = item.select_one('.hlFld-Title a[href^="/doi/"]')
        if title is None:
            continue
        identifier = title["href"].split("/doi/", 1)[1]
        rows.append({"id": identifier, "doi": identifier,
            "title": re.sub(r"\s+", " ", title.get_text("", strip=False)).strip(), "url": urljoin(base, title["href"]),
            "listing": item.get_text("\n", strip=True),
            "snippet": "\n".join(p.get_text("", strip=False) for p in item.select(".issue-item__abstract"))})
    return rows


def browser_download(context, url, hosts, *, headers=None, form=None, response_info=None):
    from playwright.sync_api import TimeoutError as BrowserTimeout, Error as BrowserError
    for _ in range(6):
        parsed = urlsplit(url)
        if parsed.hostname in {'validate.perfdrive.com','challenges.cloudflare.com'}:
            raise ServiceError('publisher_access_challenge','Publisher redirected the file request to an access challenge',status='restricted',blocked_host=parsed.hostname)
        if parsed.scheme not in ("https", "http") or parsed.hostname not in hosts or parsed.username or parsed.password or parsed.port not in (None, 80, 443):
            raise ServiceError("source_boundary", "Observed document link left the selected source", blocked_host=parsed.hostname)
        try:
            if form is None:
                response = context.request.get(url, max_redirects=0, timeout=45000, headers=headers or {})
            else:
                response = context.request.post(url, data=urlencode(form,doseq=True), max_redirects=0, timeout=45000,
                    headers={**(headers or {}),'Content-Type':'application/x-www-form-urlencoded'})
        except BrowserTimeout:
            raise ServiceError("timeout", "Source document did not respond within the download timeout", retryable=True) from None
        except BrowserError:
            raise ServiceError("connection_error", "Source document connection failed", retryable=True) from None
        if response.status in (301, 302, 303, 307, 308):
            url = urljoin(url, response.headers.get("location", ""))
            if response.status in (301,302,303):
                form = None
            continue
        if response.status in (401, 403):
            raise ServiceError("access_restricted", "Source restricted this document", status="restricted", http_status=response.status)
        if response.status == 429:
            raise ServiceError("rate_limited", "Source request limit reached", retry_after=response.headers.get("retry-after"))
        if response.status in (404, 410):
            raise ServiceError("not_found_at_source", "Document not found at this source", status="not_found")
        if response.status >= 400:
            raise ServiceError("provider_error", "Document download failed", http_status=response.status)
        if response_info is not None:
            response_info.update(status=response.status, **{key:response.headers[key] for key in
                ('content-range','content-length','content-encoding','etag','last-modified','date') if key in response.headers})
        return response.body(), response.headers.get("content-type", "application/octet-stream").split(";")[0], response.url
    raise ServiceError("redirect_limit", "Document download returned too many redirects")


def dismiss_cookies(page):
    for selector in ("#onetrust-reject-all-handler", 'button.osano-cm-denyAll'):
        button = page.locator(selector)
        if button.count() and button.first.is_visible():
            button.first.click()
            return
    osano = page.get_by_role("button", name="Reject Non-Essential", exact=True)
    if osano.count() and osano.first.is_visible():
        osano.first.click()
        return
    banner = page.locator("#onetrust-banner-sdk")
    if banner.count() and banner.is_visible():
        page.wait_for_function("typeof OneTrust !== 'undefined' && typeof OneTrust.RejectAll === 'function'", timeout=15000)
        page.evaluate("OneTrust.RejectAll()")
        banner.wait_for(state="hidden", timeout=15000)


class KudosGateway:
    def __init__(self, credential_root, sanitizer, engine="chromium"):
        self.root = Path(credential_root)
        self.sanitizer = sanitizer
        self.engine = engine
        self.context = self.browser = self.playwright = None
        self.pages = {}
        self.credentials(required=False)

    def credentials(self, required=True):
        path = self.root / "kudos.md"
        if not path.exists():
            if not required:
                return {}
            raise ServiceError("credentials_missing", "KUDOS credentials are absent from the protected store", status="restricted", provider="kudos")
        raw = path.read_text("utf-8-sig")
        fields = {}
        for key in ("ID", "PW"):
            match = re.search(r"(?mi)^\s*(?:[-*]\s*)?" + key + r"\s*:\s*(.+?)\s*$", raw)
            if not match:
                if required:
                    raise ServiceError("credentials_invalid", "KUDOS credential file does not contain the expected fields", status="restricted")
                continue
            fields[key] = match.group(1).strip().strip("`")
        self.sanitizer.secrets = tuple(sorted(set(self.sanitizer.secrets) | set(fields.values()), key=len, reverse=True))
        return fields

    def start(self):
        if self.context:
            return
        from playwright.sync_api import sync_playwright
        self.playwright = sync_playwright().start()
        self.browser = getattr(self.playwright, self.engine).launch(headless=True, **({"channel": "chrome"} if self.engine == "chromium" else {}))
        state = self.root / "scholarly-mcp" / "kudos.json"
        self.context = self.browser.new_context(storage_state=str(state) if state.exists() else None, accept_downloads=True)
        self.context.set_default_timeout(25000)

    def login(self, page):
        page.goto("https://kudos.knu.ac.kr/pages/index.htm", wait_until="domcontentloaded", timeout=45000)
        login = page.get_by_role("link", name="로그인", exact=True).first
        logout = page.get_by_role("link", name="로그아웃", exact=True).first
        login.or_(logout).wait_for(timeout=20000)
        if logout.count() and logout.is_visible():
            return
        fields = self.credentials()
        login.click()
        require_source_url(page.url, {"kudos.knu.ac.kr"})
        page.locator("#userid").fill(fields["ID"])
        page.locator("#passwd").fill(fields["PW"])
        page.locator("#passwd").press("Enter")
        try:
            page.get_by_role("link", name="로그아웃", exact=True).first.wait_for(timeout=30000)
        except Exception:
            raise ServiceError("authentication_failed", "KUDOS login did not reach an authenticated page", status="restricted", provider="kudos") from None
        state = self.root / "scholarly-mcp" / "kudos.json"
        state.parent.mkdir(parents=True, exist_ok=True)
        self.context.storage_state(path=str(state))

    def open(self, source, label, hosts, ready):
        self.start()
        cached = self.pages.get(source)
        if cached and not cached.is_closed() and urlsplit(cached.url).hostname in hosts:
            return cached
        page = self.context.new_page()
        stage = 'portal_login'
        target = None
        try:
            self.login(page)
            stage = 'academic_database_page'
            page.get_by_role("link", name="검색", exact=True).first.hover()
            page.get_by_role("link", name="학술DB", exact=True).first.click()
            stage = 'database_filter'
            with page.expect_navigation(wait_until="domcontentloaded"):
                page.locator("#search_order").fill(label)
                page.locator("#search_order").press("Enter")
            row = page.locator(".db-tit").filter(has_text=label).first
            stage = 'database_shortcut'
            shortcut = row.get_by_role("link", name="바로가기")
            shortcut.wait_for()
            with self.context.expect_page(timeout=25000) as popup:
                shortcut.click()
            target = popup.value
            stage = 'publisher_redirect'
            target.wait_for_url(lambda u: urlsplit(str(u)).hostname in hosts, wait_until="domcontentloaded", timeout=55000)
            stage = 'publisher_ready'
            target.locator(ready).filter(visible=True).first.wait_for(timeout=55000)
            require_source_url(target.url, hosts)
            self.pages[source] = target
            return target
        except ServiceError:
            raise
        except Exception as error:
            observed_host = urlsplit(target.url).hostname if target is not None else None
            challenge = observed_host in {'validate.perfdrive.com', 'challenges.cloudflare.com'}
            raise ServiceError('publisher_access_challenge' if challenge else 'gateway_navigation_failed',
                'Publisher redirected to an access challenge' if challenge else 'KUDOS academic-DB shortcut did not reach a ready source page',
                status='restricted' if challenge else 'error', source=source, stage=stage, error_type=type(error).__name__, observed_host=observed_host, retryable=True) from None
        finally:
            page.close()

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def public_page(self, source):
        self.start()
        page = self.pages.get(source)
        if page is None or page.is_closed():
            page = self.context.new_page()
            self.pages[source] = page
        return page


class MathSciNet:
    source = "mathscinet"
    EXPORTS = {"bibtex": "bib", "endnote": "end", "amsref": "ams", "tex": "tex"}

    def __init__(self, store, gateway):
        self.store, self.gateway = store, gateway

    def page(self):
        return self.gateway.open(self.source, "MathSciNet", MSC_HOSTS, "#searchTextInput, main h1")

    def citation_exports(self,identifiers,formats):
        if any(not re.fullmatch(r'[0-9]+',str(value)) for value in identifiers):
            raise ServiceError('invalid_export','Every selected citation must have an MR number')
        identifiers=[str(int(value)) for value in identifiers]
        if not identifiers or len(identifiers)!=len(set(identifiers)) or any(format not in self.EXPORTS for format in formats):
            raise ServiceError('invalid_export','Select distinct MR numbers and documented citation formats')
        page=self.page();host=urlsplit(page.url).hostname
        url='https://'+host+'/mathscinet/api/publications/format?'+urlencode({'formats':'ams,bib,tex,end','ids':','.join(identifiers)})
        data,_,actual=browser_download(self.gateway.context,url,MSC_HOSTS)
        try:payload=json.loads(data)
        except ValueError:raise ServiceError('invalid_response','MathSciNet returned no citation JSON') from None
        evidence=self.store.put(encoded(payload),'application/json',self.source,actual,role='provider_citation_formats',requested_mr_order=identifiers)
        order=[str(row.get('paperId')) for row in payload if isinstance(row,dict)] if isinstance(payload,list) else []
        if not isinstance(payload,list) or len(order)!=len(payload) or len(order)!=len(set(order)) or set(order)!=set(identifiers):
            raise ServiceError('citation_identity_mismatch','MathSciNet citation response identifies a different set of MR records',evidence=evidence)
        media={'bibtex':'application/x-bibtex','endnote':'application/x-endnote-refer','amsref':'text/plain','tex':'application/x-tex'}
        exports=[]
        for format in formats:
            values=[row.get(self.EXPORTS[format]) for row in payload]
            if any(not isinstance(value,str) or not value.strip() for value in values):
                raise ServiceError('citation_format_missing','MathSciNet omitted a requested formatted citation',format=format,evidence=evidence,partial_exports=exports)
            text='\n\n'.join(values)
            if format in ('bibtex','endnote'):
                parsed=bibliography(text.encode('utf-8'),media[format])
                observed=[]
                for item in parsed:
                    value=item.get('mrnumber',item.get('id','')) if format=='bibtex' else item.get('fields',{}).get('L',[''])[0]
                    try:observed.append(str(int(mathscinet_target(str(value)))))
                    except (ServiceError,ValueError):observed.append(None)
                if observed!=order:
                    raise ServiceError('citation_identity_mismatch','Formatted citations differ from their MR publication records',format=format,evidence=evidence,partial_exports=exports)
            artifact=self.store.put(text,media[format],self.source,actual,preserve_bytes=True,role='citation_export',format=format,count=len(payload),
                mr_order=order,requested_mr_order=identifiers,parent_ref=evidence['ref'],serialization='Provider-formatted strings joined by blank lines; provider array order retained')
            exports.append({'format':format,'artifact':artifact})
        return exports

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 100:
            raise ServiceError("invalid_range", "MathSciNet requires start >= 0 and limit 1..100")
        if cursor or set(options) - {"sort"}:
            raise ServiceError("invalid_options", "MathSciNet uses start; place field constraints in query and use options.sort for ordering")
        sort = options.get("sort", "newest")
        if sort not in ("newest", "oldest", "relevance"):
            raise ServiceError("invalid_options", "Validated sort values are newest, oldest, relevance")
        if export not in (None, "json", *self.EXPORTS):
            raise ServiceError("invalid_export", "Use json, bibtex, endnote, amsref or tex")
        page = self.page()
        host = urlsplit(page.url).hostname
        size = next(n for n in (5, 10, 20, 50, 100) if n >= limit)
        first_page = start // size + 1
        last_page = (start + limit - 1) // size + 1
        records, evidence, citations, citation_artifacts, export_errors = [], [], [], [], []
        total = None
        from playwright.sync_api import TimeoutError as BrowserTimeout
        for page_number in range(first_page, last_page + 1):
            query_url = "https://" + host + "/mathscinet/publications-search?" + urlencode({"query": query, "page": page_number, "size": size, "sort": sort, "facets": ""})
            def matching(response):
                url = urlsplit(response.url)
                params = parse_qs(url.query)
                return url.hostname == host and url.path == "/mathscinet/api/publications/search" and params.get("query") == [query] and params.get("currentPage") == [str(page_number)] and params.get("pageSize") == [str(size)]
            try:
                with page.expect_response(matching, timeout=45000) as captured:
                    goto_source(page, query_url, MSC_HOSTS, wait_until="domcontentloaded", timeout=45000)
                response = captured.value
                if response.status != 200:
                    raise ServiceError("provider_error", "MathSciNet search request failed", http_status=response.status)
                payload = response.json()
                if not isinstance(payload.get("results"), list) or type(payload.get("total")) is not int:
                    raise ServiceError("invalid_response", "MathSciNet search response has an unexpected schema")
                total = payload["total"]
                raw = self.store.put(encoded(payload), "application/json", self.source, response.url, role="provider_response", query=query, page=page_number, page_size=size, sort=sort)
                evidence.append(raw)
                offset = (page_number - 1) * size
                selected_indexes = [i for i in range(len(payload["results"])) if start <= offset + i < start + limit]
                # Save the entire received response; the requested window is a separate artifact.
                records.extend(payload["results"][i] for i in selected_indexes)
                if export in self.EXPORTS and selected_indexes:
                    try:
                        selected=[str(payload['results'][i]['mrnumber']) for i in selected_indexes]
                        native=self.citation_exports(selected,[export])[0]['artifact']
                        citations.append(self.store.read(native['ref'])[1].decode('utf-8'))
                        citation_artifacts.append(native)
                    except ServiceError as error:
                        export_errors.append({'page':page_number,**error.result})
                if offset + len(payload["results"]) >= total:
                    break
            except BrowserTimeout:
                raise ServiceError("source_timeout", "MathSciNet did not finish the requested search/export", source=self.source, evidence=evidence, retryable=True) from None
        artifact = self.store.put(encoded(records), "application/json", self.source, query_url, role="records", query=query, start=start, requested=limit, total=total)
        exported = artifact
        if citations:
            media = {"bibtex": "application/x-bibtex", "endnote": "application/x-endnote-refer", "amsref": "text/plain", "tex": "application/x-tex"}[export]
            exported = citation_artifacts[0] if len(citations)==1 else self.store.put("\n\n".join(citations), media, self.source, query_url, preserve_bytes=True,
                role="citation_export", format=export, count=sum(a['count'] for a in citation_artifacts),parent_refs=[a['ref'] for a in citation_artifacts])
        if export_errors:
            exported={'status':'partial','artifacts':citation_artifacts,'errors':export_errors,**({'artifact':exported} if citations else {})}
        has_more = start + len(records) < total
        return {"status": "partial" if export_errors else "ok" if records else "not_found", "source": self.source, "query": query, "options": options,
            "start": start, "requested": limit, "received": len(records), "total": total, "has_more": has_more,
            "next": {"start": start + len(records)} if has_more else None, "records": artifact, "export": exported,
            "evidence": evidence, "preview": [{"id": "MR" + str(row["mrnumber"]), "titles": row["titles"]} for row in records[:3]],
            "scope": "KUDOS → academic DB → MathSciNet proxy; selected source only"}

    def fetch(self, target, *, parts):
        if set(parts)-{'metadata','abstract','fulltext','supplementary','export'}:
            raise ServiceError('invalid_parts','Unknown requested content')
        is_doi=bool(re.match(r'^(?:10\.\d{4,9}/|doi:|https?://(?:dx\.)?doi\.org/)',target,re.I))
        is_name=not re.fullmatch(r'(?:MR)?[0-9]+',target,re.I) and not target.startswith(('http://','https://'))
        if is_doi or is_name:
            if not target.strip():raise ServiceError('invalid_target','Supply an MR number, DOI, document URL or title')
            from api_adapters import doi
            identifier=doi(target) if is_doi else None
            query=('doi:' if is_doi else 'ti:')+'('+json.dumps(identifier or target,ensure_ascii=False)+')'
            found=self.search(query,options={},limit=20,export='bibtex' if is_doi else None)
            if is_doi and found['status']=='ok' and found.get('total')==found.get('received')==1:
                rows=json.loads(self.store.read(found['records']['ref'])[1])
                citations=bibliography(self.store.read(found['export']['ref'])[1],'application/x-bibtex')
                if len(citations)==1 and citations[0].get('doi','').casefold()==identifier.casefold():
                    result=self.fetch('MR'+str(rows[0]['mrnumber']),parts=parts)
                    return {**result,'requested_target':target,'lookup':{'query':query,'records':found['records'],'export':found['export']}}
            return {**found,'requested_target':target,'status':'selection_required' if found.get('received') else found['status'],
                'message':'Select an MR record from the preserved candidates; DOI input is followed only when the native citation confirms it'}
        mr = mathscinet_target(target)
        page = self.page()
        host = urlsplit(page.url).hostname
        url = "https://" + host + "/mathscinet/article?mr=" + mr
        goto_source(page, url, MSC_HOSTS, wait_until="domcontentloaded", timeout=45000)
        page.locator("main h1").filter(has_text="MR" + mr).wait_for(timeout=45000)
        raw = page.locator("main").inner_html()
        html = clean_html(raw, self.store.sanitizer)
        html_artifact = self.store.put(html, "text/html", self.source, url, role="source_page", mr="MR" + mr)
        text = BeautifulSoup(html, "html.parser").get_text("\n", strip=True)
        text_artifact = self.store.put(text, "text/plain", self.source, url, role="source_page_text", parent_ref=html_artifact["ref"])
        components = {}
        for part in parts:
            if part in ("metadata", "export"):
                components[part] = {"status": "available", "artifact": html_artifact}
            elif part == "abstract":
                components[part] = {"status": "source_page", "artifact": html_artifact, "reason": "Review, source-selected summary and author abstract remain labeled in the preserved page; no semantic relabeling"}
            elif part == "fulltext":
                components[part] = {"status": "not_offered", "reason": "MathSciNet Review PDF is a review, not the cited work's full text. Article links belong to their named providers."}
            elif part == "supplementary":
                link = page.get_by_role("link", name="Review PDF")
                if link.count():
                    observed = urljoin(url, link.first.get_attribute("href"))
                    if urlsplit(observed).hostname != host:
                        raise ServiceError("source_boundary", "Review PDF link left MathSciNet")
                    response = self.gateway.context.request.get(observed, timeout=45000)
                    data = response.body()
                    if response.status != 200 or not data.startswith(b"%PDF-"):
                        components[part] = {"status": "error", "code": "invalid_review_pdf"}
                    else:
                        import pymupdf
                        with pymupdf.open(stream=data, filetype="pdf") as document:
                            pages = len(document)
                        artifact = self.store.put(data, "application/pdf", self.source, observed, role="review_pdf", mr="MR" + mr, pages=pages)
                        components[part] = {"status": "available", "artifact": artifact}
                else:
                    components[part] = {"status": "not_found", "reason": "No Review PDF link on this record"}
            else:
                raise ServiceError("invalid_parts", "Unknown requested content", part=part)
        if 'export' in parts:
            try:
                exports=self.citation_exports([mr],list(self.EXPORTS))
                components['export']={'status':'available','artifact':exports[0]['artifact'],'artifacts':exports}
            except ServiceError as error:components['export']=error.result
        return {"status": "ok" if all(v["status"] == "available" for v in components.values()) else "partial", "source": self.source,
            "target": "MR" + mr, "components": components, "records": text_artifact, "source_page": html_artifact,
            "links": [{"label": a.get_text(" ", strip=True), "url": self.store.sanitizer.url(urljoin(url, a["href"]))} for a in BeautifulSoup(html, "html.parser").select("a[href]")],
            "scope": "Only this MathSciNet record was retrieved"}


class WebOfScience:
    source = "wos"
    hosts = {"www-webofscience-com.libproxy.knu.ac.kr", "www.webofscience.com"}
    formats = {"plain": ("Plain text file", "application/x-wos"),
        "ris": ("RIS (other reference software)", "application/x-research-info-systems"),
        "bibtex": ("BibTeX", "application/x-bibtex"), "excel": ("Excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        "tsv": ("Tab delimited file", "text/tab-separated-values"), "html": ("Printable HTML file", "text/html")}

    def __init__(self, store, gateway):
        self.store, self.gateway = store, gateway

    def cookies(self, page):
        dismiss_cookies(page)

    def export_records(self, page, start, end, format):
        label, media = self.formats[format]
        page.locator("#export-trigger-btn").click()
        page.get_by_role("menuitem", name=label, exact=True).click()
        page.locator('input[name="markFrom"]').wait_for()
        page.locator("#radio3-input").focus()
        page.locator("#radio3-input").press("Space")
        page.locator('input[name="markFrom"]').fill(str(start + 1))
        page.locator('input[name="markTo"]').fill(str(end))
        page.get_by_text("Record Content:", exact=True).locator("..").get_by_role("combobox").click()
        content = "Full Record and Cited References" if format == "plain" else "Full Record"
        page.get_by_role("option", name=content, exact=True).click()
        with page.expect_download(timeout=60000) as event:
            page.locator("#exportButton").click()
        download = event.value
        if download.failure():
            raise ServiceError("export_failed", "WOS native export download failed")
        data = Path(download.path()).read_bytes()
        if not data:
            raise ServiceError("empty_export", "WOS native export was empty")
        if format=='excel':
            if data.startswith(bytes.fromhex('d0cf11e0a1b11ae1')):
                media='application/vnd.ms-excel'
            elif data.startswith(b'PK'):
                media='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:
                raise ServiceError('invalid_export','WOS returned no recognized Excel workbook')
        return self.store.put(data, media, self.source, page.url, role="citation_export", format=format,
            record_content=content, start=start, end=end, original_name=download.suggested_filename)

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ServiceError("invalid_range", "WOS requires start >= 0 and limit 1..1000")
        if options or cursor:
            raise ServiceError("invalid_options", "Use native WOS field/date constraints in query and start for the requested window; additional UI filters are still being implemented")
        if export not in (None, "json", *self.formats):
            raise ServiceError("invalid_export", "Use json, plain, ris, bibtex, excel, tsv or html")
        page = self.gateway.open(self.source, "Web of Science CPCI", self.hosts, '#composeQuerySmartSearch,input[name="search-main-box"]')
        self.cookies(page)
        page.get_by_role("link", name="Advanced Search", exact=True).first.click()
        page.get_by_text("QUERY BUILDER", exact=True).click()
        area = page.locator("#advancedSearchInputArea")
        area.fill(query)
        with page.expect_response(lambda r: urlsplit(r.url).hostname in self.hosts and urlsplit(r.url).path == "/api/wosnx/core/runQuerySearch", timeout=60000) as event:
            page.get_by_role("button", name="Search", exact=True).click()
        response = event.value
        if response.status != 200:
            raise ServiceError("provider_error", "WOS browser search failed", http_status=response.status)
        request = response.request.post_data_json
        if request.get("search", {}).get("query") != [{"rowText": query}] or request["search"].get("database") != "WOSCC":
            raise ServiceError("query_mismatch", "WOS did not submit the requested query and collection")
        result = wos_events(response.text())
        evidence = self.store.put(encoded(result["events"]), "application/json", self.source, response.url,
            role="provider_response", query=query, collection="WOSCC", search_options=request["search"].get("options", {}))
        total = result["total"]
        if start >= total:
            artifact = self.store.put(b"[]", "application/json", self.source, page.url, role="records", query=query, start=start)
            return {"status": "not_found", "source": self.source, "query": query, "total": total, "received": 0, "records": artifact, "evidence": evidence,
                "has_more": False, "scope": "Requested WOS result window is empty"}
        page.locator("#export-trigger-btn").wait_for(timeout=30000)
        end = min(start + limit, total)
        full_export = self.export_records(page, start, end, "plain")
        records = bibliography(self.store.read(full_export["ref"])[1], "application/x-wos")
        if len(records) != end - start:
            raise ServiceError("export_range_mismatch", "WOS export count differs from the requested record window", expected=end - start, received=len(records), evidence=full_export)
        artifact = self.store.put(encoded(records), "application/json", self.source, page.url,
            role="records", query=query, start=start, requested=limit, total=total, export_ref=full_export["ref"])
        exported = artifact if export in (None, "json") else full_export if export == "plain" else self.export_records(page, start, end, export)
        return {"status": "ok", "source": self.source, "query": query, "options": options, "collection": "WOSCC", "editions": "All within institutional access",
            "start": start, "requested": limit, "received": len(records), "total": total, "records": artifact, "export": exported,
            "full_record_export": full_export, "evidence": evidence, "has_more": end < total, "next": {"start": end} if end < total else None,
            "preview": [{"id": r["id"], "title": " ".join(r["fields"].get("ti", []))} for r in records[:3]],
            "scope": "KUDOS academic DB → Web of Science Core Collection, including licensed CPCI editions"}

    def fetch(self, target, *, parts):
        from api_adapters import doi
        is_title = False
        if target.startswith(('http://', 'https://')) and urlsplit(target).hostname not in ('doi.org', 'dx.doi.org'):
            require_source_url(target, self.hosts)
            match = re.search(r'/full-record/(WOS:[0-9A-Z]+)(?:/|$)', unquote(urlsplit(target).path))
            if not match:
                raise ServiceError('invalid_target', 'Use a WOS full-record URL, accession number, DOI or title')
            target = match[1]
        if re.fullmatch(r"(?:WOS:)?[0-9A-Z]+", target):
            value = target if target.startswith("WOS:") else "WOS:" + target
            query = "UT=(" + value + ")"
        elif target.startswith(("10.", "doi:", "https://doi.org/")):
            query = 'DO=("' + doi(target).replace('"', '\\"') + '")'
        else:
            is_title = True
            query = 'TI=("' + target.replace('"', '\\"') + '")'
        result = self.search(query, options={}, limit=20 if is_title else 1, export="plain")
        if result["status"] != "ok":
            return result
        if is_title:
            result.update(status='selection_required', message='Select the accession number or DOI from these title candidates')
            return result
        if result["total"] != 1:
            result["status"] = "selection_required"
            return result
        rows = json.loads(self.store.read(result["records"]["ref"])[1])
        components = {}
        for part in parts:
            if part in ("metadata", "supplementary", "export") or (part == "abstract" and rows[0]["fields"].get("ab")):
                components[part] = {"status": "available", "artifact": result["records"]}
            elif part == "abstract":
                components[part] = {"status": "not_found", "reason": "No abstract tag in this full record"}
            elif part == "fulltext":
                components[part] = {"status": "not_offered", "reason": "WOS indexes this work; publisher full text is a separate source"}
            else:
                raise ServiceError("invalid_parts", "Unknown requested content", part=part)
        result["components"] = components
        result["status"] = "ok" if all(v["status"] == "available" for v in components.values()) else "partial"
        return result


class ECCC:
    source = "eccc"
    hosts = {"eccc.weizmann.ac.il"}

    def __init__(self, store, gateway):
        self.store, self.gateway = store, gateway

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        if options or cursor or export not in (None, "json", "html"):
            raise ServiceError("invalid_options", "ECCC uses a literal query, start/limit and json/html export")
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ServiceError("invalid_range", "Use start >= 0 and limit 1..1000")
        page = self.gateway.public_page(self.source)
        goto_source(page, "https://eccc.weizmann.ac.il/", self.hosts, wait_until="domcontentloaded", timeout=45000)
        page.locator('input[name="search"]').fill(query)
        with page.expect_navigation(wait_until="domcontentloaded"):
            page.locator('input[name="search"]').press("Enter")
        if parse_qs(urlsplit(page.url).query).get("search") != [query]:
            raise ServiceError("query_mismatch", "ECCC did not navigate to the requested search")
        require_source_url(page.url, self.hosts)
        raw = page.content()
        if "Results for query" not in page.locator("body").inner_text():
            raise ServiceError("invalid_response", "ECCC did not return its result listing")
        records = eccc_records(raw)
        source_page = self.store.put(clean_html(raw, self.store.sanitizer), "text/html", self.source, page.url, role="search_page", query=query)
        all_records = self.store.put(encoded(records), "application/json", self.source, page.url, role="all_received_records", query=query)
        selected = records[start:start + limit]
        artifact = self.store.put(encoded(selected), "application/json", self.source, page.url, role="records", query=query, start=start, requested=limit, parent_ref=all_records["ref"])
        return {"status": "ok" if selected else "not_found", "source": self.source, "query": query, "start": start, "requested": limit,
            "received": len(selected), "total": None, "stored_total": len(records), "has_more": start + len(selected) < len(records),
            "records": artifact, "all_records": all_records, "export": source_page if export == "html" else artifact, "evidence": source_page,
            "preview": [{k: row[k] for k in ("id", "title", "url")} for row in selected[:3]],
            "scope": "All rows supplied on this ECCC search page are preserved, including duplicate hits. Snippets are not abstracts. The page provides no independent corpus-wide total."}

    def fetch(self, target, *, parts):
        if set(parts)-{'metadata','abstract','fulltext','supplementary','export'}:
            raise ServiceError('invalid_parts','Unknown requested content')
        revision = None
        if target.startswith(("https://", "http://")):
            parsed = urlsplit(target)
            if parsed.hostname not in self.hosts:
                raise ServiceError("source_boundary", "Target is outside ECCC")
            match = re.fullmatch(r"/report/([0-9]{4})/([0-9]{1,3})/?(?:revision/([0-9]+)/?(?:download)?|download)?", parsed.path)
            if not match:
                raise ServiceError("invalid_target", "Use an ECCC report or revision download URL")
            year, number = int(match.group(1)), int(match.group(2))
            revision = int(match.group(3)) if match.group(3) else 0 if parsed.path.endswith("/download") else None
        else:
            match = re.fullmatch(r"TR([0-9]{2})-([0-9]{3})(?:r([0-9]+))?", target, re.I)
            if not match:
                if not target.strip() or re.match(r'TR[0-9]{2}-',target,re.I):
                    raise ServiceError("invalid_target", "Use TRyy-nnn, TRyy-nnnrN, an ECCC report URL or a title")
                candidates=self.search(target,options={},limit=20)
                return {**candidates,'requested_target':target,'status':'selection_required' if candidates.get('received') else candidates['status'],
                    'message':'Select an ECCC report and revision from the native search candidates'}
            year = int(match.group(1)) + (1900 if int(match.group(1)) >= 94 else 2000)
            number = int(match.group(2))
            revision = int(match.group(3)) if match.group(3) else None
        url = f"https://eccc.weizmann.ac.il/report/{year}/{number:03d}/"
        page = self.gateway.public_page(self.source)
        response = goto_source(page, url, self.hosts, wait_until="domcontentloaded", timeout=45000)
        if response and response.status >= 400:
            raise ServiceError("provider_error", "ECCC report request failed", http_status=response.status)
        raw = page.content()
        versions = eccc_versions(raw)
        if not versions:
            raise ServiceError("not_found_at_source" if "404" in page.title() else "invalid_response", "ECCC returned no report revisions", status="not_found" if "404" in page.title() else "error")
        selected = max(versions, key=lambda v: v["revision"]) if revision is None else next((v for v in versions if v["revision"] == revision), None)
        if selected is None:
            raise ServiceError("not_found_at_source", "Requested ECCC revision is not on the report page", status="not_found")
        artifact = self.store.put(encoded([selected]), "application/json", self.source, url, role="records", revision=selected["revision"])
        source_page = self.store.put(clean_html(raw, self.store.sanitizer), "text/html", self.source, url, role="source_page")
        components = {}
        for part in parts:
            if part in ("metadata", "abstract", "export"):
                components[part] = {"status": "available", "artifact": artifact}
            elif part == "fulltext":
                try:
                    data, media, obtained_url = browser_download(self.gateway.context, selected["pdf"], self.hosts)
                    if not data.startswith(b"%PDF-"):
                        raise ServiceError("unexpected_content", "ECCC did not return a PDF")
                    import pymupdf
                    with pymupdf.open(stream=data, filetype="pdf") as doc:
                        pages = len(doc)
                    pdf = self.store.put(data, "application/pdf", self.source, obtained_url, role="fulltext", revision=selected["revision"], pages=pages)
                    components[part] = {"status": "available", "artifact": pdf}
                except ServiceError as error:
                    components[part] = error.result
            elif part == "supplementary":
                components[part] = {"status": "source_page", "artifact": source_page, "reason": "Report page includes revisions and comments; additional attachments are not automatically classified"}
            else:
                raise ServiceError("invalid_parts", "Unknown requested content", part=part)
        return {"status": "ok" if all(v["status"] == "available" for v in components.values()) else "partial", "source": self.source,
            "target": selected["id"], "revision": selected["revision"], "components": components, "records": artifact,
            "source_page": source_page, "versions": [{k: v[k] for k in ("id", "revision", "version_label", "pdf")} for v in versions]}


class ACM:
    source = "acm-dl"
    hosts = {"dl-acm-org.libproxy.knu.ac.kr", "portal-acm-org.libproxy.knu.ac.kr", "dl.acm.org"}
    fields = {"AllField", "Title", "ContentGroupTitle", "ContribAuthor", "Abstract", "Fulltext", "Affiliation", "Keyword", "ConferenceLocation", "ConferenceSponsor", "Contrib", "PubIdSortField", "DOI"}
    formats = {"bibtex": ("bibtex", "application/x-bibtex"), "endnote": ("endNote", "application/x-endnote-refer"), "acmref": ("acm", "text/plain")}

    def __init__(self, store, gateway):
        self.store, self.gateway = store, gateway
        self.known_records = {}

    def page(self):
        return self.gateway.open(self.source, "ACM", self.hosts, 'input[name="AllField"]')

    def render_citations(self, page, payload, identifiers, format):
        items = {}
        for entry in payload.get("items", []):
            items.update(entry)
        if {key.lower() for key in items} != {key.lower() for key in identifiers} or payload.get("exportedDoiLength") != len(identifiers):
            raise ServiceError("export_identity_mismatch", "ACM citation response differs from the selected records")
        script_ref = getattr(self, "processor_ref", None)
        if script_ref is None:
            script_url = "https://" + urlsplit(page.url).hostname + "/templates/jsp/_ux3/_acm/citeproc.min.js"
            script, media, obtained = browser_download(self.gateway.context, script_url, self.hosts)
            if "javascript" not in media:
                raise ServiceError("citation_processor_unavailable", "The observed ACM citation processor did not return JavaScript")
            script_ref = self.store.put(script, "text/javascript", self.source, obtained, preserve_bytes=True, role="citation_processor")
            self.processor_ref = script_ref
        script = self.store.read(script_ref["ref"])[1].decode("utf-8")
        source_data = self.store.put(encoded(payload), "application/json", self.source, page.url, role="native_citation_data", identifiers=identifiers, format=format)
        # The publisher's processor and supplied CSL style run without its unrelated page bundles.
        renderer = self.gateway.context.new_page()
        try:
            renderer.route("**/*", lambda route: route.abort())
            renderer.set_content("<html><body></body></html>")
            renderer.evaluate("window.UX = {}")
            renderer.add_script_tag(content=script)
            rendered = renderer.evaluate("""data => {
                const items = Object.assign({}, ...data.items);
                const processor = new UX.CSL.Engine({retrieveLocale: () => data.locale, retrieveItem: id => items[id]}, data.style);
                processor.setOutputFormat('text');
                processor.updateItems(Object.keys(items));
                return processor.makeBibliography();
            }""", payload)
            if not rendered or len(rendered[1]) != len(identifiers):
                raise ServiceError("export_count_mismatch", "Citation processor did not render every selected record")
            text = "\n".join(rendered[1])
        finally:
            renderer.close()
        return self.store.put(text, self.formats[format][1], self.source, page.url, role="citation_export", format=format,
            identifiers=identifiers, source_data_ref=source_data["ref"], processor_ref=script_ref["ref"])

    def citation(self, page, identifiers, format="bibtex", *, record_page=False):
        if not record_page:
            for identifier in identifiers:
                checkbox = page.locator('input[type="checkbox"][name="' + identifier + '"]')
                if not checkbox.is_checked():
                    checkbox.focus()
                    checkbox.press("Space")
        with page.expect_response(lambda r: urlsplit(r.url).path == "/action/exportCiteProcCitation", timeout=45000) as exported:
            if record_page:
                page.get_by_role("button", name="Export Citation", exact=True).first.click()
            else:
                page.get_by_text("Export Citations", exact=True).filter(visible=True).first.click()
        selector = page.locator("#citation-format")
        selector.wait_for()
        value, media = self.formats[format]
        if selector.input_value() != value:
            with page.expect_response(lambda r: urlsplit(r.url).path == "/action/exportCiteProcCitation", timeout=45000) as exported:
                selector.select_option(value)
        response = exported.value
        if response.status != 200:
            raise ServiceError("export_failed", "ACM native citation response failed", http_status=response.status)
        artifact = self.render_citations(page, response.json(), identifiers, format)
        page.get_by_role("button", name="Close modal", exact=True).filter(visible=True).first.click()
        return artifact

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        allowed = {"field", "fields", "collection", "from_year", "to_year", "from_month", "to_month", "sort"}
        if set(options) - allowed or cursor:
            raise ServiceError("invalid_options", "Use ACM field/fields, collection, date range and sort; pagination uses start")
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ServiceError("invalid_range", "ACM requires start >= 0 and limit 1..1000")
        if export not in (None, "json", *self.formats):
            raise ServiceError("invalid_export", "Use json, bibtex, endnote or acmref")
        terms = [{"field": options.get("field", "AllField"), "value": query}, *options.get("fields", [])]
        if any(set(term) != {"field", "value"} or term["field"] not in self.fields or not isinstance(term["value"], str) for term in terms):
            raise ServiceError("invalid_options", "Each additional field has field and value; fields are combined by native AND")
        collection = {"fulltext": "dl", "guide": "all"}.get(options.get("collection", "fulltext"))
        if not collection:
            raise ServiceError("invalid_options", "collection must be fulltext or guide")
        page = self.page()
        host = urlsplit(page.url).hostname
        goto_source(page, "https://" + host + "/search/advanced", self.hosts, wait_until="domcontentloaded", timeout=45000)
        page.locator('select[name="expand"]').select_option(collection)
        for index, term in enumerate(terms, 1):
            if index > 1:
                page.locator(".advanced-search__search-in__add").filter(visible=True).first.click()
            page.locator("#searchArea" + str(index)).select_option(term["field"])
            entry = page.locator("#text" + str(index))
            entry.fill(term["value"])
            entry.press("Tab")
            if term["value"]:
                page.wait_for_function("i => document.getElementById('text'+i).name === 'text'+i && document.getElementById('searchArea'+i).name === 'field'+i", arg=index)
        if options.get("from_year") or options.get("to_year"):
            page.locator("#customRange").focus()
            page.locator("#customRange").press("Space")
            for option, control in {"from_year": "fromYear", "to_year": "toYear", "from_month": "fromMonth", "to_month": "toMonth"}.items():
                if options.get(option):
                    page.locator("#" + control).select_option(str(options[option]))
        with page.expect_navigation(wait_until="domcontentloaded"):
            page.locator("#advanced-search-btn").click()
        parsed = urlsplit(page.url)
        params = parse_qs(parsed.query, keep_blank_values=True)
        if params.get("field1") != [terms[0]["field"]] or params.get("text1") != [query] or params.get("expand") != [collection]:
            raise ServiceError("query_mismatch", "ACM did not submit the requested field and collection")
        sort = options.get("sort")
        if sort:
            if sort not in ("EpubDate_asc", "EpubDate_desc"):
                raise ServiceError("invalid_options", "Validated ACM sort values are EpubDate_asc and EpubDate_desc")
            params["sortBy"] = [sort]
        size = 50
        params["pageSize"] = [str(size)]
        rows, evidence, exports = [], [], []
        total = None
        for page_index in range(start // size, (start + limit - 1) // size + 1):
            params["startPage"] = [str(page_index)]
            url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(params, doseq=True), ""))
            goto_source(page, url, self.hosts, wait_until="domcontentloaded", timeout=45000)
            main = page.locator("main")
            main.wait_for()
            text = main.inner_text()
            match = re.search(r"([0-9,]+)\s+Results? for:", text, re.I)
            if not match:
                raise ServiceError("invalid_response", "ACM result count is missing")
            total = int(match.group(1).replace(",", ""))
            raw = main.inner_html()
            records = acm_records(raw, page.url)
            evidence.append(self.store.put(clean_html(raw, self.store.sanitizer), "text/html", self.source, page.url, role="search_page", query=query, options=options))
            selected = [row for i, row in enumerate(records, page_index * size) if start <= i < start + limit]
            if selected:
                native = self.citation(page, [row["id"] for row in selected])
                bibliographic = bibliography(self.store.read(native["ref"])[1], "application/x-bibtex")
                from collections import Counter
                if Counter(r["id"].lower() for r in bibliographic) != Counter(r["id"].lower() for r in selected):
                    raise ServiceError("export_identity_mismatch", "ACM citations do not correspond to the selected result records", evidence=native)
                by_id = {r["id"].lower(): r for r in bibliographic}
                for row in selected:
                    bib = by_id[row["id"].lower()]
                    row.update(bibliography=bib, year=bib.get("year"), abstract=bib.get("abstract"))
                    self.known_records[row["id"].lower()] = (bib, native)
                rows.extend(selected)
                exports.append(native if export in (None, "json", "bibtex") else self.citation(page, [row["id"] for row in selected], export))
            if (page_index + 1) * size >= total:
                break
        artifact = self.store.put(encoded(rows), "application/json", self.source, page.url, role="records", query=query, options=options, start=start, requested=limit, total=total)
        exported = artifact
        if export not in (None, "json") and exports:
            content = b"\n\n".join(self.store.read(a["ref"])[1] for a in exports)
            exported = self.store.put(content, self.formats[export][1], self.source, page.url, role="citation_export", format=export, count=len(rows))
        return {"status": "ok" if rows else "not_found", "source": self.source, "query": query, "options": options,
            "start": start, "requested": limit, "received": len(rows), "total": total, "has_more": start + len(rows) < total,
            "next": {"start": start + len(rows)} if start + len(rows) < total else None, "records": artifact, "export": exported,
            "native_citations": exports, "evidence": evidence, "preview": [{k: row.get(k) for k in ("id", "title", "year")} for row in rows[:3]]}

    def fetch(self, target, *, parts):
        from api_adapters import doi
        value = target
        if target.startswith(("http://", "https://")) and urlsplit(target).hostname in self.hosts:
            value = re.sub(r"^/doi/(?:pdf/|epdf/|full/|abs/)?", "", urlsplit(target).path)
        elif target.startswith(("http://", "https://")) and urlsplit(target).hostname not in {"doi.org", "dx.doi.org"}:
            raise ServiceError("source_boundary", "Use an ACM record URL or DOI")
        try:
            identifier = doi(value)
        except ServiceError:
            result = self.search(target, options={"field": "Title", "collection": "guide"}, limit=20)
            result["status"] = "selection_required" if result["received"] else "not_found"
            return result
        if identifier.lower() not in self.known_records:
            result = self.search(identifier, options={"field": "DOI", "collection": "guide"}, limit=2, export="bibtex")
            if result["status"] != "ok":
                return result
            if result["total"] != 1 or identifier.lower() not in self.known_records:
                result["status"] = "selection_required"
                return result
        record, citation_source = self.known_records[identifier.lower()]
        page = self.page()
        url = "https://" + urlsplit(page.url).hostname + "/doi/" + quote(identifier, safe="/")
        goto_source(page, url, self.hosts, wait_until="domcontentloaded", timeout=45000)
        page.get_by_role("heading", level=1).first.wait_for()
        records = [record]
        native = self.store.put(record["raw_text"], "application/x-bibtex", self.source, page.url, role="citation_export", identifiers=[identifier], parent_ref=citation_source["ref"])
        artifact = self.store.put(encoded(records), "application/json", self.source, page.url, role="records", target=identifier)
        raw = page.locator("main").inner_html()
        source_page = self.store.put(clean_html(raw, self.store.sanitizer), "text/html", self.source, page.url, role="source_page", target=identifier)
        components = {}
        for part in parts:
            if part in ("metadata", "export"):
                components[part] = {"status": "available", "artifact": native if part == "export" else artifact}
            elif part == "abstract":
                components[part] = {"status": "available", "artifact": artifact} if records[0].get("abstract") else {"status": "not_found", "reason": "This native citation has no abstract field"}
            elif part == "fulltext":
                link = page.locator('a[href*="/doi/pdf/"]').filter(visible=True)
                candidates = [urljoin(page.url, a.get_attribute("href")) for a in link.all()]
                candidates = [u for u in candidates if urlsplit(u).path == "/doi/pdf/" + identifier]
                if not candidates:
                    components[part] = {"status": "not_implemented", "reason": "No selected-document PDF control; HTML-only full text handling is pending", "artifact": source_page}
                    continue
                try:
                    data, media, obtained_url = browser_download(self.gateway.context, candidates[0], self.hosts)
                    if not data.startswith(b"%PDF-"):
                        raise ServiceError("unexpected_content", "ACM PDF control returned no PDF")
                    import pymupdf
                    with pymupdf.open(stream=data, filetype="pdf") as document:
                        pages = len(document)
                    pdf = self.store.put(data, "application/pdf", self.source, obtained_url, role="fulltext", target=identifier, pages=pages)
                    components[part] = {"status": "available", "artifact": pdf}
                except ServiceError as error:
                    components[part] = error.result
            elif part == "supplementary":
                try:
                    from supplements import fetch_supplementary
                    components[part]=fetch_supplementary(self,page,identifier,source_page,download_hosts=self.hosts)
                    components[part].setdefault('artifact',source_page)
                except ServiceError as exc:components[part]=exc.result
                except Exception as exc:components[part]={'status':'error','code':'supplementary_retrieval_failed','error_type':type(exc).__name__,'artifact':source_page}
            else:
                raise ServiceError("invalid_parts", "Unknown requested content", part=part)
        return {"status": "ok" if all(v["status"] == "available" for v in components.values()) else "partial", "source": self.source,
            "target": identifier, "components": components, "records": artifact, "source_page": source_page, "native_citation": native}
