"""Fixed API adapters. Redirects, failure and retrieval stay within a source."""
from __future__ import annotations

import json
import re
import time
from urllib.parse import parse_qs, quote, unquote, urljoin, urlsplit

import httpx
from defusedxml import ElementTree

from registry import SOURCES
from scholarly import ServiceError, encoded


def doi(value):
    value = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:)", "", value.strip(), flags=re.I)
    if not re.fullmatch(r"10\.[0-9]{4,9}/\S+", value):
        raise ServiceError("invalid_target", "Use a DOI or a DOI resolver link for this source")
    return value


def brief(row):
    keys = ("id", "DOI", "title", "display_name", "year", "published", "authors", "author", "url", "URL", "key", "paperId")
    return {k: row[k] for k in keys if k in row}


class APIAdapter:
    source = ""
    hosts = ()
    options = ()
    max_limit = 100
    min_interval = 0.0

    def __init__(self, store, client=None):
        self.store = store
        self.client = client or httpx.Client(timeout=httpx.Timeout(45, connect=20), follow_redirects=False,
            headers={"User-Agent": "scholarly-mcp/0.1 (local scholarly research)", "Accept": "application/json"})
        self.last_request = 0.0

    def allowed_url(self, url):
        parts = urlsplit(url)
        return parts.scheme == "https" and not parts.username and not parts.password and parts.hostname in self.hosts and parts.port in (None, 443)

    def request(self, url, *, params=None, headers=None, accept="json", json_body=None):
        request_headers = httpx.Headers(headers or {})
        if "Accept" not in request_headers:
            request_headers["Accept"] = {"json": "application/json", "xml": "application/xml, application/atom+xml, application/rss+xml, text/xml;q=0.9, */*;q=0.1",
                "html": "text/html, application/xhtml+xml;q=0.9, */*;q=0.1"}.get(accept, "*/*")
        for hop in range(6):
            if not self.allowed_url(url):
                raise ServiceError("source_boundary", "Requested URL or redirect is outside this source", source=self.source)
            wait = self.min_interval - (time.monotonic() - self.last_request)
            if wait > 0:
                time.sleep(wait)
            self.last_request = time.monotonic()
            try:
                response = (self.client.get(url, params=params, headers=request_headers, follow_redirects=False) if json_body is None else
                    self.client.post(url, params=params, json=json_body, headers=request_headers, follow_redirects=False))
            except httpx.TimeoutException:
                raise ServiceError("timeout", "Source did not respond within the request timeout", source=self.source, retryable=True) from None
            except httpx.HTTPError:
                raise ServiceError("connection_error", "Source connection failed", source=self.source, retryable=True) from None
            if response.is_redirect:
                if response.status_code in (301, 302, 303):
                    json_body = None
                url = urljoin(str(response.url), response.headers.get("location", ""))
                params = None
                continue
            break
        else:
            raise ServiceError("redirect_limit", "Source returned too many redirects", source=self.source)
        code = response.status_code
        if code == 429:
            raise ServiceError("rate_limited", "Source request limit reached; retry according to retry_after", source=self.source,
                retry_after=response.headers.get("retry-after"), retryable=True)
        if code in (401, 403):
            raise ServiceError("access_restricted", "Source rejected the current access credentials or network", status="restricted", source=self.source, http_status=code)
        if code in (404, 410):
            raise ServiceError("not_found_at_source", "Target was not found at this source", status="not_found", source=self.source, http_status=code)
        if code >= 400:
            raise ServiceError("provider_error", "Source returned an HTTP error", source=self.source, http_status=code, retryable=code >= 500)
        media = response.headers.get("content-type", "").split(";")[0].strip().lower()
        is_html = media in ('text/html', 'application/xhtml+xml') or response.content.lstrip().lower().startswith((b'<!doctype html', b'<html'))
        if accept != 'html' and is_html:
            challenged = bool(re.search(r"verify|human|captcha|robot|anubis|just a moment|access denied", response.text, re.I))
            raise ServiceError("access_challenge" if challenged else "unexpected_content", "Source returned HTML instead of the requested API data",
                status="restricted" if challenged else "error", source=self.source)
        try:
            payload = response.json() if accept == "json" else response.content
        except ValueError:
            raise ServiceError("invalid_response", "Source response could not be decoded as JSON", source=self.source) from None
        next_link = response.links.get("next", {}).get("url", "")
        page_cursor = parse_qs(urlsplit(next_link).query).get("page_token", [None])[0]
        page_number = parse_qs(urlsplit(next_link).query).get("page", [""])[0]
        preserved = encoded(payload) if accept == 'json' else response.content
        if is_html:
            from browser_adapters import clean_html
            preserved = clean_html(preserved, self.store.sanitizer)
        evidence = self.store.put(preserved,
            "application/json" if accept == "json" else (media or "application/octet-stream"), self.source, str(response.url), preserve_bytes=accept == "binary", role="provider_response",
            **({"next_cursor": page_cursor} if page_cursor else {}), **({"next_page": int(page_number)} if page_number.isdigit() else {}))
        return payload, evidence

    def validate(self, options, start, limit, cursor=None):
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= self.max_limit:
            raise ServiceError("invalid_range", f"start must be nonnegative; limit must be 1..{self.max_limit}")
        unknown = set(options) - set(self.options)
        if unknown:
            raise ServiceError("invalid_options", "Unsupported search options; see describe_source", fields=sorted(unknown))

    def page(self, rows, total, evidence, query, options, start, limit, cursor=None, more=None, evidence_refs=None):
        if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
            raise ServiceError("invalid_response", "Provider records do not have the expected structure", source=self.source)
        has_more = more if more is not None else (start + len(rows) < total if total is not None else bool(cursor))
        if not rows and has_more:
            raise ServiceError("incomplete_response", "Source reports more results but returned no records", source=self.source, evidence=evidence)
        artifact = self.store.put(encoded(rows), "application/json", self.source, evidence["url"], role="records",
            request={"query": query, "options": options, "start": start, "limit": limit}, evidence_ref=evidence["ref"],
            **({'evidence_refs':evidence_refs} if evidence_refs else {}))
        return {"status": "ok" if rows else "not_found", "source": self.source, "query": query, "options": options,
            "start": start, "requested": limit, "received": len(rows), "total": total, "has_more": has_more,
            "next": ({"cursor": cursor} if cursor else {"start": start + len(rows)}) if has_more else None,
            "records": artifact, "export": artifact, "evidence": evidence, "preview": [brief(r) for r in rows[:3]],
            "scope": "Only the named source and the requested result window were searched"}

    def export_page(self, result, export):
        if export not in (None, "json", "native"):
            raise ServiceError("export_not_implemented", "Requested export format is not implemented", status="not_implemented", source=self.source, requested_format=export, partial_result=result)
        if export == "native":
            result["export"] = result["evidence"]
        return result

    def fetched(self, rows, evidence, parts, available=("metadata", "abstract")):
        unknown = set(parts) - {"metadata", "abstract", "fulltext", "supplementary", "export"}
        if unknown:
            raise ServiceError("invalid_parts", "Unknown requested content", parts=sorted(unknown))
        result = self.page(rows, len(rows), evidence, "", {}, 0, len(rows))
        result["components"] = {part: {"status": "available", "artifact": result["records"]} if part in available else
            {"status": "not_offered", "reason": "This endpoint does not provide the requested content"} for part in parts}
        if any(v["status"] != "available" for v in result["components"].values()):
            result["status"] = "partial" if rows else "not_found"
        return result


