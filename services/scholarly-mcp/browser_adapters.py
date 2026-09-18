"""Observed browser workflows, including KUDOS's academic database gateway."""
from __future__ import annotations
from waits import SOURCE_WAIT_MS, TRANSIENT_ATTEMPTS, TRANSIENT_PAUSE_MS

import json
import logging
import random
import time
from collections import Counter
from pathlib import Path
import re
from uuid import uuid4
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit, urlunsplit, quote, unquote

from bs4 import BeautifulSoup

from scholarly import ServiceError, bibliography, encoded, failure_details

MSC_HOSTS = {"mathscinet.ams.org", "mathscinet-ams-org.libproxy.knu.ac.kr"}


def is_access_challenge(raw):
    soup=BeautifulSoup(raw,'html.parser')
    title=soup.title.get_text(' ',strip=True) if soup.title else ''
    return bool(soup.select_one('#challenge-error-text,#capInput') or
                re.search(r'^(?:Access Denied|Just a moment|Attention Required|403 Forbidden|Client Challenge|Radware Bot Manager Captcha)',title,re.I))


def require_source_url(url, hosts):
    parsed = urlsplit(url)
    if parsed.scheme not in ("https", "http") or parsed.hostname not in hosts or parsed.username or parsed.password or parsed.port not in (None, 80, 443):
        raise ServiceError("source_boundary", "Document navigation left the named source")


def goto_source(page, url, hosts, **kwargs):
    require_source_url(url, hosts)
    response = page.goto(url, **kwargs)
    require_source_url(page.url, hosts)
    return response


def clean_html(raw, sanitizer):
    soup = BeautifulSoup(raw, "html.parser")
    for tag in list(soup.find_all(["script", "input", "form", "iframe", "object", "embed", "button"])):
        if tag.name == "script" and str(tag.get("type", "")).startswith("math/tex") and not tag.has_attr("src"):
            continue
        if tag.name in ("form", "button"):
            tag.unwrap()
        else:
            tag.decompose()
    for tag in soup.find_all(True):
        for key in list(tag.attrs):
            if key.lower().startswith(("on", "data-", "wire:")) or sanitizer.sensitive.search(key):
                del tag.attrs[key]
            elif key in ("href", "src"):
                value = tag.get(key, "")
                if value.lower().startswith(("javascript:", "data:text/html")):
                    del tag.attrs[key]
                elif not value.startswith("data:"):
                    tag[key] = sanitizer.url(value)
    return sanitizer.text(str(soup))


def mathscinet_record(raw, base, sanitizer):
    html = clean_html(raw, sanitizer)
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.select_one('[id^="publication-"]')
    if heading is None:
        raise ServiceError("invalid_response", "MathSciNet result has no publication identity")
    anchors = heading.select('a[href*="article?mr="]')
    if len(anchors) < 2:
        raise ServiceError("invalid_response", "MathSciNet result has no title link")
    mr = re.search(r"mr=([0-9]+)", anchors[0]["href"]).group(1)
    return {"id": "MR" + mr, "title": anchors[1].get_text("", strip=True),
        "url": sanitizer.url(urljoin(base, anchors[0]["href"])), "text": soup.get_text("\n", strip=True),
        "html": html, "links": [{"label": a.get_text(" ", strip=True), "url": sanitizer.url(urljoin(base, a["href"]))} for a in soup.select("a[href]")]}


def mathscinet_target(target):
    if target.startswith(("http://", "https://")):
        parsed = urlsplit(target)
        if parsed.hostname not in MSC_HOSTS:
            raise ServiceError("source_boundary", "The target is outside MathSciNet")
        target = parse_qs(parsed.query).get("mr", [""])[0]
    target = re.sub(r"^MR", "", target, flags=re.I)
    if not re.fullmatch(r"[0-9]{1,8}", target):
        raise ServiceError("invalid_target", "Use an MR number or a MathSciNet article link")
    return target


def retry_transient(action, attempts=None):
    """제공자가 같은 요청에 간헐적으로 내는 일시 오류를 정해진 횟수까지 다시 시도한다.

    retryable 표지가 없는 오류는 요청 쪽 문제이므로 곧바로 올린다. 끝까지 실패하면 시도 횟수를 함께 보고한다.
    """
    attempts = attempts or TRANSIENT_ATTEMPTS
    for attempt in range(1, attempts + 1):
        try:
            return action()
        except ServiceError as error:
            # 안쪽 단계가 이미 횟수를 다 쓴 오류(attempts)는 바깥에서 곱해 다시 시도하지 않는다.
            if not error.result.get('retryable') or 'attempts' in error.result:
                raise
            if attempt == attempts:
                error.result['attempts'] = attempt
                raise
            # 지수 백오프에 지터를 더한다. 여러 호출이 같은 순간에 다시 몰리지 않게 한다.
            time.sleep(TRANSIENT_PAUSE_MS / 1000 * 2 ** (attempt - 1) * (1 + random.random() / 4))


def wos_events(raw):
    events = [json.loads(line) for line in raw.splitlines() if line.strip()]
    failure = next((e.get("payload") for e in events if e.get("key") == "error"), None)
    if failure is not None:
        # WoS는 HTTP 200 스트림 안에 자기 오류를 싣는다. 같은 요청이 다음 번에는 성공하는 일시 오류가 실측되었다.
        raise ServiceError("provider_error", "Web of Science reported an error inside its response stream",
                           provider_message=failure, retryable=True)
    info = next((e["payload"] for e in events if e.get("key") == "searchInfo"), None)
    if info is None or type(info.get("RecordsFound")) is not int:
        raise ServiceError("invalid_response", "WOS search stream has no result count")
    records = {}
    for event in events:
        if event.get("key") == "records":
            records.update(event["payload"])
    return {"total": info["RecordsFound"], "available": info.get("RecordsAvailable"),
        "records": [records[k] for k in sorted(records, key=int)], "events": events}


def wos_facet_candidates(events):
    analyze=next((event.get('payload') for event in events if event.get('key')=='analyze'),None)
    if analyze is None:return []
    if not isinstance(analyze,dict):raise ServiceError('invalid_response','WOS analyze event is not an object')
    controls={'DT':('DT',None),'PY':('PY',None),'DX2NG':('DX2NG',None),
              'OA':('FB',{'OPEN ACCESS':'Open Access'}),'ECR':('FB',{'Y':'Enriched Cited References'})}
    candidates=[]
    for group in analyze.values():
        if not isinstance(group,dict) or not isinstance(group.get('Name'),str) or not isinstance(group.get('Values'),list):
            raise ServiceError('invalid_response','WOS analyze group has an unexpected shape')
        index=group['Name']
        for item in group['Values']:
            if not isinstance(item,dict) or not isinstance(item.get('Key'),str) or type(item.get('Value')) is not int:
                raise ServiceError('invalid_response','WOS facet candidate has an unexpected shape')
            # REVIEW·EARLY ACCESS 같은 빠른 필터 그룹은 키를 DT.로 시작시킨다. 쓰는 그룹에만 이름 접두를 요구한다.
            if index not in controls:continue
            if not item['Key'].startswith(index+'.'):
                raise ServiceError('invalid_response','WOS facet candidate has an unexpected shape')
            value=item['Key'][len(index)+1:];section,labels=controls[index]
            if labels is not None and value not in labels:continue
            candidates.append({'group':index,'value':item['Key'],'label':labels[value] if labels else value,
                               'count':item['Value'],'control_section':section})
    return candidates


WOS_FACET_GROUPS={
    'publication_years':('PY','Publication Years'),'document_types':('DT','Document Types'),
    'researcher_profiles':('DX2NG','Researcher Profiles'),'wos_categories':('TASCA','Web of Science Categories'),
    'citation_topics_meso':('TMSO','Citation Topics Meso'),'citation_topics_micro':('TMIC','Citation Topics Micro'),
    'sustainable_development_goals':('SDG','Sustainable Development Goals'),'wos_indexes':('EDN','Web of Science Index'),
    'affiliations':('OG','Affiliations'),'affiliation_departments':('DLM','Affiliation with Department'),
    'publication_titles':('SO','Publication Titles'),'languages':('LA','Languages'),'countries_regions':('CU','Countries/Regions'),
    'publishers':('PUBL','Publishers'),'research_areas':('SJ','Research Areas'),'open_access_types':('OAJ','Open Access'),
    'funding_agencies':('FO','Funding Agencies'),'conference_titles':('CF','Conference Titles'),'group_authors':('GP','Group Authors'),
    'book_series_titles':('SE','Book Series Titles'),'editors':('ED','Editors'),'editorial_notices':('EN','Editorial Notices')}


def wos_control_candidates(raw,field,group):
    soup=BeautifulSoup(raw,'html.parser');result=[];seen=set()
    for node in soup.select('input[type="checkbox"][name]'):
        if node.get('name')!=group:continue
        value=node.get('value');aria=node.get('aria-label','');match=re.fullmatch(r'(.+?),\s*(\d{1,3}(?:,\d{3})+|\d+)',aria)
        if not isinstance(value,str) or not value.startswith(group+'.') or not match:
            raise ServiceError('invalid_response','WOS facet control has an unexpected identity or count')
        if value in seen:continue
        seen.add(value);result.append({'field':field,'label':match[1],'count':int(match[2].replace(',','')),
                                       'native_group':group,'native_value':value})
    return result


def eccc_records(raw):
    soup = BeautifulSoup(raw, "html.parser")
    records = []
    for box in soup.select("div#box"):
        title = box.select_one("h4")
        link = title.find_parent("a") if title else None
        if not link or not re.fullmatch(r"/report/[0-9]{4}/[0-9]+/?", link.get("href", "")):
            continue
        identity = re.search(r"TR[0-9]{2}-[0-9]{3}", box.get_text(" "))
        records.append({"id": identity.group() if identity else None, "title": title.get_text(" ", strip=True),
            "url": urljoin("https://eccc.weizmann.ac.il/", link["href"]),
            "listing": box.get_text("\n", strip=True), "snippet": "\n".join(p.get_text(" ", strip=True) for p in box.find_all("p"))})
    return records


def eccc_versions(raw):
    soup = BeautifulSoup(raw, "html.parser")
    versions = []
    for box in soup.select("div#box"):
        heading = box.select_one("h4")
        pdf = box.select_one('a[href$="/download"]')
        if not heading or not pdf:
            continue
        link = urljoin("https://eccc.weizmann.ac.il/", pdf["href"])
        revision = re.search(r"/revision/([0-9]+)/download$", link)
        header = heading.parent.get_text(" ", strip=True)
        report = re.search(r"TR[0-9]{2}-[0-9]{3}", header)
        versions.append({"id": report.group() if report else None, "revision": int(revision.group(1)) if revision else 0,
            "title": heading.get_text(" ", strip=True), "version_label": header, "pdf": link,
            "authors": [a.get_text(" ", strip=True) for a in box.select('a[href^="/author/"]')],
            "abstract": "\n\n".join(p.get_text("", strip=False) for p in box.find_all("p", recursive=False))})
    return versions


def acm_records(raw, base):
    soup = BeautifulSoup(raw, "html.parser")
    rows = []
    for item in soup.select("li.search__item"):
        title = item.select_one('.hlFld-Title a[href^="/doi/"]')
        if title is None:
            continue
        identifier = title["href"].split("/doi/", 1)[1]
        rows.append({"id": identifier, "doi": identifier,
            "title": re.sub(r"\s+", " ", title.get_text("", strip=False)).strip(), "url": urljoin(base, title["href"]),
            "listing": item.get_text("\n", strip=True),
            "snippet": "\n".join(p.get_text("", strip=False) for p in item.select(".issue-item__abstract"))})
    return rows


def browser_download(context, url, hosts, *, headers=None, form=None, response_info=None):
    from playwright.sync_api import TimeoutError as BrowserTimeout, Error as BrowserError
    for _ in range(6):
        parsed = urlsplit(url)
        if parsed.hostname in {'validate.perfdrive.com','challenges.cloudflare.com'}:
            raise ServiceError('publisher_access_challenge','Publisher redirected the file request to an access challenge',status='restricted',blocked_host=parsed.hostname)
        if parsed.scheme not in ("https", "http") or parsed.hostname not in hosts or parsed.username or parsed.password or parsed.port not in (None, 80, 443):
            raise ServiceError("source_boundary", "Observed document link left the selected source", blocked_host=parsed.hostname)
        try:
            if form is None:
                response = context.request.get(url, max_redirects=0, timeout=SOURCE_WAIT_MS, headers=headers or {})
            else:
                response = context.request.post(url, data=urlencode(form,doseq=True), max_redirects=0, timeout=SOURCE_WAIT_MS,
                    headers={**(headers or {}),'Content-Type':'application/x-www-form-urlencoded'})
        except BrowserTimeout:
            raise ServiceError("timeout", "Source document did not respond within the download timeout", retryable=True) from None
        except BrowserError:
            raise ServiceError("connection_error", "Source document connection failed", retryable=True) from None
        if response.status in (301, 302, 303, 307, 308):
            url = urljoin(url, response.headers.get("location", ""))
            if response.status in (301,302,303):
                form = None
            continue
        if response.status in (401, 403):
            raise ServiceError("access_restricted", "Source restricted this document", status="restricted", http_status=response.status)
        if response.status == 429:
            raise ServiceError("rate_limited", "Source request limit reached", retry_after=response.headers.get("retry-after"))
        if response.status in (404, 410):
            raise ServiceError("not_found_at_source", "Document not found at this source", status="not_found")
        if response.status >= 400:
            raise ServiceError("provider_error", "Document download failed", http_status=response.status)
        if response_info is not None:
            response_info.update(status=response.status, **{key:response.headers[key] for key in
                ('content-range','content-length','content-encoding','etag','last-modified','date') if key in response.headers})
        return response.body(), response.headers.get("content-type", "application/octet-stream").split(";")[0], response.url
    raise ServiceError("redirect_limit", "Document download returned too many redirects")


def dismiss_cookies(page):
    for selector in ("#onetrust-reject-all-handler", 'button.osano-cm-denyAll'):
        button = page.locator(selector)
        if button.count() and button.first.is_visible():
            button.first.click()
            return
    osano = page.get_by_role("button", name="Reject Non-Essential", exact=True)
    if osano.count() and osano.first.is_visible():
        osano.first.click()
        return
    banner = page.locator("#onetrust-banner-sdk")
    if banner.count() and banner.is_visible():
        page.wait_for_function("typeof OneTrust !== 'undefined' && typeof OneTrust.RejectAll === 'function'", timeout=SOURCE_WAIT_MS)
        page.evaluate("OneTrust.RejectAll()")
        banner.wait_for(state="hidden", timeout=SOURCE_WAIT_MS)


DRIVER = None


def playwright_driver():
    """이 프로세스의 sync Playwright 드라이버를 돌려준다.

    한 스레드는 sync 인스턴스를 하나만 가질 수 있고 서버의 모든 게이트웨이는 한 워커 스레드를 공유한다.
    두 번째 sync_playwright().start()는 거절당해 나중에 뜨는 자료원이 영구히 실패하므로 하나를 함께 쓴다.
    드라이버는 프로세스가 끝날 때까지 산다. 게이트웨이 하나를 닫는다고 멈추지 않는다.
    """
    global DRIVER
    if DRIVER is None:
        from playwright.sync_api import sync_playwright
        DRIVER = sync_playwright().start()
    return DRIVER


class KudosGateway:
    def __init__(self, credential_root, sanitizer, engine="chromium"):
        self.root = Path(credential_root)
        self.sanitizer = sanitizer
        self.engine = engine
        self.context = self.browser = self.playwright = None
        self.pages = {}
        self.credentials(required=False)

    def state_path(self):
        if self.engine not in ('chromium','firefox','webkit'):
            raise ServiceError('invalid_browser_engine','Use a supported browser engine')
        return self.root/'scholarly-mcp'/('kudos-'+self.engine+'.json')

    def save_state(self):
        if self.context is None:return
        state=self.state_path();state.parent.mkdir(parents=True,exist_ok=True)
        temporary=state.with_name('.'+uuid4().hex+'.tmp')
        try:
            temporary.write_text(json.dumps(self.context.storage_state(),ensure_ascii=False),encoding='utf-8')
            temporary.replace(state)
        finally:
            if temporary.exists():temporary.unlink()

    def credentials(self, required=True):
        path = self.root / "kudos.md"
        if not path.exists():
            if not required:
                return {}
            raise ServiceError("credentials_missing", "KUDOS credentials are absent from the protected store", status="restricted", provider="kudos")
        raw = path.read_text("utf-8-sig")
        fields = {}
        for key in ("ID", "PW"):
            match = re.search(r"(?mi)^\s*(?:[-*]\s*)?" + key + r"\s*:\s*(.+?)\s*$", raw)
            if not match:
                if required:
                    raise ServiceError("credentials_invalid", "KUDOS credential file does not contain the expected fields", status="restricted")
                continue
            fields[key] = match.group(1).strip().strip("`")
        self.sanitizer.secrets = tuple(sorted(set(self.sanitizer.secrets) | set(fields.values()), key=len, reverse=True))
        return fields

    def start(self):
        if self.context:
            return
        self.playwright = playwright_driver()
        self.browser = getattr(self.playwright, self.engine).launch(headless=True, **({"channel": "chrome"} if self.engine == "chromium" else {}))
        state = self.state_path()
        if not state.exists():state = self.root / "scholarly-mcp" / "kudos.json"
        self.context = self.browser.new_context(storage_state=str(state) if state.exists() else None, accept_downloads=True)
        self.context.set_default_timeout(SOURCE_WAIT_MS)

    def login(self, page):
        page.goto("https://kudos.knu.ac.kr/pages/index.htm", wait_until="domcontentloaded", timeout=SOURCE_WAIT_MS)
        login = page.get_by_role("link", name="로그인", exact=True).first
        logout = page.get_by_role("link", name="로그아웃", exact=True).first
        login.or_(logout).wait_for(timeout=SOURCE_WAIT_MS)
        if logout.count() and logout.is_visible():
            return
        fields = self.credentials()
        login.click()
        require_source_url(page.url, {"kudos.knu.ac.kr"})
        page.locator("#userid").fill(fields["ID"])
        page.locator("#passwd").fill(fields["PW"])
        page.locator("#passwd").press("Enter")
        try:
            page.get_by_role("link", name="로그아웃", exact=True).first.wait_for(timeout=SOURCE_WAIT_MS)
        except Exception:
            raise ServiceError("authentication_failed", "KUDOS login did not reach an authenticated page", status="restricted", provider="kudos") from None
        self.save_state()

    def open(self, source, label, hosts, ready):
        self.start()
        cached = self.pages.get(source)
        if cached and not cached.is_closed() and urlsplit(cached.url).hostname in hosts:
            return cached
        page = self.context.new_page()
        stage = 'portal_login'
        target = None
        try:
            self.login(page)
            stage = 'academic_database_page'
            page.get_by_role("link", name="검색", exact=True).first.hover()
            page.get_by_role("link", name="학술DB", exact=True).first.click()
            stage = 'database_filter'
            with page.expect_navigation(wait_until="domcontentloaded"):
                page.locator("#search_order").fill(label)
                page.locator("#search_order").press("Enter")
            row = page.locator(".db-tit").filter(has_text=label).first
            stage = 'database_shortcut'
            shortcut = row.get_by_role("link", name="바로가기")
            shortcut.wait_for()
            with self.context.expect_page(timeout=SOURCE_WAIT_MS) as popup:
                shortcut.click()
            target = popup.value
            stage = 'publisher_redirect'
            target.wait_for_url(lambda u: urlsplit(str(u)).hostname in hosts, wait_until="domcontentloaded", timeout=SOURCE_WAIT_MS)
            stage = 'publisher_ready'
            target.locator(ready).filter(visible=True).first.wait_for(timeout=SOURCE_WAIT_MS)
            require_source_url(target.url, hosts)
            self.pages[source] = target
            return target
        except ServiceError:
            raise
        except Exception as error:
            observed_host = urlsplit(target.url).hostname if target is not None else None
            challenge = observed_host in {'validate.perfdrive.com', 'challenges.cloudflare.com'}
            raise ServiceError('publisher_access_challenge' if challenge else 'gateway_navigation_failed',
                'Publisher redirected to an access challenge' if challenge else 'KUDOS academic-DB shortcut did not reach a ready source page',
                status='restricted' if challenge else 'error', source=source, stage=stage, **failure_details(error), observed_host=observed_host, retryable=True) from None
        finally:
            page.close()

    def close(self):
        if self.browser:
            try:self.save_state()
            except Exception as error:
                logging.getLogger('scholarly').warning('browser state was not saved: %s',type(error).__name__)
            self.browser.close()
        self.context = self.browser = self.playwright = None
        self.pages = {}

    def public_page(self, source):
        self.start()
        page = self.pages.get(source)
        if page is None or page.is_closed():
            page = self.context.new_page()
            self.pages[source] = page
        return page


