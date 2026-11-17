# 바탕 토큰 뒤에 붙는 꼴(첨자·인수)을 장별로 모아 센다.
# 사용: python -I 검토전체22_R13S2_forms.py [-n 길이] 바탕토큰...
import sys, io, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = r"C:/math/임시/주차함수_증명/장v2/"
FILES = ["장1","장2","부록D_장2","장3","부록D_장3","장4","부록D_장4","장5A","장5B","부록D_장5A","장6","장7A","장7B","부록D_장7A","부록D_장7B","장8","부록D_장8","장9","부록D_장9","장10"]
a = sys.argv[1:]; n = 14
if a[0]=='-n': n = int(a[1]); a = a[2:]
def form(s, p):
    # 토큰 뒤의 첨자/위첨자/괄호 인수를 n자까지 자른다
    t = s[p:p+n]
    return t
for f in FILES:
    L = open(W+f+".md", encoding='utf-8').read().split('\n')
    C = collections.Counter(); first = {}
    for i, s in enumerate(L):
        for k in a:
            p = s.find(k)
            while p >= 0:
                t = form(s, p+len(k)); C[k+t] += 1; first.setdefault(k+t, i+1)
                p = s.find(k, p+1)
    if C:
        print(f"[{f}] " + '  ¦  '.join(f"{t} ×{c}@{first[t]}" for t, c in C.most_common()))
