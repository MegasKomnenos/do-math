# -*- coding: utf-8 -*-
# 특정 글자의 출현을 장 파일에서 찾아 짧은 문맥을 보인다(손 판단용).
import re, io, os, sys
base = r"C:\math\임시\주차함수_증명\장v2"
def grep(files, pat, width=110, maxhits=6):
    rx = re.compile(pat)
    print(f"=== {pat}  in {files}")
    n = 0
    for f in files:
        for i, line in enumerate(io.open(os.path.join(base, f), encoding='utf-8'), 1):
            for m in rx.finditer(line):
                s = max(0, m.start()-width//2); e = min(len(line), m.end()+width//2)
                print(f"  {f}:{i}: …{line[s:e].strip()}…")
                n += 1
                if n >= maxhits: return
    if n == 0: print("  (없음)")

grep(['장5A.md'], r'\\mathrm\{cb\}_\{?[A-Za-z]', maxhits=12)
grep(['장5A.md'], r'\$N\$|N\\ge|N\+1|\\binom\{2N\}', maxhits=8)
grep(['장10.md'], r'가족 \$F\$|F\\in|_F\b|\$F\$', maxhits=8)
grep(['장2.md'], r'\\mathcal G_\{[a-z],', maxhits=4)
grep(['장5A.md'], r'\\mathcal G_\{[a-z],', maxhits=4)
grep(['장4.md'], r'\\mathfrak S', maxhits=8)
grep(['장3.md'], r'\\mathsf P', maxhits=4)
grep(['장11.md'], r'\\mathrm\{Bor\}', maxhits=4)
grep(['장11.md'], r'\\mathfrak P', maxhits=4)
grep(['장11.md'], r'\\mathcal Z', maxhits=4)
grep(['장11.md'], r'\\mathrm\{Stays\}[^^]', maxhits=4)
grep(['장11.md'], r'\\mathrm\{Stays\}', maxhits=6)
grep(['장8.md'], r'\^\{?\\sigma\}?', maxhits=6)
grep(['장7A.md', '장7B.md'], r'A\^\{?\\sigma', maxhits=4)
grep(['장7A.md', '장7B.md'], r'\\mathcal N_\{?(\\ell|k)', maxhits=4)
grep(['장10.md'], r'\\mathrm\{Bor\}\^\{\*', maxhits=3)
grep(['장10.md'], r'\\pi\^0', maxhits=3)
grep(['장10.md'], r'\\pi_\{?[A-Za-z]', maxhits=4)
grep(['장7A.md', '장7B.md'], r'\\pi_\{?[A-Za-z]', maxhits=4)
grep(['장4.md'], r'(?<![A-Za-z\\])m(?![A-Za-z])', maxhits=6)
grep(['장5A.md', '장5B.md'], r'\\eta(?![A-Za-z])', maxhits=6)
grep(['장10.md'], r'\\mathfrak s\^\{\\mathrm\{low\}\}', maxhits=4)
grep(['장7A.md', '장7B.md'], r'(?<![\\A-Za-z{])D_k', maxhits=6)
grep(['장10.md'], r'(?<![A-Za-z\\{])T(?![A-Za-z}])', maxhits=8)
grep(['장4.md'], r'(?<![A-Za-z\\])q(?![A-Za-z])', maxhits=4)
grep(['장5A.md'], r'(?<![A-Za-z\\:])X(?![A-Za-z-])', maxhits=4)
grep(['장6.md'], r'(?<![A-Za-z\\:])X(?![A-Za-z-])', maxhits=4)
grep(['장11.md'], r'\\Omega', maxhits=6)
grep(['장11.md'], r'\\mathcal Y', maxhits=4)
grep(['장11.md'], r'\\mathfrak R', maxhits=4)
grep(['장11.md'], r'\\mathfrak a', maxhits=6)
grep(['장11.md'], r'\\mathsf Q|\\mathsf W', maxhits=6)
grep(['장11.md'], r'\\mathcal I_k|\\mathrm\{DD\}', maxhits=6)
