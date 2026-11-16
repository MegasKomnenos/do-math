# -*- coding: utf-8 -*-
"""결정 91 (3) 후속(사용자 「(가)는 지워」): 정리 theorem-C-moment의 (가)(k≥2001, n≥n°_k의 모멘트 판정; moment-window만 쓰던 부분)를 진술과 증명에서 지우고
(나)를 단일 진술로 만든다. 머리의 의존은 (나)가 쓰는 정리 theorem-G-prime으로. 부록 D의 「(나)의」 참조를 고친다. 멱등."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "장v2", "장7B.md")
Q = os.path.join(ROOT, "장v2", "부록D_장7B.md")

EDITS_7B = [
    (r"[증명됨, 계산 보조(방향 반올림 구간, 정확 정수·유리수), 명제 {{7:polar-W}}에 의존; r10ff8c2, rb7effe0].** $\mathfrak m^\sharp:=(n-k)/(k+1)$로 둔다.",
     r"[증명됨, 계산 보조(방향 반올림 구간, 정확 정수·유리수), 정리 {{7:theorem-G-prime}}에 의존; r10ff8c2, rb7effe0].** $\mathfrak m^\sharp:=(n-k)/(k+1)$로 둔다."),
    ("\n\n(가) 모든 정수 $k\\ge2001$과 $n\\ge n^\\circ_k=\\lceil2k^{3/2}\\rceil$에서 $\\mathbb E^\\sigma_{n,k}[\\mathcal T_k]>0$이다.\n\n(나) $841\\le k\\le2000$인 열마다",
     "\n\n$841\\le k\\le2000$인 열마다"),
    ("$n_{\\mathrm M}(2000)=73032$다.\n\n**증명.** (가) $k\\mathfrak Z^{\\mathrm H}_n=n\\,\\mathfrak P_k(n)$이고, 명제 {{7:polar-W}}(가)의 둘째 문장에 따라 모든 $k\\ge2001$과 $n\\ge n^\\circ_k$에서 $\\mathfrak P_k(n)\\le1.446/\\sqrt k$다. 또 $n\\ge2k^{3/2}\\ge2k+1$이므로 따름정리 {{7:factorial-moment}}에서 $\\mathfrak Z_n\\ge\\mathfrak m^\\sharp(\\mathfrak m^\\sharp-1)$이다. 그러므로 $\\mathbb E^\\sigma_{n,k}[\\mathcal T_k]\\ge \\mathrm Q(n):=\\mathfrak m^\\sharp(\\mathfrak m^\\sharp-1)-1.446n/\\sqrt k$이고, $\\mathrm Q$는 $n$의 볼록 이차식이다. $n=2k^{3/2}$에서 $\\mathfrak m^\\sharp=(2\\sqrt k-1)k/(k+1)=(2\\sqrt k-1)-(2\\sqrt k-1)/(k+1)\\ge2\\sqrt k-1-2/\\sqrt k\\ge2\\sqrt k-1.045$다($k\\ge2001$에서 $2/\\sqrt k\\le0.045$). 그러므로 $\\mathfrak m^\\sharp(\\mathfrak m^\\sharp-1)\\ge(2\\sqrt k-1.045)(2\\sqrt k-2.045)=4k-6.18\\sqrt k+2.137>4k-6.18\\sqrt k$이고, $\\mathrm Q(2k^{3/2})>4k-6.18\\sqrt k-2.892k=1.108k-6.18\\sqrt k>0$이다($\\sqrt k>5.58$). 같은 점에서 $\\mathrm Q'(n)=(2\\mathfrak m^\\sharp-1)/(k+1)-1.446/\\sqrt k\\ge(4\\sqrt k-3.09)/(k+1)-1.446/\\sqrt k$이고, 이것이 양수인 것은 $2.554k>3.09\\sqrt k+1.446$와 같아 $k\\ge2001$에서 성립한다. 볼록 이차식이 한 점에서 양수이고 도함수도 양수이면 그 점의 오른쪽에서 증가하며 양수이므로, $n\\ge2k^{3/2}$인 모든 정수에서 $\\mathrm Q(n)>0$이다.\n\n(나) $n\\ge n^{\\mathrm{bis}}_0$에서",
     "$n_{\\mathrm M}(2000)=73032$다.\n\n**증명.** $n\\ge n^{\\mathrm{bis}}_0$에서"),
    ("$\\mathrm Q_k$도 볼록 이차식이고, 열마다 $\\mathrm Q_k(n_{\\mathrm M}(k))>0$과 $\\mathrm Q_k'(n_{\\mathrm M}(k))>0$이 성립하면 (가)와 같은 이유로 $n\\ge n_{\\mathrm M}(k)$에서 $\\mathrm Q_k(n)>0$이다.",
     "$\\mathrm Q_k$는 $n$의 볼록 이차식이다. 볼록 이차식이 한 점에서 양수이고 도함수도 양수이면 그 점의 오른쪽에서 증가하며 양수이므로, 열마다 $\\mathrm Q_k(n_{\\mathrm M}(k))>0$과 $\\mathrm Q_k'(n_{\\mathrm M}(k))>0$이 성립하면 $n\\ge n_{\\mathrm M}(k)$에서 $\\mathrm Q_k(n)>0$이다."),
]
EDITS_D = [
    ("정리 {{7:theorem-C-moment}}(나)의", "정리 {{7:theorem-C-moment}}의"),
    ("정리 {{7:theorem-C-moment}}(나)와", "정리 {{7:theorem-C-moment}}와"),
    ("정리 {{7:theorem-C-moment}} (나)", "정리 {{7:theorem-C-moment}}"),
]


def apply(path, edits):
    s = io.open(path, encoding="utf-8").read()
    n = 0
    for old, new in edits:
        c = s.count(old)
        if c == 0:
            if new in s:
                continue
            print("앵커 없음:", os.path.basename(path), old[:60].replace("\n", "⏎")); continue
        s = s.replace(old, new); n += c
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)
    print(os.path.basename(path), "고침", n)
    return s


s7 = apply(P, EDITS_7B)
sd = apply(Q, EDITS_D)
for name, s in [("장7B", s7), ("부록D_장7B", sd)]:
    for key in ["theorem-C-moment}}(가)", "theorem-C-moment}}(나)", "polar-W}}(가)의 둘째 문장에 따라 모든 $k\\ge2001$과 $n\\ge n^\\circ_k$에서 $\\mathfrak P_k(n)\\le1.446"]:
        if key in s:
            print("남은 참조:", name, key[:50])
