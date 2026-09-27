"""Check the delivered offline HTML, links, source corpus and browser interactions."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import unquote, urlsplit
sys.dont_write_bytecode = True
from course_sources import source_bytes, source_manifest

BASE=Path(__file__).resolve().parents[1]

class Document(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True)
        self.ids=[]; self.links=[]; self.lang=None; self.h1=0
        self.source_lines=[]; self.in_source=False; self.source_buffer=None
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag=='html': self.lang=a.get('lang')
        if tag=='h1': self.h1+=1
        if tag=='div' and 'source-line' in a.get('class','').split(): self.in_source=True
        if tag=='span' and self.in_source: self.source_buffer=[]
        if tag in {'a','link'} and a.get('href'): self.links.append(a['href'])
        if tag=='script' and a.get('src'): self.links.append(a['src'])
    def handle_data(self,data):
        if self.source_buffer is not None: self.source_buffer.append(data)
    def handle_endtag(self,tag):
        if tag=='span' and self.source_buffer is not None:
            self.source_lines.append(''.join(self.source_buffer)); self.source_buffer=None
        if tag=='div': self.in_source=False

def static_checks(output_dir=None):
    pages={p.resolve():Document(p.read_text(encoding='utf-8')) for p in BASE.rglob('*.html')}
    errors=[]; links=0
    for path,doc in pages.items():
        duplicate=[k for k,v in Counter(doc.ids).items() if v>1]
        if duplicate: errors.append((str(path.relative_to(BASE)), 'duplicate_ids',duplicate))
        if doc.lang!='ko' or doc.h1!=1: errors.append((str(path.relative_to(BASE)),'document_shell',doc.lang,doc.h1))
        for url in doc.links:
            parts=urlsplit(url)
            if parts.scheme or parts.netloc: errors.append((str(path),'unexpected_network_dependency',url)); continue
            target=(path.parent/unquote(parts.path)).resolve() if parts.path else path
            links+=1
            if not target.exists(): errors.append((str(path.relative_to(BASE)),'missing_target',url))
            elif parts.fragment and target.suffix=='.html':
                d=pages.get(target)
                if d is None: d=Document(target.read_text(encoding='utf-8'))
                if unquote(parts.fragment) not in d.ids: errors.append((str(path.relative_to(BASE)),'missing_anchor',url))
    m=source_manifest()
    originals=source_bytes()
    c=json.loads((BASE/'reference/coverage.json').read_text(encoding='utf-8'))
    if {x['path'] for x in m['files']}!={x['path'] for x in c}: errors.append('coverage_population_mismatch')
    for row in m['files']:
        raw=originals[row['path']]
        if sha256(raw).hexdigest()!=row['sha256']: errors.append(('raw_mismatch',row['path']))
        source=pages[(BASE/'reference/sources'/row['viewer']).resolve()]
        expected={f'L{i}' for i in range(1,row['lines']+1)}
        if not expected.issubset(source.ids): errors.append(('line_coverage',row['path']))
        if source.source_lines!=raw.decode('utf-8-sig').splitlines(): errors.append(('source_view_text',row['path']))
    # Workspace Markdown links must also resolve; skip the frozen originals and editorial quotations.
    for file in (BASE/'MISSION.md',BASE/'RESOURCES.md',BASE/'NOTES.md'):
        for target in re.findall(r'\]\(([^)]+)\)',file.read_text(encoding='utf-8')):
            if not (file.parent/target).resolve().exists(): errors.append((file.name,'markdown_link',target))
    report={'html_files':len(pages),'links_checked':links,'source_files':len(m['files']),
            'lessons':len(list((BASE/'lessons').glob('*.html'))),'errors':errors}
    if output_dir is not None:
        output_dir.mkdir(parents=True,exist_ok=True)
        (output_dir/'static-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
    if errors: raise SystemExit(1)

def browser_checks(output_dir=None):
    from playwright.sync_api import sync_playwright
    if output_dir is None:
        with tempfile.TemporaryDirectory(prefix='do-math-course-check-') as folder:
            return browser_checks(Path(folder))
    evidence=output_dir/'browser'; evidence.mkdir(parents=True,exist_ok=True)
    errors=[]; feedback_count=0; visited=[]
    teaching=[BASE/'index.html',*sorted((BASE/'lessons').glob('*.html')),*sorted((BASE/'reference').glob('*.html'))]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={'width':1365,'height':900},device_scale_factor=1)
        page.on('pageerror',lambda e:errors.append('js:'+str(e)))
        for file in teaching:
            page.goto(file.as_uri()); visited.append(file.relative_to(BASE).as_posix())
            if page.locator('h1').count()!=1: errors.append(file.name+':h1')
            for quiz in page.locator('.quiz').all():
                expected=int(quiz.get_attribute('data-answer'))
                for index,button in enumerate(quiz.locator('button').all()):
                    button.click()
                    actual=quiz.locator('.feedback').get_attribute('class')
                    if ('ok' if index==expected else 'retry') not in actual: errors.append(file.name+':quiz_feedback')
                    if not quiz.locator('.feedback').inner_text().strip(): errors.append(file.name+':empty_feedback')
                    feedback_count+=1
            page.set_viewport_size({'width':390,'height':844})
            width=page.evaluate('({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth})')
            if width['scroll']>width['client']+1: errors.append(file.name+':mobile_overflow:'+str(width))
            if file.name in ('0001-five-judgments.html','0017-identity-review.html','0009-scenarios.html'):
                page.screenshot(path=str(evidence/(file.stem+'-mobile.png')),full_page=True)
            page.set_viewport_size({'width':1365,'height':900})
        page.goto((BASE/'index.html').as_uri()); page.screenshot(path=str(evidence/'index-desktop.png'),full_page=True)
        page.goto((BASE/'lessons/0007-task-contract.html').as_uri()); page.screenshot(path=str(evidence/'lesson-desktop.png'),full_page=True)
        page.goto((BASE/'reference/0002-glossary.html').as_uri())
        total=page.locator('.glossary-entry').count(); page.locator('[data-glossary-search]').fill('판정 사용 효력')
        visible=page.locator('.glossary-entry:visible').count()
        if not (0<visible<total): errors.append('glossary_filter')
        page.locator('[data-glossary-search]').fill('zzzz-missing-term')
        if page.locator('.glossary-entry:visible').count()!=0: errors.append('glossary_empty')
        page.locator('[data-glossary-search]').fill('')
        if page.locator('.glossary-entry:visible').count()!=150: errors.append('glossary_reset')
        page.goto((BASE/'reference/0007-catalog.html').as_uri()); page.locator('[data-catalog-search]').fill('scripts/do_math/submission.py')
        if page.locator('[data-catalog-row]:visible').count()!=1: errors.append('catalog_filter')
        page.goto((BASE/'reference/0009-scenarios.html').as_uri())
        for i in range(5):
            if page.locator('[data-step]:visible').count()!=1: errors.append('scenario_visible')
            if not page.locator('[data-position]').inner_text().startswith(str(i+1)): errors.append('scenario_position')
            if i<4: page.locator('[data-next]').click()
        if not page.locator('[data-next]').is_disabled(): errors.append('scenario_end')
        page.emulate_media(media='print')
        if page.locator('[data-step]:visible').count()!=5: errors.append('scenario_print')
        page.goto((BASE/'lessons/0017-identity-review.html').as_uri())
        page.pdf(path=str(evidence/'lesson-print.pdf'),format='A4',print_background=True,margin={'top':'15mm','bottom':'15mm','left':'15mm','right':'15mm'})
        if not page.locator('details.answer').is_visible(): errors.append('print_answer_missing')
        browser.close()
    report={'pages':len(visited),'page_paths':visited,'viewports':[1365,390],
            'quiz_choices_checked':feedback_count,'glossary_entries':150,'scenario_cases':5,
            'print':'A4 lesson and all scenario steps','errors':errors}
    (output_dir/'browser-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
    if errors: raise SystemExit(1)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=['static','browser'])
    parser.add_argument('--output-dir',type=Path,help='keep evidence only when requested')
    args=parser.parse_args()
    {'static':static_checks,'browser':browser_checks}[args.mode](args.output_dir)
