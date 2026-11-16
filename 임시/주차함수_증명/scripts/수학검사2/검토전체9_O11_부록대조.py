# -*- coding: utf-8 -*-
"""부록 A·C를 장부_v2와, 부록 B의 폴더 서술을 기록 폴더와 대조한다 (O11).
(1) 부록 A 행 ↔ 장부 1.2 행: 기호, 뜻, 정의 절
(2) 부록 C 낱말 표 ↔ 장부 3절: 첫 정의 절, 기록의 용어 ↔ 첫 판의 낱말
(3) 부록 C 셋째 표 ↔ 장부 7절
(4) 부록 C 둘째 표(기록 이름) ↔ 장부 4절
(5) 부록 B: 인용 기록의 evidence/producer, evidence/peer 존재 수
(6) 부록 A 기호의 정의 문맥 출력(수식 대조용)"""
import re, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:\math\임시\주차함수_증명"
def rows(path, start_pat=None, end_pat=None):
    out=[]; on = start_pat is None
    for l in open(path, encoding='utf-8'):
        if start_pat and re.match(start_pat, l): on=True; continue
        if end_pat and on and re.match(end_pat, l): on=False
        if on and l.startswith('| ') and not l.startswith('|---'):
            out.append([c.strip() for c in l.strip().strip('|').split(' | ')])
    return out
norm = lambda s: re.sub(r'\s+', '', s)

# (1)
print("### (1) 부록 A ↔ 장부 1.2")
A = [r for r in rows(BASE+r"\장v2\부록A.md") if r[0] != '기호']
L12 = rows(BASE+r"\장부_v2.md", r'^### 1\.2', r'^### 1\.3')
L12 = [r for r in L12 if r[0] != '글자(LaTeX)']
L11 = rows(BASE+r"\장부_v2.md", r'^### 1\.1', r'^### 1\.2')
print("A 행", len(A), "장부1.2 행", len(L12), "장부1.1 행", len(L11))
idx = {}
for r in L12 + L11:
    idx[norm(r[0])] = r
unmatched=[]
for r in A:
    key = norm(r[0])
    m = idx.get(key)
    if m is None:
        # 첫 기호만으로 재시도
        k2 = norm(r[0].split(',')[0])
        m = next((v for k,v in idx.items() if k.startswith(k2) or k2.startswith(k)), None)
    if m is None:
        unmatched.append(r[0]); continue
    # 장부 1.2: 글자|바탕|뜻|정의 절|쓰이는 장|첫 판|기록 ; 1.1: 글자|뜻|절|... (확인)
    if len(m) >= 7:
        lmean, lsec, lrec = m[2], m[3], m[6]
    else:
        lmean, lsec, lrec = m[1], m[2], m[-1]
    flags=[]
    if norm(lsec) != norm(r[2]): flags.append(f"절 다름 A:{r[2]} / 장부:{lsec}")
    if norm(lmean) != norm(r[1]): flags.append("뜻 다름")
    if norm(lrec) != norm(r[3]): flags.append("기록 글자 다름")
    if flags:
        print(f"\n- {r[0]}: " + '; '.join(flags))
        if "뜻 다름" in flags: print("   A :", r[1][:300]); print("   장부:", lmean[:300])
        if "기록 글자 다름" in flags: print("   A기록 :", r[3][:300]); print("   장부기록:", lrec[:300])
print("\n부록 A에 있으나 장부 1.1·1.2에 못 찾음:", unmatched)
aset = {norm(r[0]) for r in A}
print("장부 1.2에 있으나 부록 A에 없음:", [r[0] for r in L12 if norm(r[0]) not in aset][:60])

# (2)
print("\n### (2) 부록 C 낱말 표 ↔ 장부 3절")
C1 = [r for r in rows(BASE+r"\장v2\부록C.md", r'^### 낱말', r'^### 기록이') if r[0] != '이 글의 용어']
L3 = [r for r in rows(BASE+r"\장부_v2.md", r'^## 3\.', r'^## 4\.') if r[0] != '낱말']
l3 = {norm(r[0]): r for r in L3}
for r in C1:
    m = l3.get(norm(r[0]))
    if m is None:
        print(f"- 장부 3절에 같은 낱말 행 없음: {r[0]}"); continue
    fl=[]
    if norm(m[2]) != norm(r[2]): fl.append(f"절 다름 C:{r[2]} / 장부:{m[2]}")
    if norm(m[3]) != norm(r[1]): fl.append(f"기록 용어 다름 C:{r[1]} / 장부 첫판:{m[3]}")
    if fl: print(f"- {r[0]}: " + '; '.join(fl))