class MathSciNet:
    source = "mathscinet"
    EXPORTS = {"bibtex": "bib", "endnote": "end", "amsref": "ams", "tex": "tex"}
    sorts={'newest':'newest','relevance':'relevance','oldest':'oldest','citations':'citations','author-count':'authors','paging':'paging'}
    facet_groups={'review_status':'Review Status','publication_type':'Publication Type','authors':'Authors','institutions':'Institutions',
                  'primary_classifications':'Primary Classifications','journals':'Journals','publication_years':'Publication Years'}
    facet_native={'review_status':('frs','label'),'publication_type':('fpt','label'),'authors':('auid','numeric'),
                  'institutions':('finst','institution'),'primary_classifications':('fpc','numeric'),
                  'journals':('ji','numeric'),'publication_years':('y','label')}
    facet_payload_groups={'review_status':'reviewStatuses','publication_type':'publicationTypes','authors':'authors',
                          'institutions':'institutions','primary_classifications':'primaryClassifications',
                          'journals':'journals','publication_years':'publicationYears'}
    facet_search_routes={'authors':('/mathscinet/api/publications/authors-facet','authorName'),
                         'institutions':('/mathscinet/api/publications/institutions-facet','names'),
                         'primary_classifications':('/mathscinet/api/publications/prim-class-facet','text'),
                         'journals':('/mathscinet/api/publications/journals-facet','text')}

    def __init__(self, store, gateway):
        self.store, self.gateway = store, gateway

    def page(self):
        return self.gateway.open(self.source, "MathSciNet", MSC_HOSTS, "#searchTextInput, main h1")

    @classmethod
    def advanced_options(cls,options):
        if not isinstance(options,dict) or set(options)-{'sort','facet_filters','facet_group','facet_query'}:
            raise ServiceError('invalid_options','Use current MathSciNet publication sort and facet fields')
        sort=options.get('sort','newest');group=options.get('facet_group');query=options.get('facet_query')
        if sort not in cls.sorts:raise ServiceError('invalid_options','Use a current MathSciNet publication sort')
        if group is not None and group not in cls.facet_groups:raise ServiceError('invalid_options','Use a current MathSciNet publication facet field')
        if query is not None and (group is None or not isinstance(query,str) or not query.strip()):
            raise ServiceError('invalid_options','facet_query needs facet_group and a nonempty search string')
        filters=[];raw=options.get('facet_filters')
        if raw is not None:
            if not isinstance(raw,dict):raise ServiceError('invalid_options','facet_filters must map current result fields to include/exclude labels')
            for field,spec in raw.items():
                if field not in cls.facet_groups or not isinstance(spec,dict) or not spec or set(spec)-{'include','exclude'}:
                    raise ServiceError('invalid_options','Each facet field needs include and/or exclude exact labels')
                include=spec.get('include',[]);exclude=spec.get('exclude',[])
                if not include and not exclude or any(not isinstance(items,list) or not items or any(not isinstance(item,str) or not item.strip() for item in items)
                       or len({item.casefold() for item in items})!=len(items) for items in (include,exclude) if items) \
                        or {item.casefold() for item in include}&{item.casefold() for item in exclude}:
                    raise ServiceError('invalid_options','Facet labels must be distinct and cannot be both included and excluded')
                filters.append((field,cls.facet_groups[field],include,exclude))
        return {'sort':cls.sorts[sort],'sort_name':sort,'facet_filters':filters,
                'facet_preview':(group,query) if group else None}

    @classmethod
    def facet_candidates(cls,raw,field):
        if field not in cls.facet_groups:raise ServiceError('invalid_options','Use a current MathSciNet publication facet field')
        soup=BeautifulSoup(raw,'html.parser');sections=[]
        for section in soup.select('div.section'):
            title=section.select_one('.title label.m-0')
            if title and title.get_text(' ',strip=True)==cls.facet_groups[field]:sections.append(section)
        if len(sections)!=1:return []
        result=[];seen=set()
        for box in sections[0].select('[role="checkbox"][aria-label]'):
            label=box.get('aria-label','')
            if '<' in label:label=BeautifulSoup(label,'html.parser').get_text(' ',strip=True)
            label=re.sub(r'\s+',' ',label).strip()
            container=box.parent;count=None
            for _ in range(4):
                if container is None:break
                numbers=re.findall(r'(?<!\d)([\d,]+)(?!\d)',container.get_text(' ',strip=True))
                if numbers:
                    count=int(numbers[-1].replace(',',''));break
                container=container.parent
            if not label or count is None:continue
            key=label.casefold()
            if key in seen:raise ServiceError('invalid_response','MathSciNet facet labels are duplicated in one group')
            seen.add(key);result.append({'label':label,'count':count})
        return result

    @staticmethod
    def validate_search_request(url,query,page,size,sort,facets):
        params=parse_qs(urlsplit(url).query,keep_blank_values=True)
        expected={'query':[query],'currentPage':[str(page)],'pageSize':[str(size)],'sort':[sort]}
        if any(params.get(key)!=value for key,value in expected.items()):
            raise ServiceError('query_mismatch','MathSciNet search request did not retain query, sort, facets and result range')
        actual_facets=params.get('facets')
        if actual_facets!=[facets] and not (facets=='' and actual_facets is None):
            raise ServiceError('query_mismatch','MathSciNet search request retained another facet state')

    @staticmethod
    def matches_facet_response(response,host,query):
        location=urlsplit(response.url)
        return location.hostname==host and location.path=='/mathscinet/api/publications/facets' and \
            parse_qs(location.query,keep_blank_values=True).get('query')==[query]

    @classmethod
    def facet_source_candidates(cls,field,rows):
        if not isinstance(rows,list):raise ServiceError('invalid_response','MathSciNet facet response omitted a current group',field=field)
        candidates=[];seen=set();_,kind=cls.facet_native[field]
        for order,row in enumerate(rows):
            if not isinstance(row,dict) or not isinstance(row.get('id'),str) or not isinstance(row.get('value'),str) or type(row.get('total')) is not int:
                raise ServiceError('invalid_response','MathSciNet facet response has a malformed candidate',field=field)
            source_label=' '.join(BeautifulSoup(row['value'],'html.parser').get_text(' ',strip=True).split())
            label=(row['id']+' - '+source_label) if field=='primary_classifications' else source_label;folded=label.casefold()
            if not label or folded in seen:raise ServiceError('invalid_response','MathSciNet facet response duplicated a label',field=field)
            seen.add(folded);native=(json.dumps(label,ensure_ascii=False) if kind=='label' else "v'"+row['id']+"'" if kind=='institution' else json.dumps(row['id']))
            candidates.append({'label':label,'source_label':source_label,'count':row['total'],'native_term':native,'native_order':order,'source_id':row['id']})
        return candidates

    @classmethod
    def facet_payload_candidates(cls,payload):
        if not isinstance(payload,dict):raise ServiceError('invalid_response','MathSciNet facet response is not an object')
        return {field:cls.facet_source_candidates(field,payload.get(key)) for field,key in cls.facet_payload_groups.items()}

    @classmethod
    def validate_facet_query(cls,previous,current,field,selected):
        tag,_=cls.facet_native[field]
        if not selected or any(item.get('state') not in ('include','exclude') or not isinstance(item.get('native_term'),str) or not item['native_term'] for item in selected):
            raise ServiceError('query_mismatch','MathSciNet facet validation requires source-bound native candidate values',field=field)
        include=[item for item in selected if item['state']=='include'];exclude=[item for item in selected if item['state']=='exclude'];parts=[]
        if not current.startswith(previous+' '):
            raise ServiceError('query_mismatch','MathSciNet facet query did not retain the exact selected group, mode and native values',field=field,stage='facet_delta_prefix')
        tail=current[len(previous)+1:]
        def consume(text,items):
            remaining=Counter(item['native_term'] for item in items);wrapped=len(items)>1
            if wrapped:
                if not text.startswith('('):return None
                position=1
            else:position=0
            def match(offset,left):
                if not left:
                    return offset+1 if wrapped and text.startswith(')',offset) else offset if not wrapped else None
                for term in sorted(left,key=len,reverse=True):
                    if text.startswith(term,offset):
                        rest=left.copy();rest[term]-=1
                        if not rest[term]:del rest[term]
                        end=offset+len(term)
                        if rest:
                            if not text.startswith(' OR ',end):continue
                            end+=4
                        found=match(end,rest)
                        if found is not None:return found
                return None
            return match(position,remaining)
        if include:
            prefix=tag+':'
            if not tail.startswith(prefix):raise ServiceError('query_mismatch','MathSciNet facet query used another native group',field=field)
            end=consume(tail[len(prefix):],include)
            if end is None:raise ServiceError('query_mismatch','MathSciNet facet query changed the included native values',field=field)
            tail=tail[len(prefix)+end:]
        if exclude:
            prefix=(' NOT ' if include else 'NOT ')+tag+':'
            if not tail.startswith(prefix):raise ServiceError('query_mismatch','MathSciNet facet query omitted or changed the exclusion',field=field)
            end=consume(tail[len(prefix):],exclude)
            if end is None:raise ServiceError('query_mismatch','MathSciNet facet query changed the excluded native values',field=field)
            tail=tail[len(prefix)+end:]
        if tail:
            raise ServiceError('query_mismatch','MathSciNet facet query retained unrequested terms',field=field,stage='facet_delta_tail')

    def facet_scope(self,page,field):
        heading=self.facet_groups[field]
        scopes=page.locator('div.section').filter(has=page.get_by_text(heading,exact=True)).filter(visible=True)
        if scopes.count()!=1:
            all_labels=page.get_by_text(heading,exact=True);display=None
            raise ServiceError('facet_selection_required','The current MathSciNet result has no unique requested facet group',status='selection_required',field=field,
                               candidate_group_count=scopes.count(),attached_group_count=all_labels.count(),panel_display=display)
        return scopes.first

    def open_facets(self,page):
        if page.get_by_text('Review Status',exact=True).filter(visible=True).count():return
        dismiss_cookies(page)
        close=page.get_by_role('button',name='Close',exact=True).filter(visible=True)
        if close.count():
            close.first.click();page.wait_for_timeout(250)
        button=page.locator('button[name="Show filters button"]').filter(visible=True)
        try:button.first.wait_for(state='visible',timeout=SOURCE_WAIT_MS)
        except Exception:
            main=page.locator('main');text=main.inner_text() if main.count() else ''
            raise ServiceError('facet_selection_required','MathSciNet did not finish rendering its current result filters',status='selection_required',
                               page_path=urlsplit(page.url).path,page_title=page.title(),main_text=' '.join(text.split())[:160]) from None
        if button.count()!=1:raise ServiceError('facet_selection_required','MathSciNet did not offer its current result filters',status='selection_required',filter_button_count=button.count())
        button.click()
        page.get_by_text('Review Status',exact=True).filter(visible=True).first.wait_for(state='visible',timeout=SOURCE_WAIT_MS)

    def current_facet_candidates(self,scope,field):
        return self.facet_candidates(scope.evaluate('(node)=>node.outerHTML'),field)

    def search_facet_candidates(self,page,scope,field,value,effective_query,native_catalog=None):
        search=scope.locator('input[placeholder="Search '+self.facet_groups[field]+'"]');route,param=self.facet_search_routes[field]
        if search.input_value()==value:
            search.fill('');page.wait_for_timeout(100)
        with page.expect_response(lambda response:urlsplit(response.url).hostname in MSC_HOSTS and urlsplit(response.url).path==route and
                                  parse_qs(urlsplit(response.url).query,keep_blank_values=True).get('query')==[effective_query] and
                                  parse_qs(urlsplit(response.url).query,keep_blank_values=True).get(param)==[value],timeout=SOURCE_WAIT_MS) as event:search.fill(value)
        response=event.value
        if response.status!=200:raise ServiceError('provider_error','MathSciNet facet candidate search failed',http_status=response.status,field=field)
        searched=self.facet_source_candidates(field,response.json());existing={(item['label'].casefold(),item['source_id']):item for item in (native_catalog or {}).get(field,[])}
        for item in searched:existing[(item['label'].casefold(),item['source_id'])]=item
        if native_catalog is not None:native_catalog[field]=list(existing.values())
        group=search.locator('xpath=ancestor::div[contains(@class,"input-group")][1]');button=group.locator('button:visible')
        if button.count()!=1:raise ServiceError('facet_selection_required','MathSciNet facet search has no unique visible control',status='selection_required',field=field)
        search.scroll_into_view_if_needed();button.click();source_labels={item['label'].casefold() for item in searched};current=None
        for _ in range(60):
            current=self.current_facet_candidates(scope,field)
            if all(item['label'].casefold() in source_labels for item in current) and (current or not searched):break
            page.wait_for_timeout(250)
        else:raise ServiceError('facet_candidates_not_ready','MathSciNet facet search did not display its source-bound candidates',field=field)
        return searched,current

    def resolve_facet(self,page,scope,field,label,native_catalog=None,effective_query=None):
        candidates=self.current_facet_candidates(scope,field)
        matches=[item for item in candidates if item['label'].casefold()==label.casefold()]
        if len(matches)!=1:
            search=scope.locator('input[placeholder="Search '+self.facet_groups[field]+'"]')
            if search.count():
                tokens=re.findall(r'\w{3,}',label);fallback=max(tokens,key=len) if tokens else label;queries=list(dict.fromkeys((label,fallback)));searched=[]
                for value in queries:
                    searched,candidates=self.search_facet_candidates(page,scope,field,value,effective_query,native_catalog)
                    if sum(item['label'].casefold()==label.casefold() for item in searched)==1:break
                matches=[item for item in candidates if item['label'].casefold()==label.casefold()]
        if len(matches)!=1:
            raise ServiceError('facet_selection_required','Select one exact label from the current MathSciNet facet group',status='selection_required',field=field,candidates=candidates)
        boxes=[]
        for box in scope.locator('[role="checkbox"][aria-label]').all():
            value=box.get_attribute('aria-label') or ''
            if '<' in value:value=BeautifulSoup(value,'html.parser').get_text(' ',strip=True)
            if re.sub(r'\s+',' ',value).strip().casefold()==label.casefold():boxes.append(box)
        if len(boxes)!=1:raise ServiceError('facet_selection_required','The selected MathSciNet label has no unique native control',status='selection_required',field=field,candidates=candidates)
        return boxes[0],matches[0],candidates

    def apply_facets(self,page,query,size,sort,filters,preview,base_total=None,native_catalog=None):
        if not filters and preview is None:return '',[],[],None
        page.wait_for_function("() => document.querySelectorAll('input[name=\"Select article checkbox\"]').length > 0",timeout=SOURCE_WAIT_MS)
        self.open_facets(page);evidence=[];artifacts=[];effective=query;current_total=base_total
        for field,_,include,exclude in filters:
            self.open_facets(page)
            scope=self.facet_scope(page,field);selected=[];all_candidates=[]
            for state,labels in (('include',include),('exclude',exclude)):
                for label in labels:
                    box,candidate,candidates=self.resolve_facet(page,scope,field,label,native_catalog,effective);all_candidates=candidates
                    native=[item for item in (native_catalog or {}).get(field,[]) if item['label'].casefold()==label.casefold()]
                    if len(native)!=1:raise ServiceError('facet_selection_required','The selected MathSciNet label has no unique source facet identity',status='selection_required',field=field,candidates=candidates)
                    clicks=1 if state=='include' else 2
                    for _ in range(clicks):box.evaluate('(node)=>node.click()');page.wait_for_timeout(100)
                    expected='true' if state=='include' else 'mixed'
                    if box.get_attribute('aria-checked')!=expected:
                        raise ServiceError('facet_selection_failed','MathSciNet did not retain the requested include/exclude state',field=field,label=label)
                    selected.append({**candidate,**{key:native[0][key] for key in ('native_term','native_order')},'state':state})
            artifacts.append(self.store.put(encoded(all_candidates),'application/json',self.source,page.url,role='facet_candidates',field=field,
                scope='Current MathSciNet result facet candidates'))
            facet_responses=[]
            def captured_facet(response):
                if urlsplit(response.url).hostname in MSC_HOSTS and urlsplit(response.url).path=='/mathscinet/api/publications/facets':facet_responses.append(response)
            page.on('response',captured_facet)
            try:
                with page.expect_response(lambda response:urlsplit(response.url).hostname in MSC_HOSTS and urlsplit(response.url).path=='/mathscinet/api/publications/search',timeout=SOURCE_WAIT_MS) as event:
                    scope.get_by_role('button',name='Apply',exact=True).filter(visible=True).first.click(no_wait_after=True)
                response=event.value
                if response.status!=200:raise ServiceError('provider_error','MathSciNet facet refinement failed',http_status=response.status,field=field)
                params=parse_qs(urlsplit(response.url).query,keep_blank_values=True);new_query=params.get('query',[None])[0]
                if not isinstance(new_query,str) or not new_query or new_query==effective or params.get('sort')!=[sort]:
                    raise ServiceError('query_mismatch','MathSciNet refinement did not add the selected facet labels',field=field,
                                       query_keys=sorted(params),facets_present='facets' in params,query_matches=params.get('query')==[effective],
                                        query_length=len(params.get('query',[''])[0]),observed_query=new_query,selected=selected)
                self.validate_facet_query(effective,new_query,field,selected)
                matching_facets=[]
                for _ in range(180):
                    matching_facets=[item for item in facet_responses if parse_qs(urlsplit(item.url).query,keep_blank_values=True).get('query')==[new_query]]
                    if matching_facets:break
                    page.wait_for_timeout(250)
            finally:
                page.remove_listener('response',captured_facet)
            if not matching_facets or matching_facets[-1].status!=200:
                raise ServiceError('query_mismatch','MathSciNet refreshed facets are not bound to the refined query',field=field,stage='facet_refresh_query')
            native_catalog.update(self.facet_payload_candidates(matching_facets[-1].json()))
            total,rows,_=self.validated_search_page(response.json(),1,size)
            if current_total is not None and total>current_total:raise ServiceError('result_set_mismatch','MathSciNet refinement enlarged the current result set',field=field)
            current_total=total;effective=new_query;evidence.append(self.store.put(encoded(response.json()),'application/json',self.source,response.url,
                role='facet_response',field=field,selected=selected,total=total,received=len(rows),native_query=effective))
        preview_artifact=None
        if preview:
            self.open_facets(page);field,facet_query=preview;scope=self.facet_scope(page,field)
            if facet_query:
                search=scope.locator('input[placeholder="Search '+self.facet_groups[field]+'"]')
                if not search.count():raise ServiceError('facet_selection_required','This MathSciNet facet group has no candidate search',status='selection_required',field=field)
                _,candidates=self.search_facet_candidates(page,scope,field,facet_query,effective,native_catalog)
            else:candidates=self.current_facet_candidates(scope,field)
            preview_artifact=self.store.put(encoded(candidates),'application/json',self.source,page.url,role='facet_candidates',field=field,query=facet_query,
                scope='Current MathSciNet result facet candidates')
        return effective,evidence,artifacts,preview_artifact

    @staticmethod
    def validated_search_page(payload,page_number,page_size,previous_total=None):
        if not isinstance(payload,dict) or not isinstance(payload.get('results'),list) or type(payload.get('total')) is not int or payload['total']<0:
            raise ServiceError('invalid_response','MathSciNet search response has an unexpected schema')
        total=payload['total']
        if previous_total is not None and total!=previous_total:
            raise ServiceError('search_range_changed','MathSciNet result total changed while reading the requested range',
                previous_total=previous_total,current_total=total,page=page_number)
        offset=(page_number-1)*page_size
        expected=min(page_size,max(0,total-offset))
        rows=payload['results']
        identifiers=[]
        for row in rows:
            value=row.get('mrnumber') if isinstance(row,dict) else None
            if isinstance(value,bool) or not re.fullmatch(r'[0-9]+',str(value or '')):
                raise ServiceError('invalid_response','MathSciNet search result has no valid MR identity',page=page_number)
            identifiers.append(str(int(value)))
        if len(rows)!=expected or len(identifiers)!=len(set(identifiers)):
            raise ServiceError('invalid_response','MathSciNet search page does not match its reported range',
                page=page_number,expected=expected,received=len(rows))
        return total,rows,identifiers

    @staticmethod
    def record_identity(text,mr):
        match=re.search(r'\bMR([0-9]+)\b',text)
        if not match or int(match[1])!=int(mr):
            raise ServiceError('identity_mismatch','MathSciNet record heading identifies another MR publication')
        return match[1]

    @staticmethod
    def citation_control(raw,base,mr,*,basis='references'):
        if basis not in ('references','reviews'):
            raise ServiceError('invalid_options','Use citation_basis references or reviews')
        soup=BeautifulSoup(raw,'html.parser')
        sections=[heading.parent for heading in soup.find_all('h3') if heading.get_text(' ',strip=True)=='Citations']
        if len(sections)!=1:
            raise ServiceError('citation_control_missing','MathSciNet record has no unique Citations section')
        section=sections[0];canonical=str(int(mr));controls={}
        for label,key in (('From References','references'),('From Reviews','reviews')):
            lines=[node for node in section.find_all(['div','p'])
                   if re.fullmatch(re.escape(label)+r':\s*[\d,]+',node.get_text(' ',strip=True))]
            if len(lines)!=1:
                raise ServiceError('citation_control_invalid','MathSciNet Citations section has no unique basis count',basis=key)
            line=lines[0];count=int(re.search(r'([\d,]+)$',line.get_text(' ',strip=True))[1].replace(',',''))
            links=line.select('a[href]');control={'total':count,'query':None,'url':None}
            if count:
                if len(links)!=1:
                    raise ServiceError('citation_control_invalid','MathSciNet citation count has no unique search control',basis=key)
                url=urljoin(base,links[0]['href']);parts=urlsplit(url);query=parse_qs(parts.query).get('query',[None])[0]
                valid=parts.hostname==urlsplit(base).hostname and parts.path=='/mathscinet/publications-search'
                if key=='references':valid=valid and query=='cp:'+canonical
                else:
                    match=re.fullmatch(r'r:\(MR([0-9]+) OR "refcno ([0-9]+)"\)',query or '')
                    valid=valid and bool(match) and int(match[1])==int(match[2])==int(canonical)
                if not valid:
                    raise ServiceError('citation_control_invalid','MathSciNet citation control identifies another record or basis',basis=key)
                control.update({'query':query,'url':url})
            elif links:
                raise ServiceError('citation_control_invalid','MathSciNet zero citation count unexpectedly has a search control',basis=key)
            controls[key]=control
        chosen=controls[basis]
        return {'target':'MR'+mr,'query':chosen['query'],'total':chosen['total'],
                'from_references':controls['references']['total'],'from_reviews':controls['reviews']['total'],'url':chosen['url']}

    def citation_relation(self,mr,basis='references'):
        page=self.page();host=urlsplit(page.url).hostname
        url='https://'+host+'/mathscinet/article?'+urlencode({'mr':mr})
        goto_source(page,url,MSC_HOSTS,wait_until='domcontentloaded',timeout=SOURCE_WAIT_MS)
        heading=page.locator('main h1').first;heading.wait_for(timeout=SOURCE_WAIT_MS)
        observed_mr=self.record_identity(heading.inner_text(),mr)
        relation=self.citation_control(page.locator('main').inner_html(),url,observed_mr,basis=basis)
        evidence=self.store.put(encoded(relation),'application/json',self.source,url,role='citation_relation_control',direction='incoming',basis=basis)
        return {**relation,'evidence':evidence}

    def relationship_target(self,target):
        if re.fullmatch(r'(?:MR)?[0-9]+',target,re.I):
            return {'mr':mathscinet_target(target),'requested_target':target,'lookup':None}
        if not re.match(r'^(?:10\.\d{4,9}/|doi:|https?://(?:dx\.)?doi\.org/)',target,re.I):
            raise ServiceError('invalid_target','Supply an MR number or DOI for a MathSciNet relationship search')
        from api_adapters import doi
        identifier=doi(target)
        query='doi:('+json.dumps(identifier,ensure_ascii=False)+')'
        found=self.search(query,options={},limit=2,export='bibtex')
        lookup={'query':query,'records':found.get('records'),'export':found.get('export')}
        if found.get('status')=='ok' and found.get('total')==found.get('received')==1:
            rows=json.loads(self.store.read(found['records']['ref'])[1])
            citations=bibliography(self.store.read(found['export']['ref'])[1],'application/x-bibtex')
            if len(rows)==len(citations)==1 and citations[0].get('doi','').casefold()==identifier.casefold():
                return {'mr':str(rows[0]['mrnumber']),'requested_target':target,'lookup':lookup}
        raise ServiceError('selection_required','Select one MR record; DOI relationship searches require one native citation identity match',
            status='selection_required',requested_target=target,lookup=lookup)

    @staticmethod
    def reference_control(raw,base,mr):
        soup=BeautifulSoup(raw,'html.parser')
        matches=[]
        for link in soup.find_all('a',href=True):
            if link.get_text(' ',strip=True)!='Search References':continue
            url=urljoin(base,link['href']);parts=urlsplit(url)
            query=parse_qs(parts.query).get('query',[None])[0]
            if parts.hostname==urlsplit(base).hostname and parts.path=='/mathscinet/publications-search' and isinstance(query,str) and re.fullmatch(r'@\|mr:[0-9]+(?:,[0-9]+)*',query):
                matches.append((link,url,query))
        if len(matches)!=1:
            raise ServiceError('reference_control_missing','MathSciNet record has no unique Search References control')
        link,url,query=matches[0]
        identifiers=query.removeprefix('@|mr:').split(',')
        container=link.find_parent('div',class_=lambda value:value and 'card-body' in value.split())
        source_items=len(container.select('li')) if container else None
        unique=len(set(identifiers))
        return {'target':'MR'+mr,'query':query,'url':url,'source_reference_items':source_items,
                'searchable_mr_occurrences':len(identifiers),'searchable_unique_mrs':unique,
                'duplicate_mr_occurrences':len(identifiers)-unique}

    def reference_relation(self,mr):
        page=self.page();host=urlsplit(page.url).hostname
        url='https://'+host+'/mathscinet/article?'+urlencode({'mr':mr})
        goto_source(page,url,MSC_HOSTS,wait_until='domcontentloaded',timeout=SOURCE_WAIT_MS)
        heading=page.locator('main h1').first;heading.wait_for(timeout=SOURCE_WAIT_MS)
        observed_mr=self.record_identity(heading.inner_text(),mr)
        raw=page.locator('main').inner_html()
        relation=self.reference_control(raw,url,observed_mr)
        source_page=self.store.put(clean_html(raw,self.store.sanitizer),'text/html',self.source,url,
            role='reference_source_page',mr='MR'+observed_mr,scope='Original source bibliography including entries without searchable MR identities')
        evidence=self.store.put(encoded(relation),'application/json',self.source,url,role='reference_relation_control',direction='outgoing',
            scope='MathSciNet-indexed MR subset from the source reference list',source_page_ref=source_page['ref'])
        return {**relation,'evidence':evidence,'source_page':source_page}

    def citing(self,target,*,sort,start=0,limit=20,cursor=None,export=None,citation_basis='references'):
        resolved=self.relationship_target(target);mr=resolved['mr']
        relation=self.citation_relation(mr,citation_basis)
        label={'references':'From References','reviews':'From Reviews'}[citation_basis]
        if relation['total']==0:
            artifact=self.store.put(b'[]','application/json',self.source,relation['evidence']['url'],role='citation_records',target=relation['target'],basis=citation_basis,total=0)
            return {'status':'not_found','source':self.source,'query':target,'options':{'kind':'citations','sort':sort,'citation_basis':citation_basis},
                'kind':'citations','target':relation['target'],'lookup':resolved['lookup'],'native_query':None,'start':start,'requested':limit,
                'received':0,'total':0,'has_more':False,'next':None,'records':artifact,'export':artifact,
                'relation':{'direction':'incoming','basis':label,'total':0,'from_references':relation['from_references'],
                'from_reviews':relation['from_reviews'],'evidence':relation['evidence']},'evidence':[relation['evidence']]}
        found=self.search(relation['query'],options={'sort':sort},start=start,limit=limit,cursor=cursor,export=export)
        if citation_basis=='references' and found.get('total')!=relation['total']:
            raise ServiceError('citation_count_mismatch','MathSciNet cited-by results differ from the document control',
                               target=relation['target'],control_total=relation['total'],search_total=found.get('total'),evidence=relation['evidence'])
        counts={} if citation_basis=='references' else {'control_total':relation['total'],'result_total':found.get('total'),
            'count_difference':found.get('total')-relation['total'] if type(found.get('total')) is int else None}
        return {**found,'query':target,'options':{'kind':'citations','sort':sort,'citation_basis':citation_basis},'kind':'citations','target':relation['target'],'lookup':resolved['lookup'],
                'native_query':relation['query'],'relation':{'direction':'incoming','basis':label,'total':relation['total'],
                'from_references':relation['from_references'],'from_reviews':relation['from_reviews'],**counts,'evidence':relation['evidence']},
                'evidence':[relation['evidence'],*found.get('evidence',[])]}

    def references(self,target,*,sort,start=0,limit=20,cursor=None,export=None):
        resolved=self.relationship_target(target);mr=resolved['mr']
        relation=self.reference_relation(mr)
        found=self.search(relation['query'],options={'sort':sort},start=start,limit=limit,cursor=cursor,export=export)
        if found.get('total')!=relation['searchable_unique_mrs']:
            raise ServiceError('reference_count_mismatch','MathSciNet searchable references differ from the document control',
                target='MR'+mr,control_total=relation['searchable_unique_mrs'],search_total=found.get('total'),evidence=relation['evidence'])
        fields={key:relation[key] for key in ('source_reference_items','searchable_mr_occurrences','searchable_unique_mrs','duplicate_mr_occurrences')}
        source_evidence=[relation['source_page']] if relation.get('source_page') else []
        return {**found,'query':target,'options':{'kind':'references','sort':sort},'kind':'references','target':'MR'+mr,'lookup':resolved['lookup'],
            'native_query':relation['query'],'relation':{'direction':'outgoing','basis':'Search References',
            'scope':'MathSciNet-indexed MR subset from the source reference list',**fields,'evidence':relation['evidence'],
            **({'source_page':relation['source_page']} if relation.get('source_page') else {})},
            'evidence':[relation['evidence'],*source_evidence,*found.get('evidence',[])]}

    def citation_exports(self,identifiers,formats):
        if any(not re.fullmatch(r'[0-9]+',str(value)) for value in identifiers):
            raise ServiceError('invalid_export','Every selected citation must have an MR number')
        identifiers=[str(int(value)) for value in identifiers]
        if not identifiers or len(identifiers)!=len(set(identifiers)) or any(format not in self.EXPORTS for format in formats):
            raise ServiceError('invalid_export','Select distinct MR numbers and documented citation formats')
        page=self.page();host=urlsplit(page.url).hostname
        url='https://'+host+'/mathscinet/api/publications/format?'+urlencode({'formats':'ams,bib,tex,end','ids':','.join(identifiers)})
        data,_,actual=browser_download(self.gateway.context,url,MSC_HOSTS)
        try:payload=json.loads(data)
        except ValueError:raise ServiceError('invalid_response','MathSciNet returned no citation JSON') from None
        evidence=self.store.put(encoded(payload),'application/json',self.source,actual,role='provider_citation_formats',requested_mr_order=identifiers)
        order=[str(row.get('paperId')) for row in payload if isinstance(row,dict)] if isinstance(payload,list) else []
        if not isinstance(payload,list) or len(order)!=len(payload) or len(order)!=len(set(order)) or set(order)!=set(identifiers):
            raise ServiceError('citation_identity_mismatch','MathSciNet citation response identifies a different set of MR records',evidence=evidence)
        media={'bibtex':'application/x-bibtex','endnote':'application/x-endnote-refer','amsref':'text/plain','tex':'application/x-tex'}
        exports=[]
        for format in formats:
            values=[row.get(self.EXPORTS[format]) for row in payload]
            if any(not isinstance(value,str) or not value.strip() for value in values):
                raise ServiceError('citation_format_missing','MathSciNet omitted a requested formatted citation',format=format,evidence=evidence,partial_exports=exports)
            text='\n\n'.join(values)
            if format in ('bibtex','endnote'):
                parsed=bibliography(text.encode('utf-8'),media[format])
                observed=[]
                for item in parsed:
                    value=item.get('mrnumber',item.get('id','')) if format=='bibtex' else item.get('fields',{}).get('L',[''])[0]
                    try:observed.append(str(int(mathscinet_target(str(value)))))
                    except (ServiceError,ValueError):observed.append(None)
                if observed!=order:
                    raise ServiceError('citation_identity_mismatch','Formatted citations differ from their MR publication records',format=format,evidence=evidence,partial_exports=exports)
            artifact=self.store.put(text,media[format],self.source,actual,preserve_bytes=True,role='citation_export',format=format,count=len(payload),
                mr_order=order,requested_mr_order=identifiers,parent_ref=evidence['ref'],serialization='Provider-formatted strings joined by blank lines; provider array order retained')
            exports.append({'format':format,'artifact':artifact})
        return exports

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 100:
            raise ServiceError("invalid_range", "MathSciNet requires start >= 0 and limit 1..100")
        advanced_keys={'sort','facet_filters','facet_group','facet_query'}
        if cursor or set(options) - (advanced_keys|{"kind","citation_basis"}):
            raise ServiceError("invalid_options", "MathSciNet uses start; select publications, citations or references and a documented sort")
        settings=self.advanced_options({key:value for key,value in options.items() if key in advanced_keys})
        sort_name=options.get("sort", "newest");sort=settings['sort']
        kind=options.get('kind','publications')
        if kind not in ('publications','citations','references'):
            raise ServiceError('invalid_options','Use kind publications, citations or references')
        citation_basis=options.get('citation_basis','references')
        if citation_basis not in ('references','reviews') or (kind!='citations' and 'citation_basis' in options):
            raise ServiceError('invalid_options','Use citation_basis references or reviews only with kind citations')
        if export not in (None, "json", *self.EXPORTS):
            raise ServiceError("invalid_export", "Use json, bibtex, endnote, amsref or tex")
        if kind=='citations':
            if set(options)-{'kind','sort','citation_basis'}:raise ServiceError('invalid_options','MathSciNet relationship searches do not accept publication facet filters')
            arguments={'sort':sort_name,'start':start,'limit':limit,'cursor':cursor,'export':export}
            if 'citation_basis' in options:arguments['citation_basis']=citation_basis
            return self.citing(query,**arguments)
        if kind=='references':
            if set(options)-{'kind','sort'}:raise ServiceError('invalid_options','MathSciNet relationship searches do not accept publication facet filters')
            return self.references(query,sort=sort_name,start=start,limit=limit,cursor=cursor,export=export)
        page = self.page()
        host = urlsplit(page.url).hostname
        size = next(n for n in (5, 10, 20, 50, 100) if n >= limit)
        first_page = start // size + 1
        last_page = (start + limit - 1) // size + 1
        effective_query=query;filter_evidence=[];facet_artifacts=[];facet_preview=None;zero_filter_state=None
        if settings['facet_filters'] or settings['facet_preview']:
            control_url="https://"+host+"/mathscinet/publications-search?"+urlencode({'query':query,'page':1,'size':size,'sort':sort,'facets':''})
            with page.expect_response(lambda response:self.matches_facet_response(response,host,query),timeout=SOURCE_WAIT_MS) as facet_event:
                with page.expect_response(lambda response:urlsplit(response.url).hostname==host and urlsplit(response.url).path=='/mathscinet/api/publications/search'
                                           and parse_qs(urlsplit(response.url).query).get('query')==[query],timeout=SOURCE_WAIT_MS) as control:
                    goto_source(page,control_url,MSC_HOSTS,wait_until='domcontentloaded',timeout=SOURCE_WAIT_MS)
            self.validate_search_request(control.value.url,query,1,size,sort,'')
            if facet_event.value.status!=200:raise ServiceError('provider_error','MathSciNet facet candidates failed',http_status=facet_event.value.status)
            if parse_qs(urlsplit(facet_event.value.url).query,keep_blank_values=True).get('query')!=[query]:
                raise ServiceError('query_mismatch','MathSciNet facet candidates are not bound to the base query')
            native_catalog=self.facet_payload_candidates(facet_event.value.json())
            base_total=self.validated_search_page(control.value.json(),1,size)[0]
            if base_total==0:
                zero_filter_state={'status':'not_applicable','reason':'The base MathSciNet query has no current facet candidates; requested filters were not applied'}
            else:
                effective_query,filter_evidence,facet_artifacts,facet_preview=self.apply_facets(page,query,size,sort,settings['facet_filters'],settings['facet_preview'],base_total,native_catalog)
        records, evidence, citations, citation_artifacts, export_errors = [], list(filter_evidence), [], [], []
        total = None;seen_mrs=set()
        from playwright.sync_api import TimeoutError as BrowserTimeout
        for page_number in range(first_page, last_page + 1):
            query_url = "https://" + host + "/mathscinet/publications-search?" + urlencode({"query": effective_query, "page": page_number, "size": size, "sort": sort, "facets": ""})
            def matching(response):
                url = urlsplit(response.url)
                if url.hostname!=host or url.path!="/mathscinet/api/publications/search":return False
                try:self.validate_search_request(response.url,effective_query,page_number,size,sort,'');return True
                except ServiceError:return False
            try:
                with page.expect_response(matching, timeout=SOURCE_WAIT_MS) as captured:
                    goto_source(page, query_url, MSC_HOSTS, wait_until="domcontentloaded", timeout=SOURCE_WAIT_MS)
                response = captured.value
                if response.status != 200:
                    raise ServiceError("provider_error", "MathSciNet search request failed", http_status=response.status)
                payload = response.json()
                total,rows,page_mrs=self.validated_search_page(payload,page_number,size,total)
                if seen_mrs.intersection(page_mrs):
                    raise ServiceError('invalid_response','MathSciNet search pages repeated an MR identity',page=page_number)
                seen_mrs.update(page_mrs)
                raw = self.store.put(encoded(payload), "application/json", self.source, response.url, role="provider_response", query=query,native_query=effective_query,
                                     page=page_number, page_size=size, sort=sort)
                evidence.append(raw)
                offset = (page_number - 1) * size
                selected_indexes = [i for i in range(len(rows)) if start <= offset + i < start + limit]
                # Save the entire received response; the requested window is a separate artifact.
                records.extend(rows[i] for i in selected_indexes)
                if export in self.EXPORTS and selected_indexes:
                    try:
                        selected=[str(rows[i]['mrnumber']) for i in selected_indexes]
                        native=self.citation_exports(selected,[export])[0]['artifact']
                        citations.append(self.store.read(native['ref'])[1].decode('utf-8'))
                        citation_artifacts.append(native)
                    except ServiceError as error:
                        export_errors.append({'page':page_number,**error.result})
                if offset + len(rows) >= total:
                    break
            except BrowserTimeout:
                raise ServiceError("source_timeout", "MathSciNet did not finish the requested search/export", source=self.source, evidence=evidence, retryable=True) from None
        artifact = self.store.put(encoded(records), "application/json", self.source, query_url, role="records", query=query, start=start, requested=limit, total=total)
        exported = artifact
        if citations:
            media = {"bibtex": "application/x-bibtex", "endnote": "application/x-endnote-refer", "amsref": "text/plain", "tex": "application/x-tex"}[export]
            exported = citation_artifacts[0] if len(citations)==1 else self.store.put("\n\n".join(citations), media, self.source, query_url, preserve_bytes=True,
                role="citation_export", format=export, count=sum(a['count'] for a in citation_artifacts),parent_refs=[a['ref'] for a in citation_artifacts])
        if export_errors:
            exported={'status':'partial','artifacts':citation_artifacts,'errors':export_errors,**({'artifact':exported} if citations else {})}
        has_more = start + len(records) < total
        return {"status": "partial" if export_errors else "ok" if records else "not_found", "source": self.source, "query": query, "options": options,
            "start": start, "requested": limit, "received": len(records), "total": total, "has_more": has_more,
            "next": {"start": start + len(records)} if has_more else None, "records": artifact, "export": exported,
            "evidence": evidence,"sort":sort_name,"native_query":effective_query,"facet_groups":list(self.facet_groups),"facet_candidates":facet_preview,
            "filter_evidence":filter_evidence,"applied_facet_candidates":facet_artifacts,
            **({'filter_state':zero_filter_state} if zero_filter_state else {}),
            "preview": [{"id": "MR" + str(row["mrnumber"]), "titles": row["titles"]} for row in records[:3]],
            "scope": "KUDOS → academic DB → MathSciNet proxy; selected source only"}

    def fetch(self, target, *, parts):
        if set(parts)-{'metadata','abstract','fulltext','supplementary','export'}:
            raise ServiceError('invalid_parts','Unknown requested content')
        is_doi=bool(re.match(r'^(?:10\.\d{4,9}/|doi:|https?://(?:dx\.)?doi\.org/)',target,re.I))
        is_name=not re.fullmatch(r'(?:MR)?[0-9]+',target,re.I) and not target.startswith(('http://','https://'))
        if is_doi or is_name:
            if not target.strip():raise ServiceError('invalid_target','Supply an MR number, DOI, document URL or title')
            from api_adapters import doi
            identifier=doi(target) if is_doi else None
            query=('doi:' if is_doi else 'ti:')+'('+json.dumps(identifier or target,ensure_ascii=False)+')'
            found=self.search(query,options={},limit=20,export='bibtex' if is_doi else None)
            if is_doi and found['status']=='ok' and found.get('total')==found.get('received')==1:
                rows=json.loads(self.store.read(found['records']['ref'])[1])
                citations=bibliography(self.store.read(found['export']['ref'])[1],'application/x-bibtex')
                if len(citations)==1 and citations[0].get('doi','').casefold()==identifier.casefold():
                    result=self.fetch('MR'+str(rows[0]['mrnumber']),parts=parts)
                    return {**result,'requested_target':target,'lookup':{'query':query,'records':found['records'],'export':found['export']}}
            return {**found,'requested_target':target,'status':'selection_required' if found.get('received') else found['status'],
                'message':'Select an MR record from the preserved candidates; DOI input is followed only when the native citation confirms it'}
        mr = mathscinet_target(target)
        page = self.page()
        host = urlsplit(page.url).hostname
        url = "https://" + host + "/mathscinet/article?mr=" + mr
        goto_source(page, url, MSC_HOSTS, wait_until="domcontentloaded", timeout=SOURCE_WAIT_MS)
        page.locator("main h1").filter(has_text="MR" + mr).wait_for(timeout=SOURCE_WAIT_MS)
        raw = page.locator("main").inner_html()
        html = clean_html(raw, self.store.sanitizer)
        html_artifact = self.store.put(html, "text/html", self.source, url, role="source_page", mr="MR" + mr)
        text = BeautifulSoup(html, "html.parser").get_text("\n", strip=True)
        text_artifact = self.store.put(text, "text/plain", self.source, url, role="source_page_text", parent_ref=html_artifact["ref"])
        components = {}
        for part in parts:
            if part in ("metadata", "export"):
                components[part] = {"status": "available", "artifact": html_artifact}
            elif part == "abstract":
                components[part] = {"status": "source_page", "artifact": html_artifact, "reason": "Review, source-selected summary and author abstract remain labeled in the preserved page; no semantic relabeling"}
            elif part == "fulltext":
                components[part] = {"status": "not_offered", "reason": "MathSciNet Review PDF is a review, not the cited work's full text. Article links belong to their named providers."}
            elif part == "supplementary":
                link = page.get_by_role("link", name="Review PDF")
                if link.count():
                    observed = urljoin(url, link.first.get_attribute("href"))
                    if urlsplit(observed).hostname != host:
                        raise ServiceError("source_boundary", "Review PDF link left MathSciNet")
                    response = self.gateway.context.request.get(observed, timeout=SOURCE_WAIT_MS)
                    data = response.body()
                    if response.status != 200 or not data.startswith(b"%PDF-"):
                        components[part] = {"status": "error", "code": "invalid_review_pdf"}
                    else:
                        import pymupdf
                        with pymupdf.open(stream=data, filetype="pdf") as document:
                            pages = len(document)
                        artifact = self.store.put(data, "application/pdf", self.source, observed, role="review_pdf", mr="MR" + mr, pages=pages)
                        components[part] = {"status": "available", "artifact": artifact}
                else:
                    components[part] = {"status": "not_found", "reason": "No Review PDF link on this record"}
            else:
                raise ServiceError("invalid_parts", "Unknown requested content", part=part)
        if 'export' in parts:
            try:
                exports=self.citation_exports([mr],list(self.EXPORTS))
                components['export']={'status':'available','artifact':exports[0]['artifact'],'artifacts':exports}
            except ServiceError as error:components['export']=error.result
        return {"status": "ok" if all(v["status"] == "available" for v in components.values()) else "partial", "source": self.source,
            "target": "MR" + mr, "components": components, "records": text_artifact, "source_page": html_artifact,
            "links": [{"label": a.get_text(" ", strip=True), "url": self.store.sanitizer.url(urljoin(url, a["href"]))} for a in BeautifulSoup(html, "html.parser").select("a[href]")],
            "scope": "Only this MathSciNet record was retrieved"}


