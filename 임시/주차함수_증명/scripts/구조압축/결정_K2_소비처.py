# -*- coding: utf-8 -*-
# 결정 K2 — 처분 대상 라벨의 출현 전수(grep -F 상당). 장v2/*.md, 장부_v2.md, 지도_덧씌우기.json, 대응표.
import os, sys, glob, io
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r"C:\math\임시\주차함수_증명"
files = sorted(glob.glob(os.path.join(ROOT, "장v2", "*.md"))) + [
    os.path.join(ROOT, "장부_v2.md"),
    os.path.join(ROOT, "dependency_map", "지도_덧씌우기.json"),
    os.path.join(ROOT, "대조v2", "라벨_번호_대응표_1114.md"),
]
labels = """5:cayley-ratio 5:old-5-4 5:lemma-L 5:old-5-5 5:nf-ratio 5:first-moment-weight 5:parity-tail 5:old-5-7 5:laurent-coeff 5:kernel-crude
5:marked-recursion 5:marked-chain-rec 5:weight-envelope 5:omitted-tail 5:old-5-12 5:cover-edge 5:old-5-10 5:old-5-11 5:old-5-15
5:old-5-21 5:old-5-22 5:old-5-23 5:old-5-24 5:old-5-25 5:stirling-bor 5:old-5-26 5:old-5-27 5:old-5-28 5:old-5-30 5:old-5-31 5:borel-gf 5:bt-tail
5:stop-lower 5:rig-int 5:scaled-integrand 5:riemann-unimodal 5:old-5-32 5:old-5-33 5:old-5-34 5:hover-tail 5:band-inequality 5:right-part 5:old-5-38 5:old-5-18
6:old-7-13 6:tilt-sum 6:old-7-20 6:old-7-21 6:old-7-24 6:increment-bounds 6:same-kernel 6:old-8-11 6:pair-rearrange 6:diag-first-layer 6:cor-L
6:tilt-split 6:theorem-U 6:lemma-B 6:lemma-A 6:lemma-O 6:lemma-F 6:lemma-E 6:lemma-N 6:old-6-19 6:DD-lower-bound 6:path-shift 6:theorem-D 6:prop-W
6:prop-R 6:pair-formula 6:lemma-H 6:lemma-Hprime 6:lemma-M 6:critical-front 6:far-window 6:first-layer-end 6:small-k-bulk 6:above-window 6:v-negative 6:V-all
10:old-8-24 10:old-8-25 10:old-8-15 8:prop-U-apriori 8:old-6-30 2:old-2-34
D:newton-m170 D:tail-T1-partAB D:bernstein-signs D:window-mass-constant D:band-check D:theorem-D-base D:prop-W-thirteen D:tilt-sum-small-k D:theorem-U-constant""".split()
texts = {}
for f in files:
    with open(f, encoding='utf-8') as fh:
        texts[os.path.basename(f)] = fh.read()
print("라벨 | 파일별 출현 수(0인 파일 생략) | 합계")
for lab in labels:
    key = "{{" + lab + "}}"
    row = []
    tot = 0
    for name, t in texts.items():
        c = t.count(key)
        if name.endswith('json') or name.startswith('라벨'):
            c = t.count(lab)
        if c:
            row.append(f"{name}:{c}")
            tot += c
    print(f"{lab} | {' '.join(row)} | {tot}")
