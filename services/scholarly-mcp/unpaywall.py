"""Keyless Unpaywall API; the operator's required contact email stays internal."""
import json
from pathlib import Path
import re
from urllib.parse import quote

from api_adapters import APIAdapter, doi, brief
from scholarly import ServiceError, encoded


class Unpaywall(APIAdapter):
    source = "unpaywall"
    hosts = ("api.unpaywall.org",)
    options = ("is_oa",)
    max_limit = 1000

    def __init__(self, store, client=None, contact_email=None, contact_file=None):
        super().__init__(store, client)
        self.contact_email = contact_email
        self.contact_file = Path(contact_file) if contact_file else None

    def contact(self):
        address = self.contact_email
        if self.contact_file and self.contact_file.exists():
            try:
                address = json.loads(self.contact_file.read_text("utf-8-sig"))["email"]
            except (ValueError, KeyError, TypeError):
                raise ServiceError("contact_configuration_invalid", "The operator contact file must contain an email field") from None
        if not address:
            raise ServiceError("contact_email_required", "Unpaywall requires an operator contact email; configure the protected contact file. No API key or account is required")
        if not isinstance(address, str) or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", address):
            raise ServiceError("contact_configuration_invalid", "The configured contact email is not valid")
        self.store.sanitizer.secrets = tuple(sorted(set(self.store.sanitizer.secrets) | {address}, key=len, reverse=True))
        return address

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if cursor or not query or export not in (None, "json", "native"):
            raise ServiceError("invalid_options", "Use a title query, start/limit and json/native export")
        if options.get("is_oa") is not None and type(options["is_oa"]) is not bool:
            raise ServiceError("invalid_options", "is_oa must be a Boolean or null")
        address = self.contact()
        rows, evidence, total, more = [], [], None, False
        for page_number in range(start // 50 + 1, (start + limit - 1) // 50 + 2):
            params = {"query": query, "page": page_number, "email": address}
            if options.get("is_oa") is not None:
                params["is_oa"] = str(options["is_oa"]).lower()
            raw, observed = self.request("https://api.unpaywall.org/v2/search", params=params)
            native = raw.get("results") if isinstance(raw, dict) else raw
            if not isinstance(native, list) or not all(isinstance(row, dict) and isinstance(row.get("response"), dict) for row in native):
                raise ServiceError("invalid_response", "Unpaywall search returned no DOI result array", evidence=observed)
            evidence.append(observed)
            offset = (page_number - 1) * 50
            for index, row in enumerate(native, offset):
                if start <= index < start + limit:
                    rows.append({**row, "DOI": row["response"].get("doi"), "title": row["response"].get("title")})
            more = start + len(rows) < offset + len(native) or len(native) == 50
            if len(native) < 50:
                total = offset + len(native) if native or page_number == 1 else None
                break
        artifact = self.store.put(encoded(rows), "application/json", self.source, evidence[0]["url"], role="records",
            query=query, options=options, start=start, requested=limit, evidence_refs=[item["ref"] for item in evidence])
        return {"status": "ok" if rows else "not_found", "source": self.source, "query": query, "options": options,
            "start": start, "requested": limit, "received": len(rows), "total": total, "has_more": more,
            "next": {"start": start + len(rows)} if more else None, "records": artifact,
            "evidence": {"artifacts": evidence}, "export": {"artifacts": evidence} if export == "native" else artifact,
            "preview": [brief(row) for row in rows[:3]]}

    def fetch(self, target, *, parts):
        identifier = doi(target)
        raw, evidence = self.request("https://api.unpaywall.org/v2/" + quote(identifier, safe=""), params={"email": self.contact()})
        if not isinstance(raw, dict) or raw.get("doi", "").lower() != identifier.lower():
            raise ServiceError("identity_mismatch", "Unpaywall returned a different DOI", evidence=evidence)
        result = self.fetched([raw], evidence, parts, ("metadata", "export"))
        if "fulltext" in parts:
            result["components"]["fulltext"] = {"status": "not_offered", "reason": "Unpaywall provides OA location metadata; select the location's source separately to retrieve its document", "artifact": result["records"]}
        return result
