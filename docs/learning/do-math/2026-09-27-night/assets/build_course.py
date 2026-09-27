"""Build an offline course from authored content and a pinned local source corpus."""
from __future__ import annotations
import argparse
from html import escape
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True
from course_sources import source_bytes, source_manifest, source_text

BASE = Path(__file__).resolve().parents[1]

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')

def verify_source():
    print(json.dumps({'files': len(source_bytes()), 'commit': source_manifest()['head'],
                      'mismatches': []}, ensure_ascii=False))

def load_course():
    spec = importlib.util.spec_from_file_location('course_content', BASE / 'content/course.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def inline(text, sources=None, prefix='../reference/sources/'):
    tokens = {}
    def save(html):
        key = f'\x01{len(tokens)}\x02'
        tokens[key] = html
        return key
    def source_link(match):
        path, _, heading = match.group(1).partition('::')
        row = sources[path]
        lines = source_text(path).splitlines()
        line = 1
        if heading:
            candidates = [i+1 for i,s in enumerate(lines) if (s.lstrip('# ').strip().replace('`','') == heading.replace('`',''))]
            if len(candidates) != 1:
                raise ValueError(f'Source heading not unique: {path}::{heading}: {candidates}')
            line = candidates[0]
        label = path + (' · ' + heading if heading else '')
        return save(f'<a class="source-ref" href="{prefix}{row["viewer"]}#L{line}">{escape(label)}</a>')
    if sources:
        text = re.sub(r'\[\[([^\]]+)\]\]', source_link, text)
    text = re.sub(r'`([^`]+)`', lambda m: save('<code>'+escape(m.group(1))+'</code>'), text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: save('<a href="'+escape(m.group(2),quote=True)+'">'+escape(m.group(1))+'</a>'), text)
    text = escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    for key, value in tokens.items():
        text = text.replace(key, value)
    return text

def render(text, sources, prefix='../reference/sources/'):
    lines = text.strip().splitlines()
    out, i, section = [], 0, 0
    fmt = lambda s: inline(s, sources, prefix)
    while i < len(lines):
        line = lines[i]
        if not line.strip(): i += 1; continue
        if line.startswith('```'):
            lang = line[3:].strip(); block = []; i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                block.append(lines[i]); i += 1
            out.append('<pre><code class="language-'+escape(lang)+'">'+escape('\n'.join(block))+'</code></pre>'); i += 1; continue
        if line.startswith('#'):
            n = len(line)-len(line.lstrip('#')); section += 1
            out.append(f'<h{n} id="section-{section}">{fmt(line[n:].strip())}</h{n}>'); i += 1; continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                cells=[s.strip() for s in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch('[: -]+',s) for s in cells): rows.append(cells)
                i+=1
            out.append('<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+fmt(x)+'</th>' for x in rows[0])+'</tr></thead><tbody>')
            out.extend('<tr>'+''.join('<td>'+fmt(x)+'</td>' for x in row)+'</tr>' for row in rows[1:])
            out.append('</tbody></table></div>'); continue
        if line.startswith('- ') or re.match(r'\d+\. ',line):
            numbered=not line.startswith('- '); tag='ol' if numbered else 'ul'; out.append('<'+tag+'>')
            pattern=r'\d+\. ' if numbered else r'- '
            while i<len(lines) and re.match(pattern,lines[i]):
                out.append('<li>'+fmt(re.sub('^'+pattern,'',lines[i]))+'</li>'); i+=1
            out.append('</'+tag+'>'); continue
        if line.startswith('> '):
            out.append('<aside class="callout"><p>'+fmt(line[2:])+'</p></aside>'); i+=1; continue
        para=[line]; i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||```|- |\d+\. |> )',lines[i]):
            para.append(lines[i]); i+=1
        out.append('<p>'+fmt(' '.join(para))+'</p>')
    return '\n'.join(out)

def page(title, body, level=1, kind='수업', wide=False):
    up='../'*level
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} · do-math 9월 27일 밤</title><link rel="stylesheet" href="{up}assets/course.css"><script defer src="{up}assets/course.js"></script></head>
<body><a class="skip-link" href="#main">본문으로</a><div class="shell{' source-shell' if wide else ''}">
<nav class="topbar" aria-label="과정 탐색"><a href="{up}index.html">do-math · 9월 27일 밤</a><span><a href="{up}reference/0001-map.html">전체 지도</a> · <a href="{up}reference/0002-glossary.html">용어</a> · <a href="{up}reference/0007-catalog.html">원문·구현 찾기</a></span></nav>
<main id="main"><div class="eyebrow">{escape(kind)} / 2026.09.27 NIGHT</div>{body}</main>
<footer class="footer">기준: bdccee3 · do-math-cli/5 · do-math-state/7. 교육용 사례는 실제 실행 증거와 구별합니다. 이해가 막히는 문장이나 회상 답을 대화에 보내면 이어서 설명합니다.</footer></div></body></html>'''

def build(draft=None):
    course=load_course()
    data=source_manifest()
    sources={x['path']:x for x in data['files']}
    aggregate=['# do-math 전체 과정 — 2026년 9월 27일 밤\n\n'+course.INTRO]
    cards=[]
    for i,item in enumerate(course.LESSONS,1):
        slug=f'{i:04}-{item["slug"]}.html'; item['filename']=slug
        assert len({len(x.split()) for x in item['choices']})==1, item['title']
        assert item['answer'] in range(len(item['choices']))
    for i,item in enumerate(course.LESSONS,1):
        title=f'{i:02}. {item["title"]}'
        body='<h1>'+escape(title)+'</h1><p class="lead">'+escape(item['win'])+'</p>'
        body+=render(item['body'],sources)
        body+='<h2 id="practice">판단 연습</h2><fieldset class="quiz" data-answer="'+str(item['answer'])+'" data-explain="'+escape(item['explain'],quote=True)+'"><legend>'+escape(item['question'])+'</legend>'
        for j,c in enumerate(item['choices']): body+=f'<button type="button" data-choice="{j}" aria-pressed="false">{escape(c)}</button>'
        body+='<p class="feedback" role="status" aria-live="polite"></p></fieldset>'
        body+='<details class="answer"><summary>정답과 해설</summary><p>'+escape(item['choices'][item['answer']])+' — '+escape(item['explain'])+'</p></details>'
        body+='<aside class="recall"><h2>자기 말로 남기기</h2><p>'+escape(item['recall'])+'</p><label for="recall-answer">나의 설명</label><textarea id="recall-answer" placeholder="이 답변은 저장하거나 전송하지 않습니다."></textarea><p class="muted">오늘은 본문을 덮고 설명하고, 하루 뒤 같은 질문을 다시 답해 보세요. 답을 대화에 보내면 피드백을 받을 수 있습니다.</p></aside>'
        body+='<h2 id="sources">원문에서 확인하기</h2><p class="source">'+inline(' · '.join('[['+p+']]' for p in item['sources']),sources)+'</p>'
        body+='<p><a href="../reference/0001-map.html">전체 흐름에 놓아 보기</a> · <a href="../reference/0002-glossary.html">용어 찾아보기</a></p>'
        body+='<nav class="lesson-nav" aria-label="이전 다음 수업">'
        body+=('<a href="'+course.LESSONS[i-2]['filename']+'">← 이전 수업</a>' if i>1 else '<a href="../index.html">← 시작 페이지</a>')
        body+=('<a href="'+course.LESSONS[i]['filename']+'">다음 수업 →</a>' if i<len(course.LESSONS) else '<a href="../reference/0001-map.html">전체 지도 →</a>')+'</nav>'
        write(BASE/'lessons'/item['filename'],page(title,body))
        cards.append(f'<a class="card" href="lessons/{item["filename"]}"><small>{i:02} / {escape(item["part"])}</small><strong>{escape(item["title"])}</strong><span>{escape(item["win"])}</span></a>')
        aggregate.append(f'# {title}\n\n{item["win"]}\n\n{item["body"].strip()}\n\n## 판단 연습\n\n{item["question"]}\n\n'+ '\n'.join('- '+c for c in item['choices'])+'\n\n정답: '+item['choices'][item['answer']]+'\n\n해설: '+item['explain']+'\n\n회상: '+item['recall']+'\n\n원문: '+'; '.join(item['sources']))
    for filename, title, body in course.REFERENCES:
        write(BASE/'reference'/filename,page(title,'<h1>'+escape(title)+'</h1>'+render(body,sources,'sources/'),kind='빠른 참조'))
        aggregate.append('# 참조: '+title+'\n\n'+body)
    scenario_intro='각 카드는 앞 카드와 독립적인 교육용 상황입니다. 사건이 바뀌었을 때 서로 다른 상태 축이 어떻게 달라지는지 비교하세요. 실제 실행 증거는 아닙니다.'
    body='<h1>사건에 따라 상태를 나누어 보기</h1><p>'+scenario_intro+'</p><div data-walkthrough><div class="controls"><button data-prev>← 이전 상황</button><span data-position aria-live="polite"></span><button data-next>다음 상황 →</button></div>'
    scenario_text=['# 참조: 사건에 따라 상태를 나누어 보기\n\n'+scenario_intro]
    for i,(title,*values) in enumerate(course.SCENARIOS,1):
        body+=f'<section class="step" data-step><span class="step-number">상황 {i}</span><h2>{escape(title)}</h2><div class="flow">'+''.join('<span>'+escape(x)+'</span>' for x in values[:-1])+'</div><p>'+escape(values[-1])+'</p></section>'
        scenario_text.append('## '+title+'\n\n'+'\n\n'.join(values))
    body+='</div><p><a href="../lessons/'+course.LESSONS[-1]['filename']+'">26강의 전체 사례로 돌아가기</a></p>'
    write(BASE/'reference/0009-scenarios.html',page('사건과 상태',body,kind='상태 비교'))
    aggregate.append('\n\n'.join(scenario_text))
    draft_text='\n\n---\n\n'.join(aggregate)+'\n'
    if draft is not None:
        write(draft, draft_text)
    # Exact source viewers and AST symbol indexes are derived, not authored claims.
    for row in data['files']:
        text=source_text(row['path'])
        body='<h1>'+escape(row['path'])+'</h1><p class="source">'+str(row['lines'])+'줄 · SHA-256 <code>'+row['sha256']+'</code></p>'
        if row['symbols']:
            body+='<details><summary>정의된 클래스·함수 '+str(len(row['symbols']))+'개</summary><ul>'
            body+=''.join('<li><a href="#L'+str(s['line'])+'">'+escape(s['name'])+'</a></li>' for s in row['symbols'])+'</ul></details>'
        body+='<div class="source-code">'+''.join(f'<div class="source-line" id="L{n}"><a class="line-number" href="#L{n}">{n}</a><span>{escape(s)}</span></div>' for n,s in enumerate(text.splitlines(),1))+'</div>'
        write(BASE/'reference/sources'/row['viewer'],page(row['path'],body,level=2,kind='기준 원문',wide=True))
    # The glossary reproduces every canonical definition, with exact source links.
    glossary=source_text('GLOSSARY.md').splitlines()
    definitions=[]; current=None
    for line,s in enumerate(glossary,1):
        if s.startswith('### '):
            if current: definitions.append(current)
            current={'title':s[4:],'line':line,'lines':[]}
        elif s.startswith('## '):
            if current: definitions.append(current); current=None
        elif current: current['lines'].append(s)
    if current: definitions.append(current)
    body='<h1>공통 용어 전부 찾아보기</h1><p>현행 GLOSSARY.md의 정의 '+str(len(definitions))+'개를 그대로 회수했습니다. 수업의 풀이와 구별되는 원문 정의이며, 검색어는 제목과 본문에 함께 적용됩니다.</p><label for="glossary-search">찾을 말</label><input id="glossary-search" class="glossary-search" data-glossary-search type="search"><p data-search-status class="search-status" aria-live="polite">'+str(len(definitions))+'개 용어</p>'
    for i,d in enumerate(definitions,1):
        # Original Markdown hyperlinks remain textual in the source viewer; glossary links back there.
        plain='\n'.join(d['lines']).strip()
        plain=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',plain)
        body+=f'<section class="glossary-entry" id="term-{i}"><h2>{escape(d["title"])}</h2>'+render(plain,sources,'sources/')+f'<p class="source"><a href="sources/{sources["GLOSSARY.md"]["viewer"]}#L{d["line"]}">원문 {d["line"]}행</a></p></section>'
    write(BASE/'reference/0002-glossary.html',page('공통 용어 전부',body,kind='정본 용어집'))
    # Every source file has a declared teaching destination; tests also expose actual test methods.
    coverage=[]; rows=[]
    for row in data['files']:
        nums=course.coverage(row['path'])
        if not nums: raise ValueError('Unmapped file: '+row['path'])
        mapping=' · '.join(f'<a href="../lessons/{course.LESSONS[n-1]["filename"]}">{n:02}강</a>' for n in nums)
        desc=course.file_purpose(row['path'])
        tests=sum(s['name'].split('.')[-1].startswith('test_') for s in row['symbols'])
        rowhtml=f'<tr data-catalog-row><td><a href="sources/{row["viewer"]}">{escape(row["path"])}</a></td><td>{escape(desc)}<small class="muted">{escape(row["doc"].splitlines()[0] if row["doc"] else "")}</small></td><td>{mapping}</td><td>{row["lines"]}줄'+(f' · 시험 {tests}개' if tests else '')+'</td></tr>'
        rows.append(rowhtml); coverage.append({'path':row['path'],'lessons':nums,'purpose':desc,'test_methods':tests})
    body='<h1>전체 파일과 설명 위치</h1><p>기준 스킬의 추적 파일 '+str(len(rows))+'개 모두를 수업에 연결했습니다. 본문은 역할과 경계 중심으로 설명하며, 함수의 모든 행을 줄별로 해설했다는 뜻은 아닙니다. 각 파일을 열면 원문 전부와 Python 클래스·함수 위치를 볼 수 있습니다. 시험 수는 소스에 정의된 test_ 메서드 수로, 실행 결과가 아닙니다.</p><label for="catalog-search">파일·기능 검색</label><input id="catalog-search" class="glossary-search" data-catalog-search type="search"><p data-catalog-count aria-live="polite">'+str(len(rows))+'개 파일</p><div class="table-wrap"><table><thead><tr><th>원문</th><th>이 파일에서 찾을 책임</th><th>설명</th><th>규모</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'
    body+='<p><a href="sources/manifest.json">파일별 SHA-256과 기준 기록</a> · <a href="coverage.json">전파일 대응 데이터</a></p>'
    write(BASE/'reference/0007-catalog.html',page('전체 파일과 설명 위치',body,kind='전파일 색인',wide=True))
    write(BASE/'reference/coverage.json',json.dumps(coverage,ensure_ascii=False,indent=2)+'\n')
    intro='<h1>do-math 전체를 이해하기</h1><p class="lead">질문 하나가 과제와 증거가 되고, 다음 연구로 이어지는 과정을 배웁니다.</p>'+render(course.INTRO,sources,'reference/sources/')
    intro+='<p><a class="start-link" href="lessons/'+course.LESSONS[0]['filename']+'">01강부터 읽기 →</a></p><div class="cards">'+''.join(cards)+'</div><h2>곁에 두고 찾는 자료</h2><ul>'
    for filename,title,_ in course.REFERENCES: intro+='<li><a href="reference/'+filename+'">'+escape(title)+'</a></li>'
    intro+='<li><a href="reference/0002-glossary.html">공통 용어 '+str(len(definitions))+'개</a></li><li><a href="reference/0007-catalog.html">전체 파일 '+str(len(rows))+'개와 원문</a></li><li><a href="reference/0009-scenarios.html">사건에 따라 상태 비교하기</a></li></ul><p class="source">'+escape(data['skill_commit'].replace('\n',' · '))+'</p>'
    write(BASE/'index.html',page('do-math 전체를 이해하기',intro,level=0,kind='새 전체 과정'))
    print(json.dumps({'lessons':len(course.LESSONS),'glossary':len(definitions),'source_files':len(rows),'draft_bytes':len(draft_text.encode('utf-8'))},ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['build','verify-source'])
    parser.add_argument('--draft',type=Path,help='write the review manuscript only when requested')
    args=parser.parse_args()
    if args.command=='build': build(args.draft)
    else: verify_source()
