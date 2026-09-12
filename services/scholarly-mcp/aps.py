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
        if cursor:
            raise ServiceError("invalid_range", "APS feed uses start and limit rather than a cursor")
        size=limit;page_number=start//size+1;rows=[];proofs=[];pages=[];errors=[];next_page=None;native_end=start;seen=set()
        while len(rows)<limit:
            offset=(page_number-1)*size
            try:
                raw,evidence=self.request("https://harvest.aps.org/v2/journals/articles",
                    params={"set":"openaccess","page":page_number,"per_page":size,**options})
                native=raw.get("data") if isinstance(raw,dict) else None
                if not isinstance(native,list) or len(native)>size or any(not isinstance(row,dict) for row in native):
                    raise ServiceError("invalid_response","APS did not return a valid article feed page",evidence=evidence)
                identifiers=[row.get('id') for row in native]
                if any(not isinstance(identifier,str) or not identifier for identifier in identifiers):
                    raise ServiceError("invalid_response","APS returned an article without an identifier",evidence=evidence)
                if len(set(identifiers))!=len(identifiers) or seen.intersection(identifiers):
                    raise ServiceError("inconsistent_pagination","APS repeated an article in the requested feed pages",evidence=evidence)
                next_page=evidence.get("next_page")
                if next_page is not None and next_page!=page_number+1:
                    raise ServiceError("inconsistent_pagination","APS returned an unexpected next page",evidence=evidence)
                selected=native[max(0,start-offset):start+limit-offset]
                if not selected and next_page is not None:
                    raise ServiceError("incomplete_response","APS omitted records before its next feed page",evidence=evidence)
            except ServiceError as error:
                if not rows:raise
                errors.append(error.result);break
            rows.extend(selected);proofs.append(evidence);native_end=offset+len(native);seen.update(identifiers)
            pages.append({"artifact":evidence,"native_start":offset,"received":len(native),"selected":len(selected)})
            if len(rows)>=limit or next_page is None:break
            page_number=next_page
        more=bool(errors) or start+len(rows)<native_end or next_page is not None
        result=self.page(rows,None,proofs[0],query,options,start,limit,more=more,
            evidence_refs=[proof['ref'] for proof in proofs])
        result['native_pages']=pages
        result['native_export_scope']='Original provider pages; records contains the exact requested window'
        if len(proofs)>1:result['evidence']={'artifacts':proofs}
        if errors:result.update(status='partial',errors=errors)
        return self.export_page(result,export)

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
