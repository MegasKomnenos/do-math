# -*- coding: utf-8 -*-
"""S14: 장부 1.2 대조에서 의심된 기호를 장별로 찾아 자리와 문맥을 보인다(공백·중괄호를 지운 수식 조각 기준)."""
import re, sys, io, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = pathlib.Path(r"C:\math\임시\주차함수_증명")
CH = {1:["장1.md"],2:["장2.md"],3:["장3.md"],4:["장4.md"],5:["장5A.md","장5B.md"],6:["장6.md"],7:["장7A.md","장7B.md"],8:["장8.md"],9:["장9.md"],10:["장10.md"],11:["장11.md"]}
BS = chr(92)
def norm(s):
    s = re.sub(r'\s+', '', s); s = s.replace(BS + ',', '')
    return s.replace('{', '').replace('}', '')
raw = {}
for c, fs in CH.items():
    raw[c] = []
    for f in fs:
        for ln, line in enumerate((ROOT/'장v2'/f).read_text(encoding='utf-8').splitlines(), 1):
            for seg in re.findall(r'\$\$?(.+?)\$\$?', line):
                raw[c].append((f, ln, norm(seg)))
def show(pat, chs, maxn=2):
    for c in chs:
        hits = [(f, ln, s) for f, ln, s in raw[c] if re.search(pat, s)]
        print(f"  [{pat}] 장{c}: {len(hits)}건", '; '.join(f"{f}:{ln} {s[:70]}" for f, ln, s in hits[:maxn]))
L = r'(?<![A-Za-z\\])'      # 바탕 글자 앞
SUB1 = r'_(?:[a-zA-Z]|\\[a-zA-Z]+)(?![A-Za-z,])'
checks = [
 (r'b\^\(2\)_', [10]), (r'c\^\(2\)_', [2]), (r'\\mathrmcf', [11]), (L + r't_v(?![A-Za-z])', [8]),
 (r'\\beta' + SUB1, [5]), (r'\\Gamma\^', [4]), (r'\\xi(?![A-Za-z])', [11]), (r'\\mathsfa_', [7]),
 (r'\\mathrmBor\^\*', [6, 8, 10]), (r'\\mathrminc', [10]), (r'\\mathrmKD', [7, 10]),
 (L + r'x_\\ast', [2, 5, 6, 9]), (L + r'x_t(?![A-Za-z])', [1, 3]), (L + r'd' + SUB1, [6, 8]),
 (L + r'n_\\mathrmPD', [11]), (L + r'k_n(?![A-Za-z])', [11]), (r'\\kappa_N', [11]), (L + r'J_n(?![A-Za-z])', [8, 11]),
 (L + r'H_k(?![A-Za-z])', [9]), (L + r'R' + SUB1, [7, 11]), (r'\\mathcalI_k', [11]),
 (r'\\mathfraka' + SUB1, [10, 11]), (r'\\mathfrakP_k', [9, 11]), (r'\\mathrmBor_>', [9, 11]),
 (r'\\mathrmsrc', [8]), (r'\\mathrmtail', [4, 7]), (r'\\mathrmtop(?![A-Za-z])', [9, 11]), (L + r'q_\\mathrmfb', [2, 5, 6, 10]), (L + r'q_\\max', [2, 6, 10]),
 (L + r'E_[^,()]+,[^,()]+', [3, 6, 8, 9]), (r'\\varsigma' + SUB1, [11]), (r'\\vartheta(?![A-Za-z_^])', [11]),
 (r'\\omega' + SUB1, [11]), (L + r'L(?![A-Za-z_^])', [1, 11]), (L + r'X(?![A-Za-z_^])', [1]),
 (L + r'F(?![A-Za-z_^])', [11]), (L + r'G(?![A-Za-z_^])', [11]), (r'\\zeta(?![A-Za-z_^(])', [5]), (r'\\mathcalK_[^,()]+,', [6]), (r'\\star', [11]),
 (L + r'N(?![A-Za-z_^])', [4, 5, 11]), (L + r'A' + SUB1, [6, 10]),
]
for pat, chs in checks:
    show(pat, chs)
