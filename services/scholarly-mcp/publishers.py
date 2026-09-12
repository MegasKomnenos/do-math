"""Document retrieval through each publisher's own institutional/public route."""
from __future__ import annotations

from dataclasses import dataclass
import json
import csv
import io
import re
import time
from urllib.parse import quote, urljoin, urlsplit, urlunsplit, unquote, urlencode, parse_qs

import httpx
from bs4 import BeautifulSoup

from api_adapters import doi
from browser_adapters import browser_download, clean_html, goto_source, require_source_url, dismiss_cookies, is_access_challenge
from scholarly import ServiceError, encoded, bibliography


@dataclass(frozen=True)
class Profile:
    source: str
    domains: tuple[str, ...]
    gateway_label: str | None
    abstract_selector: str = 'section.abstract, .abstract, #abstract, #Abs1, #abstracts'
    file_domains: tuple[str, ...] = ()

    @property
    def hosts(self):
        return set(self.domains) | {host.replace('.', '-') + '.libproxy.knu.ac.kr' for host in self.domains}

    @property
    def download_hosts(self):
        return self.hosts | set(self.file_domains) | {host.replace('-', '--').replace('.', '-') + '.libproxy.knu.ac.kr' for host in self.file_domains}


PROFILES = [
    Profile("ams", ("www.ams.org", "ams.org", "pubs.ams.org"), "AMS"),
    Profile("cambridge", ("www.cambridge.org", "resolve.cambridge.org"), "CUP", '.col.sec.summary, section.abstract, .abstract', file_domains=('static.cambridge.org',)),
    Profile("de-gruyter", ("www.degruyter.com", "www.degruyterbrill.com"), "De Gruyter"),
    Profile("jstor", ("www.jstor.org", "jstor.org"), "JSTOR", file_domains=('artstor-collections.s3.amazonaws.com','sequoia-forum-media.s3.amazonaws.com')),
    Profile("oxford", ("academic.oup.com", "www.oxfordacademic.com"), "OUP", file_domains=("watermark02.silverchair.com","oup.silverchair-cdn.com")),
    Profile("science-direct", ("www.sciencedirect.com", "sciencedirect.com", "linkinghub.elsevier.com"), "ScienceDirect", file_domains=('pdf.sciencedirectassets.com','ars.els-cdn.com')),
    Profile("springer", ("link.springer.com", "link.springernature.com", "www.nature.com"), "Springer eJournal", file_domains=('citation-needed.springer.com','media.springernature.com')),
    Profile("taylor-francis", ("www.tandfonline.com", "tandfonline.com"), "Taylor"),
    Profile("wiley", ("onlinelibrary.wiley.com", "www.onlinelibrary.wiley.com"), "Wiley Online Library", '.article-section__abstract'),
    Profile("aip", ("pubs.aip.org", "aip.scitation.org"), "AIP", 'section.abstract:not(.abstractBorder)', file_domains=('watermark02.silverchair.com',)),
    Profile("aps", ("www.aps.org", "journals.aps.org", "link.aps.org", "physics.aps.org"), "APS", '#abstract-section-content'),
    Profile("iop", ("iopscience.iop.org",), "IOP", '.wd-jnl-art-abstract', file_domains=('content.cld.iop.org','cfn-live-content-bucket-iop-org.s3.eu-west-1.amazonaws.com')),
    Profile("siam", ("epubs.siam.org", "www.siam.org"), None),
    Profile("project-euclid", ("projecteuclid.org", "www.projecteuclid.org"), None, 'text.ArticleContentText > h2:text-is("Abstract") + div'),
    Profile("theory-of-computing", ("theoryofcomputing.org", "www.theoryofcomputing.org"), None),
]


def publication_metadata(raw):
    soup = BeautifulSoup(raw, "html.parser")
    fields = {}
    for tag in soup.select("meta[name],meta[property]"):
        name = tag.get("name", tag.get("property", ""))
        if (name.lower().startswith(("citation_", "dc.", "dc:", "dcterms.", "prism.", "og:")) or name.lower()=='publication_doi') and tag.get("content") is not None:
            fields.setdefault(name.lower(), []).append(tag["content"])
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            fields.setdefault("schema_org", []).append(json.loads(script.string or script.get_text()))
        except (ValueError, TypeError):
            continue
    return fields


def publication_dois(metadata):
    for group in [('citation_doi',),('publication_doi','dc.identifier','dc:identifier','dcterms.identifier','prism.doi')]:
        found={}
        for key in group:
            for value in metadata.get(key,[]):
                try: identifier=doi(value)
                except ServiceError: continue
                found.setdefault(identifier.casefold(),identifier)
        if found: return list(found.values())
    return []


