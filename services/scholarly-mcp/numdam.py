"""Numdam: fixed native browser search and public OAI/citation retrieval."""
import json
import re
from urllib.parse import quote, unquote, urljoin, urlsplit

from bs4 import BeautifulSoup

from api_adapters import Numdam as NumdamOAI, doi
from browser_adapters import clean_html, goto_source, require_source_url
from scholarly import ServiceError, bibliography, encoded

FIELDS = {'all': 'All', 'author': 'Author', 'title': 'Title', 'references': 'References',
          'fulltext': 'Full text', 'keywords': 'Keywords', 'date': 'Date'}
FORMATS = {'bibtex': ('bib', 'application/x-bibtex'), 'ris': ('ris', 'application/x-research-info-systems'),
           'endnote': ('enw', 'application/x-endnote-refer')}
NATIVE = re.compile(r'[A-Za-z0-9]+_[A-Za-z0-9_]+')


def numbered_page_link(second, number):
    if not re.search(r'-2-q(?:d)?t(?:&|$)', second):
        return None
    return re.sub(r'-2-(q(?:d)?t)(?=&|$)', rf'-{number}-\1', second)


def search_records(raw, base):
    soup = BeautifulSoup(raw, 'html.parser')
    header = soup.select_one('.results-header')
    match = re.search(r'([\d,\s\u00a0]+)\s+r[eé]sult', header.get_text(' ', strip=True) if header else '', re.I)
    if not match:
        if re.search(r'No results|0 results|Aucun r[eé]sultat|0 r[eé]sultat', soup.get_text(' ', strip=True), re.I):
            return [], 0
        raise ServiceError('search_parse_failed', 'Numdam did not display a result count')
    total = int(re.sub(r'\D', '', match[1]))
    rows = []
    cards=[];seen=set()
    for heading in soup.select('.search-results .common-title'):
        card=heading.find_parent(class_=lambda value:value and 'row' in value.split())
        if card is not None and id(card) not in seen:
            cards.append(card);seen.add(id(card))
    for card in cards:
        title = card.select_one('.common-title')
        link = title.find_parent('a') if title else None
        if link is None or not link.get('href', '').startswith(('/articles/', '/item/', '/books/', '/book-part/')):
            raise ServiceError('search_parse_failed', 'Numdam result has no recognized document link')
        url = urljoin(base, link['href'])
        require_source_url(url, NumdamOAI.hosts)
        rows.append({'id': url, 'title': title.get_text('', strip=False).strip(), 'url': url,
                     'listing': card.get_text('\n', strip=True),
                     'links': [{'url': urljoin(base, a['href']), 'format': a['href'].rsplit('.', 1)[-1]}
                               for a in card.select('a[href]') if a['href'].endswith(('.pdf', '.djvu'))]})
    if total and not rows:
        raise ServiceError('search_parse_failed', 'Numdam reported results without document rows')
    return rows, total


