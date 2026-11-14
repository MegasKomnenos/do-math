"""md2pdf.py 수리 패치 2(2026-11-14): 진술 판정, 진술 블록 확장, 인라인 줄바꿈 문턱, 디스플레이 관계 기호 자리·정렬, 표 단계, 글꼴·CSS."""
import re, subprocess, ast
p = r"C:\math\도구\md2pdf.py"
s = open(p, encoding="utf-8").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)


# P1. 진술/증명 판정
rep('''                head = ch[1].content.strip()
                if PROOF_HEAD.match(head):          # 「정리 2.32의 증명.」은 증명이지 진술이 아니므로 증명 판정을 먼저 한다
                    t.attrJoin("class", "proof")
                elif STATEMENT_HEAD.match(head):
                    t.attrJoin("class", "thm")''',
    '''                head = ch[1].content.strip()
                # 「정리 2.32의 증명.」은 증명이지 진술이 아니므로 증명 판정을 먼저 한다. 다만 지위 표지 [증명됨; …]가 붙은 머리는
                # 제목에 「…의 증명 구조」가 들어 있어도 진술이다.
                if PROOF_HEAD.match(head) and not (STATEMENT_HEAD.match(head) and "[" in head):
                    t.attrJoin("class", "proof")
                elif STATEMENT_HEAD.match(head):
                    t.attrJoin("class", "thm")
                    thm_starts.append(i)''')

# P2. 진술 블록 확장
rep('''    tokens = md.parse(text, env)
    title = ""
    headings: list[dict] = []
    n = 0
    i = 0
    while i < len(tokens):''',
    '''    tokens = md.parse(text, env)
    title = ""
    headings: list[dict] = []
    thm_starts: list[int] = []
    n = 0
    i = 0
    while i < len(tokens):''')
rep('''        i += 1
    body = md.renderer.render(tokens, md.options, env)
    return body, title, headings
''',
    r'''        i += 1
    wrap_statement_blocks(tokens, thm_starts)
    body = md.renderer.render(tokens, md.options, env)
    return body, title, headings


# 진술 문단 뒤에 빈 줄로 떨어져 이어지는 항목 문단의 머리: (가)(나)…, (ㄱ)(ㄴ)…, (i)(ii)…, (a)(b)…, (1)(2)…, (A)(A⁺)…
ITEM_HEAD = re.compile(r"^\((?:[가-힣]|[ㄱ-ㅎ]|[ivx]+|[a-z]|\d+|[A-Z][′'⁺+*♯♭]*)\)")


def wrap_statement_blocks(tokens, thm_starts: list[int]) -> None:
    """진술 문단(paragraph_open에 class thm)에 이어지는 항목 문단과 디스플레이 수식을 <div class="thmblk">로 감싼다.
    원고는 긴 진술의 항목을 빈 줄로 나눈 별도 문단으로 적으므로, 문단마다 꾸미면 세로선이 머리 문단만 감싸고
    항목들은 선 밖의 보통 문단으로 보인다. 진술이 아닌 문단(증명, 설명)이 나오면 거기서 블록을 닫는다."""
    from markdown_it.token import Token

    def is_item_paragraph(j: int) -> bool:
        if tokens[j].type != "paragraph_open" or tokens[j].attrGet("class"):
            return False
        inline = tokens[j + 1]
        ch = [c for c in (inline.children or []) if not (c.type == "text" and c.content == "")]
        return bool(ch) and ch[0].type == "text" and bool(ITEM_HEAD.match(ch[0].content.lstrip()))

    inserts: list[tuple[int, str]] = []   # (토큰 위치, html)
    for start in thm_starts:
        j = start
        while tokens[j].type != "paragraph_close":
            j += 1
        end = j + 1                       # 블록 끝(배타). 진술 문단 바로 뒤부터 이어 붙일 수 있는 것을 센다
        k = end
        while k < len(tokens):
            if tokens[k].type == "math_block":
                k += 1
                end = k
                continue
            if is_item_paragraph(k):
                while tokens[k].type != "paragraph_close":
                    k += 1
                k += 1
                end = k
                continue
            break
        if end > j + 1:
            inserts.append((start, '<div class="thmblk">'))
            inserts.append((end, "</div>"))
    for pos, html_ in sorted(inserts, key=lambda t: t[0], reverse=True):
        tok = Token("html_block", "", 0)
        tok.content = html_ + "\n"
        tok.block = True
        tokens.insert(pos, tok)
''')