class Crossref(APIAdapter):
    source = "crossref"
    hosts = ("api.crossref.org",)
    options = ("filter", "sort", "order", "query.bibliographic", "query.author", "query.title", "query.container-title", "query.affiliation", "select", "facet", "citation_style", "locale")
    max_limit = 1000
    export_types = {'bibtex': 'application/x-bibtex', 'ris': 'application/x-research-info-systems',
        'csl-json': 'application/vnd.citationstyles.csl+json', 'plain': 'text/x-bibliography',
        'rdf': 'application/rdf+xml', 'turtle': 'text/turtle',
        'unixref': 'application/vnd.crossref.unixref+xml', 'unixsd': 'application/vnd.crossref.unixsd+xml'}

    def native_export(self, identifier, format, *, style=None, locale=None):
        from scholarly import bibliography
        media = self.export_types[format]
        accept = media
        if format == 'plain':
            for key, value in [('style', style), ('locale', locale)]:
                if value is not None:
                    if not re.fullmatch(r'[A-Za-z0-9_-]+', value):
                        raise ServiceError('invalid_options', 'Citation style and locale must be service identifiers')
                    accept += '; ' + key + '=' + value
        raw, evidence = self.request('https://api.crossref.org/v1/works/' + quote(identifier, safe='') + '/transform',
            headers={'Accept': accept}, accept='xml' if 'xml' in media else 'json' if format == 'csl-json' else 'binary')
        if format in ('bibtex', 'ris'):
            records = bibliography(raw, media)
            observed = records[0].get('doi') if format == 'bibtex' and records else records[0].get('fields', {}).get('do', [None])[0] if records else None
            if len(records) != 1 or not observed or doi(observed).casefold() != identifier.casefold():
                raise ServiceError('identity_mismatch', 'Crossref citation identifies a different DOI', evidence=evidence)
        elif format == 'csl-json':
            if not isinstance(raw, dict) or str(raw.get('DOI', '')).casefold() != identifier.casefold():
                raise ServiceError('identity_mismatch', 'Crossref CSL identifies a different DOI', evidence=evidence)
            raw = encoded(raw)
        elif format in ('unixref', 'unixsd'):
            root = ElementTree.fromstring(raw)
            headers = root.findall('.//{*}doi_data/{*}doi')
            if not any((h.text or '').casefold() == identifier.casefold() for h in headers):
                raise ServiceError('identity_mismatch', 'Crossref XML has no matching deposited DOI', evidence=evidence)
        elif not raw.strip() or identifier.casefold() not in raw.decode('utf-8').casefold():
            raise ServiceError('identity_mismatch', 'Crossref transformed citation does not identify the DOI', evidence=evidence)
        canonical = 'application/json' if format == 'csl-json' else 'text/plain' if format == 'plain' else media
        return self.store.put(raw, canonical, self.source, evidence['url'], role='native_citation', format=format,
                              doi=identifier, source_media_type=media, evidence_ref=evidence['ref'])

    def export_page(self, result, export):
        if export not in self.export_types:
            return super().export_page(result, export)
        rows = json.loads(self.store.read(result['records']['ref'])[1])
        artifacts, errors = [], []
        for row in rows:
            if not row.get('DOI'):
                errors.append({'code': 'missing_doi', 'message': 'Native citation export requires DOI in selected fields'})
                continue
            try:
                artifacts.append(self.native_export(row['DOI'], export, style=result['options'].get('citation_style'), locale=result['options'].get('locale')))
            except ServiceError as error:
                errors.append({'doi': row['DOI'], **error.result})
        result['export'] = {'status': 'partial' if errors else 'available', 'artifacts': artifacts, 'errors': errors}
        if export in ('bibtex', 'ris', 'plain', 'turtle'):
            content = b'\n\n'.join(self.store.read(a['ref'])[1] for a in artifacts)
            media = 'text/plain' if export == 'plain' else self.export_types[export]
            result['export'].update(self.store.put(content, media, self.source, result['evidence']['url'], role='native_citations', parent_refs=[a['ref'] for a in artifacts]))
        if errors:
            result['status'] = 'partial'
        return result

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if any(k in options for k in ('citation_style', 'locale')) and export != 'plain':
            raise ServiceError('invalid_options', 'citation_style/locale apply only to plain citation export')
        params = {"query": query, "rows": limit, **{k:v for k,v in options.items() if k not in ('citation_style', 'locale')}}
        params.update({"cursor": cursor} if cursor else {"offset": start})
        raw, evidence = self.request("https://api.crossref.org/works", params=params)
        try:
            message = raw["message"]
            result = self.page(message["items"], message["total-results"], evidence, query, options, start, limit, message.get("next-cursor"))
        except (KeyError, TypeError):
            raise ServiceError("invalid_response", "Crossref response has no works result set", evidence=evidence) from None
        return self.export_page(result, export)

    def fetch(self, target, *, parts):
        if not target.startswith(('http://', 'https://', '10.', 'doi:')):
            candidates = self.search('', options={'query.title': target}, limit=5)
            candidates['status'] = 'selection_required' if candidates['received'] else 'not_found'
            return candidates
        identifier = doi(target)
        raw, evidence = self.request("https://api.crossref.org/works/" + quote(identifier, safe=""))
        row = raw.get("message")
        if not isinstance(row, dict) or str(row.get("DOI", "")).lower() != identifier.lower():
            raise ServiceError("identity_mismatch", "Crossref record does not match the requested DOI", evidence=evidence)
        result = self.fetched([row], evidence, parts, ("metadata", "export") + (("abstract",) if row.get("abstract") else ()))
        if "abstract" in parts and not row.get("abstract"):
            result["components"]["abstract"] = {"status": "not_found", "reason": "This Crossref record contains no abstract field"}
        if 'export' in parts:
            artifacts, errors = [], []
            for format in self.export_types:
                try:
                    artifacts.append({'format': format, 'artifact': self.native_export(identifier, format)})
                except ServiceError as error:
                    errors.append({'format': format, **error.result})
            result['components']['export'] = {'status': 'partial' if errors else 'available', 'artifacts': artifacts, 'errors': errors}
            if artifacts:
                result['components']['export']['artifact'] = artifacts[0]['artifact']
            if errors:
                result['status'] = 'partial'
        return result


