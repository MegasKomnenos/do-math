# -*- coding: utf-8 -*-
# 장부 1.2 「쓰이는 장」을 장 파일(+그 장의 부록 D)에서 기호의 핵을 찾아 견준다. 결과는 후보일 뿐 — 원문을 열어 확인한다.
import re, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체23_R13_lib import *
rows=json.load(open(os.path.join(base,"scripts","수학검사2","검토전체23_R13_rows12.json"),encoding="utf-8"))
def norm(t):
    t=re.sub(r"\\(mathsf|mathfrak|mathcal|mathrm|mathbb|mathscr)\{([A-Za-z])\}", r"\\\1 \2", t)
    for _ in range(3):
        t=re.sub(r"([_^])\{([A-Za-z0-9])\}", r"\1\2", t)
    t=t.replace("\\prime","′")
    return t
texts={}
for f in files+[a for a in appx if a.startswith("부록D")]:
    ch=chap_of_file[f]
    texts.setdefault(ch,[]).append((f,norm(rd(f))))
FONT=re.compile(r"\\(?:mathsf|mathfrak|mathcal|mathrm|mathbb|mathscr|operatorname|text|hat|tilde|bar|widehat|widetilde|dot)\s*\{?$")
def plain(letter, suf=""):
    rx=re.compile(r"(?<![\\A-Za-z])"+letter+suf)
    def f(t):
        out=[]
        for m in rx.finditer(t):
            if FONT.search(t[max(0,m.start()-14):m.start()]): continue
            out.append(m.start())
        return out
    return f
def R(p):
    rx=re.compile(p)
    return lambda t:[m.start() for m in rx.finditer(t)]
def any_(*fs):
    return lambda t: sorted(set(sum((f(t) for f in fs),[])))