# CSS
rep('''.thm { margin: 0.9em 0 0.9em; padding: 0.15em 0 0.15em 0.9em; border-left: 2.5px solid #333; break-inside: avoid; }''',
    '''.thm { margin: 0.9em 0 0.9em; padding: 0.15em 0 0.15em 0.9em; border-left: 2.5px solid #333; break-inside: avoid; }
/* 항목 문단·디스플레이 수식까지 이어지는 긴 진술은 .thmblk가 블록 전체를 감싸고 세로선을 그린다. 안의 .thm은 선을 다시 긋지 않는다 */
.thmblk { margin: 0.9em 0 0.9em; padding: 0.15em 0 0.15em 0.9em; border-left: 2.5px solid #333; break-inside: avoid; }
.thmblk .thm { margin: 0; padding: 0; border-left: 0; break-inside: auto; }
.thmblk > p, .thmblk > .para { margin: 0.35em 0 0; }
.thmblk > .katex-display { margin: 0.6em 0 0.6em; }''')
rep('''#sheet { overflow-x: clip; }''',
    '''#sheet { overflow-x: clip; overflow-clip-margin: 6px; }   /* 클립 여유: 줄 끝 이탤릭 글자의 삐침이 잘리지 않게 */''')
rep('''em.lat, em:lang(en) { font-style: italic; text-emphasis: none; -webkit-text-emphasis: none; }  /* 로마자뿐인 강조(문헌 제목)는 기울임 */''',
    '''em.lat, em:lang(en) { font-style: italic; text-emphasis: none; -webkit-text-emphasis: none; font-family: "md2pdf-sym", "Times New Roman", "Noto Serif", var(--body); }  /* 로마자뿐인 강조(문헌 제목)는 기울임. 한글 글꼴에는 이탤릭이 없어 합성 기울임이 되므로 참 이탤릭이 있는 글꼴로 */''')
rep('''@page { size: ${paper}; }''',
    '''@page { size: ${paper}; }
/* 본문 글꼴에 없는 기호(위·아래 첨자 글자, ♭♯♮, ‴, ⋆, ∎, ⌈⌉, ⟺, ℓ, 수학 글자체)는 한 글꼴에서 가져온다.
   글꼴마다 다른 대체 글리프로 튀어 「P⁺ ⁺」처럼 벌어지거나 모양이 어긋나던 것을 막는다. */
@font-face { font-family: "md2pdf-sym"; src: local("Cambria Math"), local("CambriaMath"), local("Segoe UI Symbol");
  unicode-range: U+2070-209F, U+2034, U+2113, U+220E, U+22C6, U+2308-230B, U+27F5-27FF, U+1D400-1D7FF; }
@font-face { font-family: "md2pdf-sym"; src: local("Segoe UI Symbol"), local("SegoeUISymbol"), local("Cambria Math");
  unicode-range: U+266D-266F; }''')
rep('''  word-break: ${word_break}; line-break: strict; overflow-wrap: anywhere;''',
    '''  word-break: ${word_break}; line-break: strict; overflow-wrap: anywhere;
  text-spacing-trim: trim-all;   /* 「」·（）같은 전각 괄호의 글리프 안 여백을 잘라 「 순열 」처럼 벌어지지 않게 */''')
rep('''    css = Template(CSS).substitute({
        "font_body": opts.font_body,''',
    '''    css = Template(CSS).substitute({
        "font_body": '"md2pdf-sym", ' + opts.font_body,''')

# FIT_JS
rep('''  const kindAfter = b => {
    if (b.dataset.punctEnd === '1') return 'punct';''',
    '''  const kindAfter = b => {
    if (b.dataset.punctEnd === '1') return 'punct';
    if (b.dataset.relEnd === '1') return 'rel';''')
rep('''  const S = (...a) => new Set(a);''',
    '''  // 디스플레이 수식: 줄을 바꿀 때 관계 기호(=, ≤)는 줄 끝이 아니라 다음 줄 머리에 둔다(amsmath의 관례). KaTeX의 base 조각은
  // 관계 기호로 끝나므로 그 기호(와 뒤 공백)를 다음 base 머리로 옮기고, 앞 base에 「관계 자리」 표지를 남긴다.
  const relToNextLine = kh => {
    if (kh.dataset.relMoved === '1') return;
    kh.dataset.relMoved = '1';
    const bases = Array.from(kh.children).filter(isBase);
    for (let i = 0; i < bases.length - 1; i++) {
      const kids = Array.from(bases[i].children);
      let j = kids.length - 1;
      while (j >= 0 && (kids[j].classList.contains('strut') || kids[j].classList.contains('mspace'))) j--;
      if (j < 0 || !kids[j].classList.contains('mrel')) continue;
      const next = bases[i + 1];
      const strut = next.querySelector(':scope > .strut');
      const anchor = strut ? strut.nextSibling : next.firstChild;
      for (const m of kids.slice(j)) next.insertBefore(m, anchor);
      if (j > 0 && kids[j - 1].classList.contains('mspace')) kids[j - 1].remove();   // 관계 기호 앞 공백은 줄 끝에 남기지 않는다
      bases[i].dataset.relEnd = '1';
    }
  };
  const S = (...a) => new Set(a);''')
