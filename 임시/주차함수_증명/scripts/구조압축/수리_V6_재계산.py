# -*- coding: utf-8 -*-
# 수리 U17 — 장부 1.2 「쓰이는 장」 재계산과 5절(장별 배정과 여유 글자) 재생성.
#  본문은 물결 4 체크포인트 3e8c5ae0의 장 파일 사본(_u17_chk/장v2; 부록 A·B·C 제외, 부록 D 조각은 그 장으로 센다).
#  글자 찾기: 1.2 첫 칸의 변형(쉼표로 나뉜 것)마다 「머리」(바탕 글자와 윗첨자 장식까지; 아래첨자·인수는 뗌)를 만들고
#    수식 안에서 그 머리가 글자 경계로 나타나는지 본다. 머리에 윗첨자가 없으면 뒤에 ^가 오는 자리는 세지 않는다(다른 행의 장식 변형).
#  --scan: 제안만 찍는다. --write: 1.2의 「쓰이는 장」 칸과 5절 행을 수리_U17_편집.apply로 바꾼다.
import glob
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from 수리_U17_편집 import apply  # noqa: E402

LEDGER = os.path.join(ROOT, '장부_v2.md')
WRITE = '--write' in sys.argv
ONLY5 = '--only5' in sys.argv  # 2026-11-17(21차 ZL 뒤): 1.2 「쓰이는 장」 칸은 손으로 채운 현행을 믿고 5절만 다시 만든다(1.2는 읽기만, 쓰지 않음)


def section(lines, start, end):
    a = next(i for i, l in enumerate(lines) if l.startswith(start))
    b = next((i for i, l in enumerate(lines) if i > a and l.startswith(end)), len(lines))
    return a, b


def rows(lines, a, b):
    out = []
    for i in range(a, b):
        l = lines[i]
        if l.startswith('| ') and not l.startswith('|---'):
            cells = [c.strip() for c in l.strip()[1:-1].split(' | ')]
            out.append((i, cells))
    return out


# ---------------------------------------------------------------- 본문
def chapter_of(fname):
    m = re.match(r'(?:부록D_)?장(\d+)[AB]?\.md$', fname)
    return int(m.group(1)) if m else None


texts = {}
CHK = next((a.split('=',1)[1] for a in sys.argv if a.startswith('--dir=')), '_v6_tree')  # V6: 장 파일 폴더(--dir=_v6_tree | _v6_chk)
for f in sorted(glob.glob(os.path.join(HERE, CHK, '장v2', '*.md'))):
    ch = chapter_of(os.path.basename(f))
    if ch is None:
        continue
    texts[ch] = texts.get(ch, '') + '\n' + io.open(f, encoding='utf-8').read()
MATH = re.compile(r'\$([^$]+)\$')
MATH_ALL = re.compile(r'\$\$(.+?)\$\$|\$([^$\n]+?)\$', re.S)   # 표시 수식($$…$$)을 먼저 잡아 인라인 수식과 어긋나지 않게 한다
BRACE1 = re.compile(r'\\(mathcal|mathfrak|mathsf|mathrm|mathbb)\{([A-Za-z])\}')


def norm_math(s):
    return BRACE1.sub(r'\\\1\2', s.replace(' ', ''))


math_by_ch = {ch: ' '.join(norm_math(m.group(1) or m.group(2)) for m in MATH_ALL.finditer(t)) for ch, t in texts.items()}

# ---------------------------------------------------------------- 머리 만들기
CMD = r'\\[A-Za-z]+'


def heads_of(glyph_cell):
    """첫 칸 「$…$, $…$」 또는 「$a, b$」에서 변형마다 (머리 정규식, 윗첨자 있음) 목록."""
    out = []
    for m in MATH.finditer(glyph_cell):
        inner = m.group(1).replace(' ', '')
        for variant in split_variants(inner):
            h = head(variant)
            if h:
                out.append(h)
    return out