class Numdam(NumdamOAI):
    def __init__(self, store, gateway, client=None):
        super().__init__(store, client)
        self.gateway = gateway

    def document(self, target):
        value = target.removeprefix('oai:numdam.org:').strip()
        requested_doi = None
        if value.startswith(('http://', 'https://')):
            parsed = urlsplit(value)
            if parsed.hostname in ('doi.org', 'dx.doi.org'):
                value = doi(value)
            else:
                require_source_url(value, self.hosts)
                match = re.fullmatch(r'/(?:articles|item|books|book-part)/(.+?)/?', unquote(parsed.path))
                if not match:
                    raise ServiceError('invalid_target', 'Use a Numdam document URL')
                value = re.sub(r'\.(pdf|djvu)$', '', match[1])
        if NATIVE.fullmatch(value):
            return value, None, None
        if value.startswith(('10.', 'doi:')):
            requested_doi = doi(value)
            url = 'https://www.numdam.org/articles/' + quote(requested_doi, safe='/') + '/'
        else:
            candidates = self.search(value, options={'field': 'title'}, limit=5)
            raise ServiceError('select_document', 'Select a document URL from the title search',
                               status='selection_required' if candidates['received'] else 'not_found', candidates=candidates)
        page = self.gateway.public_page(self.source)
        response = goto_source(page, url, self.hosts, wait_until='domcontentloaded', timeout=45000)
        if response and response.status == 404:
            raise ServiceError('not_found_at_source', 'Numdam did not find this document', status='not_found')
        raw = page.content()
        soup = BeautifulSoup(raw, 'html.parser')
        ids = {m[1] for a in soup.select('a[href^="/export_citation/"]')
               if (m := re.fullmatch(r'/export_citation/([A-Za-z0-9_]+)/(?:bib|ris|enw)/', a['href']))}
        meta_doi = soup.select_one('meta[name="citation_doi"]')
        if len(ids) != 1 or not meta_doi or doi(meta_doi.get('content', '')).casefold() != requested_doi.casefold():
            raise ServiceError('identity_mismatch', 'Numdam page does not identify the requested DOI uniquely')
        evidence = self.store.put(clean_html(raw, self.store.sanitizer), 'text/html', self.source, page.url, role='document_page')
        return ids.pop(), requested_doi, evidence

    def citation(self, identifier, kind):
        suffix, media = FORMATS[kind]
        url = 'https://www.numdam.org/export_citation/' + identifier + '/' + suffix + '/'
        data, evidence = self.request(url, accept='binary')
        if kind in ('bibtex', 'ris'):
            rows = bibliography(data, media)
            if len(rows) != 1 or identifier.casefold() not in data.decode('utf-8-sig').casefold():
                raise ServiceError('identity_mismatch', 'Numdam citation does not identify the requested record', evidence=evidence)
        elif not data.lstrip().startswith(b'%0 ') or identifier.encode() not in data:
            raise ServiceError('identity_mismatch', 'Numdam EndNote does not identify the requested record', evidence=evidence)
        return self.store.put(data, media, self.source, evidence['url'], role='native_citation', identifier=identifier, evidence_ref=evidence['ref'])

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        if not query and 'field' not in options and 'terms' not in options:
            return super().search(query, options=options, start=start, limit=limit, cursor=cursor, export=export)
        if set(options) - {'field', 'terms'} or cursor or export not in (None, 'json', 'html', 'native', *FORMATS):
            raise ServiceError('invalid_options', 'Use field/terms, start/limit and json/html/bibtex/ris/endnote export')
        self.validate({}, start, limit)
        if not isinstance(options.get('terms', []), list):
            raise ServiceError('invalid_options', 'terms must be an array of search conditions')
        additional = options.get('terms', [])
        date_only = (not query and options.get('field', 'all') == 'all' and additional
                     and all(isinstance(term, dict) and term.get('field') == 'date' for term in additional))
        terms = [{'field': options.get('field', 'all'), 'query': '*' if date_only else query}] + additional
        for index, term in enumerate(terms):
            if not isinstance(term, dict) or set(term) - {'field', 'query', 'not', 'from', 'until'} or term.get('field') not in FIELDS:
                raise ServiceError('invalid_options', 'Each term needs a supported field and query; date uses from/until')
            if (index == 0 and term['field'] in ('date', 'keywords')) or type(term.get('not', False)) is not bool:
                raise ServiceError('invalid_options', 'Use date/keywords in additional terms; not must be boolean')
            if term['field'] != 'date' and (not isinstance(term.get('query'), str) or not term['query'].strip()):
                raise ServiceError('invalid_query', 'Every text search field needs a nonempty query')
            if term['field'] == 'date':
                bounds = [term.get(key) for key in ('from', 'until')]
                if (not any(value not in (None, '') for value in bounds)
                        or any(value not in (None, '') and not re.fullmatch(r'\d{4}', str(value))
                               for value in bounds)):
                    raise ServiceError('invalid_options', 'Date bounds are four-digit years')
        page = self.gateway.public_page(self.source)
        goto_source(page, 'https://www.numdam.org/', self.hosts, wait_until='domcontentloaded', timeout=45000)
        for index, term in enumerate(terms):
            if index and not page.locator(f'input[name="q{index}"]').count():
                page.locator('#add-search-field').click()
            group = page.locator('.search-group').filter(has=page.locator(f'input[name="q{index}"]'))
            group.locator('button.dropdown-toggle').click()
            group.locator('a.dropdown-item').filter(has_text=re.compile('^' + FIELDS[term['field']] + '$')).click()
            if term['field'] == 'date':
                for key, name in (('from', 'q-f-'), ('until', 'q-l-')):
                    value = term.get(key)
                    group.locator(f'input[name="{name}{index}"]').fill(
                        '*' if value in (None, '') else str(value))
            else:
                group.locator(f'input[name="q{index}"]').fill(term['query'])
            if term.get('not'):
                group.locator(f'input[name="not{index}"]').check()
        with page.expect_navigation(wait_until='domcontentloaded'):
            page.locator('form').filter(has=page.locator('input[name=q0]')).locator('button[type=submit]').click()
        require_source_url(page.url, self.hosts)
        raw = page.content()
        first = self.store.put(clean_html(raw, self.store.sanitizer), 'text/html', self.source, page.url, role='native_search_page', page=1)
        try:
            first_rows, total = search_records(raw, page.url)
        except ServiceError as error:
            error.result['evidence'] = first
            raise
        soup = BeautifulSoup(raw, 'html.parser')
        second = next((a['href'] for a in soup.select('.pagination a[href]') if a.get_text(strip=True) == '2'), None)
        evidence, rows = [], []
        evidence.append(first)
        for number in range(start // 20 + 1, min((start + limit - 1) // 20 + 1, (total + 19) // 20) + 1):
            if number == 1:
                batch = first_rows
            else:
                link = numbered_page_link(second or '', number)
                if not link:
                    raise ServiceError('pagination_missing', 'Numdam did not expose its next page link', evidence=first)
                goto_source(page, urljoin(first['url'], link), self.hosts, wait_until='domcontentloaded', timeout=45000)
                raw = page.content()
                current = self.store.put(clean_html(raw, self.store.sanitizer), 'text/html', self.source, page.url, role='native_search_page', page=number)
                evidence.append(current)
                batch, current_total = search_records(raw, page.url)
                active = BeautifulSoup(raw, 'html.parser').select_one('.pagination .active')
                if current_total != total or not active or active.get_text(strip=True) != str(number):
                    raise ServiceError('range_mismatch', 'Numdam changed the requested result page or total', evidence=current)
            expected = min(20, total - (number - 1) * 20)
            if len(batch) != expected:
                raise ServiceError('range_mismatch', 'Numdam returned an incomplete result page', evidence=evidence[-1])
            rows.extend(batch[max(0, start - (number - 1) * 20):min(20, start + limit - (number - 1) * 20)])
        result = self.page(rows, total, first, query, options, start, limit)
        if date_only:
            result['native_match_all_query'] = '*'
        result['evidence_pages'] = evidence
        if export in ('native', 'html'):
            result['export'] = {'artifacts': evidence}
        elif export in FORMATS:
            artifacts, errors, contents = [], [], []
            for row in rows:
                try:
                    identifier, _, _ = self.document(row['url'])
                    artifact = self.citation(identifier, export)
                    artifacts.append(artifact)
                    contents.append(self.store.read(artifact['ref'])[1])
                except ServiceError as error:
                    errors.append({'id': row['id'], **error.result})
            combined = self.store.put(b'\n\n'.join(contents), FORMATS[export][1], self.source, first['url'], role='native_citations', requested=len(rows), received=len(artifacts), parent_refs=[a['ref'] for a in artifacts])
            result['export'] = {'status': 'partial' if errors else 'available', **combined, 'artifacts': artifacts, 'errors': errors}
            if errors:
                result['status'] = 'partial'
        return result

    def fetch(self, target, *, parts):
        identifier, requested_doi, page = self.document(target)
        result = super().fetch(identifier, parts=parts)
        result['target'] = target
        result['native_id'] = identifier
        if page:
            result['document_page'] = page
        if 'export' in parts:
            artifacts, errors = [], []
            for kind in FORMATS:
                try:
                    artifacts.append({'format': kind, 'artifact': self.citation(identifier, kind)})
                except ServiceError as error:
                    errors.append({'format': kind, **error.result})
            result['components']['export'] = {'status': 'partial' if errors else 'available', 'artifacts': artifacts, 'errors': errors}
            if artifacts:
                result['components']['export']['artifact'] = artifacts[0]['artifact']
        if 'supplementary' in parts:
            records = json.loads(self.store.read(result['records']['ref'])[1])
            files = []
            errors = []
            for link in records[0]['links']:
                if link['url'].endswith('.djvu'):
                    try:
                        data, original = self.request(link['url'], accept='binary')
                        if not data.startswith(b'AT&TFORM'):
                            raise ServiceError('unexpected_content', 'Numdam did not return a DjVu file')
                        artifact = self.store.put(data, 'image/vnd.djvu', self.source, original['url'], role='alternative_fulltext', identifier=identifier)
                        files.append({'format': 'djvu', 'artifact': artifact})
                    except ServiceError as error:
                        errors.append(error.result)
            result['components']['supplementary'] = {'status': 'partial' if errors else 'available' if files else 'not_offered',
                'artifacts': files, 'errors': errors, 'scope': 'Alternative DjVu fulltext linked by this Numdam record'}
        result['status'] = 'ok' if all(c['status'] == 'available' for c in result['components'].values()) else 'partial'
        return result