class Crossmark(Crossref):
    """Crossmark deposits are exposed through the same public Crossref works API."""
    source = "crossmark"


class Arxiv(APIAdapter):
    source = "arxiv"
    hosts = ("export.arxiv.org", "arxiv.org", "www.arxiv.org")
    options = ("sort_by", "sort_order")
    max_limit = 2000
    min_interval = 3.0
    ns = {"a": "http://www.w3.org/2005/Atom", "o": "http://a9.com/-/spec/opensearch/1.1/", "x": "http://arxiv.org/schemas/atom"}

    def parse(self, raw):
        root = ElementTree.fromstring(raw)
        rows = []
        for entry in root.findall("a:entry", self.ns):
            identifier = entry.findtext("a:id", namespaces=self.ns)
            if identifier and "/errors" in identifier:
                raise ServiceError("invalid_query", "arXiv rejected this query")
            rows.append({"id": identifier, "title": entry.findtext("a:title", namespaces=self.ns),
                "abstract": entry.findtext("a:summary", namespaces=self.ns), "published": entry.findtext("a:published", namespaces=self.ns),
                "updated": entry.findtext("a:updated", namespaces=self.ns), "authors": [a.findtext("a:name", namespaces=self.ns) for a in entry.findall("a:author", self.ns)],
                "categories": [c.attrib for c in entry.findall("a:category", self.ns)],
                "links": [link.attrib for link in entry.findall("a:link", self.ns)],
                "doi": entry.findtext("x:doi", namespaces=self.ns), "journal_ref": entry.findtext("x:journal_ref", namespaces=self.ns),
                "comment": entry.findtext("x:comment", namespaces=self.ns)})
        return rows, int(root.findtext("o:totalResults", str(len(rows)), self.ns))

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if cursor:
            raise ServiceError("invalid_cursor", "arXiv uses start, not cursor")
        params = {"search_query": query, "start": start, "max_results": limit}
        params.update({{"sort_by": "sortBy", "sort_order": "sortOrder"}[k]: v for k, v in options.items()})
        raw, evidence = self.request("https://export.arxiv.org/api/query", params=params, accept="xml")
        rows, total = self.parse(raw)
        return self.export_page(self.page(rows, total, evidence, query, options, start, limit), export)

    def fetch(self, target, *, parts):
        value = re.sub(r"^arxiv:", "", target.strip(), flags=re.I)
        requested_format = 'pdf'
        if value.startswith(("http://", "https://")):
            parsed = urlsplit(value)
            if parsed.hostname not in self.hosts:
                raise ServiceError("source_boundary", "Target is outside arXiv")
            matched = re.fullmatch(r'/(abs|pdf|src|html)/(.+)', parsed.path)
            if not matched:
                raise ServiceError('invalid_target', 'Use an arXiv document URL')
            requested_format = matched[1] if matched[1] in ('html', 'src') else 'pdf'
            value = matched[2].removesuffix('.pdf')
        if not re.fullmatch(r"(?:[0-9]{4}\.[0-9]{4,5}|[a-zA-Z.-]+/[0-9]{7})(?:v[0-9]+)?", value):
            if not target.startswith(('http://', 'https://', 'arxiv:', 'arXiv:', '10.')) and any(c.isalpha() for c in target):
                result = self.search('ti:"' + target.replace('"', '\\"') + '"', options={}, limit=5)
                result['status'] = 'selection_required' if result['received'] else 'not_found'
                return result
            raise ServiceError("invalid_target", "Use an arXiv identifier or arXiv document URL")
        raw, evidence = self.request("https://export.arxiv.org/api/query", params={"id_list": value}, accept="xml")
        rows, _ = self.parse(raw)
        if not rows:
            raise ServiceError("not_found_at_source", "No arXiv record for this identifier", status="not_found", evidence=evidence)
        version = rows[0]["id"].split("/abs/")[-1]
        if value.rsplit("v", 1)[-1].isdigit() and "v" in value and version != value:
            raise ServiceError("identity_mismatch", "arXiv returned a different requested version", evidence=evidence)
        result = self.fetched(rows, evidence, parts, ("metadata", "abstract", "export"))
        downloads = {}
        for part, endpoint in [('fulltext', requested_format), ('supplementary', 'src')]:
            if part not in parts:
                continue
            try:
                if endpoint in downloads:
                    result['components'][part] = downloads[endpoint]
                    continue
                data, artifact = self.request(f"https://arxiv.org/{endpoint}/{quote(version, safe='/')}", accept='html' if endpoint == 'html' else 'binary')
                if endpoint == 'pdf':
                    import pymupdf
                    if not data.startswith(b"%PDF-"):
                        raise ServiceError("unexpected_content", "arXiv did not return a PDF")
                    with pymupdf.open(stream=data, filetype="pdf") as document:
                        if not len(document):
                            raise ServiceError("invalid_document", "PDF has no pages")
                        pages = len(document)
                    artifact = self.store.put(data, 'application/pdf', self.source, artifact["url"], version=version, pages=pages)
                elif endpoint == 'html':
                    from bs4 import BeautifulSoup
                    from browser_adapters import clean_html
                    soup = BeautifulSoup(data, 'html.parser')
                    if not soup.select_one('article.ltx_document') or not soup.select_one('h1.ltx_title_document'):
                        raise ServiceError('unexpected_content', 'arXiv did not return a rendered article for this version')
                    artifact = self.store.put(clean_html(data, self.store.sanitizer), 'text/html', self.source, artifact['url'], version=version, role='fulltext', format='html')
                elif endpoint == 'src' and data.startswith(b'\x1f\x8b'):
                    artifact = self.store.put(data, 'application/gzip', self.source, artifact['url'], version=version, role='submission_source', source_media_type=artifact['media_type'])
                result["components"][part] = {"status": "available", "artifact": artifact, "version": version}
                downloads[endpoint] = result['components'][part]
            except ServiceError as error:
                result["components"][part] = error.result
        result["status"] = "ok" if all(v["status"] == "available" for v in result["components"].values()) else "partial"
        result["version"] = version
        return result