def split_variants(s):
    parts, depth, buf = [], 0, ''
    for ch in s:
        if ch in '{(':
            depth += 1
        elif ch in '})':
            depth -= 1
        if ch == ',' and depth == 0:
            parts.append(buf)
            buf = ''
            continue
        buf += ch
    parts.append(buf)
    return [p for p in parts if p]


def head(v):
    """글자의 머리: 바탕(명령 또는 글자) + 윗첨자 장식. 아래첨자·인수·:= 뒤는 뗀다."""
    v = re.split(r':=|\\ge|\\le|>|<|=', v)[0]
    # 바탕
    m = re.match(r'(\\(?:mathrm|mathfrak|mathcal|mathsf|mathbb|widehat|bar|tilde)\{[^}]*\}|\\(?:mathrm|mathfrak|mathcal|mathsf|mathbb|widehat|bar|tilde) ?[A-Za-z]|\\[A-Za-z]+|[A-Za-z])', v)
    if not m:
        return None
    base = m.group(1)
    rest = v[m.end():]
    sup = ''
    while True:
        m2 = re.match(r'(\^(?:\{[^}]*\}|\\[A-Za-z]+|[A-Za-z0-9*′])|_(?:\{[^}]*\}|\\[A-Za-z]+|[A-Za-z0-9]))', rest)
        if not m2:
            break
        tok = m2.group(1)
        rest = rest[m2.end():]
        if tok.startswith('^'):
            sup += tok
    has_sub = '_' in v[m.end():m.end() + 1] or bool(re.match(r'(\^[^_]*)?_', v[m.end():]))
    pat = re.escape(base + sup)
    if re.fullmatch(r'[A-Za-z]', base):
        pat = r'(?<![A-Za-z\\])' + pat
    if not sup:
        pat += r'(?!\^)'
    pat += r'(?![A-Za-z])'
    if has_sub and not sup:
        pat += r'(?=_)'
    return (re.compile(pat), base + sup)


def base_patterns(glyph_cell):
    """바탕 글자(명령 또는 한 글자)만의 정규식: 어떤 장식으로도 이 바탕이 없는 장은 그 글자를 쓰지 않는다."""
    out = []
    for m in MATH.finditer(glyph_cell):
        for v in split_variants(norm_math(m.group(1))):
            mm = re.match(r'(\\(?:mathrm|mathfrak|mathcal|mathsf|mathbb)[A-Za-z]|\\(?:mathrm|mathfrak|mathcal|mathsf|mathbb)\{[^}]*\}|\\(?:widehat|bar|tilde)\{?\\?[A-Za-z]+\}?|\\[A-Za-z]+|[A-Za-z])', v)
            if mm:
                b = mm.group(1)
                out.append(re.compile((r'(?<![A-Za-z\\])' if b[0].isalpha() else '') + re.escape(b) + r'(?![A-Za-z])'))
    return out


def _is_weak(t):
    """더하는 쪽 근거가 못 되는 글자열: 명령(\\) 없이 세 글자 이하(m_1, t_0, D_k …)거나 장식 없는 한 글자·한 명령."""
    if re.fullmatch(r'\\?[A-Za-z]+', t) or re.fullmatch(r'\\(?:mathrm|mathfrak|mathcal|mathsf|mathbb)\{?[A-Za-z]\}?', t):
        return True
    return '\\' not in t and len(t) <= 3


def raw_tokens(glyph_cell):
    toks = []
    for m in MATH.finditer(glyph_cell):
        for v in split_variants(norm_math(m.group(1))):
            v = re.split(r':=', v)[0]
            toks.append(v)
            w = re.sub(r'\([^()]*\)$', '', v)
            if w and w != v:
                toks.append(w)
    return toks


