# -*- coding: utf-8 -*-
"""불변식: 표지의 쌍반점 개수를 괄호 밖에서만 센다(계산 증거(범위; 층) 꼴 허용). 장부·공통지침 규칙 10 문구 보강."""
import io
import re


def rw(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


root = "임시/주차함수_증명"

p = root + "/scripts/불변식.py"
s = rw(p)
old = '''            if bracket.count(";") != 1:
                failures.append(f"{i}: 지위 표지의 쌍반점은 하나(지위; 식별자)여야 함 [{bracket}]")'''
assert s.count(old) == 1, s.count(old)
new = '''            outside = bracket
            for _ in range(3):
                outside = re.sub(r"\\([^()]*\\)", "", outside)  # 괄호 안(계산 증거(범위; 층) 등)의 쌍반점은 세지 않는다
            if outside.count(";") != 1:
                failures.append(f"{i}: 지위 표지의 괄호 밖 쌍반점은 하나(지위; 식별자)여야 함 [{bracket}]")'''
s = s.replace(old, new)
wr(p, s)
print("불변식 semicolon rule")

for p, old_frag in ((root + "/장부_기호용어이름.md", "10. 지위 표지의 문법: 대괄호 안은 쌍반점 하나로 「지위; 식별자」."),
                    (root + "/파견/집필_공통지침.md", "- 표지의 문법(2026-11-12 확정): 대괄호 안은 쌍반점 하나로 「지위; 식별자」.")):
    s = rw(p)
    assert s.count(old_frag) == 1, (p, s.count(old_frag))
    s = s.replace(old_frag, old_frag + " 괄호 안의 쌍반점(「계산 증거(범위; 층)」)은 세지 않는다.")
    wr(p, s)
    print("patched", p.split("/")[-1])
