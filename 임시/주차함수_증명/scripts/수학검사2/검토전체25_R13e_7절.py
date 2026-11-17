# -*- coding: utf-8 -*-
# 7절 첫째 열(이 글의 글자)의 $…$ 토큰마다 머리(글자체 명령+바탕 글자 또는 로마체 이름, 위첨자 꼬리표)를 뽑아
# 1.1·1.2 첫째 열의 머리 집합과 견주고, 장 파일(본문·부록 D)에 그 머리가 고정 문자열로 있는지 센다.
# 후보만 찍는다 — 판단은 원문 행을 열어 한다.
import sys, io, re, glob, os, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
def load(n,p):
    spec = importlib.util.spec_from_file_location(n,p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
t12 = load('t12','scripts/수학검사2/검토전체25_R13e_표12.py')
BS=chr(92)
def heads(tok):
    # 토큰 안의 '머리'들: \mathrm{name}(^{\mathrm{tag}})?, \math(cal|frak|sf) X (^{\mathrm{tag}}|^\sym)?, \mathsf{NAME}
    out=[]
    for m in re.finditer(re.escape(BS)+r'(mathrm|mathcal|mathfrak|mathsf|mathbb)\s*(\{[A-Za-z0-9]+\}|\s[A-Za-z])', tok):
        h = BS+m.group(1)+(m.group(2) if m.group(2).startswith('{') else ' '+m.group(2).strip())
        rest = tok[m.end():]
        sup = re.match(r'\s*\^\s*(\{'+re.escape(BS)+r'mathrm\{[A-Za-z]+\}\}|'+re.escape(BS)+r'[A-Za-z]+|\{'+re.escape(BS)+r'[A-Za-z]+\}|\{'+re.escape(BS)+r'mathrm [A-Za-z]\})', rest)
        out.append((h, sup.group(0).strip() if sup else ''))
    return out
def toks(cell): return re.findall(r'\$([^$]+)\$', cell)
# 1.2·1.1 머리
H12=set(); H12full=set()
for ln,c in t12.table(49,288)+t12.table(26,41):
    for t in toks(c[0]):
        for h,s in heads(t):
            H12.add(h); H12full.add((h,s))
ALL = {os.path.basename(f)[:-3]: io.open(f,encoding='utf-8').read() for f in glob.glob('장v2/*.md')}
BODY = {k:v for k,v in ALL.items() if not k.startswith('부록A') and not k.startswith('부록B') and not k.startswith('부록C')}
def count_body(s): return sum(v.count(s) for v in BODY.values())
seen=set()
for ln,c in t12.table(1243,1441):
    for col in (0,):
        for t in toks(c[col]):
            for h,s in heads(t):
                if h.startswith(BS+'mathrm') and h in (BS+'mathrm{low}',BS+'mathrm{up}',BS+'mathrm{src}'): continue
                key=(h,s)
                if key in seen: continue
                seen.add(key)
                in12 = h in H12; in12f = key in H12full
                nb = count_body(h); alt = h.replace(' ','{',1)+'}' if ' ' in h else h
                nb2 = count_body(alt) if alt!=h else 0
                if not in12 or (nb+nb2)==0 or not in12f:
                    print('%d행: 머리 %s%s — 1.1·1.2에 %s(위첨자까지 %s); 본문·부록 D %d건(+중괄호 철자 %d건); 토큰 $%s$'%(ln,h,s,'있음' if in12 else '없음','있음' if in12f else '없음',nb,nb2,t[:70]))