def primary_pdf_links(raw, base, *, identifier=None):
    soup = BeautifulSoup(raw, "html.parser")
    urls = [urljoin(base, tag["content"]) for tag in soup.select('meta[name="citation_pdf_url"][content]')]
    if urls:
        return list(dict.fromkeys(urls))
    if identifier:
        for tag in soup.select('a.show-pdf[href*="/doi/pdf/"]'):
            link=urljoin(base,tag['href'])
            if unquote(urlsplit(link).path).lower()=='/doi/pdf/'+identifier.lower():
                urls.append(link)
        if urls:
            return list(dict.fromkeys(urls))
    # These explicitly identify the current publication; unrelated PDF links are not candidates.
    for tag in soup.select('a[data-track-action="download pdf"],a[data-test="pdf-link"],a.article-tools__pdf,a.c-pdf-download__link,a[data-item-name="download-pdf"]'):
        if tag.get("href"):
            urls.append(urljoin(base, tag["href"]))
    return list(dict.fromkeys(urls))


def wiley_records(raw, base):
    soup = BeautifulSoup(raw, "html.parser")
    count = soup.select_one('.result__count')
    if count is None and soup.select_one('.search-result__no-result') and soup.select_one('.result__current') and soup.select_one('.result__current').get_text(strip=True) == '0':
        return [], 0
    if count is None or not re.fullmatch(r'[\d,\s]+', count.get_text()):
        raise ServiceError('invalid_response', 'Wiley did not return a search result count')
    rows = []
    for item in soup.select('li.search__item'):
        title = item.select_one('.meta__title a.publication_title')
        if title is None:
            raise ServiceError('invalid_response', 'Wiley result is missing its publication link')
        url = urljoin(base, title['href'])
        match = re.search(r'/doi/(?:abs/|full/|epdf/)?(10\..+)', unquote(urlsplit(url).path))
        if not match:
            raise ServiceError('invalid_response', 'Wiley publication link has no DOI')
        rows.append({'id': match[1], 'doi': match[1], 'title': title.get_text(' ', strip=True), 'url': url,
                     'authors': [a.get_text(' ', strip=True) for a in item.select('.publication_contrib_author')],
                     'listing': item.get_text('\n', strip=True)})
    return rows, int(re.sub(r'[,\s]', '', count.get_text()))


