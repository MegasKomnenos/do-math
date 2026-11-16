# T14: 남은 글자 자리 확인(파이썬 정규식; 셸의 역슬래시 변환을 피함)
import re, os
root = r"C:\math\임시\주차함수_증명\장v2"
def T(f): return open(os.path.join(root, f), encoding='utf-8').read()
ch = {k: T(k + ".md") for k in ["장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]}
def show(f, pat, w=70, n=2):
    t = ch[f] if f in ch else T(f)
    ms = list(re.finditer(pat, t))
    print(f"  {f} /{pat}/ -> {len(ms)}", end='')
    for m in ms[:n]:
        s = max(0, m.start() - w); print(f"\n     ...{t[s:m.end()+w]!r}", end='')
    print()
print("== Bor_le per chapter")
for f in ch: print(f, len(re.findall(r'\\mathrm\{Bor\}_\{?\\le', ch[f])), end=' | ')
print("\n== a^rho 11:", len(re.findall(r'\\mathfrak a\^\{?\\rho', ch["장11"])), " beta 5A/5B:", len(re.findall(r'\\beta', ch["장5A"])), len(re.findall(r'\\beta', ch["장5B"])), " Pr^sigma 8/11:", len(re.findall(r'\\Pr\^\{?\\sigma', ch["장8"])), len(re.findall(r'(\\Pr|\\mathbb E)\^\{?\\sigma', ch["장11"])))
print("== 2.8 old-2-31 proof (517-534) fonts:")
seg = "\n".join(ch["장2"].split('\n')[516:534])
print(sorted(set(re.findall(r'\\mathcal [A-Z](?:_[A-Za-z0-9{}]+)?', seg))), sorted(set(re.findall(r'q_\{d,k\}|\\mu', seg))))
show("장2", r'\\eta\s*[:=]')
for p in [r'\\mathfrak b_j', r'\\varrho_n', r'\\mathfrak d_n', r'\\Delta\^j', r'\\mathcal V_j', r'\\Omega\(z\)', r'\\mathcal G_\{j,i\}']:
    show("장2", p, n=1); show("장5A", p, n=1)
show("장6", r'\\mathfrak n_J|n_J', n=1); show("장6", r'Jensen', w=90, n=3)
show("장8", r'\\hat\{?\\varsigma', n=1); show("장8", r'\\mathcal T_N', n=1); show("장8", r'\\varsigma', n=3)
show("장9", r'\\mathfrak q_m', n=1); show("장9", r'\\mathfrak y\^\{\\mathrm S\}|\\mathfrak y\^\{\\mathrm B\}', n=2); show("장9", r'\\mathrm\{T1\}_n|\\mathrm\{Ld\}_n', n=1); show("장9", r'K\^\+_1|K_1\^\+|9467', n=2)
show("장10", r'\\gamma\^\{\\mathrm U\}|\\gamma\^U', n=1); show("장10", r'\(d-1\)/\(y\+2-d\)|\\tilde\\omega\(d\)\(d-1\)', n=2)
show("부록D_장5B.md", r'\\mathrm\{ex\}', n=1); show("부록D_장6.md", r'\\mathfrak q\(m,d\)', n=1)
show("장4", r'\\sum_\{j=1\}\^\{N\}', w=120, n=1)
show("장5A", r'x\^N|x\^\{N\+1\}|\\le N', w=60, n=2)
