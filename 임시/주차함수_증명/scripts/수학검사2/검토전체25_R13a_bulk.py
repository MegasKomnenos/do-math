# -*- coding: utf-8 -*-
# R13a: first-pass locator. For each ledger 1.2 row (by line no.), count hand-given fixed-string
# tokens per chapter (bare = not preceded by a letter / font command) and print next to the
# ledger's "쓰이는 장" cell. Only an aid for finding places to read.
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
F = importlib.import_module('검토전체25_R13a_find')
base = F.base
data = F.load()
led = io.open(os.path.join(base, '장부_v2.md'), encoding='utf-8').read().split('\n')
FONTS = ('\\mathfrak', '\\mathsf', '\\mathcal', '\\mathrm', '\\mathbb', '\\hat', '\\tilde', '\\bar', '\\widehat', '\\widetilde', '\\overline')
def bare_ok(l, p):
    if p == 0: return True
    c = l[p-1]
    if c.isalpha() and ord(c) < 128: return False
    if c == '\\': return False
    pre = l[:p].rstrip()
    if c == '{':
        pre = pre[:-1].rstrip()
    for f in FONTS:
        if pre.endswith(f): return False
    return True
T = {
49: ['a_i','a_1','a_n','a_{\\sigma','a_j'],
50: ['b_{'], 51: ['b^\\sigma','b^{\\sigma}'], 52: ['b^{(2)}'], 53: ['b^T','b^{T}','b^{\\mathrm T}'],
54: ['c_m(','c_n(','c_N(','c_{'], 55: ['c^{(2)}'], 56: ['d_i','d_{\\sigma','d_n'], 57: ['d_{'],
58: ['d^\\star','d^{\\star}'], 59: ['e_n'], 60: ['\\ell^\\ast','\\ell^{\\ast}','\\ell^*'], 61: ['\\ell_n','\\ell_{n'],
63: ['g('], 64: ['h_i','h_j','h_1','h_n','h_{','h_p'], 65: ['k_n','k_{n'], 66: ['k_0','k^\\ast','k^{\\ast}','k^*'],
67: ['m_{\\mathrm{fb}}'], 68: ['m_0'], 69: ['m^\\flat','m^{\\flat}'], 70: ['n^\\sharp','n^{\\sharp}'],
71: ['n^{\\mathrm G}','n^{\\mathrm{G}}'], 72: ['p_'], 73: ['q_{\\max}'], 74: ['q_{\\mathrm{fb}}'],
75: ['s^T','s^{T}','s^{\\mathrm T}'], 76: ['s_m(','s_n(','s_N(','s_{'], 77: ['s^{\\mathrm{low}}'], 78: ['s^{\\mathrm{cf}}'],
79: ['s^{\\mathrm W}','s^{\\mathrm{W}}'], 80: ['t_v','t_{v','t_u','t_w'], 81: ['t_0(','\\mathrm{wid}'], 82: ['w_m','w_{'],
83: ['\\hat x','\\hat{x}'], 84: ['x_t(','x_{','x_m(','x_n('], 85: ['x_\\ast','x_{\\ast}','x_*'], 86: ['y_0'],
87: ['A_{'], 88: ['A^\\sigma','A^{\\sigma}'], 89: ['A_\\ell(','A_{\\ell}(','A_{k-1}(','A_k(','A_{k}('], 90: ['[\\mathrm{wg}]'],
91: ['A^c','A^{c}'], 92: ['B_{'], 93: ['C_k','C_{'], 94: ['E_{','E2_{'],
97: ['H_k','H_t','H_m','H_{'], 98: ['I_v','I_{v'], 99: ['J_n(','J_{','J_m('], 100: ['J^{\\mathrm G}'],
103: ['M(F)'], 104: ['M^{\\#}','M^\\#'], 105: ['M^T','M^{T}'], 106: ['P_n(','P_m(','P_{'],
107: ['Q_\\ell','Q_{\\ell','Q_{k-1}','Q_k'], 108: ['R_j','R_0','R_{'], 109: ['S_1','S_i','S_0','S_L','S_j','S_{','S_2'],
110: ['T_\\ell','T_{\\ell','T_k','T_{k'], 111: ['T(x)','T(1/e)','T('], 112: ['T^{\\le','T^{>'], 113: ['U_v','U_{v'], 114: ['V('],
115: ['W_n(','W^{[','W_{n'], 116: ['X_n','(X\\ge','(X\\le','X\\ge','X\\le'], 117: ['Z_k','Z_{'], 118: ['\\alpha'],
119: ['\\beta_i','\\beta_j','\\beta_1','\\beta_{'], 120: ['\\chi_m','\\chi_{','\\chi_n'], 121: ['\\delta_t','\\delta_{','\\delta_m'],
122: ['\\epsilon'], 123: ['\\Gamma^\\pm','\\Gamma^{\\pm}','\\Gamma^+','\\Gamma^-','\\Gamma^{+}','\\Gamma^{-}'],
124: ['\\Gamma_'], 125: ['\\kappa_'], 126: ['\\lambda'], 127: ['\\widehat\\Lambda','\\hat\\Lambda','\\Lambda'],
128: ['\\mu_'], 129: ['\\nu_{\\min}','\\bar\\nu','\\bar{\\nu}'], 130: ['\\Omega'], 131: ['\\omega_','\\tilde\\omega','\\tilde{\\omega}'],
132: ['\\Phi'], 133: ['\\pi^0','\\pi^{0}'], 134: ['\\pi_'], 135: ['\\Pi'], 136: ['\\Pi_'], 137: ['\\Pi^{\\mathrm{up}}'],
138: ['\\pi^{\\mathrm{two}}'], 139: ['\\Psi('], 140: ['\\Psi^{\\mathrm{low}}'], 141: ['\\rho_k','\\rho_{k'], 142: ['\\sigma'],
143: ['\\tau'], 144: ['\\theta_'], 145: ['\\Theta_'], 146: ['\\varkappa_'], 147: ['\\varsigma_'], 148: ['\\vartheta'],
149: ['\\vartheta_{\\mathrm{lb}}'], 150: ['\\vartheta^{\\mathrm T}'], 151: ['\\Xi'], 152: ['\\xi'],
153: ['\\mathcal A'], 154: ['\\mathcal B'], 155: ['\\mathcal D'], 156: ['\\mathcal E_{<'], 157: ['\\mathcal G'], 158: ['\\mathcal I'],
159: ['\\mathcal K'], 160: ['\\mathcal M'], 161: ['\\mathcal N'], 162: ['\\mathcal P_'], 163: ['\\mathcal P^{(k)}'], 164: ['\\mathcal R'],
165: ['\\mathcal S'], 166: ['\\mathcal T'], 167: ['\\mathcal U'], 168: ['\\mathcal V'], 169: ['\\mathcal W'], 170: ['\\mathcal X'],
171: ['\\mathcal Z'], 172: ['\\mathfrak a_','\\mathfrak a^{('], 173: ['\\mathfrak a^\\circ','\\mathfrak a^{\\circ}'],
174: ['\\mathfrak a^\\rho','\\mathfrak a^{\\rho}'], 175: ['\\mathfrak A'], 176: ['\\mathfrak b'], 177: ['\\mathfrak c'],
178: ['\\mathfrak D^{\\mathrm{src}}'], 179: ['\\mathfrak D_'], 180: ['\\mathfrak E'], 181: ['\\mathfrak f'], 182: ['\\mathfrak H'],
183: ['\\mathfrak k'], 184: ['\\mathfrak m('], 185: ['\\mathfrak p'], 186: ['\\mathfrak P'], 187: ['\\mathfrak P_k(\\infty)'],
188: ['\\mathfrak Q'], 189: ['\\mathfrak r'], 190: ['\\mathfrak R_'], 191: ['\\mathfrak R^{\\mathrm{low}}'], 192: ['\\mathfrak S_'],
193: ['\\mathfrak s_'], 194: ['\\mathfrak s^{\\mathrm{fr}}'], 195: ['\\mathfrak s^{\\mathrm{up}}'], 196: ['\\mathfrak s^{\\mathrm{low}}'],
197: ['\\mathfrak T'], 198: ['\\mathfrak u'], 199: ['\\mathfrak v'], 200: ['\\mathfrak w'], 201: ['\\mathfrak W'],
202: ['\\mathsf a'], 203: ['\\mathsf b'], 204: ['\\mathsf c'], 205: ['\\mathsf f'], 206: ['\\mathsf{FLQ}'], 207: ['\\mathsf g'],
208: ['\\mathsf j'], 209: ['\\mathsf{LH}'], 210: ['\\mathsf m'], 211: ['\\mathsf n'], 212: ['\\mathsf P'], 213: ['\\mathsf P_'],
214: ['\\mathsf Q(','\\mathsf Q_R','\\mathsf Q'], 215: ['\\mathsf Q^\\star','\\mathsf Q^{\\star}'], 216: ['\\mathsf r'], 217: ['\\mathsf s'],
218: ['\\mathsf t'], 219: ['\\mathsf u'], 220: ['\\mathsf V'], 221: ['\\mathsf v'], 222: ['\\mathsf W'], 223: ['\\mathsf w'],
224: ['\\mathsf W_L'], 225: ['\\mathsf x'], 226: ['\\mathsf z'], 227: ['\\mathrm{apex}'], 228: ['\\mathrm{Bd}^{\\mathrm V}'],
229: ['\\mathrm{Bd}^{\\mathrm S}'], 230: ['\\mathrm{Bd}^{\\mathrm T}'], 231: ['\\mathrm{Bor}('], 232: ['\\mathrm{Bor}^{*'],
233: ['\\mathrm{Bor}^{\\mathrm{tail}}'], 234: ['\\mathrm{Bor}_{>}','\\mathrm{Bor}_>'], 235: ['\\mathrm{Bor}_\\le','\\mathrm{Bor}_{\\le'],
236: ['\\mathrm{BV}'], 237: ['\\mathrm{cl}'], 238: ['\\mathrm{DD}'], 239: ['\\mathrm{DDL}'], 240: ['\\mathrm{dup}'], 241: ['\\mathrm{fb}('],
242: ['\\mathrm{Flow}'], 243: ['\\mathrm{Gr}'], 244: ['\\mathrm{He}'], 245: ['\\mathrm{hf}'], 246: ['\\mathrm{hz}'], 247: ['\\mathrm{IH}'],
248: ['\\mathrm{inc}'], 249: ['\\mathrm{inh}'], 250: ['\\mathrm{KD}'], 251: ['\\mathrm{km}'], 252: ['\\mathrm{LB}','\\mathrm{LOW}'],
253: ['\\mathrm{lc}'], 254: ['\\mathrm{Left}'], 255: ['\\mathrm{Lip}'], 256: ['\\mathrm{loss}'], 257: ['\\mathrm{nf}'], 258: ['\\mathrm{pd}'],
259: ['\\mathrm{PF}'], 260: ['\\mathrm{PM}'], 261: ['\\mathrm{pos}'], 262: ['\\mathrm{POS}'], 263: ['\\mathrm{Quad}','\\mathrm{Stem}'],
264: ['\\mathrm{rb}'], 265: ['\\mathrm{rq}'], 266: ['\\mathrm{Ren}'], 267: ['\\mathrm{Res}'], 268: ['\\mathrm{sm}'], 269: ['\\mathrm{src}'],
270: ['\\mathrm{Stays}'], 271: ['\\mathrm{Stays}^{\\mathrm{adm}}'], 272: ['\\mathrm{Stays}^{\\mathrm{up}}'], 273: ['\\mathrm{stp}'],
274: ['\\mathrm{tail}'], 275: ['\\mathrm{tilt}'], 276: ['\\mathrm{top}'], 277: ['\\mathrm{vm}'], 278: ['\\mathrm{WIN}'], 279: ['\\mathrm{wg}'],
280: ['\\Pr_','\\mathbb E_'], 281: ['\\Pr_{\\mathrm B}'], 282: ['\\Pr^T','\\Pr^{T}','\\mathbb E^T','\\mathbb E^{T}'],
283: ['\\Pr^y(','\\Pr^{y}('], 284: ['\\Pr^y','\\Pr^{y','\\mathbb E^y','\\mathbb E^{y'],
285: ['\\Pr^\\sigma','\\Pr^{\\sigma}','\\mathbb E^\\sigma','\\mathbb E^{\\sigma}'], 286: ['(\\mathrm G)'], 287: ['(\\star)'],
}
NOBARE = set(range(118, 288))  # tokens starting with backslash/paren: no bare filter
def k(x):
    m = re.match(r'(\d+)(D?)', x); return (int(m.group(1)), m.group(2))
for n in sorted(T):
    row = led[n-1]
    cells = row.split(' | ')
    cnt = {}
    for ch, b, i, sec, l in data:
        for t in T[n]:
            st = 0
            while True:
                p = l.find(t, st)
                if p < 0: break
                st = p + len(t)
                if n not in NOBARE and not bare_ok(l, p): continue
                cnt[ch] = cnt.get(ch, 0) + 1
    found = sorted(cnt, key=k)
    claimed = cells[4].strip() if len(cells) == 7 else '?? cells=%d' % len(cells)
    cl = [c.strip() for c in claimed.split(',')]
    flag = '' if cl == found else '  <<< DIFF'
    print('L%d %s | claimed [%s] | found %s%s' % (n, cells[0][2:40], claimed, ' '.join('%s:%d' % (c, cnt[c]) for c in found), flag))
