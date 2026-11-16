# -*- coding: utf-8 -*-
# 결정 K0 — 설계서(결정_설계서.md)에 적힌 라벨 전수를 저장소와 대조한다.
#   설계서의 `장:라벨` 토큰을 모두 뽑아 (a) 현행 장v2 에 `{{라벨}}` 로 존재하는지, (b) 없으면 이 문서가 신설·이동으로 선언한 라벨인지를 가른다.
#   두 집합 밖의 토큰(오타·존재하지 않는 라벨)을 보고한다.  실행: python -I 결정_K0_라벨검사.py  (출력 _out.txt)
import re, glob, os, sys, io
sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
os.chdir(ROOT)
out = io.StringIO()
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); out.write(s + '\n')
design = open('대조v2/구조압축/결정_설계서.md', encoding='utf-8').read()
tokens = sorted(set(re.findall(r'`((?:\d+|D|[2-9]|10|11):[A-Za-z0-9\-]+)`', design)))
repo = ''.join(open(f, encoding='utf-8').read() for f in glob.glob('장v2/*.md'))
new_or_moved = set('''7:apex-positive 2:union-bound 7:tail-half 7:pair-loss-bound 7:pole-frame D:column-certificates-501-2000
5:tilted-birthday-mean 5:landing-mass 5:joining-width 6:first-layer-mass 6:one-step-loss 6:cutpoint-lower 6:old-8-25
2:weighted-partition 2:two-variable-frozen 2:volterra-residual 2:capacity-ratio 2:root-removal 2:chain-law 2:level-mass-jensen
2:curvature-level-mass 2:borel-arithmetic 2:power-sum-renewal 2:tree-expansion 2:supersolution 2:h-transform 2:nf-log-coefficients
2:row-positive 4:decrease-propagation 4:hermite-nu 4:vertical-nu 4:analytic-transfer 2:capacity-shift-ratio 9:box-mass-lp
10:regen-vs-ledger 6:old-8-19 6:old-8-20 6:old-8-21 6:old-8-22 6:old-8-23 5:chain-weight-all-orders'''.split())
exist, new, unknown = [], [], []
for t in tokens:
    if ('{{' + t + '}}') in repo: exist.append(t)
    elif t in new_or_moved: new.append(t)
    else: unknown.append(t)
P(f'설계서의 라벨 토큰 {len(tokens)}개: 현행 존재 {len(exist)}, 신설·이동 선언 {len(new)}, 미상 {len(unknown)}')
P('미상(오타 또는 존재하지 않는 라벨):', unknown if unknown else '없음')
P('신설·이동 가운데 설계서에 안 나온 것:', sorted(new_or_moved - set(new)) or '없음')
# 삭제 선언 라벨의 현재 소비처 수(참고)
deleted = '''2:old-2-16 2:old-2-18 2:old-2-19 2:old-2-20 2:old-2-30 2:old-2-36 2:old-2-44 3:old-3-5 3:old-3-6 4:old-4-4 4:gauss-coeff 4:two-corrections 4:old-4-9
5:cayley-ratio 5:old-5-4 5:lemma-L 5:nf-ratio 5:first-moment-weight 5:old-5-7 5:marked-chain-rec 5:old-5-23 5:old-5-24 5:stirling-bor 5:old-5-27 5:old-5-28
5:old-5-31 5:borel-gf 5:bt-tail 5:stop-lower 5:rig-int 5:scaled-integrand 5:riemann-unimodal 5:old-5-32
6:tilt-split 6:theorem-U 6:lemma-B 6:lemma-A 6:lemma-O 6:lemma-F 6:lemma-E 6:lemma-N 6:DD-lower-bound 6:path-shift 6:theorem-D 6:prop-W 6:pair-formula 6:critical-front 6:v-negative
7:old-6-5 7:factorial-moment 7:seed-transfer 7:old-6-10 7:level-chain 7:lemma-R-sc 7:self-consistent-S 7:cor-S-prime 7:riccati 7:pole-monotone 7:X-cert 7:old-6-12 7:transfer-F 7:lemma-P-pole 7:polar-R 7:polar-N 7:polar-W
7:variance-formula 7:theorem-C-moment 7:blocked-majorant 7:pair-check-10000 7:kernel-bound 7:tail-bound 7:pair-criterion-sharp 7:pair-reach-table 7:fold-A 7:fold-R 7:fold-T 7:fold-L1 7:fold-DIP 7:borel-monotone 7:polar-PD 7:prop-PF 7:qstar-columns 7:old-6-16 7:theorem-W
8:explicit-bounds 8:jensen-lower 8:lowest-violation 8:prop-U-apriori 8:table-lower-bound 8:envelope-code-monotone 8:old-6-29
9:F5-upper 9:psi-two-sided 9:head-sum-1 9:old-7-4 9:old-7-5 9:old-7-17 9:old-7-30 9:old-7-31 9:old-7-36 9:psi-low
10:old-8-4 10:row-3k 10:old-8-14 10:old-8-15 10:old-8-16 10:old-8-17 10:old-8-18'''.split()
moved = '7:hermite-nu 7:vertical-nu 7:analytic-transfer 10:old-8-19 10:old-8-20 10:old-8-21 10:old-8-22 10:old-8-23 10:old-8-24 10:old-8-25'.split()
P(f'\n삭제 선언 라벨 {len(deleted)}개, 이동(옛 라벨) {len(moved)}개 — 현행 장v2 출현 수(라벨 머리 1을 포함):')
files = sorted(glob.glob('장v2/*.md'))
for group, labs in (('삭제', deleted), ('이동', moved)):
    for L in labs:
        cnt = {os.path.basename(f).replace('.md', ''): open(f, encoding='utf-8').read().count('{{' + L + '}}') for f in files}
        cnt = {k: v for k, v in cnt.items() if v}
        if not cnt: P(f'  [{group}] {L}: 장v2 출현 0  <-- 확인(라벨 오타?)')
        else: P(f'  [{group}] {L}: {cnt}')
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '결정_K0_라벨검사_out.txt'), 'w', encoding='utf-8').write(out.getvalue())