def strict_tokens(glyph_cell, shared):
    """엄격한 글자열: 변형 그대로와 인수 괄호를 뗀 것. 약한 것과 다른 행도 가진 것(shared)은 뺀다."""
    toks = [t for t in set(raw_tokens(glyph_cell)) if t and not _is_weak(t) and t not in shared]
    return [re.compile((r'(?<![A-Za-z\\])' if t[0].isalpha() else '') + re.escape(t) + r'(?![A-Za-z^_])') for t in toks]


def def_chapters(sec):
    """정의 절 칸 「10.3($\\vartheta$), 10.6($\\vartheta_0$)」에서 장 번호만: 점 앞의 수."""
    return set(int(m) for m in re.findall(r'(?<![\d.$_{^])(\d+)\.\d', sec))


SHARED = set()   # 두 행 이상이 가진 글자열(인수를 뗀 꼴이 겹치는 것 — \pi_n 등); 장부를 읽은 뒤 채운다
# 수리자 판단으로 더하지 않는 장: 본문의 그 글자열이 1.3에 등록된 국소 글자(또는 국소 꼬리표)여서 전역의 쓰임이 아닌 자리
EXCLUDE_ADD = {
    '$\\vartheta, \\vartheta_0$': {6},                                   # 6.4 국소 $\vartheta_\xi(y)$의 $\xi=0$ 값
    '$\\mathcal Y_k(n), \\mathcal Y^{\\mathrm{LP}}_k(n)$': {7},         # 7.3 국소 표시 생성함수 $\mathcal Y_k$
    '$\\mathfrak l_m(t)$': {5},                                          # 5.2 국소 Laurent 계수 $\mathfrak l_m$
    '$\\mathrm{Lip}$': {7},                                              # 7장 부록 D 항목의 국소 $\mathrm{Lip}$
    '$\\mathrm{top}, \\mathrm{top}_\\pi$': {9},                          # 9.4 국소 $\upsilon_{\mathrm{top}}$
    '$(\\star)(n)$': {4},                                                # 4장의 식 꼬리표 $(\star)$
}


def used_chapters(glyph_cell, cur):
    """보수적 재계산: 현행 집합에서 바탕 글자조차 없는 장을 빼고, 엄격한 글자열이 보이는 장을 더한다."""
    base, strict = base_patterns(glyph_cell), strict_tokens(glyph_cell, SHARED)
    out = set()
    for ch, mt in math_by_ch.items():
        if ch in cur:
            if not base or any(p.search(mt) for p in base):
                out.add(ch)
        elif ch not in EXCLUDE_ADD.get(glyph_cell, set()) and any(p.search(mt) for p in strict):
            out.add(ch)
    return out


def fmt_chs(chs):
    return ', '.join(str(c) for c in sorted(chs)) if chs else '—'


def parse_chs(s):
    return set(int(x) for x in re.findall(r'\d+', s))


# ---------------------------------------------------------------- 장부 읽기
lines = io.open(LEDGER, encoding='utf-8').read().split('\n')
a11, b11 = section(lines, '### 1.1', '### 1.2')
a12, b12 = section(lines, '### 1.2', '### 1.3')
a3, b3 = section(lines, '## 3. ', '## 4. ')
a5, b5 = section(lines, '## 5. ', '## 6. ')
r11 = [(i, c) for i, c in rows(lines, a11, b11) if c[0] != '글자']
r12 = [(i, c) for i, c in rows(lines, a12, b12) if c[0].startswith('$')]
r3 = [(i, c) for i, c in rows(lines, a3, b3) if c[0] != '낱말']
r5 = [(i, c) for i, c in rows(lines, a5, b5) if c[0] != '장']

# ---------------------------------------------------------------- 쓰이는 장 재계산
_cnt = {}
for i, c in r12:
    for t in set(raw_tokens(c[0])):
        _cnt[t] = _cnt.get(t, 0) + 1