def springer_records(raw, base):
    soup = BeautifulSoup(raw, 'html.parser')
    matches = re.findall(r'Showing\s+([\d,]+)[–-]([\d,]+)\s+of\s+([\d,]+)\s+results', soup.get_text(' ', strip=True))
    if not matches:
        if re.search(r'\b0 results\b|No results|No search results', soup.get_text(' ', strip=True), re.I):
            return [], 0, 0
        raise ServiceError('invalid_response', 'Springer returned no recognized result range')
    first, last, total = [int(x.replace(',', '')) for x in matches[0]]
    rows = []
    for item in soup.select('li.app-card-open'):
        anchor = item.select_one('h3 a')
        if anchor is None:
            raise ServiceError('invalid_response', 'Springer record has no publication title')
        url = urljoin(base, anchor['href'])
        identity = re.search(r'/(10\..+)$', unquote(urlsplit(url).path))
        if not identity:
            raise ServiceError('invalid_response', 'Springer publication link has no DOI')
        rows.append({'doi': identity[1], 'id': identity[1], 'title': anchor.get_text(' ', strip=True),
                     'url': url, 'listing': item.get_text('\n', strip=True)})
    if len(rows) != last-first+1:
        raise ServiceError('range_mismatch', 'Springer listing does not match its displayed result range')
    return rows, total, first-1


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

    def explicit_pdf(self,url,parts):
        """Read an explicitly named PDF, including native navigation downloads."""
        from pathlib import Path
        import pymupdf
        self.gateway.start()
        if self.profile.gateway_label:
            self.gateway.open(self.source,self.profile.gateway_label,self.profile.hosts,'body')
        context=self.gateway.context
        expected=urlsplit(url)
        downloads,pages=[],[]
        def captured(download):
            actual=urlsplit(download.url)
            if actual.path==expected.path and actual.query==expected.query:
                downloads.append(download)
        def opened(page):
            pages.append(page)
            page.on('download',captured)
        cached=self.gateway.pages.get(self.source)
        if not self.profile.gateway_label and cached and not cached.is_closed():
            opened(cached)
        context.on('page',opened)
        try:
            if callable(getattr(self.gateway,'native_download',None)):
                page=self.gateway.public_page(self.source)
                data,_,actual=self.gateway.native_download(page,lambda:self.document(url),self.profile.download_hosts,
                                                          expected.path,query=expected.query)
            else:
                try:
                    page=self.document(url)
                except Exception as error:
                    if not downloads:
                        if isinstance(error,ServiceError):
                            raise
                        raise ServiceError('pdf_navigation_failed','The requested PDF did not produce a document or download',error_type=type(error).__name__) from None
                if downloads:
                    if len(downloads)!=1:
                        raise ServiceError('ambiguous_download','The PDF navigation produced multiple matching downloads')
                    download=downloads[0]
                    require_source_url(download.url,self.profile.download_hosts)
                    data=Path(download.path()).read_bytes()
                    actual=download.url
                else:
                    data,_,actual=browser_download(context,page.url,self.profile.download_hosts)
            if not data.startswith(b'%PDF-'):
                raise ServiceError('unexpected_content','The explicit PDF address returned no PDF')
            try:
                with pymupdf.open(stream=data,filetype='pdf') as document:
                    metadata={**document.metadata,'pages':len(document),'page_labels':document.get_page_labels()}
            except Exception:
                raise ServiceError('invalid_document','The downloaded PDF cannot be read') from None
            artifact=self.store.put(data,'application/pdf',self.source,actual,role='explicit_pdf_file',requested_url=url,pages=metadata['pages'])
            record=self.store.put(encoded([metadata]),'application/json',self.source,actual,role='embedded_pdf_metadata',parent_ref=artifact['ref'])
            components={}
            for part in parts:
                if part=='metadata':
                    components[part]={'status':'available','artifact':record,'kind':'embedded_pdf_metadata'}
                elif part in ('fulltext','export'):
                    components[part]={'status':'available','artifact':artifact,'format':'pdf'}
                else:
                    components[part]={'status':'not_implemented','reason':'The explicit-file path provides PDF bytes and embedded metadata; separate abstract or attachment retrieval requires a document-page target'}
            return {'status':'ok' if all(c['status']=='available' for c in components.values()) else 'partial','source':self.source,
                    'target':url,'components':components,'records':record,
                    'scope':'Exactly the requested PDF file; it may be an excerpt, supplement or complete work. Coverage of a larger work is not inferred.'}
        finally:
            context.remove_listener('page',opened)
            for page in pages:
                page.remove_listener('download',captured)
                if not page.is_closed():
                    page.close()

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        if self.source=='iop':
            from iop_search import search
            return search(self,query,options=options,start=start,limit=limit,cursor=cursor,export=export)
        if self.source=='aps-institutional':
            from aps_institutional import search
            return search(self,query,options=options,start=start,limit=limit,cursor=cursor,export=export)
        if self.source == 'project-euclid':
            from euclid import search
            return search(self,query,options=options,start=start,limit=limit,cursor=cursor,export=export)
        if self.source == 'wiley':
            return self.wiley_search(query, options=options, start=start, limit=limit, cursor=cursor, export=export)
        if self.source == 'springer':
            return self.springer_search(query, options=options, start=start, limit=limit, cursor=cursor, export=export)
        if self.source in ('oxford','aip'):
            from silverchair import search
            return search(self, query, options=options, start=start, limit=limit, cursor=cursor, export=export)
        if self.source == 'cambridge':
            from cambridge import search
            return search(self,query,options=options,start=start,limit=limit,cursor=cursor,export=export)
        if self.source == 'taylor-francis':
            from taylor import search
            return search(self,query,options=options,start=start,limit=limit,cursor=cursor,export=export)
        if self.source == 'de-gruyter':
            from degruyter import search
            return search(self,query,options=options,start=start,limit=limit,cursor=cursor,export=export)
        raise ServiceError("publisher_search_not_implemented", "This document adapter currently accepts exact publisher links and DOIs; native advanced search/export remains in development", status="not_implemented", source=self.source)

    def springer_citation(self, page, identifier, format='bibtex'):
        labels = {'bibtex': ('.BIB', 'application/x-bibtex'), 'ris': ('.RIS', 'application/x-research-info-systems'), 'endnote': ('.ENW', 'text/plain')}
        label, media = labels[format]
        control = page.locator('a[href*="/v2/references/"][href*="flavour=citation"]')
        control.first.wait_for(state='attached', timeout=30000)
        link = urljoin(page.url, control.first.get_attribute('href'))
        location = urlsplit(link)
        if unquote(location.path).lower() != '/v2/references/' + identifier.lower():
            raise ServiceError('identity_mismatch', 'Springer citation control identifies another publication')
        params = parse_qs(location.query)
        params['format'] = [{'bibtex':'bibtex','ris':'refman','endnote':'endnote'}[format]]
        link = urlunsplit((location.scheme,location.netloc,location.path,urlencode(params,doseq=True),''))
        data, _, actual = browser_download(self.gateway.context, link, self.profile.download_hosts)
        if format in ('bibtex', 'ris'):
            parsed = bibliography(data, media)
            observed = [row.get('doi') or row.get('fields', {}).get('do', [None])[0] or row.get('id') for row in parsed]
            if len(observed) != 1 or doi(str(observed[0])).lower() != identifier.lower():
                raise ServiceError('identity_mismatch', 'Springer citation does not identify the requested publication')
        elif not data.strip() or data.lstrip().startswith(b'<'):
            raise ServiceError('unexpected_content', 'Springer returned no citation text')
        return self.store.put(data, media, self.source, actual, role='native_citation', doi=identifier, format=format)

    def springer_search(self, query, *, options, start, limit, cursor, export):
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ServiceError('invalid_range', 'Use start >= 0 and limit 1..1000')
        allowed = {'field', 'title', 'author', 'journal', 'date_from', 'date_to', 'content_type', 'open_access', 'language', 'subject', 'discipline', 'subdiscipline', 'sort'}
        if cursor or set(options)-allowed or options.get('field', 'Anywhere') not in ('Anywhere', 'Title', 'Author'):
            raise ServiceError('invalid_options', 'Use the documented Springer advanced-search fields and filters')
        if export not in (None, 'json', 'html', 'csv', 'bibtex', 'ris', 'endnote'):
            raise ServiceError('invalid_export', 'Use json, html, csv, bibtex, ris or endnote')
        params = { {'Anywhere': 'query', 'Title': 'title', 'Author': 'contributor'}[options.get('field', 'Anywhere')]: query }
        mapping = {'title': 'title', 'author': 'contributor', 'journal': 'journal', 'date_from': 'dateFrom', 'date_to': 'dateTo',
                   'content_type': 'content-type', 'language': 'language', 'subject': 'taxonomy', 'discipline': 'facet-discipline', 'subdiscipline': 'facet-sub-discipline'}
        for key, native in mapping.items():
            if key in options:
                if native in params:
                    raise ServiceError('invalid_options', 'A query field cannot also be supplied as a separate filter')
                params[native] = options[key]
        if 'date_from' in options or 'date_to' in options:
            params['date'] = 'custom'
        if 'open_access' in options:
            if type(options['open_access']) is not bool:
                raise ServiceError('invalid_options', 'open_access requires a boolean')
            if options['open_access']:
                params['openAccess'] = 'true'
        sorts = {'relevance': 'relevance', 'newest': 'newestFirst', 'oldest': 'oldestFirst'}
        if options.get('sort', 'relevance') not in sorts:
            raise ServiceError('invalid_options', 'Use sort relevance, newest or oldest')
        params['sortBy'] = sorts[options.get('sort', 'relevance')]
        page = self.gateway.open(self.source, self.profile.gateway_label, self.profile.hosts, 'body')
        base = 'https://' + urlsplit(page.url).hostname
        rows, evidence, total = [], [], None
        for number in range(start//20+1, (start+limit-1)//20+2):
            params['page'] = number
            goto_source(page, base+'/search?'+urlencode(params, doseq=True), self.profile.hosts, wait_until='domcontentloaded', timeout=45000)
            page.wait_for_function("() => /Showing\\s+[\\d,]+[–-][\\d,]+\\s+of\\s+[\\d,]+\\s+results|0 results|No results|No search results/i.test(document.body.innerText)", timeout=30000)
            raw = clean_html(page.content(), self.store.sanitizer)
            native, found, first = springer_records(raw, base)
            if found and first != (number-1)*20 or total is not None and total != found:
                raise ServiceError('range_mismatch', 'Springer returned a changed or different result range')
            total = found
            evidence.append(self.store.put(raw, 'text/html', self.source, page.url, role='search_page', query=query, options=options, page=number))
            rows.extend(row for i,row in enumerate(native, first) if start <= i < start+limit)
            if number*20 >= total:
                break
        artifact = self.store.put(encoded(rows), 'application/json', self.source, page.url, role='records', query=query, options=options, start=start, requested=limit, total=total)
        exported, failures = artifact, []
        if export == 'html':
            exported = {'artifacts': evidence}
        elif export == 'csv':
            stream = io.StringIO(newline='')
            writer = csv.DictWriter(stream, fieldnames=['doi','id','title','url','listing'])
            writer.writeheader()
            writer.writerows(rows)
            exported = self.store.put(stream.getvalue(), 'text/csv', self.source, page.url, role='mechanical_export', parent_ref=artifact['ref'])
        elif export in ('bibtex','ris','endnote'):
            citations = []
            for row in rows:
                document = self.gateway.context.new_page()
                try:
                    goto_source(document, row['url'], self.profile.hosts, wait_until='domcontentloaded', timeout=45000)
                    citations.append(self.springer_citation(document, row['doi'], export))
                except ServiceError as error:
                    failures.append({'doi': row['doi'], **error.result})
                except Exception as error:
                    failures.append({'doi': row['doi'], 'status': 'error', 'code': 'citation_export_failed', 'error_type': type(error).__name__})
                finally:
                    document.close()
            exported = {'status': 'partial' if failures else 'available', 'artifacts': citations, 'failures': failures}
        more = start+len(rows)<total
        return {'status': 'partial' if failures else 'ok' if rows else 'not_found', 'source': self.source, 'query': query,
                'start': start, 'requested': limit, 'received': len(rows), 'total': total, 'has_more': more,
                'next': {'start': start+len(rows)} if more else None, 'records': artifact, 'export': exported, 'evidence': evidence,
                'preview': [{k:r[k] for k in ('doi','title')} for r in rows[:3]]}

    def wiley_search(self, query, *, options, start, limit, cursor, export):
        fields = {'Anywhere': 'AllField', 'Title': 'Title', 'Author': 'Contrib', 'Keywords': 'Keyword',
                  'Abstract': 'Abstract', 'Author Affiliation': 'Affiliation', 'Funding Agency': 'FundingAgency'}
        formats = {'bibtex': ('BibTex', 'application/x-bibtex'), 'ris': ('RIS', 'application/x-research-info-systems'),
                   'plain': ('txt', 'text/plain'), 'endnote': ('EndNote', 'text/plain'), 'medlars': ('Medlars', 'text/plain')}
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ServiceError('invalid_range', 'Use start >= 0 and limit 1..1000')
        allowed = {'field', 'terms', 'publication', 'after_year', 'after_month', 'before_year', 'before_month', 'sort'}
        if cursor or set(options) - allowed or options.get('field', 'Anywhere') not in fields:
            raise ServiceError('invalid_options', 'Use the documented Wiley fields, date/publication filters and start/limit')
        if export not in (None, 'json', 'html', *formats):
            raise ServiceError('invalid_export', 'Use json, html, bibtex, ris, plain, endnote or medlars')
        params = {'field1': fields[options.get('field', 'Anywhere')], 'text1': query, 'Ppub': '', 'pageSize': 20}
        terms = options.get('terms', [])
        if not isinstance(terms, list) or len(terms) > 2:
            raise ServiceError('invalid_options', 'Wiley supports at most two additional advanced-search rows')
        for i, term in enumerate(terms, 2):
            if not isinstance(term, dict) or set(term) != {'field', 'query'} or term['field'] not in fields or not isinstance(term['query'], str):
                raise ServiceError('invalid_options', 'Each additional row requires a documented field and query')
            params.update({f'field{i}': fields[term['field']], f'text{i}': term['query']})
        if options.get('publication'):
            params['publication'] = options['publication']
        for key, native in [('after_year', 'AfterYear'), ('before_year', 'BeforeYear'), ('after_month', 'AfterMonth'), ('before_month', 'BeforeMonth')]:
            if key in options:
                value = options[key]
                if type(value) is not int or not (1 <= value <= (12 if 'month' in key else 9999)):
                    raise ServiceError('invalid_options', 'Year and month filters require valid integers')
                params[native] = value
        sort = options.get('sort', 'relevance')
        if sort == 'date':
            params['sortBy'] = 'Earliest'
        elif sort != 'relevance':
            raise ServiceError('invalid_options', 'Use sort relevance or date, as labeled by Wiley')
        page = self.gateway.open(self.source, self.profile.gateway_label, self.profile.hosts, '#searchField1')
        base = 'https://' + urlsplit(page.url).hostname
        rows, evidence, citations, failures, total = [], [], [], [], None
        for number in range(start // 20, (start + limit - 1) // 20 + 1):
            params['startPage'] = number
            goto_source(page, base + '/action/doSearch?' + urlencode(params), self.profile.hosts, wait_until='domcontentloaded', timeout=45000)
            page.locator('.result__count, .search-result__no-result').first.wait_for(timeout=30000)
            dismiss_cookies(page)
            actual = parse_qs(urlsplit(page.url).query)
            if actual.get('text1') != [query] or actual.get('field1') != [params['field1']] or actual.get('startPage') != [str(number)]:
                raise ServiceError('query_mismatch', 'Wiley returned a different search or page')
            raw = clean_html(page.content(), self.store.sanitizer)
            native, found = wiley_records(raw, base)
            if total is not None and total != found:
                raise ServiceError('range_changed', 'Wiley result count changed during pagination')
            total = found
            if len(native) != min(20, max(0, total-number*20)):
                raise ServiceError('range_mismatch', 'Wiley result count does not match the requested page')
            evidence.append(self.store.put(raw, 'text/html', self.source, page.url, role='search_page', query=query, options=options, page=number))
            selected = [(i, row) for i, row in enumerate(native) if start <= number*20+i < start+limit]
            rows.extend(row for _, row in selected)
            if export in formats and selected:
                try:
                    page.get_by_role('link', name='Export Citation(s)', exact=True).click()
                    boxes = page.locator('input[name=bulkDownload]')
                    boxes.first.wait_for(state='attached')
                    for i, row in selected:
                        box = boxes.nth(i)
                        if box.input_value().lower() != row['doi'].lower():
                            raise ServiceError('identity_mismatch', 'Citation selection does not match the search record')
                        if not box.is_checked():
                            box.focus()
                            box.press('Space')
                    page.get_by_role('button', name='Next', exact=True).click()
                    format_name, media = formats[export]
                    radio = page.locator('#radio-format-' + format_name)
                    radio.focus()
                    radio.press('Space')
                    with page.expect_download(timeout=30000) as pending:
                        page.get_by_role('button', name='Export', exact=True).click()
                    download = pending.value
                    from pathlib import Path
                    data = Path(download.path()).read_bytes()
                    download.delete()
                    if export in ('bibtex', 'ris'):
                        parsed = bibliography(data, media)
                        observed = [r.get('doi') or r.get('fields', {}).get('do', [None])[0] for r in parsed]
                        if sorted(doi(str(x)).lower() for x in observed) != sorted(r['doi'].lower() for _, r in selected):
                            raise ServiceError('identity_mismatch', 'Native citations do not match the selected DOIs')
                    elif not data.strip() or data.lstrip().startswith(b'<'):
                        raise ServiceError('unexpected_content', 'Wiley returned no citation text')
                    citations.append(data)
                    page.get_by_role('button', name='Close modal', exact=True).click()
                except ServiceError as error:
                    failures.append(error.result)
                except Exception as error:
                    failures.append({'status': 'error', 'code': 'citation_export_failed', 'error_type': type(error).__name__})
            if (number+1)*20 >= total:
                break
        records = self.store.put(encoded(rows), 'application/json', self.source, page.url, role='records', query=query, options=options, start=start, requested=limit, total=total)
        exported = records
        if export == 'html':
            exported = {'artifacts': evidence}
        elif export in formats:
            exported = {'status': 'partial' if failures else 'available', 'failures': failures}
            if citations:
                exported['artifact'] = self.store.put(b'\n\n'.join(citations), formats[export][1], self.source, page.url, role='native_citations', parent_ref=records['ref'])
        more = start+len(rows) < total
        return {'status': 'partial' if failures else 'ok' if rows else 'not_found', 'source': self.source,
                'query': query, 'options': options, 'start': start, 'requested': limit, 'received': len(rows), 'total': total,
                'has_more': more, 'next': {'start': start+len(rows)} if more else None,
                'records': records, 'export': exported, 'evidence': evidence,
                'preview': [{k:r[k] for k in ('doi','title')} for r in rows[:3]]}

    def fetch(self, target, *, parts):
        allowed={"metadata", "abstract", "fulltext", "supplementary", "export"}
        if self.source in ('springer','iop'):allowed.add('fulltext_html')
        unknown = set(parts) - allowed
        if unknown:
            raise ServiceError("invalid_parts", "Unknown requested content", parts=sorted(unknown))
        if not target.startswith(('http://', 'https://', '10.', 'doi:')):
            candidates = self.search(target, options={'sort':'relevance'} if self.source=='iop' else {'field':'Title'} if self.source in ('wiley','springer','oxford','aip','taylor-francis') else {}, limit=20)
            return {**candidates, 'status': 'selection_required' if candidates.get('received') else candidates['status'],
                    'message': 'Select the exact publication DOI or URL from the preserved candidates'}
        url, identifier = self.resolve_target(target)
        requested_identifier = identifier
        if urlsplit(url).path.lower().endswith('.pdf') or self.source=='siam' and urlsplit(url).path.startswith('/doi/pdf/'):
            return self.explicit_pdf(url,parts)
        page = self.document(url)
        try:
            try:
                page.wait_for_function("includeChallenge => [...document.querySelectorAll('meta[name],meta[property]')].some(m=>/^(citation_title|dc[.:]title)$/i.test(m.name||m.getAttribute('property')||'') && m.content?.trim()) || (document.querySelector('meta[name=publication_doi]')?.content?.trim() && document.querySelector('meta[property=\"og:title\"]')?.content?.trim() && document.querySelector('h1.banner-widget__heading')?.innerText?.trim()) || (includeChallenge && (document.querySelector('#challenge-error-text,#capInput') || /^(Access Denied|Just a moment|Attention Required|403 Forbidden)/i.test(document.title)))", arg=self.source!='siam', timeout=75000 if self.source=='siam' else 20000)
            except Exception:
                if is_access_challenge(page.content()):
                    raise ServiceError('publisher_access_restricted','Publisher returned an access verification page',status='restricted',source=self.source) from None
                raise ServiceError("document_not_ready", "Publisher did not initialize a document page", source=self.source) from None
            body = page.locator("body").inner_text()
            if is_access_challenge(page.content()) or re.search(r"CPE00001|Verify you are human", body[:1000], re.I):
                raise ServiceError("publisher_access_restricted", "Publisher returned an access/error page", status="restricted", source=self.source)
            require_source_url(page.url, self.profile.hosts)
            raw = page.content()
            metadata = publication_metadata(raw)
            titles = metadata.get("citation_title", metadata.get("dc.title", metadata.get("dc:title", [])))
            if not titles and metadata.get('publication_doi') and metadata.get('og:title') and publication_dois(metadata):
                heading = BeautifulSoup(raw, 'html.parser').select_one('h1.banner-widget__heading')
                if heading and heading.get_text(' ', strip=True):
                    titles = [heading.get_text(' ', strip=True)]
            if not titles:
                raise ServiceError("metadata_not_identified", "Publisher page has no recognized publication title metadata", source=self.source)
            observed_dois = publication_dois(metadata)
            if identifier and observed_dois and identifier.lower() not in {x.lower().removeprefix("https://doi.org/") for x in observed_dois}:
                raise ServiceError("identity_mismatch", "Publisher metadata contains a different DOI", source=self.source)
            if not identifier and len(observed_dois)==1:
                identifier=observed_dois[0]
            source_page = self.store.put(clean_html(raw, self.store.sanitizer), "text/html", self.source, page.url, role="source_page", requested_target=target)
            record = {"title": titles[0], "doi": identifier, "metadata": metadata, "url": self.store.sanitizer.url(page.url)}
            artifact = self.store.put(encoded([record]), "application/json", self.source, page.url, role="records", evidence_ref=source_page["ref"])
            native_citation = None
            if self.source in ('aip','taylor-francis') and set(parts) & {'abstract','export'}:
                try:
                    if self.source=='aip':
                        from silverchair import citation
                        cited=citation(self,page,identifier or observed_dois[0])
                    else:
                        from taylor import citation
                        cited=citation(self,[identifier or observed_dois[0]],page.url)
                    native_citation = {'status':'available','artifact':cited,'format':'bibtex'}
                except ServiceError as error:
                    native_citation = error.result
                except Exception as error:
                    native_citation = {'status':'error','code':'citation_export_failed','error_type':type(error).__name__}
            components = {}
            for part in parts:
                if part == 'export' and self.source in ('iop','project-euclid'):
                    if self.source=='iop':
                        from iop import citation
                        formats=('bibtex','ris')
                    else:
                        from euclid import citation
                        formats=('bibtex','ris','endnote','citation-pdf')
                    artifacts,errors=[],[]
                    for format in formats:
                        try:
                            artifacts.append({'format':format,'artifact':citation(self,page,identifier or observed_dois[0],format)})
                        except ServiceError as error:
                            errors.append({'format':format,**error.result})
                        except Exception as error:
                            errors.append({'format':format,'status':'error','code':'citation_export_failed','error_type':type(error).__name__})
                    components[part]={'status':'partial' if errors else 'available','artifacts':artifacts,'errors':errors}
                    if artifacts:
                        components[part]['artifact']=artifacts[0]['artifact']
                elif part == 'export' and self.source == 'springer':
                    try:
                        components[part] = {'status': 'available', 'artifact': self.springer_citation(page, identifier or observed_dois[0]), 'format': 'bibtex'}
                    except ServiceError as error:
                        components[part] = error.result
                elif part == 'export' and self.source == 'cambridge':
                    from cambridge import citation
                    product_id=urlsplit(page.url).path.rstrip('/').rsplit('/',1)[-1]
                    try:
                        components[part]={'status':'available','artifact':citation(self.store,[product_id]),'format':'ris'}
                    except ServiceError as error:
                        components[part]=error.result
                elif part == 'export' and self.source == 'de-gruyter':
                    from degruyter import citation
                    try:
                        components[part]={'status':'available','artifact':citation(self,page,identifier or observed_dois[0]),'format':'ris'}
                    except ServiceError as error:
                        components[part]=error.result
                elif part == 'export' and self.source in ('aip','taylor-francis'):
                    components[part] = native_citation
                elif part == 'abstract' and self.source in ('aip','taylor-francis') and native_citation and native_citation['status']=='available':
                    native = self.store.read(native_citation['artifact']['ref'])[1]
                    rows = bibliography(native,'application/x-bibtex')
                    content = rows[0].get('abstract') if rows else None
                    if content:
                        abstract = self.store.put(content,'text/plain',self.source,page.url,role='abstract',format='native_bibtex_field',parent_ref=native_citation['artifact']['ref'])
                        components[part] = {'status':'available','artifact':abstract}
                    else:
                        components[part] = {'status':'source_page','artifact':source_page,'reason':'The native citation does not include an abstract'}
                elif part == 'export' and self.source == 'oxford':
                    from silverchair import citation
                    try:
                        components[part] = {'status':'available','artifact':citation(self,page,identifier or observed_dois[0]),'format':'bibtex'}
                    except ServiceError as error:
                        components[part] = error.result
                elif part in ("metadata", "export"):
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
                elif part=='fulltext_html':
                    from publisher_html import fetch_html
                    try:
                        components[part]=fetch_html(self,page,identifier or (observed_dois[0] if observed_dois else None),source_page)
                    except ServiceError as error:
                        components[part]=error.result
                elif part == "fulltext":
                    links = primary_pdf_links(page.content(), page.url, identifier=identifier or (observed_dois[0] if observed_dois else None))
                    if not links:
                        components[part] = {"status": "not_implemented", "reason": "No recognized document-bound PDF control; further layout/full-HTML handling is pending", "artifact": source_page}
                        continue
                    try:
                        origin = urlsplit(page.url)
                        headers = {"User-Agent": page.evaluate("navigator.userAgent"), "Referer": origin.scheme + "://" + origin.netloc + "/"}
                        data, media, obtained = browser_download(self.gateway.context, links[0], self.profile.download_hosts, headers=headers)
                        if not data.startswith(b"%PDF-") and self.source == 'wiley':
                            viewer = self.gateway.context.new_page()
                            try:
                                goto_source(viewer, links[0], self.profile.hosts, wait_until='domcontentloaded', timeout=45000)
                                ready = viewer.wait_for_function("() => { const src = document.querySelector('#pdf-iframe')?.getAttribute('src'); return src && new URL(src, location.href).searchParams.get('file') ? src : false; }", timeout=30000)
                                iframe = urljoin(viewer.url, ready.json_value())
                                require_source_url(iframe, self.profile.hosts)
                                candidates = parse_qs(urlsplit(iframe).query).get('file', [])
                                if len(candidates) != 1:
                                    raise ServiceError('invalid_response', 'Wiley PDF viewer has no unique document file')
                                actual = urljoin(viewer.url, candidates[0])
                                data, media, obtained = browser_download(self.gateway.context, actual, self.profile.download_hosts, headers=headers)
                            finally:
                                viewer.close()
                        if not data.startswith(b"%PDF-"):
                            raise ServiceError("unexpected_content", "Publisher document control returned non-PDF content")
                        import pymupdf
                        with pymupdf.open(stream=data, filetype="pdf") as doc:
                            pages = len(doc)
                        pdf = self.store.put(data, "application/pdf", self.source, obtained, role="fulltext", pages=pages, target=target, publication_metadata_ref=artifact["ref"])
                        components[part] = {"status": "available", "artifact": pdf}
                    except ServiceError as error:
                        components[part] = error.result
                elif part=='supplementary' and self.source in ('springer','wiley','aip','cambridge','oxford','taylor-francis','de-gruyter','project-euclid','iop'):
                    if self.source=='iop':
                        from iop import supplementary as fetch_supplementary
                    else:
                        from supplements import fetch_supplementary
                    components[part]=fetch_supplementary(self,page,identifier or (observed_dois[0] if observed_dois else None),source_page)
                else:
                    components[part] = {"status": "source_page", "artifact": source_page, "reason": "Supplementary content is preserved in its source context; automatic attachment retrieval is pending"}
            return {"status": "ok" if all(item["status"] == "available" for item in components.values()) else "partial", "source": self.source,
                "target": target, "records": artifact, "source_page": source_page, "components": components,
                "identity": {"requested_doi": requested_identifier, "observed_dois": observed_dois, "basis": "Exact publisher URL and available publisher metadata; file-level bibliography review is separate"}}
        finally:
            page.close()


def make_publishers(store, gateway):
    return {profile.source: Publisher(store, gateway, profile) for profile in PROFILES}
