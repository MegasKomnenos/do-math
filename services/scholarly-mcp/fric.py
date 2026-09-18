"""KNU FRIC's public catalogue; copying requests are a separate service."""
import csv
import io
import re
from urllib.parse import parse_qs, urljoin, urlsplit
from waits import SOURCE_WAIT_MS

from bs4 import BeautifulSoup

from browser_adapters import clean_html, goto_source, require_source_url
from scholarly import ServiceError, encoded


def catalogue(raw, base):
    soup = BeautifulSoup(raw, 'html.parser')
    header = soup.select_one('.list_top')
    match = re.search(r'전체\s*([\d,]+)\s*건\(\s*(\d+)\s*/\s*(\d+)\s*페이지', header.get_text(' ', strip=True) if header else '')
    if not match:
        raise ServiceError('catalogue_not_ready', 'FRIC did not display its catalogue count and page')
    total, number, pages = [int(s.replace(',', '')) for s in match.groups()]
    rows = []
    if total:
        for item in soup.select('.search-list > ul > li'):
            title = item.select_one('span.tit')
            link = title.find_parent('a') if title else None
            if not link or not link.get('href'):
                raise ServiceError('catalogue_parse_failed', 'FRIC record has no title or record link')
            url = urljoin(base, link['href'])
            identifier = parse_qs(urlsplit(url).query).get('id', [None])[0]
            if not identifier:
                raise ServiceError('catalogue_parse_failed', 'FRIC record has no public catalogue identifier')
            listing = item.get_text('\n', strip=True)
            issns = list(dict.fromkeys(re.findall(r'\b\d{4}-\d{3}[\dXx]\b', listing)))
            rows.append({'id': identifier, 'title': title.get_text('', strip=False).strip(), 'record_url': url,
                         'issn': issns, 'listing': listing, 'source_fields': [s.get_text(' ', strip=True) for s in item.select('span.data')],
                         'target': 'issn:' + issns[0] if issns else title.get_text(' ', strip=True)})
    links = {int(a.get_text(strip=True)): urljoin(base, a['href']) for a in soup.select('.va-pc a[href]') if a.get_text(strip=True).isdigit()}
    return rows, total, number, pages, links


