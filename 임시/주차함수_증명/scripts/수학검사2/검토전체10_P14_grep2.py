# -*- coding: utf-8 -*-
# 2차 문맥 조회: 장 파일과 기록 원문에서 장부 7절·2절의 주장을 대조할 자리를 찾는다.
import re, io, os, glob
base = r"C:\math\임시\주차함수_증명\장v2"
REC = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"

def grep(files, pat, width=120, maxhits=5, root=base):
    rx = re.compile(pat)
    print(f"=== {pat}  in {files}")
    n = 0
    for f in files:
        p = os.path.join(root, f)
        if not os.path.exists(p):
            print("  (파일 없음)", p); continue
        for i, line in enumerate(io.open(p, encoding='utf-8', errors='replace'), 1):
            for m in rx.finditer(line):
                s = max(0, m.start()-width//2); e = min(len(line), m.end()+width//2)
                print(f"  {os.path.basename(f)}:{i}: …{line[s:e].strip()}…")
                n += 1
                if n >= maxhits: return
                break
    if n == 0: print("  (없음)")

def rec(prefix):
    d = glob.glob(os.path.join(REC, prefix + '*'))
    return d[0] if d else None

def rgrep(prefix, pat, files=('exposition.md',), maxhits=4, width=140):
    d = rec(prefix)
    if not d: print("기록 없음", prefix); return
    paths = []
    for f in files:
        paths += glob.glob(os.path.join(d, f))
    grep(paths, pat, width=width, maxhits=maxhits, root='')

print("##### 장 파일")
grep(['장6.md', '장8.md', '장9.md', '장11.md'], r'\\mathrm\{Bor\}_\{?\\le', maxhits=8)
grep(['장6.md'], r'\\mathsf s_\{?\\mathrm\{?B', maxhits=3)
grep(['장7A.md', '장7B.md'], r'\\mathfrak a\^\{?\\circ', maxhits=3)
grep(['장6.md', '장7A.md', '장7B.md'], r'0\.765\d*', maxhits=8)
grep(['장6.md', '장10.md', '장11.md'], r'50\.6\d*', maxhits=8)
grep(['장10.md'], r'0\.5319\d*|\\mathsf f_1', maxhits=4)
grep(['장9.md', '장11.md'], r'1\.206\d*', maxhits=4)
grep(['장6.md', '장7B.md', '장8.md'], r'0\.307', maxhits=4)
grep(['장5B.md'], r'0\.71216|7\.7148', maxhits=4)
grep(['장11.md'], r'n\^\\(sharp|flat|circ)_k|n\^\{\\(sharp|flat|circ)\}_k', maxhits=6)
grep(['장11.md'], r'(?<![A-Za-z\\])e_n|B_\{n,|(?<![A-Za-z\\])T\(x\)|(?<![A-Za-z\\{])T\(', maxhits=8)
grep(['장8.md'], r'착지 환경', maxhits=3)
grep(['장4.md'], r'(?<![A-Za-z\\{])N(?![A-Za-z}])', maxhits=5)
grep(['장2.md', '장3.md'], r'(?<![A-Za-z\\{])N(?![A-Za-z}])', maxhits=5)
grep(['장6.md'], r'\\Pi_j\(y\)|\\Pi_j\(t\)|\\Pi_j:=|\\Pi_j\(y\):=', maxhits=4)
grep(['장5A.md'], r'(?<![A-Za-z\\{])N(?![A-Za-z}])', maxhits=8)

print("##### 기록 원문")
rgrep('r5bbc534', r'D_N\(s\)', maxhits=3)
rgrep('r5bbc534', r'A_N\s*[:=]|0\.798|3\.2R', maxhits=4)
rgrep('r5bbc534', r'\\lambda_q|\\omega_N\(r\)', maxhits=3)
rgrep('re71a735', r'D_1\s*[:=]|\\lfloor\s*0\.6', maxhits=3)
rgrep('re71a735', r'\\theta_0|I_1\s*[:=]', maxhits=4)
rgrep('r030ffae', r'Q\^\{?\\mathrm\{low\}\}?_c|Q\^\{low\}_c|Q\^\{\\rm low\}', maxhits=3)
rgrep('r030ffae', r'G\s*:?=\s*\\lfloor|G\s*:?=\s*300|L_0\s*:?=', maxhits=5)
rgrep('r8456f59', r'\\kappa_N\s*[:=]|B_N\s*[:=]', maxhits=4)
rgrep('rfc69320', r'C_\\Psi|1\.6780525|\\Psi_\\flat', maxhits=4)
rgrep('rb6a2cd0', r'r_S\s*[:=]|W_S\s*[:=]|U_k\(s\)\s*[:=]|T\(s\)\s*[:=]', maxhits=6)
rgrep('r3d0856b', r'c_m\s*[:=]|c_m\s*=\s*2', maxhits=4)
rgrep('r7e03176', r'\\psi\(a\)\s*[:=]|16\.54|k\\ge\s*4000|k\s*\\geq\s*4000', maxhits=5)
rgrep('r051bfe1', r'0\.307|\\delta_N\s*[:=]|\\kappa_N\s*[:=]', maxhits=5)
rgrep('ra88ba51', r'n-\\ell-2|n-l-2', maxhits=3)
rgrep('r2fe0259', r'q_F\s*[:=]|\\pi_2\(F\+1\)', maxhits=3)
rgrep('r8a9b11e', r's_0\s*[:=]|0\.71216|R_\\ell\s*[:=]|\\lfloor\s*6', maxhits=5)
rgrep('r2ec875c', r'\\mathfrak m\(n\)|170|m\^\{3/2\}\+9m', maxhits=4)
rgrep('rae1f209', r'L_\*\(6668\)|1\.206|c_m\s*[:=]', maxhits=4)
rgrep('r1aa0be6', r'\\mathcal R\(n,d\)\s*[:=]|e\^d', maxhits=3)
rgrep('r42d9a17', r'w_r\s*[:=]|\\delta_\{n,r\}\s*[:=]', maxhits=3)
rgrep('r98fb348', r'P_2\(c\)\s*[:=]', maxhits=2)
rgrep('rad00a59', r'\\rho_t\s*[:=]|U\(x\)\s*[:=]', maxhits=3)
