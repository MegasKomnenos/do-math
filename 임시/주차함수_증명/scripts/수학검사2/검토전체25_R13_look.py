# -*- coding: utf-8 -*-
# 자리 보기 도구: 장부 행·장 파일 행의 문맥, 고정 문자열 건수.
import io, re, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
base = 'C:/math/임시/주차함수_증명/'
J = io.open(base + '장부_v2.md', encoding='utf-8').read().split('\n')
def jl(n, pat, w=130):
    l = J[n - 1]; p = l.find(pat)
    print('장부', n, '|', ('NOT FOUND ' + pat) if p < 0 else l[max(0, p - w):p + len(pat) + w]); print()
def ch(f, n, pat=None, w=110):
    L = io.open(base + '장v2/' + f + '.md', encoding='utf-8').read().split('\n')
    l = L[n - 1]
    if pat:
        p = l.find(pat); print(f, n, '|', ('NOT FOUND ' + pat) if p < 0 else l[max(0, p - w):p + len(pat) + w])
    else:
        print(f, n, '|', l[:2 * w])
    print()
def cnt(pat, files=None):
    r = {}
    for p in sorted(glob.glob(base + '장v2/*.md')):
        name = __import__('os').path.basename(p)[:-3]
        if files and name not in files: continue
        L = io.open(p, encoding='utf-8').read().split('\n')
        for i, l in enumerate(L, 1):
            if pat in l:
                r.setdefault(name, []).append(i)
    print('count', pat, {k: (len(v), v[:8]) for k, v in r.items()}); print()
def jcnt(pat, lo=1, hi=None):
    r = [i for i, l in enumerate(J, 1) if pat in l and i >= lo and (hi is None or i <= hi)]
    print('장부 count', pat, r[:12]); print()
for line in io.open(sys.argv[1], encoding='utf-8'):
    line = line.rstrip('\n')
    if not line.strip(): continue
    a = line.split('\t')
    if a[0] == 'jl': jl(int(a[1]), a[2], int(a[3]) if len(a) > 3 else 130)
    elif a[0] == 'ch': ch(a[1], int(a[2]), a[3] if len(a) > 3 and a[3] else None, int(a[4]) if len(a) > 4 else 110)
    elif a[0] == 'cnt': cnt(a[1], a[2].split(',') if len(a) > 2 else None)
    elif a[0] == 'jcnt': jcnt(a[1], int(a[2]) if len(a) > 2 else 1, int(a[3]) if len(a) > 3 else None)