WOS_ERROR_PREFIX = '/wos/error/'


def wos_error_message(url):
    """WoS가 자기 오류 화면을 띄웠으면 그 사유를 돌려주고, 아니면 None을 돌려준다.

    오류 화면에는 검색 제어가 없다. 그 상태로 제어를 기다리면 나타나지 않을 것을 한도까지 기다리게 된다.
    """
    parts = urlsplit(url)
    if not parts.path.startswith(WOS_ERROR_PREFIX):
        return None
    return parse_qs(parts.query).get('message', ['unknown'])[0]


def wos_search_failure(response, query):
    """검색 요청이 200이 아닐 때 막은 주체를 가려 보고할 오류를 만든다.

    실측: 기관 프록시는 불리언 연산자와 필드=(…)가 결합한 검색식을 SQL 주입으로 보고 자기 HTML 400을 돌려준다.
    그 요청은 WoS에 닿지 않았으므로 다시 시도해도 같다. 호출자가 검색식 모양을 바꿔야 한다.
    """
    if "html" in (response.headers.get("content-type") or "").lower():
        return ServiceError("query_rejected",
                            "The institutional proxy blocked this query text before Web of Science saw it; "
                            "use one field tag per query and narrow with facet_filters",
                            http_status=response.status, query=query, rejected_by="institutional_proxy", stage="search")
    return ServiceError("provider_error", "WOS browser search failed", http_status=response.status, stage="search")


