"""Scopus through its KUDOS browser session; no developer API credentials."""
import csv
import io
import json
import re
from urllib.parse import urlsplit, parse_qs

from browser_adapters import dismiss_cookies, goto_source
from scholarly import ServiceError, encoded


def primary_request(request, query):
    return request.get("documentClassification") == "primary" and request.get("query") == query


def scopus_records(payload):
    meta, rows = payload.get("metadata", {}), payload.get("items")
    if not isinstance(rows, list) or not all(isinstance(r, dict) and r.get("eid") for r in rows):
        raise ServiceError("invalid_response", "Scopus response contains no primary document records")
    total, offset = meta.get("totalCount"), meta.get("offset")
    capacity = meta.get("itemCount")
    if type(total) is not int or type(offset) is not int or type(capacity) is not int or len(rows) != min(capacity, max(0, total - offset)):
        raise ServiceError("invalid_response", "Scopus document range does not match its response metadata")
    return rows, total, offset


def reference_records(payload):
    meta,rows=payload.get('metadata',{}),payload.get('items')
    total,offset,capacity=meta.get('totalCount'),meta.get('offset'),meta.get('itemCount')
    if not isinstance(rows,list) or any(not isinstance(row,dict) for row in rows) or any(type(v) is not int for v in (total,offset,capacity)):
        raise ServiceError('invalid_response','Scopus returned no reference result range')
    if min(total,offset)<0 or capacity<1 or len(rows)!=min(capacity,max(0,total-offset)):
        raise ServiceError('range_mismatch','Scopus reference rows do not match their declared range')
    return rows,total,offset


