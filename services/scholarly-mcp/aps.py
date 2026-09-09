"""APS's keyless open-access Harvest API; institutional access is a separate source."""
import re
from urllib.parse import quote

from api_adapters import APIAdapter, doi
from scholarly import ServiceError


class APS(APIAdapter):
    source = "aps"
    hosts = ("harvest.aps.org",)
    options = ("from", "until", "date", "journals")
    max_limit = 100

    def page(self, rows, *args, **kwargs):
        result = super().page(rows, *args, **kwargs)
        result["preview"] = [{"id": row.get("id"), "title": row.get("title"), "date": row.get("date"),
            "author_count": len(row.get("authors", []))} for row in rows[:3]]
        return result

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if query:
            raise ServiceError("keyword_search_not_offered", "The public APS Harvest API uses date/journal filters; leave query empty. Keyword search belongs to the institutional journal interface", status="unsupported")
        if start % limit or cursor:
            raise ServiceError("invalid_range", "APS feed start must be a multiple of limit")
        raw, evidence = self.request("https://harvest.aps.org/v2/journals/articles", params={"set": "openaccess", "page": start // limit + 1, "per_page": limit, **options})
        rows = raw.get("data")
        if not isinstance(rows, list):
            raise ServiceError("invalid_response", "APS did not return an article feed", evidence=evidence)
        return self.export_page(self.page(rows, None, evidence, query, options, start, limit, more=bool(evidence.get("next_page"))), export)

    def fetch(self, target, *, parts):
        identifier = doi(target)
        if not identifier.lower().startswith("10.1103/"):
            raise ServiceError("source_boundary", "Use an APS DOI")
        url = "https://harvest.aps.org/v2/journals/articles/" + quote(identifier, safe="/")
        raw, evidence = self.request(url)
        row = raw.get("data")
        if not isinstance(row, dict) or row.get("id", "").lower() != identifier.lower():
            raise ServiceError("identity_mismatch", "APS returned a different article", evidence=evidence)
        result = self.fetched([row], evidence, parts, ("metadata", "export") + (("abstract",) if row.get("abstract") else ()))
        if "fulltext" in parts:
            try:
                data, native = self.request(url, headers={"Accept": "application/pdf"}, accept="binary")
                if not data.startswith(b"%PDF-"):
                    raise ServiceError("unexpected_content", "APS did not return PDF content", evidence=native)
                import pymupdf
                with pymupdf.open(stream=data, filetype="pdf") as document:
                    pages = len(document)
                pdf = self.store.put(data, "application/pdf", self.source, native["url"], role="fulltext", target=identifier, pages=pages)
                result["components"]["fulltext"] = {"status": "available", "artifact": pdf}
            except ServiceError as error:
                result["components"]["fulltext"] = error.result
        if "supplementary" in parts:
            obtained, failures = [], []
            for format, accept in (("xml", "application/xml"), ("bagit_zip", "application/zip")):
                try:
                    _, native = self.request(url, headers={"Accept": accept}, accept="xml" if format == "xml" else "binary")
                    obtained.append({"format": format, "artifact": native})
                except ServiceError as error:
                    failures.append({"format": format, **error.result})
            result["components"]["supplementary"] = {"status": "available" if not failures else "partial", "artifacts": obtained, "failures": failures}
        result["status"] = "ok" if all(c["status"] == "available" for c in result["components"].values()) else "partial"
        return result
