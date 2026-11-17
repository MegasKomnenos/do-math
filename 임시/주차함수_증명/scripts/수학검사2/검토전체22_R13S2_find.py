# 고정 문자열을 장 파일별로 세고(장 단위 합산), 필요하면 자리(행·절·앞뒤 글)를 보여 준다.
# 사용: python -I 검토전체22_R13S2_find.py [-v N] [-c W] [-f 파일머리] 문자열...
import sys, io, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = r"C:/math/임시/주차함수_증명/장v2/"
FILES = ["장1","장2","부록D_장2","장3","부록D_장3","장4","부록D_장4","장5A","장5B","부록D_장5A","장6","장7A","장7B","부록D_장7A","부록D_장7B","장8","부록D_장8","장9","부록D_장9","장10","부록A","부록B","부록C"]
def chap(f):
    m = re.search(r'장(\d+)', f)
    return m.group(1) if m else f
def load(f):
    return open(W+f+".md", encoding='utf-8').read().split('\n')
def main():
    a = sys.argv[1:]; v = 0; cw = 70; only = None
    while a and a[0] in ('-v','-c','-f'):
        if a[0]=='-v': v = int(a[1])
        elif a[0]=='-c': cw = int(a[1])
        else: only = a[1]
        a = a[2:]
    keys = a
    tot = {}
    for f in FILES:
        if only and not f.startswith(only): continue
        L = load(f); sec = ''; hits = []
        for i, s in enumerate(L):
            m = re.match(r'^#{2,4} (\S+)', s)
            if m: sec = m.group(1)
            for k in keys:
                p = s.find(k)
                while p >= 0:
                    hits.append((i+1, sec, s, p, k)); p = s.find(k, p+1)
        if hits:
            tot.setdefault(chap(f), []).append((f, len(hits)))
            if v:
                seen = 0
                for (ln, sec, s, p, k) in hits:
                    if seen >= v: break
                    seen += 1
                    print(f"  {f}:{ln} [{sec}] …{s[max(0,p-cw):p+len(k)+cw]}…")
    print(' | '.join(f"{c}: " + ','.join(f"{f}={n}" for f, n in fs) for c, fs in tot.items()) or 'NONE')
main()