rep('''  // 1) 인라인 수식: 관계 기호와 \\allowbreak(목록 쉼표, 긴 숫자열) 뒤에서 줄을 바꾼다. 행 폭의 30%를 넘는 수식은 이항 기호·쉼표 뒤도
  //    연다(TeX는 이항 기호 뒤 줄바꿈도 허용한다). 그래도 한 묶음이 행 폭을 넘으면 어디서나 끊는다.
  for (const kh of document.querySelectorAll('.katex-html')) {
    if (kh.closest('.katex-display') || kh.closest('table')) continue;
    const box = kh.closest('p, li, dd, blockquote, div, h1, h2, h3, h4, h5, h6') || document.body;
    const avail = box.clientWidth;
    regroup(kh, S('rel', 'allow'));
    if (totalWidth(kh) > avail * 0.3) { splitAtPunct(kh); regroup(kh, S('rel', 'allow', 'bin', 'punct')); }
    if (maxGroup(kh) > avail) regroup(kh, S('any'));
  }''',
    '''  // 1) 인라인 수식. TeX은 관계 기호·이항 기호 뒤의 줄바꿈을 벌점으로 억제해, 식을 통째로 다음 줄로 옮겨도 행간 간격이 크게
  //    나빠지지 않으면 식 안에서 끊지 않는다. Chromium은 벌점이 없어 허용한 자리마다 낱말 사이와 같은 값으로 끊으므로,
  //    짧은 식까지 「d_i =」/「pos_i − a_i」로 갈라졌다. 그래서 행 폭의 1/5 이하인 식은 통째로 두고, 그보다 길면 관계 기호와
  //    \\allowbreak(목록 쉼표, 긴 숫자열) 뒤를, 행 폭의 45%를 넘으면 이항 기호·쉼표 뒤도 연다. 한 묶음이 행 폭을 넘으면 어디서나 끊는다.
  for (const kh of document.querySelectorAll('.katex-html')) {
    if (kh.closest('.katex-display') || kh.closest('table')) continue;
    const box = kh.closest('p, li, dd, blockquote, div, h1, h2, h3, h4, h5, h6') || document.body;
    const avail = box.clientWidth;
    regroup(kh, S());
    const w = totalWidth(kh);
    if (w > avail * 0.2) regroup(kh, S('rel', 'allow'));
    if (w > avail * 0.45) { splitAtPunct(kh); regroup(kh, S('rel', 'allow', 'bin', 'punct')); }
    if (maxGroup(kh) > avail) regroup(kh, S('any'));
  }''')
rep('''    k.style.whiteSpace = 'normal';
    splitAtPunct(kh);''',
    '''    k.style.whiteSpace = 'normal';
    relToNextLine(kh);
    // 여러 줄로 갈라진 식은 amsmath multline처럼 첫 줄을 왼쪽에, 마지막 줄을 오른쪽에 맞춘다(가운데 정렬된 조각이 떠 보이지 않게).
    kh.style.textAlign = 'left'; kh.style.textAlignLast = 'right';
    splitAtPunct(kh);''')
rep('''    for (const kh of tb.querySelectorAll('.katex-html')) regroup(kh, S('rel', 'allow'));
    if (!over()) continue;''',
    '''    for (const kh of tb.querySelectorAll('.katex-html')) regroup(kh, S());   // 표가 폭 안에 들면 칸 안 수식은 끊지 않는다
    if (!over()) continue;
    for (const kh of tb.querySelectorAll('.katex-html')) regroup(kh, S('rel', 'allow'));
    if (!over()) continue;''')
rep('''  for (const el of document.querySelectorAll('.thm')) {
    if (el.getBoundingClientRect().height > limit) el.style.breakInside = 'auto';
  }''',
    '''  for (const el of document.querySelectorAll('.thm, .thmblk')) {
    if (el.getBoundingClientRect().height > limit) el.style.breakInside = 'auto';
  }''')

open(p, "w", encoding="utf-8", newline="\n").write(s)
ast.parse(s)
fit = s[s.index('FIT_JS = r"""') + len('FIT_JS = r"""'):]
fit = fit[:fit.index('"""')]
r = subprocess.run(["node", "-e", "new Function('return ('+process.argv[1]+')'); console.log('js ok')", fit], capture_output=True, text=True)
print(r.stdout.strip(), r.stderr[:400])
print("patched")