P={}
P[49]=plain('a',r'_'); P[50]=plain('b',r'_\{'); P[51]=plain('b',r'\^\\sigma'); P[52]=plain('b',r'\^\{\(2\)\}')
P[53]=plain('b',r'\^T'); P[54]=plain('c',r'_(?:[a-zA-Z0-9]|\{[^}]*\})\('); P[55]=plain('c',r'\^\{\(2\)\}')
P[56]=plain('d',r'_(?:[a-z0-9](?![a-z,(])|\{\\sigma)'); P[57]=plain('d',r'_\{[^}]*,[^}]*\}'); P[58]=plain('d',r'\^\\star')
P[59]=plain('e',r'_'); P[60]=R(r'\\ell\^(?:\\ast|\*)'); P[61]=R(r'\\ell_n(?![A-Za-z])')
P[63]=plain('g',r'\('); P[64]=plain('h',r'_'); P[65]=plain('k',r'_n(?![A-Za-z])')
P[66]=any_(plain('k',r'_0'),plain('k',r'\^(?:\\ast|\*)')); P[67]=R(r'm_\{\\mathrm\{fb\}\}'); P[68]=plain('m',r'_0'); P[69]=plain('m',r'\^\\flat')
P[70]=plain('n',r'\^\\sharp'); P[71]=plain('n',r'\^\{\\mathrm G\}'); P[72]=plain('p',r'_'); P[73]=R(r'q_\{\\max\}'); P[74]=R(r'q_\{\\mathrm\{fb\}\}')
P[75]=plain('s',r'\^T'); P[76]=plain('s',r'_(?:[a-zA-Z0-9]|\{[^}]*\})\('); P[77]=plain('s',r'\^\{\\mathrm\{low\}\}'); P[78]=plain('s',r'\^\{\\mathrm\{cf\}\}'); P[79]=plain('s',r'\^\{\\mathrm W\}')
P[80]=plain('t',r'_v'); P[81]=any_(plain('t',r'_0'),R(r'\\mathrm\{wid\}')); P[82]=plain('w',r'_'); P[83]=R(r'\\hat x'); P[84]=plain('x',r'_(?:[a-z]|\{[^}]*\})\('); P[85]=plain('x',r'_(?:\\ast|\*)')
P[86]=plain('y',r'_0'); P[87]=plain('A',r'_\{[^}]*,[^}]*\}'); P[88]=plain('A',r'\^\\sigma'); P[89]=plain('A',r'_(?:\\ell|[a-z]|\{[^},]*\})\(')
P[90]=plain('A',r'(?:_[a-z0-9]|_\{[^}]*\})?\['); P[91]=plain('A',r'\^c'); P[92]=plain('B',r'_\{[^}]*,[^}]*\}'); P[93]=plain('C',r'_')
P[94]=plain('E',r'2?_\{[^}]*,[^}]*\}'); P[95]=plain('F',r'(?![A-Za-z_^])'); P[96]=plain('G',r'(?![A-Za-z_^])'); P[97]=plain('H',r'_'); P[98]=plain('I',r'_v')
P[99]=plain('J',r'_'); P[100]=plain('J',r'\^\{\\mathrm G\}'); P[101]=plain('L',r'(?![A-Za-z_^])'); P[102]=plain('M',r'(?![A-Za-z^])'); P[103]=plain('M',r'\(F'); P[104]=plain('M',r'\^(?:\\#|\{\\#\})'); P[105]=plain('M',r'\^T')
P[106]=plain('P',r'_[a-z{]'); P[107]=plain('Q',r'_'); P[108]=plain('R',r'_'); P[109]=plain('S',r'_'); P[110]=plain('T',r'_'); P[111]=plain('T',r'\('); P[112]=plain('T',r'\^\{(?:\\le|>|\\gt)')
P[113]=plain('U',r'_'); P[114]=plain('V',r'\('); P[115]=plain('W',r'_'); P[116]=plain('X',r'(?![A-Za-z^])'); P[117]=plain('Z',r'_')
P[118]=R(r'\\alpha(?![A-Za-z])'); P[119]=R(r'\\beta_'); P[120]=R(r'\\chi_'); P[121]=R(r'\\delta_'); P[122]=R(r'\\epsilon_'); P[123]=R(r'\\Gamma\^'); P[124]=R(r'\\Gamma_')
P[125]=R(r'\\kappa_'); P[126]=R(r'\\lambda(?![A-Za-z])'); P[127]=R(r'\\widehat\s*\\Lambda'); P[128]=R(r'\\mu_'); P[129]=any_(R(r'\\nu_\{\\min\}'),R(r'\\bar\s*\\nu'))
P[130]=R(r'\\Omega(?![A-Za-z])'); P[131]=R(r'\\omega(?![A-Za-z])'); P[132]=R(r'\\Phi(?![A-Za-z])'); P[133]=R(r'\\pi\^0'); P[134]=R(r'\\pi_'); P[135]=R(r'\\Pi(?![A-Za-z_^])'); P[136]=R(r'\\Pi_')
P[137]=R(r'\\Pi\^\{\\mathrm\{up\}\}'); P[138]=R(r'\\pi\^\{\\mathrm\{two\}\}'); P[139]=R(r'\\Psi\('); P[140]=R(r'\\Psi\^\{\\mathrm\{low\}\}'); P[141]=R(r'\\rho_'); P[142]=R(r'\\sigma(?![A-Za-z])'); P[143]=R(r'\\tau(?![A-Za-z])')
P[144]=R(r'\\theta_'); P[145]=R(r'\\Theta_'); P[146]=R(r'\\varkappa_'); P[147]=R(r'\\varsigma_'); P[148]=R(r'\\vartheta(?![A-Za-z^]|_\{)'); P[149]=R(r'\\vartheta_\{\\mathrm\{lb\}\}'); P[150]=R(r'\\vartheta\^\{\\mathrm T\}')
P[151]=R(r'\\Xi_'); P[152]=R(r'\\xi(?![A-Za-z])')
for ln,c in [(153,'A'),(154,'B'),(155,'D'),(156,'E'),(157,'G'),(158,'I'),(159,'K'),(160,'M'),(161,'N'),(164,'R'),(165,'S'),(166,'T'),(167,'U'),(168,'V'),(169,'W'),(170,'X'),(171,'Z')]:
    P[ln]=R(r'\\mathcal '+c+r'(?![A-Za-z])')