class WebOfScience:
    source = "wos"
    hosts = {"www-webofscience-com.libproxy.knu.ac.kr", "www.webofscience.com"}
    formats = {"plain": ("Plain text file", "application/x-wos"),
        "ris": ("RIS (other reference software)", "application/x-research-info-systems"),
        "bibtex": ("BibTeX", "application/x-bibtex"), "excel": ("Excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        "tsv": ("Tab delimited file", "text/tab-separated-values"), "html": ("Printable HTML file", "text/html")}
    sorts={'relevance':('Relevance','relevance'),'date-newest':('Date: newest first','date-descending'),
           'date-oldest':('Date: oldest first','date-ascending'),'citations-highest':('Citations: highest first','times-cited-descending'),
           'citations-lowest':('Citations: lowest first','times-cited-ascending'),'recently-added':('Recently added','recently-added'),
           'usage-all-time':('Usage (all time): most first',None),'usage-180-days':('Usage (last 180 days): most first',None),
           'conference-title-asc':('Conference title: A to Z',None),'conference-title-desc':('Conference title: Z to A',None),
           'first-author-asc':('First author name: A to Z',None),'first-author-desc':('First author name: Z to A',None),
           'publication-title-asc':('Publication title: A to Z',None),'publication-title-desc':('Publication title: Z to A',None),
           'document-title-asc':('Document title: A to Z',None),'document-title-desc':('Document title: Z to A',None),
           'background-highest':('Background: Highest first',None),'basis-highest':('Basis: Highest first',None),
           'support-highest':('Support: Highest first',None),'differ-highest':('Differ: Highest first',None),
           'discuss-highest':('Discuss: Highest first',None)}
    citation_class_sorts={'background-highest','basis-highest','support-highest','differ-highest','discuss-highest'}
    edition_values={'SCI-EXPANDED':'WOS.SCI','SSCI':'WOS.SSCI','AHCI':'WOS.AHCI','CPCI-S':'WOS.ISTP','CPCI-SSH':'WOS.ISSHP','ESCI':'WOS.ESCI'}

    def __init__(self, store, gateway):
        self.store, self.gateway = store, gateway

    def cookies(self, page):
        dismiss_cookies(page)

    def advanced_options(self,options):
        if set(options)-{'sort','editions','facets','facet_filters','facet_group','facet_query'}:
            raise ServiceError('invalid_options','Use documented WOS sort, editions and result facet fields')
        sort=options.get('sort','relevance')
        if sort not in self.sorts:raise ServiceError('invalid_options','Use a current WOS result sort listed by describe_source')
        requested=options.get('editions')
        if requested is not None and (not isinstance(requested,list) or not requested or any(not isinstance(value,str) or value not in self.edition_values for value in requested) or len(set(requested))!=len(requested)):
            raise ServiceError('invalid_options','editions must be a non-empty distinct list of current WOS edition names')
        editions=None if requested is None else [(label,native) for label,native in self.edition_values.items() if label in requested]
        raw_facets=options.get('facets',[])
        if not isinstance(raw_facets,list) or any(not isinstance(value,str) or not re.fullmatch(r'[A-Z0-9]+\..+',value) for value in raw_facets) or len(set(raw_facets))!=len(raw_facets):
            raise ServiceError('invalid_options','facets must be distinct values copied from the current WOS facet candidates')
        facets=[(value.split('.',1)[0],value.split('.',1)[1],value) for value in raw_facets]
        raw_filters=options.get('facet_filters',{})
        if not isinstance(raw_filters,dict):raise ServiceError('invalid_options','facet_filters must map current WOS field names to exact label arrays')
        filters=[]
        for field,values in raw_filters.items():
            if field not in WOS_FACET_GROUPS or not isinstance(values,list) or not values or any(not isinstance(value,str) or not value or value!=value.strip() for value in values) or len(set(values))!=len(values):
                raise ServiceError('invalid_options','Each WOS facet field needs distinct nonempty exact labels')
            group,heading=WOS_FACET_GROUPS[field];filters.append((field,group,heading,values))
        if {index for index,_,_ in facets}&{group for _,group,_,_ in filters}:
            raise ServiceError('invalid_options','Do not request one WOS facet through both native-value and friendly-label inputs')
        preview=options.get('facet_group');query=options.get('facet_query')
        if preview is not None and preview not in WOS_FACET_GROUPS:raise ServiceError('invalid_options','facet_group must be a current WOS result field')
        if query is not None and (preview is None or not isinstance(query,str) or not query.strip() or query!=query.strip()):
            raise ServiceError('invalid_options','facet_query needs facet_group and a nonempty exact search string')
        facet_preview=(preview,*WOS_FACET_GROUPS[preview],query) if preview else None
        return {'sort':self.sorts[sort],'sort_name':sort,'editions':editions,'facets':facets,
                'facet_filters':filters,'facet_preview':facet_preview}

    def validate_advanced_request(self,request,editions,sort):
        search=request.get('search',{});retrieve=request.get('retrieve',{})
        actual=search.get('editions')
        if actual!=editions and not (actual is None and editions==list(self.edition_values.values())):
            raise ServiceError('query_mismatch','WOS search did not retain the requested editions')
        actual_sort=retrieve.get('sort')
        if (sort is not None and actual_sort!=sort) or (sort is None and (not isinstance(actual_sort,str) or not actual_sort)):
            raise ServiceError('query_mismatch','WOS search did not retain the requested sort')
        return actual_sort

    def result_qid(self,url):
        match=re.search(r'/wos/woscc/summary/([A-Za-z0-9-]+)/',urlsplit(url).path)
        failure=wos_error_message(url)
        if failure:
            raise ServiceError('provider_error','Web of Science replaced the result page with its own error screen',
                               stage='result_page',provider_message=failure,retryable=True)
        if not match:raise ServiceError('query_mismatch','WOS result page has no current query identity')
        return match[1]

    def final_facets(self,result):
        return wos_facet_candidates(result['events'])

    def validate_refine_request(self,request,facets,sort,qid):
        grouped=[]
        for index,value,_ in facets:
            current=next((item for item in grouped if item['index']==index),None)
            if current is None:current={'index':index,'value':[]};grouped.append(current)
            current['value'].append(value)
        if request.get('qid')!=qid or request.get('refines')!=grouped or request.get('retrieve',{}).get('sort')!=sort:
            raise ServiceError('query_mismatch','WOS refine request did not retain the requested facets and sort')

    def requested_export(self,page,start,end,format,records,full_export):
        if format in (None,'json'):return records,None
        if format=='plain':return full_export,None
        try:return self.export_records(page,start,end,format),None
        except ServiceError as error:return error.result,error.result
        except Exception as error:
            failure={'status':'error','code':'export_failed',**failure_details(error)}
            return failure,failure

    def select_editions(self,page,requested):
        combo=page.get_by_role('combobox',name=re.compile(r'^selectEdition,',re.I));combo.wait_for(state='visible',timeout=SOURCE_WAIT_MS);page.wait_for_timeout(1200);combo.click(force=True);page.wait_for_timeout(400)
        choices=page.get_by_role('option').filter(visible=True);choices.first.wait_for(state='visible',timeout=SOURCE_WAIT_MS);available=[]
        for index in range(choices.count()):
            text=' '.join(choices.nth(index).inner_text().split())
            match=next(((label,native) for label,native in self.edition_values.items() if '('+label+')' in text),None)
            if match:available.append((*match,index))
        desired={label for label,_,_ in available} if requested is None else {label for label,_ in requested}
        if desired-{label for label,_,_ in available}:
            page.keyboard.press('Escape')
            raise ServiceError('selection_required','Select editions available in the current institutional WOS session',status='selection_required',
                               candidates=[{'label':label,'value':native} for label,native,_ in available])
        if requested is None and any(choices.nth(index).get_attribute('aria-selected')!='true' for _,_,index in available):
            page.get_by_role('option',name='Select All',exact=True).click(force=True);page.wait_for_timeout(200)
        else:
            for label,_,index in available:
                option=choices.nth(index)
                if (option.get_attribute('aria-selected')=='true')!=(label in desired):
                    option.click(force=True);page.wait_for_timeout(100)
        actual={label for label,_,index in available if choices.nth(index).get_attribute('aria-selected')=='true'}
        if actual!=desired:
            page.keyboard.press('Escape')
            raise ServiceError('query_mismatch','WOS edition controls did not retain the requested selection')
        page.keyboard.press('Escape')
        return [(label,native) for label,native,_ in available if label in desired]

    def apply_facets(self,page,result,requested,sort):
        candidates=wos_facet_candidates(result['events'])
        if not requested:return result,candidates,None
        indexed={item['value']:item for item in candidates}
        if any(value not in indexed for _,_,value in requested):
            raise ServiceError('selection_required','Copy facet values from the current WOS result candidates',status='selection_required',candidates=candidates)
        groups=[]
        for item in requested:
            group=next((values for index,values in groups if index==item[0]),None)
            if group is None:group=[];groups.append((item[0],group))
            group.append(item)
        applied=[];evidence=[];current=result
        for index,group in groups:
            qid=self.result_qid(page.url)
            current_candidates={item['value']:item for item in wos_facet_candidates(current['events'])}
            if any(value not in current_candidates for _,_,value in group):
                raise ServiceError('selection_required','A requested WOS facet is not available after the preceding refinements',status='selection_required',candidates=list(current_candidates.values()))
            values=[current_candidates[value] for _,_,value in group]
            section=page.locator('[data-ta="filter-section-'+values[0]['control_section']+'"]')
            if section.count()!=1:
                raise ServiceError('selection_required','The current WOS result has no unique control section for this facet',status='selection_required',candidate=values[0])
            heading=section.locator('button.filter-heading').first
            if heading.count() and heading.get_attribute('aria-expanded')=='false':heading.click();page.wait_for_timeout(200)
            scope=section
            def matching_boxes(candidate):
                matches=[];boxes=section.locator('mat-checkbox input[type="checkbox"]')
                if scope is not section:boxes=scope.locator('mat-checkbox input[type="checkbox"]')
                for i in range(boxes.count()):
                    box=boxes.nth(i);aria=box.get_attribute('aria-label') or '';match=re.fullmatch(r'(.+?),\s*(\d{1,3}(?:,\d{3})+|\d+)',aria)
                    if match and box.is_visible() and match[1].casefold()==candidate['label'].casefold() and int(match[2].replace(',',''))==candidate['count']:matches.append(box)
                return matches
            if any(not matching_boxes(candidate) for candidate in values):
                more=section.get_by_role('button',name=re.compile(r'^(?:See all|Show more)',re.I)).filter(visible=True)
                if more.count():
                    more.first.click();page.wait_for_timeout(400)
                    expanded=page.locator('app-refine-see-all-shared').filter(visible=True)
                    if expanded.count():scope=expanded.first
            selected=[]
            for candidate in values:
                matches=matching_boxes(candidate)
                if not matches:
                    search=scope.locator('input[type="search"],input[placeholder*="Search" i]').filter(visible=True)
                    if search.count():search.first.fill(candidate['label']);page.wait_for_timeout(500);matches=matching_boxes(candidate)
                if len(matches)!=1:
                    raise ServiceError('selection_required','A current WOS facet could not be matched inside its native control section',status='selection_required',candidate=candidate)
                box=matches[0]
                if not box.is_checked():box.locator('xpath=ancestor::mat-checkbox[1]').locator('label').click()
                selected.append(box)
            refine=scope.get_by_role('button',name='Refine',exact=True).filter(visible=True).first if scope is not section else selected[0].locator('xpath=ancestor::div[contains(@class,"width-wrapper")][1]').get_by_role('button',name='Refine',exact=True)
            with page.expect_response(lambda response:urlsplit(response.url).hostname in self.hosts and urlsplit(response.url).path=='/api/wosnx/core/runQueryRefine',timeout=SOURCE_WAIT_MS) as event:
                refine.click()
            response=event.value
            if response.status!=200:raise ServiceError('provider_error','WOS result refinement failed',http_status=response.status)
            applied.extend(group);request=response.request.post_data_json;self.validate_refine_request(request,group,sort,qid)
            current=wos_events(response.text())
            evidence.append(self.store.put(encoded(current['events']),'application/json',self.source,response.url,role='refine_response',
                                           facets=[value for _,_,value in applied],sort=sort))
        return current,wos_facet_candidates(current['events']),evidence[0] if len(evidence)==1 else evidence

    def load_facet_group(self,page,field,group,heading,query=None,current_qid=None,current_total=None):
        current_qid=current_qid or self.result_qid(page.url)
        before_selection=page.locator('#snRefine input[type="checkbox"]:checked').evaluate_all("nodes=>nodes.map(n=>(n.name||'')+'\u0000'+(n.value||'')).sort()")
        section=page.locator('[data-ta="filter-section-'+group+'"]')
        if section.count()!=1:raise ServiceError('facet_not_offered','The current WOS result has no '+heading+' facet',status='not_offered',field=field)
        control=section.locator('button.filter-heading')
        evidence=None;observed_analysis=None
        if control.get_attribute('aria-expanded')!='true':
            def matching(response):
                if urlsplit(response.url).hostname not in self.hosts or urlsplit(response.url).path!='/api/wosnx/core/runQueryGetRecordsStream':return False
                try:
                    analyzes=response.request.post_data_json.get('retrieve',{}).get('analyzes')
                    return isinstance(analyzes,list) and len(analyzes)==1 and analyzes[0].startswith(group+'.')
                except Exception:return False
            with page.expect_response(matching,timeout=SOURCE_WAIT_MS) as event:control.click()
            response=event.value
            if response.status!=200:raise ServiceError('provider_error','WOS facet candidate request failed',http_status=response.status,field=field)
            if response.request.post_data_json.get('qid')!=current_qid:
                raise ServiceError('query_mismatch','WOS facet candidate request is not bound to the current result',field=field)
            native=wos_events(response.text());analyze=next((event.get('payload') for event in native['events'] if event.get('key')=='analyze'),{})
            if current_total is not None and native['total']!=current_total:
                raise ServiceError('result_set_mismatch','WOS facet candidate lookup changed the current result total')
            if not any(isinstance(value,dict) and value.get('Name')==group for value in analyze.values()):
                raise ServiceError('query_mismatch','WOS facet candidate response identifies another field',field=field)
            observed_analysis=(native['events'],response.url,native['total'])
        page.wait_for_timeout(200);scope=section;expanded=False
        if query is not None:
            more=section.get_by_role('button',name=re.compile(r'^(?:See all|Show more)',re.I)).filter(visible=True)
            if more.count():
                more.first.click();page.wait_for_timeout(400)
                overlay=page.locator('app-refine-see-all-shared').filter(visible=True)
                if overlay.count():scope=overlay.first;expanded=True
            search=scope.locator('input[type="search"],input[placeholder*="Search" i]').filter(visible=True)
            if search.count():search.first.fill(query);page.wait_for_timeout(600)
        after_selection=page.locator('#snRefine input[type="checkbox"]:checked').evaluate_all("nodes=>nodes.map(n=>(n.name||'')+'\u0000'+(n.value||'')).sort()")
        if self.result_qid(page.url)!=current_qid or after_selection!=before_selection:
            raise ServiceError('result_set_mismatch','WOS facet candidate lookup changed the current result or active filters')
        if observed_analysis:
            events,url,total=observed_analysis
            evidence=self.store.put(encoded(events),'application/json',self.source,url,role='facet_analysis',field=field,native_group=group,
                                    qid_matched=True,result_total=total,selection_unchanged=True)
        return wos_control_candidates(scope.inner_html(),field,group),scope,evidence,expanded

    def apply_named_facets(self,page,result,filters,sort):
        if not filters:return result,[],[]
        current=result;evidence=[];artifacts=[]
        for field,group,heading,labels in filters:
            qid=self.result_qid(page.url)
            candidates,scope,analysis,expanded=self.load_facet_group(page,field,group,heading,current_qid=qid,current_total=current['total'])
            if analysis:evidence.append(analysis)
            if any(sum(item['label'].casefold()==label.casefold() for item in candidates)!=1 for label in labels):
                candidates,scope,extra,expanded=self.load_facet_group(page,field,group,heading,labels[0],current_qid=qid,current_total=current['total'])
                if extra:evidence.append(extra)
            selected=[]
            for label in labels:
                if expanded:
                    search=scope.locator('input[type="search"],input[placeholder*="Search" i]').filter(visible=True)
                    if search.count():search.first.fill(label);page.wait_for_timeout(500);candidates=wos_control_candidates(scope.inner_html(),field,group)
                matches=[item for item in candidates if item['label'].casefold()==label.casefold()]
                if len(matches)!=1:
                    raise ServiceError('selection_required','Select one exact label from the current WOS facet field',status='selection_required',
                                       field=field,candidates=candidates)
                candidate=matches[0];boxes=scope.locator('input[type="checkbox"]');controls=[]
                for index in range(boxes.count()):
                    box=boxes.nth(index)
                    if box.is_visible() and box.get_attribute('name')==group and box.get_attribute('value')==candidate['native_value']:controls.append(box)
                if len(controls)!=1:raise ServiceError('selection_required','The selected WOS facet label has no unique native control',status='selection_required',field=field,candidate=candidate)
                box=controls[0]
                if not box.is_checked():box.locator('xpath=ancestor::mat-checkbox[1]').locator('label').click()
                selected.append(candidate)
            artifact=self.store.put(encoded(selected),'application/json',self.source,page.url,role='facet_candidates',field=field,
                                    native_group=group,query=labels,scope='Exact visible labels resolved in one current WOS facet field')
            artifacts.append(artifact)
            refine=scope.get_by_role('button',name='Refine',exact=True).filter(visible=True).first if expanded else controls[0].locator('xpath=ancestor::div[contains(@class,"width-wrapper")][1]').get_by_role('button',name='Refine',exact=True)
            with page.expect_response(lambda response:urlsplit(response.url).hostname in self.hosts and urlsplit(response.url).path=='/api/wosnx/core/runQueryRefine',timeout=SOURCE_WAIT_MS) as event:
                refine.click()
            response=event.value
            if response.status!=200:raise ServiceError('provider_error','WOS result refinement failed',http_status=response.status,field=field)
            requested=[(group,item['native_value'][len(group)+1:],item['native_value']) for item in selected]
            self.validate_refine_request(response.request.post_data_json,requested,sort,qid)
            current=wos_events(response.text());evidence.append(self.store.put(encoded(current['events']),'application/json',self.source,response.url,
                role='refine_response',field=field,labels=labels,native_values=[item['native_value'] for item in selected],sort=sort))
        return current,evidence,artifacts

    def preview_facet_group(self,page,preview,result):
        if preview is None:return None,None
        field,group,heading,query=preview;qid=self.result_qid(page.url)
        candidates,scope,evidence,expanded=self.load_facet_group(page,field,group,heading,query,current_qid=qid,current_total=result['total'])
        artifact=self.store.put(encoded(candidates),'application/json',self.source,page.url,role='facet_candidates',field=field,
                                native_group=group,query=query,scope='Current visible candidates; use facet_query to search the native expanded list')
        if expanded:
            cancel=scope.get_by_role('button',name='Cancel',exact=True).filter(visible=True)
            if cancel.count():cancel.first.click()
        return artifact,evidence

    def apply_sort(self,page,result,sort):
        label,expected_native=sort;control=page.locator('#selectSortOption').filter(visible=True).first;control.wait_for(timeout=SOURCE_WAIT_MS)
        evidence=None
        if control.get_attribute('aria-label')!='Sort by '+label:
            control.click()
            choice=page.get_by_role('menuitem',name=label,exact=True).filter(visible=True)
            if not choice.count():
                citation_class=page.get_by_role('menuitem',name='Citation class',exact=True).filter(visible=True)
                if citation_class.count():citation_class.first.click();choice=page.get_by_role('menuitem',name=label,exact=True).filter(visible=True)
            if choice.count()!=1:raise ServiceError('sort_not_offered','The current WOS result does not offer the requested sort',status='unsupported')
            with page.expect_response(lambda response:urlsplit(response.url).hostname in self.hosts and urlsplit(response.url).path=='/api/wosnx/core/runQueryGetRecordsStream',timeout=SOURCE_WAIT_MS) as event:
                choice.first.click()
            response=event.value
            if response.status!=200:raise ServiceError('provider_error','WOS result sorting failed',http_status=response.status)
            request=response.request.post_data_json;native=request.get('retrieve',{}).get('sort')
            if not isinstance(native,str) or not native or expected_native is not None and native!=expected_native:
                raise ServiceError('query_mismatch','WOS did not retain the requested sort')
            sorted_result=wos_events(response.text())
            if sorted_result['total']!=result['total']:raise ServiceError('result_set_mismatch','WOS sorting changed the result set size')
            result=sorted_result
            evidence=self.store.put(encoded(result['events']),'application/json',self.source,response.url,role='sort_response',sort=native,total=result['total'])
        else:
            native=urlsplit(page.url).path.rstrip('/').split('/')[-2]
            if expected_native is not None and native!=expected_native:raise ServiceError('query_mismatch','WOS result route did not retain the requested sort')
        if control.get_attribute('aria-label')!='Sort by '+label or '/'+native+'/' not in urlsplit(page.url).path:
            raise ServiceError('query_mismatch','WOS result page did not retain the requested sort')
        return result,evidence,native

    def citing_target(self, target):
        from api_adapters import doi
        if target.startswith(('http://', 'https://')) and urlsplit(target).hostname not in ('doi.org', 'dx.doi.org'):
            require_source_url(target, self.hosts)
            match=re.search(r'/full-record/(WOS:[0-9A-Z]+)(?:/|$)',unquote(urlsplit(target).path))
            if not match:raise ServiceError('invalid_target','Use a WOS accession number, DOI or full-record URL for citing works')
            target=match[1]
        if re.fullmatch(r'(?:WOS:)?[0-9A-Z]+',target):
            value=target if target.startswith('WOS:') else 'WOS:'+target
            return 'UT=('+value+')',None
        if target.startswith(('10.','doi:','https://doi.org/','https://dx.doi.org/')):
            value=doi(target)
            return 'DO=('+json.dumps(value)+')',value
        raise ServiceError('invalid_target','Use a WOS accession number, DOI or full-record URL for citing works')

    def validate_citing_request(self,request,accession,sort):
        search=request.get('search',{});retrieve=request.get('retrieve',{})
        if search.get('database')!='WOSCC' or search.get('mode')!='citing_article' or search.get('parentId')!={'type':'colluid','value':accession}:
            raise ServiceError('identity_mismatch','WOS citing search is not bound to the selected accession')
        if retrieve.get('sort')!=sort or type(retrieve.get('count')) is not int or retrieve['count']<1:
            raise ServiceError('query_mismatch','WOS citing search did not retain the requested sort or result window')
        return retrieve['count']

    def search_citations(self,target,*,start,limit,export,sort='date-descending'):
        sort_key='date-newest' if sort=='date-descending' else sort
        if sort_key not in self.sorts:raise ServiceError('invalid_options','Use a current WOS citing-result sort')
        sort_setting=self.sorts[sort_key]
        query,expected_doi=self.citing_target(target)
        parent=self.search(query,options={},limit=1,export='plain')
        if parent.get('status')!='ok':return {**parent,'kind':'citations','requested_target':target}
        if parent.get('total')!=parent.get('received') or parent.get('total')!=1:
            return {**parent,'status':'selection_required','kind':'citations','requested_target':target,
                    'message':'Select one WOS accession number before requesting citing works'}
        parent_rows=json.loads(self.store.read(parent['records']['ref'])[1]);parent_row=parent_rows[0]
        accession=parent_row.get('id')
        if not re.fullmatch(r'WOS:[0-9A-Z]+',accession or ''):
            raise ServiceError('identity_mismatch','WOS parent search returned no unique accession')
        if expected_doi and [value.casefold() for value in parent_row.get('fields',{}).get('di',[])]!=[expected_doi.casefold()]:
            raise ServiceError('identity_mismatch','WOS parent search returned another DOI')
        page=self.gateway.pages[self.source];host=urlsplit(page.url).hostname
        record_url='https://'+host+'/wos/woscc/full-record/'+accession
        goto_source(page,record_url,self.hosts,wait_until='domcontentloaded',timeout=SOURCE_WAIT_MS);self.cookies(page)
        link=page.locator('a[href*="/citing-summary/'+accession+'"]:visible').first
        control_total=int(parent_row.get('fields',{}).get('tc',['0'])[0].replace(',',''))
        if control_total:
            try:link.wait_for(state='visible',timeout=SOURCE_WAIT_MS)
            except Exception:raise ServiceError('citing_control_missing','WOS full record has citations but no citing-results control',source_page=record_url) from None
        if not link.count():
            if control_total==0:
                artifact=self.store.put(b'[]','application/json',self.source,record_url,role='citing_records',target=accession,total=0)
                return {'status':'not_found','source':self.source,'query':target,'options':{'kind':'citations','sort':sort},
                        'kind':'citations','target':accession,'sort':sort,'start':start,'requested':limit,'received':0,'total':0,
                        'has_more':False,'next':None,'records':artifact,'export':artifact,'parent':parent['records'],
                        'scope':'Incoming WOS Core Collection records for the selected accession'}
            raise ServiceError('citing_control_missing','WOS full record has citations but no citing-results control',source_page=record_url)
        href=urlsplit(urljoin(record_url,link.get_attribute('href')))
        if href.path!='/wos/woscc/citing-summary/'+accession:
            raise ServiceError('identity_mismatch','WOS citing control identifies another accession')
        citing_url='https://'+host+href.path
        with page.expect_response(lambda r:urlsplit(r.url).hostname in self.hosts and urlsplit(r.url).path=='/api/wosnx/core/runQuerySearch',timeout=SOURCE_WAIT_MS) as event:
            goto_source(page,citing_url,self.hosts,wait_until='domcontentloaded',timeout=SOURCE_WAIT_MS)
        response=event.value
        if response.status!=200:raise ServiceError('provider_error','WOS citing search failed',http_status=response.status)
        request=response.request.post_data_json;page_size=self.validate_citing_request(request,accession,'date-descending')
        native=wos_events(response.text());total=native['total']
        initial_evidence=self.store.put(encoded(native['events']),'application/json',self.source,response.url,role='citing_search_response',
                                target=accession,direction='incoming',control_total=control_total,result_total=total,
                                native_page_size=page_size,sort='date-descending')
        sort_evidence=None;native_sort='date-descending'
        if sort_key!='date-newest':
            native,sort_evidence,native_sort=self.apply_sort(page,native,sort_setting)
            if native['total']!=total:raise ServiceError('result_set_mismatch','WOS citing sort changed the result set size')
        if start>=total:
            artifact=self.store.put(b'[]','application/json',self.source,page.url,role='citing_records',target=accession,start=start,total=total)
            return {'status':'not_found','source':self.source,'query':target,'options':{'kind':'citations','sort':sort},
                    'kind':'citations','target':accession,'sort':sort,'start':start,'requested':limit,'received':0,'total':total,
                    'has_more':False,'next':None,'records':artifact,'export':artifact,'evidence':initial_evidence,'sort_evidence':sort_evidence,'native_sort':native_sort,'parent':parent['records'],
                    'relation':{'direction':'incoming','control_total':control_total,'result_total':total},
                    'scope':'Incoming WOS Core Collection records for the selected accession'}
        page.locator('#export-trigger-btn').wait_for(timeout=SOURCE_WAIT_MS)
        end=min(start+limit,total);full_export=self.export_records(page,start,end,'plain')
        records=bibliography(self.store.read(full_export['ref'])[1],'application/x-wos')
        if len(records)!=end-start:
            raise ServiceError('export_range_mismatch','WOS citing export count differs from the requested record window',expected=end-start,received=len(records),evidence=full_export)
        artifact=self.store.put(encoded(records),'application/json',self.source,page.url,role='citing_records',target=accession,
                                start=start,requested=limit,total=total,export_ref=full_export['ref'])
        exported,export_error=self.requested_export(page,start,end,export,artifact,full_export)
        return {'status':'partial' if export_error else 'ok','source':self.source,'query':target,'options':{'kind':'citations','sort':sort},'kind':'citations',
                'target':accession,'sort':sort,'start':start,'requested':limit,'received':len(records),'total':total,'records':artifact,
                'export':exported,'full_record_export':full_export,'evidence':initial_evidence,'sort_evidence':sort_evidence,'native_sort':native_sort,'parent':parent['records'],
                'relation':{'direction':'incoming','control_total':control_total,'result_total':total},'export_error':export_error,
                'has_more':end<total,'next':{'start':end} if end<total else None,
                'preview':[{'id':row['id'],'title':' '.join(row['fields'].get('ti',[]))} for row in records[:3]],
                'scope':'Incoming WOS Core Collection records for the selected accession'}

    def export_records(self, page, start, end, format):
        """결과 화면의 원 내보내기를 받는다. WoS가 일시 오류로 자기 오류 화면에 가면 결과 화면으로 돌아와 다시 시도한다."""
        origin = page.url
        def attempt():
            try:
                if wos_error_message(page.url):
                    page.goto(origin, wait_until="domcontentloaded", timeout=SOURCE_WAIT_MS)
                    self.dialog_control(page, "#export-trigger-btn")
                return self.export_once(page, start, end, format)
            except ServiceError:
                raise
            except Exception:
                failure = wos_error_message(page.url)
                if failure is None:
                    raise
                raise ServiceError('provider_error', 'Web of Science replaced the export dialog with its own error screen',
                                   stage='export', provider_message=failure, retryable=True) from None
        return retry_transient(attempt)

    def dialog_control(self, page, selector):
        """대화상자의 제어를 기다리되, WoS가 그 사이 자기 오류 화면으로 가면 대기를 소진하지 않고 곧바로 알린다."""
        page.wait_for_function("(selector) => location.pathname.startsWith('" + WOS_ERROR_PREFIX + "')"
                               " || document.querySelector(selector) !== null", arg=selector, timeout=SOURCE_WAIT_MS)
        failure = wos_error_message(page.url)
        if failure:
            raise ServiceError('provider_error', 'Web of Science replaced the export dialog with its own error screen',
                               stage='export', provider_message=failure, retryable=True)
        return page.locator(selector)

    def export_once(self, page, start, end, format):
        label, media = self.formats[format]
        page.locator("#export-trigger-btn").click()
        page.get_by_role("menuitem", name=label, exact=True).click()
        self.dialog_control(page, 'input[name="markFrom"]')
        page.locator("#radio3-input").focus()
        page.locator("#radio3-input").press("Space")
        self.dialog_control(page, 'input[name="markFrom"]').fill(str(start + 1))
        page.locator('input[name="markTo"]').fill(str(end))
        page.get_by_text("Record Content:", exact=True).locator("..").get_by_role("combobox").click()
        content = "Full Record and Cited References" if format == "plain" else "Full Record"
        page.get_by_role("option", name=content, exact=True).click()
        with page.expect_download(timeout=SOURCE_WAIT_MS) as event:
            page.locator("#exportButton").click()
        download = event.value
        if download.failure():
            raise ServiceError("export_failed", "WOS native export download failed")
        data = Path(download.path()).read_bytes()
        if not data:
            raise ServiceError("empty_export", "WOS native export was empty")
        if format=='excel':
            if data.startswith(bytes.fromhex('d0cf11e0a1b11ae1')):
                media='application/vnd.ms-excel'
            elif data.startswith(b'PK'):
                media='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:
                source_export=self.store.put(data,'application/octet-stream',self.source,page.url,preserve_bytes=True,role='source_export',
                                             format=format,start=start,end=end,original_name=download.suggested_filename)
                raise ServiceError('invalid_export','WOS returned no recognized Excel workbook',source_export=source_export)
        return self.store.put(data, media, self.source, page.url, role="citation_export", format=format,
            record_content=content, start=start, end=end, original_name=download.suggested_filename)

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        """검색 한 번을 실행한다. WoS의 일시 오류는 facet·정렬 단계에서도 나므로 흐름 전체를 다시 시도할 수 있게 감싼다."""
        return retry_transient(lambda: self.search_once(query, options=options, start=start, limit=limit, cursor=cursor, export=export))

    def search_once(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ServiceError("invalid_range", "WOS requires start >= 0 and limit 1..1000")
        if cursor or set(options)-{'kind','sort','editions','facets','facet_filters','facet_group','facet_query'}:
            raise ServiceError("invalid_options", "Use native WOS field/date constraints in query, documented sort and editions, and current facet values")
        if export not in (None, "json", *self.formats):
            raise ServiceError("invalid_export", "Use json, plain, ris, bibtex, excel, tsv or html")
        kind=options.get('kind','publications');sort=options.get('sort','date-descending' if kind=='citations' else None)
        if kind=='citations':
            if set(options)-{'kind','sort'}:raise ServiceError('invalid_options','Citing works accept kind and a current citing-result sort')
            if sort!='date-descending' and sort not in self.sorts:raise ServiceError('invalid_options','Use a current WOS citing-result sort')
            return self.search_citations(query,start=start,limit=limit,export=export,sort=sort)
        if kind!='publications':raise ServiceError('invalid_options','Use kind publications or citations')
        settings=self.advanced_options({key:value for key,value in options.items() if key!='kind'})
        page = self.gateway.open(self.source, "Web of Science CPCI", self.hosts, '#composeQuerySmartSearch,input[name="search-main-box"]')
        self.cookies(page)
        def submit():
            # 실측: 같은 getHistory·runQuerySearch 요청에 WoS가 간헐적으로 Server.internalError를 낸다.
            # 오류 화면에도 Advanced Search 링크가 있어 같은 자리에서 다시 들어갈 수 있다.
            # 실측: 직전 호출이 facet 패널을 연 채 끝나면 그 dimmed-background가 머리글 링크의 클릭을 가로채 대기를 소진했다.
            # Escape로는 닫히지 않고 패널의 Cancel이 닫는다.
            if page.locator('.dimmed-background').filter(visible=True).count():
                page.get_by_role('button', name='Cancel', exact=True).filter(visible=True).first.click()
                page.locator('.dimmed-background').first.wait_for(state='hidden', timeout=SOURCE_WAIT_MS)
            page.get_by_role("link", name="Advanced Search", exact=True).first.click()
            page.get_by_text("QUERY BUILDER", exact=True).click()
            page.wait_for_function("() => document.querySelector('#advancedSearchInputArea') !== null"
                                   " || location.pathname.startsWith('" + WOS_ERROR_PREFIX + "')", timeout=SOURCE_WAIT_MS)
            failure=wos_error_message(page.url)
            if failure:
                raise ServiceError('provider_error','Web of Science answered the query builder with its own error screen',
                                   stage='query_builder',provider_message=failure,retryable=True)
            editions=self.select_editions(page,settings['editions'])
            page.locator("#advancedSearchInputArea").fill(query)
            with page.expect_response(lambda r: urlsplit(r.url).hostname in self.hosts and urlsplit(r.url).path == "/api/wosnx/core/runQuerySearch", timeout=SOURCE_WAIT_MS) as event:
                page.get_by_role("button", name="Search", exact=True).click()
            answer = event.value
            if answer.status != 200:
                raise wos_search_failure(answer, query)
            return editions, answer, wos_events(answer.text())
        selected_editions, response, result = retry_transient(submit)
        request = response.request.post_data_json
        if request.get("search", {}).get("query") != [{"rowText": query}] or request["search"].get("database") != "WOSCC":
            raise ServiceError("query_mismatch", "WOS did not submit the requested query and collection")
        initial_sort=self.validate_advanced_request(request,[native for _,native in selected_editions],None)
        evidence = self.store.put(encoded(result["events"]), "application/json", self.source, response.url,
            role="provider_response", query=query, collection="WOSCC", editions=[label for label,_ in selected_editions],
            search_options=request["search"].get("options", {}))
        if result['total']==0:
            artifact=self.store.put(b'[]','application/json',self.source,page.url,role='records',query=query,start=start,total=0)
            return {'status':'not_found','source':self.source,'query':query,'options':options,'collection':'WOSCC',
                    'editions':[label for label,_ in selected_editions],'sort':settings['sort_name'],'start':start,'requested':limit,
                    'received':0,'total':0,'records':artifact,'export':artifact,'evidence':evidence,'filter_evidence':None,
                    'sort_evidence':None,'facets':wos_facet_candidates(result['events']),
                    'facet_scope':'Current native analyze candidates matched to current result controls','has_more':False,'next':None,
                    'scope':'Requested WOS result window is empty'}
        page.locator("#export-trigger-btn").wait_for(timeout=SOURCE_WAIT_MS)
        result,facets,filter_evidence=self.apply_facets(page,result,settings['facets'],initial_sort)
        result,named_filter_evidence,applied_facet_candidates=self.apply_named_facets(page,result,settings['facet_filters'],initial_sort)
        facets=self.final_facets(result)
        preview_candidates,preview_evidence=self.preview_facet_group(page,settings['facet_preview'],result)
        result,sort_evidence,native_sort=self.apply_sort(page,result,settings['sort'])
        facet_groups=[{'field':field,'label':label} for field,(_,label) in WOS_FACET_GROUPS.items()]
        candidate_artifacts=[*applied_facet_candidates,*([preview_candidates] if preview_candidates else [])]
        total = result["total"]
        if start >= total:
            artifact = self.store.put(b"[]", "application/json", self.source, page.url, role="records", query=query, start=start)
            return {"status": "not_found", "source": self.source, "query": query,"options":options,"total": total, "received": 0, "records": artifact,
                "export":artifact,"evidence": evidence,"filter_evidence":filter_evidence,"sort_evidence":sort_evidence,
                "facets":facets,"facet_scope":"Current native analyze candidates matched to current result controls",
                "facet_groups":facet_groups,"facet_candidates":candidate_artifacts,"named_filter_evidence":named_filter_evidence,
                "facet_preview_evidence":preview_evidence,"editions":[label for label,_ in selected_editions],"sort":settings['sort_name'],"native_sort":native_sort,"has_more": False, "scope": "Requested WOS result window is empty"}
        end = min(start + limit, total)
        full_export = self.export_records(page, start, end, "plain")
        records = bibliography(self.store.read(full_export["ref"])[1], "application/x-wos")
        if len(records) != end - start:
            raise ServiceError("export_range_mismatch", "WOS export count differs from the requested record window", expected=end - start, received=len(records), evidence=full_export)
        artifact = self.store.put(encoded(records), "application/json", self.source, page.url,
            role="records", query=query, start=start, requested=limit, total=total, export_ref=full_export["ref"])
        exported,export_error=self.requested_export(page,start,end,export,artifact,full_export)
        return {"status": "partial" if export_error else "ok", "source": self.source, "query": query, "options": options, "collection": "WOSCC", "editions": [label for label,_ in selected_editions],"sort":settings['sort_name'],"native_sort":native_sort,
            "start": start, "requested": limit, "received": len(records), "total": total, "records": artifact, "export": exported,
            "full_record_export": full_export, "evidence": evidence,"filter_evidence":filter_evidence,"sort_evidence":sort_evidence,
            "facets":facets,"facet_scope":"Current native analyze candidates matched to current result controls",
            "facet_groups":facet_groups,"facet_candidates":candidate_artifacts,"named_filter_evidence":named_filter_evidence,
            "facet_preview_evidence":preview_evidence,"export_error":export_error,"has_more": end < total, "next": {"start": end} if end < total else None,
            "preview": [{"id": r["id"], "title": " ".join(r["fields"].get("ti", []))} for r in records[:3]],
            "scope": "KUDOS academic DB → Web of Science Core Collection, including licensed CPCI editions"}

    def fetch(self, target, *, parts):
        from api_adapters import doi
        is_title = False;expected_accession=expected_doi=None
        if target.startswith(('http://', 'https://')) and urlsplit(target).hostname not in ('doi.org', 'dx.doi.org'):
            require_source_url(target, self.hosts)
            match = re.search(r'/full-record/(WOS:[0-9A-Z]+)(?:/|$)', unquote(urlsplit(target).path))
            if not match:
                raise ServiceError('invalid_target', 'Use a WOS full-record URL, accession number, DOI or title')
            target = match[1]
        if re.fullmatch(r"(?:WOS:)?[0-9A-Z]+", target):
            value = target if target.startswith("WOS:") else "WOS:" + target
            expected_accession=value
            query = "UT=(" + value + ")"
        elif target.startswith(("10.", "doi:", "https://doi.org/")):
            expected_doi=doi(target);query = 'DO=("' + expected_doi.replace('"', '\\"') + '")'
        else:
            is_title = True
            query = 'TI=("' + target.replace('"', '\\"') + '")'
        result = self.search(query, options={}, limit=20 if is_title else 1, export="plain")
        if result["status"] != "ok":
            return result
        if is_title:
            result.update(status='selection_required', message='Select the accession number or DOI from these title candidates')
            return result
        if result["total"] != 1:
            result["status"] = "selection_required"
            return result
        rows = json.loads(self.store.read(result["records"]["ref"])[1])
        row=rows[0]
        if expected_accession and row.get('id')!=expected_accession:
            raise ServiceError('identity_mismatch','WOS search returned another accession',evidence=result['records'])
        if expected_doi:
            observed=[]
            for value in row.get('fields',{}).get('di',[]):
                try:observed.append(doi(value).casefold())
                except ServiceError:continue
            if expected_doi.casefold() not in observed:
                raise ServiceError('identity_mismatch','WOS search returned another DOI',evidence=result['records'])
        components = {}
        for part in parts:
            if part in ("metadata", "export") or (part == "abstract" and rows[0]["fields"].get("ab")):
                components[part] = {"status": "available", "artifact": result["records"]}
            elif part == 'supplementary':
                incoming=self.search(target,options={'kind':'citations'},limit=20)
                components[part]={'status':'available' if incoming.get('status') in ('ok','not_found') else 'partial',
                                  'artifact':result['records'],
                                  'references':{'status':'available','direction':'outgoing','count':len(rows[0]['fields'].get('cr',[])),
                                                'artifact':result['records']},
                                  'citations':{'direction':'incoming',**incoming}}
            elif part == "abstract":
                components[part] = {"status": "not_found", "reason": "No abstract tag in this full record"}
            elif part == "fulltext":
                components[part] = {"status": "not_offered", "reason": "WOS indexes this work; publisher full text is a separate source"}
            else:
                raise ServiceError("invalid_parts", "Unknown requested content", part=part)
        result["components"] = components
        result["status"] = "ok" if all(v["status"] == "available" for v in components.values()) else "partial"
        return result


class ECCC:
    source = "eccc"
    hosts = {"eccc.weizmann.ac.il"}

    def __init__(self, store, gateway):
        self.store, self.gateway = store, gateway

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        if options or cursor or export not in (None, "json", "html"):
            raise ServiceError("invalid_options", "ECCC uses a literal query, start/limit and json/html export")
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ServiceError("invalid_range", "Use start >= 0 and limit 1..1000")
        page = self.gateway.public_page(self.source)
        goto_source(page, "https://eccc.weizmann.ac.il/", self.hosts, wait_until="domcontentloaded", timeout=SOURCE_WAIT_MS)
        page.locator('input[name="search"]').fill(query)
        with page.expect_navigation(wait_until="domcontentloaded"):
            page.locator('input[name="search"]').press("Enter")
        if parse_qs(urlsplit(page.url).query).get("search") != [query]:
            raise ServiceError("query_mismatch", "ECCC did not navigate to the requested search")
        require_source_url(page.url, self.hosts)
        raw = page.content()
        if "Results for query" not in page.locator("body").inner_text():
            raise ServiceError("invalid_response", "ECCC did not return its result listing")
        records = eccc_records(raw)
        source_page = self.store.put(clean_html(raw, self.store.sanitizer), "text/html", self.source, page.url, role="search_page", query=query)
        all_records = self.store.put(encoded(records), "application/json", self.source, page.url, role="all_received_records", query=query)
        selected = records[start:start + limit]
        artifact = self.store.put(encoded(selected), "application/json", self.source, page.url, role="records", query=query, start=start, requested=limit, parent_ref=all_records["ref"])
        return {"status": "ok" if selected else "not_found", "source": self.source, "query": query, "start": start, "requested": limit,
            "received": len(selected), "total": None, "stored_total": len(records), "has_more": start + len(selected) < len(records),
            "records": artifact, "all_records": all_records, "export": source_page if export == "html" else artifact, "evidence": source_page,
            "preview": [{k: row[k] for k in ("id", "title", "url")} for row in selected[:3]],
            "scope": "All rows supplied on this ECCC search page are preserved, including duplicate hits. Snippets are not abstracts. The page provides no independent corpus-wide total."}

    def fetch(self, target, *, parts):
        if set(parts)-{'metadata','abstract','fulltext','supplementary','export'}:
            raise ServiceError('invalid_parts','Unknown requested content')
        revision = None
        if target.startswith(("https://", "http://")):
            parsed = urlsplit(target)
            if parsed.hostname not in self.hosts:
                raise ServiceError("source_boundary", "Target is outside ECCC")
            match = re.fullmatch(r"/report/([0-9]{4})/([0-9]{1,3})/?(?:revision/([0-9]+)/?(?:download)?|download)?", parsed.path)
            if not match:
                raise ServiceError("invalid_target", "Use an ECCC report or revision download URL")
            year, number = int(match.group(1)), int(match.group(2))
            revision = int(match.group(3)) if match.group(3) else 0 if parsed.path.endswith("/download") else None
        else:
            match = re.fullmatch(r"TR([0-9]{2})-([0-9]{3})(?:r([0-9]+))?", target, re.I)
            if not match:
                if not target.strip() or re.match(r'TR[0-9]{2}-',target,re.I):
                    raise ServiceError("invalid_target", "Use TRyy-nnn, TRyy-nnnrN, an ECCC report URL or a title")
                candidates=self.search(target,options={},limit=20)
                return {**candidates,'requested_target':target,'status':'selection_required' if candidates.get('received') else candidates['status'],
                    'message':'Select an ECCC report and revision from the native search candidates'}
            year = int(match.group(1)) + (1900 if int(match.group(1)) >= 94 else 2000)
            number = int(match.group(2))
            revision = int(match.group(3)) if match.group(3) else None
        url = f"https://eccc.weizmann.ac.il/report/{year}/{number:03d}/"
        page = self.gateway.public_page(self.source)
        response = goto_source(page, url, self.hosts, wait_until="domcontentloaded", timeout=SOURCE_WAIT_MS)
        if response and response.status >= 400:
            raise ServiceError("provider_error", "ECCC report request failed", http_status=response.status)
        raw = page.content()
        versions = eccc_versions(raw)
        if not versions:
            raise ServiceError("not_found_at_source" if "404" in page.title() else "invalid_response", "ECCC returned no report revisions", status="not_found" if "404" in page.title() else "error")
        selected = max(versions, key=lambda v: v["revision"]) if revision is None else next((v for v in versions if v["revision"] == revision), None)
        if selected is None:
            raise ServiceError("not_found_at_source", "Requested ECCC revision is not on the report page", status="not_found")
        artifact = self.store.put(encoded([selected]), "application/json", self.source, url, role="records", revision=selected["revision"])
        source_page = self.store.put(clean_html(raw, self.store.sanitizer), "text/html", self.source, url, role="source_page")
        components = {}
        for part in parts:
            if part in ("metadata", "abstract", "export"):
                components[part] = {"status": "available", "artifact": artifact}
            elif part == "fulltext":
                try:
                    data, media, obtained_url = browser_download(self.gateway.context, selected["pdf"], self.hosts)
                    if not data.startswith(b"%PDF-"):
                        raise ServiceError("unexpected_content", "ECCC did not return a PDF")
                    import pymupdf
                    with pymupdf.open(stream=data, filetype="pdf") as doc:
                        pages = len(doc)
                    pdf = self.store.put(data, "application/pdf", self.source, obtained_url, role="fulltext", revision=selected["revision"], pages=pages)
                    components[part] = {"status": "available", "artifact": pdf}
                except ServiceError as error:
                    components[part] = error.result
            elif part == "supplementary":
                components[part] = {"status": "source_page", "artifact": source_page, "reason": "Report page includes revisions and comments; additional attachments are not automatically classified"}
            else:
                raise ServiceError("invalid_parts", "Unknown requested content", part=part)
        return {"status": "ok" if all(v["status"] == "available" for v in components.values()) else "partial", "source": self.source,
            "target": selected["id"], "revision": selected["revision"], "components": components, "records": artifact,
            "source_page": source_page, "versions": [{k: v[k] for k in ("id", "revision", "version_label", "pdf")} for v in versions]}


class ACM:
    source = "acm-dl"
    hosts = {"dl-acm-org.libproxy.knu.ac.kr", "portal-acm-org.libproxy.knu.ac.kr", "dl.acm.org"}
    fields = {"AllField", "Title", "ContentGroupTitle", "ContribAuthor", "Abstract", "Fulltext", "Affiliation", "Keyword", "ConferenceLocation", "ConferenceSponsor", "Contrib", "PubIdSortField", "DOI"}
    formats = {"bibtex": ("bibtex", "application/x-bibtex"), "endnote": ("endNote", "application/x-endnote-refer"), "acmref": ("acm", "text/plain")}
    category_fields = {'SeriesKey','Artifact','Funding','CCS','PrimaryCCS','PublisherRaw'}
    category_operators = {'And','Or','Nor'}
    facet_fields = {'SeriesKey','ConceptID','ContentItemType','SpecifiedLevelConceptID','SponsorAcronymRaw','content'}
    facet_groups = {'SeriesKey':'publication','ConceptID':'concept','ContentItemType':'content_item_type',
        'SpecifiedLevelConceptID':'venue','SponsorAcronymRaw':'sponsor','content':'result_category'}

    def __init__(self, store, gateway):
        self.store, self.gateway = store, gateway
        self.known_records = {}

    def page(self):
        return self.gateway.open(self.source, "ACM", self.hosts, 'input[name="AllField"]')

    @staticmethod
    def boolean_expression(query,options):
        expression=options.get('expression')
        if expression is None:return None
        if not isinstance(expression,str) or not expression.strip() or query!='' or 'field' in options or 'fields' in options:
            raise ServiceError('invalid_options','ACM expression requires query="" and cannot be combined with field or fields')
        return expression

    @staticmethod
    def edit_boolean_query(page,expression):
        edit=page.locator('#search__edit');edit.wait_for(state='visible',timeout=SOURCE_WAIT_MS)
        with page.expect_navigation(wait_until='domcontentloaded'):edit.click()
        syntax=page.get_by_text('View Query Syntax',exact=True)
        if syntax.count() and syntax.is_visible():syntax.click()
        area=page.locator('#editableQuery');area.wait_for(state='visible',timeout=SOURCE_WAIT_MS);area.fill(expression)
        if area.input_value()!=expression:
            raise ServiceError('query_mismatch','ACM Edit Query did not preserve the requested expression')
        with page.expect_navigation(wait_until='domcontentloaded'):
            page.locator('#advanced-search-btn').click()

    @classmethod
    def category_constraint(cls,value):
        if not isinstance(value,dict) or set(value) not in ({'field','operator','value'},{'field','operator','values'}) \
                or value.get('field') not in cls.category_fields or value.get('operator') not in cls.category_operators:
            raise ServiceError('invalid_options','ACM category constraint requires an observed field, And/Or/Nor and exact labels')
        values=[value['value']] if 'value' in value else value['values']
        if not isinstance(values,list) or not values or len(values)!=len(set(values)) or any(not isinstance(item,str) or not item.strip() for item in values):
            raise ServiceError('invalid_options','ACM category constraint values must be distinct nonempty exact labels')
        return {'field':value['field'],'operator':value['operator'],'values':values}

    @classmethod
    def facet_candidates(cls,raw,base):
        candidates=[];seen=set();host=urlsplit(base).hostname;base_params=parse_qs(urlsplit(base).query);soup=BeautifulSoup(raw,'html.parser')
        controls={node.get('aria-controls'):node.get_text(' ',strip=True) for node in soup.select('a.facet__ctrl[aria-controls]')}
        for link in soup.select('a[href]'):
            url=urljoin(base,link['href']);parts=urlsplit(url)
            if parts.hostname!=host or parts.path!='/action/doSearch':continue
            params=parse_qs(parts.query)
            changed=[field for field in cls.facet_fields if params.get(field)!=base_params.get(field)]
            if len(changed)!=1:continue
            field=changed[0];new_values=params.get(field,[]);old_values=base_params.get(field,[])
            added=[value for value in new_values if value not in old_values]
            if len(added)!=1 or any(params.get(existing)!=base_params.get(existing) for existing in cls.facet_fields if existing!=field):continue
            value=added[0];text=link.get_text(' ',strip=True)
            match=re.fullmatch(r'(.+?)\s*\(([0-9,]+)\)',text)
            if not value or (not match and field!='content'):continue
            panel=next((ancestor.get('id') for ancestor in link.parents if ancestor.get('id') in controls),None)
            key=(field,value)
            if key in seen:continue
            seen.add(key);candidates.append({'field':field,'value':value,'label':match[1].strip() if match else text,
                'count':int(match[2].replace(',','')) if match else None,'group':cls.facet_groups[field],
                'panel':panel,'panel_label':controls.get(panel),'url':url})
        return candidates

    @classmethod
    def select_facet(cls,candidates,request):
        if not isinstance(request,dict) or set(request) not in ({'field','value'},{'field','value','panel'}) or request.get('field') not in cls.facet_fields \
                or not isinstance(request.get('value'),str) or not request['value']:
            raise ServiceError('invalid_options','ACM facet requires an observed field and native value')
        matches=[candidate for candidate in candidates if candidate['field']==request['field'] and candidate['value']==request['value']
                 and ('panel' not in request or candidate['panel']==request['panel'])]
        if len(matches)!=1:
            offered=[{key:item[key] for key in ('field','value','label','count','panel','panel_label')} for item in candidates if item['field']==request['field']]
            raise ServiceError('facet_selection_required','Select one facet offered by the current ACM result page',status='selection_required',candidates=offered)
        return matches[0]

    @staticmethod
    def fulltext_document(raw,base,identifier):
        parts=urlsplit(base)
        if parts.path!='/doi/full/'+identifier:
            raise ServiceError('identity_mismatch','ACM HTML full text URL identifies another DOI')
        soup=BeautifulSoup(raw,'html.parser')
        dois=[node.get('content','').strip() for node in soup.select('meta[name="publication_doi" i],meta[name="dc.Identifier" i]')]
        if not any(value.casefold()==identifier.casefold() for value in dois):
            raise ServiceError('identity_mismatch','ACM HTML full text metadata identifies another DOI')
        articles=soup.select('article');body=soup.select('article section#bodymatter');headings=soup.select('article h1')
        if len(articles)!=1 or len(body)!=1 or len(headings)!=1 or not body[0].get_text(' ',strip=True):
            raise ServiceError('document_not_ready','ACM page has no unique article body')
        tex=[node.get_text('',strip=True) for node in articles[0].select('span.core-tex')]
        if any(not value for value in tex):
            raise ServiceError('invalid_response','ACM article contains an empty TeX expression')
        return {'document_doi':identifier,'parent_doi':None,'title':headings[0].get_text(' ',strip=True),
            'body_scope':'article including bodymatter and labeled backmatter','html':str(articles[0]),'tex':tex,
            'body_text_chars':len(body[0].get_text(' ',strip=True)),'sections':len(body[0].select('section')),
            'has_backmatter':bool(articles[0].select('section#backmatter'))}

    @staticmethod
    def citation_selection(checked,requested):
        current={value.casefold():value for value in checked};wanted={value.casefold():value for value in requested}
        return {'uncheck':[current[key] for key in current if key not in wanted],
                'check':[wanted[key] for key in wanted if key not in current]}

    @staticmethod
    def match_citation_records(selected,bibliographic,payload):
        items={}
        if not isinstance(payload,dict) or not isinstance(payload.get('items'),list):
            raise ServiceError('invalid_response','ACM citation response has an unexpected schema')
        for entry in payload['items']:
            if not isinstance(entry,dict):raise ServiceError('invalid_response','ACM citation item wrapper is invalid')
            for key,value in entry.items():
                folded=key.casefold()
                if folded in items or not isinstance(value,dict):raise ServiceError('invalid_response','ACM citation identities are duplicated or invalid')
                if value.get('id') and str(value['id']).casefold()!=folded:
                    raise ServiceError('export_identity_mismatch','ACM citation item key and id differ')
                if value.get('DOI') and str(value['DOI']).casefold()!=folded:
                    raise ServiceError('export_identity_mismatch','ACM citation item key and DOI differ')
                items[folded]=(key,value)
        if payload.get('exportedDoiLength')!=len(items):
            raise ServiceError('invalid_response','ACM citation response count differs from its item wrappers')
        requested=[row['id'].casefold() for row in selected]
        if len(requested)!=len(set(requested)) or any(value not in items for value in requested):
            raise ServiceError('export_identity_mismatch','ACM citation response omitted a selected record')
        used=set();matched=[]
        def title(value):return re.sub(r'\s+',' ',str(value or '')).strip().casefold()
        for row,identifier in zip(selected,requested):
            exact=[index for index,item in enumerate(bibliographic) if identifier in {str(item.get('id','')).casefold(),str(item.get('doi','')).casefold()}]
            if len(exact)==1:index=exact[0]
            elif not exact and identifier.startswith('10.5555/'):
                key,item=items[identifier];record_path=urlsplit(row.get('url','')).path
                if record_path!='/doi/'+row['id'] or title(row.get('title'))!=title(item.get('title')):
                    raise ServiceError('export_identity_mismatch','ACM Guide key, record URL and CSL title do not identify the same record')
                candidates=[i for i,value in enumerate(bibliographic) if title(value.get('title'))==title(item.get('title'))]
                if len(candidates)!=1:raise ServiceError('export_identity_mismatch','ACM Guide citation title is not unique in the source export')
                index=candidates[0]
            else:raise ServiceError('export_identity_mismatch','ACM formatted citation does not identify the selected record')
            if index in used:raise ServiceError('export_identity_mismatch','ACM formatted citation was matched to more than one selected record')
            used.add(index);matched.append(bibliographic[index])
        additional=[key for folded,(key,_) in items.items() if folded not in set(requested)]
        return {'selected':matched,'included_identifiers':[key for key,_ in items.values()],
            'additional_identifiers':additional,'selection_status':'partial' if additional else 'exact'}

    @staticmethod
    def component_failure(error,source_page,code):
        if isinstance(error,ServiceError):
            return {**error.result,'artifact':error.result.get('artifact',source_page)}
        return {'status':'error','code':code,**failure_details(error),'artifact':source_page}

    def render_citations(self, page, payload, identifiers, format):
        items = {}
        if not isinstance(payload,dict) or not isinstance(payload.get('items'),list):
            raise ServiceError('invalid_response','ACM citation response has an unexpected schema')
        for entry in payload['items']:
            if not isinstance(entry,dict) or any(key.casefold() in {item.casefold() for item in items} for key in entry):
                raise ServiceError('invalid_response','ACM citation item wrapper is invalid or duplicated')
            items.update(entry)
        source_data = self.store.put(encoded(payload), "application/json", self.source, page.url, role="native_citation_data", identifiers=identifiers, format=format)
        requested={key.casefold() for key in identifiers};included={key.casefold() for key in items}
        if not requested.issubset(included):
            raise ServiceError("export_identity_mismatch", "ACM citation response omitted a selected record",evidence=source_data,
                requested_count=len(identifiers),item_count=len(items),exported_doi_length=payload.get('exportedDoiLength'))
        if payload.get('exportedDoiLength')!=len(items):
            raise ServiceError('invalid_response','ACM citation response count differs from its item wrappers',evidence=source_data)
        additional=[key for key in items if key.casefold() not in requested]
        script_ref = getattr(self, "processor_ref", None)
        if script_ref is None:
            script_url = "https://" + urlsplit(page.url).hostname + "/templates/jsp/_ux3/_acm/citeproc.min.js"
            script, media, obtained = browser_download(self.gateway.context, script_url, self.hosts)
            if "javascript" not in media:
                raise ServiceError("citation_processor_unavailable", "The observed ACM citation processor did not return JavaScript")
            script_ref = self.store.put(script, "text/javascript", self.source, obtained, preserve_bytes=True, role="citation_processor")
            self.processor_ref = script_ref
        script = self.store.read(script_ref["ref"])[1].decode("utf-8")
        # The publisher's processor and supplied CSL style run without its unrelated page bundles.
        renderer = self.gateway.context.new_page()
        try:
            renderer.route("**/*", lambda route: route.abort())
            renderer.set_content("<html><body></body></html>")
            renderer.evaluate("window.UX = {}")
            renderer.add_script_tag(content=script)
            rendered = renderer.evaluate("""data => {
                const items = Object.assign({}, ...data.items);
                const processor = new UX.CSL.Engine({retrieveLocale: () => data.locale, retrieveItem: id => items[id]}, data.style);
                processor.setOutputFormat('text');
                processor.updateItems(Object.keys(items));
                return processor.makeBibliography();
            }""", payload)
            if not rendered or not isinstance(rendered[1],list) or not rendered[1]:
                raise ServiceError("export_count_mismatch", "Citation processor returned no formatted citation",evidence=source_data)
            text = "\n".join(rendered[1])
        finally:
            renderer.close()
        return self.store.put(text, self.formats[format][1], self.source, page.url, role="citation_export", format=format,
            identifiers=identifiers,included_identifiers=list(items),additional_identifiers=additional,
            selection_status='partial' if additional else 'exact',rendered_count=len(rendered[1]),
            source_data_ref=source_data["ref"], processor_ref=script_ref["ref"])

    def citation(self, page, identifiers, format="bibtex", *, record_page=False):
        if not record_page:
            boxes=page.locator('li.search__item.issue-item-container input[type="checkbox"][name]:checked')
            checked=[box.get_attribute('name') for box in boxes.all() if box.get_attribute('name')]
            changes=self.citation_selection(checked,identifiers)
            for identifier in changes['uncheck']:
                checkbox=page.locator('input[type="checkbox"][name="'+identifier+'"]');checkbox.focus();checkbox.press('Space')
            for identifier in changes['check']:
                checkbox = page.locator('input[type="checkbox"][name="' + identifier + '"]')
                checkbox.focus();checkbox.press("Space")
            selected=[box.get_attribute('name').casefold() for box in page.locator('li.search__item.issue-item-container input[type="checkbox"][name]:checked').all() if box.get_attribute('name')]
            if set(selected)!={value.casefold() for value in identifiers}:
                raise ServiceError('export_identity_mismatch','ACM selected checkboxes differ from the requested records')
        with page.expect_response(lambda r: urlsplit(r.url).path == "/action/exportCiteProcCitation", timeout=SOURCE_WAIT_MS) as exported:
            if record_page:
                page.get_by_role("button", name="Export Citation", exact=True).first.click()
            else:
                page.get_by_text("Export Citations", exact=True).filter(visible=True).first.click()
        selector = page.locator("#citation-format")
        selector.wait_for()
        value, media = self.formats[format]
        if selector.input_value() != value:
            with page.expect_response(lambda r: urlsplit(r.url).path == "/action/exportCiteProcCitation", timeout=SOURCE_WAIT_MS) as exported:
                selector.select_option(value)
        response = exported.value
        if response.status != 200:
            raise ServiceError("export_failed", "ACM native citation response failed", http_status=response.status)
        artifact = self.render_citations(page, response.json(), identifiers, format)
        page.get_by_role("button", name="Close modal", exact=True).filter(visible=True).first.click()
        return artifact

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        allowed = {"field", "fields", "expression", "collection", "from_year", "to_year", "from_month", "to_month", "sort", "constraint", "facet", "facets"}
        if set(options) - allowed or cursor:
            raise ServiceError("invalid_options", "Use ACM field/fields, collection, date range and sort; pagination uses start")
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ServiceError("invalid_range", "ACM requires start >= 0 and limit 1..1000")
        if export not in (None, "json", *self.formats):
            raise ServiceError("invalid_export", "Use json, bibtex, endnote or acmref")
        expression=self.boolean_expression(query,options)
        additional=options.get('fields',[])
        if not isinstance(additional,list):
            raise ServiceError('invalid_options','ACM fields must be an ordered list of field/value terms')
        terms = [{"field": options.get("field", "AllField"), "value": expression if expression is not None else query}, *additional]
        if any(set(term) != {"field", "value"} or term["field"] not in self.fields or not isinstance(term["value"], str) for term in terms):
            raise ServiceError("invalid_options", "Each additional field has field and value; fields are combined by native AND")
        collection = {"fulltext": "dl", "guide": "all"}.get(options.get("collection", "fulltext"))
        if not collection:
            raise ServiceError("invalid_options", "collection must be fulltext or guide")
        constraint=self.category_constraint(options['constraint']) if 'constraint' in options else None
        if 'facet' in options and 'facets' in options:
            raise ServiceError('invalid_options','Use facet or facets, not both')
        facets=[options['facet']] if 'facet' in options else options.get('facets',[])
        valid_keys=({'field','value'},{'field','value','panel'})
        if not isinstance(facets,list) or any(not isinstance(item,dict) or set(item) not in valid_keys or item.get('field') not in self.facet_fields
                or not isinstance(item.get('value'),str) or not item['value'] or ('panel' in item and (not isinstance(item['panel'],str)
                or not re.fullmatch(r'[A-Za-z0-9/_-]+',item['panel']))) for item in facets):
            raise ServiceError('invalid_options','ACM facet requires field and native value')
        if len(facets)!=len({(item['field'],item['value'],item.get('panel')) for item in facets}):
            raise ServiceError('invalid_options','ACM facets must be distinct')
        sort=options.get('sort')
        if sort is not None and sort not in ('EpubDate_asc','EpubDate_desc','downloaded','cited'):
            raise ServiceError('invalid_options','Validated ACM sort values are EpubDate_asc, EpubDate_desc, downloaded and cited')
        dates={key:options.get(key) for key in ('from_year','to_year','from_month','to_month')}
        if any(value is not None and (type(value) is not int or (key.endswith('month') and not 1<=value<=12)) for key,value in dates.items()):
            raise ServiceError('invalid_options','ACM date values use integer years and months 1..12')
        if (dates['from_month'] is not None and dates['from_year'] is None) or (dates['to_month'] is not None and dates['to_year'] is None):
            raise ServiceError('invalid_options','ACM month bounds require the corresponding year')
        if dates['from_year'] is not None and dates['to_year'] is not None:
            lower=(dates['from_year'],dates['from_month'] or 1);upper=(dates['to_year'],dates['to_month'] or 12)
            if lower>upper:raise ServiceError('invalid_options','ACM from date must not be after its to date')
        page = self.page()
        host = urlsplit(page.url).hostname
        goto_source(page, "https://" + host + "/search/advanced", self.hosts, wait_until="domcontentloaded", timeout=SOURCE_WAIT_MS)
        page.locator('select[name="expand"]').select_option(collection)
        for index, term in enumerate(terms, 1):
            if index > 1:
                page.locator(".advanced-search__search-in__add").filter(visible=True).first.click()
            page.locator("#searchArea" + str(index)).select_option(term["field"])
            entry = page.locator("#text" + str(index))
            entry.fill(term["value"])
            entry.press("Tab")
            if term["value"]:
                page.wait_for_function("i => document.getElementById('text'+i).name === 'text'+i && document.getElementById('searchArea'+i).name === 'field'+i", arg=index)
        if constraint:
            page.locator('[name="searchArea[0]"]').select_option(constraint['field'])
            page.locator('[name="operator[0]"]').select_option(constraint['operator'])
            entry=page.locator('[name="text[0]"]')
            for value in constraint['values']:
                entry.fill(value);page.wait_for_timeout(500)
                labels=page.locator('li:visible').evaluate_all("nodes => nodes.map(n => n.textContent.trim()).filter(Boolean)")
                exact=page.get_by_text(value,exact=True).filter(visible=True)
                if exact.count()!=1:
                    raise ServiceError('constraint_selection_required','Select one exact category label offered by ACM',status='selection_required',candidates=labels[:20])
                exact.click()
        if any(value is not None for value in dates.values()):
            page.locator("#customRange").focus()
            page.locator("#customRange").press("Space")
            for option, control in {"from_year": "fromYear", "to_year": "toYear", "from_month": "fromMonth", "to_month": "toMonth"}.items():
                if options.get(option) is not None:
                    selector=page.locator('#'+control)
                    if not selector.locator('option[value="'+str(options[option])+'"]').count():
                        raise ServiceError('invalid_options','ACM date value is not offered by the current control',control=option)
                    selector.select_option(str(options[option]))
        with page.expect_navigation(wait_until="domcontentloaded"):
            page.locator("#advanced-search-btn").click()
        parsed = urlsplit(page.url)
        params = parse_qs(parsed.query, keep_blank_values=True)
        if params.get("expand") != [collection] or any(params.get('field'+str(index))!=[term['field']] or params.get('text'+str(index))!=[term['value']]
                                                      for index,term in enumerate(terms,1)):
            raise ServiceError("query_mismatch", "ACM did not submit the requested field and collection")
        if expression is not None:
            self.edit_boolean_query(page,expression)
            parsed=urlsplit(page.url);params=parse_qs(parsed.query,keep_blank_values=True)
            if params.get('expand')!=[collection] or params.get('AllField')!=[expression]:
                raise ServiceError('query_mismatch','ACM result did not preserve the exact Edit Query expression and collection')
        native_constraint=None
        if constraint:
            key=constraint['field']+constraint['operator'];values=params.get(key)
            if not values or len(values)!=len(constraint['values']) or any(not value for value in values):
                raise ServiceError('query_mismatch','ACM did not submit the selected category constraint')
            native_constraint={**constraint,'native_key':key,'native_values':values,**({'native_value':values[0]} if len(values)==1 else {})}
        facet_artifacts=[];selected_facets=[]
        for step,facet in enumerate(facets,1):
            if facet.get('panel'):
                control=page.locator('a.facet__ctrl[aria-controls="'+facet['panel']+'"]')
                if control.count()!=1:
                    raise ServiceError('facet_selection_required','The requested ACM facet panel is not offered',status='selection_required',panel=facet['panel'])
                if control.get_attribute('aria-expanded')!='true':control.click();page.wait_for_timeout(1200)
            current_raw=page.locator('main').inner_html();candidates=self.facet_candidates(current_raw,page.url)
            facet_artifacts.append(self.store.put(encoded([{key:item[key] for key in ('field','value','label','count','group','panel','panel_label')} for item in candidates]),
                'application/json',self.source,page.url,role='facet_candidates',query=query,step=step))
            selected=self.select_facet(candidates,facet);selected_facets.append(selected)
            params=parse_qs(urlsplit(selected['url']).query,keep_blank_values=True)
            retained=params.get('AllField')==[expression] if expression is not None else all(
                params.get('field'+str(index))==[term['field']] and params.get('text'+str(index))==[term['value']]
                for index,term in enumerate(terms,1))
            if params.get('expand')!=[collection] or not retained:
                raise ServiceError('query_mismatch','ACM facet link did not retain the submitted search')
            if step<len(facets):
                goto_source(page,selected['url'],self.hosts,wait_until='domcontentloaded',timeout=SOURCE_WAIT_MS);page.locator('main').wait_for()
        if sort:
            params["sortBy"] = [sort]
        size = 50
        params["pageSize"] = [str(size)]
        rows, evidence, exports, source_exports, export_scopes = [], [], [], [], []
        total = None;base_params={key:list(value) for key,value in params.items() if key not in ('startPage','pageSize')}
        for page_index in range(start // size, (start + limit - 1) // size + 1):
            params["startPage"] = [str(page_index)]
            url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(params, doseq=True), ""))
            goto_source(page, url, self.hosts, wait_until="domcontentloaded", timeout=SOURCE_WAIT_MS)
            observed=parse_qs(urlsplit(page.url).query,keep_blank_values=True)
            if any(observed.get(key)!=value for key,value in base_params.items()):
                raise ServiceError('query_mismatch','ACM pagination did not retain the submitted search and filters',page=page_index)
            main = page.locator("main")
            main.wait_for()
            text = main.inner_text()
            match = re.search(r"([0-9,]+)\s+Results? for:", text, re.I)
            if not match:
                raise ServiceError("invalid_response", "ACM result count is missing")
            observed_total=int(match.group(1).replace(",", ""))
            if total is not None and observed_total!=total:
                raise ServiceError('search_range_changed','ACM result total changed while reading the requested range',previous_total=total,current_total=observed_total,page=page_index)
            total=observed_total
            raw = main.inner_html()
            records = acm_records(raw, page.url)
            expected=min(size,max(0,total-page_index*size))
            if len(records)!=expected or len({row['id'].casefold() for row in records})!=len(records):
                raise ServiceError('invalid_response','ACM result page does not match its reported range',page=page_index,expected=expected,received=len(records))
            evidence.append(self.store.put(clean_html(raw, self.store.sanitizer), "text/html", self.source, page.url, role="search_page", query=query,
                options=options,native_constraint=native_constraint,
                selected_facets=[{key:item[key] for key in ('field','value','label','count','group','panel','panel_label')} for item in selected_facets]))
            selected = [row for i, row in enumerate(records, page_index * size) if start <= i < start + limit]
            if selected:
                native = self.citation(page, [row["id"] for row in selected])
                bibliographic = bibliography(self.store.read(native["ref"])[1], "application/x-bibtex")
                payload=json.loads(self.store.read(native['source_data_ref'])[1]);matched=self.match_citation_records(selected,bibliographic,payload)
                source_manifest=self.store.read(native['source_data_ref'])[0];provider_source={'ref':native['source_data_ref'],**source_manifest}
                scope={'page':page_index,'requested_identifiers':[row['id'] for row in selected],
                    'included_identifiers':matched['included_identifiers'],'additional_identifiers':matched['additional_identifiers'],
                    'selection_status':matched['selection_status'],'rendered_count':native['rendered_count'],
                    'source_export':provider_source,'rendered_export':native}
                export_scopes.append(scope);source_exports.append(provider_source)
                for row,bib in zip(selected,matched['selected']):
                    row.update(bibliography=bib, year=bib.get("year"), abstract=bib.get("abstract"))
                    self.known_records[row["id"].lower()] = (bib, native, scope)
                rows.extend(selected)
                output=native if export in (None,"json","bibtex") else self.citation(page,[row['id'] for row in selected],export)
                if output is not native:
                    source_manifest=self.store.read(output['source_data_ref'])[0]
                    source_exports.append({'ref':output['source_data_ref'],**source_manifest})
                exports.append(output)
            if (page_index + 1) * size >= total:
                break
        artifact = self.store.put(encoded(rows), "application/json", self.source, page.url, role="records", query=query, options=options, start=start, requested=limit, total=total)
        exported = artifact
        if export not in (None, "json") and exports:
            if len(exports)==1:exported=exports[0]
            else:
                content = b"\n\n".join(self.store.read(a["ref"])[1] for a in exports)
                exported = self.store.put(content, self.formats[export][1], self.source, page.url, role="citation_export", format=export, count=len(rows),
                    parent_refs=[item['ref'] for item in exports])
        partial=any(scope['selection_status']=='partial' for scope in export_scopes)
        if partial:exported={'status':'partial','artifact':exported,'source_exports':source_exports,'scopes':export_scopes}
        return {"status": "partial" if partial else "ok" if rows else "not_found", "source": self.source, "query": query, "options": options,
            "start": start, "requested": limit, "received": len(rows), "total": total, "has_more": start + len(rows) < total,
            "next": {"start": start + len(rows)} if start + len(rows) < total else None, "records": artifact, "export": exported,
            "native_citations": exports,"source_export":source_exports[0] if source_exports else None,"source_exports":source_exports,
            "export_scopes":export_scopes,"evidence": evidence, "native_constraint":native_constraint,
            "facet":{key:selected_facets[0][key] for key in ('field','value','label','count','group','panel','panel_label')} if len(selected_facets)==1 else None,
            "facets":[{key:item[key] for key in ('field','value','label','count','group','panel','panel_label')} for item in selected_facets],
            "facet_candidates":None if not facet_artifacts else facet_artifacts[0] if len(facet_artifacts)==1 else facet_artifacts,
            "native_expression":expression,
            "preview": [{k: row.get(k) for k in ("id", "title", "year")} for row in rows[:3]]}

    def fetch(self, target, *, parts):
        from api_adapters import doi
        value = target
        if target.startswith(("http://", "https://")) and urlsplit(target).hostname in self.hosts:
            value = re.sub(r"^/doi/(?:pdf/|epdf/|full/|abs/)?", "", urlsplit(target).path)
        elif target.startswith(("http://", "https://")) and urlsplit(target).hostname not in {"doi.org", "dx.doi.org"}:
            raise ServiceError("source_boundary", "Use an ACM record URL or DOI")
        try:
            identifier = doi(value)
        except ServiceError:
            result = self.search(target, options={"field": "Title", "collection": "guide"}, limit=20)
            result["status"] = "selection_required" if result["received"] else "not_found"
            return result
        if identifier.lower() not in self.known_records:
            result = self.search(identifier, options={"field": "DOI", "collection": "guide"}, limit=2, export="bibtex")
            if result["status"] not in ('ok','partial'):
                return result
            if result["total"] != 1 or identifier.lower() not in self.known_records:
                result["status"] = "selection_required"
                return result
        record, citation_source, citation_scope = self.known_records[identifier.lower()]
        page = self.page()
        url = "https://" + urlsplit(page.url).hostname + "/doi/" + quote(identifier, safe="/")
        goto_source(page, url, self.hosts, wait_until="domcontentloaded", timeout=SOURCE_WAIT_MS)
        page.get_by_role("heading", level=1).first.wait_for()
        records = [record]
        native = self.store.put(record["raw_text"], "application/x-bibtex", self.source, page.url, role="citation_export", identifiers=[identifier], parent_ref=citation_source["ref"])
        artifact = self.store.put(encoded(records), "application/json", self.source, page.url, role="records", target=identifier)
        raw = page.locator("main").inner_html()
        source_page = self.store.put(clean_html(raw, self.store.sanitizer), "text/html", self.source, page.url, role="source_page", target=identifier)
        components = {}
        for part in parts:
            if part in ("metadata", "export"):
                components[part] = {"status": "available", "artifact": native if part == "export" else artifact}
            elif part == "abstract":
                components[part] = {"status": "available", "artifact": artifact} if records[0].get("abstract") else {"status": "not_found", "reason": "This native citation has no abstract field"}
            elif part == 'fulltext_html':
                try:
                    links=[urljoin(page.url,node.get_attribute('href')) for node in page.locator('a[href*="/doi/full/"]').all()]
                    candidates=list(dict.fromkeys(candidate for candidate in links if urlsplit(candidate).path=='/doi/full/'+identifier))
                    if not candidates:
                        components[part]={"status":"not_found","reason":"No selected-document HTML full-text control","artifact":source_page}
                        continue
                    if len(candidates)!=1:
                        raise ServiceError('identity_mismatch','ACM record has multiple HTML full-text controls for the selected DOI')
                    full_page=self.gateway.context.new_page()
                    try:
                        goto_source(full_page,candidates[0],self.hosts,wait_until='commit',timeout=SOURCE_WAIT_MS)
                        full_page.locator('article section#bodymatter').wait_for(timeout=SOURCE_WAIT_MS)
                        parsed=self.fulltext_document(full_page.content(),full_page.url,identifier)
                    finally:full_page.close()
                    expected=' '.join(str(record.get('title','')).split()).casefold();observed=' '.join(parsed['title'].split()).casefold()
                    if expected and observed!=expected:
                        raise ServiceError('identity_mismatch','ACM HTML full text title differs from its native citation')
                    html=self.store.put(clean_html(parsed['html'],self.store.sanitizer),'text/html',self.source,candidates[0],role='fulltext_html',
                        target=identifier,document_doi=identifier,parent_doi=parsed['parent_doi'],body_scope=parsed['body_scope'],
                        body_text_chars=parsed['body_text_chars'],sections=parsed['sections'],has_backmatter=parsed['has_backmatter'])
                    equations=self.store.put(encoded(parsed['tex']),'application/json',self.source,candidates[0],role='math_expressions',
                        target=identifier,notation='TeX from span.core-tex',count=len(parsed['tex']),parent_ref=html['ref'])
                    components[part]={"status":"available","artifact":html,"math":{"status":"available","artifact":equations,
                        "notation":"TeX","count":len(parsed['tex'])},"scope":parsed['body_scope']}
                except Exception as error:components[part]=self.component_failure(error,source_page,'html_retrieval_failed')
            elif part == "fulltext":
                link = page.locator('a[href*="/doi/pdf/"]').filter(visible=True)
                candidates = [urljoin(page.url, a.get_attribute("href")) for a in link.all()]
                candidates = [u for u in candidates if urlsplit(u).path == "/doi/pdf/" + identifier]
                if not candidates:
                    components[part] = {"status": "not_found", "reason": "No selected-document PDF control; HTML full text is a separate requested part", "artifact": source_page}
                    continue
                try:
                    data, media, obtained_url = browser_download(self.gateway.context, candidates[0], self.hosts)
                    if not data.startswith(b"%PDF-"):
                        raise ServiceError("unexpected_content", "ACM PDF control returned no PDF")
                    import pymupdf
                    with pymupdf.open(stream=data, filetype="pdf") as document:
                        pages = len(document)
                    pdf = self.store.put(data, "application/pdf", self.source, obtained_url, role="fulltext", target=identifier, pages=pages)
                    components[part] = {"status": "available", "artifact": pdf}
                except ServiceError as error:
                    components[part] = self.component_failure(error,source_page,'pdf_retrieval_failed')
                except Exception as error:
                    components[part] = self.component_failure(error,source_page,'pdf_retrieval_failed')
            elif part == "supplementary":
                try:
                    from supplements import fetch_supplementary
                    components[part]=fetch_supplementary(self,page,identifier,source_page,download_hosts=self.hosts)
                    components[part].setdefault('artifact',source_page)
                except ServiceError as exc:components[part]=exc.result
                except Exception as exc:components[part]={'status':'error','code':'supplementary_retrieval_failed',**failure_details(exc),'artifact':source_page}
            else:
                raise ServiceError("invalid_parts", "Unknown requested content", part=part)
        return {"status": "ok" if all(v["status"] == "available" for v in components.values()) else "partial", "source": self.source,
            "target": identifier, "components": components, "records": artifact, "source_page": source_page, "native_citation": native,
            "source_export":citation_scope['source_export'],"rendered_source_export":citation_source,"export_scope":citation_scope}
