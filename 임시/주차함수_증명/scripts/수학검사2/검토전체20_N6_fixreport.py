# N6 보고 파일의 제어문자(셸 이스케이프 손상) 복구 — 2차
import re
p = r"C:\math\임시\주차함수_증명\대조v2\수학검사2\검토전체20_N6.md"
s = open(p, encoding="utf-8", newline="").read()
for key in ["u$-이전", "floor$ 인증"]:
    i = s.find(key)
    print(key, "->", repr(s[max(0, i-12):i+len(key)]))
# 일반 복구: '$' 뒤에 CR/LF가 오고 'u$-이전'이 이어지면 \nu 로, '/100' 뒤 CR(+LF) 'floor$' 는 \rfloor 로
s2 = re.sub(r"\$\r?\n?u\$-이전", "$\\\\nu$-이전", s)
s2 = re.sub(r"/100\r?\n?floor\$", "/100\\\\rfloor$", s2)
print("changed:", s2 != s)
bad = sorted(set(ch for ch in s2 if ord(ch) < 32 and ch not in "\r\n"))
print("remaining control chars (excluding CR/LF):", bad)
open(p, "w", encoding="utf-8", newline="").write(s2)
for key in ["nu$-이전", "rfloor$ 인증"]:
    i = s2.find(key)
    print(key, "->", repr(s2[max(0, i-12):i+len(key)]))
