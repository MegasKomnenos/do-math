# -*- coding: utf-8 -*-
"""I14: (1) 의심 국소 글자의 장부 1.3 등록 여부, (2) 1.3 라벨 존재, (3) 장 절 제목, (4) 의존지도 미룬 증명 행 참조, (5) 몇 자리의 문맥."""
import re, io, sys, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
L = open(os.path.join(ROOT,'장부_v2.md'),encoding='utf-8').read().split('\n')
sec13 = range(349,415)
def find(pat, rng=sec13):
    rx = re.compile(pat); return [i for i in rng if rx.search(L[i-1])]
B = chr(92)
checks = [
 ("mathcal N_phi (7A)", B+B+"mathcal N_"+B+B+"phi"),
 ("m_1 local (7A)", r"\$m_1\$|[^a-z]m_1(?![\(\}])"),
 ("R_j local (8)", r"R_j"),
 ("Omega_y (6)", B+B+"Omega_y"), ("Omega_tau (7A)", B+B+"Omega_"+B+B+"tau"), ("Omega_e (5A)", B+B+"Omega_e"), ("Omega^pr (7/11)", B+B+"Omega"+B+"^"),
 ("Psi 다중집합 함수 (5A/7A)", "다중집합의 함수|가중치 "+B+"$"+B+B+"Psi|"+B+B+"Psi"+B+"("+B+B+B+"{"),
 ("psi 9장", B+B+"psi"), ("tau(v;q) (8)", B+B+"tau"+B+"(v"), ("Upsilon 4장/5A/8", B+B+"Upsilon(?!_k)"),
 ("old-6-3 언급", "old-6-3"), ("mathcal D_N (6)", B+B+"mathcal D_N"), ("mathcal D(alpha) (7A)", B+B+"mathcal D"+B+"("+B+B+"alpha"), ("mathcal D(z;x) 7B", B+B+"mathcal D"+B+"(z"), ("깊이 집합 (9)", "깊이"),
 ("mathcal G_y 7A", B+B+"mathcal G_y"), ("mathcal U_k(j,j') 7A", B+B+"mathcal U_k"+B+"("), ("mathcal Z 6장", B+B+"mathcal Z(?![_^a-zA-Z])"), ("mathfrak D 5A/6", B+B+"mathfrak D(?![\\^_])"),
 ("mathfrak K_i 6", B+B+"mathfrak K_i"), ("mathfrak l_m 5A", B+B+"mathfrak l_m"), ("mathfrak m_1..3 4장", B+B+"mathfrak m_[123]"), ("mathfrak m^sharp 7", B+B+"mathfrak m"+B+"^"+B+B+"sharp"), ("mathfrak m_i 8", B+B+"mathfrak m_i"),
 ("mathsf u 7B", B+B+"mathsf u(?!"+B+"()"), ("top^H 7B", "top"+B+"^"), ("mathrm D_k 7B", B+B+"mathrm D_k"), ("mathfrak R^sharp_F 10", B+B+"mathfrak R"+B+"^"+B+B+"sharp"),
 ("mathsf L / mathsf R (5/11)", B+B+"mathsf L(?!_)|"+B+B+"mathsf R(?![a-zA-Z])"), ("mathfrak L 5/11", B+B+"mathfrak L(?![a-zA-Z])"), ("Xi local", B+B+"Xi(?!_"+B+"{n)"), ("vartheta local", B+B+"vartheta"), ("Phi(xi,upsilon) 9", B+B+"Phi"+B+"("+B+B+"xi"),
 ("Phi 8장 절대연속", "절대연속"), ("mathfrak g local", B+B+"mathfrak g(?!"+B+"("+B+B+"theta)"), ("mathfrak A/B local", B+B+"mathfrak A(?![a-zA-Z_^])|"+B+B+"mathfrak B(?![a-zA-Z_^])"), ("mathfrak Q local", B+B+"mathfrak Q(?!"+B+"(y)"), ("mathcal Y local", B+B+"mathcal Y(?!_k|"+B+"^)"), ("mathcal J_j 5B", B+B+"mathcal J_j"),
 ("mathfrak v local", B+B+"mathfrak v(?!_k)"), ("mathfrak x_t 8", B+B+"mathfrak x_t"), ("mathfrak r_i 8", B+B+"mathfrak r_[0i]"), ("mathcal W_m/n", B+B+"mathcal W_[mn]"), ("Z_w(F) 9", "Z_w"), ("mathcal F_m(chi) 7B", B+B+"mathcal F_m"), ("mathcal H_k 9", B+B+"mathcal H_k"), ("mathfrak Z_q 6", B+B+"mathfrak Z_q"),
 ("Lambda 9장", B+B+"Lambda"), ("alpha 9장 임시", "임시 변수"), ("sigma 적분변수 6장", B+B+"sigma.*적분|적분.*"+B+B+"sigma"),
]
print("=== (1) 장부 등록 여부 (1.3행 / 전체 처음 12행)")
for name,pat in checks:
    print(f"{name:36s} 1.3: {find(pat)}   전체: {find(pat, range(1,len(L)+1))[:14]}")

