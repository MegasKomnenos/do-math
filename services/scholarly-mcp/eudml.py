"""EuDML's public CQL/OpenSearch and NLM metadata interfaces."""
import re
from urllib.parse import urlsplit

import httpx
from defusedxml import ElementTree

from api_adapters import APIAdapter
from scholarly import ServiceError, encoded

NS = {"os": "http://a9.com/-/spec/opensearch/1.1/", "dc": "http://purl.org/dc/elements/1.1/"}
CQL_TIMEOUT = httpx.Timeout(90, connect=20)
NLM_TIMEOUT = httpx.Timeout(120, connect=20)
BODY_METADATA = {"front", "article-meta", "book-meta", "book-part-meta", "toc", "book-part-id", "self-uri", "ext-link"}
BODY_CONTAINERS = {"body", "book-body", "book-part"}


def parse_rss(data):
    root = ElementTree.fromstring(data)
    channel = root.find("channel")
    if root.tag != "rss" or channel is None:
        raise ServiceError("invalid_response", "EuDML did not return an RSS search result")
    try:
        total = int(channel.findtext("os:totalResults", namespaces=NS))
        offset = int(channel.findtext("os:startIndex", namespaces=NS))
    except (ValueError, TypeError):
        raise ServiceError("invalid_response", "EuDML RSS contains no valid total and startIndex") from None
    rows = []
    for item in channel.findall("item"):
        identifier = item.findtext("guid", "")
        match = re.fullmatch(r"urn:eudml:doc:(\d+)", identifier)
        if not match:
            raise ServiceError("invalid_response", "EuDML RSS item has no native document identifier")
        native = {}
        for child in item:
            native.setdefault(child.tag, []).append("".join(child.itertext()))
        rows.append({"id": match[1], "title": item.findtext("title"), "url": item.findtext("link"),
            "authors": ["".join(author.itertext()) for author in item.findall("dc:creator", NS)],
            "year": item.findtext("dc:date", namespaces=NS), "pubDate": item.findtext("pubDate"),
            "native_fields": native, "raw_xml": ElementTree.tostring(item, encoding="unicode")})
    return rows, total, offset


def has_native_body(root):
    def contains_content(node):
        if (node.text or "").strip():
            return True
        for child in node:
            name = child.tag.split("}")[-1]
            if name in BODY_METADATA:
                if (child.tail or "").strip():
                    return True
                continue
            if name in BODY_CONTAINERS:
                if contains_content(child):
                    return True
            else:
                return True
            if (child.tail or "").strip():
                return True
        return False
    return any(contains_content(node) for node in root if node.tag.split("}")[-1] in ("body", "book-body"))


class EuDML(APIAdapter):
    source = "eudml"
    hosts = ("eudml.org", "www.eudml.org")
    max_limit = 1000

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if cursor or export not in (None, "json", "native", "rss", "xml", "html"):
            raise ServiceError("invalid_options", "EuDML uses a native CQL query, start/limit and json/rss/xml/html export")
        params = {"q": query, "startIndex": start, "count": limit, "format": "rss"}
        raw, evidence = self.request("https://eudml.org/api/search", params=params, accept="xml", timeout=CQL_TIMEOUT)
        rows, total, offset = parse_rss(raw)
        if offset != start:
            raise ServiceError("range_mismatch", "EuDML returned another result offset", evidence=evidence)
        result = self.page(rows, total, evidence, query, options, start, limit)
        if export in ("native", "rss"):
            result["export"] = evidence
        elif export in ("xml", "html"):
            data, native = self.request("https://eudml.org/api/search", params={**params, "format": export}, accept="xml" if export == "xml" else "html", timeout=CQL_TIMEOUT)
            identifiers = set(re.findall(r"(?:urn:eudml:doc:|/doc/)(\d+)", data.decode("utf-8")))
            if not {row["id"] for row in rows}.issubset(identifiers):
                result.update(status="partial", export={"status": "error", "code": "export_identity_unverified", "artifact": native})
            else:
                result["export"] = native
        return result

    def fetch(self, target, *, parts):
        value = target.removeprefix("urn:eudml:doc:")
        if value.startswith(("http://", "https://")):
            parsed = urlsplit(value)
            match = re.fullmatch(r"/(?:doc|api/rest)/(\d+)/?", parsed.path)
            if parsed.hostname not in self.hosts or not match:
                raise ServiceError("source_boundary", "Use an EuDML document identifier or document URL")
            value = match[1]
        if not value.isdigit():
            literal = value.replace("\\", "\\\\").replace('"', '\\"')
            result = self.search('defName = "' + literal + '"', options={}, limit=20)
            result["status"] = "selection_required" if result["received"] else "not_found"
            return result
        raw, evidence = self.request("https://eudml.org/api/rest/" + value, params={"format": "eudml-nlm"}, headers={"User-Agent": f"python-httpx/{httpx.__version__}"}, accept="xml", timeout=NLM_TIMEOUT)
        root = ElementTree.fromstring(raw)
        headers = [root.find(path) for path in ("./{*}front/{*}article-meta", "./{*}book-meta", "./{*}front/{*}book-meta", "./{*}book-part-meta")]
        header = next((node for node in headers if node is not None), None)
        if header is None:
            raise ServiceError("metadata_layout_not_implemented", "This EuDML record has no recognized article/book metadata header", status="not_implemented", evidence=evidence)
        identifiers = ["".join(node.itertext()).strip() for node in header if node.attrib.get("pub-id-type", node.attrib.get("book-id-type")) == "eudml-id"]
        if "urn:eudml:doc:" + value not in identifiers:
            raise ServiceError("identity_mismatch", "EuDML NLM record does not contain the requested EuDML identifier", evidence=evidence)
        titles = [header.find(path) for path in ("./{*}title-group/{*}article-title", "./{*}book-title-group/{*}book-title", "./{*}title-group/{*}title")]
        title = next(("".join(node.itertext()) for node in titles if node is not None), None)
        abstract = any(node.tag.split("}")[-1] in ("abstract", "trans-abstract") for node in header)
        full_body = has_native_body(root)
        links = [{"label": "".join(node.itertext()), "attributes": dict(node.attrib)} for node in root.iter() if node.tag.split("}")[-1] in ("self-uri", "ext-link")]
        record = {"id": value, "title": title, "links": links, "native_metadata": evidence}
        artifact = self.store.put(encoded([record]), "application/json", self.source, evidence["url"], role="records", target=value)
        components = {}
        for part in parts:
            if part in ("metadata", "export"):
                components[part] = {"status": "available", "artifact": evidence}
            elif part == "abstract":
                components[part] = {"status": "available", "artifact": evidence} if abstract else {"status": "not_found", "reason": "This native metadata record has no abstract element"}
            elif part == "fulltext":
                components[part] = {"status": "available", "artifact": evidence} if full_body else {"status": "not_offered", "reason": "This EuDML endpoint provides metadata and external full-text links; select the original repository separately"}
            elif part == "supplementary":
                components[part] = {"status": "available", "artifact": evidence, "content_kind": "native_metadata_and_links"}
            else:
                raise ServiceError("invalid_parts", "Unknown requested content", part=part)
        return {"status": "ok" if all(c["status"] == "available" for c in components.values()) else "partial", "source": self.source,
            "target": value, "records": artifact, "components": components, "evidence": evidence}
