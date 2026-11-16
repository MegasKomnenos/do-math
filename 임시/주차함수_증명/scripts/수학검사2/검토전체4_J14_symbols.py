# -*- coding: utf-8 -*-
"""J14: 장부 1.2 「쓰이는 장」 열을 장 파일의 수식과 대조한다.
규칙(1.2 머리): 그 기호가 둘째 판의 그 장 본문에 나타나는 모든 장.
스크립트는 자리를 찾는 데만 쓰고 판단은 사람이 한다(파견문 원칙 3).
"""
import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'C:\math\임시\주차함수_증명')
CH = {1:['장1'],2:['장2'],3:['장3'],4:['장4'],5:['장5A','장5B'],6:['장6'],7:['장7A','장7B'],8:['장8'],9:['장9'],10:['장10'],11:['장11']}
APP = {'A':['부록A'],'B':['부록B'],'C':['부록C'],'D2':['부록D_장2'],'D3':['부록D_장3'],'D4':['부록D_장4'],'D5':['부록D_장5A','부록D_장5B'],'D6':['부록D_장6'],'D7':['부록D_장7A','부록D_장7B'],'D8':['부록D_장8'],'D9':['부록D_장9'],'D10':['부록D_장10']}

def math_segments(text):
    # display math first
    segs = []
    for m in re.finditer(r'\$\$(.+?)\$\$', text, re.S):
        segs.append(m.group(1))
    text2 = re.sub(r'\$\$(.+?)\$\$', ' ', text, flags=re.S)
    for m in re.finditer(r'\$([^$\n]+?)\$', text2):
        segs.append(m.group(1))
    return segs

def load(group):
    out = {}
    for key, files in group.items():
        segs = []
        for f in files:
            t = (ROOT/'장v2'/(f+'.md')).read_text(encoding='utf-8')
            segs += math_segments(t)
        out[key] = segs
    return out

CHM = load(CH)
APM = load(APP)

# 장부 1.2 파싱
lines = (ROOT/'장부_v2.md').read_text(encoding='utf-8').splitlines()
rows = []
for i in range(48, 340):  # 0-based; lines 49..340
    L = lines[i]
    if not L.startswith('| $') and not L.startswith('| $('): continue
    cols = [c.strip() for c in L.strip().strip('|').split(' | ')]
    if len(cols) < 7:
        # fallback split
        cols = [c.strip() for c in L.strip().strip('|').split('|')]
    rows.append((i+1, cols[0], cols[4]))

def parse_chs(s):
    if '전 장' in s: return set(range(1,12))
    return set(int(x) for x in re.findall(r'\d+', s))

# 수동 패턴: 행 번호 -> 정규식 목록(하나라도 맞으면 그 장에 나타남)
# 기본: 글자 자동 생성이 어려우므로 모든 행을 수동으로 적는다.
P = {}
def add(line, *pats): P[line] = pats
NOTFONT = r'(?<!\\mathsf )(?<!\\mathfrak )(?<!\\mathcal )(?<!\\mathrm )(?<!\\mathbf )(?<!\\mathbb )(?<!\\mathscr )(?<![A-Za-z\\])'
def plain(letter):
    # 일반 이탤릭 글자(앞에 글꼴 매크로·글자 없음)
    return NOTFONT + re.escape(letter) + r'(?![A-Za-z])'
def greek(cmd):
    return r'\\' + cmd + r'(?![A-Za-z])'