SHARED.update(t for t, n in _cnt.items() if n > 1)
col5_ops, col5_log = [], []
for i, c in (r12 if not ONLY5 else []):
    if len(c) < 7:
        col5_log.append(f'[칸 수 이상] 줄 {i+1}: {c[0][:50]}')
        continue
    defch = def_chapters(c[3])
    cur = parse_chs(c[4]) if c[4].strip() not in ('', '—') else set()
    if not cur and defch == {1}:
        continue  # 1장 글자의 빈 칸은 관례대로 둔다(5절은 1장 전역 글자를 모두 뺀다)
    new = used_chapters(c[0], cur) | (defch if defch != {1} else set())
    if new != cur:
        col5_log.append(f'{c[0][:60]:60s} 정의 {c[3][:12]:12s} 현행 {fmt_chs(cur):28s} → {fmt_chs(new)}' + ('   [정의 장 없음]' if defch and not (defch & new) else ''))
        c2 = list(c)
        c2[4] = fmt_chs(new)
        col5_ops.append(('set_row', '| ' + c[0] + ' |', '| ' + ' | '.join(c2) + ' |'))
print(f'== 1.2 「쓰이는 장」: 행 {len(r12)}, 바뀜 {len(col5_ops)}')
for l in col5_log:
    print('  ', l)

# ---------------------------------------------------------------- 5절 재생성
LAT_L = list('abcdefghijklmnopqrstuvwxyz')
LAT_U = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
GRK = ['\\alpha', '\\beta', '\\gamma', '\\delta', '\\epsilon', '\\varepsilon', '\\zeta', '\\eta', '\\theta', '\\vartheta', '\\iota', '\\kappa', '\\varkappa', '\\lambda', '\\mu', '\\nu', '\\xi', '\\pi', '\\varpi', '\\rho', '\\varrho', '\\sigma', '\\varsigma', '\\tau', '\\upsilon', '\\phi', '\\varphi', '\\chi', '\\psi', '\\omega',
       '\\Gamma', '\\Delta', '\\Theta', '\\Lambda', '\\Xi', '\\Pi', '\\Sigma', '\\Upsilon', '\\Phi', '\\Psi', '\\Omega']
RESERVED_PLAIN = {'a', 'b', 'c', 'e', 'h', 'l', 'o', 'O', 'P', 'Q', 'W', 'X', '\\delta', '\\Delta', '\\Sigma', '\\varpi', '\\zeta'}  # 6절(ζ는 함수 꼴 셋째 예외)
FONT = {'일반(이탤릭)': 'plain', '프락투어': 'mathfrak', '필기체': 'mathcal', '산세리프': 'mathsf'}


def base_font(col2):
    parts = col2.split('·')
    if len(parts) < 2:
        return None
    base, font = parts[0].strip(), parts[1].strip()
    if font not in FONT:
        return None
    if not re.fullmatch(r'\\?[A-Za-z]+', base):
        return None
    return base, FONT[font]


odd = []
glyphs12 = []  # (base, font, defch, usedchs)
for i, c in r12:
    bf = base_font(c[1])
    if bf is None:
        odd.append((i, c[0][:40], c[1][:40]))
        continue
    defch = def_chapters(c[3])
    used = parse_chs(c[4]) if c[4].strip() not in ('', '—') else set()
    newused = used if ONLY5 else (used_chapters(c[0], used) if not (not used and defch == {1}) else set())
    glyphs12.append((bf[0], bf[1], defch, newused | defch, c[0]))   # newused는 재계산 뒤의 「쓰이는 장」(빠진 장은 이미 뺀 것)
print(f'== 1.2 바탕 글자·글자체 칸을 못 읽은 행 {len(odd)}')
for o in odd:
    print('  ', o)
var_bases = set()
for i, c in r11:
    for m in MATH.finditer(c[0]):
        mm = re.match(r'\\?[A-Za-z]+', m.group(1).replace(' ', ''))
        if mm:
            var_bases.add(mm.group(0))
