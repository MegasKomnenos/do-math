# 7장 머리 둘째 문단이 적은 「받아 쓰는 결과」와 7A(머리 뒤)·7B 본문이 실제로 부르는 앞 장 라벨을 견준다.
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
A = open('장v2/장7A.md', encoding='utf-8').read().split('\n')
B = open('장v2/장7B.md', encoding='utf-8').read()
intro = '\n'.join(A[:10]); bodyA = '\n'.join(A[10:])
pat = re.compile(r'\{\{([2-6]):([^}]+)\}\}')
I = set(pat.findall(intro)); 
para2 = set(pat.findall(A[4]))
UA = set(pat.findall(bodyA)); UB = set(pat.findall(B))
print("머리 둘째 문단 라벨 수:", len(para2))
print("둘째 문단에 있으나 7A 본문·7B 어디에도 없는 것:", sorted(para2 - UA - UB))
print("둘째 문단에 있고 7A 본문에만:", sorted((para2 & UA) - UB))
print("7A 본문·7B가 부르나 머리(1-10행)에 없는 앞 장 라벨:", sorted((UA | UB) - I))
print("  그 가운데 7A 본문이 부르는 것:", sorted(UA - I))
