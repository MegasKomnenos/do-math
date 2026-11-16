# -*- coding: utf-8 -*-
# 정의 전 사용 후보: 1.2 전역 기호와 3절 낱말의 첫 출현 절이 장부의 정의 절보다 앞서는 자리를 찾는다(후보; 손 판단).
import re, glob, os, io
base = r"C:\math\임시\주차함수_증명"
order = {'장1.md':1,'장2.md':2,'장3.md':3,'장4.md':4,'장5A.md':5,'장5B.md':5,'장6.md':6,'장7A.md':7,'장7B.md':7,'장8.md':8,'장9.md':9,'장10.md':10,'장11.md':11}
files = sorted(glob.glob(os.path.join(base, "장v2", "장*.md")), key=lambda f: (order[os.path.basename(f)], os.path.basename(f)))

def norm(s):
    s = re.sub(r'\s+', '', s)
    s = s.replace('{', '').replace('}', '')
    s = s.replace('\\prime', "'").replace('\\ast', '*')
    s = s.replace('\\leq', '\\le').replace('\\geq', '\\ge')
    return s

# sections: list of (sec_tuple, sec_str, normalized_line, rawline, file, lineno)
lines = []
for f in files:
    cur = (order[os.path.basename(f)],); curs = str(cur[0])
    for i, line in enumerate(io.open(f, encoding='utf-8'), 1):
        m = re.match(r'^#{2,4} (\d+(?:\.\d+)*)', line)
        if m:
            curs = m.group(1); cur = tuple(int(x) for x in curs.split('.')); continue
        lines.append((cur, curs, norm(line), line, os.path.basename(f), i))

def sec_tuple(s):
    s = s.strip()
    m = re.match(r'(\d+(?:\.\d+)*)', s)
    return tuple(int(x) for x in m.group(1).split('.')) if m else None

def split_top(sym):
    parts = []; d = 0; cur = ''
    for ch in sym:
        if ch in '({[': d += 1
        if ch in ')}]': d -= 1
        if ch == ',' and d == 0:
            parts.append(cur); cur = ''
        else:
            cur += ch
    parts.append(cur)
    return parts

def strip_trailing_args(p):
    p = p.strip()
    while p.endswith(')'):
        d = 0
        for j in range(len(p)-1, -1, -1):
            if p[j] == ')': d += 1
            elif p[j] == '(':
                d -= 1
                if d == 0:
                    p = p[:j].strip(); break
        else:
            break
    return p

def keys_of(sym):
    out = []
    for p in split_top(sym):
        p = p.strip().strip('$').strip()
        p = re.sub(r':=.*$', '', p)
        p = strip_trailing_args(p)
        p = norm(p)
        if p and p not in ('\\dots', '\\cdots') and len(p) > 1:
            out.append(p)
    return out

jb = io.open(os.path.join(base, "장부_v2.md"), encoding='utf-8').read().split('\n')
print("######## 1.2 기호: 정의 절보다 앞선 출현 후보")
for i in range(48, 340):
    l = jb[i]
    if not l.startswith('| $'): continue
    cells = [c.strip() for c in l.strip().strip('|').split('|')]
    sym, defsec = cells[0], cells[3]
    # take the earliest 정의 절 listed
    secs = [sec_tuple(x) for x in re.findall(r'\d+\.\d+', defsec)]
    if not secs: continue
    dsec = min(secs)
    for k in keys_of(sym):
        pat = re.compile(r'(?<![A-Za-z\\_^])' + re.escape(k) + r'(?![A-Za-z])')
        hits = [(sec, secs_, raw, fn, ln) for (sec, secs_, nl, raw, fn, ln) in lines if pat.search(nl)]
        early = [h for h in hits if h[0][:2] < dsec[:2]]
        if early:
            ex = early[0]
            print(f"[L{i+1}] {sym[:50]} 정의 {defsec} | key {k} | 앞선 출현 {len(early)}곳, 첫: {ex[3]}:{ex[4]} (절 {ex[1]}): …{ex[2].strip()[:140]}…")

print("######## 3절 낱말: 첫 정의 절보다 앞선 출현 후보")
for i in range(507, 737):
    l = jb[i]
    if not l.startswith('|'): continue
    cells = [c.strip() for c in l.strip().strip('|').split('|')]
    if len(cells) < 4: continue
    words, defsec = cells[0], cells[2]
    if '—' in defsec or '부록' in defsec: continue
    secs = [sec_tuple(x) for x in re.findall(r'\d+(?:\.\d+)?', defsec)]
    secs = [s for s in secs if s]
    if not secs: continue
    dsec = min(secs)
    for w in re.split(r'[,;·]\s*', words):
        w = w.strip()
        w = re.sub(r'\(.*?\)', '', w).strip()
        if not w or '$' in w or len(w) < 2: continue
        pat = re.compile(re.escape(w))
        hits = [(sec, secs_, raw, fn, ln) for (sec, secs_, nl, raw, fn, ln) in lines if pat.search(raw)]
        early = [h for h in hits if h[0][:len(dsec)] < dsec and h[0][0] != 1]
        if early:
            ex = early[0]
            print(f"[L{i+1}] 「{w}」 정의 {defsec} | 앞선 출현 {len(early)}곳(1장 제외), 첫: {ex[3]}:{ex[4]} (절 {ex[1]}): …{ex[2].strip()[:120]}…")