print("\n=== (2) 1.3 자리 열의 라벨 존재")
heads = {h['label'] for h in json.load(open(os.path.join(ROOT,'scripts','수학검사2','_I14_heads.json'),encoding='utf-8'))}
allheads = heads
labs13 = {}
for i in sec13:
    for m in re.finditer(r'\{\{(\d+:[^}]+)\}\}', L[i-1]):
        labs13.setdefault(m.group(1), []).append(i)
missing = {k:v for k,v in labs13.items() if k not in allheads}
print("1.3에 나오는 라벨 수:", len(labs13), "| 머리 없음:", missing)
print("\n=== (2b) 4절·5절·8절 등 장부 전체의 라벨 가운데 머리 없는 것 (행: 라벨)")
for i in range(1,len(L)+1):
    if i in sec13: continue
    for m in re.finditer(r'\{\{(\d+:[^}]+)\}\}', L[i-1]):
        if m.group(1) not in allheads:
            print(f"  행{i}: {m.group(1)}  | {L[i-1][:90]}")

print("\n=== (3) 장 파일의 절 제목")
order = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
for ch in order:
    for i,l in enumerate(open(os.path.join(ROOT,'장v2',ch+'.md'),encoding='utf-8'),1):
        if l.startswith('## ') or l.startswith('### '):
            print(f"  {ch}:{i}: {l.strip()[:80]}")

print("\n=== (4) 의존지도 「뒤로 미룬 증명 파일:행」 참조 대조")
D = open(os.path.join(ROOT,'의존지도_v2.md'),encoding='utf-8').read().split('\n')
for l in D:
    for m in re.finditer(r'뒤로 미룬 증명 (장[0-9AB]+)\.md:(\d+)', l):
        f, n = m.group(1), int(m.group(2))
        lab = re.match(r'^\| `\{\{([^}]+)\}\}`', l).group(1)
        lines = open(os.path.join(ROOT,'장v2',f+'.md'),encoding='utf-8').read().split('\n')
        target = lines[n-1] if n-1 < len(lines) else ''
        ok = ('{{'+lab+'}}의 증명' in target)
        if not ok:
            # find actual
            act = [i+1 for i,x in enumerate(lines) if ('{{'+lab+'}}의 증명' in x)]
            print(f"  {lab}: 지도 {f}:{n} -> 현행 {act}  | {target[:60]}")
print("  (출력 없으면 모두 일치)")

print("\n=== (5) 문맥")
def ctx(f, pat, n=3):
    rx = re.compile(pat)
    for i,l in enumerate(open(os.path.join(ROOT,'장v2',f+'.md'),encoding='utf-8'),1):
        m = rx.search(l)
        if m:
            s=max(0,m.start()-100); e=min(len(l),m.end()+100); print(f"  {f}:{i}: …{l[s:e]}…"); n-=1
            if n==0: break
print("-- {{7:old-6-3}} 인용 자리")
for ch in order:
    for i,l in enumerate(open(os.path.join(ROOT,'장v2',ch+'.md'),encoding='utf-8'),1):
        if '{{7:old-6-3}}' in l: print(f"  {ch}:{i}")
print("-- 5B Psi(")
ctx('장5B', B+B+'Psi'+B+'('); ctx('장5A', B+B+'Psi'+B+'(')
print("-- 9장 가중 창 질량 / Lambda")
ctx('장9', '가중 창 질량|'+B+B+'Lambda')
print("-- 11장 32/42/51 mathsf L, mathfrak L, Omega^pr")
ctx('장11', B+B+'mathsf L'); ctx('장11', B+B+'mathfrak L'); ctx('장11', B+B+'Omega'+B+'^')
print("-- 7장 Omega^pr")
ctx('장7A', B+B+'Omega'+B+'^'); ctx('장7B', B+B+'Omega'+B+'^')
print("-- 8:310 R_j")
ctx('장8', 'R_j', 2)
print("-- 6:854 lambda, 9:245 alpha")
ctx('장6', B+B+'lambda', 2); ctx('장9', B+B+'alpha', 2)
print("-- 6장 Z_k 언급(무거운 꼭짓점 수) / 사슬 길이 L=Z")
ctx('장6', '무거운 (자리|꼭짓점)', 3)