class Scopus:
    source = "scopus"
    hosts = ("www-scopus-com.libproxy.knu.ac.kr", "www.scopus.com")

    def __init__(self, store, gateway):
        self.store, self.gateway = store, gateway

    def page(self):
        return self.gateway.open(self.source, "Scopus", self.hosts, "main")

    def relationships(self,record):
        eid=record['eid']
        if not re.fullmatch(r'2-s2\.0-\d+',eid):
            raise ServiceError('invalid_target','The Scopus record has no canonical EID')
        page=self.page()
        goto_source(page,'https://'+urlsplit(page.url).hostname+'/pages/publications/'+eid.removeprefix('2-s2.0-'),self.hosts,wait_until='domcontentloaded',timeout=45000)
        page.locator('#references').wait_for(timeout=45000)
        dismiss_cookies(page)
        components={}
        for kind,tab,path in [('references','references','/gateway/doc-details/documents/'+eid+'/references'),('citations','citedBy','/gateway/citation-overview/documents/'+eid.removeprefix('2-s2.0-')+'/cited')]:
            records,evidence=[],[]
            total=None
            try:
                label=page.locator('#'+tab).inner_text()
                count=re.search(r'\(([\d,]+)\)',label)
                if not count:
                    raise ServiceError('relation_count_missing','Scopus did not display the relationship count')
                total=int(count[1].replace(',',''))
                if total:
                    def matches(response):
                        return urlsplit(response.url).hostname in self.hosts and urlsplit(response.url).path==path
                    with page.expect_response(matches,timeout=45000) as event:
                        page.locator('#'+tab).click()
                    response=event.value
                    while True:
                        if response.status in (401,403):
                            raise ServiceError('access_restricted','Scopus restricted this relationship list',status='restricted')
                        if response.status!=200:
                            raise ServiceError('provider_error','Scopus relationship request failed',http_status=response.status)
                        payload=response.json()
                        evidence.append(self.store.put(encoded(payload),'application/json',self.source,response.url,role='relationship_response',eid=eid,relationship=kind))
                        if kind=='references':
                            rows,reported,offset=reference_records(payload)
                            if reported!=total or offset!=len(records):
                                raise ServiceError('range_mismatch','Scopus reference page or count changed',evidence=evidence[-1])
                        else:
                            rows=payload.get('documents')
                            if not isinstance(rows,list) or any(not isinstance(row,dict) or not row.get('eid') for row in rows):
                                raise ServiceError('invalid_response','Scopus returned no citing-document array')
                        records.extend(rows)
                        if len(records)==total:
                            break
                        if len(records)>total or not rows or kind=='citations':
                            raise ServiceError('incomplete_response','The relationship array does not match the document tab count')
                        next_button=page.locator('#references-panel').get_by_role('button',name='Next',exact=True)
                        if next_button.is_disabled():
                            raise ServiceError('incomplete_response','Scopus disabled Next before the reference list was complete')
                        with page.expect_response(matches,timeout=45000) as event:
                            next_button.click()
                        response=event.value
                status={'status':'available'}
            except ServiceError as error:
                status=error.result
            except Exception as error:
                status={'status':'error','code':'relationship_retrieval_failed','error_type':type(error).__name__}
            artifact=self.store.put(encoded(records),'application/json',self.source,page.url,role='relationship_records',eid=eid,relationship=kind,total=total,received=len(records))
            components[kind]={**status,'artifact':artifact,'received':len(records),'total':total,'evidence':evidence,
                'search_metadata_count':record.get(kind,{}).get('count')}
        return {'status':'available' if all(c['status']=='available' for c in components.values()) else 'partial',**components,
                'scope':'Actual document reference/cited-by tabs; search-summary counts are preserved separately'}

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ServiceError("invalid_range", "Scopus requires start >= 0 and limit 1..1000")
        if options or cursor or export not in (None, "json", "csv", "ris", "bibtex"):
            raise ServiceError("invalid_options", "Use the native advanced query; pagination is start/limit, export is json/csv/ris/bibtex")
        page = self.page()
        goto_source(page, "https://" + urlsplit(page.url).hostname + "/pages/search/publications?type=advanced", self.hosts, wait_until="domcontentloaded", timeout=45000)
        editor = page.locator('.monaco-editor[role="code"]')
        editor.wait_for(timeout=60000)
        dismiss_cookies(page)
        editor.click(position={"x": 120, "y": 35})
        page.keyboard.press("Control+A")
        page.keyboard.insert_text(query)

        def matches(response):
            if urlsplit(response.url).hostname not in self.hosts or urlsplit(response.url).path != "/gateway/documents/search" or response.request.method != "POST":
                return False
            try:
                return primary_request(response.request.post_data_json, query)
            except Exception:
                return False

        with page.expect_response(matches, timeout=60000) as pending:
            page.locator('[data-testid="advanced-search-button"]').click()
        response = pending.value
        rows, evidence, total, offset = [], [], None, 0
        while True:
            if response.status in (401, 403):
                raise ServiceError("access_restricted", "Scopus restricted the institution session", status="restricted")
            if response.status != 200:
                raise ServiceError("provider_error", "Scopus search failed", http_status=response.status)
            payload = response.json()
            native, observed_total, observed_offset = scopus_records(payload)
            if observed_offset != offset or total is not None and observed_total != total:
                raise ServiceError("range_mismatch", "Scopus returned a changed result range")
            total = observed_total
            evidence.append(self.store.put(encoded(payload), "application/json", self.source, response.url,
                role="source_response", query=query, offset=offset, total=total))
            rows.extend(row for i, row in enumerate(native, offset) if start <= i < start + limit)
            offset += len(native)
            if offset >= min(start + limit, total) or not native:
                break
            with page.expect_response(matches, timeout=60000) as pending:
                page.get_by_role("button", name="Next", exact=True).click()
            response = pending.value
        artifact = self.store.put(encoded(rows), "application/json", self.source, page.url,
            role="records", query=query, start=start, requested=limit, total=total)
        exported = artifact
        if export == "csv":
            stream = io.StringIO(newline="")
            fields = list(dict.fromkeys(k for row in rows for k in row))
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in row.items()} for row in rows)
            exported = self.store.put(stream.getvalue(), "text/csv", self.source, page.url,
                role="mechanical_export", format="csv", parent_ref=artifact["ref"])
        if export in ("ris", "bibtex"):
            exported = {"status": "unsupported", "code": "export_deferred",
                "reason": "Native export requires a separate web account and is deferred by user instruction; JSON records remain available"}
        more = start + len(rows) < total
        return {"status": "partial" if export in ("ris", "bibtex") else "ok" if rows else "not_found", "source": self.source,
            "query": query, "start": start, "requested": limit, "received": len(rows), "total": total,
            "has_more": more, "next": {"start": start + len(rows)} if more else None,
            "records": artifact, "export": exported, "evidence": evidence,
            "preview": [{k: r.get(k) for k in ("eid", "title", "pubYear", "doi")} for r in rows[:3]]}

    def fetch(self, target, *, parts):
        from api_adapters import doi
        if target.startswith(("http://", "https://")):
            parsed = urlsplit(target)
            if parsed.hostname in self.hosts:
                identifiers = parse_qs(parsed.query).get("eid", [])
                matched = re.search(r"/(2-s2\.0-\d+)(?:/|$)", parsed.path)
                publication = re.fullmatch(r"/pages/publications/(\d+)/?", parsed.path)
                target = identifiers[0] if len(identifiers) == 1 else matched[1] if matched else '2-s2.0-'+publication[1] if publication else ""
                if not re.fullmatch(r"2-s2\.0-\d+", target):
                    raise ServiceError("invalid_target", "This Scopus URL contains no document EID")
            elif parsed.hostname not in ("doi.org", "dx.doi.org"):
                raise ServiceError("source_boundary", "Use a Scopus document URL or DOI")
        if re.fullmatch(r"2-s2\.0-\d+", target):
            query = "EID(" + target + ")"
        else:
            try:
                query = 'DOI("' + doi(target) + '")'
            except ServiceError:
                result = self.search('TITLE("' + target.replace('"', " ") + '")', options={}, limit=20)
                result["status"] = "selection_required" if result["received"] else "not_found"
                return result
        result = self.search(query, options={}, limit=2)
        if result["total"] != 1:
            result["status"] = "selection_required" if result["received"] else "not_found"
            return result
        record = json.loads(self.store.read(result["records"]["ref"])[1])[0]
        components = {}
        for part in parts:
            if part in ("metadata", "export"):
                components[part] = {"status": "available", "artifact": result["records"], "format": "json"}
            elif part == "abstract":
                components[part] = {"status": "available", "artifact": result["records"]} if record.get("abstractText") else {"status": "not_found", "reason": "The Scopus record has no abstractText"}
            elif part == "fulltext":
                components[part] = {"status": "unsupported", "reason": "Scopus indexes documents; select the publisher separately for its full text"}
            elif part == "supplementary":
                try:
                    components[part] = self.relationships(record)
                except ServiceError as error:
                    components[part] = error.result
            else:
                raise ServiceError("invalid_parts", "Unknown requested content", part=part)
        return {"status": "ok" if all(v["status"] == "available" for v in components.values()) else "partial",
            "source": self.source, "target": target, "records": result["records"], "components": components, "evidence": result["evidence"]}