class DBLP(APIAdapter):
    source = "dblp"
    hosts = ("dblp.org", "www.dblp.org", "dblp.uni-trier.de")

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if cursor:
            raise ServiceError("invalid_cursor", "DBLP uses start, not cursor")
        raw, evidence = self.request("https://dblp.org/search/publ/api", params={"q": query, "f": start, "h": limit, "format": "json"})
        hits = raw["result"]["hits"]
        rows = hits.get("hit", [])
        if isinstance(rows, dict): rows = [rows]
        return self.export_page(self.page([r["info"] for r in rows], int(hits["@total"]), evidence, query, options, start, limit), export)

    def fetch(self, target, *, parts):
        value = target
        if value.startswith("https://"):
            parsed = urlsplit(value)
            if parsed.hostname not in self.hosts or not parsed.path.startswith("/rec/"):
                raise ServiceError("source_boundary", "Use a DBLP record URL")
            value = parsed.path[5:]
        value = re.sub(r"\.(?:html|xml|bib)$", "", value)
        if not re.fullmatch(r"(?:journals|conf|books|reference|phd|tr)/[\w/.-]+", value) or ".." in value:
            raise ServiceError("invalid_target", "Use a DBLP publication key or record URL")
        raw, evidence = self.request("https://dblp.org/rec/" + value + ".xml", accept="xml")
        root = ElementTree.fromstring(raw)
        records = [{"kind": child.tag, "attributes": child.attrib, "fields": [{"name": f.tag, "value": "".join(f.itertext()), "attributes": f.attrib} for f in child]} for child in root]
        return self.fetched(records, evidence, parts, ("metadata", "export"))


class ZBMath(APIAdapter):
    source = "zbmath"
    hosts = ("api.zbmath.org", "zbmath.org")
    max_limit = 100
    options = ("Anywhere", "arXiv ID", "Author count", "Author name", "Biographic reference", "Database", "Document cited in summary/review", "Document type", "DOI", "Editor name", "External ID", "Keyword", "Language", "MSC", "Publisher", "Reference text", "Review text", "Reviewer ID", "Reviewer name", "Reviewing state", "Serial ID", "Software ID", "Software name", "Source", "State", "Title", "URL", "Year", "zbMATH Open document ID")

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if cursor:
            raise ServiceError('invalid_cursor','zbMATH uses start and limit, not a cursor')
        if options and query:
            raise ServiceError("invalid_options", "Use either a native query or structured fields; their combination is not defined")
        endpoint = "_structured_search" if options else "_search"
        page_number=start//limit
        rows,evidence=[],[]
        total=None
        while True:
            params={"page":page_number,"results_per_page":limit,**(options or {"search_string":query})}
            raw,proof=self.request('https://api.zbmath.org/v1/document/'+endpoint,params=params)
            evidence.append(proof)
            native=raw.get('result')
            reported=raw.get('status',{}).get('nr_total_results')
            reported=int(reported) if reported is not None else None
            if not isinstance(native,list) or any(not isinstance(row,dict) or not row.get('id') for row in native):
                raise ServiceError('invalid_response','zbMATH returned no native document array',evidence=proof)
            if len(evidence)>1 and reported!=total:
                raise ServiceError('range_mismatch','zbMATH result total changed between pages',evidence=evidence)
            total=reported
            first=page_number*limit
            if total is not None and len(native)!=min(limit,max(0,total-first)):
                raise ServiceError('range_mismatch','zbMATH page does not match its result count',evidence=proof)
            rows.extend(row for index,row in enumerate(native,first) if start<=index<start+limit)
            if len(rows)==limit or len(native)<limit or total is not None and first+len(native)>=total:
                break
            page_number+=1
        artifact=self.store.put(encoded(rows),'application/json',self.source,evidence[0]['url'],role='records',
                                request={'query':query,'options':options,'start':start,'limit':limit},evidence_refs=[proof['ref'] for proof in evidence])
        more=start+len(rows)<total if total is not None else len(native)==limit
        result={'status':'ok' if rows else 'not_found','source':self.source,'query':query,'options':options,'start':start,'requested':limit,
                'received':len(rows),'total':total,'has_more':more,'next':{'start':start+len(rows)} if more else None,
                'records':artifact,'export':artifact,'evidence':evidence[0] if len(evidence)==1 else {'artifacts':evidence},'preview':[brief(row) for row in rows[:3]]}
        return self.export_page(result,export)

    def fetch(self, target, *, parts):
        value = target
        requested_doi=None
        if re.match(r'^(?:10\.\d{4,9}/|doi:|https?://(?:dx\.)?doi\.org/)',value,re.I):
            requested_doi=doi(value)
            found=self.search('',options={'DOI':requested_doi},limit=2)
            if found['total']!=1:
                return {**found,'status':'selection_required' if found['received'] else 'not_found'}
            value=str(json.loads(self.store.read(found['records']['ref'])[1])[0]['id'])
        elif value.startswith(('https://','http://')):
            parsed=urlsplit(value)
            if parsed.hostname not in self.hosts:
                raise ServiceError('source_boundary','Use a zbMATH record URL or DOI')
            query=parse_qs(parsed.query).get('q',[])
            if query:
                matched=re.fullmatch(r'an:\s*([0-9]+(?:\.[0-9]+)?)',query[0],re.I)
                value=matched[1] if matched and len(query)==1 else ''
            else:
                value=parsed.path.removeprefix('/v1/document/').strip('/')
            if not re.fullmatch(r'[0-9]+(?:\.[0-9]+)?',value):
                raise ServiceError('invalid_target','This zbMATH URL identifies no single document')
        if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", value):
            found=self.search('',options={'Title':target},limit=20)
            return {**found,'status':'selection_required' if found['received'] else 'not_found'}
        raw, evidence = self.request("https://api.zbmath.org/v1/document/" + value)
        record = raw.get("result")
        if not isinstance(record, dict):
            raise ServiceError("invalid_response", "zbMATH document result is missing", evidence=evidence)
        actual=str(record.get('identifier') if '.' in value else record.get('id'))
        normalize=lambda number:'.'.join(str(int(part)) for part in number.split('.')) if re.fullmatch(r'\d+(?:\.\d+)?',number) else number
        if normalize(actual)!=normalize(value):
            raise ServiceError('identity_mismatch','zbMATH record does not match the requested identifier',evidence=evidence)
        if requested_doi:
            linked=[]
            for link in record.get('links') or []:
                if link.get('type')=='doi':
                    try:
                        linked.append(doi(link.get('identifier') or link.get('url') or '').casefold())
                    except ServiceError:
                        continue
            if requested_doi.casefold() not in linked:
                raise ServiceError('identity_mismatch','zbMATH document links contain no matching DOI',evidence=evidence)
        result=self.fetched([record],evidence,parts,('metadata','export'))
        result.update(target=target,identity={'zbmath_id':record.get('id'),'identifier':record.get('identifier'),'requested_doi':requested_doi})
        if 'abstract' in parts:
            entries=[]
            notice='zbMATH Open Web Interface contents unavailable due to conflicting licenses.'
            for index,entry in enumerate(record.get('editorial_contributions') or []):
                content=' '.join((entry.get('text') or '').split())
                state='restricted' if content==notice else 'source_page' if content else 'not_found'
                entries.append({'index':index,'type':entry.get('contribution_type'),'status':state})
            states={entry['status'] for entry in entries}
            status='source_page' if 'source_page' in states else 'restricted' if 'restricted' in states else 'not_found'
            result['components']['abstract']={'status':status,'artifact':result['records'],'selection':'/0/editorial_contributions','entries':entries,
                                              'scope':'Native reviews and summaries keep their labels; an author abstract is not inferred'}
            if status=='restricted':
                result['components']['abstract']['code']='content_license_restriction'
        if 'supplementary' in parts:
            references=record.get('references') or []
            result['components']['supplementary']={'status':'available' if references else 'not_found','artifact':result['records'],
                                                  'selection':'/0/references','reference_count':len(references),'scope':'Native indexed references; external links are not followed'}
        statuses={component['status'] for component in result['components'].values()}
        result['status']='ok' if statuses=={'available'} else 'restricted' if statuses=={'restricted'} else 'not_found' if statuses=={'not_found'} else 'partial'
        return result


