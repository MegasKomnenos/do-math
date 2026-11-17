# R13: 장부 1.1·1.2의 「쓰이는 장」 열을 장 파일에서 고정 문자열 검색으로 다시 센다(안내용 — 결과는 손으로 확인한다).
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
files = {1:['장1.md'],2:['장2.md'],3:['장3.md'],4:['장4.md'],5:['장5A.md','장5B.md'],6:['장6.md'],7:['장7A.md','장7B.md'],8:['장8.md'],9:['장9.md'],10:['장10.md']}
text = {}
for ch, fl in files.items():
    text[ch] = ''.join(open(os.path.join(ROOT, '장v2', f), encoding='utf-8').read() for f in fl)
def norm(s):
    # 공백 제거, \, 과 , 통일
    return s.replace(' ', '').replace('\\,', '').replace('\\;', '').replace('\\!', '')
ntext = {ch: norm(t) for ch, t in text.items()}
rows = []
sec = None
for ln, line in enumerate(open(os.path.join(ROOT, '장부_v2.md'), encoding='utf-8'), 1):
    if line.startswith('### 1.1'):
        sec = '1.1'
    elif line.startswith('### 1.2'):
        sec = '1.2'
    elif line.startswith('### 1.3'):
        break
    if sec and line.startswith('| $'):
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if sec == '1.1':
            glyph, used = cells[0], cells[2]
        else:
            glyph, used = cells[0], cells[4]
        rows.append((ln, sec, glyph, used, cells))
def parse_used(u):
    u = u.strip()
    if u == '—':
        return set()
    if u.startswith('전 장'):
        return set(range(1, 11))
    s = set()
    for m in re.findall(r'\d+', u):
        s.add(int(m))
    return s
def forms(glyph):
    # $…$ 조각들을 뽑고, 첨자·인수를 떼어낸 핵을 만든다
    fs = re.findall(r'\$(.+?)\$', glyph)
    out = []
    for f in fs:
        f = f.strip()
        # ':=' 뒤는 버림
        f = f.split(':=')[0]
        for piece in re.split(r',\s*(?![^{]*\})', f):
            piece = piece.strip()
            if piece:
                out.append(piece)
    return out
def variants(p):
    v = {p}
    # 인수 괄호 떼기
    v.add(re.sub(r'\([^()]*\)$', '', p))
    # 아래첨자 떼기: X_{...} 또는 X_a
    v.add(re.sub(r'_\{[^{}]*\}$', '', p))
    v.add(re.sub(r'_[A-Za-z0-9\\]+$', '', p))
    # 위첨자·아래첨자 모두 떼기
    core = re.sub(r'(\^|_)(\{[^{}]*\}|[A-Za-z0-9\\]+)', '', p)
    v.add(core)
    # 중괄호 없는 한 글자 첨자 ↔ 중괄호
    v.add(re.sub(r'\^\{(\w)\}', r'^\1', p))
    v.add(re.sub(r'_\{(\w)\}', r'_\1', p))
    return {norm(x) for x in v if len(norm(x)) >= 2 or x in ('x', 'y', 'd', 'q', 'k', 'n', 'm', 't', 'r', 'i', 'j', 'u', 'v')}
print('행 수', len(rows))
for ln, sec, glyph, used, cells in rows:
    declared = parse_used(used)
    fs = forms(glyph)
    if not fs:
        continue
    found = set()
    detail = {}
    for ch in files:
        for p in fs:
            hit = False
            for v in variants(p):
                if len(v) < 2 and not re.fullmatch(r'\\?[a-zA-Z]', v):
                    continue
                if v in ntext[ch]:
                    hit = True
                    break
            if hit:
                found.add(ch)
                detail[ch] = p
                break
    extra = found - declared
    missing = declared - found
    if extra or missing:
        print(f'{ln} {glyph[:60]} | 선언 {sorted(declared)} | 검색 {sorted(found)} | 선언에 없음 {sorted(extra)} | 검색 안 됨 {sorted(missing)}')
