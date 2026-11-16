# -*- coding: utf-8 -*-
"""결정 K1 검산 (3) — 처분 대상 라벨·글자·수의 저장소 전수 출현 수(grep -F 상당).
파일: 장v2/*.md, 장부_v2.md, README.md, dependency_map/지도_덧씌우기.json. 출력 결정_K1_소비처_out.txt.
기계 검색은 어디를 읽을지 알려 줄 뿐이고 쓰임의 판단은 결정 문서 1절·3절에서 원문으로 했다.
"""
import os, glob
ROOT = r"C:\math\임시\주차함수_증명"
files = sorted(glob.glob(os.path.join(ROOT, "장v2", "*.md"))) + [os.path.join(ROOT, "장부_v2.md"), os.path.join(ROOT, "README.md"), os.path.join(ROOT, "dependency_map", "지도_덧씌우기.json")]
texts = {}
for f in files:
    try:
        with open(f, encoding="utf-8") as fh: texts[os.path.basename(f)] = fh.read()
    except FileNotFoundError:
        pass
labels = ["7:polar-W","7:polar-N","7:polar-R","7:lemma-P-pole","7:transfer-F","7:old-6-10","7:flat-threshold","7:old-6-8","7:old-6-9",
          "7:seed-transfer","7:column-lemma","7:factorial-moment","7:level-chain","7:lemma-R-sc","7:self-consistent-S","7:cor-S-prime",
          "7:theorem-C-moment","7:variance-formula","7:moment-recursion","7:blocked-majorant","7:riccati","7:pole-unique","7:pole-monotone",
          "7:old-6-11","7:fourier-lemmas","7:X-cert","7:old-6-12","7:lemma-P-prime","7:theorem-G-prime","7:old-6-13","7:old-6-14","7:old-6-15",
          "7:qstar-implies-wlflat","7:fold-A","7:fold-R","7:fold-T","7:fold-L1","7:fold-DIP","7:borel-monotone","7:polar-PD","7:prop-PF",
          "7:qstar-columns","7:root-symmetry","7:old-6-16","7:explicit-bounds","7:top-roots","7:theorem-W","7:src-plus","7:old-6-20",
          "7:threshold-unit-ratio","7:old-6-21","7:old-6-22","7:pair-check-10000","7:kernel-bound","7:tail-bound","7:pair-criterion-sharp",
          "7:pair-reach-table","7:heavy-block","7:pair-criterion","7:hermite-nu","7:vertical-nu","7:analytic-transfer","7:integer-strips",
          "6:old-7-24","6:old-7-20","6:V-all","6:old-6-19","6:v-negative","6:critical-front","6:small-k-bulk","6:far-window","6:above-window",
          "6:first-layer-end","6:old-8-11","6:prop-W","6:prop-R","6:lemma-M","6:lemma-Hprime","6:theorem-U",
          "D:polar-blocks-488","D:self-consistent-constants","D:xcert-partAB","D:Q-fin-1130","D:moment-certification","D:column-certificates-841-2000",
          "D:seed-certificates-k120","D:column-certification-k500","D:band102-integer","D:prop-W-thirteen","D:tilt-sum-small-k"]
symbols = [r"n^\flat_k", r"n^\circ_k", r"n^\sharp_k", r"\mathsf W_L^\flat", r"\mathsf W_L", r"\mathcal W^{(>102)}", r"\mathcal W^{(>40)}",
           r"\mathsf{LRP}_2", r"10001", r"3131", r"3130", r"n_{\mathrm{PD}}", r"\mathrm{Fold}", r"\mathfrak G_k", r"0.14", r"42.14", r"0.33316",
           r"0.08329", r"2.647", r"0.529", r"\varphi_k", r"\mathsf x_k", r"5.3146", r"n_{\mathrm M}", r"\mathfrak P^{\mathrm M}_k", r"\kappa_N",
           r"\epsilon_N", r"T_k", r"n^{\psi}_k", r"\mathrm{apex}", r"\mathrm{tf}", r"\hat{\mathfrak n}_q", r"\pi^\sharp_q", r"극 영역", r"전달 범위",
           r"증가 경계", r"자기일관", r"골격 값", r"수준 사슬", r"유한 전파", r"반감 경계", r"평탄 문턱", r"꼬리 삼중", r"쌍별로 닿은 껍질"]
out = []
names = list(texts.keys())
def table(items, wrap):
    hdr = "| 항목 | " + " | ".join(n.replace('.md','') for n in names) + " | 합 |"
    out.append(hdr); out.append("|" + "---|"*(len(names)+2))
    for it in items:
        key = wrap(it)
        cnts = [texts[n].count(key) for n in names]
        if sum(cnts) == 0 and not it.startswith(('7:','6:','D:')): continue
        out.append(f"| `{it}` | " + " | ".join(str(c) if c else "·" for c in cnts) + f" | {sum(cnts)} |")
out.append("## 라벨 `{{…}}` 출현 수")
table(labels, lambda s: "{{"+s+"}}")
out.append("\n## 글자·수·낱말 출현 수(문자열 그대로; 수는 다른 뜻의 출현을 포함할 수 있다)")
table(symbols, lambda s: s)
with open(os.path.join(ROOT, r"scripts\구조압축\결정_K1_소비처_out.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out)+"\n")
print("\n".join(out))