add(49, plain('a')+r'_')                                   # a_i
add(50, plain('b')+r'_\{?[^{}]*?(?:\\ell|k|y|Y|j|0|1|2|c|m)')  # b_{n,ell}
add(51, plain('b')+r'\^\\sigma')
add(52, plain('b')+r'(?:_\{?\w+\}?)?\^\{\(2\)\}')
add(53, plain('b')+r'\^\{?T\}?')
add(54, plain('b')+r'\^\\circ')
add(55, plain('c')+r'_(?!\{?\\mathrm)')                    # c_m(Y)  (c^{(2)} 제외는 아래 후처리)
add(56, plain('c')+r'(?:_\{?\w+\}?)?\^\{\(2\)\}')
add(57, plain('d')+r'_\{?(?:i|j|n|1|\\sigma|\\sigma_i|r|s|u|v)\}?(?![,])')   # d_i
add(58, plain('d')+r'_\{[^{}]*,[^{}]*\}')                  # d_{n,k}
add(59, plain('d')+r'\^\\star')
add(60, plain('e')+r'_\{?[nmt]')                           # e_n
add(61, r'\\ell\^\\?\*|\\ell\^\\ast|\\ell\^\{\\ast\}|\\ell\^\{\*\}')
add(62, plain('f')+r'(?![_^(])', plain('f')+r'\(')          # f
add(63, plain('g')+r'\(')                                  # g(x)
add(64, plain('h')+r'_')                                   # h_i
add(65, plain('k')+r'_\{?n\}?(?![A-Za-z])')                # k_n
add(66, plain('k')+r'_0', plain('k')+r'\^\\ast', plain('k')+r'\^\*')
add(67, plain('m')+r'_\{\\mathrm\{fb\}\}')
add(68, plain('m')+r'_1\(')
add(69, plain('m')+r'_0')
add(70, plain('m')+r'\^\\flat')
add(71, plain('n')+r'\^\\sharp', plain('n')+r'\^\\flat', plain('n')+r'\^\\circ')
add(72, plain('n')+r'_\{\\mathrm\s*\{?X')
add(73, plain('n')+r'_\{\\mathrm\{PD')
add(74, plain('p')+r'_')                                   # p_n
add(75, plain('q')+r'_\{\\max\}', plain('q')+r'_\\max')
add(76, plain('q')+r'(?:\^\\circ)?_\{\\mathrm\{fb')
add(77, plain('r')+r'_0')
add(78, plain('s')+r'\^\{?T\}?')
add(79, plain('s')+r'_(?!\{?\\mathrm)(?!\{?\\max)')         # s_m(y) (s^{...} 제외 후처리)
add(80, plain('s')+r'\^\{?\\mathrm\s*\{?F\b')
add(81, plain('s')+r'\^\{\\mathrm\{low\}\}')
add(82, r'\\tilde s\^\{\\mathrm\{env\}\}')
add(83, plain('s')+r'\^\{\\mathrm\{cf\}\}')
add(84, r'(?<!\\tilde )'+plain('s')+r'\^\{\\mathrm\{env\}\}')
add(85, plain('s')+r'\^\{?\\mathrm\s*\{?W\}?\}?_')
add(86, plain('t')+r'_\{?[uvw]\}?')                        # t_v
add(87, plain('t')+r'_0\(')
add(88, plain('t')+r'\^\\dagger')
add(89, plain('w')+r'_')                                   # w_m
add(90, plain('x')+r'(?![_^(A-Za-z])', r'\\hat x')         # x, hat x
add(91, plain('x')+r'_\{?\w+\}?\(')                        # x_t(y)
add(92, plain('x')+r'_\\ast', plain('x')+r'_\*')
add(93, plain('y')+r'_0')
add(94, plain('A')+r'_\{[^{}]*,[^{}]*\}', plain('A')+r'_\{?0,')   # A_{n,ell}
add(95, plain('A')+r'\^\\sigma')
add(96, plain('A')+r'_\{?\\?\w+\}?\((?:x|z|T)')             # A_ell(x)
add(97, plain('A')+r'\^\{?c\}?_')
add(98, r'\\bar A_')
add(99, plain('A')+r'\^\{\(t\)\}', plain('A')+r'\^\\circ_', plain('A')+r'\^\\diamond_')
add(100, plain('A')+r'\^\{\\diamond,\\mathrm\{up\}\}', plain('A')+r'\^\\diamond_\{\\mathrm\{dec\}\}')
add(101, plain('B')+r'_\{')                                # B_{n,m}
add(102, plain('C')+r'_\{?[nk]')                           # C_k(x), C_{n,k}
add(103, plain('D')+r'_\{?k\}?(?![A-Za-z])')               # D_k
add(104, plain('E')+r'_\{', plain('E')+r'2_')              # E_{n,k}, E2
add(105, plain('F')+r'(?![_^(])')                          # F forest
add(106, plain('G')+r'(?![_^(])', plain('G')+r'_\{?[nN]')  # G
add(107, plain('H')+r'_\{?[ky]\}?(?:\(|(?![A-Za-z]))')      # H_k
add(108, plain('I')+r'_\{?[uvw]')
add(109, plain('J')+r'_\{?[nmt]\}?\(')                     # J_n(z)
add(110, plain('J')+r'\^\{?\\mathrm\s*\{?G')
add(111, plain('K')+r'_\{?[nmN]\}?\(')
add(112, plain('L')+r'(?![_^(A-Za-z])')                    # L chain length
add(113, plain('M')+r'(?:_\{?[nmNt0]\}?)?(?![_^A-Za-z])', plain('M')+r'\(\\alpha')   # M
add(114, plain('M')+r'\(F\)')
add(115, plain('M')+r'\^\{?\\#\}?')
add(116, plain('M')+r'\^\{?T\}?_')
add(117, plain('P')+r'_\{?[a-zA-Z0-9\\\'+^{}]*\}?\(k\)', plain('P')+r'_\{?\w+\}?\(')   # P_t(k)
add(118, plain('P')+r'\^\+_')
add(119, plain('P')+r'\^\{\\theta\\dagger\}')
add(120, plain('P')+r'\^\{?\\theta\}?_')
add(121, plain('Q')+r'_\{?[\\a-zA-Z0-9-]+\}?\(x\)', plain('Q')+r'_\{?(?:\\ell|k-1|k|y-1|y)\}?(?![A-Za-z])')
add(122, plain('R')+r'_\{?[jJi0h]')
add(123, plain('S')+r'_\{?[0-9ijJLh]')
add(124, plain('T')+r'_\{?(?:\\ell|k|y|Y|j|k-1|y-1)\}?(?:\(|(?![A-Za-z]))')   # T_ell(x)
add(125, plain('T')+r'\((?:x|z|\\rho|\\mathfrak|t|1|u)', plain('T')+r'(?![_^(A-Za-z])')   # T(x)
add(126, plain('U')+r'_\{?[uvw]')
add(127, plain('V')+r'\((?:x|t|v|u)\)')
add(128, plain('W')+r'_\{?[nmN]\}?\(')
add(129, plain('X')+r'(?:_\{?[nN]\}?)?(?![_^A-Za-z(])')
add(130, plain('Z')+r'_\{?[ky]\}?(?:\(|(?![A-Za-z]))')
add(131, greek('alpha'))
add(132, greek('beta')+r'_')
add(133, greek('chi')+r'_')
add(134, greek('delta')+r'_\{?[tsmnk\\]')
add(135, greek('Gamma')+r'\^')
add(136, greek('Gamma')+r'_')
add(137, greek('gamma')+r'_')
add(138, greek('kappa')+r'_')
add(139, greek('lambda')+r'(?![_^A-Za-z])')
add(140, greek('Lambda')+r'_\{?\\mathrm\s*\{?w')
add(141, greek('mu')+r'_')
add(142, greek('nu')+r'_[01]')
add(143, greek('nu')+r'_\{\\min', r'\\bar\\nu')
add(144, greek('Omega')+r'(?:\(|_)')
add(145, greek('omega')+r'(?:_|\^)', r'\\tilde\\omega')
add(146, greek('Phi')+r'(?![A-Za-z])')
add(147, greek('pi')+r'\^\{?0')
add(148, greek('pi')+r'_\{?\w+\}?\((?![^)]*,)')             # pi_n(m) single arg
add(149, greek('Pi')+r'(?![_^A-Za-z])')
add(150, greek('Pi')+r'_\{?[jJi]\}?\(')
add(151, greek('Pi')+r'\^\{\\mathrm\{up\}\}')
add(152, greek('pi')+r'_2\(')
add(153, greek('pi')+r'_\{?\w+\}?\([^)]*,')               # pi_n(t1,t2)
add(154, greek('pi')+r'\^\{\\mathrm\{two\}\}')
add(155, greek('Psi')+r'(?:\(|(?![_^A-Za-z]))')
add(156, greek('psi')+r'\(')
add(157, greek('Psi')+r'\^\{\\mathrm\{low\}\}_')
add(158, greek('Psi')+r'\^\{\\mathrm\{low\}\}\(')
add(159, greek('rho')+r'_\{?[ky]')
add(160, greek('sigma')+r'(?![A-Za-z])')
add(161, greek('tau')+r'(?![A-Za-z])')
add(162, greek('theta')+r'_\{?\w+\}?\(')
add(163, greek('Theta')+r'_(?!\{?\\mathrm)' , greek('Theta')+r'_\{?[nNmt]\}?(?![A-Za-z])')
add(164, greek('Theta')+r'\^\\circ')
add(165, greek('Upsilon'), r'\\hat\\Upsilon')
add(166, greek('varkappa')+r'_')
add(167, greek('varphi')+r'\^\\flat')
add(168, greek('varrho')+r'_\{?[tsm]', greek('varrho')+r'\^\{?\\mathrm\s*\{?[HL]', greek('varrho')+r'_\{\\min', greek('varrho')+r'\^\{\\mathrm\{lb')
add(169, greek('varrho')+r'\^\\dagger')
add(170, greek('varsigma')+r'_')
add(171, greek('vartheta')+r'(?![_A-Za-z])', greek('vartheta')+r'_0')
add(172, greek('vartheta')+r'_\{\\mathrm\{lb')
add(173, greek('Xi')+r'_')
add(174, greek('xi')+r'(?![A-Za-z])')
add(175, greek('zeta')+r'(?!\()(?![A-Za-z])')
add(176, r'\\mathcal A_')
add(177, r'\\mathcal B_')
add(178, r'\\mathcal C_')
add(179, r'\\mathcal D\(')
add(180, r'\\mathcal F(?:_|\^)')
add(181, r'\\mathcal G(?:_|\^)')
add(182, r'\\mathcal H_\{?\\mathrm\s*\{?B')
add(183, r'\\mathcal I_')
add(184, r'\\mathcal J_[1-4]')
add(185, r'\\mathcal K_')
add(186, r'\\mathcal M(?:_|\^)')
add(187, r'\\mathcal N_')
add(188, r'\\mathcal O_')
add(189, r'\\mathcal P_(?!\{?\\mathrm)')
add(190, r'\\mathcal P\^\{\(k\)\}')
add(191, r'\\mathcal Q_')
add(192, r'\\mathcal R_2')
add(193, r'\\mathcal S_')
add(194, r'\\mathcal T_')
add(195, r'\\mathcal U_')
add(196, r'\\mathcal V_')
add(197, r'\\mathcal W\^')
add(198, r'\\mathcal Y(?:_|\^)')
add(199, r'\\mathcal Z(?![A-Za-z_^])')
add(200, r'\\mathfrak a_', r'\\tilde\{\\mathfrak a\}')
add(201, r'\\mathfrak a\^\\circ')
add(202, r'\\mathfrak a\^\{?\\rho')
add(203, r'\\mathfrak A(?:_|\^)')
add(204, r'\\mathfrak b_')
add(205, r'\\mathfrak B(?:_|\^)')
add(206, r'\\mathfrak c_0')
add(207, r'\\mathfrak D\^\{\\mathrm\{src')
add(208, r'\\mathfrak D_')
add(209, r'\\mathfrak d_', r'\\bar\{\\mathfrak d\}')
add(210, r'\\mathfrak E_')
add(211, r'\\mathfrak f_')
add(212, r'\\mathfrak g\(')
add(213, r'\\mathfrak H_')
add(214, r'\\mathfrak h_')
add(215, r"\\mathfrak K(?:_|\^|')")
add(216, r'\\mathfrak k_')
add(217, r'\\mathfrak l_')
add(218, r'\\mathfrak m\(')
add(219, r'\\mathfrak p_')
add(220, r'\\mathfrak P_\{?\w+\}?\((?!\\infty)')
add(221, r'\\mathfrak P_\{?\w+\}?\(\\infty')
add(222, r'\\mathfrak Q\(')
add(223, r'\\mathfrak r_')
add(224, r'\\mathfrak R_')
add(225, r'\\mathfrak R\^\{\\mathrm\{low')
add(226, r'\\mathfrak S_')
add(227, r'\\mathfrak s_')
add(228, r'\\mathfrak s\^\{\\mathrm\{fr')
add(229, r'\\mathfrak s\^\{\\mathrm\{up')
add(230, r'\\mathfrak s\^\{\\mathrm\{low')
add(231, r'\\mathfrak T_')
add(232, r'\\mathfrak u_')
add(233, r'\\mathfrak v_')
add(234, r'\\mathfrak V_')
add(235, r'\\mathfrak w_', r'\\tilde\{\\mathfrak w\}')
add(236, r'\\mathfrak X(?:_|\^)')
add(237, r'\\mathfrak z_')
add(238, r'\\mathsf a_')
add(239, r'\\mathsf b_')
add(240, r'\\mathsf B\^\+')
add(241, r'\\mathsf c_\\Psi')
add(242, r'\\mathsf f_1')
add(243, r'\\mathsf\{FLQ\}')
add(244, r'\\mathsf\{FS\}')
add(245, r'\\mathsf g_')
add(246, r'\\mathsf H\^')
add(247, r'\\mathsf h_')
add(248, r'\\mathsf j_')
add(249, r'\\mathsf L_')
add(250, r'\\mathsf\{LH\}')
add(251, r'\\mathsf\{LRP\}')
add(252, r'\\mathsf m_')
add(253, r'\\mathsf n_')
add(254, r'\\mathsf P(?![_A-Za-z])')
add(255, r'\\mathsf P_')
add(256, r'\\mathsf Q(?![_^A-Za-z])', r'\\mathsf Q_', r'\\mathsf Q\(')
add(257, r'\\mathsf Q\^\\star')
add(258, r'\\mathsf r_')
add(259, r'\\mathsf S_')
add(260, r'\\mathsf s_')
add(261, r'\\mathsf\{SRC\}')
add(262, r'\\mathsf t_')
add(263, r'\\mathsf u\(')
add(264, r'\\mathsf\{UL\}', r'\\mathsf V(?![A-Za-z])')
add(265, r"\\mathsf v(?:\(|\^|'|_)")
add(266, r'\\mathsf W(?![_A-Za-z])', r'\\mathsf W\^\\sharp')
add(267, r'\\mathsf w_0')
add(268, r'\\mathsf W_L')
add(269, r'\\mathsf x_')
add(270, r"\\mathsf X(?:\^|')")
add(271, r'\\mathsf z_')
add(272, r'\\mathrm\{Bd\}\^\{?\\mathrm\s*\{?V')
add(273, r'\\mathrm\{Bd\}\^\{?\\mathrm\s*\{?S')
add(274, r'\\mathrm\{Bd\}\^\{?\\mathrm\s*\{?T')
add(275, r'\\mathrm\{Bor\}\((?!\\mathfrak Z)')
add(276, r'\\mathrm\{Bor\}\^\{\*')
add(277, r'\\mathrm\{Bor\}\^\{\\mathrm\{tail')
add(278, r'\\mathrm\{Bor\}_\{?>')
add(279, r'\\mathrm\{Bor\}_\{?\\le')
add(280, r'\\mathrm\{BV\}')
add(281, r'\\mathrm\{cl\}')
add(282, r'\\mathrm\{Conv\}', r'\\mathrm\{Kink\}')
add(283, r'\\mathrm\{DD\}(?!L)')
add(284, r'\\mathrm\{DDL\}\(')
add(285, r'\\mathrm\{DDL\}(?:_2|\^\\natural)')
add(286, r'\\mathrm\{dec\}')
add(287, r'\\mathrm\{dup\}')
add(288, r'\\mathrm\{fb\}')
add(289, r'\\mathrm\{FL\}(?!\^\{\(1\)\})')
add(290, r'\\mathrm\{FL\}\^\{\(1\)\}')
add(291, r'\\mathrm\{flat\}')
add(292, r'\\mathrm\{Flow\}')
add(293, r'\\mathrm\{Gr\}')
add(294, r'\\mathrm\{He\}')
add(295, r'\\mathrm\{hz\}')
add(296, r'\\mathrm\{IH\}')
add(297, r'\\mathrm\{inc\}')
add(298, r'\\mathrm\{inh\}')
add(299, r'\\mathrm\{KD\}')
add(300, r'\\mathrm\{km\}')
add(301, r'\\mathrm\{land\}')
add(302, r'\\mathrm\{LB\}', r'\\mathrm\{LOW\}')
add(303, r'\\mathrm\{Lc\}')
add(304, r'\\mathrm\{Left\}')
add(305, r'\\mathrm\{Lip\}')
add(306, r'\\mathrm\{LP\}')
add(307, r'\\mathrm\{merge\}')
add(308, r'\\mathrm\{need\}', r'\\mathrm R_m')
add(309, r'\\mathrm\{nf\}')
add(310, r'\\mathrm\{OB\}')
add(311, r'\\mathrm\{PAIR\}')
add(312, r'\\mathrm\{Pcor\}')
add(313, r'\\mathrm\{PF\}')
add(314, r'\\mathrm\{PM\}')
add(315, r'\\mathrm\{pos\}')
add(316, r'\\mathrm\{POS\}')
add(317, r'\\mathrm\{pr\}')
add(318, r'\\mathrm\{Quad\}', r'\\mathrm\{Stem\}')
add(319, r'\\mathrm\{rb\}')
add(320, r'\\mathrm\{regen\}')
add(321, r'\\mathrm\{rq\}')
add(322, r'\\mathrm\{Ren\}')
add(323, r'\\mathrm\{Res\}')
add(324, r'\\mathrm\{src\}')
add(325, r'\\mathrm\{Stays\}(?!\^\{\\mathrm\{(?:adm|up)\}\})')
add(326, r'\\mathrm\{Stays\}\^\{\\mathrm\{adm')
add(327, r'\\mathrm\{Stays\}\^\{\\mathrm\{up')
add(328, r'\\mathrm\{tail\}')
add(329, r'\\mathrm\{tilt\}')
add(330, r'\\mathrm\{top\}')
add(331, r'\\mathrm\{tr\}')
add(332, r'\\mathrm\{WIN\}')
add(333, r'\\Pr_\{?[nNmt]', r'\\mathbb E_\{?[nNmt]', r'\\Pr_\{?[a-z]', r'\\mathbb E_\{?[a-z]')
add(334, r'\\Pr_\{?\\mathrm\s*\{?B')
add(335, r'\\Pr\^\{?T\}?_', r'\\mathbb E\^\{?T\}?_')
add(336, r'\\Pr\^\{?y\}?\(')
add(337, r'\\Pr\^\{?y(?!\))', r'\\mathbb E\^\{?y')
add(338, r'\\Pr\^\{?\\sigma', r'\\mathbb E\^\{?\\sigma')
add(339, r'\(\\mathrm G\)_')
add(340, r'\(\\star\)\(')

def found_in(segs, pats):
    hits = []
    for s in segs:
        for p in pats:
            if re.search(p, s):
                hits.append(s); break
    return hits

verbose = '-v' in sys.argv
only = None
for a in sys.argv[1:]:
    if a.isdigit(): only = int(a)

for (ln, glyph, chs) in rows:
    if only and ln != only: continue
    if ln not in P:
        print(f'[{ln}] NO PATTERN  {glyph}'); continue
    decl = parse_chs(chs)
    actual = {}
    for c in range(1,12):
        h = found_in(CHM[c], P[ln])
        if h: actual[c] = h
    act = set(actual)
    app = {k for k,v in APM.items() if found_in(v, P[ln])}
    missing = act - decl
    extra = decl - act
    if missing or extra or only:
        print(f'[{ln}] {glyph}')
        print(f'   declared={sorted(decl)} actual={sorted(act)} +{sorted(missing)} -{sorted(extra)} appendix={sorted(app)}')
        for c in sorted(missing) if not only else sorted(act):
            for s in actual[c][:3 if not verbose else 10]:
                print(f'     ch{c}: {s[:160]}')
