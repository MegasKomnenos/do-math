"""Document retrieval through each publisher's own institutional/public route."""
from __future__ import annotations

from dataclasses import dataclass
import json
import re
import time
from urllib.parse import quote, urljoin, urlsplit

import httpx
from bs4 import BeautifulSoup

from api_adapters import doi
from browser_adapters import browser_download, clean_html, goto_source, require_source_url
from scholarly import ServiceError, encoded


@dataclass(frozen=True)
class Profile:
    source: str
    domains: tuple[str, ...]
    gateway_label: str | None
    abstract_selector: str = 'section.abstract, .abstract, #abstract, #Abs1, #abstracts'

    @property
    def hosts(self):
        return set(self.domains) | {host.replace('.', '-') + '.libproxy.knu.ac.kr' for host in self.domains}


PROFILES = [
    Profile("ams", ("www.ams.org", "ams.org", "pubs.ams.org"), "AMS"),
    Profile("cambridge", ("www.cambridge.org", "resolve.cambridge.org"), "CUP"),
    Profile("de-gruyter", ("www.degruyter.com", "www.degruyterbrill.com"), "De Gruyter"),
    Profile("jstor", ("www.jstor.org", "jstor.org"), "JSTOR"),
    Profile("oxford", ("academic.oup.com", "www.oxfordacademic.com"), "OUP"),
    Profile("science-direct", ("www.sciencedirect.com", "sciencedirect.com", "linkinghub.elsevier.com"), "ScienceDirect"),
    Profile("springer", ("link.springer.com", "link.springernature.com", "www.nature.com"), "Springer eJournal"),
    Profile("taylor-francis", ("www.tandfonline.com", "tandfonline.com"), "Taylor & Francis"),
    Profile("wiley", ("onlinelibrary.wiley.com", "www.onlinelibrary.wiley.com"), "Wiley Online Library"),
    Profile("aip", ("pubs.aip.org", "aip.scitation.org"), "AIP"),
    Profile("aps", ("www.aps.org", "journals.aps.org", "link.aps.org", "physics.aps.org"), "APS"),
    Profile("iop", ("iopscience.iop.org",), "IOP"),
    Profile("siam", ("epubs.siam.org", "www.siam.org"), None),
    Profile("project-euclid", ("projecteuclid.org", "www.projecteuclid.org"), None),
    Profile("theory-of-computing", ("theoryofcomputing.org", "www.theoryofcomputing.org"), None),
]


def publication_metadata(raw):
    soup = BeautifulSoup(raw, "html.parser")
    fields = {}
    for tag in soup.select("meta[name],meta[property]"):
        name = tag.get("name", tag.get("property", ""))
        if name.lower().startswith(("citation_", "dc.", "dc:", "dcterms.", "prism.", "og:")) and tag.get("content") is not None:
            fields.setdefault(name.lower(), []).append(tag["content"])
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            fields.setdefault("schema_org", []).append(json.loads(script.string or script.get_text()))
        except (ValueError, TypeError):
            continue
    return fields


def primary_pdf_links(raw, base):
    soup = BeautifulSoup(raw, "html.parser")
    urls = [urljoin(base, tag["content"]) for tag in soup.select('meta[name="citation_pdf_url"][content]')]
    if urls:
        return list(dict.fromkeys(urls))
    # These explicitly identify the current publication; unrelated PDF links are not candidates.
    for tag in soup.select('a[data-track-action="download pdf"],a[data-test="pdf-link"],a.article-tools__pdf,a.c-pdf-download__link,a[data-item-name="download-pdf"]'):
        if tag.get("href"):
            urls.append(urljoin(base, tag["href"]))
    return list(dict.fromkeys(urls))