# (3)
print("\n### (3) 부록 C 셋째 표 ↔ 장부 7절")
C3 = [r for r in rows(BASE+r"\장v2\부록C.md", r'^### 기록의 글자', None) if r[0] != '이 글의 글자']
L7 = [r for r in rows(BASE+r"\장부_v2.md", r'^## 7\.', r'^## 8\.') if r[0] != '이 글의 글자']
print("C3 행", len(C3), "장부7 행", len(L7))
l7 = {norm(r[0]): r for r in L7}
for r in C3:
    m = l7.get(norm(r[0]))
    if m is None: print(f"- 장부 7절에 없음: {r[0][:80]}"); continue
    fl=[]
    for i,name in ((1,'기록'),(2,'기록 글자'),(3,'이동')):
        if norm(m[i]) != norm(r[i]): fl.append(name)
    if fl:
        print(f"- {r[0][:60]}: 다름 {fl}")
        for i in range(1,4):
            if norm(m[i]) != norm(r[i]): print(f"    C :{r[i][:200]}\n    장부:{m[i][:200]}")
c3set={norm(r[0]) for r in C3}
print("장부 7절에 있으나 C에 없음:", [r[0][:50] for r in L7 if norm(r[0]) not in c3set])

# (4)
print("\n### (4) 부록 C 둘째 표 ↔ 장부 4절(기록의 이름)")
C2 = [r for r in rows(BASE+r"\장v2\부록C.md", r'^### 기록이', r'^### 기록의 글자') if r[0] != '기록의 이름']
L4 = [r for r in rows(BASE+r"\장부_v2.md", r'^## 4\.', r'^## 5\.') if r[0] != '첫 판 번호']
l4 = {}
for r in L4:
    m = re.search(r'\{\{([^}]+)\}\}', r[-1])
    if m: l4[m.group(1)] = r
for r in C2:
    m = re.search(r'\{\{([^}]+)\}\}', r[1])
    if not m: continue
    lab = m.group(1); L = l4.get(lab)
    if L is None: print(f"- 장부 4절에 라벨 없음: {lab}"); continue
    # L: 첫판번호|종류|이 글의 이름|기록의 이름|절|라벨
    if norm(L[3]) != norm(r[0]): print(f"- {lab}: 기록 이름 다름\n    C :{r[0]}\n    장부:{L[3]}")
    if norm(L[2]) != norm(r[2]): print(f"- {lab}: 이 글의 이름 다름\n    C :{r[2]}\n    장부:{L[2]}")
c2labs={re.search(r'\{\{([^}]+)\}\}', r[1]).group(1) for r in C2 if re.search(r'\{\{([^}]+)\}\}', r[1])}
print("장부 4절에 기록 이름이 있으나 C 둘째 표에 없는 라벨:", [lab for lab,L in l4.items() if L[3].strip() and lab not in c2labs])

# (5)
print("\n### (5) 부록 B 인용 기록의 evidence 구조")
R = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
B = rows(BASE+r"\장v2\부록B.md")
B = [r for r in B if r[0].startswith('r')]
np=npeer=0; noprod=[]; nopeer=[]
for ident,t,title,folder in B:
    d=os.path.join(R, folder.strip('`'))
    ev=os.path.join(d,'evidence')
    hasprod=os.path.isdir(os.path.join(ev,'producer'))
    haspeer=os.path.isdir(os.path.join(ev,'peer')) or (os.path.isdir(ev) and any('peer' in x for x in os.listdir(ev)))
    if hasprod: np+=1
    else: noprod.append((ident, ' '.join(sorted(os.listdir(ev)))[:80] if os.path.isdir(ev) else '(evidence 없음)'))
    if haspeer: npeer+=1
    else: nopeer.append(ident)
