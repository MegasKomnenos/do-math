# T14: 마지막 자리 확인(장 파일 전체 범위)
import re, os
root = r"C:\math\임시\주차함수_증명\장v2"
def T(f): return open(os.path.join(root, f), encoding='utf-8').read()
def cnt(f, pat):
    t = T(f); ms = list(re.finditer(pat, t))
    ln = [t[:m.start()].count('\n') + 1 for m in ms[:3]]
    print(f"  {f} /{pat}/ -> {len(ms)} lines {ln}")
for p in [r'\\mathfrak h_0', r'\\mathfrak P\^\{\\mathrm\{pair\}\}', r'E\^\{\(k-1\)\}', r'(?<![A-Za-z\\])E_k\b', r'\\mathfrak n_J', r'\\mathfrak N=\\lfloor|\\mathfrak N:=\\lfloor|\\mathcal N:=\\lfloor0\.35', r'Y_1']:
    cnt("장6.md", p)
for p in [r'I=8|I:=8|i<8|i<I', r'\\hat\{?\\varsigma', r'\\mathcal T_N', r'\\mathfrak z_\+']:
    cnt("장8.md", p)
for p in [r'\\mathfrak V\b', r'\\mathfrak I_i', r'\\mathrm\{ex\}', r'\\mathfrak V_\\ast']:
    cnt("장5B.md", p); cnt("부록D_장5B.md", p)
for p in [r's\^\{\\mathrm\{cf\}\}', r'(?<![A-Za-z\\])s(?![A-Za-z_^])', r'\\mathrm\{Bor\}\(']:
    cnt("장11.md", p)
for p in [r'\\mathrm\{regen\}', r'\\mathsf\{FS\}', r'\\mathfrak q_m', r'\\mathfrak y\^', r'\\mathrm\{T1\}_n|\\mathrm\{Ld\}']:
    cnt("장9.md", p)
cnt("장2.md", r'\\mathcal R_k|\\mathcal G_k|q_\{d,k\}')
cnt("장8.md", r'격자점')
cnt("장4.md", r'(?<![A-Za-z\\{])N(?![A-Za-z])')
cnt("장5A.md", r'(?<![A-Za-z\\{])N(?![A-Za-z])')
cnt("장5B.md", r'(?<![A-Za-z\\{])N(?![A-Za-z])')
cnt("장3.md", r'(?<![A-Za-z\\{])N(?![A-Za-z])')
cnt("장2.md", r'(?<![A-Za-z\\{])N(?![A-Za-z])')