class OpenAlex(APIAdapter):
    source = "openalex"
    hosts = ("api.openalex.org",)
    max_limit = 200
    options = ("filter", "sort", "select", "group_by", "corpus")

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        from openalex import search
        return search(self,query,options=options,start=start,limit=limit,cursor=cursor,export=export)

    def fetch(self, target, *, parts):
        from openalex import fetch
        return fetch(self,target,parts=parts)


class SemanticScholar(APIAdapter):
    source = "semantic-scholar"
    hosts = ("api.semanticscholar.org",)
    options = ("kind", "year", "fieldsOfStudy", "publicationTypes", "venue", "openAccessPdf", "minCitationCount", "publicationDateOrYear", "fields")
    max_limit=1000
    min_interval=1.05

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        from semantic_scholar import search
        return search(self,query,options=options,start=start,limit=limit,cursor=cursor,export=export)

    def fetch(self, target, *, parts):
        from semantic_scholar import fetch
        return fetch(self,target,parts=parts)


class OpenCitations(APIAdapter):
    source = "opencitations"
    hosts = ("api.opencitations.net",)
    options = ("direction", "filter", "sort", "require", "json")
    max_limit = 1000
    min_interval = 0.34

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if cursor:
            raise ServiceError("invalid_cursor", "Use start for the preserved citation-edge list")
        if query.startswith(("10.", "https://doi.org/")):
            query = "doi:" + doi(query)
        direction = options.get("direction", "references")
        if direction not in ('references', 'citations', 'citation', 'reference-count', 'citation-count', 'venue-citation-count'):
            raise ServiceError('invalid_options', 'Use a documented OpenCitations relation or count operation')
        if direction == 'citation':
            query = query.removeprefix('oci:')
            valid = re.fullmatch(r'\d+-\d+', query)
        elif direction == 'venue-citation-count':
            valid = re.fullmatch(r'issn:\d{4}-\d{3}[0-9Xx]', query)
        else:
            valid = re.fullmatch(r'(?:doi|pmid|omid):\S+', query)
        if not valid:
            raise ServiceError('invalid_query', 'Use DOI/PMID/OMID for document relations, OCI for citation, or ISSN for venue-citation-count')
        if export not in (None, 'json', 'native', 'csv') or (export == 'csv' and 'json' in options):
            raise ServiceError('invalid_export', 'Use json/native/csv; json transformations require JSON output')
        params = {k: v for k, v in options.items() if k != "direction"}
        url = 'https://api.opencitations.net/index/v2/' + direction + '/' + quote(query, safe='')
        if export == 'csv':
            import csv, io
            data, evidence = self.request(url, params={**params, 'format': 'csv'}, headers={'Accept': 'text/csv'}, accept='binary')
            reader = csv.DictReader(io.StringIO(data.decode('utf-8-sig')))
            raw = list(reader)
            if not reader.fieldnames or not ({'oci', 'count'} & set(reader.fieldnames)) or any(None in row for row in raw):
                raise ServiceError('invalid_response', 'OpenCitations returned no recognized CSV table', evidence=evidence)
            native = self.store.put(data, 'text/csv', self.source, evidence['url'], role='native_csv', evidence_ref=evidence['ref'])
        else:
            raw, evidence = self.request(url, params={**params, 'format': 'json'})
        if not isinstance(raw, list):
            raise ServiceError("invalid_response", "OpenCitations did not return a citation-edge array", evidence=evidence)
        result = self.page(raw[start:start + limit], len(raw), evidence, query, options, start, limit)
        if export == 'csv':
            output = io.StringIO(newline='')
            writer = csv.DictWriter(output, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(raw[start:start + limit])
            result['export'] = self.store.put(output.getvalue(), 'text/csv', self.source, evidence['url'], role='selected_csv', parent_ref=native['ref'], start=start, requested=limit)
            result['native_export'] = native
            result['export_scope'] = 'Requested window in export; complete provider CSV in native_export'
            return result
        return self.export_page(result, export)

    def fetch(self, target, *, parts):
        if set(parts) - {'metadata', 'abstract', 'fulltext', 'export', 'supplementary'}:
            raise ServiceError('invalid_parts', 'Use metadata, abstract, fulltext, export or supplementary')
        if target.startswith('https://opencitations.net/oci/'):
            target = 'oci:' + urlsplit(target).path.removeprefix('/oci/')
        operation = 'citation' if target.startswith('oci:') or re.fullmatch(r'\d+-\d+', target) else 'references'
        result = self.search(target, options={'direction': operation}, limit=1000)
        components = {}
        for part in parts:
            if part in ('metadata', 'export'):
                components[part] = {'status': 'available', 'artifact': result['evidence'], 'scope': 'Complete native citation relationship data'}
            elif part == 'supplementary' and operation == 'references':
                try:
                    incoming = self.search(target, options={'direction': 'citations'}, limit=1000)
                    components[part] = {'status': 'available', 'artifact': incoming['evidence'], 'scope': 'Incoming citation relationships'}
                except ServiceError as error:
                    components[part] = error.result
            else:
                components[part] = {'status': 'not_offered', 'reason': 'The citation index provides relationships, not article abstract or fulltext'}
        result.update(target=target, components=components)
        if any(c['status'] != 'available' for c in components.values()):
            result['status'] = 'partial'
        return result


class Numdam(APIAdapter):
    source = "numdam"
    hosts = ("www.numdam.org", "numdam.org")
    OAI = "{http://www.openarchives.org/OAI/2.0/}"
    JATS = "{http://jats.nlm.nih.gov}"
    XLINK = "{http://www.w3.org/1999/xlink}href"
    options = ("set", "from", "until", "metadata_format")

    def parse(self, raw):
        root = ElementTree.fromstring(raw)
        error = root.find(self.OAI + "error")
        if error is not None:
            code = error.get("code")
            raise ServiceError("not_found_at_source" if code in ("idDoesNotExist", "noRecordsMatch") else "invalid_query", error.text or "OAI error",
                status="not_found" if code in ("idDoesNotExist", "noRecordsMatch") else "error", oai_code=code)
        rows = []
        for record in root.iter(self.OAI + "record"):
            header = record.find(self.OAI + "header")
            identifier = header.findtext(self.OAI + "identifier")
            if header.get("status") == "deleted":
                rows.append({"id": identifier, "deleted": True})
                continue
            metadata = record.find(self.OAI + "metadata")
            front = next(iter(metadata), None)
            if front is None:
                raise ServiceError("invalid_response", "OAI record has no metadata")
            title = next(("".join(e.itertext()) for e in front.iter() if e.tag.split("}")[-1] in ("article-title", "title")), None)
            abstracts = ["".join(e.itertext()) for e in front.iter() if e.tag.split("}")[-1] == "abstract"]
            links = [{"url": e.get(self.XLINK), "media_type": e.get("content-type"), "label": "".join(e.itertext())} for e in front.iter() if e.tag.split("}")[-1] == "self-uri" and e.get(self.XLINK)]
            from xml.etree.ElementTree import tostring
            rows.append({"id": identifier, "title": title, "abstracts": abstracts, "links": links, "metadata_xml": tostring(metadata, encoding="unicode"),
                "datestamp": header.findtext(self.OAI + "datestamp")})
        token = next((e.text for e in root.iter(self.OAI + "resumptionToken")), None)
        return rows, token

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if query:
            raise ServiceError("keyword_search_not_implemented", "OAI supports collection/date enumeration; native keyword search needs its own fixed browser implementation", status="not_implemented")
        if start:
            raise ServiceError("invalid_range", "OAI enumeration uses cursor, not start")
        params = {"verb": "ListRecords", "resumptionToken": cursor} if cursor else {"verb": "ListRecords", "metadataPrefix": options.get("metadata_format", "eudml-article2"), **{k: v for k, v in options.items() if k != "metadata_format"}}
        raw, evidence = self.request("https://www.numdam.org/oai/", params=params, accept="xml")
        rows, token = self.parse(raw)
        result = self.page(rows, None, evidence, query, options, 0, limit, token)
        result["range_note"] = "OAI determines page size; all received records are preserved. Use extract for a smaller view."
        return self.export_page(result, export)

    def fetch(self, target, *, parts):
        value = target.removeprefix("oai:numdam.org:")
        if not re.fullmatch(r"[A-Za-z0-9_]+", value):
            raise ServiceError("invalid_target", "Use a Numdam native identifier, e.g. AIF_1956__6__1_0")
        raw, evidence = self.request("https://www.numdam.org/oai/", params={"verb": "GetRecord", "identifier": "oai:numdam.org:" + value, "metadataPrefix": "eudml-article2"}, accept="xml")
        rows, _ = self.parse(raw)
        if len(rows) != 1 or rows[0]["id"] != "oai:numdam.org:" + value or rows[0].get("deleted"):
            raise ServiceError("identity_mismatch", "Numdam did not return the requested active record", evidence=evidence)
        result = self.fetched(rows, evidence, parts, ("metadata", "export") + (("abstract",) if rows[0]["abstracts"] else ()))
        if "fulltext" in parts:
            pdf = next((link for link in rows[0]["links"] if link["media_type"] == "application/pdf"), None)
            if pdf:
                try:
                    data, artifact = self.request(pdf["url"], accept="binary")
                    import pymupdf
                    if not data.startswith(b"%PDF-"):
                        raise ServiceError("unexpected_content", "Numdam returned no PDF")
                    with pymupdf.open(stream=data, filetype="pdf") as doc:
                        pages = len(doc)
                    artifact = self.store.put(data, "application/pdf", self.source, artifact["url"], role="fulltext", pages=pages, identifier=rows[0]["id"])
                    result["components"]["fulltext"] = {"status": "available", "artifact": artifact}
                except ServiceError as error:
                    result["components"]["fulltext"] = error.result
        result["status"] = "ok" if all(v["status"] == "available" for v in result["components"].values()) else "partial"
        return result


class CORE(APIAdapter):
    source = "core"
    hosts = ("api.core.ac.uk",)
    options = ("sort",)
    min_interval = 2.1

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if cursor:
            raise ServiceError("invalid_cursor", "CORE uses start")
        raw, evidence = self.request("https://api.core.ac.uk/v3/search/works", params={"q": query, "offset": start, "limit": limit, **options})
        return self.export_page(self.page(raw["results"], raw["totalHits"], evidence, query, options, start, limit), export)

    def fetch(self, target, *, parts):
        value = target.strip()
        if value.startswith(('http://','https://')):
            parsed=urlsplit(value)
            if parsed.hostname not in ('core.ac.uk','www.core.ac.uk','api.core.ac.uk') or parsed.username or parsed.password:
                raise ServiceError('source_boundary','Use a CORE work URL')
            match=re.fullmatch(r'/(?:v3/)?works/(\d+)/?',parsed.path)
            if not match:raise ServiceError('invalid_target','Use a CORE work URL with its numeric ID')
            value=match[1]
        if not re.fullmatch(r"[0-9]+", value):
            result=self.search(value,options={},limit=5)
            result['status']='selection_required' if result['received'] else 'not_found'
            return result
        raw, evidence = self.request("https://api.core.ac.uk/v3/works/" + value)
        if not isinstance(raw,dict) or str(raw.get('id'))!=str(int(value)):
            raise ServiceError('identity_mismatch','CORE returned a different work ID',evidence=evidence)
        result=self.fetched([raw],evidence,parts,('metadata','export')+(('abstract',) if raw.get('abstract') else ()))
        if 'abstract' in parts and not raw.get('abstract'):
            result['components']['abstract']={'status':'not_found','reason':'This CORE record has no abstract'}
        if 'fulltext' in parts:
            content=raw.get('fullText')
            if content is None or content=='':
                component={'status':'not_found','reason':'This CORE record contains no indexed full text'}
            elif not isinstance(content,str):
                component={'status':'error','code':'invalid_response','reason':'CORE fullText was not text'}
            elif ' '.join(content.split())=='Not available for public API users.':
                component={'status':'restricted','code':'public_fulltext_restricted','reason':'CORE provides an access notice instead of full text for public API users'}
            else:
                artifact=self.store.put(content,'text/plain',self.source,evidence['url'],role='indexed_fulltext',work_id=raw['id'],metadata_ref=result['records']['ref'])
                component={'status':'available','artifact':artifact,'content_kind':'core_indexed_fulltext'}
            result['components']['fulltext']=component
        states={c['status'] for c in result['components'].values()}
        result['status']='ok' if not states or states=={'available'} else 'restricted' if states=={'restricted'} else 'not_found' if states=={'not_found'} else 'partial'
        return result


class Zenodo(APIAdapter):
    source = "zenodo"
    hosts = ("zenodo.org", "www.zenodo.org")
    options = ("sort", "communities", "type", "subtype", "access_right", "keywords")

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if cursor or start % limit:
            raise ServiceError("invalid_range", "Zenodo uses start as a multiple of limit")
        raw, evidence = self.request("https://zenodo.org/api/records", params={"q": query, "page": start // limit + 1, "size": limit, **options})
        total = raw["hits"]["total"]
        if isinstance(total, dict): total = total["value"]
        rows = [{**row, "title": row.get("metadata", {}).get("title"), "DOI": row.get("doi")} for row in raw["hits"]["hits"]]
        return self.export_page(self.page(rows, total, evidence, query, options, start, limit), export)

    def fetch(self, target, *, parts):
        filename = None
        value = target.strip()
        if value.startswith(("https://", "http://")):
            parsed = urlsplit(value)
            if parsed.hostname in self.hosts:
                match = re.fullmatch(r"/(?:api/)?records?/(\d+)(?:/files/(.+?)(?:/content)?)?/?", parsed.path)
                if not match:
                    raise ServiceError("invalid_target", "Use a Zenodo record or record-file URL")
                value, filename = match[1], unquote(match[2]) if match[2] else None
            elif parsed.hostname in ("doi.org", "dx.doi.org"):
                value = doi(value)
            else:
                raise ServiceError("source_boundary", "The target is outside Zenodo")
        value = re.sub(r"^(?:doi:)?10\.5281/zenodo\.", "", value)
        if not value.isdigit():
            result = self.search("metadata.title:" + json.dumps(target, ensure_ascii=False), options={}, limit=20)
            result["status"] = "selection_required" if result["received"] else "not_found"
            return result
        raw, evidence = self.request("https://zenodo.org/api/records/" + value)
        identifier = str(raw.get("id", ""))
        concept = str(raw.get("conceptrecid", ""))
        if value not in (identifier, concept):
            raise ServiceError("identity_mismatch", "Zenodo returned a different record", evidence=evidence)
        result = self.fetched([raw], evidence, parts, ("metadata", "export") + (("abstract",) if raw.get("metadata", {}).get("description") else ()))
        result.update(target=target, record_id=identifier, concept_id=concept or None,
            version_selection="concept_resolved_to_record" if value != identifier else "explicit_record")
        if "supplementary" in parts or "fulltext" in parts:
            files = raw.get("files", [])
            if not isinstance(files, list):
                raise ServiceError("invalid_response", "Zenodo file metadata is not in the expected format", evidence=evidence)
            result["files"] = files
            selected = [file for file in files if filename is None or file.get("key") == filename]
            acquired, failures = [], []
            import hashlib, mimetypes
            for file in selected:
                try:
                    link = file.get("links", {}).get("self")
                    if not link:
                        raise ServiceError("file_link_missing", "Zenodo did not provide this file's content link")
                    data, downloaded = self.request(link, accept="binary")
                    expected_size = file.get("size")
                    checksum = file.get("checksum", "")
                    algorithm, separator, expected_digest = checksum.partition(":")
                    if expected_size is not None and len(data) != expected_size:
                        raise ServiceError("file_integrity_mismatch", "Zenodo file size differs from the record metadata", evidence=downloaded)
                    if separator:
                        try:
                            actual_digest = hashlib.new(algorithm, data, usedforsecurity=False).hexdigest()
                        except ValueError:
                            raise ServiceError("checksum_algorithm_not_supported", "Zenodo reported an unsupported checksum algorithm", evidence=downloaded) from None
                        if actual_digest.lower() != expected_digest.lower():
                            raise ServiceError("file_integrity_mismatch", "Zenodo file checksum differs from the record metadata", evidence=downloaded)
                    media = mimetypes.guess_type(file["key"])[0] or downloaded["media_type"]
                    extra = {}
                    if data.startswith(b"%PDF-"):
                        import pymupdf
                        with pymupdf.open(stream=data, filetype="pdf") as document:
                            extra["pages"] = len(document)
                        media = "application/pdf"
                    artifact = self.store.put(data, media, self.source, downloaded["url"], preserve_bytes=True, role="record_file",
                        record_id=identifier, filename=file["key"], provider_checksum=checksum, checksum_verified=bool(separator),
                        metadata_ref=evidence["ref"], **extra)
                    acquired.append({"name": file["key"], "artifact": artifact})
                except ServiceError as error:
                    failures.append({"name": file.get("key"), **error.result})
            for part in ("supplementary", "fulltext"):
                if part in parts:
                    result["components"][part] = {"status": "partial" if failures else "available" if acquired else "not_found" if filename else "not_offered",
                        "artifacts": acquired, "failures": failures, "content_kind": "record_files", "requested_files": len(selected)}
        result["status"] = "ok" if all(component["status"] == "available" for component in result["components"].values()) else "partial"
        return result


class GitHub(APIAdapter):
    source = "github"
    hosts = ("api.github.com", "codeload.github.com", "raw.githubusercontent.com")
    options = ("kind", "sort", "order")
    fixed_repo = None

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if cursor or start % limit:
            raise ServiceError("invalid_range", "GitHub search start must be a multiple of limit")
        kind = options.get("kind", "repositories")
        if kind not in ("repositories", "commits", "issues"):
            raise ServiceError("public_feature_unavailable", "Use repositories, commits or issues. Code search requiring a separate GitHub credential is excluded.", status="unsupported")
        raw, evidence = self.request("https://api.github.com/search/" + kind,
            params={"q": query, "page": start // limit + 1, "per_page": limit, **{k: v for k, v in options.items() if k != "kind"}})
        result = self.page(raw["items"], raw["total_count"], evidence, query, options, start, limit)
        if raw.get("incomplete_results"):
            result.update(status="partial", incomplete_results=True)
        result["source_result_limit"] = 1000
        if start + len(raw["items"]) >= 1000 and result["has_more"]:
            result.update(next=None, continuation_limited=True)
        return self.export_page(result, export)

    def resolve(self, target):
        value = target
        if value.startswith("https://github.com/"):
            path = urlsplit(value).path.strip("/").split("/")
            if len(path) < 2:
                raise ServiceError("invalid_target", "Use a repository or exact file URL")
            value = "/".join(path[:2])
            if len(path) > 2:
                if path[2] not in ("blob", "tree") or len(path) < 4:
                    raise ServiceError("invalid_target", "Use a GitHub blob/tree URL or owner/repo@ref:path")
                value += "@" + path[3] + ":" + "/".join(path[4:])
        if self.fixed_repo and not re.match(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@", value) and not value.startswith(self.fixed_repo):
            value = self.fixed_repo + "@" + value
        match = re.fullmatch(r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(?:@([^:]+))?(?::(.*))?", value)
        if not match:
            raise ServiceError("invalid_target", "Use owner/repo@revision:path; path and revision can be omitted")
        repo, ref, path = match.groups()
        if self.fixed_repo and repo != self.fixed_repo:
            raise ServiceError("source_boundary", "This source is limited to its named proof library")
        if path and (".." in path.split("/") or path.startswith("/") or "\\" in path):
            raise ServiceError("invalid_target", "Repository path must be relative without parent traversal")
        if not ref:
            metadata, _ = self.request("https://api.github.com/repos/" + repo)
            ref = metadata["default_branch"]
        commit, evidence = self.request("https://api.github.com/repos/" + repo + "/commits/" + quote(ref, safe=""))
        revision = commit.get("sha", "")
        if not re.fullmatch(r"[0-9a-f]{40}", revision):
            raise ServiceError("invalid_response", "GitHub did not resolve the requested revision to a commit", evidence=evidence)
        return repo, revision, path, commit, evidence

    def fetch(self, target, *, parts):
        import base64
        repo, revision, path, commit, evidence = self.resolve(target)
        data, artifact = None, None
        if path:
            metadata, record_evidence = self.request("https://api.github.com/repos/" + repo + "/contents/" + quote(path, safe="/"), params={"ref": revision})
            if isinstance(metadata, dict) and metadata.get("type") == "file":
                if metadata.get("encoding") == "base64":
                    data = base64.b64decode(metadata["content"])
                elif metadata.get("git_url"):
                    blob, _ = self.request(metadata["git_url"])
                    if blob.get("encoding") == "base64":
                        data = base64.b64decode(blob["content"])
                if data is not None:
                    media = "text/plain" if b"\x00" not in data else "application/octet-stream"
                    try:
                        data.decode("utf-8")
                    except UnicodeDecodeError:
                        media = "application/octet-stream"
                    artifact = self.store.put(data, media, self.source, record_evidence["url"], preserve_bytes=True, revision=revision, path=path, role="repository_file")
            records = metadata if isinstance(metadata, list) else [metadata]
        else:
            records, record_evidence = [commit], evidence
            if any(part in parts for part in ("fulltext", "supplementary")):
                data, archive_evidence = self.request("https://api.github.com/repos/" + repo + "/zipball/" + revision, accept="binary")
                import io, zipfile
                if not zipfile.is_zipfile(io.BytesIO(data)):
                    raise ServiceError("invalid_document", "GitHub archive is not a ZIP file")
                artifact = self.store.put(data, "application/zip", self.source, archive_evidence["url"], revision=revision, repo=repo, role="repository_archive")
        result = self.fetched(records, record_evidence, parts, ("metadata", "export"))
        for part in ("fulltext", "supplementary"):
            if part in parts:
                result["components"][part] = {"status": "available", "artifact": artifact} if artifact else {"status": "not_found", "reason": "No file bytes for this repository target"}
        result.update(revision=revision, repository=repo, requested_target=target, revision_evidence=evidence)
        result["status"] = "ok" if all(c["status"] == "available" for c in result["components"].values()) else "partial"
        return result


class ProofLibrary(GitHub):
    options = ("revision", "path", "case_sensitive")

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if not query or cursor:
            raise ServiceError("invalid_query", "Use a nonempty literal declaration/source string and start, not cursor")
        target = self.fixed_repo + ("@" + options["revision"] if options.get("revision") else "")
        fetched = self.fetch(target, parts=["metadata", "fulltext"])
        artifact = fetched["components"]["fulltext"]["artifact"]
        raw = self.store.read(artifact["ref"])[1]
        import io, zipfile
        rows = []
        needle = query if options.get("case_sensitive", True) else query.casefold()
        with zipfile.ZipFile(io.BytesIO(raw)) as zipped:
            for member in zipped.infolist():
                if member.is_dir() or not member.filename.endswith((".lean", ".v", ".thy", ".md", "lean-toolchain")):
                    continue
                path = member.filename.partition("/")[2]
                if options.get("path") and not path.startswith(options["path"]):
                    continue
                try:
                    lines = zipped.read(member).decode("utf-8").splitlines()
                except UnicodeDecodeError:
                    continue
                for line_number, line in enumerate(lines, 1):
                    if needle in (line if options.get("case_sensitive", True) else line.casefold()):
                        rows.append({"path": path, "archive_member": member.filename, "line": line_number, "text": line, "revision": fetched["revision"]})
        result = self.page(rows[start:start + limit], len(rows), artifact, query, options, start, limit)
        result["repository_archive"] = artifact
        result["revision"] = fetched["revision"]
        result["scope"] = "Literal source-line search within the named library's exact commit; a match does not certify mathematical equivalence"
        return self.export_page(result, export)


class Mathlib(ProofLibrary):
    source = "mathlib"
    fixed_repo = "leanprover-community/mathlib4"


class MathComp(ProofLibrary):
    source = "math-comp"
    fixed_repo = "math-comp/math-comp"


class SoftwareHeritage(APIAdapter):
    source = "software-heritage"
    hosts = ("archive.softwareheritage.org",)
    options = ("with_visit",)

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if start:
            raise ServiceError("invalid_range", "Software Heritage ignores numeric offsets; use the returned next.cursor")
        raw, evidence = self.request("https://archive.softwareheritage.org/api/1/origin/search/" + quote(query, safe="") + "/",
            params={"limit": limit, **({"page_token": cursor} if cursor else {}), **options})
        if not isinstance(raw, list):
            raise ServiceError("invalid_response", "Software Heritage returned no origin list", evidence=evidence)
        result = self.page(raw, None, evidence, query, options, start, limit, cursor=evidence.get("next_cursor"), more=bool(evidence.get("next_cursor")))
        result["total"] = None
        return self.export_page(result, export)

    def fetch(self, target, *, parts):
        from software_heritage import fetch
        return fetch(self,target,parts)


def make_adapters(store, client=None):
    client = client or httpx.Client(timeout=httpx.Timeout(45, connect=20), follow_redirects=False,
        headers={"User-Agent": "scholarly-mcp/0.1 (local scholarly research)", "Accept": "application/json"})
    return {cls.source: cls(store, client=client) for cls in (Crossref, Crossmark, Arxiv, DBLP, ZBMath, OpenAlex, SemanticScholar, OpenCitations, Numdam, CORE, Zenodo, GitHub, Mathlib, MathComp, SoftwareHeritage)}
