# -*- coding: utf-8 -*-
"""E14: 고정 문자열을 장 파일에서 찾아 앞뒤 문맥을 보인다. 사용: python -I 검토전체16_E14_ctx.py 파일 문자열 [최대건수]"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
pairs = [
 ("장8", r"\mathrm{fb}(\lambda)"), ("장8", r"q_{\mathrm{fb}}:="), ("장8", r"q^\circ_{\mathrm{fb}}"), ("장8", r"m_{\mathrm{fb}}:="),
 ("장8", r"\mathsf c_\Psi:="), ("장8", r"\Psi^{\mathrm{low}}_{(\varrho)}:="), ("장8", r"\mathsf j_\infty(\xi):="), ("장8", r"s^{\mathrm{cf}}(\xi):="),
 ("장8", r"\mathfrak h(k,\nu):="), ("장8", r"\mathfrak D^{\mathrm{src}}_q:="), ("장8", r"\mathrm{LB}^{\mathrm{mono}}"),
 ("장9", r"\Psi^{\mathrm{lb}}(d):="), ("장9", r"\bar{\mathfrak d}_k:="),
 ("장10", r"\pi^{\mathrm{two}}_N:="), ("장10", r"\mathsf m_{\mathrm S}"), ("장10", r"d^\star:="), ("장10", r"\nu_{\min}(k)"),
 ("장6", r"s^{\mathrm F}(k,\nu):="), ("장6", r"\mathsf s_{\mathrm B}"), ("장6", r"\mathrm{Bd}^{\mathrm V}_k:="), ("장6", r"\varphi^\flat_k"),
 ("장5B", r"\Lambda_{\mathrm w}(Y):="), ("장5B", r"q_{\max}(Y):="), ("장2", r"W_n(\gamma):="), ("장4", r"\mathcal M_r:="), ("장4", r"\mathcal M_r"),
]
if len(sys.argv) >= 3:
    pairs = [(sys.argv[1], sys.argv[2])]
maxn = int(sys.argv[3]) if len(sys.argv) >= 4 else 2
for f, needle in pairs:
    txt = open(f"{ROOT}/장v2/{f}.md", encoding='utf-8').read()
    print(f"[{f}] {needle}")
    pos = 0; n = 0
    while n < maxn:
        i = txt.find(needle, pos)
        if i < 0: break
        line = txt.count("\n", 0, i) + 1
        print(f"  {line}: ...{txt[max(0,i-80):i+200].replace(chr(10),' ')}...")
        pos = i + 1; n += 1
    if n == 0: print("  (없음)")