P[162]=R(r'\\mathcal P_'); P[163]=R(r'\\mathcal P\^\{\(')
P[172]=R(r'\\mathfrak a_'); P[173]=R(r'\\mathfrak a\^\\circ'); P[174]=R(r'\\mathfrak a\^\\rho'); P[175]=R(r'\\mathfrak A(?![A-Za-z])')
for ln,c in [(176,'b'),(177,'c'),(180,'E'),(181,'f'),(182,'H'),(183,'k'),(184,'m'),(185,'p'),(188,'Q'),(189,'r'),(192,'S'),(197,'T'),(198,'u'),(199,'v'),(200,'w'),(201,'W')]:
    P[ln]=R(r'\\mathfrak '+c+r'(?![A-Za-z])')
P[178]=R(r'\\mathfrak D\^\{\\mathrm\{src\}\}'); P[179]=R(r'\\mathfrak D_')
P[186]=R(r'\\mathfrak P_(?:[a-zA-Z0-9]|\{[^}]*\})\((?!\\infty)'); P[187]=R(r'\\mathfrak P_(?:[a-zA-Z0-9]|\{[^}]*\})\(\\infty')
P[190]=R(r'\\mathfrak R_'); P[191]=R(r'\\mathfrak R\^\{\\mathrm\{low\}\}')
P[193]=R(r'\\mathfrak s_'); P[194]=R(r'\\mathfrak s\^\{\\mathrm\{fr\}\}'); P[195]=R(r'\\mathfrak s\^\{\\mathrm\{up\}\}'); P[196]=R(r'\\mathfrak s\^\{\\mathrm\{low\}\}')
P[202]=R(r'\\mathsf a_'); P[203]=R(r'\\mathsf b_'); P[204]=R(r'\\mathsf c_\\Psi'); P[205]=R(r'\\mathsf f_1'); P[206]=R(r'\\mathsf\{FLQ\}'); P[207]=R(r'\\mathsf g_'); P[208]=R(r'\\mathsf j_')
P[209]=R(r'\\mathsf\{LH\}'); P[210]=R(r'\\mathsf m_'); P[211]=R(r'\\mathsf n_'); P[212]=R(r'\\mathsf P(?![_A-Za-z])'); P[213]=R(r'\\mathsf P_[LXCR]'); P[214]=R(r'\\mathsf Q(?:\(|_R)')
P[215]=R(r'\\mathsf Q\^(?:\\star|\{\\star\})'); P[216]=R(r'\\mathsf r_'); P[217]=R(r'\\mathsf s_'); P[218]=R(r'\\mathsf t_'); P[219]=R(r'\\mathsf u(?![A-Za-z])'); P[220]=R(r'\\mathsf V(?![A-Za-z])')
P[221]=R(r'\\mathsf v(?![A-Za-z])'); P[222]=R(r'\\mathsf W(?![A-Za-z]|_L)'); P[223]=R(r'\\mathsf w_0'); P[224]=R(r'\\mathsf W_L'); P[225]=R(r'\\mathsf x_'); P[226]=R(r'\\mathsf z_')
def rm(name,suf=""): return R(r'\\mathrm\{'+name+r'\}'+suf)
P[227]=rm('apex'); P[228]=rm('Bd',r'\^\{\\mathrm V\}'); P[229]=rm('Bd',r'\^\{\\mathrm S\}'); P[230]=rm('Bd',r'\^\{\\mathrm T\}')
P[231]=rm('Bor',r'\('); P[232]=rm('Bor',r'\^\{\*'); P[233]=rm('Bor',r'\^\{\\mathrm\{tail\}\}'); P[234]=rm('Bor',r'_(?:>|\{>\}|\\gt|\{\\gt\})'); P[235]=rm('Bor',r'_(?:\\le|\{\\le\})')
P[236]=rm('BV'); P[237]=rm('cl'); P[238]=rm('DD'); P[239]=rm('DDL'); P[240]=rm('dup'); P[241]=rm('fb',r'\('); P[242]=rm('Flow'); P[243]=rm('Gr'); P[244]=rm('He'); P[245]=rm('hf'); P[246]=rm('hz')
P[247]=rm('IH'); P[248]=rm('inc'); P[249]=rm('inh'); P[250]=rm('KD'); P[251]=rm('km'); P[252]=any_(rm('LB'),rm('LOW')); P[253]=rm('lc'); P[254]=rm('Left'); P[255]=rm('Lip'); P[256]=rm('loss'); P[257]=rm('nf')
P[258]=rm('pd'); P[259]=rm('PF'); P[260]=rm('PM',r'_'); P[261]=rm('pos'); P[262]=rm('POS'); P[263]=any_(rm('Quad'),rm('Stem')); P[264]=rm('rb'); P[265]=rm('rq'); P[266]=rm('Ren'); P[267]=rm('Res'); P[268]=rm('sm')
P[269]=rm('src',r'_'); P[270]=rm('Stays',r'(?!\^\{\\mathrm\{(?:adm|up)\}\})'); P[271]=rm('Stays',r'\^\{\\mathrm\{adm\}\}'); P[272]=rm('Stays',r'\^\{\\mathrm\{up\}\}'); P[273]=rm('stp'); P[274]=rm('tail'); P[275]=rm('tilt')
P[276]=rm('top'); P[277]=rm('vm'); P[278]=rm('WIN'); P[279]=rm('wg'); P[280]=any_(R(r'\\Pr_(?!\{\\mathrm B\}|\\mathrm B)'),R(r'\\mathbb E_')); P[281]=R(r'\\Pr_\{?\\mathrm\{? ?B\}?\}?')
P[282]=any_(R(r'\\Pr\^T'),R(r'\\mathbb E\^T')); P[283]=R(r'\\Pr\^y\('); P[284]=any_(R(r'\\Pr\^y'),R(r'\\mathbb E\^y')); P[285]=any_(R(r'\\Pr\^\{?\\sigma'),R(r'\\mathbb E\^\{?\\sigma'))
P[286]=R(r'\(\\mathrm G\)'); P[287]=R(r'\(\\star\)')
if __name__=="__main__":
    args=sys.argv[1:]
    show = args and args[0]=="show"
    only = set(int(x) for x in args[1:]) if show else None
    for r in rows:
        ln=r["line"]
        if ln not in P:
            if not show: print(ln,r["sym"],"— 기계 검사 없음")
            continue
        claimed=set(int(x) for x in re.findall(r"\d+",r["chs"]))
        found={}
        for ch in texts:
            n=0; byf={}
            for f,t in texts[ch]:
                k=len(P[ln](t)); n+=k
                if k: byf[f]=k
            if n: found[ch]=byf
        fs=set(found)
        if show:
            if ln in only:
                print(ln,r["sym"],sorted(claimed),found)
                ctx=int(os.environ.get("CTX","70"))
                for ch in sorted(found):
                    for f,t in texts[ch]:
                        ps=P[ln](t)
                        for p in ps[:int(os.environ.get("MAXN","3"))]:
                            lno=t.count("\n",0,p)+1
                            print("   ",f,lno,"…"+t[max(0,p-ctx):p+ctx].replace("\n"," ")+"…")
            continue
        if fs!=claimed:
            print(ln,r["sym"],"| 표:",sorted(claimed),"| 표에만:",sorted(claimed-fs),"| 글에만:",{c:found[c] for c in sorted(fs-claimed)})