class KNUFric:
    source = 'knu-fric'
    hosts = {'fric.knu.ac.kr'}
    home = 'https://fric.knu.ac.kr/'
    copy_service = 'https://fric.knu.ac.kr/pages/sub.htm?nav_code=fri1700815450'

    def __init__(self, store, gateway):
        self.store, self.gateway = store, gateway

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        if set(options) - {'field'} or options.get('field', 'journal') not in ('journal', 'article') or cursor:
            raise ServiceError('invalid_options', 'Use field=journal or article; start/limit, no cursor')
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 100:
            raise ServiceError('invalid_range', 'Use start >= 0 and limit 1..100')
        if not query.strip() or export not in (None, 'json', 'html', 'csv'):
            raise ServiceError('invalid_query', 'Use a nonempty catalogue query and json/html/csv export')
        page = self.gateway.public_page(self.source)
        goto_source(page, self.home, self.hosts, wait_until='domcontentloaded', timeout=SOURCE_WAIT_MS)
        field = page.locator('#search_knu_item')
        field.wait_for(timeout=SOURCE_WAIT_MS)
        page.locator('#search_knu_sel').select_option('O' if options.get('field') == 'article' else 'S')
        field.fill(query)
        with page.expect_navigation(wait_until='domcontentloaded'):
            field.press('Enter')
        pages_seen, rows = [], []
        first_total = None
        desired = start // 10 + 1
        last = (start + limit - 1) // 10 + 1
        visited = set()
        while True:
            require_source_url(page.url, self.hosts)
            page.locator('.list_top').wait_for(timeout=SOURCE_WAIT_MS)
            raw = page.content()
            evidence = self.store.put(clean_html(raw, self.store.sanitizer), 'text/html', self.source, page.url, role='catalogue_page', query=query)
            pages_seen.append(evidence)
            try:
                batch, total, number, pages, links = catalogue(raw, page.url)
            except ServiceError as error:
                error.result['evidence'] = evidence
                raise
            if first_total is None:
                first_total = total
            elif total != first_total:
                raise ServiceError('range_mismatch', 'FRIC catalogue total changed between pages', evidence=evidence)
            if number in visited:
                raise ServiceError('pagination_stalled', 'FRIC did not advance the requested page', evidence=evidence)
            visited.add(number)
            if total == 0 or start >= total:
                break
            if len(batch) != min(10, total - (number - 1) * 10):
                raise ServiceError('range_mismatch', 'FRIC rows do not match its displayed page', evidence=evidence)
            if number >= desired:
                offset = (number - 1) * 10
                rows.extend(row for i, row in enumerate(batch, offset) if start <= i < start + limit)
            if number >= min(last, pages):
                break
            next_number = desired if number < desired else number + 1
            if next_number not in links:
                reachable = [n for n in links if number < n <= next_number]
                if not reachable:
                    raise ServiceError('pagination_missing', 'FRIC did not expose a link toward the requested page', evidence=evidence)
                next_number = max(reachable)
            goto_source(page, links[next_number], self.hosts, wait_until='domcontentloaded', timeout=SOURCE_WAIT_MS)
        records = self.store.put(encoded(rows), 'application/json', self.source, pages_seen[0]['url'], role='records', query=query, options=options, start=start, requested=limit)
        exported = records
        if export == 'html':
            exported = {'artifacts': pages_seen}
        elif export == 'csv':
            text = io.StringIO(newline='')
            writer = csv.DictWriter(text, fieldnames=['id','title','issn','record_url','listing','target'])
            writer.writeheader()
            writer.writerows({k: '; '.join(row[k]) if k == 'issn' else row[k] for k in writer.fieldnames} for row in rows)
            exported = self.store.put(text.getvalue(), 'text/csv', self.source, pages_seen[0]['url'], role='catalogue_csv', source_format='mechanical_csv', parent_ref=records['ref'])
        more = start + len(rows) < first_total
        return {'status':'ok' if rows else 'not_found', 'source':self.source, 'query':query, 'options':options, 'start':start,
                'requested':limit, 'received':len(rows), 'total':first_total, 'has_more':more,
                'next':{'start':start+len(rows)} if more else None, 'records':records, 'export':exported,
                'evidence':pages_seen, 'preview':[{'id':r['id'],'title':r['title'],'issn':r['issn']} for r in rows[:3]],
                'scope':'KNU FRIC public holdings catalogue; external RISS links remain references'}

    def fetch(self, target, *, parts):
        if set(parts) - {'metadata','abstract','fulltext','supplementary','export'}:
            raise ServiceError('invalid_parts', 'Use documented content parts')
        value = target.removeprefix('issn:')
        if target.startswith(('http://','https://')):
            raise ServiceError('source_boundary', 'Use the ISSN/target returned by the KNU FRIC catalogue; RISS is a separate linked service')
        found = self.search(value, options={'field':'journal'}, limit=20)
        if found['received'] != 1 or not re.fullmatch(r'\d{4}-\d{3}[0-9Xx]', value):
            found['status'] = 'selection_required' if found['received'] else 'not_found'
            return found
        import json
        row = json.loads(self.store.read(found['records']['ref'])[1])[0]
        if value.upper() not in {s.upper() for s in row['issn']}:
            raise ServiceError('identity_mismatch', 'FRIC returned a different ISSN', evidence=found['evidence'])
        components = {}
        for part in parts:
            if part in ('metadata','export'):
                components[part] = {'status':'available','artifact':found['records']}
            else:
                components[part] = {'status':'not_offered','reason':'This catalogue endpoint provides holdings; article delivery requires the separate document-copy service', 'service_url':self.copy_service}
        return {**found, 'status':'ok' if all(c['status']=='available' for c in components.values()) else 'partial', 'target':target, 'components':components}
