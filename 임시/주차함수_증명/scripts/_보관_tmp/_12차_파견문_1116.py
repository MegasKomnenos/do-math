# -*- coding: utf-8 -*-
"""12차 독립 검토 파견문(태그 S)과 12차 수리 공통 안내(태그 B) 1–3절을 11차 것에서 만든다. 2026-11-16."""
import io, re
ROOT = r"C:\math\임시\주차함수_증명\파견"

s = io.open(ROOT + r"\전체_독립검토11_파견문_1116.md", encoding="utf-8").read()
s = re.sub(r"^# .*$", lambda m: m.group(0).replace("11차", "12차").replace("10차 수리", "11차 수리"), s, count=1, flags=re.M)
s = s.replace("검토전체11_Q", "검토전체12_S")
s = re.sub(r"\| Q(\d+[ab]?) \|", lambda m: "| S" + m.group(1) + " |", s)
s = s.replace("Q11·Q12·Q13", "S11·S12·S13").replace("Q14", "S14").replace("Q1–Q14", "S1–S14")
s = s.replace("`scripts/수학검사2/검토전체11_<태그>_*.py`", "`scripts/수학검사2/검토전체12_<태그>_*.py`")
print("11차 남은 자리:", [s[max(0,m.start()-20):m.start()+12] for m in re.finditer("11차", s)])
io.open(ROOT + r"\전체_독립검토12_파견문_1116.md", "w", encoding="utf-8", newline="\n").write(s)
print("파견문 ok", len(s), "Q 잔존", len(re.findall(r"\bQ\d", s)))

c = io.open(ROOT + r"\전체검토11_수리_공통_1116.md", encoding="utf-8").read()
# 4절은 자리표시자로 되돌린다
i = c.find("## 4. ")
assert i > 0
c = c[:i] + "## 4. 이번 차례의 배정 메모(세션이 보고를 훑어 적은 임자와 주의; 판정이 아니다)\n\n(S1–S14 보고 회수 뒤 작성)\n"
c = c.replace("전체 독립 검토 11차(Q1–Q14) 뒤의 수리", "전체 독립 검토 12차(S1–S14) 뒤의 수리")
c = c.replace("검토전체11_", "검토전체12_").replace("수리_전체11_", "수리_전체12_").replace("인계_전체11_", "인계_전체12_")
c = re.sub(r"\bA(\d+|D|L)\b", lambda m: "B" + m.group(1), c)
c = re.sub(r"\bQ(\d+[ab]?)\b", lambda m: "S" + m.group(1), c)
c = c.replace("6차·7차·8차·9차·10차에도", "6차부터 11차까지")
c = c.replace("「6차에도 문제가 계속 남아 있으면 9차, 10차도 반복」", "「6차에도 문제가 계속 남아 있으면 7차, 8차도 반복」·「10차 수리 이후에도 최대 20차까지 계속 꾸준히 이어가 문제가 이어지면」")
io.open(ROOT + r"\전체검토12_수리_공통_1116.md", "w", encoding="utf-8", newline="\n").write(c)
print("공통 ok", len(c), "A 잔존", len(re.findall(r"\bA(\d+|D|L)\b", c)), "11차 잔존", c.count("11차"))