class Publisher:
    def __init__(self, store, gateway, profile):
        self.store, self.gateway, self.profile = store, gateway, profile
        self.source = profile.source

    def resolve_target(self, target):
        if target.startswith(("10.", "doi:", "https://doi.org/", "http://doi.org/")):
            identifier = doi(target)
            url = "https://doi.org/" + quote(identifier, safe="/")
            with httpx.Client(timeout=30, follow_redirects=False) as client:
                for _ in range(5):
                    response = client.get(url)
                    if response.is_redirect:
                        url = urljoin(url, response.headers["location"])
                        if urlsplit(url).hostname not in {"doi.org", "dx.doi.org"}:
                            break
                    else:
                        raise ServiceError("identifier_resolution_failed", "DOI resolver did not provide a publisher location", http_status=response.status_code)
        else:
            identifier, url = None, target
        parsed = urlsplit(url)
        if parsed.scheme not in ("https", "http") or parsed.username or parsed.password or parsed.hostname not in self.profile.hosts:
            raise ServiceError("source_boundary", "Target resolves outside the named publisher; choose the correct source explicitly", source=self.source)
        return url, identifier

    def document(self, url):
        if self.profile.gateway_label:
            self.gateway.open(self.source, self.profile.gateway_label, self.profile.hosts, "body")
            portal = self.gateway.context.new_page()
            try:
                portal.goto("https://kudos.knu.ac.kr/pages/sub.htm?nav_code=kud1641346542", wait_until="domcontentloaded", timeout=45000)
                with self.gateway.context.expect_page(timeout=30000) as opened:
                    # Use the same authenticated KUDOS navigation function invoked by its actual DB shortcuts.
                    portal.evaluate("url => popup_gourl(url)", url)
                page = opened.value
                page.wait_for_url(lambda value: urlsplit(str(value)).hostname in self.profile.hosts, wait_until="domcontentloaded", timeout=55000)
                require_source_url(page.url, self.profile.hosts)
                return page
            finally:
                portal.close()
        page = self.gateway.public_page(self.source)
        goto_source(page, url, self.profile.hosts, wait_until="domcontentloaded", timeout=45000)
        return page

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        raise ServiceError("publisher_search_not_implemented", "This document adapter currently accepts exact publisher links and DOIs; native advanced search/export remains in development", status="not_implemented", source=self.source)

    def fetch(self, target, *, parts):
        unknown = set(parts) - {"metadata", "abstract", "fulltext", "supplementary", "export"}
        if unknown:
            raise ServiceError("invalid_parts", "Unknown requested content", parts=sorted(unknown))
        url, identifier = self.resolve_target(target)
        page = self.document(url)
        try:
            try:
                page.wait_for_function("() => [...document.querySelectorAll('meta[name],meta[property]')].some(m=>/citation_title|dc[.:]title|og:title/i.test(m.name||m.getAttribute('property')||'')) || [...document.querySelectorAll('h1')].some(h=>h.textContent.trim())", timeout=20000)
            except Exception:
                raise ServiceError("document_not_ready", "Publisher did not initialize a document page", source=self.source) from None
            body = page.locator("body").inner_text()
            if re.search(r"^(?:Access Denied|Just a moment|Attention Required|403 Forbidden)|CPE00001|Verify you are human", page.title() + "\n" + body[:1000], re.I):
                raise ServiceError("publisher_access_restricted", "Publisher returned an access/error page", status="restricted", source=self.source)
            require_source_url(page.url, self.profile.hosts)
            raw = page.content()
            metadata = publication_metadata(raw)
            titles = metadata.get("citation_title", metadata.get("dc.title", metadata.get("dc:title", [])))
            if not titles:
                raise ServiceError("metadata_not_identified", "Publisher page has no recognized publication title metadata", source=self.source)
            observed_dois = metadata.get("citation_doi", [])
            if identifier and observed_dois and identifier.lower() not in {x.lower().removeprefix("https://doi.org/") for x in observed_dois}:
                raise ServiceError("identity_mismatch", "Publisher metadata contains a different DOI", source=self.source)
            source_page = self.store.put(clean_html(raw, self.store.sanitizer), "text/html", self.source, page.url, role="source_page", requested_target=target)
            record = {"title": titles[0], "doi": identifier, "metadata": metadata, "url": self.store.sanitizer.url(page.url)}
            artifact = self.store.put(encoded([record]), "application/json", self.source, page.url, role="records", evidence_ref=source_page["ref"])
            components = {}
            for part in parts:
                if part in ("metadata", "export"):
                    components[part] = {"status": "available", "artifact": artifact, "format": "source_metadata_json"}
                elif part == "abstract":
                    nodes = page.locator(self.profile.abstract_selector).filter(visible=True)
                    if nodes.count():
                        content = "\n".join(nodes.all_inner_texts())
                        html = "\n".join(node.inner_html() for node in nodes.all())
                        abstract = self.store.put(clean_html(html, self.store.sanitizer), "text/html", self.source, page.url, role="source_abstract_region", parent_ref=source_page["ref"])
                        components[part] = {"status": "available" if content.strip() else "source_page", "artifact": abstract, "region_text_present": bool(content.strip())}
                    else:
                        components[part] = {"status": "source_page", "artifact": source_page, "reason": "Abstract region is not yet identified for this page layout"}
                elif part == "fulltext":
                    links = primary_pdf_links(raw, page.url)
                    if not links:
                        components[part] = {"status": "not_implemented", "reason": "No recognized document-bound PDF control; further layout/full-HTML handling is pending", "artifact": source_page}
                        continue
                    try:
                        data, media, obtained = browser_download(self.gateway.context, links[0], self.profile.hosts)
                        if not data.startswith(b"%PDF-"):
                            raise ServiceError("unexpected_content", "Publisher document control returned non-PDF content")
                        import pymupdf
                        with pymupdf.open(stream=data, filetype="pdf") as doc:
                            pages = len(doc)
                        pdf = self.store.put(data, "application/pdf", self.source, obtained, role="fulltext", pages=pages, target=target, publication_metadata_ref=artifact["ref"])
                        components[part] = {"status": "available", "artifact": pdf}
                    except ServiceError as error:
                        components[part] = error.result
                else:
                    components[part] = {"status": "source_page", "artifact": source_page, "reason": "Supplementary content is preserved in its source context; automatic attachment retrieval is pending"}
            return {"status": "ok" if all(item["status"] == "available" for item in components.values()) else "partial", "source": self.source,
                "target": target, "records": artifact, "source_page": source_page, "components": components,
                "identity": {"requested_doi": identifier, "observed_dois": observed_dois, "basis": "Exact publisher URL and available publisher metadata; file-level bibliography review is separate"}}
        finally:
            page.close()


def make_publishers(store, gateway):
    return {profile.source: Publisher(store, gateway, profile) for profile in PROFILES}
