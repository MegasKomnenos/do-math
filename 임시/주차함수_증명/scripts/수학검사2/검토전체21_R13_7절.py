# R13: 장부 7절(기록 글자 대응)의 「이 글의 글자」가 1.1·1.2에 있거나 장 파일 본문에 있는지, 기록 식별자 집합이 부록 B·장 파일 인용과 같은지 본다.
import re, sys, io, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
lines = open(os.path.join(ROOT, '장부_v2.md'), encoding='utf-8').read().split('\n')
def section_rows(start_pat, end_pat):
    rows = []
    on = False
    for i, l in enumerate(lines, 1):
        if l.startswith(start_pat):
            on = True
            continue
        if on and l.startswith(end_pat):
            break
        if on and l.startswith('| $') or (on and l.startswith('| ') and '|' in l[2:] and not l.startswith('| 이 글') and not l.startswith('|---') and not l.startswith('| 글자') and not l.startswith('| 양 ') and not l.startswith('| (Q')):
            cells = [c.strip() for c in l.strip().strip('|').split('|')]
            rows.append((i, cells))
    return rows
def norm(s):
    return s.replace(' ', '').replace('\\,', '').replace('\\;', '').replace('\\!', '')
# 1.1·1.2·1.3 글자 셀 모음
glyph_text = ''
on = False
for l in lines:
    if l.startswith('## 1.'):
        on = True
    elif l.startswith('## 2.'):
        on = False
    if on:
        glyph_text += l + '\n'
glyph_norm = norm(glyph_text)
chap = ''
for f in sorted(glob.glob(os.path.join(ROOT, '장v2', '*.md'))):
    chap += open(f, encoding='utf-8').read()
chap_norm = norm(chap)
rows7 = section_rows('## 7.', '## 8.')
print('7절 행 수', len(rows7))
def core(tok):
    t = tok.strip()
    t = re.sub(r'\([^()]*\)$', '', t)          # 인수
    t = re.sub(r'\((.*)\)', '', t) if t.count('(') == 1 and t.endswith(')') else t
    return t
print('\n== 7절 「이 글의 글자」 가운데 1절(글자 사전)에도 장 파일에도 없는 토큰')
for ln, cells in rows7:
    if len(cells) < 4:
        continue
    first = cells[0]
    toks = re.findall(r'\$(.+?)\$', first)
    missing = []
    for t in toks:
        for piece in re.split(r',\s*(?![^{]*\})', t):
            p = norm(piece.strip())
            if not p or len(p) < 2:
                continue
            variants = {p, norm(core(piece))}
            # 첨자·장식 떼기
            variants.add(re.sub(r'(\^|_)(\{[^{}]*\}|\\?[A-Za-z0-9]+)$', '', p))
            found = any(v and (v in glyph_norm or v in chap_norm) for v in variants)
            if not found:
                missing.append(piece.strip())
    if missing:
        print(f'  행 {ln}: {missing}  | 기록 {cells[1][:60]}')
# 식별자 집합
id_re = re.compile(r'\[(r[0-9a-f]{7})\]')
ids7 = set()
for ln, cells in rows7:
    ids7 |= set(id_re.findall(cells[1])) if len(cells) > 1 else set()
B = open(os.path.join(ROOT, '장v2', '부록B.md'), encoding='utf-8').read()
idsB = set(re.findall(r'\br([0-9a-f]{7})\b', B))
idsB = {'r' + x for x in idsB}
ids_chap = set()
for f in glob.glob(os.path.join(ROOT, '장v2', '장*.md')) + glob.glob(os.path.join(ROOT, '장v2', '부록D_*.md')):
    ids_chap |= {'r' + x for x in re.findall(r'\br([0-9a-f]{7})\b', open(f, encoding='utf-8').read())}
ids12 = set(id_re.findall(glyph_text))
print('\n7절 식별자', len(ids7), '| 부록 B', len(idsB), '| 장·부록 D 인용', len(ids_chap), '| 1절', len(ids12))
print('7절에 있으나 부록 B에 없음:', sorted(ids7 - idsB))
print('부록 B에 있으나 7절에 없음:', sorted(idsB - ids7))
print('장·부록 D 인용에 있으나 부록 B에 없음:', sorted(ids_chap - idsB))
print('부록 B에 있으나 장·부록 D 인용에 없음:', sorted(idsB - ids_chap))
print('1절(글자 사전)에 있으나 부록 B에 없음:', sorted(ids12 - idsB))
# 2·3·4절의 식별자도
rest = '\n'.join(lines)
ids_all = set(id_re.findall(rest))
print('장부 전체에 있으나 부록 B에 없음:', sorted(ids_all - idsB))
