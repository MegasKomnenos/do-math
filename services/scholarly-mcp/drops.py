"""DROPS: public metadata exports; fixed UI search and document-link discovery."""
import json
import re
from urllib.parse import urljoin, urlsplit, unquote

from bs4 import BeautifulSoup

from api_adapters import APIAdapter, doi
from browser_adapters import browser_download, clean_html, goto_source, require_source_url
from scholarly import ServiceError, encoded, bibliography
from defusedxml import ElementTree

EXPORTS = {'bibtex': 'application/x-bibtex', 'xml': 'application/xml', 'acm-xml': 'application/xml', 'doaj-xml': 'application/xml', 'schema-org': 'application/json', 'codemeta-json': 'application/json'}


def file_links(raw, base):
    soup = BeautifulSoup(raw, 'html.parser')
    links = []
    for node in soup.select('section.metadata.files a[href]'):
        url = urljoin(base, node['href'])
        if urlsplit(url).hostname == 'drops.dagstuhl.de' and urlsplit(url).path.startswith('/storage/') and url not in links:
            links.append(url)
    return links


class DROPS(APIAdapter):
    source = "drops"
    hosts = ("drops.dagstuhl.de",)
    max_limit = 1000

    def __init__(self, store, gateway, client=None):
        super().__init__(store, client=client)
        self.gateway = gateway

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if cursor or export not in (None, 'json', 'html', *EXPORTS):
            raise ServiceError('invalid_options', 'DROPS uses start/limit; see describe_source for native export formats')
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
        result = {"status": "ok" if rows else "not_found", "source": self.source, "query": query, "start": start,
            "requested": limit, "received": len(rows), "total": total, "has_more": start + len(rows) < total,
            "next": {"start": start + len(rows)} if start + len(rows) < total else None,
            "records": artifact, "export": {"artifacts": observations} if export == "html" else artifact, "evidence": observations,
            "preview": [{k: row[k] for k in ("id", "title", "url")} for row in rows[:3]]}
        if export in EXPORTS:
            artifacts, errors = [], []
            for row in rows:
                try:
                    artifacts.append(self.native_export(row['url'], export))
                except ServiceError as error:
                    errors.append({'id': row['id'], **error.result})
            result['export'] = {'status': 'partial' if errors else 'available', 'artifacts': artifacts, 'errors': errors}
            if export == 'bibtex':
                result['export'].update(self.store.put(b'\n\n'.join(self.store.read(a['ref'])[1] for a in artifacts), EXPORTS[export], self.source, page.url, role='native_citations', parent_refs=[a['ref'] for a in artifacts]))
            if errors:
                result['status'] = 'partial'
        return result

    def native_export(self, entity, kind):
        require_source_url(entity, self.hosts)
        if not urlsplit(entity).path.startswith('/entities/'):
            raise ServiceError('source_boundary', 'Use a DROPS entity')
        url = entity.rstrip('/') + '/metadata/' + kind
        expected = unquote(entity).split('/entities/', 1)[1].split('/', 1)[1]
        if kind == 'bibtex':
            url += '/download'
            data, evidence = self.request(url, accept='binary')
            rows = bibliography(data, EXPORTS[kind])
            if not rows or (expected.startswith('10.') and (len(rows) != 1 or rows[0].get('doi', '').casefold() != expected.casefold())):
                raise ServiceError('identity_mismatch', 'DROPS BibTeX does not identify the requested entity', evidence=evidence)
        elif kind == 'codemeta-json':
            url += '/download'
            data, evidence = self.request(url)
            metadata, _ = self.request(entity.rstrip('/') + '/metadata/schema-org')
            if not data.get('codeRepository') or data.get('name') != metadata.get('name') or data.get('codeRepository') != metadata.get('codeRepository'):
                raise ServiceError('identity_mismatch', 'CodeMeta does not match this DROPS software record', evidence=evidence)
            data = encoded(data)
        else:
            data, evidence = self.request(url, accept='json' if kind == 'schema-org' else 'xml')
            if kind == 'schema-org':
                if data.get('url', '').rstrip('/').casefold() != entity.rstrip('/').casefold():
                    raise ServiceError('identity_mismatch', 'DROPS metadata identifies another entity', evidence=evidence)
                data = encoded(data)
            else:
                root = ElementTree.fromstring(data)
                paths = {'xml': './{*}' + ('artifact' if '/entities/artifact/' in entity else 'article') + '/{*}doi', 'acm-xml': './book-part/book-part-meta/book-part-id[@book-part-id-type="doi"]', 'doaj-xml': './record/doi'}
                identity = root.findtext(paths[kind])
                expected = unquote(entity).split('/entities/', 1)[1].split('/', 1)[1]
                if expected.startswith('10.') and (not identity or identity.casefold() != expected.casefold()):
                    raise ServiceError('identity_mismatch', 'DROPS XML header does not identify the requested entity', evidence=evidence)
        return self.store.put(data, EXPORTS[kind], self.source, url, role='native_export', format=kind, entity=entity, evidence_ref=evidence['ref'])

    def fetch(self, target, *, parts):
        selected_file = None
        if target.startswith(("10.", "doi:", "https://doi.org/")):
            identifier = doi(target)
            if not identifier.lower().startswith("10.4230/"):
                raise ServiceError("source_boundary", "This DOI is not a DROPS identifier")
            entity = 'https://drops.dagstuhl.de/entities/' + ('artifact/' if identifier.lower().startswith('10.4230/artifacts.') else 'document/') + identifier
        elif target.startswith("https://"):
            parsed = urlsplit(target)
            require_source_url(target, self.hosts)
            if parsed.path.startswith('/storage/'):
                name = unquote(parsed.path.rsplit('/', 1)[-1])
                if not re.fullmatch(r'(?:LIPIcs|OASIcs|DARTS|TGDK|LITES|DagRep|DagMan)\.[A-Za-z0-9._-]+\.(pdf|html)', name):
                    raise ServiceError('invalid_target', 'Use an entity URL for this DROPS storage file')
                selected_file = target
                entity = 'https://drops.dagstuhl.de/entities/document/10.4230/' + name.rsplit('.', 1)[0]
            elif not parsed.path.startswith('/entities/'):
                raise ServiceError("source_boundary", "Use a DROPS entity URL")
            else:
                entity = target.split('/metadata/')[0].rstrip('/')
        else:
            result = self.search(target, options={}, limit=20)
            result["status"] = "selection_required" if result["received"] else "not_found"
            return result
        raw, evidence = self.request(entity + "/metadata/schema-org")
        if not isinstance(raw, dict) or raw.get("url", "").rstrip("/").lower() != entity.lower():
            raise ServiceError("identity_mismatch", "DROPS metadata does not match the requested entity", evidence=evidence)
        result = self.fetched([raw], evidence, parts, ("metadata", "export") + (("abstract",) if raw.get("abstract") else ()))
        if 'export' in parts:
            artifacts, errors = [{'format': 'schema-org', 'artifact': evidence}], []
            kinds = ['bibtex', 'xml']
            if '/entities/document/' in entity:
                kinds += ['acm-xml', 'doaj-xml']
            if raw.get('@type') == 'SoftwareSourceCode':
                kinds.append('codemeta-json')
            for kind in kinds:
                try:
                    artifacts.append({'format': kind, 'artifact': self.native_export(entity, kind)})
                except ServiceError as error:
                    errors.append({'format': kind, **error.result})
            result['components']['export'] = {'status': 'partial' if errors else 'available', 'artifact': evidence, 'artifacts': artifacts, 'errors': errors}
        if "fulltext" in parts or "supplementary" in parts:
            page = self.gateway.public_page(self.source)
            goto_source(page, entity, self.hosts, wait_until="domcontentloaded", timeout=45000)
            html = page.content()
            source_page = self.store.put(clean_html(html, self.store.sanitizer), "text/html", self.source, page.url, role="source_page", entity=entity)
            if "fulltext" in parts:
                links = file_links(html, page.url)
                if selected_file:
                    if selected_file not in links:
                        raise ServiceError('identity_mismatch', 'Requested storage file is not linked by this DROPS document', evidence=source_page)
                    links = [selected_file]
                files, errors = [], []
                for link in links:
                    try:
                        data, media, url = browser_download(self.gateway.context, link, self.hosts)
                        info = {}
                        if urlsplit(link).path.endswith('.pdf'):
                            if not data.startswith(b'%PDF-'):
                                raise ServiceError('unexpected_content', 'DROPS returned no PDF')
                            import pymupdf
                            with pymupdf.open(stream=data, filetype='pdf') as doc:
                                info['pages'] = len(doc)
                            media = 'application/pdf'
                        elif urlsplit(link).path.endswith('.html'):
                            body = BeautifulSoup(data, 'html.parser')
                            if entity.rsplit('/', 1)[-1] not in body.get_text() or not body.select_one('article'):
                                raise ServiceError('identity_mismatch', 'DROPS HTML does not contain this article identity')
                            data = clean_html(data, self.store.sanitizer)
                            media = 'text/html'
                        artifact = self.store.put(data, media, self.source, url, role='fulltext', entity=entity, **info)
                        files.append({'format': urlsplit(link).path.rsplit('.', 1)[-1], 'artifact': artifact})
                    except ServiceError as error:
                        errors.append({'url': self.store.sanitizer.url(link), **error.result})
                result['components']['fulltext'] = {'status': 'partial' if errors else 'available' if files else 'not_offered', 'artifacts': files, 'errors': errors}
                if files:
                    result['components']['fulltext']['artifact'] = files[0]['artifact']
            if "supplementary" in parts:
                soup = BeautifulSoup(html, 'html.parser')
                sections = [h.find_parent('section') for h in soup.select('h2') if h.get_text(' ', strip=True) == 'Supplementary Materials']
                references = [{'text': s.get_text('\n', strip=True), 'links': [{'label': a.get_text(' ', strip=True), 'url': urljoin(page.url, a['href']), 'external': urlsplit(urljoin(page.url, a['href'])).hostname not in self.hosts} for a in s.select('a[href]')]} for s in sections]
                artifact = self.store.put(encoded(references), 'application/json', self.source, page.url, role='supplementary_references', parent_ref=source_page['ref'])
                result['components']['supplementary'] = {'status': 'available' if references else 'not_offered', 'artifact': artifact, 'scope': 'Supplementary descriptions and links published by DROPS; external files are not fetched'}
            result["source_page"] = source_page
        result["status"] = "ok" if all(c["status"] == "available" for c in result["components"].values()) else "partial"
        return result
