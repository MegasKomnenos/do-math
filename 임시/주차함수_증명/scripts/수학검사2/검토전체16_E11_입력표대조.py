# 9장·10장(과 7.7절 정리 old-6-22의 증명)이 인용하는 앞 장의 라벨 집합과 11.3절 세 표의 라벨 집합을 견준다.
import re, os
root = r"C:\math\임시\주차함수_증명"
def read(p): return open(os.path.join(root, "장v2", p), encoding="utf-8").read()
ch9, ch10, ch7b, ch11 = read("장9.md"), read("장10.md"), read("장7B.md"), read("장11.md")
lab = r"\{\{(\d+[AB]?:[a-zA-Z0-9-]+)\}\}"
def labs(t): return set(x.replace("5A:","5:").replace("5B:","5:").replace("7A:","7:").replace("7B:","7:") for x in re.findall(lab, t))
earlier = lambda S: {x for x in S if int(x.split(":")[0]) <= 8}
c9, c10 = earlier(labs(ch9)), earlier(labs(ch10))
# 정리 old-6-22의 증명 부분: 머리부터 다음 진술 머리 전까지
i = ch7b.index("**정리 {{7:old-6-22}}")
j = ch7b.find("\n**", i + 10)
while j != -1 and "의 증명" in ch7b[j:j+60]: j = ch7b.find("\n**", j + 3)
seg22 = ch7b[i: j if j != -1 else None]
c22 = earlier(labs(seg22)) - {"7:old-6-22"}
# 11.3절 부분
a = ch11.index("### 11.3"); b = ch11.index("### 11.4")
s113 = ch11[a:b]
t_shared = s113[s113.index("**공유 입력.**"): s113.index("**첫째 증명의 고유 입력.**")]
t_first = s113[s113.index("**첫째 증명의 고유 입력.**"): s113.index("**둘째 증명의 고유 입력.**")]
t_second = s113[s113.index("**둘째 증명의 고유 입력.**"):]
L_sh, L_1, L_2 = earlier(labs(t_shared)), earlier(labs(t_first)), earlier(labs(t_second))
print("9장이 인용하는 앞 장 라벨 수", len(c9), " 10장", len(c10), " old-6-22 증명", len(c22))
print("\n9장 또는 old-6-22 증명이 인용하지만 11.3 어느 표에도 없는 것:", sorted((c9 | c22) - L_sh - L_1 - L_2))
print("\n10장이 인용하지만 11.3 어느 표에도 없는 것:", sorted(c10 - L_sh - L_1 - L_2))
print("\n첫째 고유 표에 있으나 10장도 인용하는 것:", sorted(L_1 & c10))
print("둘째 고유 표에 있으나 9장이나 old-6-22 증명도 인용하는 것:", sorted(L_2 & (c9 | c22)))
print("\n공유 표에 있으나 9장·old-6-22 증명 어디에도 안 나오는 것:", sorted(L_sh - c9 - c22))
print("공유 표에 있으나 10장에 안 나오는 것:", sorted(L_sh - c10))
print("\n첫째 고유 표에 있으나 9장·old-6-22에 안 나오는 것:", sorted(L_1 - c9 - c22))
print("둘째 고유 표에 있으나 10장에 안 나오는 것:", sorted(L_2 - c10))
print("\nold-6-22 증명 인용:", sorted(c22))
