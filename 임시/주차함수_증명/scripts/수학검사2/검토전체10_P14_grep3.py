# -*- coding: utf-8 -*-
import re, io, os
base = r"C:\math\임시\주차함수_증명\장v2"
def grep(files, pat, width=140, maxhits=6, root=base):
    rx = re.compile(pat); print("===", pat, files); n = 0
    for f in files:
        for i, line in enumerate(io.open(os.path.join(root, f), encoding='utf-8'), 1):
            m = rx.search(line)
            if m:
                s = max(0, m.start()-width//2); e = min(len(line), m.end()+width//2)
                print(f"  {f}:{i}: …{line[s:e].strip()}…"); n += 1
                if n >= maxhits: return
    if n == 0: print("  (없음)")
grep(['장5A.md', '장5B.md'], r'\\mathcal I_[a-zA-Z{]')
grep(['장5B.md'], r'F_1|F_3|F_4', maxhits=4)
grep(['장5A.md'], r'(?<![A-Za-z\\{])F(?![A-Za-z}_^])', maxhits=4)
grep(['장2.md'], r'\\mathcal I_', maxhits=2)
def show(f, lo, hi):
    L = io.open(os.path.join(base, f), encoding='utf-8').read().split('\n')
    print("=====", f, lo, hi)
    for i in range(lo-1, hi): print(i+1, ':', L[i][:300])
show('장6.md', 298, 306)
show('장10.md', 492, 503)
grep(['장4.md'], r'\\Phi\(T|\\Phi\(\\mathfrak Y\)|\\Phi:=|\\Phi\^\{\\mathrm\{aux\}\}:=', maxhits=4)
grep(['장2.md'], r'e_n\s*(:=|=)', maxhits=3)
grep(['장2.md'], r'random walk|renewal function|exponential formula|critical Boltzmann', maxhits=4)
grep(['장1.md'], r'linear probing|parking function', maxhits=3)
grep(['장3.md'], r'log-concave', maxhits=2)
grep(['장10.md'], r'h-transform', maxhits=2)
grep(['장5A.md'], r'Fortuin', maxhits=2)
# 장부 안의 낡은 절 번호 흔적
jb = r"C:\math\임시\주차함수_증명"
grep(['장부_v2.md'], r'5\.7(?![\d])', maxhits=12, root=jb)
grep(['장부_v2.md'], r'(?<![\d.])5\.6(?![\d])', maxhits=20, root=jb)
grep(['장부_v2.md'], r'명제 U·X|명제 X', maxhits=6, root=jb)
grep(['장부_v2.md'], r'정리 4\.5|정리 5\.28|정리 2\.14', maxhits=8, root=jb)