print(f"인용 기록 {len(B)}개 중 evidence/producer 있음 {np}, 없음 {len(noprod)}")
for x in noprod: print("   ", x)
print(f"evidence/peer(또는 peer 이름 파일) 있음 {npeer}, 없음 {len(nopeer)}: {nopeer}")

# (6)
print("\n### (6) 부록 A 기호의 정의 문맥")
def show(f, pats, w=170, maxn=2):
    Ls=open(BASE+'\\장v2\\'+f,encoding='utf-8').read().split('\n')
    for pat in pats:
        n=0
        for i,l in enumerate(Ls,1):
            for m in re.finditer(pat, l):
                print(f"[{f}:{i}] …{l[max(0,m.start()-30):m.end()+w]}…"); n+=1
                if n>=maxn: break
            if n>=maxn: break
        if n==0: print(f"[{f}] {pat} : 없음")
E = re.escape
show('장5B.md',[E(r'q_{\max}(Y):='), E(r'q_{\max}:='), E(r'\Lambda_{\mathrm w}(Y):='), E(r'\mathrm{Lc}(Y,q)')])
show('장7A.md',[E(r'n_{\mathrm X}(k)'), E(r'\mathfrak P_k(n)')])
show('장7B.md',[E(r'n_{\mathrm{PD}}(k)'), E(r'\Pi^{\mathrm{up}}_j'), E(r'\mathrm{Left}_n'), E(r'\mathcal W^{(>102)}')])
show('장6.md',[E(r'\varphi^\flat_k'), E(r'\mathrm{Bd}^{\mathrm V}_k'), E(r's^{\mathrm F}(k,\nu)'), E(r'Bor}_\le('), E(r'\mathfrak X_d(y)'), E(r'\mathsf v(k)'), E(r'\mathrm{DD}(m,y)'), E(r'\mathfrak s_d(y)'), E(r'\varsigma_m(\ell)')])
show('장8.md',[E(r'm_{\mathrm{fb}}'), E(r'q_{\mathrm{fb}}'), E(r'\mathrm{fb}(\lambda)'), E(r'\mathrm{km}_N'), E(r'\mathfrak B_N'), E(r'\Psi^{\mathrm{low}}'), E(r'\mathsf c_\Psi'), E(r'\mathsf j_\infty'), E(r's^{\mathrm{cf}}'), E(r'\mathfrak D^{\mathrm{src}}_q')])
show('장10.md',[E(r'\pi^{\mathrm{two}}_N'), E(r'\varkappa_m'), E(r'\omega_m'), E(r'\mathfrak f_m'), E(r'\vartheta_{\mathrm{lb}}'), E(r'\vartheta_0'), E(r'\mathrm{Stays}:='), E(r'\mathrm{PM}_y(d)'), E(r'\mathsf m_{\mathrm S}'), E(r'd^\star')])
show('장9.md',[E(r'\Psi^{\mathrm{lb}}'), r'P\^\{?\\theta\}?_t', E(r'\mathrm{flat}_k(t)'), E(r'\mathcal J_1'), E(r'\mathsf L_\ast(k)'), E(r'\pi_2(t)'), E(r'\gamma_m'), E(r'K_n(m)'), E(r'\pi_n(t_1,t_2)'), E(r'\Theta^\circ_n'), E(r'\mathfrak l_m(t)'), E(r'\mathsf h_N')])
show('장2.md',[E(r'\Phi'), E(r'\mathrm{nf}(n,d)'), E(r'W_n(\gamma)'), E(r'\mathrm{Gr}(x)'), E(r'\Xi_{n,k}'), E(r'J_n(z)'), E(r'\mathfrak v_k')])
show('장5A.md',[E(r'\mathcal Z'), E(r'\mathrm{rq}_r'), E(r'\mathrm{rq}:=')])
show('장4.md',[E(r'\mathsf n_k'), E(r'\mathsf g_k'), E(r'\mathcal A_{k,n}'), E(r'\eta(v)')])
show('장7A.md',[E(r'\mathsf t_k'), E(r'\mathcal T_k(\sigma)'), E(r'n^\sharp_k'), E(r'n^\flat_k')])
