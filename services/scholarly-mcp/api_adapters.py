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

    def request(self, url, *, params=None, headers=None, accept="json"):
        for hop in range(6):
            parts = urlsplit(url)
            if parts.scheme != "https" or parts.username or parts.password or parts.hostname not in self.hosts or parts.port not in (None, 443):
                raise ServiceError("source_boundary", "Requested URL or redirect is outside this source", source=self.source)
            wait = self.min_interval - (time.monotonic() - self.last_request)
            if wait > 0:
                time.sleep(wait)
            self.last_request = time.monotonic()
            try:
                response = self.client.get(url, params=params, headers=headers, follow_redirects=False)
            except httpx.TimeoutException:
                raise ServiceError("timeout", "Source did not respond within the request timeout", source=self.source, retryable=True) from None
            except httpx.HTTPError:
                raise ServiceError("connection_error", "Source connection failed", source=self.source, retryable=True) from None
            if response.is_redirect:
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
        if accept in ("json", "xml") and (media == "text/html" or response.content.lstrip().lower().startswith((b"<!doctype html", b"<html"))):
            challenged = bool(re.search(r"verify|human|captcha|robot|anubis|just a moment|access denied", response.text, re.I))
            raise ServiceError("access_challenge" if challenged else "unexpected_content", "Source returned HTML instead of the requested API data",
                status="restricted" if challenged else "error", source=self.source)
        try:
            payload = response.json() if accept == "json" else response.content
        except ValueError:
            raise ServiceError("invalid_response", "Source response could not be decoded as JSON", source=self.source) from None
        next_link = response.links.get("next", {}).get("url", "")
        page_cursor = parse_qs(urlsplit(next_link).query).get("page_token", [None])[0]
        evidence = self.store.put(encoded(payload) if accept == "json" else response.content,
            "application/json" if accept == "json" else (media or "application/octet-stream"), self.source, str(response.url), preserve_bytes=accept == "binary", role="provider_response",
            **({"next_cursor": page_cursor} if page_cursor else {}))
        return payload, evidence

    def validate(self, options, start, limit, cursor=None):
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= self.max_limit:
            raise ServiceError("invalid_range", f"start must be nonnegative; limit must be 1..{self.max_limit}")
        unknown = set(options) - set(self.options)
        if unknown:
            raise ServiceError("invalid_options", "Unsupported search options; see describe_source", fields=sorted(unknown))

    def page(self, rows, total, evidence, query, options, start, limit, cursor=None, more=None):
        if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
            raise ServiceError("invalid_response", "Provider records do not have the expected structure", source=self.source)
        has_more = more if more is not None else (start + len(rows) < total if total is not None else bool(cursor))
        if not rows and has_more:
            raise ServiceError("incomplete_response", "Source reports more results but returned no records", source=self.source, evidence=evidence)
        artifact = self.store.put(encoded(rows), "application/json", self.source, evidence["url"], role="records",
            request={"query": query, "options": options, "start": start, "limit": limit}, evidence_ref=evidence["ref"])
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
    options = ("filter", "sort", "order", "query.bibliographic", "query.author", "query.title", "query.container-title", "query.affiliation", "select", "facet")
    max_limit = 1000

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        params = {"query": query, "rows": limit, **options}
        params.update({"cursor": cursor} if cursor else {"offset": start})
        raw, evidence = self.request("https://api.crossref.org/works", params=params)
        try:
            message = raw["message"]
            result = self.page(message["items"], message["total-results"], evidence, query, options, start, limit, message.get("next-cursor"))
        except (KeyError, TypeError):
            raise ServiceError("invalid_response", "Crossref response has no works result set", evidence=evidence) from None
        return self.export_page(result, export)

    def fetch(self, target, *, parts):
        identifier = doi(target)
        raw, evidence = self.request("https://api.crossref.org/works/" + quote(identifier, safe=""))
        row = raw.get("message")
        if not isinstance(row, dict) or str(row.get("DOI", "")).lower() != identifier.lower():
            raise ServiceError("identity_mismatch", "Crossref record does not match the requested DOI", evidence=evidence)
        result = self.fetched([row], evidence, parts, ("metadata", "export") + (("abstract",) if row.get("abstract") else ()))
        if "abstract" in parts and not row.get("abstract"):
            result["components"]["abstract"] = {"status": "not_found", "reason": "This Crossref record contains no abstract field"}
        return result


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
        if value.startswith(("http://", "https://")):
            parsed = urlsplit(value)
            if parsed.hostname not in self.hosts:
                raise ServiceError("source_boundary", "Target is outside arXiv")
            value = re.sub(r"^/(?:abs|pdf|src|html)/", "", parsed.path).removesuffix(".pdf")
        if not re.fullmatch(r"(?:[0-9]{4}\.[0-9]{4,5}|[a-zA-Z.-]+/[0-9]{7})(?:v[0-9]+)?", value):
            raise ServiceError("invalid_target", "Use an arXiv identifier or arXiv document URL")
        raw, evidence = self.request("https://export.arxiv.org/api/query", params={"id_list": value}, accept="xml")
        rows, _ = self.parse(raw)
        if not rows:
            raise ServiceError("not_found_at_source", "No arXiv record for this identifier", status="not_found", evidence=evidence)
        version = rows[0]["id"].split("/abs/")[-1]
        if value.rsplit("v", 1)[-1].isdigit() and "v" in value and version != value:
            raise ServiceError("identity_mismatch", "arXiv returned a different requested version", evidence=evidence)
        result = self.fetched(rows, evidence, parts, ("metadata", "abstract", "export"))
        for part, endpoint, kind in [("fulltext", "pdf", "application/pdf"), ("supplementary", "src", "application/octet-stream")]:
            if part not in parts:
                continue
            try:
                data, artifact = self.request(f"https://arxiv.org/{endpoint}/{quote(version, safe='/')}", accept="binary")
                if part == "fulltext":
                    import pymupdf
                    if not data.startswith(b"%PDF-"):
                        raise ServiceError("unexpected_content", "arXiv did not return a PDF")
                    with pymupdf.open(stream=data, filetype="pdf") as document:
                        if not len(document):
                            raise ServiceError("invalid_document", "PDF has no pages")
                        pages = len(document)
                    artifact = self.store.put(data, kind, self.source, artifact["url"], version=version, pages=pages)
                result["components"][part] = {"status": "available", "artifact": artifact, "version": version}
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
        if start % limit:
            raise ServiceError("invalid_range", "zbMATH start must be a multiple of limit")
        if options and query:
            raise ServiceError("invalid_options", "Use either a native query or structured fields; their combination is not defined")
        endpoint = "_structured_search" if options else "_search"
        params = {"page": start // limit, "results_per_page": limit, **(options or {"search_string": query})}
        raw, evidence = self.request("https://api.zbmath.org/v1/document/" + endpoint, params=params)
        rows = raw.get("result")
        if not isinstance(rows, list):
            raise ServiceError("invalid_response", "zbMATH did not return its document array", evidence=evidence)
        total = raw.get("status", {}).get("nr_total_results")
        if total is not None: total = int(total)
        return self.export_page(self.page(rows, total, evidence, query, options, start, limit, more=len(rows) == limit if total is None else None), export)

    def fetch(self, target, *, parts):
        value = target
        if value.startswith("https://zbmath.org/"):
            value = value.removeprefix("https://zbmath.org/")
        if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", value):
            raise ServiceError("invalid_target", "Use a zbMATH document number")
        raw, evidence = self.request("https://api.zbmath.org/v1/document/" + value)
        record = raw.get("result")
        if not isinstance(record, dict):
            raise ServiceError("invalid_response", "zbMATH document result is missing", evidence=evidence)
        return self.fetched([record], evidence, parts, ("metadata", "abstract", "export"))


class OpenAlex(APIAdapter):
    source = "openalex"
    hosts = ("api.openalex.org",)
    max_limit = 200
    options = ("filter", "sort", "select", "group_by")

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if not cursor and start % limit:
            raise ServiceError("invalid_range", "OpenAlex start must be a multiple of limit")
        params = {"search": query, "per-page": limit, **options}
        params.update({"cursor": cursor} if cursor else {"page": start // limit + 1})
        raw, evidence = self.request("https://api.openalex.org/works", params=params)
        return self.export_page(self.page(raw["results"], raw["meta"]["count"], evidence, query, options, start, limit, raw["meta"].get("next_cursor")), export)

    def fetch(self, target, *, parts):
        value = target.removeprefix("https://openalex.org/")
        if value.startswith(("10.", "doi:", "https://doi.org/")):
            value = "https://doi.org/" + doi(value)
        elif not re.fullmatch(r"W[0-9]+", value):
            raise ServiceError("invalid_target", "Use an OpenAlex W identifier or DOI")
        raw, evidence = self.request("https://api.openalex.org/works/" + quote(value, safe=""))
        return self.fetched([raw], evidence, parts, ("metadata", "export") + (("abstract",) if raw.get("abstract_inverted_index") else ()))


class SemanticScholar(APIAdapter):
    source = "semantic-scholar"
    hosts = ("api.semanticscholar.org",)
    options = ("year", "fieldsOfStudy", "publicationTypes", "venue", "openAccessPdf", "minCitationCount", "publicationDateOrYear", "fields")

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        params = {"query": query, "offset": start, "limit": limit,
            "fields": "title,authors,year,abstract,externalIds,url,openAccessPdf,publicationTypes", **options}
        raw, evidence = self.request("https://api.semanticscholar.org/graph/v1/paper/search", params=params)
        return self.export_page(self.page(raw["data"], raw.get("total"), evidence, query, options, start, limit, more="next" in raw), export)

    def fetch(self, target, *, parts):
        value = target
        if value.startswith(("10.", "https://doi.org/", "doi:")): value = "DOI:" + doi(value)
        if not re.fullmatch(r"(?:[0-9a-f]{40}|(?:DOI|ARXIV|PMID|CorpusId):\S+)", value, re.I):
            raise ServiceError("invalid_target", "Use a paper ID, DOI, ARXIV:id or CorpusId:id")
        raw, evidence = self.request("https://api.semanticscholar.org/graph/v1/paper/" + quote(value, safe=""),
            params={"fields": "title,authors,year,abstract,externalIds,url,openAccessPdf,publicationTypes,references,citations"})
        return self.fetched([raw], evidence, parts, ("metadata", "export") + (("abstract",) if raw.get("abstract") else ()))


class OpenCitations(APIAdapter):
    source = "opencitations"
    hosts = ("api.opencitations.net",)
    options = ("direction", "filter", "sort", "require")
    max_limit = 1000
    min_interval = 0.34

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if cursor:
            raise ServiceError("invalid_cursor", "Use start for the preserved citation-edge list")
        if query.startswith(("10.", "https://doi.org/")):
            query = "doi:" + doi(query)
        if not re.fullmatch(r"(?:doi|pmid|omid):\S+", query):
            raise ServiceError("invalid_query", "OpenCitations requires a DOI, PMID or OMID, not a keyword query")
        direction = options.get("direction", "references")
        if direction not in ("references", "citations"):
            raise ServiceError("invalid_options", "direction must be references or citations")
        params = {k: v for k, v in options.items() if k != "direction"}
        raw, evidence = self.request("https://api.opencitations.net/index/v2/" + direction + "/" + quote(query, safe=""), params=params)
        if not isinstance(raw, list):
            raise ServiceError("invalid_response", "OpenCitations did not return a citation-edge array", evidence=evidence)
        return self.export_page(self.page(raw[start:start + limit], len(raw), evidence, query, options, start, limit), export)

    def fetch(self, target, *, parts):
        return self.search(target, options={"direction": "references"}, limit=1000)


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
        value = target.removeprefix("https://core.ac.uk/works/")
        if not re.fullmatch(r"[0-9]+", value):
            raise ServiceError("invalid_target", "Use a CORE works identifier")
        raw, evidence = self.request("https://api.core.ac.uk/v3/works/" + value)
        available = ("metadata", "export") + (("abstract",) if raw.get("abstract") else ()) + (("fulltext",) if raw.get("fullText") else ())
        return self.fetched([raw], evidence, parts, available)


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
        return self.export_page(self.page(raw["hits"]["hits"], total, evidence, query, options, start, limit), export)

    def fetch(self, target, *, parts):
        value = re.sub(r"^(?:https://zenodo.org/(?:records?|record)/|https://doi.org/10.5281/zenodo\.|10.5281/zenodo\.)", "", target)
        if not value.isdigit():
            raise ServiceError("invalid_target", "Use a Zenodo record number or its record DOI")
        raw, evidence = self.request("https://zenodo.org/api/records/" + value)
        result = self.fetched([raw], evidence, parts, ("metadata", "export", "abstract"))
        if "supplementary" in parts or "fulltext" in parts:
            result["files"] = raw.get("files", [])
            result["status"] = "partial"
            for part in ("supplementary", "fulltext"):
                if part in parts:
                    result["components"][part] = {"status": "not_implemented", "reason": "Record file selection and download are pending; file metadata is preserved"}
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
        match = re.fullmatch(r"swh:1:(cnt|dir|rev|rel|snp):([0-9a-f]{40})(?:;.*)?", target)
        if match:
            kind, key = match.groups()
            endpoint = {"cnt": "content/sha1_git:", "dir": "directory/", "rev": "revision/", "rel": "release/", "snp": "snapshot/"}[kind]
            url = "https://archive.softwareheritage.org/api/1/" + endpoint + key + "/"
        elif target.startswith(("https://", "http://")):
            kind = "origin"
            url = "https://archive.softwareheritage.org/api/1/origin/" + quote(target, safe="") + "/get/"
        else:
            raise ServiceError("invalid_target", "Use an SWHID or an origin URL")
        raw, evidence = self.request(url)
        result = self.fetched(raw if isinstance(raw, list) else [raw], evidence, parts, ("metadata", "export"))
        if kind == "cnt" and any(part in parts for part in ("fulltext", "supplementary")):
            data, blob = self.request(url + "raw/", accept="binary")
            for part in ("fulltext", "supplementary"):
                if part in parts:
                    result["components"][part] = {"status": "available", "artifact": blob}
        result["target"] = target
        result["status"] = "ok" if all(c["status"] == "available" for c in result["components"].values()) else "partial"
        return result


def make_adapters(store, client=None):
    client = client or httpx.Client(timeout=httpx.Timeout(45, connect=20), follow_redirects=False,
        headers={"User-Agent": "scholarly-mcp/0.1 (local scholarly research)", "Accept": "application/json"})
    return {cls.source: cls(store, client=client) for cls in (Crossref, Arxiv, DBLP, ZBMath, OpenAlex, SemanticScholar, OpenCitations, Numdam, CORE, Zenodo, GitHub, Mathlib, MathComp, SoftwareHeritage)}
