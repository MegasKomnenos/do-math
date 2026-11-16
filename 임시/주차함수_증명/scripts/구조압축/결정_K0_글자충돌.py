# -*- coding: utf-8 -*-
# 결정 K0 — 다섯 결정 문서가 들이는 새 글자·새 라벨·옮기는 글자의 충돌 검사.
#   (1) 새 라벨 전수: 저장소(장v2·장부·구조표·README·지도 덧씌우기·영어)에 이미 있는지.
#   (2) 새 글자·옮기는 글자의 바탕 토큰이 어느 장 파일과 장부에 몇 번 나오는지(같은 바탕 글자의 다른 양 = R1′ 충돌 후보).
#   실행: python -I 결정_K0_글자충돌.py  (출력은 같은 이름 _out.txt 로 저장)
import re, glob, os, sys, io
sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
os.chdir(ROOT)
out = io.StringIO()
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); out.write(s + '\n')

# ---------- (1) 새 라벨 ----------
new_labels = {
 'K1': ['7:apex-positive', '2:union-bound', '7:tail-half', '7:pair-loss-bound', '7:pole-frame', 'D:column-certificates-501-2000'],
 'K2': ['5:tilted-birthday-mean', '5:landing-mass', '5:joining-width', '6:first-layer-mass', '6:one-step-loss', '6:cutpoint-lower', '6:old-8-25'],
 'K3': ['2:weighted-partition', '2:two-variable-frozen', '2:volterra-residual', '2:capacity-ratio', '2:root-removal', '2:chain-law',
        '2:level-mass-jensen', '2:curvature-level-mass', '2:borel-arithmetic', '2:power-sum-renewal', '2:tree-expansion', '2:supersolution',
        '2:h-transform', '2:nf-log-coefficients', '2:row-positive', '4:decrease-propagation', '4:hermite-nu', '4:vertical-nu', '4:analytic-transfer'],
 'K4': ['2:capacity-shift-ratio', '9:box-mass-lp', '10:regen-vs-ledger'],
 'K0': ['6:old-8-19', '6:old-8-20', '6:old-8-21', '6:old-8-22', '6:old-8-23', '5:chain-weight-all-orders'],
}
scan_files = sorted(glob.glob('장v2/*.md')) + ['장부_v2.md', '구조표_v2.md', '원고_자료/README.md', 'dependency_map/지도_덧씌우기.json'] + sorted(glob.glob('영어/**/*.md', recursive=True))
scan_files = [f for f in scan_files if os.path.exists(f)]
texts = {f: open(f, encoding='utf-8', errors='replace').read() for f in scan_files}
P('== (1) 새 라벨의 저장소 출현(정확 일치 `{{라벨}}` 과 부분 문자열) ==')
for who, labs in new_labels.items():
    for L in labs:
        exact = sum(t.count('{{' + L + '}}') for t in texts.values())
        part = sum(t.count(L) for t in texts.values())
        flag = '' if exact == 0 and part == 0 else '  <-- 확인'
        P(f'  {who} {L}: 정확 {exact}, 부분 {part}{flag}')

