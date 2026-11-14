import ast, subprocess
p = r"C:\math\도구\md2pdf.py"
s = open(p, encoding="utf-8").read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:60]); s = s.replace(old, new)
# CSS: text-spacing-trim은 이 글꼴(Noto Serif KR 가변판)에 효과가 없어(halt 특성 없음) 전각 낫표의 안쪽 여백을 직접 줄인다
rep('''  text-spacing-trim: trim-all;   /* 「」·（）같은 전각 괄호의 글리프 안 여백을 잘라 「 순열 」처럼 벌어지지 않게 */
''', '')
rep('''code { font-family: var(--mono);''',
'''/* 전각 낫표 「」『』는 글리프의 안쪽 절반이 비어 「 순열 」처럼 보인다. text-spacing-trim은 이 글꼴(halt 특성 없음)에 듣지 않으므로 여백을 직접 줄인다 */
.qo { margin-right: -0.38em; }
.qc { margin-left: -0.38em; }
code { font-family: var(--mono);''')
# 본문 글자(태그 밖, 코드 밖)의 낫표를 감싼다. 수식 치환 뒤에 적용해 .nb 결합 판정을 해치지 않는다.
rep('''def substitute_math(s: str, rendered: list[str]) -> str:''',
'''_TEXT_SEG = re.compile(r"(<code>.*?</code>|<[^>]+>)|([^<]+)", re.S)


def tighten_quotes(body: str) -> str:
    """본문 글자의 전각 낫표 「『를 .qo로, 」』를 .qc로 감싼다(태그·코드 안은 건드리지 않는다)."""
    def seg(m):
        if m.group(1) is not None:
            return m.group(1)
        t = m.group(2)
        if "「" not in t and "」" not in t and "『" not in t and "』" not in t:
            return t
        t = re.sub(r"[「『]", lambda q: f'<span class="qo">{q.group(0)}</span>', t)
        return re.sub(r"[」』]", lambda q: f'<span class="qc">{q.group(0)}</span>', t)
    return _TEXT_SEG.sub(seg, body)


def substitute_math(s: str, rendered: list[str]) -> str:''')
rep('''    body = substitute_math(body, rendered)
    for h in headings:''',
'''    body = tighten_quotes(substitute_math(body, rendered))
    for h in headings:''')
open(p, "w", encoding="utf-8", newline="\n").write(s); ast.parse(s); print("patched")
