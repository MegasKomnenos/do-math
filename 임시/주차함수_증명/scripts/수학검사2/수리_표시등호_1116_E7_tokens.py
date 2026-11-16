"""E7 보조 도구(읽기 전용): 장 파일의 백슬래시 명령 가운데 알려진 KaTeX 명령이 아닌 것을 센다
(예: `\\geR`처럼 관계 기호 뒤에 공백 없이 글자가 붙어 한 토큰이 된 자리).
사용: python -I 이_파일.py <md 파일들>
"""
import collections
import re
import sys

KNOWN = set("""alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta iota kappa varkappa lambda mu nu xi pi varpi
rho varrho sigma varsigma tau upsilon phi varphi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma Upsilon Phi Psi Omega
mathrm mathcal mathfrak mathsf mathbb mathbf mathscr operatorname text hat tilde bar underline widetilde overline vec dot
le ge leq geq lt gt ne neq approx sim simeq equiv subset subseteq supset in notin to mapsto cdot cdots ldots dots times pm mp
mid infty partial nabla sum prod int iint lim sup inf max min log ln exp sin cos tan cosh sinh tanh arctan sqrt frac dfrac
tfrac binom left right bigl bigr Bigl Bigr biggl biggr lvert rvert lVert rVert langle rangle lceil rceil lfloor rfloor sharp
flat natural ast star circ dagger prime bullet quad qquad tag label Pr mathop limits nolimits displaystyle textstyle
scriptstyle succ prec ll gg top perp forall exists neg lnot wedge vee cap cup setminus emptyset varnothing underbrace
overbrace stackrel overset underset substack colon ldotp cdotp vert Vert backslash big Big bigg Bigg dagger ddagger
operatorname* arg deg det dim gcd hom ker lg liminf limsup Pr sec csc cot coth sinh cosh tanh ell hbar imath jmath
mathit boldsymbol pmb not iff implies impliedby land lor longrightarrow Rightarrow Leftarrow Leftrightarrow leftarrow
rightarrow uparrow downarrow leftrightarrow longmapsto hookrightarrow nearrow searrow propto because therefore
dotsc dotsb dotsm dotsi ddots vdots lbrace rbrace lbrack rbrack lparen rparen urcorner llcorner
begin end aligned align cases pmatrix bmatrix vmatrix matrix array hline
smash phantom hphantom vphantom raisebox rule kern mkern mskip thinspace negthinspace enspace
color textcolor fbox boxed
""".split())


def main(files):
    for f in files:
        txt = open(f, encoding='utf-8').read()
        toks = collections.Counter(re.findall(r'\\([A-Za-z]+)', txt))
        bad = {t: c for t, c in toks.items() if t not in KNOWN}
        print(f, bad)
        for t in bad:
            for ln, line in enumerate(txt.split('\n'), 1):
                if '\\' + t in line:
                    i = line.index('\\' + t)
                    print(f'   {ln}: …{line[max(0, i - 40):i + 40]}…')


if __name__ == '__main__':
    main(sys.argv[1:])