# ---------- (2) 글자 토큰 ----------
tokens = {
 # (이름, 패턴들)
 'K1 전달 문턱 T_k  대  2.10절 T_ℓ(나무 함수의 절단; 9장 14회)': [r'T_k\b', r'T_\{k', r'T_\{\\ell'],
 'K1 전달 문턱 대안 n^{G}_k / n^{T}_k': [r'n\^\{\\mathrm G\}', r'n\^\{\\mathrm\{G\}\}', r'n\^\{\\mathrm T\}', r'n\^\\psi_k', r'n\^\{\\mathrm\{bis\}\}'],
 'K1 왼쪽 창 \\mathcal W (현행 \\mathcal W^{(>102)}; 2.12 \\mathcal W_n(γ)와 바탕 글자 같음)': [r'\\mathcal W\^', r'\\mathcal W_n', r'\\mathcal W\b'],
 'K1 apex^H': [r'\\mathrm\{apex\}'],
 'K1 N7 e_x (p,q 지표)': [r'\\be_x\b', r'\\be_p\b', r'\\be_q\b'],
 'K2 한 칸 손실 D_{n,k}  대  8장 D_1,D_2,D_3·6.4 D_k': [r'\bD_\{n,k\}', r'\bD_1\b', r'\bD_3\b', r'\bD_k\b'],
 'K2 합집합 상계 \\mathcal U_m  대  6.5 볼츠만 꼬리합 \\mathcal U_k(m)': [r'\\mathcal U_k', r'\\mathcal U_m', r'\\mathcal U\b'],
 'K1 합집합 상계 \\mathrm{UB}': [r'\\mathrm\{UB\}'],
 'K2 \\widehat\\Lambda (5B Λ_w 변형) 대 8장 Λ': [r'\\widehat\\Lambda', r'\\Lambda_\{\\mathrm w\}', r'\\Lambda\(', r'\\Lambda\b'],
 'K2 \\mathfrak W_0': [r'\\mathfrak W_0'],
 'K2 \\mathsf u^\\flat': [r'\\mathsf u\^\\flat'],
 'K2 옮기는 \\mathsf m_S, \\mathfrak s^{up}': [r'\\mathsf m_\{\\mathrm S\}', r'\\mathfrak s\^\{\\mathrm\{up\}\}'],
 'K3 wg / A_n[wg]': [r'\\mathrm\{wg\}', r'A_n\['],
 'K3 \\mathcal K_{n,k}(η,y) / η': [r'\\mathcal K_\{n,k\}\(', r'\\eta\b'],
 'K3 2.7절로 당기는 \\mathcal E_{<k}, \\mathfrak T_{≤k}, \\mathcal Q_k, \\mathcal D(, \\mathcal G_\\ast': [r'\\mathcal E_\{<k\}', r'\\mathfrak T_\{', r'\\mathcal Q_k', r'\\mathcal D\(', r'\\mathcal D\b', r'\\mathcal G_\\ast'],
 'K3 Ψ^{low}, \\mathsf c_Ψ (8.2→2.9)': [r'\\Psi\^\{\\mathrm\{low\}\}', r'\\mathsf c_\\Psi'],
 'K3 H 국소 후보 \\mathfrak q, \\mathfrak o, \\mathcal R, κ, \\mathfrak M': [r'\\mathfrak q\b', r'\\mathfrak q_', r'\\mathfrak o\b', r'\\mathfrak o_', r'\\mathcal R\b', r'\\mathcal R_j', r'\\kappa_0', r'\\kappa_N', r'\\mathfrak M\b', r'\\mathfrak M_y'],
 'K4 L_{n,m}  대  2.5 L(사슬 길이; 2·3·6·7·9·10장)': [r'\bL_\{n,m\}', r'\bL\b'],
 'K4 \\bar\\omega_i, \\bar s_i, \\mathsf L_3': [r'\\bar\\omega', r'\\bar s_', r'\\mathsf L_3', r'\\mathsf L_\\ast'],
 'K4 Stays^{adm}': [r'\\mathrm\{Stays\}\^\{\\mathrm\{adm\}\}'],
 'K0 10.5절→6.5절 이동 글자(6장과 충돌 검사): \\mathfrak h_y, inc, tr_y, \\mathfrak M_y, \\mathfrak A, \\mathfrak k_d, \\mathfrak n_q, \\mathfrak t_q, \\mathfrak H_d, DDL, \\mathfrak s^{fr}, Res': [
     r'\\mathfrak h_y', r'\\mathfrak h\b', r'\\mathrm\{inc\}', r'\\mathrm\{tr\}_y', r'\\mathfrak M_y', r'\\mathfrak A_j', r'\\mathfrak A\^', r'\\mathfrak A\b', r'\\mathfrak k_d', r'\\mathfrak k\b',
     r'\\mathfrak n_q', r'\\mathfrak n\b', r'\\mathfrak t_q', r'\\mathfrak t\b', r'\\mathfrak t_', r'\\mathfrak H_d', r'\\mathfrak H\b', r'\\mathrm\{DDL\}', r'\\mathfrak s\^\{\\mathrm\{fr\}\}', r'\\mathrm\{Res\}'],
 'K0 6.45 가 받는 DDL♮ 와 6장 기존 \\mathfrak X^1_d, \\mathcal R_j(기울임 인자)': [r'\\mathfrak X\^1_d', r'\\mathfrak X\^0_d', r'\\mathcal R_j'],
}
chap_files = sorted(glob.glob('장v2/*.md')) + ['장부_v2.md']
ctexts = {f: open(f, encoding='utf-8').read() for f in chap_files}
P('\n== (2) 글자 토큰의 장별 출현 수(0 이면 비어 있음) ==')
for name, pats in tokens.items():
    P('--', name)
    for p in pats:
        rx = re.compile(p)
        cnt = {os.path.basename(f).replace('.md', ''): len(rx.findall(t)) for f, t in ctexts.items()}
        cnt = {k: v for k, v in cnt.items() if v}
        P(f'   {p} -> {cnt if cnt else 0}')

# 장부 1.2 의 바탕 글자 행(글자체 열) — 바탕 글자가 같은 전역 행을 뽑는다
P('\n== (3) 장부 1.2 전역 행 가운데 바탕 글자 T·W·U·D·L·η·R·κ·M·H·A·k·n·t 의 행(글자체 열 기준) ==')
ledger = ctexts['장부_v2.md'].splitlines()
want = ['T·', 'W·', 'U·', 'D·', 'L·', 'η·', 'R·', 'κ·', 'M·', 'H·', 'A·', 'k·', 'n·', 't·', 'h·', 'Λ·', 'q·', 'o·']
for i, line in enumerate(ledger, 1):
    if line.startswith('| $') and '|' in line[2:]:
        cells = [c.strip() for c in line.split('|')]
        if len(cells) > 3 and any(cells[2].startswith(w) for w in want):
            P(f'  {i}: {cells[1][:60]} | {cells[2][:22]} | {cells[3][:70]} | 정의절 {cells[4] if len(cells)>4 else ""}')
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '결정_K0_글자충돌_out.txt'), 'w', encoding='utf-8').write(out.getvalue())