print('== 1.1 변수 바탕 글자:', sorted(var_bases))
ch1_bases = {(b, f) for b, f, d, u, g in glyphs12 if 1 in d}


def free_letters(ch):
    taken = set()
    for b, f, d, u, g in glyphs12:
        if ch in u or ch in d or 1 in d:
            taken.add((b, f))
    out = {}
    out['라틴 소문자'] = [x for x in LAT_L if x not in var_bases and x not in RESERVED_PLAIN and (x, 'plain') not in taken]
    out['라틴 대문자'] = [x for x in LAT_U if x not in var_bases and x not in RESERVED_PLAIN and (x, 'plain') not in taken]
    out['그리스'] = [x for x in GRK if x not in var_bases and x not in RESERVED_PLAIN and (x, 'plain') not in taken]
    out['필기체'] = ['\\mathcal ' + x for x in LAT_U if (x, 'mathcal') not in taken]
    out['프락투어'] = ['\\mathfrak ' + x for x in LAT_L + LAT_U if (x, 'mathfrak') not in taken]
    out['산세리프(명명 상수에만)'] = ['\\mathsf ' + x for x in LAT_L + LAT_U if (x, 'mathsf') not in taken and x not in ('P', 'Q', 'W', 'X')]   # 명제 이름의 바탕 글자는 어느 장에도 넣지 않는다(5절 머리말·6절)
    return out


def fmt_free(d):
    parts = []
    for k, v in d.items():
        parts.append(k + ': ' + (', '.join('$' + x + '$' for x in v) if v else '없음') + '.')
    return ' '.join(parts)


def first_ch(sec):
    m = re.search(r'(?<![\d.$_{^])(\d+)\.\d', sec) or re.search(r'\d+', sec)
    return int(m.group(1) if m.lastindex else m.group(0)) if m else None


# 낱말: 3절 첫 정의 절의 가장 앞 절
words_by_ch = {}
skipped_words = []
for i, c in r3:
    sec = c[2]
    if re.search(r'부록 D|^D\b|일반어', sec) or not re.search(r'\d', sec):
        skipped_words.append((c[0][:40], sec[:30]))
        continue
    ch = first_ch(sec)
    words_by_ch.setdefault(ch, []).append(c[0])
print('== 3절에서 어느 장에도 두지 않은 행:', skipped_words)
glyph_by_ch = {}
for i, c in r12:
    ch = first_ch(c[3])
    if ch is not None:
        glyph_by_ch.setdefault(ch, []).append(c[0])

ops5, log5 = [], []
for i, c in r5:
    ch = int(c[0])
    g = '; '.join(glyph_by_ch.get(ch, [])) or '없음'
    w = '; '.join(words_by_ch.get(ch, [])) or '없음'
    fr = fmt_free(free_letters(ch))
    new = f'| {ch} | {g} | {w} | {fr} |'
    if new != lines[i]:
        ops5.append(('set_row', f'| {ch} |', new))
        # 차이 요약
        def items(s):
            return set(x.strip() for x in s.split('; ') if x.strip())
        og, ow = items(c[1]), items(c[2])
        ng, nw = items(g), items(w)
        def letters(s):
            return set(re.findall(r'\$([^$]+)\$', s))
        ofr, nfr = letters(c[3]), letters(fr)
        log5.append(f'[5절 {ch}] 기호 +{sorted(ng-og)} -{sorted(og-ng)} | 낱말 +{sorted(nw-ow)} -{sorted(ow-nw)} | 여유 +{sorted(nfr-ofr)} -{sorted(ofr-nfr)}')
print(f'== 5절: 행 {len(r5)}, 바뀜 {len(ops5)}')
for l in log5:
    print('  ', l[:1200])

if WRITE:
    if not ONLY5:
        apply(LEDGER, col5_ops, region=('### 1.2', '### 1.3'))
    apply(LEDGER, ops5, region=('## 5. ', '## 6. '))
